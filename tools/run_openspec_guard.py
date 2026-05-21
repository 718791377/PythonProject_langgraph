#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def emit_line(stream: object, text: str) -> None:
    encoding = getattr(stream, "encoding", None) or "utf-8"
    if hasattr(stream, "buffer"):
        stream.buffer.write((text + "\n").encode(encoding, errors="replace"))
    else:
        stream.write(text + "\n")


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout:
        emit_line(sys.stdout, stdout)
    if stderr:
        emit_line(sys.stderr, stderr)


def run_checked(command: list[str], cwd: Path, failure_message: str) -> None:
    result = run(command, cwd=cwd)
    print_output(result)
    if result.returncode != 0:
        raise SystemExit(failure_message)


def run_json_command(command: list[str], cwd: Path, step_name: str) -> dict:
    result = run(command, cwd=cwd)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    payload: dict = {
        "step": step_name,
        "command": command,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "ok": result.returncode == 0,
    }
    if stdout:
        try:
            payload["data"] = json.loads(stdout)
        except json.JSONDecodeError:
            payload["data"] = None
            payload["parse_error"] = "stdout was not valid JSON"
    else:
        payload["data"] = None
    return payload


def require_git_root(root: Path, git: str) -> None:
    result = run([git, "rev-parse", "--is-inside-work-tree"], cwd=root)
    if result.returncode != 0 or result.stdout.strip().lower() != "true":
        raise SystemExit("OpenSpec guard cannot require a clean git tree because this root is not inside a git work tree.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository OpenSpec guard sequence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--tool", default="codex", help="OpenSpec AI tool integration to validate.")
    parser.add_argument("--refresh-managed-files", action="store_true", help="Re-run `openspec init --tools <tool> --force` and `openspec update --force` before verification.")
    parser.add_argument("--require-clean-git", action="store_true", help="Fail if the repository is dirty after the guard finishes.")
    parser.add_argument("--skip-validate", action="store_true", help="Pass `--skip-validate` to verify_official_openspec.py.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable aggregated JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")

    python_exe = Path(sys.executable)
    verify_script = root / "tools" / "verify_official_openspec.py"
    repo_language_script = root / "tools" / "check_current_repo_authority_language.py"
    governance_rules_script = root / "tools" / "check_document_governance_rules.py"
    implementation_plan_rules_script = root / "tools" / "check_implementation_plan_rules.py"
    skills_governance_script = root / "tools" / "check_codex_skills_governance.py"
    name_clarity_rules_script = root / "tools" / "check_name_clarity_rules.py"
    canary_surface_script = root / "tools" / "check_context_retention_canary_surface.py"
    safety_rule_script_backing_script = root / "tools" / "check_safety_rule_script_backing.py"
    precommit_update_archive_script = root / "tools" / "check_precommit_update_archive.py"
    skills_audit_output_retention_script = root / "tools" / "check_skills_audit_output_retention.py"
    openspec_code_archive_evidence_script = root / "tools" / "check_openspec_code_archive_evidence.py"
    mcp_router_scope_policy_script = root / "tools" / "check_mcp_router_scope_policy.py"
    local_mirrored_ci_gate_script = root / "tools" / "check_local_mirrored_ci_gate.py"
    remote_publication_approval_policy_script = root / "tools" / "check_remote_publication_approval_policy.py"
    role_routing_directive_evidence_script = root / "tools" / "check_role_routing_directive_evidence.py"
    delegation_wait_discipline_evidence_script = root / "tools" / "check_delegation_wait_discipline_evidence.py"
    durable_artifact_state_surfaces_script = root / "tools" / "check_durable_artifact_state_surfaces.py"
    leader_session_scope_evidence_script = root / "tools" / "check_leader_session_scope_evidence.py"
    capability_switch_chain_script = root / "tools" / "check_capability_switch_chain.py"
    windows_cleanup_output_control_script = root / "tools" / "check_windows_cleanup_output_control.py"
    plugin_modules_skill_script = root / "tools" / "check_plugin_modules_skill.py"
    pyside6_gui_template_contract_script = root / "tools" / "check_pyside6_gui_template_contract.py"
    pyside6_gui_preview_helper_contract_script = root / "tools" / "check_pyside6_gui_preview_helper_contract.py"
    pyside6_gui_skill_contract_script = root / "tools" / "check_pyside6_gui_skill_contract.py"
    pyside6_project_opt_in_contract_script = root / "tools" / "check_pyside6_project_opt_in_contract.py"
    pyside6_packaging_opt_in_contract_script = root / "tools" / "check_pyside6_packaging_opt_in_contract.py"
    durable_routing_smoke_gate_template_script = root / "tools" / "check_durable_routing_smoke_gate_template.py"
    codex_native_rollback_release_gate_template_script = root / "tools" / "check_codex_native_rollback_release_gate_template.py"
    worktree_hygiene_script = root / "tools" / "check_worktree_session_hygiene.py"
    worktree_task_receipt_script = root / "tools" / "check_worktree_task_receipt.py"
    session_ownership_claims_script = root / "tools" / "check_session_ownership_claims.py"
    orchestration_activation_policy_script = root / "tools" / "check_orchestration_activation_policy.py"
    custom_agent_toml_schema_script = root / "tools" / "check_custom_agent_toml_schema.py"
    agent_skill_profile_surface_boundaries_script = root / "tools" / "check_agent_skill_profile_surface_boundaries.py"
    effective_lane_fit_evidence_script = root / "tools" / "check_effective_lane_fit_evidence.py"
    fanout_write_ownership_evidence_script = root / "tools" / "check_fanout_write_ownership_evidence.py"

    if not verify_script.exists():
        raise SystemExit(f"Missing verification script: {verify_script}")
    if not repo_language_script.exists():
        raise SystemExit(f"Missing repository wording check script: {repo_language_script}")
    if not governance_rules_script.exists():
        raise SystemExit(f"Missing document governance check script: {governance_rules_script}")
    if not implementation_plan_rules_script.exists():
        raise SystemExit(f"Missing implementation plan rules check script: {implementation_plan_rules_script}")
    if not skills_governance_script.exists():
        raise SystemExit(f"Missing Codex skills governance check script: {skills_governance_script}")
    if not name_clarity_rules_script.exists():
        raise SystemExit(f"Missing name clarity rules check script: {name_clarity_rules_script}")
    if not canary_surface_script.exists():
        raise SystemExit(f"Missing context-retention canary surface check script: {canary_surface_script}")
    if not safety_rule_script_backing_script.exists():
        raise SystemExit(f"Missing safety rule script-backing check script: {safety_rule_script_backing_script}")
    if not precommit_update_archive_script.exists():
        raise SystemExit(f"Missing pre-commit update/archive check script: {precommit_update_archive_script}")
    if not skills_audit_output_retention_script.exists():
        raise SystemExit(f"Missing Skills audit output retention check script: {skills_audit_output_retention_script}")
    if not openspec_code_archive_evidence_script.exists():
        raise SystemExit(f"Missing OpenSpec code archive evidence check script: {openspec_code_archive_evidence_script}")
    if not mcp_router_scope_policy_script.exists():
        raise SystemExit(f"Missing MCP Router scope policy check script: {mcp_router_scope_policy_script}")
    if not local_mirrored_ci_gate_script.exists():
        raise SystemExit(f"Missing local mirrored CI/MR gate check script: {local_mirrored_ci_gate_script}")
    if not remote_publication_approval_policy_script.exists():
        raise SystemExit(f"Missing remote publication approval policy check script: {remote_publication_approval_policy_script}")
    if not role_routing_directive_evidence_script.exists():
        raise SystemExit(f"Missing role/directive evidence check script: {role_routing_directive_evidence_script}")
    if not delegation_wait_discipline_evidence_script.exists():
        raise SystemExit(f"Missing delegation/wait discipline evidence check script: {delegation_wait_discipline_evidence_script}")
    if not durable_artifact_state_surfaces_script.exists():
        raise SystemExit(f"Missing durable artifact/state-surface evidence check script: {durable_artifact_state_surfaces_script}")
    if not leader_session_scope_evidence_script.exists():
        raise SystemExit(f"Missing leader/session scope evidence check script: {leader_session_scope_evidence_script}")
    if not capability_switch_chain_script.exists():
        raise SystemExit(f"Missing capability-switch chain check script: {capability_switch_chain_script}")
    if not windows_cleanup_output_control_script.exists():
        raise SystemExit(f"Missing Windows cleanup-output control check script: {windows_cleanup_output_control_script}")
    if not plugin_modules_skill_script.exists():
        raise SystemExit(f"Missing plugin-modules skill check script: {plugin_modules_skill_script}")
    if not pyside6_project_opt_in_contract_script.exists():
        raise SystemExit(f"Missing PySide6 project opt-in contract check script: {pyside6_project_opt_in_contract_script}")
    if not pyside6_packaging_opt_in_contract_script.exists():
        raise SystemExit(f"Missing PySide6 packaging opt-in contract check script: {pyside6_packaging_opt_in_contract_script}")
    if not durable_routing_smoke_gate_template_script.exists():
        raise SystemExit(f"Missing durable routing smoke gate template check script: {durable_routing_smoke_gate_template_script}")
    if not codex_native_rollback_release_gate_template_script.exists():
        raise SystemExit(f"Missing Codex native rollback release gate template check script: {codex_native_rollback_release_gate_template_script}")
    if not worktree_hygiene_script.exists():
        raise SystemExit(f"Missing worktree session hygiene check script: {worktree_hygiene_script}")
    if not worktree_task_receipt_script.exists():
        raise SystemExit(f"Missing worktree task receipt check script: {worktree_task_receipt_script}")
    if not session_ownership_claims_script.exists():
        raise SystemExit(f"Missing session ownership claims check script: {session_ownership_claims_script}")
    if not orchestration_activation_policy_script.exists():
        raise SystemExit(f"Missing orchestration activation policy check script: {orchestration_activation_policy_script}")
    if not custom_agent_toml_schema_script.exists():
        raise SystemExit(f"Missing custom agent TOML schema check script: {custom_agent_toml_schema_script}")
    if not agent_skill_profile_surface_boundaries_script.exists():
        raise SystemExit(f"Missing agent/skill/profile surface boundary check script: {agent_skill_profile_surface_boundaries_script}")
    if not effective_lane_fit_evidence_script.exists():
        raise SystemExit(f"Missing effective lane-fit evidence check script: {effective_lane_fit_evidence_script}")
    if not fanout_write_ownership_evidence_script.exists():
        raise SystemExit(f"Missing fan-out/write-ownership evidence check script: {fanout_write_ownership_evidence_script}")

    openspec = shutil.which("openspec") or shutil.which("openspec.cmd")
    if args.json:
        payload: dict = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "check_name": "run_openspec_guard",
            "ok": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "counts": {
                "steps_total": 0,
                "steps_passed": 0,
                "steps_failed": 0,
            },
            "root": str(root),
            "tool": args.tool,
            "refresh_managed_files": bool(args.refresh_managed_files),
            "require_clean_git": bool(args.require_clean_git),
            "skip_validate": bool(args.skip_validate),
            "steps": [],
        }

        if args.refresh_managed_files:
            if not openspec:
                payload["ok"] = False
                payload["failed_step"] = "refresh_managed_files"
                payload["error"] = "OpenSpec guard cannot refresh managed files because `openspec` is not in PATH."
                payload["errors"].append(payload["error"])
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1

            for step_name, command in [
                ("openspec_init", [openspec, "init", "--tools", args.tool, "--force"]),
                ("openspec_update", [openspec, "update", "--force"]),
            ]:
                step_payload = run_json_command(command, cwd=root, step_name=step_name)
                payload["steps"].append(step_payload)
                payload["counts"]["steps_total"] += 1
                if not step_payload["ok"]:
                    payload["ok"] = False
                    payload["counts"]["steps_failed"] += 1
                    payload["failed_step"] = step_name
                    payload["error"] = (
                        "OpenSpec guard failed while refreshing the official tool integration."
                        if step_name == "openspec_init"
                        else "OpenSpec guard failed while updating official OpenSpec instruction files."
                    )
                    payload["errors"].append(payload["error"])
                    print(json.dumps(payload, ensure_ascii=False, indent=2))
                    return 1
                payload["counts"]["steps_passed"] += 1

        verify_command = [str(python_exe), str(verify_script), "--root", str(root), "--tool", args.tool, "--json"]
        if args.skip_validate:
            verify_command.append("--skip-validate")
        for step_name, command, error_message in [
            ("verify_official_openspec", verify_command, "OpenSpec guard failed during official OpenSpec verification."),
            (
                "check_current_repo_authority_language",
                [str(python_exe), str(repo_language_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during current-repository authority wording verification.",
            ),
            (
                "check_document_governance_rules",
                [str(python_exe), str(governance_rules_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during document governance rules verification.",
            ),
            (
                "check_implementation_plan_rules",
                [str(python_exe), str(implementation_plan_rules_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during implementation plan rules verification.",
            ),
            (
                "check_name_clarity_rules",
                [str(python_exe), str(name_clarity_rules_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during name clarity rules verification.",
            ),
            (
                "check_context_retention_canary_surface",
                [str(python_exe), str(canary_surface_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during context-retention canary surface verification.",
            ),
            (
                "check_safety_rule_script_backing",
                [str(python_exe), str(safety_rule_script_backing_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during safety rule script-backing verification.",
            ),
            (
                "check_precommit_update_archive",
                [str(python_exe), str(precommit_update_archive_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during pre-commit update/archive verification.",
            ),
            (
                "check_skills_audit_output_retention",
                [str(python_exe), str(skills_audit_output_retention_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during Skills audit output retention verification.",
            ),
            (
                "check_openspec_code_archive_evidence",
                [str(python_exe), str(openspec_code_archive_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during OpenSpec code archive evidence verification.",
            ),
            (
                "check_mcp_router_scope_policy",
                [str(python_exe), str(mcp_router_scope_policy_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during MCP Router scope policy verification.",
            ),
            (
                "check_local_mirrored_ci_gate",
                [str(python_exe), str(local_mirrored_ci_gate_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during local mirrored CI/MR gate verification.",
            ),
            (
                "check_remote_publication_approval_policy",
                [str(python_exe), str(remote_publication_approval_policy_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during remote publication approval policy verification.",
            ),
            (
                "check_role_routing_directive_evidence",
                [str(python_exe), str(role_routing_directive_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during role/directive evidence verification.",
            ),
            (
                "check_delegation_wait_discipline_evidence",
                [str(python_exe), str(delegation_wait_discipline_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during delegation/wait discipline evidence verification.",
            ),
            (
                "check_durable_artifact_state_surfaces",
                [str(python_exe), str(durable_artifact_state_surfaces_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during durable artifact/state-surface evidence verification.",
            ),
            (
                "check_leader_session_scope_evidence",
                [str(python_exe), str(leader_session_scope_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during leader/session scope evidence verification.",
            ),
            (
                "check_capability_switch_chain",
                [str(python_exe), str(capability_switch_chain_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during capability-switch chain verification.",
            ),
            (
                "check_windows_cleanup_output_control",
                [str(python_exe), str(windows_cleanup_output_control_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during Windows cleanup-output control verification.",
            ),
            (
                "check_plugin_modules_skill",
                [str(python_exe), str(plugin_modules_skill_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during plugin-modules skill verification.",
            ),
            (
                "check_pyside6_gui_template_contract",
                [str(python_exe), str(pyside6_gui_template_contract_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during PySide6 GUI template contract verification.",
            ),
            (
                "check_pyside6_gui_preview_helper_contract",
                [str(python_exe), str(pyside6_gui_preview_helper_contract_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during PySide6 GUI preview helper contract verification.",
            ),
            (
                "check_pyside6_gui_skill_contract",
                [str(python_exe), str(pyside6_gui_skill_contract_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during PySide6 GUI skill contract verification.",
            ),
            (
                "check_pyside6_project_opt_in_contract",
                [str(python_exe), str(pyside6_project_opt_in_contract_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during PySide6 consumer-project opt-in contract verification.",
            ),
            (
                "check_pyside6_packaging_opt_in_contract",
                [str(python_exe), str(pyside6_packaging_opt_in_contract_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during PySide6 packaging opt-in contract verification.",
            ),
            (
                "check_durable_routing_smoke_gate_template",
                [str(python_exe), str(durable_routing_smoke_gate_template_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during durable routing smoke gate template verification.",
            ),
            (
                "check_codex_native_rollback_release_gate_template",
                [str(python_exe), str(codex_native_rollback_release_gate_template_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during Codex native rollback release gate template verification.",
            ),
            (
                "check_worktree_session_hygiene",
                [str(python_exe), str(worktree_hygiene_script), "--root", str(root), "--allow-current-dirty", "--json"],
                "OpenSpec guard failed during multi-session worktree hygiene verification.",
            ),
            (
                "check_worktree_task_receipt",
                [str(python_exe), str(worktree_task_receipt_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during worktree task receipt verification.",
            ),
            (
                "check_session_ownership_claims",
                [str(python_exe), str(session_ownership_claims_script), "--root", str(root), "--allow-current-dirty", "--json"],
                "OpenSpec guard failed during session ownership claim verification.",
            ),
            (
                "check_orchestration_activation_policy",
                [str(python_exe), str(orchestration_activation_policy_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during orchestration activation policy verification.",
            ),
            (
                "check_codex_skills_governance",
                [str(python_exe), str(skills_governance_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during Codex skills governance verification.",
            ),
            (
                "check_custom_agent_toml_schema",
                [str(python_exe), str(custom_agent_toml_schema_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during custom agent TOML schema verification.",
            ),
            (
                "check_agent_skill_profile_surface_boundaries",
                [str(python_exe), str(agent_skill_profile_surface_boundaries_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during agent/skill/profile surface boundary verification.",
            ),
            (
                "check_effective_lane_fit_evidence",
                [str(python_exe), str(effective_lane_fit_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during effective lane-fit evidence verification.",
            ),
            (
                "check_fanout_write_ownership_evidence",
                [str(python_exe), str(fanout_write_ownership_evidence_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during fan-out/write-ownership evidence verification.",
            ),
        ]:
            step_payload = run_json_command(command, cwd=root, step_name=step_name)
            payload["steps"].append(step_payload)
            payload["counts"]["steps_total"] += 1
            if not step_payload["ok"]:
                payload["ok"] = False
                payload["counts"]["steps_failed"] += 1
                payload["failed_step"] = step_name
                payload["error"] = error_message
                payload["errors"].append(error_message)
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            payload["counts"]["steps_passed"] += 1

        if args.require_clean_git:
            git = shutil.which("git") or shutil.which("git.exe")
            if not git:
                payload["ok"] = False
                payload["failed_step"] = "git_clean_check"
                payload["error"] = "OpenSpec guard cannot check working tree cleanliness because `git` is not in PATH."
                payload["errors"].append(payload["error"])
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1

            git_root_check = run([git, "rev-parse", "--is-inside-work-tree"], cwd=root)
            git_root_payload = {
                "step": "git_root_check",
                "command": [git, "rev-parse", "--is-inside-work-tree"],
                "returncode": git_root_check.returncode,
                "stdout": git_root_check.stdout.strip(),
                "stderr": git_root_check.stderr.strip(),
                "ok": git_root_check.returncode == 0 and git_root_check.stdout.strip().lower() == "true",
            }
            payload["steps"].append(git_root_payload)
            payload["counts"]["steps_total"] += 1
            if not git_root_payload["ok"]:
                payload["ok"] = False
                payload["counts"]["steps_failed"] += 1
                payload["failed_step"] = "git_root_check"
                payload["error"] = "OpenSpec guard cannot require a clean git tree because this root is not inside a git work tree."
                payload["errors"].append(payload["error"])
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            payload["counts"]["steps_passed"] += 1

            status = run([git, "status", "--porcelain", "--untracked-files=all"], cwd=root)
            dirty_lines = [line for line in status.stdout.splitlines() if line.strip()]
            status_payload = {
                "step": "git_clean_check",
                "command": [git, "status", "--porcelain", "--untracked-files=all"],
                "returncode": status.returncode,
                "stdout": status.stdout.strip(),
                "stderr": status.stderr.strip(),
                "dirty_lines": dirty_lines,
                "ok": status.returncode == 0 and not dirty_lines,
            }
            payload["steps"].append(status_payload)
            payload["counts"]["steps_total"] += 1
            if not status_payload["ok"]:
                payload["ok"] = False
                payload["counts"]["steps_failed"] += 1
                payload["failed_step"] = "git_clean_check"
                payload["error"] = (
                    "OpenSpec guard failed while checking git status."
                    if status.returncode != 0
                    else "OpenSpec guard detected uncommitted drift after refresh. Commit the refreshed managed files before continuing."
                )
                payload["errors"].append(payload["error"])
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 1
            payload["counts"]["steps_passed"] += 1

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.refresh_managed_files:
        if not openspec:
            raise SystemExit("OpenSpec guard cannot refresh managed files because `openspec` is not in PATH.")

        run_checked(
            [openspec, "init", "--tools", args.tool, "--force"],
            cwd=root,
            failure_message="OpenSpec guard failed while refreshing the official tool integration.",
        )
        run_checked(
            [openspec, "update", "--force"],
            cwd=root,
            failure_message="OpenSpec guard failed while updating official OpenSpec instruction files.",
        )

    verify_command = [str(python_exe), str(verify_script), "--root", str(root), "--tool", args.tool]
    if args.skip_validate:
        verify_command.append("--skip-validate")
    run_checked(
        verify_command,
        cwd=root,
        failure_message="OpenSpec guard failed during official OpenSpec verification.",
    )

    run_checked(
        [str(python_exe), str(repo_language_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during current-repository authority wording verification.",
    )

    run_checked(
        [str(python_exe), str(governance_rules_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during document governance rules verification.",
    )

    run_checked(
        [str(python_exe), str(implementation_plan_rules_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during implementation plan rules verification.",
    )

    run_checked(
        [str(python_exe), str(name_clarity_rules_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during name clarity rules verification.",
    )

    run_checked(
        [str(python_exe), str(canary_surface_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during context-retention canary surface verification.",
    )

    run_checked(
        [str(python_exe), str(safety_rule_script_backing_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during safety rule script-backing verification.",
    )
    run_checked(
        [str(python_exe), str(precommit_update_archive_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during pre-commit update/archive verification.",
    )
    run_checked(
        [str(python_exe), str(skills_audit_output_retention_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during Skills audit output retention verification.",
    )
    run_checked(
        [str(python_exe), str(openspec_code_archive_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during OpenSpec code archive evidence verification.",
    )
    run_checked(
        [str(python_exe), str(mcp_router_scope_policy_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during MCP Router scope policy verification.",
    )
    run_checked(
        [str(python_exe), str(local_mirrored_ci_gate_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during local mirrored CI/MR gate verification.",
    )
    run_checked(
        [str(python_exe), str(remote_publication_approval_policy_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during remote publication approval policy verification.",
    )
    run_checked(
        [str(python_exe), str(role_routing_directive_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during role/directive evidence verification.",
    )
    run_checked(
        [str(python_exe), str(delegation_wait_discipline_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during delegation/wait discipline evidence verification.",
    )
    run_checked(
        [str(python_exe), str(durable_artifact_state_surfaces_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during durable artifact/state-surface evidence verification.",
    )

    run_checked(
        [str(python_exe), str(leader_session_scope_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during leader/session scope evidence verification.",
    )

    run_checked(
        [str(python_exe), str(windows_cleanup_output_control_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during Windows cleanup-output control verification.",
    )

    run_checked(
        [str(python_exe), str(plugin_modules_skill_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during plugin-modules skill verification.",
    )

    run_checked(
        [str(python_exe), str(pyside6_gui_template_contract_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during PySide6 GUI template contract verification.",
    )

    run_checked(
        [str(python_exe), str(pyside6_gui_preview_helper_contract_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during PySide6 GUI preview helper contract verification.",
    )

    run_checked(
        [str(python_exe), str(pyside6_gui_skill_contract_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during PySide6 GUI skill contract verification.",
    )

    run_checked(
        [str(python_exe), str(pyside6_project_opt_in_contract_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during PySide6 consumer-project opt-in contract verification.",
    )

    run_checked(
        [str(python_exe), str(pyside6_packaging_opt_in_contract_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during PySide6 packaging opt-in contract verification.",
    )

    run_checked(
        [str(python_exe), str(durable_routing_smoke_gate_template_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during durable routing smoke gate template verification.",
    )

    run_checked(
        [str(python_exe), str(codex_native_rollback_release_gate_template_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during Codex native rollback release gate template verification.",
    )

    run_checked(
        [str(python_exe), str(worktree_hygiene_script), "--root", str(root), "--allow-current-dirty"],
        cwd=root,
        failure_message="OpenSpec guard failed during multi-session worktree hygiene verification.",
    )

    run_checked(
        [str(python_exe), str(worktree_task_receipt_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during worktree task receipt verification.",
    )

    run_checked(
        [str(python_exe), str(session_ownership_claims_script), "--root", str(root), "--allow-current-dirty"],
        cwd=root,
        failure_message="OpenSpec guard failed during session ownership claim verification.",
    )

    run_checked(
        [str(python_exe), str(orchestration_activation_policy_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during orchestration activation policy verification.",
    )

    run_checked(
        [str(python_exe), str(skills_governance_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during Codex skills governance verification.",
    )

    run_checked(
        [str(python_exe), str(custom_agent_toml_schema_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during custom agent TOML schema verification.",
    )

    run_checked(
        [str(python_exe), str(agent_skill_profile_surface_boundaries_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during agent/skill/profile surface boundary verification.",
    )

    run_checked(
        [str(python_exe), str(effective_lane_fit_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during effective lane-fit evidence verification.",
    )

    run_checked(
        [str(python_exe), str(fanout_write_ownership_evidence_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during fan-out/write-ownership evidence verification.",
    )

    if args.require_clean_git:
        git = shutil.which("git") or shutil.which("git.exe")
        if not git:
            raise SystemExit("OpenSpec guard cannot check working tree cleanliness because `git` is not in PATH.")

        require_git_root(root, git)
        status = run([git, "status", "--porcelain", "--untracked-files=all"], cwd=root)
        print_output(status)
        dirty_lines = [line for line in status.stdout.splitlines() if line.strip()]
        if status.returncode != 0:
            raise SystemExit("OpenSpec guard failed while checking git status.")
        if dirty_lines:
            raise SystemExit(
                "OpenSpec guard detected uncommitted drift after refresh. Commit the refreshed managed files before continuing."
            )

    print("OpenSpec guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
