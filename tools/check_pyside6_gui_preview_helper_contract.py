#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "pyside6_gui_preview_helper_contract"
HELPER_PATH = Path("tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1")
REQUIRED_JSON_FIELDS = [
    "project_root",
    "project_root_evidence",
    "python_path",
    "python_version",
    "package_manager",
    "dependency_style",
    "planned_file_changes",
    "applied_file_changes",
    "rollback_note",
    "apply_mode",
    "smoke_test",
    "package_manager_command_evidence",
    "planned_commands",
    "local_only_artifacts",
    "blockers",
    "rollback_steps",
]
REQUIRED_SCRIPT_SNIPPETS = [
    "ProjectRoot",
    "Mode",
    "preview",
    "apply",
    "DependencyStyle",
    "PythonPath",
    "PackageVersion",
    "CreateTemplate",
    "RunSmokeTest",
    "ConvertTo-Json",
    "project_root_evidence",
    "planned_file_changes",
    "applied_file_changes",
    "rollback_note",
    "local_only_artifacts",
    "rollback_steps",
    "Get-ProjectRelativeFullPath",
    "Update-RequirementsGui",
    "Update-PyProjectDependency",
    "Apply-TemplateFiles",
    "Write-RollbackNote",
    "New-PlannedCommand",
    "Get-PackageManagerCommandEvidence",
    "project_native_dependency_command",
    "lockfile_update_command",
    "lockfile_expectation",
]
FORBIDDEN_HELPER_SNIPPETS = [
    "apply_not_implemented",
    "Start-Process",
    "pip install --user",
    "--user",
    "git push",
    "git fetch",
    "git merge",
    "git reset",
    "git clean",
    "Remove-Item",
    "Move-Item",
]
LEGACY_UNGATED_WRITE_SNIPPETS = [
    "New-Item",
    "Set-Content",
    "Out-File",
    "Add-Content",
    "Copy-Item",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_powershell() -> str | None:
    for candidate in ("powershell.exe", "powershell", "pwsh.exe", "pwsh"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    system_ps = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if system_ps.exists():
        return str(system_ps)
    return None


def run_helper(
    repo_root: Path,
    fixture: Path,
    *,
    mode: str = "preview",
    dependency_style: str = "auto",
    package_name: str = "sample_gui",
    create_template: bool = True,
    run_smoke_test: bool = True,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    powershell = find_powershell()
    if not powershell:
        raise RuntimeError("PowerShell executable not found; cannot validate PySide6 GUI helper execution.")
    command = [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(repo_root / HELPER_PATH),
        "-ProjectRoot",
        str(fixture),
        "-Mode",
        mode,
        "-DependencyStyle",
        dependency_style,
        "-PackageName",
        package_name,
    ]
    if create_template:
        command.append("-CreateTemplate")
    if run_smoke_test:
        command.append("-RunSmokeTest")
    command.append("-Json")
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", check=False)


def make_fixture(root: Path, *, name: str, dependency_surface: str) -> Path:
    fixture = root / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
    fixture.mkdir(parents=True, exist_ok=True)
    if dependency_surface == "pyproject":
        (fixture / "pyproject.toml").write_text(
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n",
            encoding="utf-8",
        )
    elif dependency_surface == "uv":
        (fixture / "pyproject.toml").write_text(
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n",
            encoding="utf-8",
        )
        (fixture / "uv.lock").write_text("# fixture lockfile marker\n", encoding="utf-8")
    elif dependency_surface == "poetry":
        (fixture / "pyproject.toml").write_text(
            "[tool.poetry]\nname = \"sample\"\nversion = \"0.1.0\"\ndescription = \"fixture\"\nauthors = []\n",
            encoding="utf-8",
        )
        (fixture / "poetry.lock").write_text("# fixture lockfile marker\n", encoding="utf-8")
    elif dependency_surface == "requirements":
        (fixture / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    elif dependency_surface == "none":
        pass
    else:
        raise ValueError(f"unknown dependency surface: {dependency_surface}")
    if dependency_surface != "none":
        (fixture / "README.md").write_text("# Sample\n", encoding="utf-8")
    return fixture


def snapshot_files(root: Path) -> set[str]:
    return {str(path.relative_to(root)).replace("\\", "/") for path in root.rglob("*") if path.is_file()}


def load_json_stdout(result: subprocess.CompletedProcess[str], errors: list[str], label: str) -> dict[str, Any] | None:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} did not emit valid JSON with -Json: {exc}: {result.stdout!r}")
        return None


def validate_preview_payload(payload: dict[str, Any], errors: list[str]) -> None:
    for field in REQUIRED_JSON_FIELDS:
        if field not in payload:
            errors.append(f"Preview helper JSON missing required field `{field}`.")
    if payload.get("mode") != "preview":
        errors.append("Preview helper JSON must report mode=preview.")
    if payload.get("apply_mode") is not False:
        errors.append("Preview helper JSON must report apply_mode=false.")
    if payload.get("dependency_style") != "pyproject-extra":
        errors.append("Preview helper should detect pyproject fixture as dependency_style=pyproject-extra.")
    planned = payload.get("planned_file_changes") or []
    if not any(isinstance(item, dict) and item.get("path") == "pyproject.toml" for item in planned):
        errors.append("Preview helper did not plan pyproject.toml dependency update for pyproject fixture.")
    if not any(isinstance(item, dict) and item.get("path") == "src/sample_gui/app.py" for item in planned):
        errors.append("Preview helper did not plan sample_gui app template creation when -CreateTemplate is set.")
    if payload.get("applied_file_changes") not in ([], None):
        errors.append("Preview helper must not report applied_file_changes in preview mode.")
    command_evidence = payload.get("package_manager_command_evidence") or {}
    if command_evidence.get("project_package_manager") != "pyproject":
        errors.append("Preview helper should report project_package_manager=pyproject for pyproject fixture command evidence.")
    if command_evidence.get("install_command") != 'python -m pip install -e ".[gui]"':
        errors.append("Preview helper should emit pyproject-extra install guidance for pyproject fixtures.")
    if "lockfile" not in str(command_evidence.get("lockfile_expectation", "")).lower():
        errors.append("Preview helper command evidence must include lockfile expectation text.")
    planned_commands = payload.get("planned_commands") or []
    if not any(isinstance(item, dict) and item.get("affects_lockfile") is True for item in planned_commands):
        errors.append("Preview helper planned_commands must identify the command/guidance that can affect lockfile state.")


def validate_apply_payload(payload: dict[str, Any], fixture: Path, errors: list[str]) -> None:
    for field in REQUIRED_JSON_FIELDS:
        if field not in payload:
            errors.append(f"Apply helper JSON missing required field `{field}`.")
    if payload.get("mode") != "apply":
        errors.append("Apply helper JSON must report mode=apply.")
    if payload.get("apply_mode") is not True:
        errors.append("Apply helper JSON must report apply_mode=true.")
    if not payload.get("ok"):
        errors.append(f"Apply helper reported blockers for a valid requirements fixture: {payload.get('blockers')}")
    expected_paths = [
        "requirements-gui.txt",
        "src/sample_gui/__init__.py",
        "src/sample_gui/app.py",
        "src/sample_gui/main_window.py",
        "tools/gui/check_pyside6_env.py",
        "tools/gui/run_gui.ps1",
        "tests/test_gui_import.py",
        "docs/pyside6_gui_rollback.md",
    ]
    for rel in expected_paths:
        if not (fixture / rel).exists():
            errors.append(f"Apply helper did not create expected project-local file: {rel}")
    requirements = fixture / "requirements-gui.txt"
    if requirements.exists() and "PySide6" not in requirements.read_text(encoding="utf-8"):
        errors.append("requirements-gui.txt does not declare PySide6 after apply.")
    app = fixture / "src" / "sample_gui" / "app.py"
    if app.exists() and "{{" in app.read_text(encoding="utf-8"):
        errors.append("Generated app.py still contains unresolved template placeholders.")
    applied = payload.get("applied_file_changes") or []
    if not any(isinstance(item, dict) and item.get("path") == "requirements-gui.txt" for item in applied):
        errors.append("Apply helper JSON did not report requirements-gui.txt in applied_file_changes.")
    if payload.get("rollback_note") != "docs/pyside6_gui_rollback.md":
        errors.append("Apply helper JSON must report rollback_note=docs/pyside6_gui_rollback.md.")
    command_evidence = payload.get("package_manager_command_evidence") or {}
    if command_evidence.get("project_package_manager") != "pip":
        errors.append("Apply helper should report project_package_manager=pip for requirements fixtures command evidence.")
    if command_evidence.get("install_command") != "python -m pip install -r requirements-gui.txt":
        errors.append("Apply helper should emit requirements-gui install guidance for requirements fixtures.")
    if command_evidence.get("run_smoke_test_requested") is not True:
        errors.append("Apply helper command evidence should preserve whether -RunSmokeTest was requested.")


def validate_fail_closed_payload(payload: dict[str, Any], fixture: Path, errors: list[str]) -> None:
    if payload.get("ok"):
        errors.append("Apply helper should fail closed when project root evidence is missing.")
    blocker_codes = {item.get("code") for item in payload.get("blockers", []) if isinstance(item, dict)}
    if "unsafe_project_root" not in blocker_codes:
        errors.append("Apply helper missing unsafe_project_root blocker for fixture without root evidence.")
    if snapshot_files(fixture):
        errors.append("Fail-closed apply helper wrote files into an unsafe fixture.")


def validate_package_manager_command_payload(
    payload: dict[str, Any],
    errors: list[str],
    *,
    expected_package_manager: str,
    expected_dependency_style: str,
    expected_dependency_command: str,
    expected_install_command: str,
    expected_lockfile_command: str,
) -> None:
    if payload.get("mode") != "preview":
        errors.append(f"{expected_package_manager} command sample must use preview mode.")
    command_evidence = payload.get("package_manager_command_evidence") or {}
    if command_evidence.get("project_package_manager") != expected_package_manager:
        errors.append(f"Expected project_package_manager={expected_package_manager}, got {command_evidence.get('project_package_manager')!r}.")
    if command_evidence.get("dependency_style") != expected_dependency_style:
        errors.append(f"Expected dependency_style={expected_dependency_style}, got {command_evidence.get('dependency_style')!r}.")
    if command_evidence.get("project_native_dependency_command") != expected_dependency_command:
        errors.append(f"Expected dependency command `{expected_dependency_command}`, got {command_evidence.get('project_native_dependency_command')!r}.")
    if command_evidence.get("install_command") != expected_install_command:
        errors.append(f"Expected install command `{expected_install_command}`, got {command_evidence.get('install_command')!r}.")
    if command_evidence.get("lockfile_update_command") != expected_lockfile_command:
        errors.append(f"Expected lockfile command `{expected_lockfile_command}`, got {command_evidence.get('lockfile_update_command')!r}.")


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    helper = root / HELPER_PATH

    if not helper.exists():
        errors.append(f"Missing PySide6 GUI helper: {HELPER_PATH}")
    else:
        text = read_text(helper)
        for snippet in REQUIRED_SCRIPT_SNIPPETS:
            if snippet not in text:
                errors.append(f"{HELPER_PATH} missing required snippet: {snippet}")
        for snippet in FORBIDDEN_HELPER_SNIPPETS + LEGACY_UNGATED_WRITE_SNIPPETS:
            if snippet in text:
                errors.append(f"{HELPER_PATH} contains forbidden global write, launch, or remote-operation snippet: {snippet}")

    preview_payload: dict[str, Any] | None = None
    apply_payload: dict[str, Any] | None = None
    fail_closed_payload: dict[str, Any] | None = None
    uv_payload: dict[str, Any] | None = None
    poetry_payload: dict[str, Any] | None = None
    created_fixtures: list[Path] = []
    if helper.exists() and not errors:
        preview_fixture = make_fixture(root, name="pyside6-preview", dependency_surface="pyproject")
        apply_fixture = make_fixture(root, name="pyside6-apply", dependency_surface="requirements")
        unsafe_fixture = make_fixture(root, name="pyside6-unsafe", dependency_surface="none")
        uv_fixture = make_fixture(root, name="pyside6-uv", dependency_surface="uv")
        poetry_fixture = make_fixture(root, name="pyside6-poetry", dependency_surface="poetry")
        created_fixtures.extend([preview_fixture, apply_fixture, unsafe_fixture, uv_fixture, poetry_fixture])
        before = snapshot_files(preview_fixture)
        try:
            preview_result = run_helper(root, preview_fixture, mode="preview", dependency_style="auto")
            apply_result = run_helper(root, apply_fixture, mode="apply", dependency_style="requirements")
            fail_result = run_helper(root, unsafe_fixture, mode="apply", dependency_style="requirements", create_template=True)
            uv_result = run_helper(root, uv_fixture, mode="preview", dependency_style="auto", create_template=False, run_smoke_test=False)
            poetry_result = run_helper(root, poetry_fixture, mode="preview", dependency_style="auto", create_template=False, run_smoke_test=False)
        except RuntimeError as exc:
            errors.append(str(exc))
        else:
            after = snapshot_files(preview_fixture)
            if before != after:
                errors.append("Preview helper changed fixture files; preview mode must be read-only.")
            if preview_result.returncode != 0:
                errors.append(f"Preview helper returned {preview_result.returncode}: {preview_result.stderr or preview_result.stdout}")
            if apply_result.returncode != 0:
                errors.append(f"Apply helper returned {apply_result.returncode}: {apply_result.stderr or apply_result.stdout}")
            if fail_result.returncode == 0:
                errors.append("Fail-closed apply scenario returned success for unsafe fixture.")
            if uv_result.returncode != 0:
                errors.append(f"uv preview helper returned {uv_result.returncode}: {uv_result.stderr or uv_result.stdout}")
            if poetry_result.returncode != 0:
                errors.append(f"Poetry preview helper returned {poetry_result.returncode}: {poetry_result.stderr or poetry_result.stdout}")
            preview_payload = load_json_stdout(preview_result, errors, "Preview helper")
            apply_payload = load_json_stdout(apply_result, errors, "Apply helper")
            fail_closed_payload = load_json_stdout(fail_result, errors, "Fail-closed apply helper")
            uv_payload = load_json_stdout(uv_result, errors, "uv preview helper")
            poetry_payload = load_json_stdout(poetry_result, errors, "Poetry preview helper")
            if preview_payload:
                if not preview_payload.get("ok"):
                    errors.append(f"Preview helper reported blockers for a valid pyproject fixture: {preview_payload.get('blockers')}")
                validate_preview_payload(preview_payload, errors)
            if apply_payload:
                validate_apply_payload(apply_payload, apply_fixture, errors)
            if fail_closed_payload:
                validate_fail_closed_payload(fail_closed_payload, unsafe_fixture, errors)
            if uv_payload:
                validate_package_manager_command_payload(
                    uv_payload,
                    errors,
                    expected_package_manager="uv",
                    expected_dependency_style="group",
                    expected_dependency_command="uv add --group gui PySide6",
                    expected_install_command="uv sync --group gui",
                    expected_lockfile_command="uv lock",
                )
            if poetry_payload:
                validate_package_manager_command_payload(
                    poetry_payload,
                    errors,
                    expected_package_manager="poetry",
                    expected_dependency_style="pyproject-extra",
                    expected_dependency_command="poetry add --optional PySide6",
                    expected_install_command="poetry install --extras gui",
                    expected_lockfile_command="poetry lock",
                )
        finally:
            for fixture in created_fixtures:
                shutil.rmtree(fixture, ignore_errors=True)

    info.append("PySide6 GUI helper is preview-first and supports explicit project-local apply mode with rollback evidence.")
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "helper": str(helper),
        "preview_sample": preview_payload,
        "apply_sample": apply_payload,
        "fail_closed_sample": fail_closed_payload,
        "uv_sample": uv_payload,
        "poetry_sample": poetry_payload,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_json_fields": len(REQUIRED_JSON_FIELDS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PySide6 GUI preview/apply helper contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 GUI helper contract check passed." if payload["ok"] else "PySide6 GUI helper contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
