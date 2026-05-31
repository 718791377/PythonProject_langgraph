#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "worktree_task_receipt"
RECEIPT_RELATIVE = Path(".omx/worktree-task-receipt.json")
CLAIMS_RELATIVE = Path(".omx/session-claims")
DURABLE_STATE_RELATIVE = Path(".omx/state")
DURABLE_TEAM_RELATIVE = DURABLE_STATE_RELATIVE / "team"
DURABLE_LANGGRAPH_RELATIVE = DURABLE_STATE_RELATIVE / "langgraph"
ACTIVE_SELECTOR_RELATIVE = DURABLE_STATE_RELATIVE / "selectors" / "active.json"
TRACKED_TEAM_RECORD_NAME = "codex-auto-managed-team.json"
LANGGRAPH_BACKEND_RECORD_NAME = "backend.json"
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
ALLOWED_CLAIM_STATUSES = ALLOWED_LIFECYCLE_STATUSES | {"inactive"}
COMPLETION_REQUIRED_LIFECYCLE_STATUSES = {"merged-local-main", "cleaned", "remote-sync-needed", "completed"}
REQUIRED_METADATA_FIELDS = {
    "schema_version": int,
    "session_id": str,
    "branch": str,
    "worktree": str,
    "task_name": str,
    "task_summary": str,
    "document_plan_only": bool,
    "requires_code_implementation": bool,
    "created_at": str,
    "expected_merge_or_pause": str,
    "next_action": str,
    "requires_local_main_merge": bool,
    "requires_remote_sync": bool,
    "lifecycle_status": str,
    "paths": list,
}
COMPLETION_FIELDS = {
    "completed_at": str,
    "rollback_ref": str,
    "local_main_commit": str,
    "cleaned_worktree": str,
    "deleted_branch": str,
    "remote_sync_status": str,
}


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_worktree_list(output: str) -> list[dict[str, str]]:
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, value = line.split(" ", 1) if " " in line else (line, "true")
        if key == "worktree" and current:
            worktrees.append(current)
            current = {}
        current[key] = value
    if current:
        worktrees.append(current)
    return worktrees


def branch_name(worktree: dict[str, str]) -> str | None:
    branch = worktree.get("branch")
    if not branch:
        return None
    prefix = "refs/heads/"
    return branch[len(prefix) :] if branch.startswith(prefix) else branch


