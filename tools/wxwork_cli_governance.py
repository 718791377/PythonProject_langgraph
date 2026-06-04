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

    args = parser.parse_args(argv)
    if args.command == "api-status":
        payload = command_api_status(args)
    elif args.command == "webhook-plan":
        payload = command_webhook_plan(args)
    elif args.command == "gui-plan":
        payload = command_gui_plan(args)
    elif args.command == "gui-check":
        payload = command_gui_check(args)
    else:  # pragma: no cover
        parser.error(f"unknown command {args.command}")
    emit(payload)
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
