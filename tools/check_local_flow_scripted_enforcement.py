#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "local_flow_scripted_enforcement"
COMPLETE_FLOW_DOC = Path("完整提交流程.md")
POLICY_EN = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md")
POLICY_ZH = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md")
PLAN_EXIT_CHECKER = Path("tools/check_plan_exit_execution_governance.py")
LOCAL_FLOW_CHECKER = Path("tools/check_local_flow_scripted_enforcement.py")
LOCAL_FLOW_HELPER = Path("tools/complete_local_flow_to_remote_gate.py")
LOCAL_RETIRE_LOCK = Path("tools/local_main_retire_lock.py")
LOCAL_RETIRE_LOCK_CHECKER = Path("tools/check_local_main_retire_lock.py")
SCHEDULER_ROB_PLAN_EN = Path("docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md")
SCHEDULER_ROB_PLAN_ZH = Path("docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md")
LOCAL_MR_REVIEW = Path("tools/ci/local_mr_review.ps1")
RUN_GUARD = Path("tools/run_openspec_guard.py")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")

REQUIRED_DOC_TERMS = [
    "完整本地提交流程",
    "git merge --ff-only <feature-branch>",
    "提交前必须检查 Git 状态和 worktree",
    "远端发布门",
    "tools/check_plan_exit_execution_governance.py",
    "tools/complete_local_flow_to_remote_gate.py",
    "local-main-retire.lock",
]
REQUIRED_POLICY_EN_TERMS = [
    "Post-Plan Local Governance Package",
    "complete local commit flow",
    "remote publication gate",
    "tools/check_plan_exit_execution_governance.py",
    "tools/complete_local_flow_to_remote_gate.py",
    "tools/local_main_retire_lock.py",
    "tools/ci/local_mr_review.ps1",
]
REQUIRED_POLICY_ZH_TERMS = [
    "`/plan` 之后的本地治理包",
    "完整本地提交流程",
    "远端发布门",
    "tools/check_plan_exit_execution_governance.py",
    "tools/complete_local_flow_to_remote_gate.py",
    "tools/local_main_retire_lock.py",
    "tools/ci/local_mr_review.ps1",
]
REQUIRED_TESTS = {
    "check_plan_exit_execution_governance.test.py",
    "check_local_flow_scripted_enforcement.test.py",
    "check_local_main_retire_lock.test.py",
    "check_complete_local_flow_self_retire_preflight.test.py",
}
REQUIRED_PLAN_EXIT_TERMS = [
    "requires_user_confirmation_before_implementation",
    "implementation_confirmed_by_user",
    "governance_package_commit",
    "governance_package_merged_to_local_main",
    "implementation_plan",
    "active registered implementation-plan",
    "confirmed Stage A receipt/claim",
]
REQUIRED_LOCAL_FLOW_HELPER_TERMS = [
    "governance-confirmation",
    "--implementation-plan",
    "implementation_confirmed_by_user",
    "implementation_plan",
    "awaiting_implementation_confirmation",
    "Governance-confirmation stage must be docs-only",
    "--self-retire",
    "--acquire-retire-lock",
    "local_main_retire_lock.py",
    "self_retire_lock",
    "preflight_self_retire_rob_entry",
    "REQUIRED_SELF_RETIRE_GATES",
]
REQUIRED_RETIRE_LOCK_TERMS = [
    "local-main-retire",
    "owner_session_id",
    "nonce",
    "reclaim-stale",
]
REQUIRED_PARALLEL_ADMISSION_TERMS = [
    "Work-Conserving",
    "eligible",
    "hotspot lease",
    "resource backpressure",
    "local-main retire",
]
def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")


def read_text(root: Path, relative: Path, errors: list[str]) -> str:
    path = root / relative
    if not path.exists():
        errors.append(f"Missing required file: {relative.as_posix()}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{relative.as_posix()} is not valid UTF-8: {exc}")
        return ""


def require_terms(label: str, text: str, terms: list[str], errors: list[str]) -> None:
    for term in terms:
        if term not in text:
            errors.append(f"{label} is missing required term: {term}")


def changed_paths(root: Path, base_ref: str, head_ref: str) -> tuple[list[str], list[str]]:
    result = run_git(root, ["diff", "--name-only", f"{base_ref}..{head_ref}"])
    if result.returncode != 0:
        return [], [result.stderr.strip() or result.stdout.strip() or "git diff failed"]
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()], []


