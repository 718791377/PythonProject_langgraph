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
ALLOWED_LIFECYCLE_STATUSES = {
    "active",
    "paused",
    "ready-to-merge",
    "merged-local-main",
    "cleaned",
    "remote-sync-needed",
    "completed",
    "superseded",
}
ALLOWED_CLAIM_STATUSES = ALLOWED_LIFECYCLE_STATUSES | {"inactive"}
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
    if require_completion or lifecycle in {"merged-local-main", "cleaned", "remote-sync-needed", "completed"}:
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


def matching_claims(worktree_path: Path, branch: str) -> list[Path]:
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
        claims = matching_claims(worktree_path, branch)
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
    return payload(root, records, errors, warnings, info)


def payload(root: Path, records: list[dict[str, Any]], errors: list[str], warnings: list[str], info: list[str]) -> dict[str, Any]:
    feature_records = [record for record in records if not record.get("is_primary")]
    by_class: dict[str, int] = {}
    for record in feature_records:
        key = str(record.get("classification") or "unclassified_feature_worktree")
        by_class[key] = by_class.get(key, 0) + 1
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "worktrees": records,
        "residual_worktree_classification": by_class,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "policy": {
            "feature_worktree_requires_receipt": True,
            "feature_worktree_requires_branch_matching_claim": True,
            "document_plan_worktrees_should_not_be_long_lived": True,
            "completed_work_requires_completion_receipt": True,
            "remote_mutation_allowed": False,
        },
        "counts": {
            "worktrees": len(records),
            "feature_worktrees": len(feature_records),
            "with_receipt": sum(1 for record in feature_records if record.get("receipt_present")),
            "with_claim": sum(1 for record in feature_records if record.get("claim_present")),
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
