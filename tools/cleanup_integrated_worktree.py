#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "integrated_worktree_cleanup"
GIT_LOCAL_ENV_KEYS = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_WORK_TREE",
}


def git_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in GIT_LOCAL_ENV_KEYS:
        env.pop(key, None)
    return env


def run_git(root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=git_env(),
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


def resolve_worktree_root(root: Path) -> Path | None:
    result = run_git(root, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def resolve_common_dir(root: Path) -> Path | None:
    result = run_git(root, ["rev-parse", "--git-common-dir"])
    if result.returncode != 0:
        return None
    path = Path(result.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def primary_root_from_common_dir(common_dir: Path) -> Path:
    return common_dir.parent.resolve() if common_dir.name == ".git" else common_dir.resolve()


def resolve_ref(root: Path, ref: str) -> str | None:
    result = run_git(root, ["rev-parse", "--verify", ref])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool | None:
    result = run_git(root, ["merge-base", "--is-ancestor", ancestor, descendant])
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_claim_name(branch: str) -> str:
    return branch.replace("/", "__").replace("\\", "__")


def backup_refs_for_branch(root: Path, branch: str) -> list[str]:
    result = run_git(root, ["for-each-ref", "--format=%(refname)", "refs/backup/local-main"])
    if result.returncode != 0:
        return []
    suffix = f"-before-{branch}"
    return sorted(ref.strip() for ref in result.stdout.splitlines() if ref.strip().endswith(suffix))


def find_worktree(root: Path, branch: str, worktree_path: Path | None) -> dict[str, str] | None:
    result = run_git(root, ["worktree", "list", "--porcelain"])
    if result.returncode != 0:
        return None
    for item in parse_worktree_list(result.stdout):
        item_branch = branch_name(item)
        item_path = Path(item.get("worktree", "")).resolve()
        if item_branch != branch:
            continue
        if worktree_path is not None and item_path != worktree_path.resolve():
            continue
        return item
    return None


def status_records(worktree_path: Path) -> list[str] | None:
    result = run_git(worktree_path, ["status", "--porcelain", "--untracked-files=all"])
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def load_completed_claim(worktree_path: Path, branch: str) -> dict[str, Any] | None:
    claim_root = worktree_path / ".omx" / "session-claims"
    if not claim_root.exists():
        return None
    candidates = list(claim_root.glob("*.json"))
    exact = claim_root / f"{safe_claim_name(branch)}.json"
    if exact.exists():
        candidates.insert(0, exact)
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("branch") == branch and data.get("status") == "completed":
            data["_source_claim_path"] = str(path)
            return data
    return None


def copy_claim_to_primary(root: Path, claim: dict[str, Any], branch: str, cleanup_payload: dict[str, Any]) -> Path:
    archive_dir = root / ".omx" / "session-claims" / "completed"
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / f"{safe_claim_name(branch)}.json"
    preserved = dict(claim)
    preserved["cleanup"] = {
        "cleaned_at": datetime.now(timezone.utc).isoformat(),
        "cleanup_check": cleanup_payload,
    }
    target.write_text(json.dumps(preserved, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def evaluate(root: Path, branch: str, worktree_path: Path | None, main_branch: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    root = root.resolve()
    worktree_root = resolve_worktree_root(root)
    if worktree_root is None:
        errors.append(f"Not a Git worktree: {root}")
        return payload(root, branch, worktree_path, main_branch, None, None, [], None, errors, warnings, info)
    common_dir = resolve_common_dir(worktree_root)
    root = primary_root_from_common_dir(common_dir) if common_dir else worktree_root
    main_head = resolve_ref(root, main_branch)
    branch_head = resolve_ref(root, branch)
    if not main_head:
        errors.append(f"Cannot resolve local {main_branch}.")
    if not branch_head:
        errors.append(f"Cannot resolve local branch {branch}.")

    worktree = find_worktree(root, branch, worktree_path)
    if not worktree:
        errors.append(f"No registered worktree found for branch {branch}.")
        return payload(root, branch, worktree_path, main_branch, main_head, branch_head, [], None, errors, warnings, info)

    actual_worktree_path = Path(worktree["worktree"]).resolve()
    if worktree_path is not None and actual_worktree_path != worktree_path.resolve():
        errors.append(f"Registered worktree path does not match requested path: {actual_worktree_path} != {worktree_path.resolve()}.")
    if actual_worktree_path == root:
        errors.append("Refusing to clean the primary repository directory.")
    if not path_is_relative_to(actual_worktree_path, root / ".worktrees"):
        errors.append(f"Refusing to clean a worktree outside {root / '.worktrees'}: {actual_worktree_path}")

    dirty = status_records(actual_worktree_path)
    if dirty is None:
        errors.append(f"Cannot read git status for worktree {actual_worktree_path}.")
    elif dirty:
        errors.append("Worktree has tracked, staged, untracked, or local-only changes; classify and preserve them before cleanup.")

    merged = is_ancestor(root, branch, main_branch) if branch_head and main_head else None
    if merged is not True:
        errors.append(f"Branch {branch} is not merged into local {main_branch}.")

    backups = backup_refs_for_branch(root, branch)
    if not backups:
        errors.append(f"No local rollback backup ref found under refs/backup/local-main/*-before-{branch}.")

    claim = load_completed_claim(actual_worktree_path, branch)
    if not claim:
        errors.append(f"No completed session claim found for branch {branch} in {actual_worktree_path / '.omx/session-claims'}.")

    if main_head and branch_head and main_head == branch_head:
        info.append(f"Local {main_branch} already points at branch {branch} head.")
    elif merged is True:
        info.append(f"Branch {branch} is contained in local {main_branch}.")

    return payload(root, branch, actual_worktree_path, main_branch, main_head, branch_head, backups, claim, errors, warnings, info)


def payload(
    root: Path,
    branch: str,
    worktree_path: Path | None,
    main_branch: str,
    main_head: str | None,
    branch_head: str | None,
    backup_refs: list[str],
    claim: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
    info: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "cleanup_ready": not errors,
        "root": str(root),
        "branch": branch,
        "worktree": str(worktree_path) if worktree_path else None,
        "main_branch": main_branch,
        "main_head": main_head,
        "branch_head": branch_head,
        "backup_refs": backup_refs,
        "claim_status": claim.get("status") if claim else None,
        "claim_source": claim.get("_source_claim_path") if claim else None,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "safety_policy": {
            "requires_branch_merged_to_main": True,
            "requires_clean_worktree": True,
            "requires_worktree_under_dot_worktrees": True,
            "requires_completed_claim": True,
            "requires_rollback_backup_ref": True,
            "deletes_remote_refs": False,
            "deletes_backup_refs": False,
            "uses_force_branch_delete": False,
        },
    }


def execute_cleanup(result: dict[str, Any]) -> dict[str, Any]:
    if not result["cleanup_ready"]:
        return result
    root = Path(result["root"]).resolve()
    branch = str(result["branch"])
    worktree_path = Path(str(result["worktree"])).resolve()
    claim = load_completed_claim(worktree_path, branch)
    preserved_claim = copy_claim_to_primary(root, claim or {}, branch, result)
    remove_worktree = run_git(root, ["worktree", "remove", str(worktree_path)])
    if remove_worktree.returncode != 0:
        result["errors"].append(remove_worktree.stderr.strip() or "git worktree remove failed")
        result["ok"] = False
        result["cleanup_ready"] = False
        return result
    delete_branch = run_git(root, ["branch", "-d", branch])
    if delete_branch.returncode != 0:
        result["errors"].append(delete_branch.stderr.strip() or "git branch -d failed")
        result["ok"] = False
        result["cleanup_ready"] = False
        return result
    result["executed"] = True
    result["preserved_claim"] = str(preserved_claim)
    result["removed_worktree"] = str(worktree_path)
    result["deleted_branch"] = branch
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely remove an already-integrated feature worktree and local branch.")
    parser.add_argument("--root", default=".", help="Primary repository root.")
    parser.add_argument("--branch", required=True, help="Local feature branch to clean.")
    parser.add_argument("--worktree", default=None, help="Expected feature worktree path. Defaults to the registered worktree for --branch.")
    parser.add_argument("--main-branch", default="main", help="Local integration branch.")
    parser.add_argument("--execute", action="store_true", help="Actually remove the worktree and delete the local branch after checks pass.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    worktree_path = Path(args.worktree).resolve() if args.worktree else None
    result = evaluate(Path(args.root), args.branch, worktree_path, args.main_branch)
    if args.execute:
        result = execute_cleanup(result)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["info"]:
            print(message)
        for message in result["warnings"]:
            print(f"WARNING: {message}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        if result.get("executed"):
            print(f"Removed worktree and deleted local branch: {args.branch}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