def read_json(path: Path, errors: list[str], prefix: str) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        errors.append(f"{prefix}: missing {path}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"{prefix}: invalid JSON in {path}: {exc}")
        return None
    except OSError as exc:
        errors.append(f"{prefix}: cannot read {path}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{prefix}: {path} must contain a JSON object")
        return None
    return data


def read_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, f"missing {path}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: {exc}"
    except OSError as exc:
        return None, f"cannot read {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"{path} must contain a JSON object"
    return data, None


def relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def paths_match(left: str | None, right: Path) -> bool:
    if not left or not str(left).strip():
        return False
    try:
        return Path(left).resolve() == right.resolve()
    except OSError:
        return False


def directory_file_count(path: Path) -> int:
    try:
        return sum(1 for child in path.rglob("*") if child.is_file())
    except OSError:
        return 0


def add_durable_residue_record(
    records: list[dict[str, Any]],
    *,
    root: Path,
    kind: str,
    path: Path,
    state_class: str,
    safe_next_action: str,
    reason: str,
    auto_adopt_allowed: bool = False,
    **extra: Any,
) -> None:
    record: dict[str, Any] = {
        "kind": kind,
        "path": relative_to_root(root, path),
        "state_class": state_class,
        "safe_next_action": safe_next_action,
        "auto_adopt_allowed": auto_adopt_allowed,
        "reason": reason,
    }
    record.update({key: value for key, value in extra.items() if value is not None})
    records.append(record)


def classify_durable_residue(root: Path) -> list[dict[str, Any]]:
    """Classify repo-local .omx durable residue without mutating or adopting it."""

    root = root.resolve()
    records: list[dict[str, Any]] = []

    team_root = root / DURABLE_TEAM_RELATIVE
    tracked_record_path = team_root / TRACKED_TEAM_RECORD_NAME
    tracked_team_names: set[str] = set()
    if tracked_record_path.exists():
        tracked_record, tracked_error = read_json_object(tracked_record_path)
        if tracked_record is None:
            add_durable_residue_record(
                records,
                root=root,
                kind="invalid_tracked_team_record",
                path=tracked_record_path,
                state_class="protected_residue",
                safe_next_action="manual-inspection-required",
                reason=tracked_error or "tracked team record is unreadable",
            )
        else:
            team_name = tracked_record.get("team_name")
            if isinstance(team_name, str) and team_name.strip():
                tracked_team_names.add(team_name)
                if not (team_root / team_name).exists():
                    add_durable_residue_record(
                        records,
                        root=root,
                        kind="stale_tracked_record",
                        path=tracked_record_path,
                        state_class="safe_cleanup_candidate",
                        safe_next_action="remove-through-approved-reconciliation-path",
                        reason="tracked native team record points to a missing team directory",
                        tracked_team_name=team_name,
                    )

    if team_root.exists():
        for team_dir in sorted((path for path in team_root.iterdir() if path.is_dir()), key=lambda p: p.name):
            if team_dir.name in tracked_team_names:
                continue
            file_count = directory_file_count(team_dir)
            if file_count == 0:
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="empty_unmanaged_native_team_directory",
                    path=team_dir,
                    state_class="safe_cleanup_candidate",
                    safe_next_action="remove-through-approved-reconciliation-path",
                    reason="unmanaged native team directory contains no files",
                    team_name=team_dir.name,
                    file_count=file_count,
                )
            else:
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="non_empty_unmanaged_native_team_directory",
                    path=team_dir,
                    state_class="protected_residue",
                    safe_next_action="manual-inspection-required",
                    reason="unmanaged native team directory contains repo-local state files",
                    team_name=team_dir.name,
                    file_count=file_count,
                )

    selector_path = root / ACTIVE_SELECTOR_RELATIVE
    if selector_path.exists():
        selector, selector_error = read_json_object(selector_path)
        if selector is None:
            add_durable_residue_record(
                records,
                root=root,
                kind="invalid_active_selector",
                path=selector_path,
                state_class="protected_residue",
                safe_next_action="manual-inspection-required",
                reason=selector_error or "active selector is unreadable",
            )
        else:
            selector_repo_root = selector.get("repo_root")
            backend_family = selector.get("backend_family") or selector.get("backend")
            if isinstance(selector_repo_root, str) and selector_repo_root.strip() and not paths_match(selector_repo_root, root):
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="stale_selector",
                    path=selector_path,
                    state_class="stale_selector",
                    safe_next_action="refresh-selector-or-ignore-as-stale",
                    reason="active selector points to a different repository root",
                    backend_family=backend_family,
                    selector_repo_root=selector_repo_root,
                )
            else:
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="active_current_selector",
                    path=selector_path,
                    state_class="selector_authority",
                    safe_next_action="inspect-as-current-authority; do-not-auto-adopt-by-itself",
                    reason="active selector is current repo-local authority evidence",
                    backend_family=backend_family,
                    selector_repo_root=selector_repo_root,
                )

    langgraph_root = root / DURABLE_LANGGRAPH_RELATIVE
    langgraph_backend_path = langgraph_root / LANGGRAPH_BACKEND_RECORD_NAME
    if langgraph_backend_path.exists():
        backend_record, backend_error = read_json_object(langgraph_backend_path)
        if backend_record is None:
            add_durable_residue_record(
                records,
                root=root,
                kind="invalid_langgraph_backend_record",
                path=langgraph_backend_path,
                state_class="protected_residue",
                safe_next_action="manual-inspection-required",
                reason=backend_error or "LangGraph backend record is unreadable",
            )
        else:
            thread_id = backend_record.get("thread_id")
            thread_status = ""
            thread_path: Path | None = None
            if isinstance(thread_id, str) and thread_id.strip():
                thread_path = langgraph_root / "threads" / f"{thread_id}.json"
                thread_record, _ = read_json_object(thread_path)
                if isinstance(thread_record, dict):
                    for key in ("status", "lifecycle_status", "state_class"):
                        value = thread_record.get(key)
                        if isinstance(value, str) and value.strip():
                            thread_status = value
                            break
            backend_status = ""
            for key in ("status", "lifecycle_status", "state_class"):
                value = backend_record.get(key)
                if isinstance(value, str) and value.strip():
                    backend_status = value
                    break
            status_values = {backend_status.lower(), thread_status.lower()}
            completed_markers = {"completed", "complete", "closed", "archived", "cleaned"}
            completed = bool(status_values & completed_markers) or bool(backend_record.get("completed_at"))
            if completed:
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="completed_langgraph_state",
                    path=langgraph_backend_path,
                    state_class="legacy_completed_state",
                    safe_next_action="inspect-or-archive; do-not-auto-resume",
                    reason="LangGraph backend record describes a completed legacy thread",
                    backend_family=backend_record.get("backend") or backend_record.get("backend_family") or "langgraph",
                    thread_id=thread_id,
                    status=backend_status or thread_status,
                    thread_path=relative_to_root(root, thread_path) if thread_path else None,
                )
            else:
                add_durable_residue_record(
                    records,
                    root=root,
                    kind="legacy_langgraph_state",
                    path=langgraph_backend_path,
                    state_class="inspectable_legacy_state",
                    safe_next_action="inspect-before-resume-or-archive; do-not-auto-resume",
                    reason="LangGraph backend record exists as inspectable durable state",
                    backend_family=backend_record.get("backend") or backend_record.get("backend_family") or "langgraph",
                    thread_id=thread_id,
                    status=backend_status or thread_status,
                    thread_path=relative_to_root(root, thread_path) if thread_path else None,
                )
    elif langgraph_root.exists() and directory_file_count(langgraph_root) > 0:
        add_durable_residue_record(
            records,
            root=root,
            kind="unmanaged_langgraph_runtime_residue",
            path=langgraph_root,
            state_class="protected_residue",
            safe_next_action="manual-inspection-required",
            reason="repo-local LangGraph runtime files exist without a backend record",
            file_count=directory_file_count(langgraph_root),
        )

    return records


