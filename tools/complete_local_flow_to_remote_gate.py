#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import check_plan_exit_execution_governance as plan_exit
import commit_reorder_buffer as commit_rob
import advance_worktree_task_lifecycle as lifecycle

DOC_PREFIXES = ("docs_bilingual/", "openspec/", "docs/")
DOC_EXACT_PATHS = {"完整提交流程.md"}
DOCS_BILINGUAL_PREFIX = "docs_bilingual/"
IMPLEMENTATION_PLAN_PREFIX = "docs_bilingual/implementation_plans/"
DEFAULT_RECEIPT = ".omx/worktree-task-receipt.json"
REQUIRED_SELF_RETIRE_GATES = ("precommit_update_archive", "local_gate", "local_mr_review")


def run_json_tool(args: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("JSON tool returned invalid output: " + completed.stdout + completed.stderr) from exc
    if completed.returncode != 0 or not payload.get("ok"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload


def acquire_retire_lock(root: Path, *, session_id: str, branch: str, worktree: Path, entry_id: str, ttl_minutes: int) -> str:
    payload = run_json_tool(
        [
            str(Path(__file__).resolve().parent / "local_main_retire_lock.py"),
            "acquire",
            "--root",
            str(root),
            "--session-id",
            session_id,
            "--branch",
            branch,
            "--worktree",
            str(worktree),
            "--entry-id",
            entry_id,
            "--ttl-minutes",
            str(ttl_minutes),
        ],
        cwd=root,
    )
    nonce = str(payload.get("nonce") or payload.get("lock", {}).get("nonce") or "")
    if not nonce:
        raise RuntimeError("local-main retire lock acquire succeeded without returning a nonce")
    return nonce


def release_retire_lock(root: Path, nonce: str) -> None:
    run_json_tool(
        [
            str(Path(__file__).resolve().parent / "local_main_retire_lock.py"),
            "release",
            "--root",
            str(root),
            "--nonce",
            nonce,
        ],
        cwd=root,
    )


def record_self_retired_rob(root: Path, *, entry_id: str, rollback_ref: str, local_main_commit: str, session_id: str, lock_nonce: str) -> None:
    run_json_tool(
        [
            str(Path(__file__).resolve().parent / "commit_reorder_buffer.py"),
            "retire",
            "--root",
            str(root),
            "--entry-id",
            entry_id,
            "--rollback-ref",
            rollback_ref,
            "--local-main-commit",
            local_main_commit,
            "--retire-mode",
            "self_retire_lock",
            "--retire-owner-session-id",
            session_id,
            "--retire-lock-nonce",
            lock_nonce,
            "--evidence",
            "self-retired via tools/complete_local_flow_to_remote_gate.py",
        ],
        cwd=root,
    )


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


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def diff_paths(root: Path, base_ref: str, head_ref: str) -> list[str]:
    result = run_git(root, ["diff", "--name-only", f"{base_ref}..{head_ref}"], check=True)
    return [normalize_path(line) for line in result.stdout.splitlines() if line.strip()]


def is_docs_path(path: str) -> bool:
    return path in DOC_EXACT_PATHS or path.startswith(DOC_PREFIXES)


def is_docs_bilingual_path(path: str) -> bool:
    return path.startswith(DOCS_BILINGUAL_PREFIX)


def is_canonical_implementation_plan_path(path: str) -> bool:
    return (
        path.startswith(IMPLEMENTATION_PLAN_PREFIX)
        and path.endswith(".md")
        and not path.endswith(".zh-CN.md")
    )


def infer_implementation_plan(paths: list[str]) -> str | None:
    candidates = sorted({path for path in paths if is_canonical_implementation_plan_path(path)})
    if len(candidates) == 1:
        return candidates[0]
    return None


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


def safe_claim_name(branch: str) -> str:
    return branch.replace("/", "__").replace("\\", "__")


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return {}
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON payload must be an object: {path}")
    return payload


def write_json_object(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def claim_path_for_branch(worktree: Path, branch: str) -> Path:
    claim_root = worktree / ".omx" / "session-claims"
    exact = claim_root / f"{safe_claim_name(branch)}.json"
    if exact.exists():
        return exact
    if claim_root.exists():
        for path in sorted(claim_root.glob("*.json")):
            data = load_json_object(path)
            if data.get("branch") == branch:
                return path
    return exact


def record_local_main_completion(
    *,
    worktree: Path,
    branch: str,
    receipt_path: Path,
    rollback_ref: str,
    local_main_commit: str,
    local_feature_commit: str,
    preserve_carrier: bool,
) -> dict[str, str]:
    now = datetime.now(timezone.utc).isoformat()
    cleaned_worktree = "preserved-for-audit" if preserve_carrier else "pending-automatic-safe-cleanup"
    deleted_branch = "preserved-as-local-publication-carrier" if preserve_carrier else "pending-automatic-safe-cleanup"
    remote_sync_status = "not_authorized:remote_publication_gate_closed"
    claim_path = claim_path_for_branch(worktree, branch)
    receipt = load_receipt(receipt_path)
    claim = load_json_object(claim_path)
    base_state = str(receipt.get("lifecycle_status") or receipt.get("status") or claim.get("lifecycle_status") or claim.get("status") or "active")
    base_payload = {
        "schema_version": 1,
        "session_id": receipt.get("session_id") or claim.get("session_id") or safe_claim_name(branch),
        "status": base_state,
        "lifecycle_status": base_state,
        "branch": branch,
        "worktree": str(worktree),
        "task_name": receipt.get("task_name") or claim.get("task_name") or branch,
        "task_summary": receipt.get("task_summary") or claim.get("task_summary") or "local main integration",
        "document_plan_only": bool(receipt.get("document_plan_only", claim.get("document_plan_only", False))),
        "requires_code_implementation": bool(receipt.get("requires_code_implementation", claim.get("requires_code_implementation", True))),
        "created_at": receipt.get("created_at") or claim.get("created_at") or now,
        "expected_merge_or_pause": receipt.get("expected_merge_or_pause") or claim.get("expected_merge_or_pause") or "merge to local main",
        "next_action": receipt.get("next_action") or claim.get("next_action") or "complete local main integration",
        "requires_local_main_merge": True,
        "requires_remote_sync": False,
        "remote_publication_authorized": False,
        "paths": receipt.get("paths") or claim.get("paths") or [],
    }
    receipt.update({**base_payload, **receipt, "branch": branch, "worktree": str(worktree), "status": base_state, "lifecycle_status": base_state})
    claim.update({**base_payload, **claim, "branch": branch, "worktree": str(worktree), "status": base_state, "lifecycle_status": base_state})
    write_receipt(receipt_path, receipt)
    write_json_object(claim_path, claim)

    def _state() -> str:
        current = load_receipt(receipt_path)
        return str(current.get("lifecycle_status") or current.get("status") or "active")

    if _state() in {"active", "paused"}:
        lifecycle.advance_lifecycle(
            worktree=worktree,
            branch=branch,
            next_state="ready-to-merge",
            owner="tools/complete_local_flow_to_remote_gate.py",
            evidence_paths=["tools/ci/local_gate.ps1", "tools/ci/local_mr_review.ps1"],
            cleanup_decision="pending-local-main-merge",
            reason="local gates passed before local main integration",
        )
    if _state() == "ready-to-merge":
        lifecycle.advance_lifecycle(
            worktree=worktree,
            branch=branch,
            next_state="merged-local-main",
            owner="tools/complete_local_flow_to_remote_gate.py",
            evidence_paths=["git merge --ff-only", "post-merge local gate"],
            cleanup_decision=cleaned_worktree,
            reason="local main integration completed; remote publication gate remains closed",
            rollback_ref=rollback_ref,
            local_main_commit=local_main_commit,
            cleaned_worktree=cleaned_worktree,
            deleted_branch=deleted_branch,
            remote_sync_status=remote_sync_status,
        )
    if _state() == "merged-local-main":
        lifecycle.advance_lifecycle(
            worktree=worktree,
            branch=branch,
            next_state="completed",
            owner="tools/complete_local_flow_to_remote_gate.py",
            evidence_paths=["post-merge local gate", "remote publication gate stop"],
            cleanup_decision=cleaned_worktree,
            reason="local package completed; remote publication not authorized",
            rollback_ref=rollback_ref,
            local_main_commit=local_main_commit,
            cleaned_worktree=cleaned_worktree,
            deleted_branch=deleted_branch,
            remote_sync_status=remote_sync_status,
        )

    common_updates: dict[str, Any] = {
        "updated_at": now,
        "completed_at": now,
        "local_feature_commit": local_feature_commit,
        "local_main_commit": local_main_commit,
        "merged_local_main_commit": local_main_commit,
        "rollback_ref": rollback_ref,
        "requires_local_main_merge": False,
        "requires_remote_sync": False,
        "remote_publication_authorized": False,
        "remote_publication_performed": False,
        "remote_publication_status": "not_authorized",
        "remote_sync_status": remote_sync_status,
        "next_action": "Local main integration and post-merge local gate complete; stopped at the remote publication gate until explicit GitLab/GitHub publication approval.",
    }
    claim = load_json_object(claim_path)
    claim.update({"status": "completed", "lifecycle_status": "completed", **common_updates})
    write_json_object(claim_path, claim)
    receipt = load_receipt(receipt_path)
    receipt.update({"status": "completed", "lifecycle_status": "completed", **common_updates})
    write_receipt(receipt_path, receipt)
    return {"claim_path": str(claim_path), "receipt_path": str(receipt_path)}


def record_governance_receipt(path: Path, *, branch: str, commit: str, implementation_plan: str) -> None:
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
            "implementation_plan": implementation_plan,
            "implementation_confirmed_by_user": False,
            "implementation_confirmation_recorded_at": None,
            "implementation_stage": "awaiting_confirmation",
            "next_action": "Await current user confirmation before non-document implementation.",
        }
    )
    write_receipt(path, payload)


def require_implementation_confirmation(path: Path, *, root: Path, main_ref: str) -> None:
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
    plan = plan_exit.implementation_plan_from_payload(payload)
    validation_errors = plan_exit.validate_implementation_plan_confirmation(
        root,
        plan,
        str(payload.get("governance_package_commit") or ""),
        main_ref,
    )
    if validation_errors:
        raise RuntimeError(
            "Implementation stage requires active or final registered implementation-plan confirmation: "
            + "; ".join(validation_errors)
        )


def resolved_path_key(root: Path, value: str | None) -> str:
    path = Path(value or ".")
    if not path.is_absolute():
        path = root / path
    return str(path.resolve()).casefold()


def load_self_retire_rob_entry(root: Path, entry_id: str) -> dict[str, Any]:
    path = commit_rob.entry_path(root, entry_id)
    try:
        entry = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"ROB entry not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ROB entry is not valid JSON: {path}: {exc}") from exc
    if not isinstance(entry, dict):
        raise RuntimeError(f"ROB entry must be a JSON object: {path}")
    return entry


