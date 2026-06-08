#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RECEIPT_RELATIVE = Path(".omx/worktree-task-receipt.json")
CLAIMS_RELATIVE = Path(".omx/session-claims")
ALLOWED_LIFECYCLE_STATUSES = {
    "active",
    "paused",
    "ready-to-merge",
    "merged-local-main",
    "cleaned",
    "remote-sync-needed",
    "completed",
    "superseded",
    "stale",
}
INTEGRATION_STATES = {"merged-local-main", "remote-sync-needed", "completed"}
CLEANUP_STATES = {"cleaned"}
EXCEPTIONAL_STATES = {"paused", "superseded", "stale"}
COMPLETION_REQUIRED_STATES = INTEGRATION_STATES | CLEANUP_STATES
TERMINAL_STATES = {"cleaned", "remote-sync-needed", "completed", "superseded", "stale"}
ALLOWED_TRANSITIONS = {
    "active": {"paused", "ready-to-merge", "superseded", "stale"},
    "paused": {"active", "ready-to-merge", "superseded", "stale"},
    "ready-to-merge": {"paused", "merged-local-main", "superseded", "stale"},
    "merged-local-main": {"completed", "cleaned", "remote-sync-needed"},
    "completed": {"cleaned", "remote-sync-needed"},
    "remote-sync-needed": {"completed", "cleaned"},
    "cleaned": set(),
    "superseded": set(),
    "stale": set(),
}