def summarize_durable_residue(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    by_state_class: dict[str, int] = {}
    by_safe_next_action: dict[str, int] = {}
    for record in records:
        kind = str(record.get("kind") or "unknown")
        state_class = str(record.get("state_class") or "unknown")
        safe_next_action = str(record.get("safe_next_action") or "unknown")
        by_kind[kind] = by_kind.get(kind, 0) + 1
        by_state_class[state_class] = by_state_class.get(state_class, 0) + 1
        by_safe_next_action[safe_next_action] = by_safe_next_action.get(safe_next_action, 0) + 1
    return {
        "records": len(records),
        "by_kind": by_kind,
        "by_state_class": by_state_class,
        "by_safe_next_action": by_safe_next_action,
        "safe_cleanup_candidates": sum(
            1 for record in records if record.get("state_class") == "safe_cleanup_candidate"
        ),
        "protected_residue": sum(1 for record in records if record.get("state_class") == "protected_residue"),
        "auto_adopt_allowed": sum(1 for record in records if record.get("auto_adopt_allowed") is True),
    }


def validate_metadata(
    data: dict[str, Any],
    *,
    path: Path,
    branch: str,
    worktree_path: Path,
    errors: list[str],
    warnings: list[str],
    require_completion: bool,
) -> dict[str, Any]:
    prefix = str(path)
    for field, expected_type in REQUIRED_METADATA_FIELDS.items():
        if field not in data:
            errors.append(f"{prefix}: `{field}` is required")
            continue
        value = data.get(field)
        if expected_type is bool:
            if not isinstance(value, bool):
                errors.append(f"{prefix}: `{field}` must be boolean")
        elif expected_type is int:
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{prefix}: `{field}` must be integer")
        elif expected_type is list:
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"{prefix}: `{field}` must be a non-empty string list or an empty list of strings")
        elif not isinstance(value, expected_type) or not str(value).strip():
            errors.append(f"{prefix}: `{field}` must be a non-empty string")
    if data.get("schema_version") != 1:
        errors.append(f"{prefix}: `schema_version` must be 1")
    if data.get("branch") != branch:
        errors.append(f"{prefix}: `branch` must match registered worktree branch `{branch}`")
    declared_worktree = data.get("worktree")
    if isinstance(declared_worktree, str) and declared_worktree.strip():
        try:
            if Path(declared_worktree).resolve() != worktree_path.resolve():
                errors.append(f"{prefix}: `worktree` must match registered path `{worktree_path}`")
        except OSError:
            errors.append(f"{prefix}: `worktree` path cannot be resolved")
    lifecycle = data.get("lifecycle_status")
    if lifecycle not in ALLOWED_LIFECYCLE_STATUSES:
        errors.append(f"{prefix}: `lifecycle_status` must be one of {sorted(ALLOWED_LIFECYCLE_STATUSES)}")
    status = data.get("status")
    if status is not None and status not in ALLOWED_CLAIM_STATUSES:
        errors.append(f"{prefix}: `status` must be one of {sorted(ALLOWED_CLAIM_STATUSES)} when present")
    if data.get("document_plan_only") is True and data.get("requires_code_implementation") is True:
        errors.append(f"{prefix}: document-plan-only work cannot also require code implementation")
    if data.get("document_plan_only") is True and data.get("requires_local_main_merge") is not True:
        warnings.append(f"{prefix}: document-plan-only work should normally merge to local main and cleanup promptly")
    if require_completion or lifecycle in COMPLETION_REQUIRED_LIFECYCLE_STATUSES:
        completion = data.get("completion") if isinstance(data.get("completion"), dict) else data
        for field, expected_type in COMPLETION_FIELDS.items():
            if field not in completion:
                errors.append(f"{prefix}: completion `{field}` is required for lifecycle `{lifecycle}`")
                continue
            value = completion.get(field)
            if not isinstance(value, expected_type) or not str(value).strip():
                errors.append(f"{prefix}: completion `{field}` must be a non-empty string")
    return {
        "task_name": data.get("task_name"),
        "lifecycle_status": lifecycle,
        "document_plan_only": data.get("document_plan_only"),
        "requires_code_implementation": data.get("requires_code_implementation"),
        "next_action": data.get("next_action"),
        "requires_remote_sync": data.get("requires_remote_sync"),
    }