def expected_self_retire_implementation_plan(receipt_path: Path, implementation_plan: str | None) -> str:
    if implementation_plan:
        return normalize_path(implementation_plan)
    receipt = load_receipt(receipt_path)
    plan = str(receipt.get("implementation_plan") or "").strip()
    if not plan:
        raise RuntimeError(
            "--self-retire requires --implementation-plan or receipt implementation_plan before ROB preflight."
        )
    return normalize_path(plan)


def preflight_self_retire_rob_entry(
    root: Path,
    *,
    worktree: Path,
    branch: str,
    session_id: str,
    entry_id: str,
    receipt_path: Path,
    implementation_plan: str | None,
) -> dict[str, Any]:
    entry = load_self_retire_rob_entry(root, entry_id)
    expected_plan = expected_self_retire_implementation_plan(receipt_path, implementation_plan)
    errors: list[str] = []

    state = str(entry.get("state") or "")
    if state != "ready":
        errors.append(f"ROB entry {entry_id} state must be ready before self-retire; got {state!r}")
    actual_session = str(entry.get("session_id") or "")
    if actual_session != session_id:
        errors.append(f"ROB entry {entry_id} session_id mismatch: expected {session_id!r}, got {actual_session!r}")
    actual_branch = str(entry.get("branch") or "")
    if actual_branch != branch:
        errors.append(f"ROB entry {entry_id} branch mismatch: expected {branch!r}, got {actual_branch!r}")
    actual_plan = normalize_path(str(entry.get("implementation_plan") or ""))
    if actual_plan != expected_plan:
        errors.append(
            f"ROB entry {entry_id} implementation_plan mismatch: expected {expected_plan!r}, got {actual_plan!r}"
        )
    actual_worktree = str(entry.get("worktree") or "")
    if actual_worktree and resolved_path_key(root, actual_worktree) != resolved_path_key(root, str(worktree)):
        errors.append(
            f"ROB entry {entry_id} worktree mismatch: expected {str(worktree)!r}, got {actual_worktree!r}"
        )

    gate_status = entry.get("gate_status") or {}
    if not isinstance(gate_status, dict):
        errors.append(f"ROB entry {entry_id} gate_status must be a JSON object")
        gate_status = {}
    for gate in REQUIRED_SELF_RETIRE_GATES:
        status = str(gate_status.get(gate) or "")
        if status != "passed":
            errors.append(f"ROB entry {entry_id} gate_status.{gate} must be passed before self-retire; got {status!r}")

    if errors:
        raise RuntimeError("; ".join(errors))
    return {
        "entry_id": entry_id,
        "state": state,
        "session_id": actual_session,
        "branch": actual_branch,
        "implementation_plan": actual_plan,
        "required_gate_status": {gate: str(gate_status.get(gate) or "") for gate in REQUIRED_SELF_RETIRE_GATES},
    }


