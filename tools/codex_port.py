#!/usr/bin/env python3
"""Repo-local codex-port allocator MVP.

This helper models the user-level port registry/lease contract without
installing a user-level wrapper. Tests should pass --state-dir so no user-level
state is touched. Runtime wrappers may later set CODEX_PORT_STATE_DIR or use the
user-level default.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import socket
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANGES_FILE = ROOT / "tools" / "codex_port_ranges.json"
DEFAULT_STATE_DIR = Path(os.environ.get("CODEX_PORT_STATE_DIR", str(Path.home() / ".codex" / "state" / "ports")))
VALID_OWNERS = {"codex", "openclaw", "external_reserved"}
WRITE_ACTIONS = {"reserve", "renew", "release", "import-legacy", "gc"}


class CodexPortError(Exception):
    def __init__(self, code: str, message: str, *, exit_code: int = 2) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


@dataclass(frozen=True)
class RangeSpec:
    name: str
    owner: str
    start: int
    end: int
    purpose: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_time(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def json_dump(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def load_ranges(path: Path) -> dict[str, RangeSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    ranges: dict[str, RangeSpec] = {}
    for name, item in raw.get("ranges", {}).items():
        ranges[name] = RangeSpec(
            name=name,
            owner=str(item["owner"]),
            start=int(item["start"]),
            end=int(item["end"]),
            purpose=str(item.get("purpose", "")),
        )
    return ranges


def state_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    state_dir = Path(args.state_dir) if getattr(args, "state_dir", None) else DEFAULT_STATE_DIR
    registry = Path(args.registry) if getattr(args, "registry", None) else state_dir / "registry.json"
    lock = registry.with_suffix(registry.suffix + ".lock")
    return state_dir, registry, lock


def default_registry() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "registry_revision": 0,
        "generated_by": "codex-port repo-local MVP",
        "leases": [],
    }


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_registry()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CodexPortError("registry_corrupt", f"Registry is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("leases", []), list):
        raise CodexPortError("registry_corrupt", "Registry schema is invalid")
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
                raise CodexPortError("registry_lock_timeout", f"Timed out waiting for registry lock: {lock_path}")
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


def is_socket_listening(host: str, port: int, timeout: float = 0.08) -> bool:
    # Fast local availability probe. We never kill or attach to the owner; a
    # failed bind is enough evidence to skip the port for allocation.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return True
    return False


def pid_exists(pid: int | None) -> bool | None:
    if not pid:
        return None
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def lease_active(lease: dict[str, Any], now_ts: float | None = None) -> bool:
    status = lease.get("status")
    if status in {"released", "stale"}:
        return False
    if status == "legacy_reserved":
        return True
    expiry = parse_time(lease.get("lease_expiry"))
    now_ts = time.time() if now_ts is None else now_ts
    if status == "pending_bind" and expiry and expiry < now_ts:
        return True  # fail closed until gc writes evidence
    if status == "active" and expiry and expiry < now_ts:
        return True  # fail closed until stale evidence exists
    return status in {"pending_bind", "active"}


def used_ports(registry: dict[str, Any]) -> set[int]:
    ports: set[int] = set()
    for lease in registry.get("leases", []):
        if lease_active(lease):
            try:
                ports.add(int(lease["port"]))
            except Exception:
                continue
    return ports


def receipt_path(state_dir: Path, action: str, lease_id: str | None = None) -> Path:
    suffix = lease_id or uuid.uuid4().hex[:12]
    safe_action = action.replace("/", "-")
    return state_dir / "receipts" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{safe_action}-{suffix}.json"


def write_receipt(state_dir: Path, action: str, payload: dict[str, Any]) -> str:
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool": "codex-port",
        "action": action,
        "sanitized": True,
        **payload,
    }
    p = receipt_path(state_dir, action, str(payload.get("lease_id", "")) or None)
    atomic_write_json(p, payload)
    return str(p)


def session_or_default(value: str | None) -> str:
    if value:
        return value
    return os.environ.get("CODEX_SESSION_ID") or f"manual-{socket.gethostname()}-{os.getpid()}"


def response(ok: bool, action: str, **kwargs: Any) -> dict[str, Any]:
    return {"ok": ok, "action": action, "tool": "codex-port", **kwargs}


def ensure_owner_range(owner: str, range_spec: RangeSpec) -> None:
    if owner not in VALID_OWNERS:
        raise CodexPortError("invalid_owner", f"Unsupported owner: {owner}")
    if range_spec.owner != owner:
        raise CodexPortError(
            "owner_range_mismatch",
            f"Owner {owner} cannot allocate from range {range_spec.name} owned by {range_spec.owner}",
        )


def command_reserve(args: argparse.Namespace) -> dict[str, Any]:
    ranges = load_ranges(Path(args.ranges_file))
    if args.range not in ranges:
        raise CodexPortError("unknown_range", f"Unknown port range: {args.range}")
    range_spec = ranges[args.range]
    ensure_owner_range(args.owner, range_spec)
    state_dir, registry_path, lock_path = state_paths(args)
    host = args.host
    live_collisions = {p for p in range(range_spec.start, range_spec.end + 1) if is_socket_listening(host, p)}
    lease_id = uuid.uuid4().hex
    owner_session = session_or_default(args.owner_session)
    ttl = int(args.ttl)
    created = now_iso()
    expiry = datetime.fromtimestamp(time.time() + ttl, timezone.utc).isoformat(timespec="seconds")
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        unavailable = used_ports(registry) | live_collisions
        chosen = None
        for port in range(range_spec.start, range_spec.end + 1):
            if port not in unavailable:
                chosen = port
                break
        if chosen is None:
            raise CodexPortError("range_exhausted", f"No available port in range {range_spec.name}")
        lease = {
            "owner": args.owner,
            "project_slug": args.project,
            "tool": args.tool,
            "host": host,
            "port": chosen,
            "lease_id": lease_id,
            "pid": args.pid,
            "created_at": created,
            "renewed_at": created,
            "ttl_seconds": ttl,
            "lease_expiry": expiry,
            "owner_session": owner_session,
            "purpose": args.purpose,
            "status": "pending_bind",
            "range": range_spec.name,
        }
        registry.setdefault("leases", []).append(lease)
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "reserve", {"lease_id": lease_id, "owner": args.owner, "port": chosen, "status": "pending_bind"})
    return response(
        True,
        "reserve",
        lease_id=lease_id,
        owner=args.owner,
        project_slug=args.project,
        tool=args.tool,
        host=host,
        port=chosen,
        status="pending_bind",
        range=range_spec.name,
        lease_expiry=expiry,
        registry=str(registry_path),
        receipt=receipt,
        collision_warnings=[{"port": p, "reason": "live_socket_listening"} for p in sorted(live_collisions)],
        process_kill_performed=False,
    )


def find_lease(registry: dict[str, Any], *, lease_id: str | None = None, port: int | None = None) -> dict[str, Any] | None:
    for lease in registry.get("leases", []):
        if lease_id is not None and lease.get("lease_id") == lease_id:
            return lease
        if port is not None and int(lease.get("port", -1)) == int(port) and lease.get("status") not in {"released", "stale"}:
            return lease
    return None


def command_renew(args: argparse.Namespace) -> dict[str, Any]:
    state_dir, registry_path, lock_path = state_paths(args)
    owner_session = session_or_default(args.owner_session)
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        lease = find_lease(registry, lease_id=args.lease_id)
        if not lease:
            raise CodexPortError("lease_not_found", f"Lease not found: {args.lease_id}")
        if lease.get("owner_session") != owner_session:
            raise CodexPortError("owner_session_mismatch", "Lease owner session does not match; refusing renew")
        renewed = now_iso()
        ttl = int(args.ttl)
        lease["renewed_at"] = renewed
        lease["ttl_seconds"] = ttl
        lease["lease_expiry"] = datetime.fromtimestamp(time.time() + ttl, timezone.utc).isoformat(timespec="seconds")
        if lease.get("status") == "pending_bind" and args.activate:
            lease["status"] = "active"
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "renew", {"lease_id": args.lease_id, "status": lease.get("status"), "port": lease.get("port")})
    return response(True, "renew", lease_id=args.lease_id, status=lease.get("status"), port=lease.get("port"), receipt=receipt)


def command_release(args: argparse.Namespace) -> dict[str, Any]:
    state_dir, registry_path, lock_path = state_paths(args)
    owner_session = session_or_default(args.owner_session)
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        lease = find_lease(registry, port=args.port)
        if not lease:
            raise CodexPortError("lease_not_found", f"No active lease found for port {args.port}")
        if lease.get("owner_session") != owner_session:
            raise CodexPortError("owner_session_mismatch", "Lease owner session does not match; refusing release")
        lease["status"] = "released"
        lease["released_at"] = now_iso()
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "release", {"lease_id": lease.get("lease_id"), "port": args.port, "status": "released"})
    return response(True, "release", lease_id=lease.get("lease_id"), port=args.port, status="released", receipt=receipt)


def command_list(args: argparse.Namespace) -> dict[str, Any]:
    _, registry_path, _ = state_paths(args)
    registry = load_registry(registry_path)
    leases = []
    for lease in registry.get("leases", []):
        if args.owner and lease.get("owner") != args.owner:
            continue
        leases.append({
            "owner": lease.get("owner"),
            "project_slug": lease.get("project_slug"),
            "tool": lease.get("tool"),
            "host": lease.get("host"),
            "port": lease.get("port"),
            "lease_id": lease.get("lease_id"),
            "lease_expiry": lease.get("lease_expiry"),
            "owner_session": lease.get("owner_session"),
            "purpose": lease.get("purpose"),
            "status": lease.get("status"),
            "range": lease.get("range"),
        })
    return response(True, "list", registry=str(registry_path), registry_revision=registry.get("registry_revision", 0), leases=leases)


def command_import_legacy(args: argparse.Namespace) -> dict[str, Any]:
    ranges = load_ranges(Path(args.ranges_file))
    owner = args.owner
    if owner not in {"openclaw", "external_reserved"}:
        raise CodexPortError("invalid_legacy_owner", "Legacy imports are restricted to openclaw or external_reserved")
    state_dir, registry_path, lock_path = state_paths(args)
    lease_id = uuid.uuid4().hex
    owner_session = session_or_default(args.owner_session)
    matching_ranges = [r for r in ranges.values() if r.start <= args.port <= r.end]
    range_name = matching_ranges[0].name if matching_ranges else "external"
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        if find_lease(registry, port=args.port):
            raise CodexPortError("port_already_registered", f"Port {args.port} already has a non-released lease")
        created = now_iso()
        lease = {
            "owner": owner,
            "project_slug": args.project,
            "tool": args.tool,
            "host": args.host,
            "port": args.port,
            "lease_id": lease_id,
            "pid": args.pid,
            "created_at": created,
            "renewed_at": created,
            "ttl_seconds": None,
            "lease_expiry": None,
            "owner_session": owner_session,
            "purpose": args.purpose,
            "status": "legacy_reserved",
            "range": range_name,
        }
        registry.setdefault("leases", []).append(lease)
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "import-legacy", {"lease_id": lease_id, "owner": owner, "port": args.port, "status": "legacy_reserved"})
    return response(True, "import-legacy", lease_id=lease_id, owner=owner, port=args.port, status="legacy_reserved", receipt=receipt)


def stale_candidates(registry: dict[str, Any]) -> list[dict[str, Any]]:
    now_ts = time.time()
    candidates: list[dict[str, Any]] = []
    for lease in registry.get("leases", []):
        status = lease.get("status")
        if status in {"released", "stale", "legacy_reserved"}:
            continue
        expiry_ts = parse_time(lease.get("lease_expiry"))
        expired = bool(expiry_ts and expiry_ts < now_ts)
        pid_state = pid_exists(lease.get("pid"))
        pid_missing = pid_state is False
        if expired or pid_missing:
            candidates.append({
                "lease_id": lease.get("lease_id"),
                "port": lease.get("port"),
                "status": status,
                "expired": expired,
                "pid_missing": pid_missing,
                "reason": "expired_or_pid_missing",
            })
    return candidates


def command_gc(args: argparse.Namespace) -> dict[str, Any]:
    state_dir, registry_path, lock_path = state_paths(args)
    if args.dry_run:
        registry = load_registry(registry_path)
        return response(True, "gc", dry_run=True, registry=str(registry_path), stale_candidates=stale_candidates(registry), receipt=None)
    with registry_lock(lock_path):
        registry = load_registry(registry_path)
        candidates = stale_candidates(registry)
        candidate_ids = {c["lease_id"] for c in candidates}
        for lease in registry.get("leases", []):
            if lease.get("lease_id") in candidate_ids:
                lease["status"] = "stale"
                lease["stale_marked_at"] = now_iso()
        write_registry(registry_path, registry)
    receipt = write_receipt(state_dir, "gc", {"stale_count": len(candidates), "dry_run": False})
    return response(True, "gc", dry_run=False, stale_candidates=candidates, stale_marked=len(candidates), receipt=receipt)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-port", description="Codex user-level port lease allocator MVP")
    parser.add_argument("--state-dir", help="State directory containing registry.json and receipts/.")
    parser.add_argument("--registry", help="Explicit registry JSON path.")
    parser.add_argument("--ranges-file", default=str(DEFAULT_RANGES_FILE), help="Port range configuration JSON.")
    sub = parser.add_subparsers(dest="top_command", required=True)
    lease = sub.add_parser("lease")
    lease_sub = lease.add_subparsers(dest="lease_command", required=True)

    reserve = lease_sub.add_parser("reserve")
    reserve.add_argument("--owner", required=True)
    reserve.add_argument("--project", required=True)
    reserve.add_argument("--tool", required=True)
    reserve.add_argument("--range", required=True)
    reserve.add_argument("--purpose", required=True)
    reserve.add_argument("--ttl", type=int, required=True)
    reserve.add_argument("--host", default="127.0.0.1")
    reserve.add_argument("--pid", type=int)
    reserve.add_argument("--owner-session")
    reserve.set_defaults(func=command_reserve)

    renew = lease_sub.add_parser("renew")
    renew.add_argument("--lease-id", required=True)
    renew.add_argument("--owner-session", required=True)
    renew.add_argument("--ttl", type=int, required=True)
    renew.add_argument("--activate", action="store_true", help="Promote pending_bind to active after owner wrapper binds successfully.")
    renew.set_defaults(func=command_renew)

    release = lease_sub.add_parser("release")
    release.add_argument("--owner-session", required=True)
    release.add_argument("--port", type=int, required=True)
    release.set_defaults(func=command_release)

    list_cmd = lease_sub.add_parser("list")
    list_cmd.add_argument("--owner")
    list_cmd.set_defaults(func=command_list)

    import_legacy = lease_sub.add_parser("import-legacy")
    import_legacy.add_argument("--owner", required=True)
    import_legacy.add_argument("--port", type=int, required=True)
    import_legacy.add_argument("--purpose", required=True)
    import_legacy.add_argument("--project", default="legacy")
    import_legacy.add_argument("--tool", default="legacy")
    import_legacy.add_argument("--host", default="127.0.0.1")
    import_legacy.add_argument("--pid", type=int)
    import_legacy.add_argument("--owner-session")
    import_legacy.set_defaults(func=command_import_legacy)

    gc = lease_sub.add_parser("gc")
    gc.add_argument("--dry-run", action="store_true")
    gc.set_defaults(func=command_gc)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    json_requested = "--json" in argv
    argv = [item for item in argv if item != "--json"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not json_requested:
        json_dump(response(False, "parse", error="json_required", message="codex-port MVP requires --json for deterministic compact output"))
        return 2
    action = getattr(args, "lease_command", getattr(args, "top_command", "unknown"))
    try:
        result = args.func(args)
        json_dump(result)
        return 0
    except CodexPortError as exc:
        json_dump(response(False, action, error=exc.code, message=exc.message, process_kill_performed=False))
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
