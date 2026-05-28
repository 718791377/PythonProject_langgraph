#!/usr/bin/env python3
"""Repo-local OpenCLI governance guard.

This helper models the OpenCLI browser-adapter boundary without installing
OpenCLI, launching browsers, connecting to browser targets, or mutating
user-level Codex configuration.  It keeps OpenCLI on-demand and requires a
browser-owner lease for every target-bound action.  Sensitive actions also
require a current one-task authorization receipt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path(os.environ.get("OPENCLI_GOVERNANCE_STATE_DIR", str(Path.home() / ".codex" / "state" / "browser-automation" / "opencli")))
REQUIRED_RECEIPT_FIELDS = ("action", "target", "scope", "expiry", "session", "operator_confirmation")
OPENCLI_PORT_RANGE = range(39300, 39500)
VALID_PORT_LEASE_STATUS = {"pending_bind", "active"}
READ_ONLY_ACTIONS = {
    "adapter.inventory": "read-only OpenCLI adapter inventory",
    "session.inspect": "read-only browser session inspection",
    "page.snapshot": "read-only page snapshot",
    "screenshot.capture": "read-only screenshot capture",
}
SENSITIVE_ACTIONS = {
    "cookie.read": "sensitive cookie read",
    "js.evaluate": "JavaScript execution",
    "mouse.click": "browser click/write action",
    "keyboard.type": "browser typing/write action",
    "page.navigate": "browser navigation/write action",
}
ALLOWED_OWNER_CLASSES = {
    "codex-managed-isolated",
    "codex-managed-project",
    "human-delegated",
}
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
SECRET_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


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


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def state_dir(args: argparse.Namespace) -> Path:
    return Path(args.state_dir) if args.state_dir else DEFAULT_STATE_DIR


def load_registry(owner_state_dir: Path) -> dict[str, Any]:
    registry = owner_state_dir / "registry.json"
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema_version": 1, "registry_revision": 0, "leases": []}
    except json.JSONDecodeError:
        return {"schema_version": 1, "registry_revision": 0, "leases": [], "registry_error": "invalid_json"}
    except OSError:
        return {"schema_version": 1, "registry_revision": 0, "leases": [], "registry_error": "unreadable"}
    if not isinstance(data, dict):
        return {"schema_version": 1, "registry_revision": 0, "leases": [], "registry_error": "not_object"}
    if not isinstance(data.get("leases"), list):
        data["leases"] = []
    return data


def compact_lease(lease: dict[str, Any] | None) -> dict[str, Any] | None:
    if not lease:
        return None
    return {
        "lease_id": lease.get("lease_id"),
        "owner_class": lease.get("owner_class"),
        "project_slug": lease.get("project_slug"),
        "session_id": lease.get("session_id"),
        "target": sanitize_text(lease.get("target", ""), limit=160),
        "lease_expiry": lease.get("lease_expiry"),
        "status": lease.get("status"),
        "profile_path_hash": lease.get("profile_path_hash", ""),
    }


def find_owner_lease(registry: dict[str, Any], *, target: str, session: str, lease_id: str | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    blockers: list[str] = []
    if registry.get("registry_error"):
        return None, [f"owner_registry_{registry['registry_error']}"]

    matches: list[dict[str, Any]] = []
    for item in registry.get("leases", []):
        if not isinstance(item, dict):
            continue
        if item.get("status") != "active":
            continue
        if lease_id and item.get("lease_id") != lease_id:
            continue
        if item.get("target") != target:
            continue
        if item.get("session_id") != session:
            continue
        expiry = parse_time(item.get("lease_expiry"))
        if expiry is not None and expiry <= now_utc():
            continue
        matches.append(item)

    if not matches:
        blockers.append("owner_lease_required")
        return None, blockers
    lease = matches[0]
    if str(lease.get("owner_class", "")) not in ALLOWED_OWNER_CLASSES:
        blockers.append("owner_class_not_allowed_for_opencli")
    return lease, blockers


def validate_authorization_receipt(path: str | None, *, action: str, target: str, session: str) -> tuple[bool, list[str], dict[str, Any]]:
    if not path:
        return False, ["authorization_receipt_required"], {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return False, ["authorization_receipt_missing"], {}
    except json.JSONDecodeError:
        return False, ["authorization_receipt_invalid_json"], {}
    except OSError:
        return False, ["authorization_receipt_unreadable"], {}
    if not isinstance(data, dict):
        return False, ["authorization_receipt_not_object"], {}

    blockers: list[str] = []
    for field in REQUIRED_RECEIPT_FIELDS:
        if field not in data:
            blockers.append(f"authorization_receipt_missing_{field}")
    if data.get("operator_confirmation") is not True:
        blockers.append("authorization_receipt_operator_confirmation_not_true")

    receipt_target = data.get("target")
    if isinstance(receipt_target, str):
        if receipt_target not in {target, "*"}:
            blockers.append("authorization_receipt_target_mismatch")
    else:
        blockers.append("authorization_receipt_target_invalid")

    receipt_session = data.get("session")
    if isinstance(receipt_session, str):
        if receipt_session != session:
            blockers.append("authorization_receipt_session_mismatch")
    else:
        blockers.append("authorization_receipt_session_invalid")

    receipt_action = str(data.get("action", "")).lower()
    if not any(marker in receipt_action for marker in ("opencli", "browser", "tab", "delegate")):
        blockers.append("authorization_receipt_action_not_opencli_or_browser")

    scope = sanitize_text(data.get("scope", ""), limit=200)
    if action not in scope and "sensitive" not in scope.lower() and "*" not in scope:
        blockers.append("authorization_receipt_scope_missing_action")

    parsed_expiry = parse_time(data.get("expiry"))
    if parsed_expiry is None:
        blockers.append("authorization_receipt_expiry_invalid")
    elif parsed_expiry <= now_utc():
        blockers.append("authorization_receipt_expired")

    summary = {
        field: (data.get(field) if field == "operator_confirmation" else sanitize_text(data.get(field, ""), limit=160))
        for field in REQUIRED_RECEIPT_FIELDS
        if field in data
    }
    return not blockers, blockers, summary


def validate_port_policy(args: argparse.Namespace) -> tuple[bool, list[str], dict[str, Any]]:
    blockers: list[str] = []
    requested_port = str(args.port).strip().lower()
    if requested_port != "auto":
        blockers.append("opencli_port_must_be_auto")

    if not args.port_lease_receipt:
        blockers.append("opencli_port_lease_receipt_required")
        return False, blockers, {
            "port": sanitize_text(args.port, limit=32),
            "port_mode": "auto" if requested_port == "auto" else "fixed",
            "lease_verified": False,
            "hard_coded_port_allowed": False,
            "codex_browser_opencli_range": "39300-39499",
        }

    try:
        data = json.loads(Path(args.port_lease_receipt).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return False, blockers + ["opencli_port_lease_receipt_missing"], {}
    except json.JSONDecodeError:
        return False, blockers + ["opencli_port_lease_receipt_invalid_json"], {}
    except OSError:
        return False, blockers + ["opencli_port_lease_receipt_unreadable"], {}

    if not isinstance(data, dict):
        return False, blockers + ["opencli_port_lease_receipt_not_object"], {}

    if data.get("tool") != "codex-port":
        blockers.append("opencli_port_lease_tool_mismatch")
    if data.get("owner") != "codex":
        blockers.append("opencli_port_lease_owner_mismatch")
    if data.get("status") not in VALID_PORT_LEASE_STATUS:
        blockers.append("opencli_port_lease_status_not_active_or_pending")
    if data.get("sanitized") is not True:
        blockers.append("opencli_port_lease_not_sanitized")
    if not data.get("lease_id"):
        blockers.append("opencli_port_lease_id_missing")

    try:
        leased_port = int(data.get("port"))
    except (TypeError, ValueError):
        leased_port = None
        blockers.append("opencli_port_lease_port_invalid")
    if leased_port is not None and leased_port not in OPENCLI_PORT_RANGE:
        blockers.append("opencli_port_lease_range_mismatch")

    summary = {
        "port": "auto",
        "port_mode": "auto" if requested_port == "auto" else "fixed",
        "lease_verified": not blockers,
        "hard_coded_port_allowed": False,
        "codex_browser_opencli_range": "39300-39499",
        "lease_id": sanitize_text(data.get("lease_id", ""), limit=64),
        "lease_status": sanitize_text(data.get("status", ""), limit=32),
        "owner": sanitize_text(data.get("owner", ""), limit=32),
        "leased_port": leased_port,
    }
    return not blockers, blockers, summary


def classify_action(action: str) -> dict[str, Any]:
    if action in READ_ONLY_ACTIONS:
        return {
            "known": True,
            "sensitive": False,
            "action_kind": "read-only",
            "description": READ_ONLY_ACTIONS[action],
        }
    if action in SENSITIVE_ACTIONS:
        return {
            "known": True,
            "sensitive": True,
            "action_kind": "sensitive",
            "description": SENSITIVE_ACTIONS[action],
        }
    return {
        "known": False,
        "sensitive": True,
        "action_kind": "unknown",
        "description": "unknown action is treated as sensitive and blocked",
    }


def build_safety(action: str, classification: dict[str, Any], adapter_mode: str, *, uses_port_auto: bool) -> dict[str, Any]:
    return {
        "governance_check_only": True,
        "adapter_mode": adapter_mode,
        "on_demand_required": True,
        "autoload_allowed": False,
        "installs_opencli": False,
        "starts_opencli": False,
        "launches_browser": False,
        "connects_to_browser": False,
        "reads_cookies": False,
        "executes_javascript": False,
        "clicks_or_types": False,
        "navigates": False,
        "mutates_browser_state": False,
        "raw_profile_paths_in_output": False,
        "human_owned_direct_binding_allowed": False,
        "hard_coded_port_allowed": False,
        "requires_codex_port_lease_receipt": True,
        "uses_port_auto": uses_port_auto,
        "requested_action_would_read_cookies": action == "cookie.read",
        "requested_action_would_execute_javascript": action == "js.evaluate",
        "requested_action_would_click_or_type": action in {"mouse.click", "keyboard.type"},
        "requested_action_would_navigate": action == "page.navigate",
        "requested_action_is_sensitive": bool(classification["sensitive"]),
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    action = args.action_name
    classification = classify_action(action)
    blockers: list[str] = []
    authorization_summary: dict[str, Any] = {}

    if args.adapter_mode != "on-demand":
        blockers.append("opencli_must_remain_on_demand")
    if not classification["known"]:
        blockers.append("unknown_action")
    _, port_blockers, port_summary = validate_port_policy(args)
    blockers.extend(port_blockers)

    registry = load_registry(Path(args.owner_state_dir) if args.owner_state_dir else state_dir(args) / "owner-registry")
    owner_lease, owner_blockers = find_owner_lease(registry, target=args.target, session=args.session, lease_id=args.owner_lease_id)
    blockers.extend(owner_blockers)

    if classification["sensitive"]:
        _, auth_blockers, authorization_summary = validate_authorization_receipt(
            args.authorization_receipt,
            action=action,
            target=args.target,
            session=args.session,
        )
        blockers.extend(auth_blockers)

    dispatch_allowed = not blockers
    return {
        "schema_version": 1,
        "ok": dispatch_allowed,
        "tool": "opencli-governance",
        "action": "check",
        "requested_action": action,
        "target": sanitize_text(args.target, limit=160),
        "session": sanitize_text(args.session, limit=120),
        "adapter_mode": args.adapter_mode,
        "action_kind": classification["action_kind"],
        "action_description": classification["description"],
        "dispatch_allowed": dispatch_allowed,
        "owner_required": True,
        "authorization_required": bool(classification["sensitive"]),
        "owner_verified": bool(owner_lease and "owner_lease_required" not in blockers and "owner_class_not_allowed_for_opencli" not in blockers),
        "authorization_verified": bool(classification["sensitive"] and authorization_summary and not any(item.startswith("authorization_receipt_") for item in blockers)),
        "port_policy": port_summary,
        "owner_lease": compact_lease(owner_lease),
        "authorization_receipt": authorization_summary,
        "blockers": blockers,
        "safety": build_safety(action, classification, args.adapter_mode, uses_port_auto=str(args.port).strip().lower() == "auto"),
    }


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenCLI on-demand browser governance guard.")
    parser.add_argument("--state-dir", default=None, help="OpenCLI governance state directory.")
    parser.add_argument("--owner-state-dir", default=None, help="Browser owner registry state directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Check whether an OpenCLI browser action may be dispatched.")
    check.add_argument("--action", dest="action_name", required=True, help="OpenCLI action name, e.g. session.inspect or page.navigate.")
    check.add_argument("--target", required=True, help="Browser owner target key.")
    check.add_argument("--session", required=True, help="Current automation session id.")
    check.add_argument("--adapter-mode", default="on-demand", help="Must remain on-demand in this repo-local guard.")
    check.add_argument("--port", default="auto", help="OpenCLI adapter port policy. Only 'auto' is allowed.")
    check.add_argument("--port-lease-receipt", default=None, help="Path to a sanitized codex-port lease receipt for the OpenCLI adapter.")
    check.add_argument("--owner-lease-id", default=None, help="Optional expected browser owner lease id.")
    check.add_argument("--authorization-receipt", default=None, help="Path to one-task sensitive browser/OpenCLI authorization receipt.")
    check.add_argument("--json", action="store_true", help="Emit JSON.")

    args = parser.parse_args(argv)
    try:
        payload = evaluate(args)
    except Exception as exc:  # pragma: no cover - fail-closed safety net
        payload = {
            "schema_version": 1,
            "ok": False,
            "tool": "opencli-governance",
            "action": "check",
            "dispatch_allowed": False,
            "blockers": ["unexpected_error"],
            "error": sanitize_text(str(exc), limit=240),
            "safety": {
                "governance_check_only": True,
                "adapter_mode": "unknown",
                "on_demand_required": True,
                "autoload_allowed": False,
                "installs_opencli": False,
                "starts_opencli": False,
                "launches_browser": False,
                "connects_to_browser": False,
                "mutates_browser_state": False,
                "raw_profile_paths_in_output": False,
            },
        }
    if args.json:
        emit(payload)
    else:
        print("allowed" if payload.get("dispatch_allowed") else "blocked")
        for blocker in payload.get("blockers", []):
            print(f"blocker: {blocker}")
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
