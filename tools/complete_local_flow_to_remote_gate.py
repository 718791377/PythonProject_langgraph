#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_git(root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result


def is_clean(root: Path) -> bool:
    result = run_git(root, ["status", "--porcelain", "--untracked-files=all"], check=True)
    return not result.stdout.strip()


def current_branch(root: Path) -> str:
    result = run_git(root, ["branch", "--show-current"], check=True)
    branch = result.stdout.strip()
    if not branch:
        raise RuntimeError("Current worktree is detached; local flow helper requires a named feature branch.")
    return branch


def main() -> int:
    parser = argparse.ArgumentParser(description="Complete a local feature branch flow through local main and stop at the remote publication gate.")
    parser.add_argument("--root", default=".", help="Primary repository root, normally D:\\PythonProject_langgraph.")
    parser.add_argument("--worktree", default=None, help="Feature worktree path. Defaults to current working directory.")
    parser.add_argument("--branch", default=None, help="Feature branch name. Defaults to the worktree current branch.")
    parser.add_argument("--main", default="main", help="Local main branch name.")
    parser.add_argument("--skip-local-gate", action="store_true", help="Do not run local_gate.ps1; intended only when another checker already explains why the full gate cannot run.")
    parser.add_argument("--skip-local-mr-review", action="store_true", help="Do not run local_mr_review.ps1; intended only for explicitly justified diagnostics.")
    parser.add_argument("--execute", action="store_true", help="Actually create backup ref, merge, and optionally run gates. Without this flag, print the planned actions only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    worktree = Path(args.worktree).resolve() if args.worktree else Path.cwd().resolve()
    branch = args.branch or current_branch(worktree)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_branch = branch.replace("/", "-")
    backup_ref = f"refs/backup/local-main/{timestamp}-before-{safe_branch}"
    actions: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    try:
        if branch == args.main:
            raise RuntimeError("Feature branch must not be local main.")
        if not is_clean(worktree):
            raise RuntimeError("Feature worktree is not clean; commit or remove drift before completing local flow.")
        main_branch = current_branch(root)
        if main_branch != args.main:
            raise RuntimeError(f"Primary root must be on {args.main}; current branch is {main_branch!r}.")
        if not is_clean(root):
            raise RuntimeError("Primary root is not clean; cannot merge into local main.")
        merge_base = run_git(root, ["merge-base", args.main, branch], check=True).stdout.strip()
        if not merge_base:
            raise RuntimeError("Unable to find merge base between local main and feature branch.")

        actions.extend([
            f"verify feature worktree clean: {worktree}",
            f"verify primary root clean and on {args.main}: {root}",
            f"create rollback backup ref {backup_ref} -> {args.main}",
            f"merge --ff-only {branch} into {args.main}",
            "stop before GitLab/GitHub remote publication",
        ])
        if not args.skip_local_gate:
            actions.insert(2, "run tools/ci/local_gate.ps1 in feature worktree")
            actions.append("run tools/ci/local_gate.ps1 in primary root after merge")
        if not args.skip_local_mr_review:
            insert_at = 3 if not args.skip_local_gate else 2
            actions.insert(insert_at, "run tools/ci/local_mr_review.ps1 in feature worktree")

        if args.execute:
            if not args.skip_local_gate:
                gate = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(worktree / "tools/ci/local_gate.ps1")], cwd=str(worktree), capture_output=True, text=True, encoding="utf-8", errors="replace")
                if gate.returncode != 0:
                    raise RuntimeError("feature local_gate.ps1 failed\n" + gate.stdout + gate.stderr)
            if not args.skip_local_mr_review:
                review = subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(worktree / "tools/ci/local_mr_review.ps1"),
                        "-Root",
                        str(worktree),
                        "-BaseRef",
                        args.main,
                        "-HeadRef",
                        branch,
                    ],
                    cwd=str(worktree),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if review.returncode != 0:
                    raise RuntimeError("feature local_mr_review.ps1 failed\n" + review.stdout + review.stderr)
            run_git(root, ["update-ref", backup_ref, args.main], check=True)
            run_git(root, ["merge", "--ff-only", branch], check=True)
            if not args.skip_local_gate:
                gate = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(root / "tools/ci/local_gate.ps1")], cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace")
                if gate.returncode != 0:
                    raise RuntimeError("main local_gate.ps1 failed after merge\n" + gate.stdout + gate.stderr)
    except Exception as exc:
        errors.append(str(exc))

    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": not errors,
        "executed": args.execute,
        "root": str(root),
        "worktree": str(worktree),
        "branch": branch,
        "main": args.main,
        "backup_ref": backup_ref,
        "remote_publication_performed": False,
        "stop_state": "remote_publication_gate",
        "actions": actions,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Local flow to remote publication gate " + ("completed." if payload["ok"] and args.execute else "planned."))
        for action in actions:
            print(f"  - {action}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