def run_local_gate(script_root: Path, label: str, *, step_timeout_seconds: int) -> None:
    gate = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_root / "tools/ci/local_gate.ps1"),
            "-StepTimeoutSeconds",
            str(step_timeout_seconds),
        ],
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


def run_integrated_worktree_cleanup(root: Path, *, branch: str, worktree: Path, main_ref: str) -> dict[str, Any]:
    cleanup_script = root / "tools" / "cleanup_integrated_worktree.py"
    if not cleanup_script.exists():
        cleanup_script = Path(__file__).resolve().with_name("cleanup_integrated_worktree.py")
    cleanup = subprocess.run(
        [
            sys.executable,
            str(cleanup_script),
            "--root",
            str(root),
            "--branch",
            branch,
            "--worktree",
            str(worktree),
            "--main-branch",
            main_ref,
            "--execute",
            "--json",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        payload = json.loads(cleanup.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("cleanup_integrated_worktree.py returned invalid JSON: " + cleanup.stdout + cleanup.stderr) from exc
    if cleanup.returncode != 0 or not payload.get("ok"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Complete a local feature branch flow through local main and stop at the remote publication gate.")
    parser.add_argument("--root", default=".", help="Primary repository root, normally D:\\PythonProject_langgraph.")
    parser.add_argument("--worktree", default=None, help="Feature worktree path. Defaults to current working directory.")
    parser.add_argument("--branch", default=None, help="Feature branch name. Defaults to the worktree current branch.")
    parser.add_argument("--main", default="main", help="Local main branch name.")
    parser.add_argument("--stage", choices=("standard", "governance-confirmation", "implementation"), default="standard", help="Flow stage: standard final integration, Stage A governance confirmation, or Stage B implementation integration.")
    parser.add_argument("--implementation-plan", default=None, help="Confirmed implementation-plan file for governance-confirmation or implementation stages.")
    parser.add_argument("--receipt", default=DEFAULT_RECEIPT, help="Receipt JSON path relative to the feature worktree.")
    parser.add_argument("--skip-local-gate", action="store_true", help="Do not run local_gate.ps1; intended only when another checker already explains why the full gate cannot run.")
    parser.add_argument("--skip-local-mr-review", action="store_true", help="Do not run local_mr_review.ps1; intended only for explicitly justified diagnostics.")
    parser.add_argument("--self-retire", action="store_true", help="Allow this session to acquire the local-main retire lock and retire its own ready ROB entry.")
    parser.add_argument("--session-id", default=None, help="Session id required for --self-retire or --acquire-retire-lock.")
    parser.add_argument("--rob-entry-id", default=None, help="ROB entry id required for --self-retire or --acquire-retire-lock.")
    parser.add_argument("--acquire-retire-lock", action="store_true", help="Acquire the local-main retire lock around the local-main mutation.")
    parser.add_argument("--lock-ttl-minutes", type=int, default=120, help="TTL for the local-main retire lock.")
    parser.add_argument("--preserve-carrier", action="store_true", help="After local main integration, preserve the local feature worktree and branch instead of running safe cleanup.")
    parser.add_argument("--local-gate-step-timeout-seconds", type=int, default=600, help="Per-step timeout passed to tools/ci/local_gate.ps1 for feature and post-merge gates.")
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
    implementation_plan: str | None = None
    use_retire_lock = bool(args.self_retire or args.acquire_retire_lock)
    retire_lock_nonce: str | None = None
    self_retire_rob_preflight: dict[str, Any] | None = None
    completion_records: dict[str, str] | None = None
    cleanup_result: dict[str, Any] | None = None

    try:
        if branch == args.main:
            raise RuntimeError("Feature branch must not be local main.")
        if use_retire_lock and not args.session_id:
            raise RuntimeError("--session-id is required when acquiring the local-main retire lock.")
        if use_retire_lock and not args.rob_entry_id:
            raise RuntimeError("--rob-entry-id is required when acquiring the local-main retire lock.")
        if not is_clean(worktree):
            raise RuntimeError("Feature worktree is not clean; commit or remove drift before completing local flow.")
        if args.execute and not args.preserve_carrier and path_is_relative_to(Path.cwd(), worktree):
            raise RuntimeError(
                "Automatic cleanup cannot remove the process current worktree safely; "
                "rerun this helper from the primary root or pass --preserve-carrier."
            )
        main_branch = current_branch(root)
        if main_branch != args.main:
            raise RuntimeError(f"Primary root must be on {args.main}; current branch is {main_branch!r}.")
        if not is_clean(root):
            raise RuntimeError("Primary root is not clean; cannot merge into local main.")
        merge_base = run_git(root, ["merge-base", args.main, branch], check=True).stdout.strip()
        if not merge_base:
            raise RuntimeError("Unable to find merge base between local main and feature branch.")
        if args.self_retire:
            assert args.session_id is not None
            assert args.rob_entry_id is not None
            self_retire_rob_preflight = preflight_self_retire_rob_entry(
                root,
                worktree=worktree,
                branch=branch,
                session_id=args.session_id,
                entry_id=args.rob_entry_id,
                receipt_path=receipt_path,
                implementation_plan=args.implementation_plan,
            )

        changed_paths = diff_paths(root, args.main, branch)
        if args.stage == "governance-confirmation":
            require_governance_confirmation_diff(changed_paths)
            implementation_plan = plan_exit.normalize_path(args.implementation_plan) if args.implementation_plan else infer_implementation_plan(changed_paths)
            if not implementation_plan:
                raise RuntimeError(
                    "Governance-confirmation stage requires --implementation-plan or exactly one canonical implementation-plan file in the branch diff."
                )
            if implementation_plan not in changed_paths:
                raise RuntimeError(
                    "Governance-confirmation stage implementation plan must be part of the committed docs package: "
                    + implementation_plan
                )
            governance_package_commit = run_git(root, ["rev-parse", branch], check=True).stdout.strip()
            stop_state = "awaiting_implementation_confirmation"
        elif args.stage == "implementation":
            require_implementation_confirmation(receipt_path, root=root, main_ref=args.main)

        actions.extend([
            f"verify feature worktree clean: {worktree}",
            f"verify primary root clean and on {args.main}: {root}",
            f"validate stage: {args.stage}",
            f"create rollback backup ref {backup_ref} -> {args.main}",
            f"merge --ff-only {branch} into {args.main}",
            "record completed claim and worktree receipt for local main integration",
            "stop before GitLab/GitHub remote publication",
        ])
        if use_retire_lock:
            actions.insert(3, "acquire .omx/locks/local-main-retire.lock before mutating local main")
            actions.append("release .omx/locks/local-main-retire.lock after retire attempt")
            if args.self_retire:
                actions.append("record ROB entry as retired with self_retire_lock evidence")
        if args.stage == "governance-confirmation":
            actions.append("record receipt as awaiting implementation confirmation for " + str(implementation_plan))
        if args.preserve_carrier:
            actions.append("preserve feature worktree and local feature branch by explicit --preserve-carrier")
        else:
            actions.append("run safe cleanup for the integrated local feature worktree and branch")
        if not args.skip_local_gate:
            actions.insert(3, f"run tools/ci/local_gate.ps1 in feature worktree (step timeout {args.local_gate_step_timeout_seconds}s)")
            actions.append(f"run tools/ci/local_gate.ps1 in primary root after merge (step timeout {args.local_gate_step_timeout_seconds}s)")
        if not args.skip_local_mr_review:
            insert_at = 4 if not args.skip_local_gate else 3
            actions.insert(insert_at, "run tools/ci/local_mr_review.ps1 in feature worktree")

        if args.execute:
            if not args.skip_local_gate:
                run_local_gate(worktree, "feature", step_timeout_seconds=args.local_gate_step_timeout_seconds)
            if not args.skip_local_mr_review:
                run_local_mr_review(worktree, args.main, branch)
            try:
                if use_retire_lock:
                    assert args.session_id is not None
                    assert args.rob_entry_id is not None
                    retire_lock_nonce = acquire_retire_lock(
                        root,
                        session_id=args.session_id,
                        branch=branch,
                        worktree=worktree,
                        entry_id=args.rob_entry_id,
                        ttl_minutes=args.lock_ttl_minutes,
                    )
                    if not is_clean(root):
                        raise RuntimeError("Primary root became dirty after acquiring the local-main retire lock.")
                run_git(root, ["update-ref", backup_ref, args.main], check=True)
                run_git(root, ["merge", "--ff-only", branch], check=True)
                if args.stage == "governance-confirmation":
                    assert governance_package_commit is not None
                    assert implementation_plan is not None
                    record_governance_receipt(
                        receipt_path,
                        branch=branch,
                        commit=governance_package_commit,
                        implementation_plan=implementation_plan,
                    )
                if not args.skip_local_gate:
                    run_local_gate(root, "main", step_timeout_seconds=args.local_gate_step_timeout_seconds)
                local_main_commit = run_git(root, ["rev-parse", args.main], check=True).stdout.strip()
                local_feature_commit = run_git(root, ["rev-parse", branch], check=True).stdout.strip()
                completion_records = record_local_main_completion(
                    worktree=worktree,
                    branch=branch,
                    receipt_path=receipt_path,
                    rollback_ref=backup_ref,
                    local_main_commit=local_main_commit,
                    local_feature_commit=local_feature_commit,
                    preserve_carrier=args.preserve_carrier,
                )
                if args.self_retire:
                    assert args.session_id is not None
                    assert args.rob_entry_id is not None
                    assert retire_lock_nonce is not None
                    record_self_retired_rob(
                        root,
                        entry_id=args.rob_entry_id,
                        rollback_ref=backup_ref,
                        local_main_commit=local_main_commit,
                        session_id=args.session_id,
                        lock_nonce=retire_lock_nonce,
                    )
                if not args.preserve_carrier:
                    os.chdir(root)
                    cleanup_result = run_integrated_worktree_cleanup(
                        root,
                        branch=branch,
                        worktree=worktree,
                        main_ref=args.main,
                    )
            finally:
                if retire_lock_nonce:
                    release_retire_lock(root, retire_lock_nonce)
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
        "implementation_plan": implementation_plan,
        "receipt": str(receipt_path),
        "remote_publication_performed": False,
        "preserve_carrier": args.preserve_carrier,
        "automatic_cleanup_enabled": not args.preserve_carrier,
        "completion_records": completion_records,
        "cleanup_result": cleanup_result,
        "retire_lock_used": use_retire_lock,
        "retire_lock_nonce": retire_lock_nonce,
        "self_retire_rob_preflight": self_retire_rob_preflight,
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