def validate_claim_lifecycle(data: dict[str, Any], path: Path, errors: list[str]) -> None:
    status = data.get("status", "active")
    if status not in ALLOWED_CLAIM_STATUSES:
        errors.append(f"{path}: `status` must be one of {sorted(ALLOWED_CLAIM_STATUSES)} when present")
    lifecycle = data.get("lifecycle_status")
    if lifecycle is not None and lifecycle not in ALLOWED_LIFECYCLE_STATUSES:
        errors.append(f"{path}: `lifecycle_status` must be one of {sorted(ALLOWED_LIFECYCLE_STATUSES)} when present")


def matching_claims(worktree_path: Path, branch: str, errors: list[str] | None = None) -> list[Path]:
    claim_dir = worktree_path / CLAIMS_RELATIVE
    if not claim_dir.exists():
        return []
    matches: list[Path] = []
    for path in sorted(claim_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("branch") == branch:
            if errors is not None:
                validate_claim_lifecycle(data, path, errors)
            matches.append(path)
    return matches


def evaluate(root: Path, require_all_feature_worktrees: bool, require_completion_for_completed: bool) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    list_result = run_git(root, ["worktree", "list", "--porcelain"])
    if list_result.returncode != 0:
        errors.append(list_result.stderr.strip() or "Unable to list Git worktrees")
        return payload(root, [], errors, warnings, info)
    worktree_items = parse_worktree_list(list_result.stdout)
    primary_path = Path(worktree_items[0].get("worktree", "")).resolve() if worktree_items else root
    records: list[dict[str, Any]] = []
    legacy_missing_receipts = 0
    legacy_missing_claims = 0
    for item in worktree_items:
        worktree_path = Path(item.get("worktree", "")).resolve()
        branch = branch_name(item)
        is_primary = worktree_path == primary_path
        is_current_feature = worktree_path == root and not is_primary
        record: dict[str, Any] = {
            "path": str(worktree_path),
            "branch": branch,
            "head": item.get("HEAD"),
            "is_primary": is_primary,
            "receipt_present": False,
            "claim_present": False,
            "classification": "primary" if is_primary else "unclassified_feature_worktree",
        }
        if is_primary or not branch:
            records.append(record)
            continue
        receipt_path = worktree_path / RECEIPT_RELATIVE
        receipt_errors: list[str] = []
        receipt = read_json(receipt_path, receipt_errors, f"{worktree_path}")
        if receipt is None:
            if require_all_feature_worktrees or is_current_feature:
                errors.extend(receipt_errors)
            else:
                legacy_missing_receipts += 1
        else:
            record["receipt_present"] = True
            summary = validate_metadata(
                receipt,
                path=receipt_path,
                branch=branch,
                worktree_path=worktree_path,
                errors=errors,
                warnings=warnings,
                require_completion=require_completion_for_completed,
            )
            record.update(summary)
            record["classification"] = str(summary.get("lifecycle_status") or "unclassified_feature_worktree")
        claim_lifecycle_issues = errors if require_all_feature_worktrees or is_current_feature else warnings
        claims = matching_claims(worktree_path, branch, claim_lifecycle_issues)
        record["claim_present"] = bool(claims)
        record["claim_paths"] = [str(path) for path in claims]
        if not claims:
            message = f"{worktree_path}: missing branch-matching claim under {CLAIMS_RELATIVE}"
            if require_all_feature_worktrees or is_current_feature:
                errors.append(message)
            else:
                legacy_missing_claims += 1
        records.append(record)
    if legacy_missing_receipts:
        warnings.append(
            f"{legacy_missing_receipts} legacy feature worktree(s) lack {RECEIPT_RELATIVE}; classify or migrate them during residual-worktree cleanup."
        )
    if legacy_missing_claims:
        warnings.append(
            f"{legacy_missing_claims} legacy feature worktree(s) lack branch-matching claims; classify or migrate them during residual-worktree cleanup."
        )
    if records:
        info.append("Worktree task receipt scan completed; residual feature worktrees are classified separately from active tasks.")
    durable_residue = classify_durable_residue(root)
    if durable_residue:
        info.append("Repo-local .omx durable residue scan completed; residue is inspectable evidence and is not auto-adopted.")
    return payload(root, records, errors, warnings, info, durable_residue)


def payload(
    root: Path,
    records: list[dict[str, Any]],
    errors: list[str],
    warnings: list[str],
    info: list[str],
    durable_residue: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    feature_records = [record for record in records if not record.get("is_primary")]
    by_class: dict[str, int] = {}
    for record in feature_records:
        key = str(record.get("classification") or "unclassified_feature_worktree")
        by_class[key] = by_class.get(key, 0) + 1
    durable_residue = durable_residue or []
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "worktrees": records,
        "residual_worktree_classification": by_class,
        "durable_residue_classification": durable_residue,
        "durable_residue_classification_summary": summarize_durable_residue(durable_residue),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "policy": {
            "feature_worktree_requires_receipt": True,
            "feature_worktree_requires_branch_matching_claim": True,
            "document_plan_worktrees_should_not_be_long_lived": True,
            "completed_work_requires_completion_receipt": True,
            "durable_residue_is_inspectable_evidence": True,
            "unmanaged_durable_state_auto_adopt_allowed": False,
            "remote_mutation_allowed": False,
        },
        "counts": {
            "worktrees": len(records),
            "feature_worktrees": len(feature_records),
            "with_receipt": sum(1 for record in feature_records if record.get("receipt_present")),
            "with_claim": sum(1 for record in feature_records if record.get("claim_present")),
            "durable_residue_records": len(durable_residue),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check feature worktree task receipts and lifecycle metadata.")
    parser.add_argument("--root", default=".", help="Primary repository root.")
    parser.add_argument(
        "--require-all-feature-worktrees",
        action="store_true",
        help="Fail when any registered feature worktree lacks a receipt or branch-matching claim.",
    )
    parser.add_argument(
        "--require-completion-for-completed",
        action="store_true",
        help="Require completion receipt fields for completed/cleaned lifecycle states.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    result = evaluate(Path(args.root), args.require_all_feature_worktrees, args.require_completion_for_completed)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["info"]:
            print(message)
        for message in result["warnings"]:
            print(f"WARNING: {message}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
