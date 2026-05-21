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
    "runtime_mode",
    "shared_runtime_root",
    "shared_runtime_python",
    "shared_runtime_status",
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
    "RuntimeMode",
    "shared",
    "project-local-override",
    "RuntimeRoot",
    "DependencyStyle",
    "OverrideReason",
    "CreateTemplate",
    "RunSmokeTest",
    "ConvertTo-Json",
    "project_root_evidence",
    "shared_runtime_status",
    "shared_runtime_missing",
    "pyside6_runtime_contract.json",
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
    runtime_mode: str = "shared",
    runtime_root: Path | None = None,
    dependency_style: str = "auto",
    package_name: str = "sample_gui",
    create_template: bool = True,
    run_smoke_test: bool = True,
    override_reason: str | None = None,
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
        "-RuntimeMode",
        runtime_mode,
        "-DependencyStyle",
        dependency_style,
        "-PackageName",
        package_name,
    ]
    if runtime_root is not None:
        command.extend(["-RuntimeRoot", str(runtime_root)])
    if override_reason:
        command.extend(["-OverrideReason", override_reason])
    if create_template:
        command.append("-CreateTemplate")
    if run_smoke_test:
        command.append("-RunSmokeTest")
    command.append("-Json")
    return subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", check=False)


def make_fixture(root: Path, *, name: str, dependency_surface: str) -> Path:
    fixture = root / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
    fixture.mkdir(parents=True, exist_ok=True)
    if dependency_surface == "pyproject":
        (fixture / "pyproject.toml").write_text("[project]\nname = \"sample\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    elif dependency_surface == "requirements":
        (fixture / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    elif dependency_surface == "none":
        pass
    else:
        raise ValueError(f"unknown dependency surface: {dependency_surface}")
    if dependency_surface != "none":
        (fixture / "README.md").write_text("# Sample\n", encoding="utf-8")
    return fixture


def make_fake_runtime(root: Path, name: str) -> Path:
    runtime = root / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}" / ".shared_runtimes" / "pyside6"
    python = runtime / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text("fake runtime python marker\n", encoding="utf-8")
    (runtime / "runtime.json").write_text(
        json.dumps(
            {
                "runtime_mode": "shared",
                "runtime_root": str(runtime),
                "runtime_python": str(python),
                "import_only_verified": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return runtime


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
    if payload.get("runtime_mode") != "shared":
        errors.append("Preview helper must default runtime_mode=shared.")
    planned = payload.get("planned_file_changes") or []
    if any(isinstance(item, dict) and item.get("path") in {"pyproject.toml", "requirements-gui.txt"} for item in planned):
        errors.append("Shared-runtime preview must not plan project dependency writes.")
    if not any(isinstance(item, dict) and item.get("path") == "tools/gui/pyside6_runtime_contract.json" for item in planned):
        errors.append("Preview helper did not plan shared runtime contract creation.")
    if not any(isinstance(item, dict) and item.get("path") == "src/sample_gui/app.py" for item in planned):
        errors.append("Preview helper did not plan sample_gui app template creation when -CreateTemplate is set.")
    if payload.get("applied_file_changes") not in ([], None):
        errors.append("Preview helper must not report applied_file_changes in preview mode.")
    command_evidence = payload.get("package_manager_command_evidence") or {}
    if command_evidence.get("runtime_mode") != "shared":
        errors.append("Preview helper command evidence must report runtime_mode=shared.")
    if command_evidence.get("install_command") not in ("", None):
        errors.append("Shared-runtime preview must not emit project-local PySide6 install guidance.")
    if "shared runtime" not in str(command_evidence.get("lockfile_expectation", "")).lower():
        errors.append("Shared-runtime command evidence must state no project lockfile mutation.")


def validate_apply_payload(payload: dict[str, Any], fixture: Path, errors: list[str]) -> None:
    for field in REQUIRED_JSON_FIELDS:
        if field not in payload:
            errors.append(f"Apply helper JSON missing required field `{field}`.")
    if payload.get("mode") != "apply":
        errors.append("Apply helper JSON must report mode=apply.")
    if payload.get("apply_mode") is not True:
        errors.append("Apply helper JSON must report apply_mode=true.")
    if not payload.get("ok"):
        errors.append(f"Apply helper reported blockers for a valid shared-runtime fixture: {payload.get('blockers')}")
    expected_paths = [
        "src/sample_gui/__init__.py",
        "src/sample_gui/app.py",
        "src/sample_gui/main_window.py",
        "tools/gui/pyside6_runtime_contract.json",
        "tools/gui/adapters/README.md",
        "tools/gui/check_pyside6_env.py",
        "tools/gui/run_gui.ps1",
        "tests/test_gui_import.py",
        "docs/pyside6_gui_rollback.md",
    ]
    for rel in expected_paths:
        if not (fixture / rel).exists():
            errors.append(f"Apply helper did not create expected project-local shared-runtime file: {rel}")
    if (fixture / "requirements-gui.txt").exists():
        errors.append("Shared-runtime apply must not create requirements-gui.txt.")
    contract = fixture / "tools" / "gui" / "pyside6_runtime_contract.json"
    if contract.exists():
        contract_data = json.loads(contract.read_text(encoding="utf-8"))
        if contract_data.get("runtime_mode") != "shared":
            errors.append("Generated runtime contract must use runtime_mode=shared.")
    applied = payload.get("applied_file_changes") or []
    if not any(isinstance(item, dict) and item.get("path") == "tools/gui/pyside6_runtime_contract.json" for item in applied):
        errors.append("Apply helper JSON did not report runtime contract in applied_file_changes.")
    if payload.get("rollback_note") != "docs/pyside6_gui_rollback.md":
        errors.append("Apply helper JSON must report rollback_note=docs/pyside6_gui_rollback.md.")


def validate_override_payload(payload: dict[str, Any], fixture: Path, errors: list[str]) -> None:
    if not payload.get("ok"):
        errors.append(f"Project-local override apply unexpectedly failed: {payload.get('blockers')}")
    if payload.get("runtime_mode") != "project-local-override":
        errors.append("Override helper JSON must report runtime_mode=project-local-override.")
    if not (fixture / "requirements-gui.txt").exists():
        errors.append("Project-local override apply should create requirements-gui.txt.")
    elif "PySide6" not in (fixture / "requirements-gui.txt").read_text(encoding="utf-8"):
        errors.append("Project-local override requirements-gui.txt must declare PySide6.")


def validate_fail_closed_payload(payload: dict[str, Any], fixture: Path, errors: list[str]) -> None:
    if payload.get("ok"):
        errors.append("Apply helper should fail closed when project root evidence is missing.")
    blocker_codes = {item.get("code") for item in payload.get("blockers", []) if isinstance(item, dict)}
    if "unsafe_project_root" not in blocker_codes:
        errors.append("Apply helper missing unsafe_project_root blocker for fixture without root evidence.")
    if snapshot_files(fixture):
        errors.append("Fail-closed apply helper wrote files into an unsafe fixture.")


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
    override_payload: dict[str, Any] | None = None
    fail_closed_payload: dict[str, Any] | None = None
    missing_runtime_payload: dict[str, Any] | None = None
    created_fixtures: list[Path] = []
    if helper.exists() and not errors:
        preview_fixture = make_fixture(root, name="pyside6-preview", dependency_surface="pyproject")
        apply_fixture = make_fixture(root, name="pyside6-apply", dependency_surface="requirements")
        override_fixture = make_fixture(root, name="pyside6-override", dependency_surface="requirements")
        unsafe_fixture = make_fixture(root, name="pyside6-unsafe", dependency_surface="none")
        missing_runtime_fixture = make_fixture(root, name="pyside6-missing-runtime", dependency_surface="requirements")
        fake_runtime = make_fake_runtime(root, "pyside6-runtime")
        created_fixtures.extend([preview_fixture, apply_fixture, override_fixture, unsafe_fixture, missing_runtime_fixture, fake_runtime.parent])
        before = snapshot_files(preview_fixture)
        try:
            preview_result = run_helper(root, preview_fixture, mode="preview", runtime_mode="shared")
            apply_result = run_helper(root, apply_fixture, mode="apply", runtime_mode="shared", runtime_root=fake_runtime)
            override_result = run_helper(
                root,
                override_fixture,
                mode="apply",
                runtime_mode="project-local-override",
                runtime_root=fake_runtime,
                dependency_style="requirements",
                override_reason="fixture isolated PySide6 version",
            )
            fail_result = run_helper(root, unsafe_fixture, mode="apply", runtime_mode="shared", runtime_root=fake_runtime)
            missing_runtime_result = run_helper(root, missing_runtime_fixture, mode="apply", runtime_mode="shared")
        except RuntimeError as exc:
            errors.append(str(exc))
        else:
            after = snapshot_files(preview_fixture)
            if before != after:
                errors.append("Preview helper changed fixture files; preview mode must be read-only.")
            if preview_result.returncode != 0:
                errors.append(f"Preview helper returned {preview_result.returncode}: {preview_result.stderr or preview_result.stdout}")
            if apply_result.returncode != 0:
                errors.append(f"Shared apply helper returned {apply_result.returncode}: {apply_result.stderr or apply_result.stdout}")
            if override_result.returncode != 0:
                errors.append(f"Project-local override apply helper returned {override_result.returncode}: {override_result.stderr or override_result.stdout}")
            if fail_result.returncode == 0:
                errors.append("Fail-closed apply scenario returned success for unsafe fixture.")
            if missing_runtime_result.returncode == 0:
                errors.append("Shared apply scenario returned success when the shared runtime was missing.")
            preview_payload = load_json_stdout(preview_result, errors, "Preview helper")
            apply_payload = load_json_stdout(apply_result, errors, "Shared apply helper")
            override_payload = load_json_stdout(override_result, errors, "Override apply helper")
            fail_closed_payload = load_json_stdout(fail_result, errors, "Fail-closed apply helper")
            missing_runtime_payload = load_json_stdout(missing_runtime_result, errors, "Missing-runtime apply helper")
            if preview_payload:
                if not preview_payload.get("ok"):
                    errors.append(f"Preview helper reported blockers for a valid pyproject fixture: {preview_payload.get('blockers')}")
                validate_preview_payload(preview_payload, errors)
            if apply_payload:
                validate_apply_payload(apply_payload, apply_fixture, errors)
            if override_payload:
                validate_override_payload(override_payload, override_fixture, errors)
            if fail_closed_payload:
                validate_fail_closed_payload(fail_closed_payload, unsafe_fixture, errors)
            if missing_runtime_payload:
                blocker_codes = {item.get("code") for item in missing_runtime_payload.get("blockers", []) if isinstance(item, dict)}
                if "shared_runtime_missing" not in blocker_codes:
                    errors.append("Shared apply helper must report shared_runtime_missing when runtime Python is absent.")
        finally:
            for fixture in created_fixtures:
                shutil.rmtree(fixture, ignore_errors=True)

    info.append("PySide6 GUI helper is preview-first, shared-runtime default, and project-local override gated.")
    return {
        "schema_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "helper": str(helper),
        "preview_sample": preview_payload,
        "apply_sample": apply_payload,
        "override_sample": override_payload,
        "fail_closed_sample": fail_closed_payload,
        "missing_runtime_sample": missing_runtime_payload,
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