def read_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json_object(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_claim_name(branch: str) -> str:
    return branch.replace("/", "__").replace("\\", "__")


def find_branch_claim(worktree: Path, branch: str) -> Path | None:
    claim_dir = worktree / CLAIMS_RELATIVE
    if not claim_dir.exists():
        return None
    exact = claim_dir / f"{safe_claim_name(branch)}.json"
    candidates = [exact] if exact.exists() else []
    candidates.extend(path for path in sorted(claim_dir.glob("*.json")) if path != exact)
    for path in candidates:
        try:
            data = read_json_object(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if data.get("branch") == branch:
            return path
    return None


def metadata_paths(worktree: Path, branch: str) -> list[Path]:
    paths: list[Path] = []
    receipt = worktree / RECEIPT_RELATIVE
    if receipt.exists():
        paths.append(receipt)
    claim = find_branch_claim(worktree, branch)
    if claim is not None and claim not in paths:
        paths.append(claim)
    if not paths:
        raise ValueError(
            f"No worktree receipt or branch-matching claim found for branch {branch!r} under {worktree}"
        )
    return paths


def current_state(payload: dict[str, Any]) -> str:
    state = str(payload.get("lifecycle_status") or payload.get("status") or "active")
    if state not in ALLOWED_LIFECYCLE_STATUSES:
        raise ValueError(f"current lifecycle state {state!r} is not allowed")
    return state


def validate_transition(previous_state: str, next_state: str) -> None:
    if next_state not in ALLOWED_LIFECYCLE_STATUSES:
        raise ValueError(f"next_state must be one of {sorted(ALLOWED_LIFECYCLE_STATUSES)}")
    if next_state == previous_state:
        return
    allowed = ALLOWED_TRANSITIONS.get(previous_state, set())
    if next_state not in allowed:
        raise ValueError(f"invalid lifecycle transition: {previous_state} -> {next_state}")


def completion_payload(
    *,
    next_state: str,
    transitioned_at: str,
    rollback_ref: str | None,
    local_main_commit: str | None,
    cleaned_worktree: str | None,
    deleted_branch: str | None,
    remote_sync_status: str | None,
) -> dict[str, str] | None:
    if next_state not in COMPLETION_REQUIRED_STATES:
        return None
    missing: list[str] = []
    values = {
        "rollback_ref": rollback_ref,
        "local_main_commit": local_main_commit,
        "cleaned_worktree": cleaned_worktree,
        "deleted_branch": deleted_branch,
        "remote_sync_status": remote_sync_status,
    }
    for key, value in values.items():
        if not isinstance(value, str) or not value.strip():
            missing.append(key)
    if missing:
        raise ValueError(f"transition to {next_state} requires completion field(s): {', '.join(missing)}")
    return {
        "completed_at": transitioned_at,
        "rollback_ref": str(rollback_ref),
        "local_main_commit": str(local_main_commit),
        "cleaned_worktree": str(cleaned_worktree),
        "deleted_branch": str(deleted_branch),
        "remote_sync_status": str(remote_sync_status),
    }


def transition_entry(
    *,
    owner: str,
    previous_state: str,
    next_state: str,
    transitioned_at: str,
    evidence_paths: list[str],
    cleanup_decision: str,
    reason: str | None,
    rollback_ref: str | None,
    local_main_commit: str | None,
    remote_publication_authorized: bool,
) -> dict[str, Any]:
    return {
        "transitioned_at": transitioned_at,
        "owner": owner,
        "previous_state": previous_state,
        "next_state": next_state,
        "evidence_paths": evidence_paths,
        "rollback_ref": rollback_ref or "",
        "local_main_commit": local_main_commit or "",
        "cleanup_decision": cleanup_decision,
        "reason": reason or "",
        "remote_publication_authorized": bool(remote_publication_authorized),
    }


def apply_transition_to_payload(
    payload: dict[str, Any],
    *,
    branch: str,
    worktree: Path,
    next_state: str,
    owner: str,
    evidence_paths: list[str],
    cleanup_decision: str,
    reason: str | None,
    rollback_ref: str | None,
    local_main_commit: str | None,
    cleaned_worktree: str | None,
    deleted_branch: str | None,
    remote_sync_status: str | None,
    remote_publication_authorized: bool,
    transitioned_at: str,
) -> dict[str, Any]:
    previous_state = current_state(payload)
    validate_transition(previous_state, next_state)
    if next_state in EXCEPTIONAL_STATES and not reason and not evidence_paths:
        raise ValueError(f"transition to {next_state} requires a reason or evidence path")
    completion = completion_payload(
        next_state=next_state,
        transitioned_at=transitioned_at,
        rollback_ref=rollback_ref,
        local_main_commit=local_main_commit,
        cleaned_worktree=cleaned_worktree,
        deleted_branch=deleted_branch,
        remote_sync_status=remote_sync_status,
    )
    updated = dict(payload)
    updated["schema_version"] = updated.get("schema_version", 1)
    updated["branch"] = branch
    updated["worktree"] = str(worktree)
    updated["status"] = next_state
    updated["lifecycle_status"] = next_state
    updated["updated_at"] = transitioned_at
    updated["remote_publication_authorized"] = bool(remote_publication_authorized)
    updated["remote_publication_performed"] = False
    if next_state in TERMINAL_STATES or next_state in COMPLETION_REQUIRED_STATES:
        updated["completed_at"] = transitioned_at if completion else updated.get("completed_at", transitioned_at)
    if rollback_ref:
        updated["rollback_ref"] = rollback_ref
    if local_main_commit:
        updated["local_main_commit"] = local_main_commit
        updated["merged_local_main_commit"] = local_main_commit
    if remote_sync_status:
        updated["remote_sync_status"] = remote_sync_status
        updated["requires_remote_sync"] = remote_sync_status not in {
            "not_authorized:remote_publication_gate_closed",
            "not_synced",
        } and next_state == "remote-sync-needed"
    if completion is not None:
        updated["completion"] = completion
    transitions = updated.get("lifecycle_transitions")
    if not isinstance(transitions, list):
        transitions = []
    transitions.append(
        transition_entry(
            owner=owner,
            previous_state=previous_state,
            next_state=next_state,
            transitioned_at=transitioned_at,
            evidence_paths=evidence_paths,
            cleanup_decision=cleanup_decision,
            reason=reason,
            rollback_ref=rollback_ref,
            local_main_commit=local_main_commit,
            remote_publication_authorized=remote_publication_authorized,
        )
    )
    updated["lifecycle_transitions"] = transitions
    return updated


def advance_lifecycle(
    *,
    worktree: Path | str,
    branch: str,
    next_state: str,
    owner: str,
    evidence_paths: list[str] | None = None,
    cleanup_decision: str,
    reason: str | None = None,
    rollback_ref: str | None = None,
    local_main_commit: str | None = None,
    cleaned_worktree: str | None = None,
    deleted_branch: str | None = None,
    remote_sync_status: str | None = None,
    remote_publication_authorized: bool = False,
) -> dict[str, Any]:
    worktree_path = Path(worktree).resolve()
    if not owner.strip():
        raise ValueError("owner is required")
    if not cleanup_decision.strip():
        raise ValueError("cleanup_decision is required")
    normalized_evidence = [str(path).replace("\\", "/") for path in (evidence_paths or []) if str(path).strip()]
    transitioned_at = datetime.now(timezone.utc).isoformat()
    paths = metadata_paths(worktree_path, branch)
    updates: list[dict[str, Any]] = []
    for path in paths:
        original = read_json_object(path)
        updated = apply_transition_to_payload(
            original,
            branch=branch,
            worktree=worktree_path,
            next_state=next_state,
            owner=owner,
            evidence_paths=normalized_evidence,
            cleanup_decision=cleanup_decision,
            reason=reason,
            rollback_ref=rollback_ref,
            local_main_commit=local_main_commit,
            cleaned_worktree=cleaned_worktree,
            deleted_branch=deleted_branch,
            remote_sync_status=remote_sync_status,
            remote_publication_authorized=remote_publication_authorized,
            transitioned_at=transitioned_at,
        )
        updates.append({"path": str(path), "previous_state": current_state(original), "next_state": next_state, "payload": updated})
    for update in updates:
        write_json_object(Path(update["path"]), update["payload"])
    return {
        "schema_version": 1,
        "ok": True,
        "worktree": str(worktree_path),
        "branch": branch,
        "next_state": next_state,
        "owner": owner,
        "transitioned_at": transitioned_at,
        "updated_paths": [update["path"] for update in updates],
        "remote_publication_authorized": bool(remote_publication_authorized),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance worktree task receipt and branch-matching claim lifecycle state.")
    parser.add_argument("--worktree", required=True, help="Feature worktree path containing .omx lifecycle metadata.")
    parser.add_argument("--branch", required=True, help="Feature branch name to match claim metadata.")
    parser.add_argument("--next-state", required=True, choices=sorted(ALLOWED_LIFECYCLE_STATUSES), help="Lifecycle state to record.")
    parser.add_argument("--owner", required=True, help="Owner session or helper recording the transition.")
    parser.add_argument("--evidence-path", action="append", default=[], help="Evidence path to include in the transition ledger; repeatable.")
    parser.add_argument("--cleanup-decision", required=True, help="Cleanup decision for this transition.")
    parser.add_argument("--reason", default=None, help="Reason for exceptional or operator-driven transitions.")
    parser.add_argument("--rollback-ref", default=None, help="Rollback ref required for integration and cleanup states.")
    parser.add_argument("--local-main-commit", default=None, help="Local main commit required for integration and cleanup states.")
    parser.add_argument("--cleaned-worktree", default=None, help="Cleaned worktree evidence for completion states.")
    parser.add_argument("--deleted-branch", default=None, help="Deleted branch evidence for completion states.")
    parser.add_argument("--remote-sync-status", default=None, help="Remote sync status for completion states.")
    parser.add_argument("--remote-publication-authorized", action="store_true", help="Record remote publication authorization; normally false.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    try:
        payload = advance_lifecycle(
            worktree=args.worktree,
            branch=args.branch,
            next_state=args.next_state,
            owner=args.owner,
            evidence_paths=args.evidence_path,
            cleanup_decision=args.cleanup_decision,
            reason=args.reason,
            rollback_ref=args.rollback_ref,
            local_main_commit=args.local_main_commit,
            cleaned_worktree=args.cleaned_worktree,
            deleted_branch=args.deleted_branch,
            remote_sync_status=args.remote_sync_status,
            remote_publication_authorized=args.remote_publication_authorized,
        )
    except Exception as exc:
        payload = {"schema_version": 1, "ok": False, "error": str(exc)}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload.get("ok"):
            print(f"Advanced lifecycle for {args.branch} to {args.next_state}.")
        else:
            print(f"ERROR: {payload.get('error')}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