def current_branch(root: Path) -> str | None:
    result = run_git(root, ["branch", "--show-current"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def evaluate(root: Path, base_ref: str | None, head_ref: str | None, require_main_for_plan_changes: bool) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    complete_flow = read_text(root, COMPLETE_FLOW_DOC, errors)
    policy_en = read_text(root, POLICY_EN, errors)
    policy_zh = read_text(root, POLICY_ZH, errors)
    local_mr_review = read_text(root, LOCAL_MR_REVIEW, errors)
    run_guard = read_text(root, RUN_GUARD, errors)
    manifest_text = read_text(root, CI_MANIFEST, errors)
    plan_exit_checker = read_text(root, PLAN_EXIT_CHECKER, errors)
    local_flow_helper = read_text(root, LOCAL_FLOW_HELPER, errors)
    retire_lock = read_text(root, LOCAL_RETIRE_LOCK, errors)
    retire_lock_checker = read_text(root, LOCAL_RETIRE_LOCK_CHECKER, errors)
    scheduler_plan_en = read_text(root, SCHEDULER_ROB_PLAN_EN, errors)
    scheduler_plan_zh = read_text(root, SCHEDULER_ROB_PLAN_ZH, errors)

    require_terms(COMPLETE_FLOW_DOC.as_posix(), complete_flow, REQUIRED_DOC_TERMS, errors)
    require_terms(COMPLETE_FLOW_DOC.as_posix(), complete_flow, REQUIRED_PARALLEL_ADMISSION_TERMS, errors)
    require_terms(POLICY_EN.as_posix(), policy_en, REQUIRED_POLICY_EN_TERMS, errors)
    require_terms(POLICY_ZH.as_posix(), policy_zh, REQUIRED_POLICY_ZH_TERMS, errors)
    require_terms(LOCAL_MR_REVIEW.as_posix(), local_mr_review, ["check_plan_exit_execution_governance.py"], errors)
    require_terms(RUN_GUARD.as_posix(), run_guard, ["check_local_flow_scripted_enforcement"], errors)
    require_terms(PLAN_EXIT_CHECKER.as_posix(), plan_exit_checker, REQUIRED_PLAN_EXIT_TERMS, errors)
    require_terms(LOCAL_FLOW_HELPER.as_posix(), local_flow_helper, REQUIRED_LOCAL_FLOW_HELPER_TERMS, errors)
    require_terms(LOCAL_RETIRE_LOCK.as_posix(), retire_lock, REQUIRED_RETIRE_LOCK_TERMS, errors)
    require_terms(LOCAL_RETIRE_LOCK_CHECKER.as_posix(), retire_lock_checker, REQUIRED_RETIRE_LOCK_TERMS, errors)
    for plan_path, plan_text in (
        (SCHEDULER_ROB_PLAN_EN, scheduler_plan_en),
        (SCHEDULER_ROB_PLAN_ZH, scheduler_plan_zh),
    ):
        require_terms(plan_path.as_posix(), plan_text, REQUIRED_PARALLEL_ADMISSION_TERMS, errors)
    info.append(
        "Parent orchestration plans are optional references and are not a global local-flow gate for unrelated sessions."
    )
    info.append(
        "Local-flow hard gates are enforced on complete-flow policy, scheduler/ROB plan surfaces, helper scripts, lock scripts, and CI registration."
    )

    try:
        manifest = json.loads(manifest_text) if manifest_text else {}
    except json.JSONDecodeError as exc:
        errors.append(f"{CI_MANIFEST.as_posix()} is not valid JSON: {exc}")
        manifest = {}
    registered_tests = set(manifest.get("python_unittest", [])) if isinstance(manifest.get("python_unittest"), list) else set()
    for test_name in sorted(REQUIRED_TESTS - registered_tests):
        errors.append(f"{CI_MANIFEST.as_posix()} is missing required test registration: {test_name}")

    for relative in (PLAN_EXIT_CHECKER, LOCAL_FLOW_CHECKER, LOCAL_FLOW_HELPER, LOCAL_RETIRE_LOCK, LOCAL_RETIRE_LOCK_CHECKER):
        path = root / relative
        if not path.exists():
            errors.append(f"Missing required script/checker: {relative.as_posix()}")
        elif not path.is_file():
            errors.append(f"Required script/checker path is not a file: {relative.as_posix()}")

    range_changed_paths: list[str] = []
    if base_ref and head_ref:
        range_changed_paths, diff_errors = changed_paths(root, base_ref, head_ref)
        errors.extend(diff_errors)
        plan_paths = [path for path in range_changed_paths if path.startswith("docs_bilingual/implementation_plans/")]
        if plan_paths and require_main_for_plan_changes:
            branch = current_branch(root)
            if branch != "main":
                errors.append(
                    "Implementation-plan updates must complete the local flow into local main before stopping; run tools/complete_local_flow_to_remote_gate.py and stop at the remote publication gate."
                )
        if plan_paths:
            info.append(f"Implementation plan changed paths: {len(plan_paths)}")

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "range_changed_paths": len(range_changed_paths),
        },
        "changed_paths": range_changed_paths,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that local Comet/complete-commit flow is backed by scripts and optional range evidence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default=None, help="Optional range base ref.")
    parser.add_argument("--head-ref", default=None, help="Optional range head ref.")
    parser.add_argument("--require-main-for-plan-changes", action="store_true", help="Fail if implementation plan changes are not already on local main.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = evaluate(Path(args.root), args.base_ref, args.head_ref, args.require_main_for_plan_changes)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("Local flow scripted enforcement check passed.")
            for message in payload["info"]:
                print(f"  - {message}")
        else:
            print("Local flow scripted enforcement check failed:")
            for error in payload["errors"]:
                print(f"  - {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
