#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


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
    openspec_code_archive_evidence_script = root / "tools" / "check_openspec_code_archive_evidence.py"
    mcp_router_scope_policy_script = root / "tools" / "check_mcp_router_scope_policy.py"
    local_mirrored_ci_gate_script = root / "tools" / "check_local_mirrored_ci_gate.py"
    windows_cleanup_output_control_script = root / "tools" / "check_windows_cleanup_output_control.py"
    plugin_modules_skill_script = root / "tools" / "check_plugin_modules_skill.py"
    durable_routing_smoke_gate_template_script = root / "tools" / "check_durable_routing_smoke_gate_template.py"
    codex_native_rollback_release_gate_template_script = root / "tools" / "check_codex_native_rollback_release_gate_template.py"
    worktree_hygiene_script = root / "tools" / "check_worktree_session_hygiene.py"
    session_ownership_claims_script = root / "tools" / "check_session_ownership_claims.py"

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
    if not openspec_code_archive_evidence_script.exists():
        raise SystemExit(f"Missing OpenSpec code archive evidence check script: {openspec_code_archive_evidence_script}")
    if not mcp_router_scope_policy_script.exists():
        raise SystemExit(f"Missing MCP Router scope policy check script: {mcp_router_scope_policy_script}")
    if not local_mirrored_ci_gate_script.exists():
        raise SystemExit(f"Missing local mirrored CI/MR gate check script: {local_mirrored_ci_gate_script}")
    if not windows_cleanup_output_control_script.exists():
        raise SystemExit(f"Missing Windows cleanup-output control check script: {windows_cleanup_output_control_script}")
    if not plugin_modules_skill_script.exists():
        raise SystemExit(f"Missing plugin-modules skill check script: {plugin_modules_skill_script}")
    if not durable_routing_smoke_gate_template_script.exists():
        raise SystemExit(f"Missing durable routing smoke gate template check script: {durable_routing_smoke_gate_template_script}")
    if not codex_native_rollback_release_gate_template_script.exists():
        raise SystemExit(f"Missing Codex native rollback release gate template check script: {codex_native_rollback_release_gate_template_script}")
    if not worktree_hygiene_script.exists():
        raise SystemExit(f"Missing worktree session hygiene check script: {worktree_hygiene_script}")
    if not session_ownership_claims_script.exists():
        raise SystemExit(f"Missing session ownership claims check script: {session_ownership_claims_script}")

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
                "check_session_ownership_claims",
                [str(python_exe), str(session_ownership_claims_script), "--root", str(root), "--allow-current-dirty", "--json"],
                "OpenSpec guard failed during session ownership claim verification.",
            ),
            (
                "check_codex_skills_governance",
                [str(python_exe), str(skills_governance_script), "--root", str(root), "--json"],
                "OpenSpec guard failed during Codex skills governance verification.",
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
        [str(python_exe), str(session_ownership_claims_script), "--root", str(root), "--allow-current-dirty"],
        cwd=root,
        failure_message="OpenSpec guard failed during session ownership claim verification.",
    )

    run_checked(
        [str(python_exe), str(skills_governance_script), "--root", str(root)],
        cwd=root,
        failure_message="OpenSpec guard failed during Codex skills governance verification.",
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
