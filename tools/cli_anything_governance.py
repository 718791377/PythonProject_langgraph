#!/usr/bin/env python3
"""Repo-local CLI-Anything receipt and harness-boundary governance guard.

This helper models the user-level ``CLI-Anything`` / CLI Hub install and
update evidence contract without cloning repositories, installing wrappers,
running network fetches, mutating user-level Codex configuration, or
hard-loading bulk skills.

It is intentionally a receipt and harness-generation boundary gate, not a live
installer and not a live CLI-Anything runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_NAME = "CLI-Anything"
OWNER_LANE = "cli-anything"
EXPECTED_SOURCE_URLS = {
    "https://github.com/HKUDS/CLI-Anything",
    "https://clianything.cc/",
}
DEFAULT_SOURCE_URL = "https://github.com/HKUDS/CLI-Anything"
DEFAULT_RECEIPT_DIR = Path(
    os.environ.get(
        "CLI_ANYTHING_RECEIPT_DIR",
        str(Path.home() / ".codex" / "state" / "tool-updates"),
    )
)
ALLOWED_STATUSES = {"reference-only", "on-demand", "disabled"}
UNPINNED_REFS = {"", "latest", "head", "main", "master", "trunk"}
REQUIRED_RECEIPT_FIELDS = {
    "schema_version",
    "tool_name",
    "owner_lane",
    "status",
    "source_url",
    "installed_version",
    "pinned_ref",
    "install_path",
    "wrapper_path",
    "state_path",
    "smoke_test_command",
    "smoke_test_result",
    "updater_command",
    "rollback_pointer",
    "last_updated_at",
    "harness_generation_only",
    "hard_loads_skills",
}

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
SECRET_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stable_hash(value: Any, length: int = 16) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:length]


def sanitize_text(value: Any, *, limit: int | None = None) -> str:
    text = str(value)
    text = SECRET_RE.sub(lambda match: match.group(0).split(match.group(1))[0] + "[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit is not None and len(text) > limit:
        suffix = "...[truncated]"
        return text[: max(0, limit - len(suffix))].rstrip() + suffix
    return text


def is_pinned_ref(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    if normalized in UNPINNED_REFS:
        return False
    if normalized.startswith(("refs/heads/", "origin/", "remotes/")):
        return False
    return True


def smoke_status(receipt: dict[str, Any]) -> str:
    result = receipt.get("smoke_test_result")
    if isinstance(result, dict):
        return str(result.get("status", "")).strip().lower()
    if isinstance(result, str):
        return result.strip().lower()
    return ""


def receipt_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool_name": receipt.get("tool_name"),
        "owner_lane": receipt.get("owner_lane"),
        "status": receipt.get("status"),
        "source_url": sanitize_text(receipt.get("source_url", ""), limit=160),
        "installed_version": sanitize_text(receipt.get("installed_version", ""), limit=80),
        "pinned_ref": sanitize_text(receipt.get("pinned_ref", ""), limit=80),
        "install_path_hash": stable_hash(receipt.get("install_path")),
        "wrapper_path_hash": stable_hash(receipt.get("wrapper_path")),
        "state_path_hash": stable_hash(receipt.get("state_path")),
        "smoke_status": smoke_status(receipt),
        "updater_command": sanitize_text(receipt.get("updater_command", ""), limit=160),
        "rollback_pointer_hash": stable_hash(receipt.get("rollback_pointer")),
        "harness_generation_only": receipt.get("harness_generation_only"),
        "hard_loads_skills": receipt.get("hard_loads_skills"),
        "last_updated_at": receipt.get("last_updated_at"),
        "receipt_id": receipt.get("receipt_id", ""),
    }


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
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


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in sorted(REQUIRED_RECEIPT_FIELDS):
        if field not in receipt:
            blockers.append(f"missing_{field}")
    if receipt.get("schema_version") != 1:
        blockers.append("schema_version_must_be_1")
    if receipt.get("tool_name") != TOOL_NAME:
        blockers.append("tool_name_must_be_cli_anything")
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("owner_lane_must_be_cli_anything")
    if receipt.get("status") not in ALLOWED_STATUSES:
        blockers.append("status_must_remain_reference_only_on_demand_or_disabled")
    if receipt.get("source_url") not in EXPECTED_SOURCE_URLS:
        blockers.append("source_url_must_match_expected_cli_anything_source")
    if not is_pinned_ref(receipt.get("pinned_ref")):
        blockers.append("pin_must_be_immutable")
    if receipt.get("installed_version") != receipt.get("pinned_ref"):
        blockers.append("installed_version_must_match_pinned_ref")
    for field in ("install_path", "wrapper_path", "state_path"):
        if not isinstance(receipt.get(field), str) or not receipt.get(field, "").strip():
            blockers.append(f"{field}_required")
    if smoke_status(receipt) != "pass":
        blockers.append("smoke_test_not_passed")
    if not isinstance(receipt.get("smoke_test_command"), str) or not receipt.get("smoke_test_command", "").strip():
        blockers.append("smoke_test_command_required")
    if not isinstance(receipt.get("updater_command"), str) or not receipt.get("updater_command", "").strip():
        blockers.append("updater_command_required")
    if not isinstance(receipt.get("rollback_pointer"), (str, dict)) or not receipt.get("rollback_pointer"):
        blockers.append("rollback_pointer_required")
    if not isinstance(receipt.get("last_updated_at"), str) or not receipt.get("last_updated_at", "").strip():
        blockers.append("last_updated_at_required")
    if receipt.get("harness_generation_only") is not True:
        blockers.append("harness_generation_only_must_be_true")
    if receipt.get("hard_loads_skills") is not False:
        blockers.append("hard_load_skills_must_be_false")
    return blockers


def build_receipt(
    *,
    pin: str,
    source_url: str,
    install_path: str,
    wrapper_path: str,
    state_path: str,
    smoke_command: str,
    smoke_status_value: str,
    rollback_pointer: Any,
    status: str,
    hard_load_skills: bool,
    updater_command: str | None = None,
    previous_receipt_id: str | None = None,
) -> dict[str, Any]:
    timestamp = now_utc()
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "status": status,
        "source_url": source_url,
        "installed_version": pin,
        "pinned_ref": pin,
        "install_path": install_path,
        "wrapper_path": wrapper_path,
        "state_path": state_path,
        "smoke_test_command": smoke_command,
        "smoke_test_result": {
            "status": smoke_status_value,
            "summary": "sanitized help smoke result",
        },
        "updater_command": updater_command or f"cli-anything updater --pin {pin}",
        "rollback_pointer": rollback_pointer,
        "last_updated_at": timestamp,
        "harness_generation_only": True,
        "hard_loads_skills": bool(hard_load_skills),
        "install_performed": False,
        "network_fetch_performed": False,
        "user_level_config_mutated": False,
        "previous_receipt_id": previous_receipt_id or "",
    }
    receipt["receipt_id"] = stable_hash(
        json.dumps(
            {
                "tool_name": receipt["tool_name"],
                "pin": receipt["pinned_ref"],
                "timestamp": timestamp,
                "rollback": receipt["rollback_pointer"],
            },
            sort_keys=True,
        ),
        length=24,
    )
    return receipt


def write_receipt(receipt_dir: Path, receipt: dict[str, Any], filename: str) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / filename
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def safety_payload() -> dict[str, Any]:
    return {
        "governance_receipt_only": True,
        "harness_generation_boundary_only": True,
        "installs_cli_anything": False,
        "updates_cli_anything": False,
        "runs_cli_anything": False,
        "network_fetch_performed": False,
        "mutates_user_level_codex_config": False,
        "hard_loads_skills": False,
        "raw_private_paths_in_output": False,
        "rollback_ready_receipt_required": True,
    }


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    receipt, load_blockers = load_json(Path(args.receipt))
    if receipt is None:
        return {
            "schema_version": 1,
            "ok": False,
            "tool": "cli-anything-governance",
            "action": "validate",
            "receipt_valid": False,
            "receipt_path_hash": stable_hash(args.receipt),
            "blockers": load_blockers,
        }
    blockers = validate_receipt(receipt)
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": "cli-anything-governance",
        "action": "validate",
        "receipt_valid": not blockers,
        "receipt_path_hash": stable_hash(args.receipt),
        "summary": receipt_summary(receipt),
        "blockers": blockers,
        "safety": safety_payload(),
    }


def command_install_record(args: argparse.Namespace) -> dict[str, Any]:
    receipt = build_receipt(
        pin=args.pin,
        source_url=args.source_url,
        install_path=args.install_path,
        wrapper_path=args.wrapper_path,
        state_path=args.state_path,
        smoke_command=args.smoke_command,
        smoke_status_value=args.smoke_status,
        rollback_pointer=args.rollback_pointer,
        status=args.status,
        hard_load_skills=args.hard_load_skills,
    )
    blockers = validate_receipt(receipt)
    if blockers:
        return {
            "schema_version": 1,
            "ok": False,
            "tool": "cli-anything-governance",
            "action": "install-record",
            "receipt_written": False,
            "blockers": blockers,
            "safety": safety_payload(),
        }
    path = write_receipt(Path(args.receipt_dir or DEFAULT_RECEIPT_DIR), receipt, "cli-anything.lock.json")
    return {
        "schema_version": 1,
        "ok": True,
        "tool": "cli-anything-governance",
        "action": "install-record",
        "receipt_written": True,
        "receipt_path_hash": stable_hash(path),
        "summary": receipt_summary(receipt),
        "blockers": [],
        "safety": safety_payload(),
    }


def command_update_plan(args: argparse.Namespace) -> dict[str, Any]:
    current, load_blockers = load_json(Path(args.current_receipt))
    blockers = list(load_blockers)
    if current is not None:
        blockers.extend(validate_receipt(current))
    if not is_pinned_ref(args.new_pin):
        blockers.append("new_pin_must_be_immutable")
    if args.smoke_status.strip().lower() != "pass":
        blockers.append("smoke_result_not_passed")
    if args.hard_load_skills:
        blockers.append("hard_load_skills_must_be_false")
    rollback_pointer = {
        "previous_receipt_id": current.get("receipt_id") if current else "",
        "previous_pin": current.get("pinned_ref") if current else "",
    }
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": "cli-anything-governance",
        "action": "update-plan",
        "staging_fetch_required": True,
        "network_fetch_performed": False,
        "pin_switch_allowed": not blockers,
        "new_pin": sanitize_text(args.new_pin, limit=80),
        "staging_dir_hash": stable_hash(args.staging_dir),
        "rollback_pointer": rollback_pointer,
        "current_receipt": receipt_summary(current) if current else {},
        "blockers": blockers,
        "safety": safety_payload(),
    }


def command_update_record(args: argparse.Namespace) -> dict[str, Any]:
    plan_payload = command_update_plan(argparse.Namespace(**vars(args)))
    if not plan_payload["ok"]:
        plan_payload["action"] = "update-record"
        plan_payload["receipt_written"] = False
        return plan_payload
    current, _ = load_json(Path(args.current_receipt))
    assert current is not None  # guarded by command_update_plan
    rollback_pointer = {
        "previous_receipt_id": current.get("receipt_id", ""),
        "previous_pin": current.get("pinned_ref", ""),
        "previous_receipt_hash": stable_hash(Path(args.current_receipt).read_text(encoding="utf-8-sig")),
    }
    receipt = build_receipt(
        pin=args.new_pin,
        source_url=str(current.get("source_url", DEFAULT_SOURCE_URL)),
        install_path=str(current.get("install_path", "")),
        wrapper_path=str(current.get("wrapper_path", "")),
        state_path=str(current.get("state_path", "")),
        smoke_command=args.smoke_command,
        smoke_status_value=args.smoke_status,
        rollback_pointer=rollback_pointer,
        status=str(current.get("status", "reference-only")),
        hard_load_skills=False,
        updater_command=str(current.get("updater_command", "")) or None,
        previous_receipt_id=str(current.get("receipt_id", "")),
    )
    path = write_receipt(Path(args.receipt_dir or DEFAULT_RECEIPT_DIR), receipt, f"cli-anything.update.{receipt['receipt_id']}.json")
    return {
        "schema_version": 1,
        "ok": True,
        "tool": "cli-anything-governance",
        "action": "update-record",
        "receipt_written": True,
        "receipt_path_hash": stable_hash(path),
        "pin_switch_allowed": True,
        "rollback_pointer": rollback_pointer,
        "summary": receipt_summary(receipt),
        "blockers": [],
        "safety": safety_payload(),
    }


def command_rollback_plan(args: argparse.Namespace) -> dict[str, Any]:
    receipt, load_blockers = load_json(Path(args.receipt))
    blockers = list(load_blockers)
    if receipt is not None:
        blockers.extend(validate_receipt(receipt))
        if not receipt.get("rollback_pointer"):
            blockers.append("rollback_pointer_required")
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": "cli-anything-governance",
        "action": "rollback-plan",
        "rollback_allowed": not blockers,
        "rollback_performed": False,
        "requires_operator_execution": True,
        "rollback_pointer": receipt.get("rollback_pointer") if receipt else {},
        "receipt": receipt_summary(receipt) if receipt else {},
        "blockers": blockers,
        "safety": safety_payload(),
    }


def command_harness_plan(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    if args.hard_load_skills:
        blockers.append("hard_load_skills_must_be_false")
    if not args.capability.strip():
        blockers.append("capability_required")
    return {
        "schema_version": 1,
        "ok": not blockers,
        "tool": "cli-anything-governance",
        "action": "harness-plan",
        "harness_generation_allowed": not blockers,
        "capability": sanitize_text(args.capability, limit=160),
        "output_dir_hash": stable_hash(args.output_dir),
        "target_process": sanitize_text(args.target_process, limit=120) if args.target_process else "",
        "repo_local_source_required": True,
        "authorization_gate_required_for_live_control": True,
        "blockers": blockers,
        "safety": safety_payload(),
    }


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CLI-Anything receipt/update/rollback and harness-boundary governance guard.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a CLI-Anything install/update receipt.")
    validate.add_argument("--receipt", required=True)
    validate.add_argument("--json", action="store_true")

    install = sub.add_parser("install-record", help="Write a pinned install/adaptation receipt without installing CLI-Anything.")
    install.add_argument("--receipt-dir", default=None)
    install.add_argument("--pin", required=True)
    install.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    install.add_argument("--install-path", required=True)
    install.add_argument("--wrapper-path", required=True)
    install.add_argument("--state-path", required=True)
    install.add_argument("--smoke-command", required=True)
    install.add_argument("--smoke-status", default="pass")
    install.add_argument("--rollback-pointer", required=True)
    install.add_argument("--status", default="reference-only")
    install.add_argument("--hard-load-skills", action="store_true")
    install.add_argument("--json", action="store_true")

    update_plan = sub.add_parser("update-plan", help="Plan a pinned update and rollback pointer without fetching or switching pins.")
    update_plan.add_argument("--current-receipt", required=True)
    update_plan.add_argument("--new-pin", required=True)
    update_plan.add_argument("--staging-dir", required=True)
    update_plan.add_argument("--smoke-status", default="pass")
    update_plan.add_argument("--hard-load-skills", action="store_true")
    update_plan.add_argument("--json", action="store_true")

    update_record = sub.add_parser("update-record", help="Write a pinned update receipt after external smoke evidence is available.")
    update_record.add_argument("--current-receipt", required=True)
    update_record.add_argument("--receipt-dir", default=None)
    update_record.add_argument("--new-pin", required=True)
    update_record.add_argument("--staging-dir", required=True)
    update_record.add_argument("--smoke-command", required=True)
    update_record.add_argument("--smoke-status", default="pass")
    update_record.add_argument("--hard-load-skills", action="store_true")
    update_record.add_argument("--json", action="store_true")

    rollback = sub.add_parser("rollback-plan", help="Show rollback evidence without executing rollback.")
    rollback.add_argument("--receipt", required=True)
    rollback.add_argument("--json", action="store_true")

    harness = sub.add_parser("harness-plan", help="Plan harness generation without hard-loading skills or controlling live apps.")
    harness.add_argument("--capability", required=True)
    harness.add_argument("--output-dir", required=True)
    harness.add_argument("--target-process", default="")
    harness.add_argument("--hard-load-skills", action="store_true")
    harness.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        handlers = {
            "validate": command_validate,
            "install-record": command_install_record,
            "update-plan": command_update_plan,
            "update-record": command_update_record,
            "rollback-plan": command_rollback_plan,
            "harness-plan": command_harness_plan,
        }
        payload = handlers[args.command](args)
    except Exception as exc:  # pragma: no cover - fail-closed safety net
        payload = {
            "schema_version": 1,
            "ok": False,
            "tool": "cli-anything-governance",
            "action": getattr(args, "command", "unknown"),
            "blockers": ["unexpected_error"],
            "error": sanitize_text(str(exc), limit=240),
            "safety": safety_payload(),
        }
    if args.json:
        emit(payload)
    else:
        print("ok" if payload.get("ok") else "blocked")
        for blocker in payload.get("blockers", []):
            print(f"blocker: {blocker}")
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
