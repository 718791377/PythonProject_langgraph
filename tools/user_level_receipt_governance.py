#!/usr/bin/env python3
"""Repo-local receipt, rollback, and redaction governance guard.

This helper validates generic user-level authorization receipts and update
receipts for the MCP / skills / browser / CLI harness governance lane. It is a
deterministic repo-local guard only: it does not install tools, call MCP
servers, control browsers, read browser state, or mutate user-level Codex
configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_receipt_governance"

AUTHORIZATION_REQUIRED_FIELDS = (
    "action",
    "target",
    "scope",
    "expiry",
    "session",
    "operator_confirmation",
)

UPDATE_REQUIRED_FIELDS = (
    "tool_name",
    "installed_version",
    "source_url",
    "install_path",
    "wrapper_path",
    "state_path",
    "smoke_test_command",
    "smoke_test_result",
    "updater_command",
    "rollback_pointer",
    "owner_lane",
    "redaction_status",
)

SMOKE_REQUIRED_FIELDS = (
    "tool_name",
    "owner_lane",
    "runtime_stage",
    "install_receipt",
    "smoke_command",
    "smoke_type",
    "smoke_result",
    "timeout_release",
    "rollback_pointer",
    "rollback_ready",
    "command_transcript",
    "transcript_redaction",
    "redaction_status",
)

ROLLBACK_REQUIRED_FIELDS = (
    "rollback_target",
    "rollback_pointer",
    "rollback_mode",
    "restore_command",
    "dry_run_result",
    "post_rollback_verification",
    "owner_lane",
    "operator_authorization",
    "redaction_status",
)

PATH_FIELDS = {"install_path", "wrapper_path", "state_path", "rollback_pointer"}
LOCAL_PATH_EVIDENCE_FIELDS = ("install_path", "wrapper_path", "state_path", "rollback_pointer")
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
ALLOWED_R4_STAGES = {"r4", "smoke-tested", "smoke_tested"}
ALLOWED_SMOKE_TYPES = {"help", "version", "status", "safe-discovery", "safe_discovery", "read-only", "readonly"}
FORBIDDEN_SMOKE_MARKERS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
ALLOWED_ROLLBACK_MODES = {"dry-run", "dry_run", "apply"}
SENSITIVE_KEY_PARTS = (
    "cookie",
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "raw_browser_data",
    "browser_history",
    "message_content",
    "message_contents",
    "plugin_description_dump",
)
SAFE_KEY_EXCEPTIONS = (
    "redaction",
    "secret_ref",
    "token_ref",
    "cookie_ref",
    "rollback_pointer_hash",
)
SECRET_VALUE_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    if value is None:
        return ""
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()[:16]


def sanitize_text(value: Any, *, limit: int = 240) -> str:
    text = "" if value is None else str(value)
    text = SECRET_VALUE_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    return text[:limit]


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text in PATH_FIELDS or key_text.endswith("_path") or key_text.endswith("_pointer"):
                result[f"{key_text}_hash"] = stable_hash(item)
            elif is_sensitive_key(key_text):
                result[key_text] = "[REDACTED_SENSITIVE_FIELD]"
            else:
                result[key_text] = sanitize_json(item)
        return result
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def load_receipt(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["receipt_missing"]
    except json.JSONDecodeError:
        return None, ["receipt_invalid_json"]
    except OSError:
        return None, ["receipt_unreadable"]
    if not isinstance(data, dict):
        return None, ["receipt_not_object"]
    return data, []


def parse_expiry(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def smoke_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "pass"
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() == "pass"
    return False


def redaction_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ALLOWED_REDACTION_STATUS
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in ALLOWED_REDACTION_STATUS
    return False


def timeout_release_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "pass"
    if isinstance(value, dict):
        status_ok = str(value.get("status", "")).strip().lower() == "pass"
        released = value.get("released", True)
        return status_ok and released is not False
    return False


def normalize_runtime_stage(value: Any) -> str:
    text = str(value or "").strip().lower()
    return "R4" if text in ALLOWED_R4_STAGES else sanitize_text(value)


def normalize_smoke_type(value: Any) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    if text == "readonly":
        return "read-only"
    return text


def normalize_rollback_mode(value: Any) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    return text


def is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    if any(exception in lowered for exception in SAFE_KEY_EXCEPTIONS):
        return False
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def collect_redaction_findings(value: Any, *, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if is_sensitive_key(str(key)) and item not in (None, "", [], {}):
                findings.append(f"sensitive_field_present:{child_path}")
            findings.extend(collect_redaction_findings(item, path=child_path))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            findings.extend(collect_redaction_findings(item, path=f"{path}[{idx}]"))
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        findings.append(f"inline_secret_value:{path}")
    return findings


def validate_authorization_receipt(receipt: dict[str, Any], *, action: str, target: str, session: str) -> list[str]:
    blockers: list[str] = []
    for field in AUTHORIZATION_REQUIRED_FIELDS:
        if field not in receipt:
            blockers.append(f"authorization_receipt_missing_{field}")
    if receipt.get("operator_confirmation") is not True:
        blockers.append("authorization_receipt_operator_confirmation_not_true")
    if str(receipt.get("target", "")) not in {target, "*"}:
        blockers.append("authorization_receipt_target_mismatch")
    if str(receipt.get("session", "")) != session:
        blockers.append("authorization_receipt_session_mismatch")
    receipt_action = str(receipt.get("action", ""))
    if receipt_action not in {action, "*"}:
        blockers.append("authorization_receipt_action_mismatch")
    scope = receipt.get("scope")
    if not (
        scope == "*"
        or (isinstance(scope, str) and (action in scope or "*" in scope))
        or (isinstance(scope, list) and (action in [str(item) for item in scope] or "*" in [str(item) for item in scope]))
    ):
        blockers.append("authorization_receipt_scope_missing_action")
    expiry = parse_expiry(receipt.get("expiry"))
    if expiry is None:
        blockers.append("authorization_receipt_expiry_invalid")
    elif expiry <= datetime.now(timezone.utc):
        blockers.append("authorization_receipt_expired")
    blockers.extend(collect_redaction_findings(receipt))
    return sorted(set(blockers))


def validate_update_receipt(receipt: dict[str, Any], *, tool_name: str | None, owner_lane: str | None) -> list[str]:
    blockers: list[str] = []
    for field in UPDATE_REQUIRED_FIELDS:
        if field not in receipt:
            blockers.append(f"update_receipt_missing_{field}")
    if tool_name is not None and str(receipt.get("tool_name", "")) != tool_name:
        blockers.append("update_receipt_tool_name_mismatch")
    if owner_lane is not None and str(receipt.get("owner_lane", "")) != owner_lane:
        blockers.append("update_receipt_owner_lane_mismatch")
    for field in ("tool_name", "installed_version", "source_url", "install_path", "wrapper_path", "state_path", "smoke_test_command", "updater_command", "owner_lane"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"update_receipt_{field}_required")
    if not smoke_pass(receipt.get("smoke_test_result")):
        blockers.append("update_receipt_smoke_test_result_must_pass")
    if not receipt.get("rollback_pointer"):
        blockers.append("update_receipt_rollback_pointer_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("update_receipt_redaction_status_must_pass")
    blockers.extend(collect_redaction_findings(receipt))
    return sorted(set(blockers))


def validate_smoke_receipt(receipt: dict[str, Any], *, tool_name: str | None, owner_lane: str | None) -> list[str]:
    blockers: list[str] = []
    for field in SMOKE_REQUIRED_FIELDS:
        if field not in receipt:
            blockers.append(f"smoke_receipt_missing_{field}")
    if tool_name is not None and str(receipt.get("tool_name", "")) != tool_name:
        blockers.append("smoke_receipt_tool_name_mismatch")
    if owner_lane is not None and str(receipt.get("owner_lane", "")) != owner_lane:
        blockers.append("smoke_receipt_owner_lane_mismatch")
    for field in ("tool_name", "owner_lane", "install_receipt", "smoke_command", "smoke_type", "rollback_pointer"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"smoke_receipt_{field}_required")
    if str(receipt.get("runtime_stage", "")).strip().lower() not in ALLOWED_R4_STAGES:
        blockers.append("smoke_receipt_runtime_stage_must_be_r4")
    if normalize_smoke_type(receipt.get("smoke_type")) not in {item.replace("_", "-") for item in ALLOWED_SMOKE_TYPES}:
        blockers.append("smoke_receipt_smoke_type_not_read_only")
    if not smoke_pass(receipt.get("smoke_result")):
        blockers.append("smoke_receipt_smoke_result_must_pass")
    if not timeout_release_pass(receipt.get("timeout_release")):
        blockers.append("smoke_receipt_timeout_release_must_pass")
    if receipt.get("rollback_ready") is not True:
        blockers.append("smoke_receipt_rollback_ready_must_be_true")
    if not redaction_pass(receipt.get("transcript_redaction")):
        blockers.append("smoke_receipt_transcript_redaction_must_pass")
    transcript_redaction = receipt.get("transcript_redaction")
    if isinstance(transcript_redaction, dict) and not str(transcript_redaction.get("redacted_transcript_hash", "")).strip():
        blockers.append("smoke_receipt_redacted_transcript_hash_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("smoke_receipt_redaction_status_must_pass")
    for field in FORBIDDEN_SMOKE_MARKERS:
        if receipt.get(field) is True:
            blockers.append(f"smoke_receipt_forbidden_{field}")
    blockers.extend(collect_redaction_findings(receipt))
    return sorted(set(blockers))


def validate_rollback_receipt(receipt: dict[str, Any], *, owner_lane: str | None) -> list[str]:
    blockers: list[str] = []
    for field in ROLLBACK_REQUIRED_FIELDS:
        if field not in receipt:
            blockers.append(f"rollback_receipt_missing_{field}")
    if owner_lane is not None and str(receipt.get("owner_lane", "")) != owner_lane:
        blockers.append("rollback_receipt_owner_lane_mismatch")
    for field in ("rollback_target", "rollback_pointer", "rollback_mode", "restore_command", "owner_lane"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"rollback_receipt_{field}_required")
    mode = normalize_rollback_mode(receipt.get("rollback_mode"))
    if mode not in {"dry-run", "apply"}:
        blockers.append("rollback_receipt_mode_invalid")
    if not smoke_pass(receipt.get("dry_run_result")):
        blockers.append("rollback_receipt_dry_run_result_must_pass")
    if not smoke_pass(receipt.get("post_rollback_verification")):
        blockers.append("rollback_receipt_post_rollback_verification_must_pass")
    if mode == "apply":
        if receipt.get("operator_authorization") is not True:
            blockers.append("rollback_receipt_apply_requires_operator_authorization")
        if not smoke_pass(receipt.get("apply_result")):
            blockers.append("rollback_receipt_apply_result_must_pass")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("rollback_receipt_redaction_status_must_pass")
    blockers.extend(collect_redaction_findings(receipt))
    return sorted(set(blockers))


def authorization_summary(receipt: dict[str, Any], *, receipt_path: Path) -> dict[str, Any]:
    return {
        "receipt_path_hash": stable_hash(str(receipt_path)),
        "action": sanitize_text(receipt.get("action")),
        "target": sanitize_text(receipt.get("target")),
        "scope": sanitize_json(receipt.get("scope")),
        "session": sanitize_text(receipt.get("session")),
        "expiry": sanitize_text(receipt.get("expiry")),
        "operator_confirmation": receipt.get("operator_confirmation") is True,
    }


def update_summary(receipt: dict[str, Any], *, receipt_path: Path) -> dict[str, Any]:
    return {
        "receipt_path_hash": stable_hash(str(receipt_path)),
        "tool_name": sanitize_text(receipt.get("tool_name")),
        "owner_lane": sanitize_text(receipt.get("owner_lane")),
        "installed_version": sanitize_text(receipt.get("installed_version")),
        "source_url": sanitize_text(receipt.get("source_url")),
        "install_path_hash": stable_hash(receipt.get("install_path")),
        "wrapper_path_hash": stable_hash(receipt.get("wrapper_path")),
        "state_path_hash": stable_hash(receipt.get("state_path")),
        "smoke_status": "pass" if smoke_pass(receipt.get("smoke_test_result")) else "not-pass",
        "updater_command": sanitize_text(receipt.get("updater_command")),
        "rollback_pointer_hash": stable_hash(receipt.get("rollback_pointer")),
        "redaction_status": sanitize_json(receipt.get("redaction_status")),
    }


def smoke_summary(receipt: dict[str, Any], *, receipt_path: Path) -> dict[str, Any]:
    return {
        "receipt_path_hash": stable_hash(str(receipt_path)),
        "tool_name": sanitize_text(receipt.get("tool_name")),
        "owner_lane": sanitize_text(receipt.get("owner_lane")),
        "runtime_stage": normalize_runtime_stage(receipt.get("runtime_stage")),
        "install_receipt_hash": stable_hash(receipt.get("install_receipt")),
        "smoke_command_hash": stable_hash(receipt.get("smoke_command")),
        "smoke_type": normalize_smoke_type(receipt.get("smoke_type")),
        "smoke_status": "pass" if smoke_pass(receipt.get("smoke_result")) else "not-pass",
        "timeout_release_status": "pass" if timeout_release_pass(receipt.get("timeout_release")) else "not-pass",
        "rollback_pointer_hash": stable_hash(receipt.get("rollback_pointer")),
        "rollback_ready": receipt.get("rollback_ready") is True,
        "command_transcript_hash": stable_hash(receipt.get("command_transcript")),
        "transcript_redaction": sanitize_json(receipt.get("transcript_redaction")),
        "redaction_status": sanitize_json(receipt.get("redaction_status")),
    }


def rollback_summary(receipt: dict[str, Any], *, receipt_path: Path) -> dict[str, Any]:
    mode = normalize_rollback_mode(receipt.get("rollback_mode"))
    return {
        "receipt_path_hash": stable_hash(str(receipt_path)),
        "rollback_target": sanitize_text(receipt.get("rollback_target")),
        "owner_lane": sanitize_text(receipt.get("owner_lane")),
        "rollback_mode": mode,
        "rollback_pointer_hash": stable_hash(receipt.get("rollback_pointer")),
        "restore_command_hash": stable_hash(receipt.get("restore_command")),
        "dry_run_status": "pass" if smoke_pass(receipt.get("dry_run_result")) else "not-pass",
        "apply_status": "pass" if smoke_pass(receipt.get("apply_result")) else ("not-applicable" if mode != "apply" else "not-pass"),
        "post_rollback_verification_status": "pass"
        if smoke_pass(receipt.get("post_rollback_verification"))
        else "not-pass",
        "operator_authorized": receipt.get("operator_authorization") is True,
        "redaction_status": sanitize_json(receipt.get("redaction_status")),
    }


def local_path_evidence(receipt: dict[str, Any]) -> dict[str, str]:
    evidence: dict[str, str] = {}
    for field in LOCAL_PATH_EVIDENCE_FIELDS:
        value = receipt.get(field)
        if isinstance(value, str) and value.strip():
            evidence[field] = value
    return evidence


def response(
    ok: bool,
    action: str,
    *,
    blockers: list[str],
    contains_raw_private_paths_in_output: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": ok,
        "action": action,
        "blockers": blockers,
        "mutates_user_level_state": False,
        "runs_external_tool": False,
        "reads_browser_data": False,
        "contains_raw_private_paths_in_output": contains_raw_private_paths_in_output,
        "contains_raw_secrets_in_output": False,
    }
    payload.update(extra)
    return payload


def command_auth_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_receipt(receipt_path)
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_authorization_receipt(receipt, action=args.action, target=args.target, session=args.session))
    ok = not blockers
    return response(
        ok,
        "auth-check",
        blockers=sorted(set(blockers)),
        authorization_valid=ok,
        authorization_summary=authorization_summary(receipt, receipt_path=receipt_path) if receipt else {},
    )


def command_update_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_receipt(receipt_path)
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_update_receipt(receipt, tool_name=args.tool_name, owner_lane=args.owner_lane))
    if args.include_local_path_evidence and not args.local_evidence_authorized:
        blockers.append("local_path_evidence_requires_explicit_authorization")
    ok = not blockers
    include_local_evidence = bool(ok and receipt and args.include_local_path_evidence and args.local_evidence_authorized)
    extra: dict[str, Any] = {}
    if include_local_evidence and receipt is not None:
        extra["local_path_evidence_scope"] = "local-only"
        extra["local_path_evidence"] = local_path_evidence(receipt)
    return response(
        ok,
        "update-check",
        blockers=sorted(set(blockers)),
        contains_raw_private_paths_in_output=include_local_evidence,
        update_receipt_valid=ok,
        rollback_ready=bool(ok and receipt and receipt.get("rollback_pointer")),
        update_summary=update_summary(receipt, receipt_path=receipt_path) if receipt else {},
        local_path_evidence_requested=bool(args.include_local_path_evidence),
        local_path_evidence_authorized=bool(args.local_evidence_authorized),
        **extra,
    )


def command_smoke_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_receipt(receipt_path)
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_smoke_receipt(receipt, tool_name=args.tool_name, owner_lane=args.owner_lane))
    ok = not blockers
    return response(
        ok,
        "smoke-check",
        blockers=sorted(set(blockers)),
        smoke_receipt_valid=ok,
        runtime_stage="R4" if ok else "blocked",
        rollback_ready=bool(ok and receipt and receipt.get("rollback_ready") is True and receipt.get("rollback_pointer")),
        smoke_summary=smoke_summary(receipt, receipt_path=receipt_path) if receipt else {},
    )


def command_rollback_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_receipt(receipt_path)
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_rollback_receipt(receipt, owner_lane=args.owner_lane))
    ok = not blockers
    return response(
        ok,
        "rollback-check",
        blockers=sorted(set(blockers)),
        rollback_receipt_valid=ok,
        rollback_performed=False,
        rollback_summary=rollback_summary(receipt, receipt_path=receipt_path) if receipt else {},
    )


def command_redact_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_receipt(receipt_path)
    blockers = list(load_blockers)
    findings: list[str] = []
    if receipt is not None:
        findings = collect_redaction_findings(receipt)
        blockers.extend(findings)
    ok = not blockers
    return response(
        ok,
        "redact-check",
        blockers=sorted(set(blockers)),
        redaction_valid=ok,
        finding_count=len(findings),
        receipt_path_hash=stable_hash(str(receipt_path)),
        sanitized_preview=sanitize_json(receipt) if receipt else {},
    )


def command_template(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind == "authorization":
        fields = list(AUTHORIZATION_REQUIRED_FIELDS)
    elif args.kind == "update":
        fields = list(UPDATE_REQUIRED_FIELDS)
    elif args.kind == "smoke":
        fields = list(SMOKE_REQUIRED_FIELDS)
    else:
        fields = list(ROLLBACK_REQUIRED_FIELDS)
    return response(True, "template", blockers=[], kind=args.kind, required_fields=fields)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate user-level authorization/update receipts and redaction boundaries.")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth-check", help="Validate one-task authorization receipt evidence.")
    auth.add_argument("--receipt", required=True)
    auth.add_argument("--action", required=True)
    auth.add_argument("--target", required=True)
    auth.add_argument("--session", required=True)
    auth.add_argument("--json", action="store_true")

    update = sub.add_parser("update-check", help="Validate update/install receipt and rollback evidence.")
    update.add_argument("--receipt", required=True)
    update.add_argument("--tool-name", default=None)
    update.add_argument("--owner-lane", default=None)
    update.add_argument(
        "--include-local-path-evidence",
        action="store_true",
        help="Include raw local install/wrapper/state/rollback paths for explicitly authorized local-only evidence.",
    )
    update.add_argument(
        "--local-evidence-authorized",
        action="store_true",
        help="Explicitly authorize raw local path evidence in output for a local-only evidence artifact.",
    )
    update.add_argument("--json", action="store_true")

    smoke = sub.add_parser("smoke-check", help="Validate R4 smoke-tested receipt and rollback readiness evidence.")
    smoke.add_argument("--receipt", required=True)
    smoke.add_argument("--tool-name", default=None)
    smoke.add_argument("--owner-lane", default=None)
    smoke.add_argument("--json", action="store_true")

    rollback = sub.add_parser("rollback-check", help="Validate rollback executor receipt evidence without executing rollback.")
    rollback.add_argument("--receipt", required=True)
    rollback.add_argument("--owner-lane", default=None)
    rollback.add_argument("--json", action="store_true")

    redact = sub.add_parser("redact-check", help="Validate that a receipt does not carry raw sensitive payloads.")
    redact.add_argument("--receipt", required=True)
    redact.add_argument("--json", action="store_true")

    template = sub.add_parser("template", help="Show required receipt fields.")
    template.add_argument("--kind", choices=("authorization", "update", "smoke", "rollback"), required=True)
    template.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "auth-check": command_auth_check,
        "update-check": command_update_check,
        "smoke-check": command_smoke_check,
        "rollback-check": command_rollback_check,
        "redact-check": command_redact_check,
        "template": command_template,
    }
    result = handlers[args.command](args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
