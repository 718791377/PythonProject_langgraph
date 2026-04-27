#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


CHECK_NAME = "worktree_session_hygiene"


def run_git(root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def normalize_path(path_text: str) -> str:
    return Path(path_text).as_posix()


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
        if " " in line:
            key, value = line.split(" ", 1)
        else:
            key, value = line, "true"
        if key == "worktree" and current:
            worktrees.append(current)
            current = {}
        current[key] = value
    if current:
        worktrees.append(current)
    return worktrees


def parse_status_porcelain(output: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for raw_line in output.splitlines():
        if not raw_line.strip() or raw_line.startswith("##"):
            continue
        status = raw_line[:2]
        path_text = raw_line[3:] if len(raw_line) > 3 else ""
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        records.append({"status": status, "path": normalize_path(path_text)})
    return records


def branch_name(worktree: dict[str, str]) -> str | None:
    branch = worktree.get("branch")
    if not branch:
        return None
    prefix = "refs/heads/"
    return branch[len(prefix) :] if branch.startswith(prefix) else branch


def resolve_ref(root: Path, ref: str) -> str | None:
    result = run_git(root, ["rev-parse", "--verify", ref])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def run_check(root: Path, *, main_branch: str, main_ref: str, allow_current_dirty: bool) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    top_result = run_git(root, ["rev-parse", "--show-toplevel"])
    if top_result.returncode != 0:
        errors.append(f"Not a Git worktree: {root}")
        return payload(root, main_branch, main_ref, allow_current_dirty, [], [], errors, warnings, info)

    current_root = Path(top_result.stdout.strip()).resolve()
    list_result = run_git(current_root, ["worktree", "list", "--porcelain"])
    if list_result.returncode != 0:
        errors.append("Unable to list Git worktrees.")
        if list_result.stderr.strip():
            errors.append(list_result.stderr.strip())
        return payload(root, main_branch, main_ref, allow_current_dirty, [], [], errors, warnings, info)

    worktrees = parse_worktree_list(list_result.stdout)
    dirty_worktrees: list[dict[str, object]] = []
    path_to_worktrees: dict[str, list[str]] = defaultdict(list)

    for worktree in worktrees:
        worktree_path = Path(worktree["worktree"]).resolve()
        branch = branch_name(worktree)
        status_result = run_git(worktree_path, ["status", "--porcelain", "--untracked-files=all"])
        if status_result.returncode != 0:
            warnings.append(f"Could not read status for worktree {worktree_path}.")
            continue
        dirty_records = parse_status_porcelain(status_result.stdout)
        is_current = worktree_path == current_root
        record = {
            "path": str(worktree_path),
            "branch": branch,
            "head": worktree.get("HEAD"),
            "is_current": is_current,
            "dirty_count": len(dirty_records),
            "dirty_paths": dirty_records,
        }
        if dirty_records:
            dirty_worktrees.append(record)
            for dirty in dirty_records:
                path_to_worktrees[str(dirty["path"])].append(str(worktree_path))

            if branch == main_branch:
                errors.append(
                    f"Main branch worktree is dirty: {worktree_path}. Preserve or move changes before aligning main."
                )
            elif is_current and not allow_current_dirty:
                errors.append(
                    f"Current non-main worktree is dirty: {worktree_path}. Use --allow-current-dirty only for an intentional feature-branch edit session."
                )
            elif not is_current:
                warnings.append(
                    f"Non-current worktree has uncommitted changes: {worktree_path} on branch {branch or '<detached>'}."
                )

    for dirty_path, owners in sorted(path_to_worktrees.items()):
        unique_owners = sorted(set(owners))
        if len(unique_owners) > 1:
            errors.append(
                f"Dirty path appears in multiple worktrees: {dirty_path} in {', '.join(unique_owners)}. Serialize ownership before continuing."
            )

    main_commit = resolve_ref(current_root, main_branch)
    target_commit = resolve_ref(current_root, main_ref)
    if main_commit and target_commit:
        if main_commit != target_commit:
            warnings.append(
                f"Local {main_branch} is not equal to {main_ref}: {main_commit} != {target_commit}. Fast-forward local main after reviewed GitLab main is ready."
            )
        else:
            info.append(f"Local {main_branch} matches {main_ref}.")
    else:
        warnings.append(
            f"Could not resolve both {main_branch} and {main_ref}; main alignment check is informational only."
        )

    if not dirty_worktrees:
        info.append("No dirty registered Git worktrees were detected.")

    return payload(root, main_branch, main_ref, allow_current_dirty, worktrees, dirty_worktrees, errors, warnings, info)


def payload(
    root: Path,
    main_branch: str,
    main_ref: str,
    allow_current_dirty: bool,
    worktrees: list[dict[str, str]],
    dirty_worktrees: list[dict[str, object]],
    errors: list[str],
    warnings: list[str],
    info: list[str],
) -> dict[str, object]:
    summarized_worktrees = [
        {
            "path": str(Path(item.get("worktree", "")).resolve()) if item.get("worktree") else "",
            "branch": branch_name(item),
            "head": item.get("HEAD"),
        }
        for item in worktrees
    ]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "main_branch": main_branch,
        "main_ref": main_ref,
        "allow_current_dirty": allow_current_dirty,
        "worktrees": summarized_worktrees,
        "dirty_worktrees": dirty_worktrees,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "worktrees": len(worktrees),
            "dirty_worktrees": len(dirty_worktrees),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check multi-session Git worktree hygiene without modifying the repository.")
    parser.add_argument("--root", default=".", help="Repository or worktree root to inspect.")
    parser.add_argument("--main-branch", default="main", help="Local branch that should mirror the reviewed mainline.")
    parser.add_argument("--main-ref", default="gitlab/main", help="Remote-tracking ref used as the authoritative mainline target.")
    parser.add_argument("--allow-current-dirty", action="store_true", help="Allow the current non-main feature worktree to be dirty.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    result = run_check(
        Path(args.root),
        main_branch=args.main_branch,
        main_ref=args.main_ref,
        allow_current_dirty=args.allow_current_dirty,
    )

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
