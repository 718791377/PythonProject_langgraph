#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DOC_PREFIXES = ("docs_bilingual/", "openspec/", "docs/")
DOC_EXACT_PATHS = {"完整提交流程.md"}
DOCS_BILINGUAL_PREFIX = "docs_bilingual/"
DEFAULT_RECEIPT = ".omx/worktree-task-receipt.json"


def run_git(root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-c", "core.quotePath=false", "-C", str(root), *args], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
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


def normalize_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def diff_paths(root: Path, base_ref: str, head_ref: str) -> list[str]:
    result = run_git(root, ["diff", "--name-only", f"{base_ref}..{head_ref}"], check=True)
    return [normalize_path(line) for line in result.stdout.splitlines() if line.strip()]


def is_docs_path(path: str) -> bool:
    return path in DOC_EXACT_PATHS or path.startswith(DOC_PREFIXES)


def is_docs_bilingual_path(path: str) -> bool:
    return path.startswith(DOCS_BILINGUAL_PREFIX)


def require_governance_confirmation_diff(paths: list[str]) -> None:
    if not paths:
        raise RuntimeError("Governance-confirmation stage has no changed paths to merge.")
    non_docs = [path for path in paths if not is_docs_path(path)]
    if non_docs:
        raise RuntimeError("Governance-confirmation stage must be docs-only; non-doc paths: " + ", ".join(non_docs))
    if not any(is_docs_bilingual_path(path) for path in paths):
        raise RuntimeError("Governance-confirmation stage must update docs_bilingual/ first.")


def load_receipt(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_governance_receipt(path: Path, *, branch: str, commit: str) -> None:
    payload = load_receipt(path)
    now = datetime.now(timezone.utc).isoformat()
    payload.update(
        {
            "schema_version": payload.get("schema_version", 1),
            "branch": payload.get("branch", branch),
            "updated_at": now,
            "requires_user_confirmation_before_implementation": True,
            "governance_package_commit": commit,
            "governance_package_merged_to_local_main": True,
            "implementation_confirmed_by_user": False,
            "implementation_confirmation_recorded_at": None,
            "implementation_stage": "awaiting_confirmation",
            "next_action": "Await current user confirmation before non-document implementation.",
        }
    )
    write_receipt(path, payload)


def require_implementation_confirmation(path: Path) -> None:
    payload = load_receipt(path)
    if not payload:
        raise RuntimeError(f"Implementation stage requires receipt confirmation, but receipt is missing: {path}")
    if payload.get("requires_user_confirmation_before_implementation") is not True:
        raise RuntimeError("Receipt must set requires_user_confirmation_before_implementation=true before implementation stage.")
    if payload.get("implementation_confirmed_by_user") is not True:
        raise RuntimeError("Implementation stage requires implementation_confirmed_by_user=true in the receipt.")
    if not payload.get("implementation_confirmation_recorded_at"):
        raise RuntimeError("Implementation stage requires implementation_confirmation_recorded_at in the receipt.")
    if payload.get("governance_package_merged_to_local_main") is not True:
        raise RuntimeError("Implementation stage requires governance_package_merged_to_local_main=true in the receipt.")
    if not payload.get("governance_package_commit"):
        raise RuntimeError("Implementation stage requires governance_package_commit in the receipt.")


def run_local_gate(script_root: Path, label: str) -> None:
    gate = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_root / "tools/ci/local_gate.ps1")],
        cwd=str(script_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if gate.returncode != 0:
        raise RuntimeError(f"{label} local_gate.ps1 failed\n" + gate.stdout + gate.stderr)


def run_local_mr_review(worktree: Path, main_ref: str, branch: str) -> None:
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
            main_ref,
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Complete a local feature branch flow through local main and stop at the remote publication gate.")
    parser.add_argument("--root", default=".", help="Primary repository root, normally D:\\PythonProject_langgraph.")
    parser.add_argument("--worktree", default=None, help="Feature worktree path. Defaults to current working directory.")
    parser.add_argument("--branch", default=None, help="Feature branch name. Defaults to the worktree current branch.")
    parser.add_argument("--main", default="main", help="Local main branch name.")
    parser.add_argument("--stage", choices=("standard", "governance-confirmation", "implementation"), default="standard", help="Flow stage: standard final integration, Stage A governance confirmation, or Stage B implementation integration.")
    parser.add_argument("--receipt", default=DEFAULT_RECEIPT, help="Receipt JSON path relative to the feature worktree.")
    parser.add_argument("--skip-local-gate", action="store_true", help="Do not run local_gate.ps1; intended only when another checker already explains why the full gate cannot run.")
    parser.add_argument("--skip-local-mr-review", action="store_true", help="Do not run local_mr_review.ps1; intended only for explicitly justified diagnostics.")
    parser.add_argument("--execute", action="store_true", help="Actually create backup ref, merge, and optionally run gates. Without this flag, print the planned actions only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    worktree = Path(args.worktree).resolve() if args.worktree else Path.cwd().resolve()
    receipt_path = worktree / args.receipt
    branch = args.branch or current_branch(worktree)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_branch = branch.replace("/", "-")
    backup_ref = f"refs/backup/local-main/{timestamp}-before-{safe_branch}"
    actions: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    stop_state = "remote_publication_gate"
    changed_paths: list[str] = []
    governance_package_commit: str | None = None

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

        changed_paths = diff_paths(root, args.main, branch)
        if args.stage == "governance-confirmation":
            require_governance_confirmation_diff(changed_paths)
            governance_package_commit = run_git(root, ["rev-parse", branch], check=True).stdout.strip()
            stop_state = "awaiting_implementation_confirmation"
        elif args.stage == "implementation":
            require_implementation_confirmation(receipt_path)

        actions.extend([
            f"verify feature worktree clean: {worktree}",
            f"verify primary root clean and on {args.main}: {root}",
            f"validate stage: {args.stage}",
            f"create rollback backup ref {backup_ref} -> {args.main}",
            f"merge --ff-only {branch} into {args.main}",
            "stop before GitLab/GitHub remote publication",
        ])
        if args.stage == "governance-confirmation":
            actions.append("record receipt as awaiting implementation confirmation")
        if not args.skip_local_gate:
            actions.insert(3, "run tools/ci/local_gate.ps1 in feature worktree")
            actions.append("run tools/ci/local_gate.ps1 in primary root after merge")
        if not args.skip_local_mr_review:
            insert_at = 4 if not args.skip_local_gate else 3
            actions.insert(insert_at, "run tools/ci/local_mr_review.ps1 in feature worktree")

        if args.execute:
            if not args.skip_local_gate:
                run_local_gate(worktree, "feature")
            if not args.skip_local_mr_review:
                run_local_mr_review(worktree, args.main, branch)
            run_git(root, ["update-ref", backup_ref, args.main], check=True)
            run_git(root, ["merge", "--ff-only", branch], check=True)
            if args.stage == "governance-confirmation":
                assert governance_package_commit is not None
                record_governance_receipt(receipt_path, branch=branch, commit=governance_package_commit)
            if not args.skip_local_gate:
                run_local_gate(root, "main")
    except Exception as exc:
        errors.append(str(exc))

    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": not errors,
        "executed": args.execute,
        "stage": args.stage,
        "root": str(root),
        "worktree": str(worktree),
        "branch": branch,
        "main": args.main,
        "backup_ref": backup_ref,
        "changed_paths": changed_paths,
        "receipt": str(receipt_path),
        "remote_publication_performed": False,
        "stop_state": stop_state,
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
