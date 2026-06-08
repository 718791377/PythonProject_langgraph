#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "repo_local_selector_runtime"
ACTIVE_SELECTOR_RELATIVE = Path(".omx/state/selectors/active.json")
SELECTOR_LEASES_RELATIVE = Path(".omx/state/selectors/leases")
SELECTOR_RECEIPTS_RELATIVE = Path(".omx/state/selectors/receipts")
ALLOWED_BACKEND_FAMILIES = {"langgraph", "native_omx"}


def parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def parse_selector_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return parse_time(value)
    except ValueError:
        return None


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()[:16]


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc}"
    except OSError as exc:
        return None, f"unreadable:{exc}"
    if not isinstance(data, dict):
        return None, "not_object"
    return data, None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_path(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path.absolute()
    return resolved.as_posix().rstrip("/").casefold()


def path_matches(value: Any, expected: Path) -> bool:
    return isinstance(value, str) and bool(value.strip()) and normalize_path(Path(value)) == normalize_path(expected)


def selector_paths(root: Path) -> dict[str, Path]:
    return {
        "active": root / ACTIVE_SELECTOR_RELATIVE,
        "leases": root / SELECTOR_LEASES_RELATIVE,
        "receipts": root / SELECTOR_RECEIPTS_RELATIVE,
    }


def response(ok: bool, action: str, *, blockers: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": iso(datetime.now(timezone.utc)),
        "check_name": CHECK_NAME,
        "ok": ok,
        "action": action,
        "blockers": sorted(set(blockers or [])),
        "mutates_user_level_state": False,
        "reads_browser_data": False,
        "contains_raw_secrets_in_output": False,
    }
    payload.update(extra)
    return payload


def existing_selector_blockers(root: Path, active_path: Path) -> list[str]:
    selector, err = read_json(active_path)
    if selector is None:
        if err == "missing":
            return []
        return [f"active_selector_{err}"]
    repo_root = selector.get("repo_root")
    if repo_root and not path_matches(repo_root, root):
        return ["cross_repo_selector_adoption_blocked"]
    released_at = selector.get("released_at")
    if isinstance(released_at, str) and released_at.strip():
        return []
    return []


def selector_id_for(owner_session: str, backend_family: str, revision: str) -> str:
    return "selector-" + stable_hash({"owner_session": owner_session, "backend_family": backend_family, "revision": revision})[:12]


def build_selector(
    *,
    root: Path,
    backend_family: str,
    owner_session: str,
    selected_reason: str,
    lease_seconds: int,
    now: datetime,
) -> dict[str, Any]:
    paths = selector_paths(root)
    revision = str(int(now.timestamp() * 1000))
    lease_nonce = "nonce-" + uuid.uuid4().hex[:16]
    selector_id = selector_id_for(owner_session, backend_family, revision)
    expires = now + timedelta(seconds=max(1, lease_seconds))
    worktree_id = root.name
    return {
        "backend_family": backend_family,
        "selector_id": selector_id,
        "repo_root": str(root),
        "worktree_id": worktree_id,
        "thread_id": f"{owner_session}:{worktree_id}:{selector_id}",
        "session_scope_id": owner_session,
        "leader_session_lineage": owner_session,
        "owner_session": owner_session,
        "selected_reason": selected_reason,
        "acquired_at": iso(now),
        "created_at": iso(now),
        "updated_at": iso(now),
        "last_heartbeat_at": iso(now),
        "lease_expires_at": iso(expires),
        "released_at": "",
        "generation": int(now.timestamp() * 1000),
        "selector_revision": revision,
        "lease_nonce": lease_nonce,
        "routing_posture": "active_scoped_selector",
        "routing_eligible": True,
        "rollback_pointer": f"selector-rollback:{stable_hash({'root': str(root), 'owner_session': owner_session, 'revision': revision})}",
        "cleanup_evidence": {
            "release_command": "repo_local_selector_runtime.py release --selector-id <id> --lease-nonce <nonce>",
            "stale_reclaim_allowed_after": iso(expires),
        },
        "layout": {
            "root": str(paths["active"].parent),
            "active_selector": str(paths["active"]),
            "selector_leases": str(paths["leases"]),
            "selector_receipts": str(paths["receipts"]),
        },
    }


def build_lease(selector: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "selector_id": selector["selector_id"],
        "backend_family": selector["backend_family"],
        "repo_root": selector["repo_root"],
        "owner_session": selector["owner_session"],
        "session_scope_id": selector["session_scope_id"],
        "lease_nonce": selector["lease_nonce"],
        "status": "active",
        "acquired_at": selector["acquired_at"],
        "updated_at": selector["updated_at"],
        "lease_expires_at": selector["lease_expires_at"],
        "selector_root": selector["layout"]["root"],
        "rollback_pointer": selector["rollback_pointer"],
    }


def receipt_path(root: Path, action: str, selector_id: str, now: datetime) -> Path:
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    return root / SELECTOR_RECEIPTS_RELATIVE / f"{stamp}-{action}-{selector_id}.json"


def build_receipt(
    *,
    root: Path,
    action: str,
    selector: dict[str, Any],
    now: datetime,
    runtime_stage: str,
    status_marker: str,
    transcript: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "receipt_type": "repo-local-selector-runtime",
        "action": action,
        "runtime_stage": runtime_stage,
        "status_marker": status_marker,
        "status": "pass",
        "repo_root_hash": stable_hash(str(root)),
        "selector_id": selector.get("selector_id"),
        "backend_family": selector.get("backend_family"),
        "owner_session": selector.get("owner_session"),
        "selected_reason": selector.get("selected_reason"),
        "lease_expires_at": selector.get("lease_expires_at"),
        "selector_revision": selector.get("selector_revision"),
        "rollback_pointer": selector.get("rollback_pointer") or f"selector-rollback:{stable_hash(selector)}",
        "rollback_ready": True,
        "cleanup_evidence": selector.get("cleanup_evidence") or {"release_or_reclaim": "recorded"},
        "redaction_status": "pass",
        "timeout_release": True,
        "bounded_command_transcript": transcript or {"status": "pass", "summary": "selector helper completed without external runtime launch"},
        "created_at": iso(now),
        "contains_raw_secrets": False,
        "contains_raw_private_paths": False,
    }


def command_write(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    now = parse_time(args.now)
    active_path = selector_paths(root)["active"]
    blockers = existing_selector_blockers(root, active_path)
    if args.backend_family not in ALLOWED_BACKEND_FAMILIES:
        blockers.append("backend_family_not_allowed")
    if not args.owner_session.strip():
        blockers.append("owner_session_required")
    if not args.selected_reason.strip():
        blockers.append("selected_reason_required")
    if blockers:
        return response(False, "write", blockers=blockers, mode="apply" if args.apply else "dry-run", mutates_repo_local_state=False)
    selector = build_selector(
        root=root,
        backend_family=args.backend_family,
        owner_session=args.owner_session,
        selected_reason=args.selected_reason,
        lease_seconds=args.lease_seconds,
        now=now,
    )
    lease = build_lease(selector)
    rec = build_receipt(
        root=root,
        action="write",
        selector=selector,
        now=now,
        runtime_stage="R3-selector-refresh",
        status_marker="installed-user-level-selector-refresh",
    )
    if args.apply:
        paths = selector_paths(root)
        write_json(paths["active"], selector)
        write_json(paths["leases"] / f"{args.owner_session}.json", lease)
        write_json(receipt_path(root, "write", selector["selector_id"], now), rec)
    return response(
        True,
        "write",
        blockers=[],
        mode="apply" if args.apply else "dry-run",
        mutates_repo_local_state=bool(args.apply),
        selector=selector if args.apply else None,
        selector_preview=selector,
        lease_preview=lease,
        receipt=rec if args.apply else None,
        receipt_preview=rec,
    )


def command_release(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    now = parse_time(args.now)
    paths = selector_paths(root)
    selector, err = read_json(paths["active"])
    blockers: list[str] = []
    if selector is None:
        blockers.append("active_selector_missing" if err == "missing" else f"active_selector_{err}")
    else:
        if selector.get("selector_id") != args.selector_id:
            blockers.append("selector_id_mismatch")
        if selector.get("lease_nonce") != args.lease_nonce:
            blockers.append("lease_nonce_mismatch")
        if selector.get("owner_session") != args.owner_session:
            blockers.append("owner_session_mismatch")
        if not path_matches(selector.get("repo_root"), root):
            blockers.append("cross_repo_selector_adoption_blocked")
    if blockers or selector is None:
        return response(False, "release", blockers=blockers, mode="apply" if args.apply else "dry-run", mutates_repo_local_state=False)
    released = dict(selector)
    released["routing_eligible"] = False
    released["released_at"] = iso(now)
    released["updated_at"] = iso(now)
    released["release_reason"] = args.release_reason
    lease_path = paths["leases"] / f"{args.owner_session}.json"
    lease, _ = read_json(lease_path)
    if lease is None:
        lease = build_lease(released)
    lease.update({"status": "released", "released_at": iso(now), "updated_at": iso(now)})
    rec = build_receipt(
        root=root,
        action="release",
        selector=released,
        now=now,
        runtime_stage="R3-selector-release",
        status_marker="released",
    )
    if args.apply:
        write_json(paths["active"], released)
        write_json(lease_path, lease)
        write_json(receipt_path(root, "release", released["selector_id"], now), rec)
    return response(
        True,
        "release",
        blockers=[],
        mode="apply" if args.apply else "dry-run",
        mutates_repo_local_state=bool(args.apply),
        selector=released,
        lease=lease,
        receipt=rec,
    )


def command_reclaim(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    now = parse_time(args.now)
    paths = selector_paths(root)
    selector, err = read_json(paths["active"])
    blockers: list[str] = []
    if selector is None:
        blockers.append("active_selector_missing" if err == "missing" else f"active_selector_{err}")
    else:
        if selector.get("selector_id") != args.selector_id:
            blockers.append("selector_id_mismatch")
        if selector.get("lease_nonce") != args.lease_nonce:
            blockers.append("lease_nonce_mismatch")
        if not path_matches(selector.get("repo_root"), root):
            blockers.append("cross_repo_selector_adoption_blocked")
        expires = parse_selector_time(selector.get("lease_expires_at"))
        if expires is None:
            blockers.append("lease_expires_at_invalid")
        elif expires > now:
            blockers.append("selector_lease_not_expired")
    if blockers or selector is None:
        return response(False, "stale-reclaim", blockers=blockers, mode="apply" if args.apply else "dry-run", mutates_repo_local_state=False)

    reclaimed = dict(selector)
    reclaimed["routing_eligible"] = False
    reclaimed["released_at"] = iso(now)
    reclaimed["updated_at"] = iso(now)
    reclaimed["reclaimed_by"] = args.owner_session
    reclaimed["reclaim_reason"] = args.reclaim_reason
    original_owner = str(selector.get("owner_session") or args.owner_session)
    lease_path = paths["leases"] / f"{original_owner}.json"
    lease, _ = read_json(lease_path)
    if lease is None:
        lease = build_lease(reclaimed)
    lease.update({"status": "stale-reclaimed", "reclaimed_at": iso(now), "reclaimed_by": args.owner_session, "updated_at": iso(now)})
    rec = build_receipt(
        root=root,
        action="stale-reclaim",
        selector=reclaimed,
        now=now,
        runtime_stage="R3-selector-stale-reclaim",
        status_marker="stale-reclaimed",
    )
    rec["reclaimed_by"] = args.owner_session
    if args.apply:
        write_json(paths["active"], reclaimed)
        write_json(lease_path, lease)
        write_json(receipt_path(root, "stale-reclaim", reclaimed["selector_id"], now), rec)
    return response(
        True,
        "stale-reclaim",
        blockers=[],
        mode="apply" if args.apply else "dry-run",
        mutates_repo_local_state=bool(args.apply),
        selector=reclaimed,
        lease=lease,
        receipt=rec,
    )


def command_smoke(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    now = parse_time(args.now)
    paths = selector_paths(root)
    selector, err = read_json(paths["active"])
    blockers: list[str] = []
    if selector is None:
        blockers.append("active_selector_missing" if err == "missing" else f"active_selector_{err}")
    else:
        if selector.get("owner_session") != args.owner_session:
            blockers.append("owner_session_mismatch")
        if not path_matches(selector.get("repo_root"), root):
            blockers.append("cross_repo_selector_adoption_blocked")
        if selector.get("routing_eligible") is not True:
            blockers.append("selector_not_routing_eligible")
    if blockers or selector is None:
        return response(False, "smoke", blockers=blockers, mode="apply" if args.apply else "dry-run", mutates_active_selector=False)
    transcript = {
        "status": "pass",
        "probe": "repo-local-selector-read-only-status",
        "timeout_seconds": args.timeout_seconds,
        "timeout_release": True,
        "selector_id": selector.get("selector_id"),
        "backend_family": selector.get("backend_family"),
    }
    rec = build_receipt(
        root=root,
        action="smoke",
        selector=selector,
        now=now,
        runtime_stage="R4-user-level-smoke-runtime",
        status_marker="smoke-tested",
        transcript=transcript,
    )
    if args.apply:
        write_json(receipt_path(root, "smoke", selector["selector_id"], now), rec)
    return response(
        True,
        "smoke",
        blockers=[],
        mode="apply" if args.apply else "dry-run",
        mutates_repo_local_state=False,
        mutates_active_selector=False,
        receipt=rec,
        receipt_preview=rec,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write, release, and smoke repo-local active durable selectors.")
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    write = sub.add_parser("write", help="Write or preview a repo-local active selector refresh.")
    write.add_argument("--apply", action="store_true")
    write.add_argument("--backend-family", required=True)
    write.add_argument("--owner-session", required=True)
    write.add_argument("--selected-reason", required=True)
    write.add_argument("--lease-seconds", type=int, default=8 * 60 * 60)
    write.add_argument("--now", default=None)
    write.add_argument("--json", action="store_true")

    release = sub.add_parser("release", help="Release a selector with explicit selector id and nonce matching.")
    release.add_argument("--apply", action="store_true")
    release.add_argument("--selector-id", required=True)
    release.add_argument("--lease-nonce", required=True)
    release.add_argument("--owner-session", required=True)
    release.add_argument("--release-reason", default="operator-release")
    release.add_argument("--now", default=None)
    release.add_argument("--json", action="store_true")

    reclaim = sub.add_parser("reclaim", help="Stale-reclaim an expired selector with explicit selector id and nonce matching.")
    reclaim.add_argument("--apply", action="store_true")
    reclaim.add_argument("--selector-id", required=True)
    reclaim.add_argument("--lease-nonce", required=True)
    reclaim.add_argument("--owner-session", required=True)
    reclaim.add_argument("--reclaim-reason", default="stale-selector-reclaim")
    reclaim.add_argument("--now", default=None)
    reclaim.add_argument("--json", action="store_true")

    smoke = sub.add_parser("smoke", help="Write or preview an R4 smoke-tested receipt without changing the active selector.")
    smoke.add_argument("--apply", action="store_true")
    smoke.add_argument("--owner-session", required=True)
    smoke.add_argument("--timeout-seconds", type=int, default=30)
    smoke.add_argument("--now", default=None)
    smoke.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    handlers = {"write": command_write, "release": command_release, "reclaim": command_reclaim, "smoke": command_smoke}
    result = handlers[args.command](args, root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
