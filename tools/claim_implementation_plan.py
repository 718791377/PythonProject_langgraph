#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import check_implementation_plan_claim_lock as claim_lock

DEFAULT_SESSION_PREFIX = "codex-session"
RECEIPT_RELATIVE = Path(".omx/worktree-task-receipt.json")
ROB_SUBDIR = Path(".omx/commit-rob/entries")
DEFAULT_NEXT_ACTION = (
    "Continue implementation in this isolated feature worktree, retire through the local-main gate, "
    "then stop at the remote publication gate."
)
DEFAULT_EXPECTED_MERGE_OR_PAUSE = (
    "Commit the implementation package, run local gates and local MR review, merge into local main after validation, "
    "then stop at the remote publication gate."
)
DEFAULT_IMPLEMENTATION_STAGE = "awaiting_confirmation"
RECEIPT_LIFECYCLE_STATUSES = {
    "active",
    "paused",
    "ready-to-merge",
    "merged-local-main",
    "cleaned",
    "remote-sync-needed",
    "completed",
    "superseded",
}
ROB_TERMINAL_STATES = {"flushed", "superseded"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_branch(root: Path) -> str:
    result = run_git(root, ["branch", "--show-current"])
    return result.stdout.strip() if result.returncode == 0 else ""


def git_head(root: Path, ref: str = "main") -> str:
    result = run_git(root, ["rev-parse", ref])
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def slugify(value: str) -> str:
    value = value.lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9._/-]+", "-", value)
    value = re.sub(r"[-_/]+", "-", value)
    return value.strip("-.") or "implementation-plan"


