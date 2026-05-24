#!/usr/bin/env python3
"""Repo-local chrome-devtools-mcp managed wrapper MVP.

This wrapper models the safe isolated-session lane for Chrome DevTools MCP
without launching Chrome, connecting to CDP, installing user-level wrappers, or
editing Codex configuration. It coordinates with the repo-local browser owner
registry so later user-level install slices can reuse the same ownership and
receipt contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STATE_DIR = Path(
    os.environ.get(
        "CHROME_DEVTOOLS_MCP_MANAGED_STATE_DIR",
        str(Path.home() / ".codex" / "state" / "browser-automation" / "chrome-devtools-mcp"),
    )
)
ROOT = Path(__file__).resolve().parents[1]
OWNER_REGISTRY_SCRIPT = ROOT / "tools" / "browser_owner_registry.py"
OWNER_CLASS = "codex-managed-isolated"
TOOL_NAME = "chrome-devtools-mcp-managed"
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
SECRET_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")


class ManagedWrapperError(Exception):
    def __init__(self, code: str, message: str, *, exit_code: int = 2, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()[:16]


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


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): sanitize_json(v) for k, v in value.items() if str(k) not in {"registry", "receipt"}}
    if isinstance(value, list):
        return [sanitize_json(v) for v in value]
    if isinstance(value, str):
        return sanitize_text(value, limit=240)
    return value


def response(ok: bool, action: str, **kwargs: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ok": ok,
        "tool": TOOL_NAME,
        "action": action,
        "safety": {
            "launches_browser": False,
            "connects_to_cdp": False,
            "mutates_user_codex_config": False,
            "reads_cookies": False,
            "writes_human_owned_profile": False,
            "raw_profile_paths_in_output": False,
            "requires_browser_lane_authorization_for_live_start": True,
        },
        **kwargs,
    }


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def state_dir(args: argparse.Namespace) -> Path:
    return Path(args.state_dir) if getattr(args, "state_dir", None) else DEFAULT_STATE_DIR


def owner_state_dir(base: Path) -> Path:
    return base / "owner-registry"


def isolated_profile_path(base: Path, project: str, session: str) -> Path:
    safe_project = re.sub(r"[^A-Za-z0-9_.-]+", "-", project).strip("-.") or "project"
    safe_session = re.sub(r"[^A-Za-z0-9_.-]+", "-", session).strip("-.") or "session"
    return base / "profiles" / "isolated" / safe_project / safe_session


def wrapper_receipt_path(base: Path, action: str, receipt_id: str | None = None) -> Path:
    suffix = receipt_id or uuid.uuid4().hex[:12]
    return base / "receipts" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{action}-{suffix}.json"


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp_name, path)


def write_wrapper_receipt(base: Path, action: str, payload: dict[str, Any]) -> dict[str, Any]:
    receipt = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool": TOOL_NAME,
        "action": action,
        "sanitized": True,
        **payload,
    }
    receipt_id = str(payload.get("owner_lease_id") or payload.get("session_id") or uuid.uuid4().hex[:12])
    path = wrapper_receipt_path(base, action, receipt_id)
    atomic_write_json(path, receipt)
    return {"receipt_path_hash": hash_text(str(path)), "receipt_written": True}


def launch_plan(base: Path, args: argparse.Namespace) -> dict[str, Any]:
    profile = isolated_profile_path(base, args.project, args.session)
    target = f"chrome-devtools-mcp:isolated:{args.project}:{args.session}"
    return {
        "mode": "isolated-session",
        "owner_class": OWNER_CLASS,
        "project_slug": args.project,
        "session_id": args.session,
        "target": sanitize_text(target, limit=180),
        "profile_path_hint": sanitize_text(str(profile), limit=180),
        "profile_path_hash": hash_text(str(profile)),
        "ttl_seconds": int(args.ttl),
        "purpose": sanitize_text(args.purpose, limit=180),
        "port_policy": {
            "tcp_port_required_by_wrapper": False,
            "chrome_debugging_port": "ephemeral-or-owner-wrapper-managed",
            "codex_browser_range": "39500-39699 if a later user-level wrapper needs a stable TCP lease",
        },
        "upstream": {
            "name": "chrome-devtools-mcp",
            "version_pin_required_before_live_start": True,
            "install_receipt_required_before_live_start": True,
            "live_start_supported_in_repo_local_mvp": False,
        },
        "command_plan": {
            "chrome_profile": "isolated managed profile",
            "profile_path_hash": hash_text(str(profile)),
            "browser_owner_registry_required": True,
            "launch_performed": False,
        },
    }


def run_owner_registry(base: Path, argv: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(OWNER_REGISTRY_SCRIPT), "--state-dir", str(owner_state_dir(base)), *argv, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ManagedWrapperError(
            "owner_registry_invalid_output",
            "browser owner registry did not return valid JSON",
            details={"returncode": proc.returncode, "stderr": sanitize_text(proc.stderr, limit=300)},
        ) from exc
    if proc.returncode != 0 or not payload.get("ok"):
        raise ManagedWrapperError(
            str(payload.get("error") or "owner_registry_failed"),
            sanitize_text(payload.get("message") or "browser owner registry command failed", limit=240),
            exit_code=proc.returncode or 2,
            details={"owner_registry": sanitize_json(payload)},
        )
    return payload


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    return response(
        True,
        "isolated-session-plan",
        dry_run=True,
        registry_mutated=False,
        start_performed=False,
        plan=launch_plan(base, args),
    )


def command_reserve(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = launch_plan(base, args)
    profile = isolated_profile_path(base, args.project, args.session)
    owner = run_owner_registry(
        base,
        [
            "lease",
            "reserve",
            "--owner-class",
            OWNER_CLASS,
            "--project",
            args.project,
            "--session",
            args.session,
            "--target",
            f"chrome-devtools-mcp:isolated:{args.project}:{args.session}",
            "--profile-path",
            str(profile),
            "--purpose",
            args.purpose,
            "--ttl",
            str(args.ttl),
        ],
    )
    lease = sanitize_json(owner.get("lease", {}))
    wrapper_receipt = write_wrapper_receipt(
        base,
        "reserve-isolated-session",
        {
            "owner_lease_id": lease.get("lease_id"),
            "owner_class": OWNER_CLASS,
            "project_slug": args.project,
            "session_id": args.session,
            "target": plan["target"],
            "profile_path_hash": plan["profile_path_hash"],
            "start_performed": False,
            "connects_to_cdp": False,
            "mutates_user_codex_config": False,
        },
    )
    return response(
        True,
        "isolated-session-reserve",
        dry_run=False,
        registry_mutated=True,
        start_performed=False,
        plan=plan,
        owner_lease=lease,
        wrapper_receipt=wrapper_receipt,
    )


def command_start(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = launch_plan(base, args)
    if args.dry_run:
        return response(
            True,
            "isolated-session-start-dry-run",
            dry_run=True,
            registry_mutated=False,
            start_performed=False,
            plan=plan,
        )
    if not args.install_receipt:
        raise ManagedWrapperError(
            "install_receipt_required",
            "Live chrome-devtools-mcp start requires a pinned user-level install receipt and explicit browser-lane authorization.",
            exit_code=3,
            details={"start_performed": False, "plan": plan},
        )
    raise ManagedWrapperError(
        "live_start_not_implemented_repo_local_mvp",
        "Repo-local MVP records the isolated-session contract only; user-level live start is deferred to a later governed install slice.",
        exit_code=4,
        details={"start_performed": False, "plan": plan},
    )


def command_release(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner = run_owner_registry(base, ["lease", "release", "--lease-id", args.lease_id, "--session", args.session])
    lease = sanitize_json(owner.get("lease", {}))
    wrapper_receipt = write_wrapper_receipt(
        base,
        "release-isolated-session",
        {
            "owner_lease_id": args.lease_id,
            "session_id": args.session,
            "status": "released",
        },
    )
    return response(True, "isolated-session-release", registry_mutated=True, start_performed=False, owner_lease=lease, wrapper_receipt=wrapper_receipt)


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner = run_owner_registry(base, ["lease", "list", "--owner-class", OWNER_CLASS])
    leases = sanitize_json(owner.get("leases", []))
    return response(True, "isolated-session-status", registry_mutated=False, start_performed=False, leases=leases)


def add_common_session_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--purpose", default="chrome-devtools-mcp isolated managed session")
    parser.add_argument("--ttl", type=int, default=900)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chrome-devtools-mcp-managed", description="Repo-local chrome-devtools-mcp managed wrapper MVP")
    parser.add_argument("--state-dir", help="State directory for wrapper receipts and owner registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    isolated = sub.add_parser("isolated-session")
    isolated_sub = isolated.add_subparsers(dest="isolated_command", required=True)

    plan = isolated_sub.add_parser("plan")
    add_common_session_args(plan)
    plan.set_defaults(func=command_plan)

    reserve = isolated_sub.add_parser("reserve")
    add_common_session_args(reserve)
    reserve.set_defaults(func=command_reserve)

    start = isolated_sub.add_parser("start")
    add_common_session_args(start)
    start.add_argument("--dry-run", action="store_true")
    start.add_argument("--install-receipt")
    start.set_defaults(func=command_start)

    release = isolated_sub.add_parser("release")
    release.add_argument("--lease-id", required=True)
    release.add_argument("--session", required=True)
    release.set_defaults(func=command_release)

    status = isolated_sub.add_parser("status")
    status.set_defaults(func=command_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    json_requested = "--json" in argv
    argv = [item for item in argv if item != "--json"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not json_requested:
        emit(response(False, "parse", error="json_required", message="chrome-devtools-mcp-managed requires --json"))
        return 2
    action = getattr(args, "isolated_command", None) or args.command
    try:
        emit(args.func(args))
        return 0
    except ManagedWrapperError as exc:
        emit(response(False, action, error=exc.code, message=exc.message, **sanitize_json(exc.details)))
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
