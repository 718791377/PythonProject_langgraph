#!/usr/bin/env python3
"""Repo-local browser owner registry MVP.

This helper models the browser automation ownership contract without launching
Chrome, connecting to CDP, or editing user-level Codex configuration. Tests pass
``--state-dir`` so no user-level state is touched. Later wrappers can reuse the
same registry contract to coordinate chrome-devtools-mcp, CDP Bridge, and
OpenCLI.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STATE_DIR = Path(os.environ.get("BROWSER_OWNER_STATE_DIR", str(Path.home() / ".codex" / "state" / "browser-automation")))
VALID_OWNER_CLASSES = {
    "codex-managed-isolated",
    "codex-managed-project",
    "human-owned",
    "human-delegated",
}
AUTH_REQUIRED_OWNER_CLASSES = {"codex-managed-project", "human-delegated"}
MANAGED_CLEANUP_OWNER_CLASSES = {"codex-managed-isolated"}
REQUIRED_RECEIPT_FIELDS = ("action", "target", "scope", "expiry", "session", "operator_confirmation")
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
TOKEN_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")


class BrowserOwnerError(Exception):
    def __init__(self, code: str, message: str, *, exit_code: int = 2, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_time(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def sanitize_text(value: Any, *, limit: int | None = None) -> str:
    text = str(value)
    text = TOKEN_RE.sub(lambda match: match.group(0).split(match.group(1))[0] + "[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit is not None and len(text) > limit:
        return text[: max(0, limit - len("...[truncated]"))].rstrip() + "...[truncated]"
    return text


def path_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def default_registry() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "registry_revision": 0,
        "generated_by": "browser-owner-registry repo-local MVP",
        "leases": [],
    }


def state_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    state_dir = Path(args.state_dir) if getattr(args, "state_dir", None) else DEFAULT_STATE_DIR
    registry = Path(args.registry) if getattr(args, "registry", None) else state_dir / "registry.json"
    lock = registry.with_suffix(registry.suffix + ".lock")
    return state_dir, registry, lock


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_registry()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BrowserOwnerError("registry_corrupt", f"Registry is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("leases", []), list):
        raise BrowserOwnerError("registry_corrupt", "Registry schema is invalid")
    data.setdefault("schema_version", 1)
    data.setdefault("registry_revision", 0)
    data.setdefault("leases", [])
    return data


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp_name, path)


@contextlib.contextmanager
def registry_lock(lock_path: Path, timeout: float = 5.0):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    fh = None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            fh = os.fdopen(fd, "w", encoding="utf-8")
            fh.write(json.dumps({"pid": os.getpid(), "created_at": now_iso()}))
            fh.flush()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise BrowserOwnerError("registry_lock_timeout", f"Timed out waiting for registry lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if fh:
            fh.close()
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def write_registry(path: Path, data: dict[str, Any]) -> None:
    data["registry_revision"] = int(data.get("registry_revision", 0)) + 1
    data["updated_at"] = now_iso()
    atomic_write_json(path, data)


def receipt_path(state_dir: Path, action: str, lease_id: str | None = None) -> Path:
    suffix = lease_id or uuid.uuid4().hex[:12]
    return state_dir / "receipts" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{action}-{suffix}.json"


def write_receipt(state_dir: Path, action: str, payload: dict[str, Any]) -> str:
    receipt = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool": "browser-owner-registry",
        "action": action,
        "sanitized": True,
        **payload,
    }
    path = receipt_path(state_dir, action, str(payload.get("lease_id", "")) or None)
    atomic_write_json(path, receipt)
    return str(path)


def active_status(lease: dict[str, Any]) -> bool:
    return lease.get("status") == "active"


def active_leases(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [lease for lease in registry.get("leases", []) if isinstance(lease, dict) and active_status(lease)]


def compact_lease(lease: dict[str, Any]) -> dict[str, Any]:
    profile_path = str(lease.get("profile_path", ""))
    return {
        "lease_id": lease.get("lease_id"),
        "owner_class": lease.get("owner_class"),
        "project_slug": lease.get("project_slug"),
        "session_id": lease.get("session_id"),
        "target": sanitize_text(lease.get("target", ""), limit=160),
        "profile_path_hint": sanitize_text(profile_path, limit=160) if profile_path else "",
        "profile_path_hash": lease.get("profile_path_hash") or (path_hash(profile_path) if profile_path else ""),
        "lease_expiry": lease.get("lease_expiry"),
        "status": lease.get("status"),
        "purpose": sanitize_text(lease.get("purpose", ""), limit=160),
        "cleanup_allowed": lease.get("owner_class") in MANAGED_CLEANUP_OWNER_CLASSES,
    }


def validate_authorization_receipt(path: Path, *, target: str, session: str) -> tuple[bool, list[str], dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
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
    if isinstance(receipt_target, str) and receipt_target not in {target, "*"}:
        blockers.append("authorization_receipt_target_mismatch")
    receipt_session = data.get("session")
    if isinstance(receipt_session, str) and receipt_session != session:
        blockers.append("authorization_receipt_session_mismatch")
    action = str(data.get("action", "")).lower()
    if "browser" not in action and "delegate" not in action and "profile" not in action:
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
    summary = {field: sanitize_text(data.get(field, ""), limit=160) if field != "operator_confirmation" else data.get(field) for field in REQUIRED_RECEIPT_FIELDS if field in data}
    return not blockers, blockers, summary


def require_authorization(args: argparse.Namespace, owner_class: str) -> tuple[bool, list[str], dict[str, Any]]:
    if owner_class not in AUTH_REQUIRED_OWNER_CLASSES:
        return True, [], {}
    if not args.authorization_receipt:
        return False, ["authorization_receipt_required"], {}
    return validate_authorization_receipt(Path(args.authorization_receipt), target=args.target, session=args.session)


def stale_candidates(registry: dict[str, Any]) -> list[dict[str, Any]]:
    now_ts = time.time()
    candidates: list[dict[str, Any]] = []
    for lease in active_leases(registry):
        expiry_ts = parse_time(lease.get("lease_expiry"))
        expired = bool(expiry_ts and expiry_ts < now_ts)
        if expired:
            item = compact_lease(lease)
            item["expired"] = True
            item["reason"] = "lease_expired"
            candidates.append(item)
    return candidates


def command_reserve(args: argparse.Namespace) -> dict[str, Any]:
    owner_class = args.owner_class
    if owner_class not in VALID_OWNER_CLASSES:
        raise BrowserOwnerError("invalid_owner_class", f"Unsupported owner class: {owner_class}")
    if owner_class == "human-owned":
        raise BrowserOwnerError("human_owned_not_managed", "human-owned Chrome is not a Codex-managed lease target")
    auth_ok, auth_blockers, auth_summary = require_authorization(args, owner_class)
    if not auth_ok:
        raise BrowserOwnerError(
            "authorization_required",
            "Browser owner class requires a current one-task authorization receipt",
            exit_code=3,
            details={"authorization_blockers": auth_blockers, "authorization_summary": auth_summary},
        )
    state_dir, registry_path, lock_path = state_paths(args)
    profile_hash = path_hash(args.profile_path)
    lease_id = uuid.uuid4().hex
    created = now_iso()
    expiry = datetime.fromtimestamp(time.time() + int(args.ttl), timezone.utc).isoformat(timespec="seconds")
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        for lease in active_leases(registry):
            if lease.get("target") == args.target:
                raise BrowserOwnerError("target_already_owned", "This browser target is already owned by another lease")
            if owner_class == "codex-managed-project" and lease.get("owner_class") == "codex-managed-project" and lease.get("profile_path_hash") == profile_hash:
                raise BrowserOwnerError("project_profile_already_owned", "This project profile is already controlled by another session")
        lease = {
            "lease_id": lease_id,
            "owner_class": owner_class,
            "project_slug": args.project,
            "session_id": args.session,
            "target": args.target,
            "profile_path": args.profile_path,
            "profile_path_hash": profile_hash,
            "created_at": created,
            "renewed_at": created,
            "ttl_seconds": int(args.ttl),
            "lease_expiry": expiry,
            "purpose": args.purpose,
            "status": "active",
            "authorization_summary": auth_summary,
        }
        registry.setdefault("leases", []).append(lease)
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "reserve", {"lease_id": lease_id, "owner_class": owner_class, "target": sanitize_text(args.target, limit=160), "profile_path_hash": profile_hash, "status": "active"})
    return response(True, "reserve", lease=compact_lease(lease), registry=str(registry_path), receipt=receipt, authorization_required=owner_class in AUTH_REQUIRED_OWNER_CLASSES, cleanup_allowed=owner_class in MANAGED_CLEANUP_OWNER_CLASSES)


def find_lease(registry: dict[str, Any], lease_id: str) -> dict[str, Any] | None:
    for lease in registry.get("leases", []):
        if isinstance(lease, dict) and lease.get("lease_id") == lease_id:
            return lease
    return None


def command_renew(args: argparse.Namespace) -> dict[str, Any]:
    state_dir, registry_path, lock_path = state_paths(args)
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        lease = find_lease(registry, args.lease_id)
        if not lease or lease.get("status") != "active":
            raise BrowserOwnerError("lease_not_found", f"Active lease not found: {args.lease_id}")
        if lease.get("session_id") != args.session:
            raise BrowserOwnerError("session_mismatch", "Lease session does not match; refusing renew")
        lease["renewed_at"] = now_iso()
        lease["ttl_seconds"] = int(args.ttl)
        lease["lease_expiry"] = datetime.fromtimestamp(time.time() + int(args.ttl), timezone.utc).isoformat(timespec="seconds")
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "renew", {"lease_id": args.lease_id, "status": "active"})
    return response(True, "renew", lease=compact_lease(lease), receipt=receipt)


def command_release(args: argparse.Namespace) -> dict[str, Any]:
    state_dir, registry_path, lock_path = state_paths(args)
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        lease = find_lease(registry, args.lease_id)
        if not lease or lease.get("status") != "active":
            raise BrowserOwnerError("lease_not_found", f"Active lease not found: {args.lease_id}")
        if lease.get("session_id") != args.session:
            raise BrowserOwnerError("session_mismatch", "Lease session does not match; refusing release")
        lease["status"] = "released"
        lease["released_at"] = now_iso()
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "release", {"lease_id": args.lease_id, "status": "released"})
    return response(True, "release", lease=compact_lease(lease), receipt=receipt)


def command_list(args: argparse.Namespace) -> dict[str, Any]:
    _, registry_path, _ = state_paths(args)
    registry = load_registry(registry_path)
    leases = []
    for lease in registry.get("leases", []):
        if not isinstance(lease, dict):
            continue
        if args.project and lease.get("project_slug") != args.project:
            continue
        if args.owner_class and lease.get("owner_class") != args.owner_class:
            continue
        leases.append(compact_lease(lease))
    return response(True, "list", registry=str(registry_path), registry_revision=registry.get("registry_revision", 0), leases=leases)


def command_stale_scan(args: argparse.Namespace) -> dict[str, Any]:
    _, registry_path, _ = state_paths(args)
    registry = load_registry(registry_path)
    return response(True, "stale-scan", dry_run=True, registry=str(registry_path), stale_candidates=stale_candidates(registry), registry_mutated=False)


def command_cleanup_dry_run(args: argparse.Namespace) -> dict[str, Any]:
    _, registry_path, _ = state_paths(args)
    registry = load_registry(registry_path)
    stale = stale_candidates(registry)
    cleanup_candidates = [item for item in stale if item.get("owner_class") in MANAGED_CLEANUP_OWNER_CLASSES]
    protected = [item for item in stale if item.get("owner_class") not in MANAGED_CLEANUP_OWNER_CLASSES]
    return response(
        True,
        "cleanup-dry-run",
        dry_run=True,
        registry=str(registry_path),
        cleanup_candidates=cleanup_candidates,
        protected_profiles=protected,
        deleted_profiles=[],
        cleanup_performed=False,
        human_owned_cleanup_performed=False,
    )


def response(ok: bool, action: str, **kwargs: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ok": ok,
        "tool": "browser-owner-registry",
        "action": action,
        "safety": {
            "launches_browser": False,
            "connects_to_cdp": False,
            "mutates_user_codex_config": False,
            "raw_profile_paths_in_output": False,
            "human_owned_cleanup_allowed": False,
        },
        **kwargs,
    }


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def add_state_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state-dir", help="State directory containing registry.json and receipts/.")
    parser.add_argument("--registry", help="Explicit registry JSON path.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="browser-owner-registry", description="Browser automation owner registry MVP")
    add_state_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    lease = sub.add_parser("lease")
    lease_sub = lease.add_subparsers(dest="lease_command", required=True)

    reserve = lease_sub.add_parser("reserve")
    reserve.add_argument("--owner-class", required=True)
    reserve.add_argument("--project", required=True)
    reserve.add_argument("--session", required=True)
    reserve.add_argument("--target", required=True, help="Target scope such as tab:<id>, browser:<id>, or profile:<slug>.")
    reserve.add_argument("--profile-path", required=True)
    reserve.add_argument("--purpose", required=True)
    reserve.add_argument("--ttl", type=int, required=True)
    reserve.add_argument("--authorization-receipt")
    reserve.set_defaults(func=command_reserve)

    renew = lease_sub.add_parser("renew")
    renew.add_argument("--lease-id", required=True)
    renew.add_argument("--session", required=True)
    renew.add_argument("--ttl", type=int, required=True)
    renew.set_defaults(func=command_renew)

    release = lease_sub.add_parser("release")
    release.add_argument("--lease-id", required=True)
    release.add_argument("--session", required=True)
    release.set_defaults(func=command_release)

    list_cmd = lease_sub.add_parser("list")
    list_cmd.add_argument("--project")
    list_cmd.add_argument("--owner-class")
    list_cmd.set_defaults(func=command_list)

    stale = sub.add_parser("stale-scan")
    stale.add_argument("--dry-run", action="store_true", required=True)
    stale.set_defaults(func=command_stale_scan)

    cleanup = sub.add_parser("cleanup")
    cleanup_sub = cleanup.add_subparsers(dest="cleanup_command", required=True)
    dry_run = cleanup_sub.add_parser("dry-run")
    dry_run.set_defaults(func=command_cleanup_dry_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    json_requested = "--json" in argv
    argv = [item for item in argv if item != "--json"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not json_requested:
        emit(response(False, "parse", error="json_required", message="browser-owner-registry MVP requires --json"))
        return 2
    action = getattr(args, "lease_command", None) or getattr(args, "cleanup_command", None) or args.command
    try:
        emit(args.func(args))
        return 0
    except BrowserOwnerError as exc:
        emit(response(False, action, error=exc.code, message=exc.message, **exc.details))
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
