#!/usr/bin/env python3
"""Repo-local chrome-devtools-mcp managed wrapper MVP.

This wrapper models safe Chrome DevTools MCP browser-profile lanes without
launching Chrome, connecting to CDP, installing user-level wrappers, or editing
Codex configuration. It coordinates with the repo-local browser owner registry
so later user-level install slices can reuse the same ownership and receipt
contract.
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
OWNER_CLASS_ISOLATED = "codex-managed-isolated"
OWNER_CLASS_PROJECT = "codex-managed-project"
TOOL_NAME = "chrome-devtools-mcp-managed"
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
SECRET_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")
REQUIRED_AUTHORIZATION_RECEIPT_FIELDS = ("action", "target", "scope", "expiry", "session", "operator_confirmation")


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


def safe_slug(value: str, fallback: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.") or fallback


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


def project_authorization_receipt_blockers(path: str | None, *, target: str, session: str) -> list[str]:
    if not path:
        return ["authorization_receipt_required"]
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return ["authorization_receipt_missing"]
    except json.JSONDecodeError:
        return ["authorization_receipt_invalid_json"]
    except OSError:
        return ["authorization_receipt_unreadable"]
    if not isinstance(data, dict):
        return ["authorization_receipt_not_object"]

    blockers: list[str] = []
    for field in REQUIRED_AUTHORIZATION_RECEIPT_FIELDS:
        if field not in data:
            blockers.append(f"authorization_receipt_missing_{field}")
    if data.get("operator_confirmation") is not True:
        blockers.append("authorization_receipt_operator_confirmation_not_true")
    receipt_target = data.get("target")
    if isinstance(receipt_target, str) and receipt_target not in {target, "*"}:
        blockers.append("authorization_receipt_target_mismatch")
    elif not isinstance(receipt_target, str):
        blockers.append("authorization_receipt_target_invalid")
    receipt_session = data.get("session")
    if isinstance(receipt_session, str) and receipt_session != session:
        blockers.append("authorization_receipt_session_mismatch")
    elif not isinstance(receipt_session, str):
        blockers.append("authorization_receipt_session_invalid")
    action = str(data.get("action", "")).lower()
    if "browser" not in action and "profile" not in action and "delegate" not in action:
        blockers.append("authorization_receipt_action_not_browser")
    expiry = data.get("expiry")
    if isinstance(expiry, str):
        try:
            parsed = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            if parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc):
                blockers.append("authorization_receipt_expired")
        except ValueError:
            blockers.append("authorization_receipt_expiry_invalid")
    elif "expiry" in data:
        blockers.append("authorization_receipt_expiry_invalid")
    return blockers


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
    return base / "profiles" / "isolated" / safe_slug(project, "project") / safe_slug(session, "session")


def project_profile_path(base: Path, project: str, profile: str) -> Path:
    return base / "profiles" / "project" / safe_slug(project, "project") / safe_slug(profile, "default")


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


def isolated_launch_plan(base: Path, args: argparse.Namespace) -> dict[str, Any]:
    profile = isolated_profile_path(base, args.project, args.session)
    target = f"chrome-devtools-mcp:isolated:{args.project}:{args.session}"
    return profile_launch_plan(
        mode="isolated-session",
        owner_class=OWNER_CLASS_ISOLATED,
        project=args.project,
        session=args.session,
        profile_name=args.session,
        purpose=args.purpose,
        ttl=args.ttl,
        profile=profile,
        target=target,
        retention="temporary-managed-profile",
        cleanup_allowed_after_stale_evidence=True,
        authorization_required_for_reserve=False,
    )


def project_launch_plan(base: Path, args: argparse.Namespace) -> dict[str, Any]:
    profile = project_profile_path(base, args.project, args.profile)
    target = f"chrome-devtools-mcp:project:{args.project}:{args.profile}"
    return profile_launch_plan(
        mode="project-profile",
        owner_class=OWNER_CLASS_PROJECT,
        project=args.project,
        session=args.session,
        profile_name=args.profile,
        purpose=args.purpose,
        ttl=args.ttl,
        profile=profile,
        target=target,
        retention="long-lived-project-profile",
        cleanup_allowed_after_stale_evidence=False,
        authorization_required_for_reserve=True,
    )


def profile_launch_plan(
    *,
    mode: str,
    owner_class: str,
    project: str,
    session: str,
    profile_name: str,
    purpose: str,
    ttl: int,
    profile: Path,
    target: str,
    retention: str,
    cleanup_allowed_after_stale_evidence: bool,
    authorization_required_for_reserve: bool,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "owner_class": owner_class,
        "project_slug": project,
        "session_id": session,
        "profile_name": sanitize_text(profile_name, limit=120),
        "target": sanitize_text(target, limit=180),
        "profile_path_hint": sanitize_text(str(profile), limit=180),
        "profile_path_hash": hash_text(str(profile)),
        "profile_retention": retention,
        "cleanup_allowed_after_stale_evidence": cleanup_allowed_after_stale_evidence,
        "authorization_required_for_reserve": authorization_required_for_reserve,
        "ttl_seconds": int(ttl),
        "purpose": sanitize_text(purpose, limit=180),
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
            "chrome_profile": mode,
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


def reserve_owner_lease(
    *,
    base: Path,
    owner_class: str,
    project: str,
    session: str,
    target: str,
    profile: Path,
    purpose: str,
    ttl: int,
    authorization_receipt: str | None = None,
) -> dict[str, Any]:
    argv = [
        "lease",
        "reserve",
        "--owner-class",
        owner_class,
        "--project",
        project,
        "--session",
        session,
        "--target",
        target,
        "--profile-path",
        str(profile),
        "--purpose",
        purpose,
        "--ttl",
        str(ttl),
    ]
    if authorization_receipt:
        argv.extend(["--authorization-receipt", authorization_receipt])
    return run_owner_registry(base, argv)


def command_isolated_plan(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    return response(True, "isolated-session-plan", dry_run=True, registry_mutated=False, start_performed=False, plan=isolated_launch_plan(base, args))


def command_isolated_reserve(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = isolated_launch_plan(base, args)
    profile = isolated_profile_path(base, args.project, args.session)
    owner = reserve_owner_lease(
        base=base,
        owner_class=OWNER_CLASS_ISOLATED,
        project=args.project,
        session=args.session,
        target=f"chrome-devtools-mcp:isolated:{args.project}:{args.session}",
        profile=profile,
        purpose=args.purpose,
        ttl=args.ttl,
    )
    lease = sanitize_json(owner.get("lease", {}))
    wrapper_receipt = write_wrapper_receipt(
        base,
        "reserve-isolated-session",
        {
            "owner_lease_id": lease.get("lease_id"),
            "owner_class": OWNER_CLASS_ISOLATED,
            "project_slug": args.project,
            "session_id": args.session,
            "target": plan["target"],
            "profile_path_hash": plan["profile_path_hash"],
            "start_performed": False,
            "connects_to_cdp": False,
            "mutates_user_codex_config": False,
        },
    )
    return response(True, "isolated-session-reserve", dry_run=False, registry_mutated=True, start_performed=False, plan=plan, owner_lease=lease, wrapper_receipt=wrapper_receipt)


def command_isolated_start(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = isolated_launch_plan(base, args)
    return fail_or_dry_run_start(args, action="isolated-session-start", plan=plan, requires_project_authorization=False)


def command_project_plan(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    return response(True, "project-profile-plan", dry_run=True, registry_mutated=False, start_performed=False, plan=project_launch_plan(base, args))


def command_project_reserve(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = project_launch_plan(base, args)
    profile = project_profile_path(base, args.project, args.profile)
    owner = reserve_owner_lease(
        base=base,
        owner_class=OWNER_CLASS_PROJECT,
        project=args.project,
        session=args.session,
        target=f"chrome-devtools-mcp:project:{args.project}:{args.profile}",
        profile=profile,
        purpose=args.purpose,
        ttl=args.ttl,
        authorization_receipt=args.authorization_receipt,
    )
    lease = sanitize_json(owner.get("lease", {}))
    wrapper_receipt = write_wrapper_receipt(
        base,
        "reserve-project-profile",
        {
            "owner_lease_id": lease.get("lease_id"),
            "owner_class": OWNER_CLASS_PROJECT,
            "project_slug": args.project,
            "session_id": args.session,
            "target": plan["target"],
            "profile_path_hash": plan["profile_path_hash"],
            "profile_retention": plan["profile_retention"],
            "cleanup_allowed_after_stale_evidence": False,
            "authorization_receipt_required": True,
            "start_performed": False,
            "connects_to_cdp": False,
            "mutates_user_codex_config": False,
        },
    )
    return response(True, "project-profile-reserve", dry_run=False, registry_mutated=True, start_performed=False, plan=plan, owner_lease=lease, wrapper_receipt=wrapper_receipt)


def command_project_start(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    plan = project_launch_plan(base, args)
    return fail_or_dry_run_start(args, action="project-profile-start", plan=plan, requires_project_authorization=True)


def fail_or_dry_run_start(args: argparse.Namespace, *, action: str, plan: dict[str, Any], requires_project_authorization: bool) -> dict[str, Any]:
    if args.dry_run:
        return response(True, f"{action}-dry-run", dry_run=True, registry_mutated=False, start_performed=False, plan=plan)
    if requires_project_authorization:
        authorization_blockers = project_authorization_receipt_blockers(args.authorization_receipt, target=str(plan["target"]), session=str(plan["session_id"]))
    else:
        authorization_blockers = []
    if authorization_blockers:
        raise ManagedWrapperError(
            "project_profile_authorization_required",
            "Project-profile live start requires a current project-profile authorization receipt.",
            exit_code=3,
            details={"start_performed": False, "authorization_blockers": authorization_blockers, "plan": plan},
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
        "Repo-local MVP records the profile contract only; user-level live start is deferred to a later governed install slice.",
        exit_code=4,
        details={"start_performed": False, "plan": plan},
    )


def command_release(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner = run_owner_registry(base, ["lease", "release", "--lease-id", args.lease_id, "--session", args.session])
    lease = sanitize_json(owner.get("lease", {}))
    action = "release-project-profile" if lease.get("owner_class") == OWNER_CLASS_PROJECT else "release-isolated-session"
    wrapper_receipt = write_wrapper_receipt(base, action, {"owner_lease_id": args.lease_id, "session_id": args.session, "status": "released"})
    return response(True, "profile-release", registry_mutated=True, start_performed=False, owner_lease=lease, wrapper_receipt=wrapper_receipt)


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner_class = OWNER_CLASS_PROJECT if getattr(args, "profile_mode", "isolated") == "project" else OWNER_CLASS_ISOLATED
    owner = run_owner_registry(base, ["lease", "list", "--owner-class", owner_class])
    leases = sanitize_json(owner.get("leases", []))
    action = "project-profile-status" if owner_class == OWNER_CLASS_PROJECT else "isolated-session-status"
    return response(True, action, registry_mutated=False, start_performed=False, leases=leases)


def command_stale_scan(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner = run_owner_registry(base, ["stale-scan", "--dry-run"])
    candidates = sanitize_json(owner.get("stale_candidates", []))
    return response(
        True,
        "stale-scan",
        dry_run=True,
        registry_mutated=False,
        start_performed=False,
        cleanup_performed=False,
        managed_profiles_only=True,
        stale_candidates=candidates,
    )


def command_cleanup_dry_run(args: argparse.Namespace) -> dict[str, Any]:
    base = state_dir(args)
    owner = run_owner_registry(base, ["cleanup", "dry-run"])
    return response(
        True,
        "cleanup-dry-run",
        dry_run=True,
        registry_mutated=False,
        start_performed=False,
        cleanup_performed=False,
        human_owned_cleanup_performed=False,
        managed_profiles_only=True,
        cleanup_candidates=sanitize_json(owner.get("cleanup_candidates", [])),
        protected_profiles=sanitize_json(owner.get("protected_profiles", [])),
        deleted_profiles=sanitize_json(owner.get("deleted_profiles", [])),
    )


def add_common_session_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--purpose", default="chrome-devtools-mcp isolated managed session")
    parser.add_argument("--ttl", type=int, default=900)


def add_common_project_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True)
    parser.add_argument("--profile", default="default")
    parser.add_argument("--session", required=True)
    parser.add_argument("--purpose", default="chrome-devtools-mcp project profile session")
    parser.add_argument("--ttl", type=int, default=900)
    parser.add_argument("--authorization-receipt")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chrome-devtools-mcp-managed", description="Repo-local chrome-devtools-mcp managed wrapper MVP")
    parser.add_argument("--state-dir", help="State directory for wrapper receipts and owner registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    isolated = sub.add_parser("isolated-session")
    isolated_sub = isolated.add_subparsers(dest="isolated_command", required=True)

    plan = isolated_sub.add_parser("plan")
    add_common_session_args(plan)
    plan.set_defaults(func=command_isolated_plan)

    reserve = isolated_sub.add_parser("reserve")
    add_common_session_args(reserve)
    reserve.set_defaults(func=command_isolated_reserve)

    start = isolated_sub.add_parser("start")
    add_common_session_args(start)
    start.add_argument("--dry-run", action="store_true")
    start.add_argument("--install-receipt")
    start.set_defaults(func=command_isolated_start)

    release = isolated_sub.add_parser("release")
    release.add_argument("--lease-id", required=True)
    release.add_argument("--session", required=True)
    release.set_defaults(func=command_release)

    status = isolated_sub.add_parser("status")
    status.set_defaults(func=command_status, profile_mode="isolated")

    project = sub.add_parser("project-profile")
    project_sub = project.add_subparsers(dest="project_command", required=True)

    project_plan = project_sub.add_parser("plan")
    add_common_project_args(project_plan)
    project_plan.set_defaults(func=command_project_plan)

    project_reserve = project_sub.add_parser("reserve")
    add_common_project_args(project_reserve)
    project_reserve.set_defaults(func=command_project_reserve)

    project_start = project_sub.add_parser("start")
    add_common_project_args(project_start)
    project_start.add_argument("--dry-run", action="store_true")
    project_start.add_argument("--install-receipt")
    project_start.set_defaults(func=command_project_start)

    project_release = project_sub.add_parser("release")
    project_release.add_argument("--lease-id", required=True)
    project_release.add_argument("--session", required=True)
    project_release.set_defaults(func=command_release)

    project_status = project_sub.add_parser("status")
    project_status.set_defaults(func=command_status, profile_mode="project")

    stale = sub.add_parser("stale-scan")
    stale.add_argument("--dry-run", action="store_true", required=True)
    stale.set_defaults(func=command_stale_scan)

    cleanup = sub.add_parser("cleanup")
    cleanup_sub = cleanup.add_subparsers(dest="cleanup_command", required=True)
    cleanup_dry_run = cleanup_sub.add_parser("dry-run")
    cleanup_dry_run.set_defaults(func=command_cleanup_dry_run)
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
    action = getattr(args, "isolated_command", None) or getattr(args, "project_command", None) or getattr(args, "cleanup_command", None) or args.command
    try:
        emit(args.func(args))
        return 0
    except ManagedWrapperError as exc:
        emit(response(False, action, error=exc.code, message=exc.message, **sanitize_json(exc.details)))
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
