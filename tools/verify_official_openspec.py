#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_CODEX_SKILLS = [
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-continue-change",
    "openspec-explore",
    "openspec-ff-change",
    "openspec-new-change",
    "openspec-onboard",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-verify-change",
]

SUPPORTED_CI_GUARDS = [
    ".github/workflows/openspec-guard.yml",
    ".gitlab-ci.yml",
]


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


def print_block(title: str, lines: list[str]) -> None:
    print(title)
    for line in lines:
        print(f"  - {line}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require_text(text: str, needle: str, error_message: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(error_message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the repository keeps its official OpenSpec enforcement surfaces.")
    parser.add_argument("--root", default=".", help="Repository root to verify.")
    parser.add_argument("--tool", default="codex", help="Primary AI tool expected for this repository.")
    parser.add_argument("--skip-validate", action="store_true", help="Skip `openspec validate --all`.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []

    if not root.exists():
        errors.append(f"Repository root does not exist: {root}")
        print_block("Errors", errors)
        return 1

    required_paths = [
        root / "AGENTS.md",
        root / "openspec" / "config.yaml",
        root / "openspec" / "changes",
        root / "openspec" / "specs",
        root / "docs_bilingual" / "project_startup_summary.md",
        root / "docs_bilingual" / "project_startup_summary.zh-CN.md",
        root / "docs_bilingual" / "docs_registry.yaml",
        root / "docs_bilingual" / "governance" / "openspec_usage_convention.md",
        root / "docs_bilingual" / "governance" / "openspec_usage_convention.zh-CN.md",
        root / "docs_bilingual" / "governance" / "openspec_opsx_project_usage_policy.md",
        root / "docs_bilingual" / "governance" / "openspec_opsx_project_usage_policy.zh-CN.md",
        root / "docs_bilingual" / "governance" / "openspec_official_workflow_policy.md",
        root / "docs_bilingual" / "governance" / "openspec_official_workflow_policy.zh-CN.md",
        root / "tools" / "bootstrap-official-openspec.ps1",
        root / "tools" / "run_openspec_guard.py",
        root / "tools" / "verify_official_openspec.py",
        root / "tools" / "check_current_repo_authority_language.py",
        root / "tools" / "current_repo_authority_language_rules.json",
        root / "tools" / "check_document_governance_rules.py",
        root / "tools" / "check_implementation_plan_rules.py",
        root / "tools" / "install-git-hooks.ps1",
        root / ".githooks" / "pre-commit",
    ]

    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing required path: {path}")

    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if registry_path.exists():
        registry_text = read_text(registry_path)
        for required_doc in [
            "doc_id: project_startup_summary",
            "doc_id: openspec_usage_convention",
            "doc_id: openspec_opsx_project_usage_policy",
            "doc_id: openspec_official_workflow_policy",
        ]:
            require_text(
                registry_text,
                required_doc,
                f"docs_registry.yaml is missing `{required_doc}`.",
                errors,
            )

    startup_summary_paths = [
        root / "docs_bilingual" / "project_startup_summary.md",
        root / "docs_bilingual" / "project_startup_summary.zh-CN.md",
    ]
    for summary_path in startup_summary_paths:
        if summary_path.exists():
            summary_text = read_text(summary_path)
            for required_reference in [
                "openspec_usage_convention",
                "openspec_opsx_project_usage_policy",
                "openspec_official_workflow_policy",
                "AGENTS.md",
            ]:
                require_text(
                    summary_text,
                    required_reference,
                    f"{summary_path} does not reference `{required_reference}`.",
                    errors,
                )

    agents_path = root / "AGENTS.md"
    if agents_path.exists():
        agents_text = read_text(agents_path)
        for required_reference in [
            "docs_bilingual/project_startup_summary.zh-CN.md",
            "docs_bilingual/project_startup_summary.md",
            "openspec_official_workflow_policy",
            "run_openspec_guard.py",
            "verify_official_openspec.py",
        ]:
            require_text(
                agents_text,
                required_reference,
                f"AGENTS.md does not reference `{required_reference}`.",
                errors,
            )

    usage_path = root / "docs_bilingual" / "governance" / "openspec_usage_convention.md"
    if usage_path.exists():
        usage_text = read_text(usage_path)
        require_text(
            usage_text,
            "openspec_official_workflow_policy.md",
            "openspec_usage_convention.md does not reference `openspec_official_workflow_policy.md`.",
            errors,
        )

    usage_zh_path = root / "docs_bilingual" / "governance" / "openspec_usage_convention.zh-CN.md"
    if usage_zh_path.exists():
        usage_zh_text = read_text(usage_zh_path)
        require_text(
            usage_zh_text,
            "openspec_official_workflow_policy.zh-CN.md",
            "openspec_usage_convention.zh-CN.md does not reference `openspec_official_workflow_policy.zh-CN.md`.",
            errors,
        )

    config_path = root / "openspec" / "config.yaml"
    if config_path.exists():
        config_text = read_text(config_path)
        for required_reference in [
            "project_startup_summary.md",
            "openspec_usage_convention.md",
            "openspec_official_workflow_policy.md",
            "run_openspec_guard.py",
            "verify_official_openspec.py",
            "check_current_repo_authority_language.py",
            "current_repo_authority_language_rules.json",
            "check_document_governance_rules.py",
            "check_implementation_plan_rules.py",
        ]:
            require_text(
                config_text,
                required_reference,
                f"openspec/config.yaml does not reference `{required_reference}`.",
                errors,
            )

    hook_path = root / ".githooks" / "pre-commit"
    if hook_path.exists():
        hook_text = read_text(hook_path)
        require_text(
            hook_text,
            "tools/run_openspec_guard.py",
            ".githooks/pre-commit does not invoke `tools/run_openspec_guard.py`.",
            errors,
        )

    openspec = shutil.which("openspec") or shutil.which("openspec.cmd")
    if not openspec:
        errors.append("OpenSpec CLI was not found in PATH. Install the official package with `npm install -g @fission-ai/openspec@latest`.")
    else:
        version_result = run([openspec, "--version"], cwd=root)
        if version_result.returncode != 0:
            errors.append("`openspec --version` failed.")
        else:
            infos.append(f"OpenSpec CLI version: {version_result.stdout.strip()}")

    tool = args.tool.strip().lower()
    codex_skills_root = root / ".codex" / "skills"
    agents_stub = root / "openspec" / "AGENTS.md"

    if tool == "codex":
        if codex_skills_root.exists():
            missing_skills = [
                name for name in EXPECTED_CODEX_SKILLS if not (codex_skills_root / name / "SKILL.md").exists()
            ]
            if missing_skills:
                errors.append("Missing expected Codex OpenSpec skills: " + ", ".join(missing_skills))
            else:
                infos.append("Detected official Codex OpenSpec skills under .codex/skills/.")
        elif agents_stub.exists():
            warnings.append("Codex-specific skills were not found, but openspec/AGENTS.md exists. Verify that the active CLI/tool integration is the intended one.")
        else:
            errors.append("No official OpenSpec instruction surface was found for Codex. Run tools/bootstrap-official-openspec.ps1.")
    else:
        if not codex_skills_root.exists() and not agents_stub.exists():
            errors.append(
                "No repository-local official OpenSpec instruction surface was found. "
                "Run tools/bootstrap-official-openspec.ps1 or re-run openspec init for the intended AI tool."
            )

    present_ci_guards = [relative for relative in SUPPORTED_CI_GUARDS if (root / relative).exists()]
    if not present_ci_guards:
        errors.append(
            "No supported CI guard surface was found. Expected at least one of: "
            + ", ".join(SUPPORTED_CI_GUARDS)
        )
    else:
        infos.append("Detected CI guard surfaces: " + ", ".join(present_ci_guards))
        for relative in present_ci_guards:
            ci_text = read_text(root / relative)
            require_text(
                ci_text,
                "tools/run_openspec_guard.py",
                f"{relative} does not invoke `tools/run_openspec_guard.py`.",
                errors,
            )
            require_text(
                ci_text,
                "openspec-guard-report.json",
                f"{relative} does not persist the OpenSpec guard JSON report artifact.",
                errors,
            )
            if relative == ".github/workflows/openspec-guard.yml":
                require_text(
                    ci_text,
                    "upload-artifact",
                    ".github/workflows/openspec-guard.yml does not upload the OpenSpec guard JSON artifact.",
                    errors,
                )
            if relative == ".gitlab-ci.yml":
                require_text(
                    ci_text,
                    "artifacts:",
                    ".gitlab-ci.yml does not publish the OpenSpec guard JSON artifact.",
                    errors,
                )

    guard_script_path = root / "tools" / "run_openspec_guard.py"
    if guard_script_path.exists():
        guard_script_text = read_text(guard_script_path)
        require_text(
            guard_script_text,
            "check_current_repo_authority_language.py",
            "tools/run_openspec_guard.py does not invoke `check_current_repo_authority_language.py`.",
            errors,
        )
        require_text(
            guard_script_text,
            "check_document_governance_rules.py",
            "tools/run_openspec_guard.py does not invoke `check_document_governance_rules.py`.",
            errors,
        )
        require_text(
            guard_script_text,
            "check_implementation_plan_rules.py",
            "tools/run_openspec_guard.py does not invoke `check_implementation_plan_rules.py`.",
            errors,
        )

    if openspec and not args.skip_validate:
        validate_result = run([openspec, "validate", "--all"], cwd=root)
        if validate_result.returncode != 0:
            errors.append("`openspec validate --all` failed.")
            output = (validate_result.stdout + "\n" + validate_result.stderr).strip()
            if output:
                warnings.append("Validation output:\n" + output)
        else:
            infos.append("`openspec validate --all` passed.")

    if infos:
        pass
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "verify_official_openspec",
        "ok": len(errors) == 0,
        "info": infos,
        "warnings": warnings,
        "errors": errors,
        "root": str(root),
        "counts": {
            "info": len(infos),
            "warnings": len(warnings),
            "errors": len(errors),
        },
        "tool": tool,
        "skip_validate": bool(args.skip_validate),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if infos:
        print_block("Info", infos)
    if warnings:
        print_block("Warnings", warnings)
    if errors:
        print_block("Errors", errors)
        return 1

    print("Official OpenSpec verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
