#!/usr/bin/env python3
"""Validate durable-routing R4 smoke receipts without adopting durable state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "durable_routing_smoke_receipts"
ALLOWED_RUNTIME_STAGES = {"r4", "smoke-tested", "smoke_tested"}
ALLOWED_CANDIDATE_BACKENDS = {"native_omx", "langgraph", "no_durable_team"}
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "not_required"}
MAX_TRANSCRIPT_CHARS = 4000
MAX_TIMEOUT_SECONDS = 120
FALSE_FIELDS = (
    "adoption_performed",
    "durable_workflow_selected",
    "durable_workflow_running",
    "durable_workflow_adopted",
    "mutation_allowed",
    "user_level_state_mutated",
    "durable_state_mutated",
    "durable_team_launched",
    "omx_apply_performed",
    "langgraph_thread_started",
    "remote_publication_authorized",
)
SECRET_VALUE_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")
ADOPTION_STATES = {"selected", "running", "adopted", "launched"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
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


def normalize_stage(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def status_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"pass", "passed", "ok"}
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in {"pass", "passed", "ok"}
    return False


def collect_sensitive_findings(value: Any, *, path: str = "$", findings: list[str] | None = None) -> list[str]:
    findings = findings if findings is not None else []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            child = f"{path}.{key}"
            if key_text in {"raw_transcript", "stdout", "stderr", "selected_backend", "backend_status"} and item not in (None, "", [], {}):
                findings.append(f"raw_or_adoption_field_present:{child}")
            collect_sensitive_findings(item, path=child, findings=findings)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            collect_sensitive_findings(item, path=f"{path}[{idx}]", findings=findings)
    elif isinstance(value, str):
        if SECRET_VALUE_RE.search(value):
            findings.append(f"inline_secret_value:{path}")
        if WINDOWS_PATH_RE.search(value) or UNC_PATH_RE.search(value) or POSIX_PRIVATE_PATH_RE.search(value):
            findings.append(f"raw_private_path:{path}")
    return findings


def require_dict(receipt: dict[str, Any], field: str, blockers: list[str]) -> dict[str, Any]:
    value = receipt.get(field)
    if not isinstance(value, dict):
        blockers.append(f"receipt_{field}_must_be_object")
        return {}
    return value


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if receipt.get("schema_version") != 1:
        blockers.append("receipt_schema_version_must_be_1")
    if receipt.get("receipt_type") != "durable-routing-smoke":
        blockers.append("receipt_type_must_be_durable_routing_smoke")
    if normalize_stage(receipt.get("runtime_stage")) not in ALLOWED_RUNTIME_STAGES:
        blockers.append("receipt_runtime_stage_must_be_r4_or_smoke_tested")
    if normalize_stage(receipt.get("stage")) != "smoke-tested":
        blockers.append("receipt_stage_must_be_smoke_tested")
    if receipt.get("read_only") is not True:
        blockers.append("receipt_read_only_must_be_true")
    if str(receipt.get("routing_mode", "")).strip().lower() != "read_only":
        blockers.append("receipt_routing_mode_must_be_read_only")
    if str(receipt.get("state_write_policy", "")).strip().lower() != "receipt_only":
        blockers.append("receipt_state_write_policy_must_be_receipt_only")
    for field in FALSE_FIELDS:
        if receipt.get(field) is not False:
            blockers.append(f"receipt_{field}_must_be_false")
    if not isinstance(receipt.get("phase"), str) or not receipt.get("phase", "").strip():
        blockers.append("receipt_phase_required")
    if not isinstance(receipt.get("task"), str) or not receipt.get("task", "").strip():
        blockers.append("receipt_task_required")
    if "read-only" not in str(receipt.get("operator_consent_boundary", "")).lower():
        blockers.append("receipt_operator_consent_boundary_must_be_read_only")

    smoke_result = require_dict(receipt, "smoke_result", blockers)
    if smoke_result and not status_pass(smoke_result):
        blockers.append("receipt_smoke_result_must_pass")
    if smoke_result.get("timed_out") is True:
        blockers.append("receipt_smoke_result_must_not_time_out")

    timeout_release = require_dict(receipt, "timeout_release", blockers)
    if timeout_release:
        if not status_pass(timeout_release):
            blockers.append("receipt_timeout_release_must_pass")
        if timeout_release.get("released") is not True:
            blockers.append("receipt_timeout_release_released_must_be_true")
        if timeout_release.get("timed_out") is True:
            blockers.append("receipt_timeout_release_timed_out_must_be_false")
        try:
            timeout_seconds = int(timeout_release.get("timeout_seconds"))
        except (TypeError, ValueError):
            timeout_seconds = 0
        if timeout_seconds <= 0 or timeout_seconds > MAX_TIMEOUT_SECONDS:
            blockers.append("receipt_timeout_seconds_must_be_bounded")

    rollback_pointer = require_dict(receipt, "rollback_pointer", blockers)
    if rollback_pointer:
        if not str(rollback_pointer.get("commit_hash", "")).strip():
            blockers.append("receipt_rollback_pointer_commit_hash_required")
        if str(rollback_pointer.get("status", "")).strip().lower() != "ready":
            blockers.append("receipt_rollback_pointer_status_must_be_ready")
    if receipt.get("rollback_ready") is not True:
        blockers.append("receipt_rollback_ready_must_be_true")

    command_transcript = require_dict(receipt, "command_transcript", blockers)
    if command_transcript:
        try:
            max_chars = int(command_transcript.get("max_excerpt_chars"))
        except (TypeError, ValueError):
            max_chars = 0
        if max_chars <= 0 or max_chars > MAX_TRANSCRIPT_CHARS:
            blockers.append("receipt_transcript_max_excerpt_chars_must_be_bounded")
        for field in ("stdout_excerpt", "stderr_excerpt"):
            value = command_transcript.get(field)
            if not isinstance(value, str):
                blockers.append(f"receipt_command_transcript_{field}_must_be_string")
            elif len(value) > MAX_TRANSCRIPT_CHARS:
                blockers.append(f"receipt_command_transcript_{field}_too_long")
        for field in ("stdout_hash", "stderr_hash"):
            if not isinstance(command_transcript.get(field), str) or not command_transcript.get(field, "").strip():
                blockers.append(f"receipt_command_transcript_{field}_required")
        if command_transcript.get("raw_transcript_omitted") is not True:
            blockers.append("receipt_command_transcript_raw_must_be_omitted")

    redaction = require_dict(receipt, "transcript_redaction", blockers)
    if redaction:
        if str(redaction.get("status", "")).strip().lower() not in ALLOWED_REDACTION_STATUS:
            blockers.append("receipt_transcript_redaction_must_pass")
        if not isinstance(redaction.get("redacted_transcript_hash"), str) or not redaction.get("redacted_transcript_hash", "").strip():
            blockers.append("receipt_redacted_transcript_hash_required")
        if redaction.get("raw_transcript_omitted") is not True:
            blockers.append("receipt_transcript_redaction_raw_must_be_omitted")

    command_safety = require_dict(receipt, "command_safety", blockers)
    if command_safety:
        if command_safety.get("safe_local_command") is not True:
            blockers.append("receipt_command_safety_must_be_safe")
        if command_safety.get("forbidden_apply_markers_detected") is not False:
            blockers.append("receipt_forbidden_apply_markers_must_be_false")
        if command_safety.get("runs_external_tool") is not False:
            blockers.append("receipt_runs_external_tool_must_be_false")

    backend = require_dict(receipt, "backend_family_evidence", blockers)
    if backend:
        candidate = str(backend.get("candidate_backend_family", "")).strip()
        if candidate not in ALLOWED_CANDIDATE_BACKENDS:
            blockers.append("receipt_candidate_backend_family_invalid")
        if str(backend.get("observed_backend_family", "")).strip() != "none":
            blockers.append("receipt_observed_backend_family_must_be_none")
        if str(backend.get("adoption_state", "")).strip().lower() in ADOPTION_STATES:
            blockers.append("receipt_backend_evidence_must_not_claim_adoption")
        if backend.get("adoption_claimed") is not False:
            blockers.append("receipt_backend_adoption_claimed_must_be_false")
        if backend.get("native_omx_launched") is not False:
            blockers.append("receipt_backend_native_omx_launched_must_be_false")
        if backend.get("langgraph_thread_started") is not False:
            blockers.append("receipt_backend_langgraph_thread_started_must_be_false")

    if str(receipt.get("redaction_status", "")).strip().lower() not in ALLOWED_REDACTION_STATUS:
        blockers.append("receipt_redaction_status_must_pass")
    blockers.extend(collect_sensitive_findings(receipt))
    return sorted(set(blockers))


def receipt_summary(receipt: dict[str, Any], *, receipt_path: Path | None = None) -> dict[str, Any]:
    backend = receipt.get("backend_family_evidence") if isinstance(receipt.get("backend_family_evidence"), dict) else {}
    smoke_result = receipt.get("smoke_result") if isinstance(receipt.get("smoke_result"), dict) else {}
    rollback = receipt.get("rollback_pointer") if isinstance(receipt.get("rollback_pointer"), dict) else {}
    transcript_data = receipt.get("command_transcript") if isinstance(receipt.get("command_transcript"), dict) else {}
    return {
        "receipt_path_hash": stable_hash(str(receipt_path))[:16] if receipt_path else "",
        "runtime_stage": "R4" if normalize_stage(receipt.get("runtime_stage")) in ALLOWED_RUNTIME_STAGES else "blocked",
        "stage": normalize_stage(receipt.get("stage")),
        "smoke_status": str(smoke_result.get("status", "")),
        "candidate_backend_family": str(backend.get("candidate_backend_family", "")),
        "adoption_state": str(backend.get("adoption_state", "")),
        "rollback_pointer_hash": stable_hash(rollback.get("commit_hash", ""))[:16],
        "command_transcript_hash": stable_hash(transcript_data)[:16] if transcript_data else "",
        "adoption_performed": receipt.get("adoption_performed") is True,
        "mutation_allowed": receipt.get("mutation_allowed") is True,
        "remote_publication_authorized": receipt.get("remote_publication_authorized") is True,
    }


def valid_fixture() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "receipt_type": "durable-routing-smoke",
        "runtime_stage": "R4",
        "stage": "smoke-tested",
        "generated_at": now_iso(),
        "target_repository_hash": "abc123",
        "phase": "verify-accept",
        "task": "fixture durable routing smoke",
        "operator_consent_boundary": "read-only smoke receipt only",
        "routing_mode": "read_only",
        "mutation_allowed": False,
        "read_only": True,
        "state_write_policy": "receipt_only",
        "validation_path": ["fixture"],
        "rollback_path": ["git revert"],
        "smoke_command": ["python", "tools/check_durable_routing_smoke_gate_template.py", "--json"],
        "smoke_command_hash": "hash",
        "smoke_result": {"status": "pass", "exit_code": 0, "timed_out": False},
        "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30, "timed_out": False},
        "rollback_pointer": {"type": "git-head", "commit_hash": "deadbeef", "status": "ready"},
        "rollback_ready": True,
        "command_transcript": {
            "stdout_excerpt": "{}",
            "stderr_excerpt": "",
            "stdout_hash": "hash1",
            "stderr_hash": "hash2",
            "max_excerpt_chars": 4000,
            "raw_transcript_omitted": True,
        },
        "transcript_redaction": {
            "status": "pass",
            "redacted_transcript_hash": "hash3",
            "raw_private_paths_redacted": True,
            "raw_secrets_redacted": True,
            "raw_transcript_omitted": True,
        },
        "command_safety": {
            "safe_local_command": True,
            "blockers": [],
            "forbidden_apply_markers_detected": False,
            "runs_external_tool": False,
        },
        "backend_family_evidence": {
            "candidate_backend_family": "langgraph",
            "observed_backend_family": "none",
            "adoption_state": "not_adopted",
            "adoption_claimed": False,
            "native_omx_launched": False,
            "langgraph_thread_started": False,
        },
        "adoption_performed": False,
        "durable_workflow_selected": False,
        "durable_workflow_running": False,
        "durable_workflow_adopted": False,
        "user_level_state_mutated": False,
        "durable_state_mutated": False,
        "durable_team_launched": False,
        "omx_apply_performed": False,
        "langgraph_thread_started": False,
        "remote_publication_authorized": False,
        "redaction_status": "pass",
    }


def run_self_test() -> dict[str, Any]:
    fixtures: list[tuple[str, dict[str, Any], bool, list[str]]] = []
    base = valid_fixture()
    fixtures.append(("valid", base, True, []))

    adoption = json.loads(json.dumps(base))
    adoption["adoption_performed"] = True
    adoption["backend_family_evidence"]["adoption_state"] = "running"
    fixtures.append(("adoption_claim", adoption, False, ["adoption_performed", "must_not_claim_adoption"]))

    unbounded = json.loads(json.dumps(base))
    unbounded["command_transcript"]["max_excerpt_chars"] = 999999
    unbounded["command_transcript"]["raw_transcript_omitted"] = False
    fixtures.append(("unbounded_transcript", unbounded, False, ["max_excerpt_chars", "raw_must_be_omitted"]))

    missing_timeout = json.loads(json.dumps(base))
    missing_timeout.pop("timeout_release")
    missing_timeout["rollback_ready"] = False
    fixtures.append(("missing_timeout_and_rollback", missing_timeout, False, ["timeout_release", "rollback_ready"]))

    errors: list[str] = []
    results: list[dict[str, Any]] = []
    for name, receipt, expected_ok, expected_terms in fixtures:
        blockers = validate_receipt(receipt)
        ok = not blockers
        blocker_text = "\n".join(blockers)
        missing_terms = [term for term in expected_terms if term not in blocker_text]
        if ok != expected_ok:
            errors.append(f"fixture:{name}:expected_ok={expected_ok}:actual_ok={ok}")
        if missing_terms:
            errors.append(f"fixture:{name}:missing_expected_terms={','.join(missing_terms)}")
        results.append(
            {
                "name": name,
                "ok": ok,
                "expected_ok": expected_ok,
                "blockers": blockers,
                "missing_expected_terms": missing_terms,
            }
        )
    return {
        "ok": not errors,
        "fixtures": results,
        "errors": errors,
        "counts": {
            "fixtures": len(fixtures),
            "negative_fixtures": sum(1 for _name, _receipt, expected_ok, _terms in fixtures if not expected_ok),
            "errors": len(errors),
        },
    }


def run_check(root: Path, receipt_path: Path | None = None, self_test: bool = True) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    receipt: dict[str, Any] | None = None
    resolved_receipt_path: Path | None = None
    if receipt_path is not None:
        resolved_receipt_path = receipt_path if receipt_path.is_absolute() else root / receipt_path
        receipt, load_errors = read_json(resolved_receipt_path)
        errors.extend(load_errors)
        if receipt is not None:
            errors.extend(validate_receipt(receipt))
    self_test_result: dict[str, Any] | None = None
    if self_test:
        self_test_result = run_self_test()
        errors.extend(f"self_test:{error}" for error in self_test_result["errors"])
    if not errors:
        info.append("Durable routing R4 smoke receipt validation is read-only and fail-closed against adoption claims.")
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "receipt_path_hash": stable_hash(str(resolved_receipt_path))[:16] if resolved_receipt_path else "",
        "receipt_summary": receipt_summary(receipt, receipt_path=resolved_receipt_path) if receipt else {},
        "self_test": self_test_result,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "info": info,
        "mutates_user_level_state": False,
        "launches_durable_team": False,
        "runs_omx_apply": False,
        "starts_langgraph_thread": False,
        "counts": {
            "errors": len(set(errors)),
            "warnings": len(warnings),
            "self_test_fixtures": 0 if self_test_result is None else self_test_result["counts"]["fixtures"],
            "negative_self_test_fixtures": 0 if self_test_result is None else self_test_result["counts"]["negative_fixtures"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate durable routing R4 smoke receipts.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--receipt", default=None, help="Optional receipt path to validate. If omitted, only self-tests run.")
    parser.add_argument("--skip-self-test", action="store_true", help="Skip built-in positive and negative receipt fixtures.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = run_check(Path(args.root), Path(args.receipt) if args.receipt else None, self_test=not args.skip_self_test)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'failed'}")
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
