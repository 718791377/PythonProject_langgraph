#!/usr/bin/env python3
"""Repo-local WXWork_CLI governance guard.

This helper models the future ``WXWork_CLI`` control boundary through
CLI-Anything without attaching to ``WXWork.exe``, probing local processes,
reading message content, calling live API/Webhook endpoints, mutating
user-level Codex configuration, or starting GUI automation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_NAME = "WXWork_CLI"
OWNER_LANE = "wxwork_cli"
TARGET_PROCESS = "WXWork.exe"
LEASE_SCOPE = "global-wxwork-gui"
SENSITIVE_ACTIONS = {"gui.attach", "gui.click", "gui.type", "gui.read-message"}
READ_ONLY_ACTIONS = {"api.status", "webhook.plan", "gui.plan"}
ALLOWED_SMOKE_TYPES = {"help": ["--help"], "status": ["--status"], "safe-discovery": ["--help"]}
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
SMOKE_FORBIDDEN_MARKERS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
SECRET_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password|webhook[_-]?key)\s*[:=]\s*([^\s,;\"']+)")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def stable_hash(value: Any, length: int = 16) -> str:
    return hashlib.sha256(str(value).encode("utf-8", errors="replace")).hexdigest()[:length]


def sanitize_text(value: Any, *, limit: int = 160) -> str:
    text = str(value)
    text = SECRET_RE.sub(lambda match: match.group(0).split(match.group(1))[0] + "[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        suffix = "...[truncated]"
        return text[: max(0, limit - len(suffix))].rstrip() + suffix
    return text


def load_json(path: str | None) -> tuple[dict[str, Any] | None, list[str]]:
    if not path:
        return None, ["receipt_missing"]
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["receipt_missing"]
    except json.JSONDecodeError:
        return None, ["receipt_invalid_json"]
    except OSError:
        return None, ["receipt_unreadable"]
    if not isinstance(data, dict):
        return None, ["receipt_not_object"]
    return data, []


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def safety_payload() -> dict[str, Any]:
    return {
        "repo_local_guard_only": True,
        "process_probe_performed": False,
        "attaches_to_wxwork": False,
        "controls_gui": False,
        "reads_message_content": False,
        "sends_messages": False,
        "calls_enterprise_wechat_api": False,
        "calls_webhook": False,
        "mutates_user_level_codex_config": False,
        "raw_private_paths_in_output": False,
    }


def validate_authorization(receipt: dict[str, Any] | None, blockers: list[str], *, action: str, session: str) -> bool:
    if receipt is None:
        blockers.append("operator_authorization_receipt_required")
        return False
    required = {"action", "target", "scope", "expiry", "session", "operator_confirmation", "owner_lane", "redaction_policy", "rollback_pointer"}
    missing = sorted(field for field in required if field not in receipt)
    blockers.extend(f"authorization_missing_{field}" for field in missing)
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("authorization_owner_lane_must_be_wxwork_cli")
    if receipt.get("action") != action:
        blockers.append("authorization_action_mismatch")
    if receipt.get("target") not in {TARGET_PROCESS, f"process:{TARGET_PROCESS}", "wecom-gui"}:
        blockers.append("authorization_target_must_be_wxwork")
    if receipt.get("session") != session:
        blockers.append("authorization_session_mismatch")
    if receipt.get("operator_confirmation") is not True:
        blockers.append("operator_confirmation_required")
    expiry = parse_datetime(receipt.get("expiry"))
    if expiry is None or expiry <= now_utc():
        blockers.append("authorization_expired_or_invalid")
    return not blockers


def validate_lease(receipt: dict[str, Any] | None, blockers: list[str], *, session: str) -> bool:
    if receipt is None:
        blockers.append("global_wxwork_lease_required")
        return False
    required = {"schema_version", "owner_lane", "lease_scope", "target_process", "session", "status", "expires_at", "timeout_release_seconds", "rollback_pointer"}
    missing = sorted(field for field in required if field not in receipt)
    blockers.extend(f"lease_missing_{field}" for field in missing)
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("lease_owner_lane_must_be_wxwork_cli")
    if receipt.get("lease_scope") != LEASE_SCOPE:
        blockers.append("lease_scope_must_be_global_wxwork_gui")
    if receipt.get("target_process") != TARGET_PROCESS:
        blockers.append("lease_target_process_must_be_wxwork")
    if receipt.get("session") != session:
        blockers.append("lease_session_mismatch")
    if receipt.get("status") != "active":
        blockers.append("lease_status_must_be_active")
    expiry = parse_datetime(receipt.get("expires_at"))
    if expiry is None or expiry <= now_utc():
        blockers.append("lease_expired_or_invalid")
    try:
        timeout = int(receipt.get("timeout_release_seconds"))
    except (TypeError, ValueError):
        timeout = 0
    if timeout <= 0:
        blockers.append("lease_timeout_release_required")
    return not blockers



def now_iso() -> str:
    return now_utc().isoformat(timespec="seconds")


def smoke_result_pass(value: Any) -> bool:
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


def hash_ref(prefix: str, value: Any) -> str:
    return f"{prefix}:{stable_hash(value)}"


def transcript_redaction(transcript: str) -> dict[str, str]:
    return {
        "status": "pass",
        "redacted_transcript_hash": stable_hash(transcript),
    }


def load_install_receipt(path: str) -> tuple[dict[str, Any] | None, list[str]]:
    receipt, blockers = load_json(path)
    return receipt, [f"install_{blocker}" for blocker in blockers]


def validate_install_receipt(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return ["install_receipt_required"]
    blockers: list[str] = []
    required = {
        "tool_name",
        "owner_lane",
        "status",
        "source_url",
        "installed_version",
        "wrapper_path",
        "smoke_test_command",
        "smoke_test_result",
        "updater_command",
        "rollback_pointer",
        "redaction_status",
    }
    missing = sorted(field for field in required if field not in receipt)
    blockers.extend(f"install_receipt_missing_{field}" for field in missing)
    if receipt.get("tool_name") != TOOL_NAME:
        blockers.append("install_receipt_tool_name_must_be_wxwork_cli")
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("install_receipt_owner_lane_must_be_wxwork_cli")
    if receipt.get("status") != "installed-user-level":
        blockers.append("install_receipt_status_must_be_installed_user_level")
    if receipt.get("source_url") != "https://github.com/HKUDS/CLI-Anything":
        blockers.append("install_receipt_source_url_must_be_cli_anything")
    wrapper_path = receipt.get("wrapper_path")
    if not isinstance(wrapper_path, str) or not wrapper_path.strip():
        blockers.append("install_receipt_wrapper_path_required")
    elif not Path(wrapper_path).exists():
        blockers.append("install_receipt_wrapper_not_resolved")
    if not smoke_result_pass(receipt.get("smoke_test_result")):
        blockers.append("install_receipt_smoke_test_result_must_pass")
    if not isinstance(receipt.get("rollback_pointer"), str) or not str(receipt.get("rollback_pointer", "")).strip():
        blockers.append("install_receipt_rollback_pointer_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("install_receipt_redaction_status_must_pass")
    for marker in ("sends_messages", "message_body_included", "gui_control_performed", "process_probe_performed"):
        if receipt.get(marker) is True:
            blockers.append(f"install_receipt_forbidden_{marker}")
    return sorted(set(blockers))


def build_smoke_receipt(
    *,
    install_receipt_path: Path,
    install_receipt: dict[str, Any],
    smoke_type: str,
    session: str,
    transcript: str,
    timeout_seconds: int,
    target_process: str,
    lease_receipt: str | None,
) -> dict[str, Any]:
    sanitized_transcript = sanitize_text(transcript, limit=1200)
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "runtime_stage": "smoke-tested",
        "r4_status": "smoke-tested",
        "smoke_tested": True,
        "session": sanitize_text(session, limit=80),
        "install_receipt": hash_ref("receipt-sha256", str(install_receipt_path)),
        "wrapper_path_hash": stable_hash(install_receipt.get("wrapper_path")),
        "smoke_command": f"{TOOL_NAME} {' '.join(ALLOWED_SMOKE_TYPES[smoke_type])}".strip(),
        "smoke_type": smoke_type,
        "smoke_result": {"status": "pass"},
        "timeout_release": {"status": "pass", "released": True, "timeout_seconds": int(timeout_seconds)},
        "rollback_pointer": hash_ref("rollback-sha256", install_receipt.get("rollback_pointer")),
        "rollback_ready": True,
        "command_transcript": sanitized_transcript,
        "transcript_redaction": transcript_redaction(sanitized_transcript),
        "redaction_status": "no_secrets",
        "process_probe_performed": False,
        "gui_control_performed": False,
        "sends_messages": False,
        "message_body_included": False,
        "wxwork_started": False,
        "wxwork_controlled": False,
        "target_process_hash": stable_hash(target_process) if target_process else "",
        "global_lease_required": bool(target_process),
        "global_lease_verified": bool(target_process and lease_receipt),
        "lease_receipt": hash_ref("lease-sha256", lease_receipt) if lease_receipt else "not-required",
        "blockers": [],
    }
    for marker in SMOKE_FORBIDDEN_MARKERS:
        receipt[marker] = False
    return receipt


def validate_smoke_receipt(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return ["smoke_receipt_required"]
    blockers: list[str] = []
    required = {
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
    }
    missing = sorted(field for field in required if field not in receipt)
    blockers.extend(f"smoke_receipt_missing_{field}" for field in missing)
    if receipt.get("tool_name") != TOOL_NAME:
        blockers.append("smoke_receipt_tool_name_must_be_wxwork_cli")
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("smoke_receipt_owner_lane_must_be_wxwork_cli")
    if str(receipt.get("runtime_stage", "")).strip().lower() not in {"r4", "smoke-tested", "smoke_tested"}:
        blockers.append("smoke_receipt_runtime_stage_must_be_r4")
    if str(receipt.get("smoke_type", "")).strip().lower() not in ALLOWED_SMOKE_TYPES:
        blockers.append("smoke_receipt_smoke_type_not_allowed")
    if not smoke_result_pass(receipt.get("smoke_result")):
        blockers.append("smoke_receipt_smoke_result_must_pass")
    if not timeout_release_pass(receipt.get("timeout_release")):
        blockers.append("smoke_receipt_timeout_release_must_pass")
    if receipt.get("rollback_ready") is not True:
        blockers.append("smoke_receipt_rollback_ready_must_be_true")
    if not redaction_pass(receipt.get("transcript_redaction")):
        blockers.append("smoke_receipt_transcript_redaction_must_pass")
    transcript_redaction_value = receipt.get("transcript_redaction")
    if isinstance(transcript_redaction_value, dict) and not str(transcript_redaction_value.get("redacted_transcript_hash", "")).strip():
        blockers.append("smoke_receipt_redacted_transcript_hash_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("smoke_receipt_redaction_status_must_pass")
    for marker in SMOKE_FORBIDDEN_MARKERS:
        if receipt.get(marker) is True:
            blockers.append(f"smoke_receipt_forbidden_{marker}")
    for marker in ("process_probe_performed", "gui_control_performed", "sends_messages", "message_body_included", "wxwork_started", "wxwork_controlled"):
        if receipt.get(marker) is True:
            blockers.append(f"smoke_receipt_forbidden_{marker}")
    transcript = str(receipt.get("command_transcript", ""))
    if SECRET_RE.search(transcript):
        blockers.append("smoke_receipt_raw_secret_in_transcript")
    if WINDOWS_PATH_RE.search(transcript) or UNC_PATH_RE.search(transcript):
        blockers.append("smoke_receipt_raw_private_path_in_transcript")
    return sorted(set(blockers))


def write_smoke_receipt(receipt_dir: Path, receipt: dict[str, Any]) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / "r4-wxwork-cli-smoke.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def smoke_summary(receipt: dict[str, Any] | None, *, receipt_path: Path | None = None) -> dict[str, Any]:
    if not receipt:
        return {}
    summary = {
        "tool_name": sanitize_text(receipt.get("tool_name"), limit=80),
        "owner_lane": sanitize_text(receipt.get("owner_lane"), limit=80),
        "runtime_stage": sanitize_text(receipt.get("runtime_stage"), limit=80),
        "r4_status": sanitize_text(receipt.get("r4_status", receipt.get("runtime_stage")), limit=80),
        "smoke_type": sanitize_text(receipt.get("smoke_type"), limit=80),
        "smoke_status": sanitize_text(receipt.get("smoke_result", {}).get("status") if isinstance(receipt.get("smoke_result"), dict) else receipt.get("smoke_result"), limit=80),
        "timeout_release_status": "pass" if timeout_release_pass(receipt.get("timeout_release")) else "not-pass",
        "rollback_ready": receipt.get("rollback_ready") is True,
        "process_probe_performed": receipt.get("process_probe_performed") is True,
        "gui_control_performed": receipt.get("gui_control_performed") is True,
        "sends_messages": receipt.get("sends_messages") is True,
        "message_body_included": receipt.get("message_body_included") is True,
    }
    if receipt_path is not None:
        summary["receipt_path_hash"] = stable_hash(str(receipt_path))
    return summary

def command_api_status(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ok": True,
        "tool": TOOL_NAME,
        "action": "api.status",
        "control_surface": "WXWork_CLI",
        "default_channel": "api_or_webhook_first",
        "gui_automation_enabled": False,
        "target_process": TARGET_PROCESS,
        "process_probe_performed": False,
        "message_content_included": False,
        "safety": safety_payload(),
    }


def command_webhook_plan(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    if not args.name.strip():
        blockers.append("webhook_name_required")
    if args.secret_ref and re.search(r"(?i)(key|token|secret)[:=]", args.secret_ref):
        blockers.append("secret_ref_must_be_reference_not_value")
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": TOOL_NAME,
        "action": "webhook.plan",
        "control_surface": "WXWork_CLI",
        "webhook_name": sanitize_text(args.name, limit=80),
        "secret_ref_hash": stable_hash(args.secret_ref) if args.secret_ref else "",
        "plan_allowed": not blockers,
        "calls_webhook": False,
        "gui_fallback_required": False,
        "blockers": blockers,
        "safety": safety_payload(),
    }


def command_gui_plan(args: argparse.Namespace) -> dict[str, Any]:
    target = args.target_process or TARGET_PROCESS
    blockers: list[str] = []
    if target != TARGET_PROCESS:
        blockers.append("target_process_must_be_wxwork")
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": TOOL_NAME,
        "action": "gui.plan",
        "target_process": sanitize_text(target, limit=80),
        "target_process_hash": stable_hash(target),
        "live_gui_control_allowed": False,
        "global_lease_required": True,
        "operator_confirmation_required": True,
        "timeout_release_required": True,
        "api_or_webhook_preferred": True,
        "blockers": blockers,
        "safety": safety_payload(),
    }


def command_gui_check(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    action = args.action
    if action not in SENSITIVE_ACTIONS:
        blockers.append("unknown_or_unsupported_gui_action")
    auth, auth_load = load_json(args.authorization_receipt)
    lease, lease_load = load_json(args.lease_receipt)
    if auth_load:
        blockers.extend(auth_load if args.authorization_receipt else ["operator_authorization_receipt_required"])
    if lease_load:
        blockers.extend(lease_load if args.lease_receipt else ["global_wxwork_lease_required"])
    validate_authorization(auth, blockers, action=action, session=args.session)
    validate_lease(lease, blockers, session=args.session)
    ok = not blockers
    return {
        "schema_version": 1,
        "ok": ok,
        "tool": TOOL_NAME,
        "action": action,
        "dispatch_allowed": ok,
        "dry_run_only": True,
        "gui_control_performed": False,
        "target_process": TARGET_PROCESS,
        "target_process_hash": stable_hash(TARGET_PROCESS),
        "owner_lease_verified": ok,
        "authorization_verified": ok,
        "global_lease_required": True,
        "operator_confirmation_required": True,
        "timeout_release_required": True,
        "message_content_included": False,
        "blockers": sorted(set(blockers)),
        "safety": safety_payload(),
    }



def blocked_smoke_payload(blockers: list[str], *, action: str = "smoke-record", transcript: str = "") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ok": False,
        "tool": TOOL_NAME,
        "action": action,
        "receipt_written": False,
        "r4_status": "blocked",
        "smoke_tested": False,
        "gui_control_performed": False,
        "process_probe_performed": False,
        "sends_messages": False,
        "message_body_included": False,
        "external_message_sent": False,
        "timeout_release": {"status": "pass", "released": True},
        "blockers": sorted(set(blockers)),
        "command_transcript": sanitize_text(transcript, limit=1200) if transcript else "",
        "safety": safety_payload(),
    }


def command_smoke_record(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    smoke_type = str(args.smoke_type).strip().lower()
    if smoke_type not in ALLOWED_SMOKE_TYPES:
        blockers.append("smoke_type_not_allowed")
    install_path = Path(args.install_receipt)
    install_receipt, install_load = load_install_receipt(args.install_receipt)
    blockers.extend(install_load)
    blockers.extend(validate_install_receipt(install_receipt))

    target_process = str(args.target_process or "").strip()
    lease_receipt_path = None
    if target_process:
        if target_process != TARGET_PROCESS:
            blockers.append("target_process_must_be_wxwork")
        lease, lease_load = load_json(args.lease_receipt)
        if lease_load:
            blockers.extend(lease_load if args.lease_receipt else ["global_wxwork_lease_required"])
        validate_lease(lease, blockers, session=args.session)
        lease_receipt_path = args.lease_receipt

    if blockers or install_receipt is None:
        return blocked_smoke_payload(blockers)

    command = [str(install_receipt["wrapper_path"]), *ALLOWED_SMOKE_TYPES[smoke_type]]
    timeout_seconds = max(1, int(args.timeout_seconds))
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        transcript = (exc.stdout or "") + "\n" + (exc.stderr or "")
        return blocked_smoke_payload(["smoke_command_timeout"], transcript=transcript)
    except OSError:
        return blocked_smoke_payload(["smoke_command_launch_failed"])

    transcript = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        return blocked_smoke_payload(["smoke_command_failed"], transcript=transcript)

    receipt = build_smoke_receipt(
        install_receipt_path=install_path,
        install_receipt=install_receipt,
        smoke_type=smoke_type,
        session=args.session,
        transcript=transcript,
        timeout_seconds=timeout_seconds,
        target_process=target_process,
        lease_receipt=lease_receipt_path,
    )
    validation_blockers = validate_smoke_receipt(receipt)
    if validation_blockers:
        return blocked_smoke_payload(validation_blockers, transcript=transcript)
    path = write_smoke_receipt(Path(args.receipt_dir), receipt)
    return {
        "schema_version": 1,
        "ok": True,
        "tool": TOOL_NAME,
        "action": "smoke-record",
        "receipt_written": True,
        "receipt_path_hash": stable_hash(str(path)),
        "r4_status": "smoke-tested",
        "smoke_tested": True,
        "smoke_summary": smoke_summary(receipt, receipt_path=path),
        "gui_control_performed": False,
        "process_probe_performed": False,
        "sends_messages": False,
        "message_body_included": False,
        "external_message_sent": False,
        "blockers": [],
        "safety": safety_payload(),
    }


def command_smoke_check(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt, load_blockers = load_json(args.receipt)
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_smoke_receipt(receipt))
    ok = not blockers
    return {
        "schema_version": 1,
        "ok": ok,
        "tool": TOOL_NAME,
        "action": "smoke-check",
        "smoke_receipt_valid": ok,
        "runtime_stage": "R4" if ok else "blocked",
        "r4_status": "smoke-tested" if ok else "blocked",
        "rollback_ready": bool(ok and receipt and receipt.get("rollback_ready") is True),
        "smoke_summary": smoke_summary(receipt, receipt_path=receipt_path) if receipt else {},
        "gui_control_performed": bool(receipt and receipt.get("gui_control_performed") is True),
        "process_probe_performed": bool(receipt and receipt.get("process_probe_performed") is True),
        "sends_messages": bool(receipt and receipt.get("sends_messages") is True),
        "message_body_included": bool(receipt and receipt.get("message_body_included") is True),
        "blockers": sorted(set(blockers)),
        "safety": safety_payload(),
    }

def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WXWork_CLI repo-local governance guard.")
    sub = parser.add_subparsers(dest="command", required=True)

    api = sub.add_parser("api-status", help="Report API/Webhook-first default posture without probing WXWork.")
    api.add_argument("--json", action="store_true")

    webhook = sub.add_parser("webhook-plan", help="Plan webhook usage without calling Enterprise WeChat.")
    webhook.add_argument("--name", required=True)
    webhook.add_argument("--secret-ref", default="")
    webhook.add_argument("--json", action="store_true")

    gui_plan = sub.add_parser("gui-plan", help="Describe GUI gates without controlling WXWork.")
    gui_plan.add_argument("--target-process", default=TARGET_PROCESS)
    gui_plan.add_argument("--json", action="store_true")

    gui_check = sub.add_parser("gui-check", help="Fail-closed sensitive GUI dispatch precheck.")
    gui_check.add_argument("--action", required=True)
    gui_check.add_argument("--session", required=True)
    gui_check.add_argument("--authorization-receipt", default=None)
    gui_check.add_argument("--lease-receipt", default=None)
    gui_check.add_argument("--json", action="store_true")

    smoke_record = sub.add_parser("smoke-record", help="Run bounded R4 help/status/safe-discovery smoke and write a smoke-tested receipt.")
    smoke_record.add_argument("--install-receipt", required=True)
    smoke_record.add_argument("--receipt-dir", required=True)
    smoke_record.add_argument("--smoke-type", choices=sorted(ALLOWED_SMOKE_TYPES), default="help")
    smoke_record.add_argument("--session", required=True)
    smoke_record.add_argument("--target-process", default="")
    smoke_record.add_argument("--lease-receipt", default=None)
    smoke_record.add_argument("--timeout-seconds", type=int, default=10)
    smoke_record.add_argument("--json", action="store_true")

    smoke_check = sub.add_parser("smoke-check", help="Validate an R4 WXWork_CLI smoke-tested receipt without replaying GUI or message actions.")
    smoke_check.add_argument("--receipt", required=True)
    smoke_check.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "api-status":
        payload = command_api_status(args)
    elif args.command == "webhook-plan":
        payload = command_webhook_plan(args)
    elif args.command == "gui-plan":
        payload = command_gui_plan(args)
    elif args.command == "gui-check":
        payload = command_gui_check(args)
    elif args.command == "smoke-record":
        payload = command_smoke_record(args)
    elif args.command == "smoke-check":
        payload = command_smoke_check(args)
    else:  # pragma: no cover
        parser.error(f"unknown command {args.command}")
    emit(payload)
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
