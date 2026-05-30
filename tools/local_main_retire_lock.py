#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "local_main_retire_lock"
LOCK_RELATIVE = Path(".omx/locks/local-main-retire.lock")
ARCHIVE_RELATIVE = Path(".omx/locks/archive")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def repo_path(value: str | None) -> Path:
    return Path(value or ".").resolve()


def lock_path(root: Path) -> Path:
    return root / LOCK_RELATIVE


def archive_dir(root: Path) -> Path:
    return root / ARCHIVE_RELATIVE


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None
    if not isinstance(data, dict):
        raise SystemExit(f"lock file must be a JSON object: {path}")
    return data


def is_expired(data: dict[str, Any], now: datetime | None = None) -> bool:
    expires = parse_timestamp(data.get("expires_at"))
    return bool(expires and expires <= (now or utc_now()))


def payload(ok: bool, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": iso(utc_now()),
        "check_name": CHECK_NAME,
        "ok": ok,
    }
    result.update(extra)
    return result


def print_payload(data: dict[str, Any]) -> int:
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data.get("ok") else 1


def archive_lock(root: Path, data: dict[str, Any], reason: str) -> Path:
    directory = archive_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    nonce = str(data.get("nonce") or "unknown")
    stamp = utc_now().strftime("%Y%m%d-%H%M%S")
    archived = dict(data)
    archived["archived_at"] = iso(utc_now())
    archived["archive_reason"] = reason
    path = directory / f"local-main-retire-{stamp}-{nonce}.json"
    path.write_text(json.dumps(archived, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(path), flags)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise


def cmd_acquire(args: argparse.Namespace) -> int:
    root = repo_path(args.root)
    path = lock_path(root)
    now = utc_now()
    warnings: list[str] = []
    errors: list[str] = []
    existing = read_json(path)
    if existing is not None:
        if not is_expired(existing, now):
            errors.append(f"active local-main retire lock exists: {path}")
            return print_payload(payload(False, action="acquire", lock_path=str(path), errors=errors, warnings=warnings, lock=existing))
        warnings.append(f"stale local-main retire lock exists: {path}")
        if not args.reclaim_stale:
            errors.append("stale lock requires --reclaim-stale before a new lock can be acquired")
            return print_payload(payload(False, action="acquire", lock_path=str(path), errors=errors, warnings=warnings, lock=existing))
        archived = archive_lock(root, existing, "reclaim-stale")
        path.unlink(missing_ok=True)
        warnings.append(f"archived stale lock to {archived}")

    nonce = uuid.uuid4().hex
    lock = {
        "schema_version": 1,
        "lock_name": "local-main-retire",
        "status": "active",
        "owner_session_id": args.session_id,
        "branch": args.branch,
        "worktree": args.worktree,
        "entry_id": args.entry_id,
        "created_at": iso(now),
        "expires_at": iso(now + timedelta(minutes=max(1, args.ttl_minutes))),
        "nonce": nonce,
    }
    try:
        atomic_write(path, lock)
    except FileExistsError:
        errors.append(f"active local-main retire lock appeared during acquire: {path}")
        return print_payload(payload(False, action="acquire", lock_path=str(path), errors=errors, warnings=warnings))
    return print_payload(payload(True, action="acquire", lock_path=str(path), lock=lock, nonce=nonce, errors=[], warnings=warnings))


def cmd_release(args: argparse.Namespace) -> int:
    root = repo_path(args.root)
    path = lock_path(root)
    data = read_json(path)
    errors: list[str] = []
    warnings: list[str] = []
    if data is None:
        errors.append(f"local-main retire lock is missing: {path}")
        return print_payload(payload(False, action="release", lock_path=str(path), errors=errors, warnings=warnings))
    if data.get("nonce") != args.nonce:
        errors.append("lock nonce mismatch; refusing to release a lock owned by another session")
        return print_payload(payload(False, action="release", lock_path=str(path), errors=errors, warnings=warnings, lock=data))
    released = dict(data)
    released["status"] = "released"
    released["released_at"] = iso(utc_now())
    archived = archive_lock(root, released, "release")
    path.unlink(missing_ok=True)
    return print_payload(payload(True, action="release", lock_path=str(path), archived_path=str(archived), lock=released, errors=[], warnings=warnings))


def cmd_status(args: argparse.Namespace) -> int:
    root = repo_path(args.root)
    path = lock_path(root)
    data = read_json(path)
    expired = bool(data and is_expired(data))
    return print_payload(payload(True, action="status", lock_path=str(path), locked=data is not None, expired=expired, lock=data, errors=[], warnings=[]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Acquire, release, or inspect the repo-local local-main retire lock.")
    sub = parser.add_subparsers(dest="command", required=True)

    acquire = sub.add_parser("acquire", help="Acquire the local-main retire lock atomically.")
    acquire.add_argument("--root", default=".")
    acquire.add_argument("--session-id", required=True)
    acquire.add_argument("--branch", required=True)
    acquire.add_argument("--worktree", required=True)
    acquire.add_argument("--entry-id", required=True)
    acquire.add_argument("--ttl-minutes", type=int, default=120)
    acquire.add_argument("--reclaim-stale", action="store_true")
    acquire.set_defaults(func=cmd_acquire)

    release = sub.add_parser("release", help="Release a lock using its nonce.")
    release.add_argument("--root", default=".")
    release.add_argument("--nonce", required=True)
    release.set_defaults(func=cmd_release)

    status = sub.add_parser("status", help="Print lock status.")
    status.add_argument("--root", default=".")
    status.set_defaults(func=cmd_status)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())