def normalize_list(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for part in str(value).split(","):
            normalized = claim_lock.normalize_repo_path(part)
            if normalized and normalized not in result:
                result.append(normalized)
    return result


def read_plan_doc_id(root: Path, plan: str) -> str:
    return claim_lock.plan_identity(root, plan)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def validate_plan(root: Path, plan_value: str) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    normalized = claim_lock.validate_plan_path(root, Path("<cli>"), plan_value, errors)
    return normalized, errors


def build_paths(plan: str, paths: list[str] | None) -> list[str]:
    result = normalize_list(paths)
    if plan not in result:
        result.insert(0, plan)
    return result


def build_claim_payload(
    *,
    root: Path,
    plan: str,
    branch: str,
    session_id: str,
    worktree: str,
    expires_hours: int,
    paths: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expires_at = utc_now() + timedelta(hours=max(1, int(expires_hours)))
    payload: dict[str, Any] = {
        "schema_version": 1,
        "session_id": session_id,
        "status": "active",
        "branch": branch,
        "worktree": worktree,
        "task_type": "implementation",
        "implementation_plan": plan,
        "implementation_plan_doc_id": read_plan_doc_id(root, plan),
        "paths": paths,
        "created_at": iso_now(),
        "expires_at": expires_at.isoformat(),
    }
    if extra:
        payload.update(extra)
    return payload


def build_confirmation_payload(args: argparse.Namespace) -> dict[str, Any]:
    confirmed = bool(args.implementation_confirmed_by_user)
    recorded_at = args.implementation_confirmation_recorded_at
    if confirmed and not recorded_at:
        recorded_at = iso_now()
    stage = args.implementation_stage
    if confirmed and stage == DEFAULT_IMPLEMENTATION_STAGE:
        stage = "implementation"
    return {
        "requires_user_confirmation_before_implementation": not args.no_requires_user_confirmation_before_implementation,
        "governance_package_commit": args.governance_package_commit or "",
        "governance_package_merged_to_local_main": bool(args.governance_package_merged_to_local_main),
        "implementation_confirmed_by_user": confirmed,
        "implementation_confirmation_recorded_at": recorded_at,
        "implementation_stage": stage,
    }


def write_claim_with_lock_check(
    *,
    root: Path,
    claims_subdir: Path,
    payload: dict[str, Any],
    force: bool,
    keep_conflicting: bool,
) -> tuple[bool, Path, dict[str, Any] | None, list[str]]:
    claim_path = root / claims_subdir / f"{slugify(str(payload['session_id']))}.json"
    if claim_path.exists() and not force:
        return False, claim_path, None, [f"claim file already exists: {claim_path}"]
    write_json(claim_path, payload)
    check = claim_lock.evaluate(root, claims_subdir)
    if not check["ok"]:
        if not keep_conflicting:
            claim_path.unlink(missing_ok=True)
        return False, claim_path, check, list(check.get("errors") or [])
    return True, claim_path, check, []


def rob_entry_path(root: Path, entry_id: str) -> Path:
    return root / ROB_SUBDIR / f"{slugify(entry_id)}.json"


def load_rob_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    directory = root / ROB_SUBDIR
    if not directory.exists():
        return entries
    for path in sorted(directory.glob("*.json")):
        data = read_json(path)
        if data is None:
            continue
        data["path"] = str(path)
        entries.append(data)
    return entries


def find_rob_entry(root: Path, *, entry_id: str | None = None, session_id: str | None = None) -> dict[str, Any] | None:
    if entry_id:
        path = rob_entry_path(root, entry_id)
        data = read_json(path)
        if data is not None:
            data["path"] = str(path)
            return data
    for entry in load_rob_entries(root):
        if session_id and entry.get("session_id") == session_id:
            return entry
    return None


def write_rob_entry(root: Path, entry: dict[str, Any]) -> Path:
    entry["updated_at"] = iso_now()
    path = rob_entry_path(root, str(entry.get("entry_id", "")))
    write_json(path, entry)
    return path


def load_local_claims(root: Path, claims_subdir: Path) -> list[dict[str, Any]]:
    claim_dir = root / claims_subdir
    claims: list[dict[str, Any]] = []
    if not claim_dir.exists():
        return claims
    for path in sorted(claim_dir.glob("*.json")):
        data = read_json(path)
        if data is None:
            continue
        data["path"] = str(path)
        claims.append(data)
    return claims


def matches_claim(data: dict[str, Any], *, session_id: str | None = None, plan: str | None = None) -> bool:
    if session_id and data.get("session_id") != session_id:
        return False
    if plan and claim_lock.normalize_repo_path(str(data.get("implementation_plan", ""))) != claim_lock.normalize_repo_path(plan):
        return False
    return True


def matching_claims(root: Path, claims_subdir: Path, *, session_id: str | None, plan: str | None) -> list[dict[str, Any]]:
    return [claim for claim in load_local_claims(root, claims_subdir) if matches_claim(claim, session_id=session_id, plan=plan)]


def read_matching_receipt(root: Path, *, session_id: str | None, plan: str | None) -> dict[str, Any] | None:
    path = root / RECEIPT_RELATIVE
    receipt = read_json(path)
    if receipt is None:
        return None
    if session_id and receipt.get("session_id") != session_id:
        return None
    if plan and claim_lock.normalize_repo_path(str(receipt.get("implementation_plan", ""))) != claim_lock.normalize_repo_path(plan):
        return None
    receipt["path"] = str(path)
    return receipt


def print_payload(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def claim(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    plan, errors = validate_plan(root, claim_lock.normalize_repo_path(args.plan))
    if errors or plan is None:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    branch = args.branch or git_branch(root)
    if not branch:
        print(json.dumps({"ok": False, "errors": ["branch is required when it cannot be detected from git"]}, indent=2))
        return 1
    session_id = args.session_id or f"{DEFAULT_SESSION_PREFIX}-{slugify(Path(plan).stem)}"
    paths = build_paths(plan, args.path)
    payload = build_claim_payload(
        root=root,
        plan=plan,
        branch=branch,
        session_id=session_id,
        worktree=str(Path(args.worktree).resolve() if args.worktree else root),
        expires_hours=args.expires_hours,
        paths=paths,
    )
    ok, claim_path, check, write_errors = write_claim_with_lock_check(
        root=root,
        claims_subdir=Path(args.claims_subdir),
        payload=payload,
        force=args.force,
        keep_conflicting=args.keep_conflicting,
    )
    if not ok:
        print(json.dumps({"ok": False, "claim_path": str(claim_path), "check": check, "errors": write_errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "claim_path": str(claim_path), "claim": payload, "check": check}, ensure_ascii=False, indent=2))
    return 0


def start(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    plan, errors = validate_plan(root, claim_lock.normalize_repo_path(args.plan))
    if errors or plan is None:
        return print_payload({"schema_version": 1, "ok": False, "action": "start", "errors": errors})
    branch = args.branch or git_branch(root)
    if not branch:
        return print_payload({"schema_version": 1, "ok": False, "action": "start", "errors": ["branch is required"]})
    session_id = args.session_id or f"{DEFAULT_SESSION_PREFIX}-{slugify(Path(plan).stem)}"
    worktree = str(Path(args.worktree).resolve() if args.worktree else root)
    paths = build_paths(plan, args.path)
    doc_id = read_plan_doc_id(root, plan)
    entry_id = args.rob_entry_id or slugify(f"{session_id}-{doc_id}")
    task_name = args.task_name or f"Implement {doc_id}"
    task_summary = args.task_summary or "Portable no-backend implementation-plan session."
    next_action = args.next_action or DEFAULT_NEXT_ACTION
    expected = args.expected_merge_or_pause or DEFAULT_EXPECTED_MERGE_OR_PAUSE
    document_plan_only = bool(args.document_plan_only)
    requires_code = not document_plan_only and not args.no_requires_code_implementation
    claim_extra = {
        "lifecycle_status": "active",
        "task_name": task_name,
        "task_summary": task_summary,
        "document_plan_only": document_plan_only,
        "requires_code_implementation": requires_code,
        "expected_merge_or_pause": expected,
        "next_action": next_action,
        "requires_local_main_merge": not args.no_requires_local_main_merge,
        "requires_remote_sync": bool(args.requires_remote_sync),
        "remote_publication_authorized": bool(args.remote_publication_authorized),
        "rob_entry_id": entry_id,
    }
    claim_extra.update(build_confirmation_payload(args))
    claim_payload = build_claim_payload(
        root=root,
        plan=plan,
        branch=branch,
        session_id=session_id,
        worktree=worktree,
        expires_hours=args.expires_hours,
        paths=paths,
        extra=claim_extra,
    )
    ok, claim_path, check, write_errors = write_claim_with_lock_check(
        root=root,
        claims_subdir=Path(args.claims_subdir),
        payload=claim_payload,
        force=args.force,
        keep_conflicting=args.keep_conflicting,
    )
    if not ok:
        return print_payload(
            {
                "schema_version": 1,
                "ok": False,
                "action": "start",
                "claim_path": str(claim_path),
                "check": check,
                "errors": write_errors,
            }
        )

    receipt = {
        "schema_version": 1,
        "session_id": session_id,
        "status": "active",
        "lifecycle_status": "active",
        "branch": branch,
        "worktree": worktree,
        "task_name": task_name,
        "task_summary": task_summary,
        "document_plan_only": document_plan_only,
        "requires_code_implementation": requires_code,
        "created_at": claim_payload["created_at"],
        "expected_merge_or_pause": expected,
        "next_action": next_action,
        "requires_local_main_merge": not args.no_requires_local_main_merge,
        "requires_remote_sync": bool(args.requires_remote_sync),
        "remote_publication_authorized": bool(args.remote_publication_authorized),
        "paths": paths,
        "implementation_plan": plan,
        "implementation_plan_doc_id": doc_id,
        "rob_entry_id": entry_id,
    }
    receipt.update(build_confirmation_payload(args))
    receipt_path = root / RECEIPT_RELATIVE
    write_json(receipt_path, receipt)

    rob_entry = {
        "schema_version": 1,
        "entry_id": entry_id,
        "state": "predicted",
        "session_id": session_id,
        "implementation_plan": plan,
        "branch": branch,
        "worktree": worktree,
        "base_main": args.base_main or git_head(root, "main"),
        "predicted_write_set": paths,
        "actual_write_set": [],
        "hotspots": normalize_list(args.hotspot),
        "dependencies": normalize_list(args.dependency),
        "gate_status": {},
        "evidence": [],
        "created_at": claim_payload["created_at"],
        "updated_at": claim_payload["created_at"],
    }
    rob_path = write_rob_entry(root, rob_entry)
    return print_payload(
        {
            "schema_version": 1,
            "ok": True,
            "action": "start",
            "claim_path": str(claim_path),
            "receipt_path": str(receipt_path),
            "rob_entry_path": str(rob_path),
            "claim": claim_payload,
            "receipt": receipt,
            "rob_entry": rob_entry,
            "check": check,
            "portable_no_backend_model": {
                "claim_status": "active",
                "receipt_lifecycle_status": "active",
                "rob_state": "predicted",
                "local_main_serialization_lock": ".omx/locks/local-main-retire.lock",
                "remote_publication_allowed": False,
            },
        }
    )


def status(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    plan = claim_lock.normalize_repo_path(args.plan) if args.plan else None
    claims = matching_claims(root, Path(args.claims_subdir), session_id=args.session_id, plan=plan)
    claim = claims[0] if claims else None
    receipt = read_matching_receipt(root, session_id=args.session_id, plan=plan)
    rob_id = None
    if claim:
        rob_id = str(claim.get("rob_entry_id") or "") or None
    if receipt and not rob_id:
        rob_id = str(receipt.get("rob_entry_id") or "") or None
    rob_entry = find_rob_entry(root, entry_id=rob_id, session_id=args.session_id)
    check = claim_lock.evaluate(root, Path(args.claims_subdir))
    ok = check["ok"] and (bool(claim) if (args.session_id or args.plan) else True)
    errors: list[str] = [] if ok else list(check.get("errors") or [])
    if (args.session_id or args.plan) and not claim:
        errors.append("no matching implementation-plan claim found")
    return print_payload(
        {
            "schema_version": 1,
            "ok": ok,
            "action": "status",
            "claim": claim,
            "receipt": receipt,
            "rob_entry": rob_entry,
            "check": check,
            "errors": errors,
            "counts": {
                "matching_claims": len(claims),
                "rob_entries": len(load_rob_entries(root)),
                "active_claims": check.get("counts", {}).get("active_claims", 0),
            },
            "portable_no_backend_model": {
                "claim_status": claim.get("status") if claim else None,
                "receipt_lifecycle_status": receipt.get("lifecycle_status") if receipt else None,
                "rob_state": rob_entry.get("state") if rob_entry else None,
                "local_main_serialization_lock": ".omx/locks/local-main-retire.lock",
                "remote_publication_allowed": False,
            },
        }
    )


def release(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    claim_dir = root / args.claims_subdir
    candidates = sorted(claim_dir.glob("*.json")) if claim_dir.exists() else []
    updated: list[str] = []
    updated_claims: list[dict[str, Any]] = []
    normalized_plan = claim_lock.normalize_repo_path(args.plan) if args.plan else None
    for path in candidates:
        data = read_json(path)
        if data is None:
            continue
        if not matches_claim(data, session_id=args.session_id, plan=normalized_plan):
            continue
        if not args.session_id and not args.plan:
            continue
        data["status"] = args.claim_status
        data["released_at"] = iso_now()
        data["release_reason"] = args.reason
        data["next_action"] = args.next_action or "Portable session claim released. No files were deleted."
        write_json(path, data)
        updated.append(str(path))
        data["path"] = str(path)
        updated_claims.append(data)

    receipt_path = root / RECEIPT_RELATIVE
    receipt = read_json(receipt_path)
    updated_receipt: dict[str, Any] | None = None
    if receipt is not None and (
        (args.session_id and receipt.get("session_id") == args.session_id)
        or (normalized_plan and claim_lock.normalize_repo_path(str(receipt.get("implementation_plan", ""))) == normalized_plan)
        or (not args.session_id and not normalized_plan and updated)
    ):
        receipt["status"] = args.receipt_lifecycle_status
        receipt["lifecycle_status"] = args.receipt_lifecycle_status
        receipt["released_at"] = iso_now()
        receipt["release_reason"] = args.reason
        receipt["next_action"] = args.next_action or "Portable session metadata was released. No files were deleted."
        write_json(receipt_path, receipt)
        receipt["path"] = str(receipt_path)
        updated_receipt = receipt

    updated_rob: dict[str, Any] | None = None
    if args.flush_rob:
        rob_id = args.rob_entry_id
        if not rob_id and updated_claims:
            rob_id = str(updated_claims[0].get("rob_entry_id") or "") or None
        if not rob_id and updated_receipt:
            rob_id = str(updated_receipt.get("rob_entry_id") or "") or None
        rob_entry = find_rob_entry(root, entry_id=rob_id, session_id=args.session_id)
        if rob_entry is not None:
            rob_entry.pop("path", None)
            rob_entry["state"] = args.rob_state
            rob_entry["flush_reason"] = args.reason
            rob_entry["flushed_at"] = iso_now()
            rob_path = write_rob_entry(root, rob_entry)
            rob_entry["path"] = str(rob_path)
            updated_rob = rob_entry

    ok = bool(updated)
    return print_payload(
        {
            "schema_version": 1,
            "ok": ok,
            "action": "release",
            "released_claims": updated,
            "receipt": updated_receipt,
            "rob_entry": updated_rob,
            "errors": [] if ok else ["no matching claim found"],
            "safety": {
                "metadata_only": True,
                "deleted_files": [],
                "deleted_worktrees": [],
                "remote_mutation_allowed": False,
            },
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create, inspect, or release portable implementation-plan session claims.")
    sub = parser.add_subparsers(dest="command", required=True)

    claim_parser = sub.add_parser("claim", help="Create an active implementation-plan claim.")
    claim_parser.add_argument("--root", default=".")
    claim_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    claim_parser.add_argument("--plan", required=True)
    claim_parser.add_argument("--session-id")
    claim_parser.add_argument("--branch")
    claim_parser.add_argument("--worktree")
    claim_parser.add_argument("--expires-hours", type=int, default=24)
    claim_parser.add_argument("--path", action="append", default=[])
    claim_parser.add_argument("--force", action="store_true")
    claim_parser.add_argument("--keep-conflicting", action="store_true")
    claim_parser.set_defaults(func=claim)

    start_parser = sub.add_parser("start", help="Start a portable no-backend session with claim, receipt, and ROB entry.")
    start_parser.add_argument("--root", default=".")
    start_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    start_parser.add_argument("--plan", required=True)
    start_parser.add_argument("--session-id")
    start_parser.add_argument("--branch")
    start_parser.add_argument("--worktree")
    start_parser.add_argument("--expires-hours", type=int, default=24)
    start_parser.add_argument("--path", action="append", default=[])
    start_parser.add_argument("--task-name")
    start_parser.add_argument("--task-summary")
    start_parser.add_argument("--expected-merge-or-pause")
    start_parser.add_argument("--next-action")
    start_parser.add_argument("--document-plan-only", action="store_true")
    start_parser.add_argument("--no-requires-code-implementation", action="store_true")
    start_parser.add_argument("--no-requires-local-main-merge", action="store_true")
    start_parser.add_argument("--requires-remote-sync", action="store_true")
    start_parser.add_argument("--remote-publication-authorized", action="store_true")
    start_parser.add_argument("--no-requires-user-confirmation-before-implementation", action="store_true")
    start_parser.add_argument("--implementation-confirmed-by-user", action="store_true")
    start_parser.add_argument("--implementation-confirmation-recorded-at")
    start_parser.add_argument("--governance-package-commit")
    start_parser.add_argument("--governance-package-merged-to-local-main", action="store_true")
    start_parser.add_argument("--implementation-stage", default=DEFAULT_IMPLEMENTATION_STAGE)
    start_parser.add_argument("--rob-entry-id")
    start_parser.add_argument("--base-main")
    start_parser.add_argument("--hotspot", action="append", default=[])
    start_parser.add_argument("--dependency", action="append", default=[])
    start_parser.add_argument("--force", action="store_true")
    start_parser.add_argument("--keep-conflicting", action="store_true")
    start_parser.set_defaults(func=start)

    status_parser = sub.add_parser("status", help="Inspect a portable no-backend claim/receipt/ROB session.")
    status_parser.add_argument("--root", default=".")
    status_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    status_parser.add_argument("--session-id")
    status_parser.add_argument("--plan")
    status_parser.set_defaults(func=status)

    release_parser = sub.add_parser("release", help="Release an active implementation-plan claim without deleting files.")
    release_parser.add_argument("--root", default=".")
    release_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    release_parser.add_argument("--session-id")
    release_parser.add_argument("--plan")
    release_parser.add_argument("--claim-status", choices=sorted(claim_lock.RELEASED_STATUSES | {"released"}), default="released")
    release_parser.add_argument("--receipt-lifecycle-status", choices=sorted(RECEIPT_LIFECYCLE_STATUSES), default="superseded")
    release_parser.add_argument("--flush-rob", action="store_true")
    release_parser.add_argument("--rob-entry-id")
    release_parser.add_argument("--rob-state", choices=sorted(ROB_TERMINAL_STATES), default="flushed")
    release_parser.add_argument("--reason", default="released")
    release_parser.add_argument("--next-action")
    release_parser.set_defaults(func=release)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
