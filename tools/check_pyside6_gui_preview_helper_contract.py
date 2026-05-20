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
    "apply_not_implemented",
    "project_root_evidence",
    "planned_file_changes",
    "local_only_artifacts",
    "rollback_steps",
]
FORBIDDEN_WRITE_SNIPPETS = [
    "New-Item",
    "Set-Content",
    "Out-File",
    "Add-Content",
    "Remove-Item",
    "Copy-Item",
    "Move-Item",
    "Start-Process",
    "git ",
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


def run_helper(repo_root: Path, fixture: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    powershell = find_powershell()
    if not powershell:
        raise RuntimeError("PowerShell executable not found; cannot validate preview helper execution.")
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
        "preview",
        "-DependencyStyle",
        "auto",
        "-PackageName",
        "sample_gui",
        "-CreateTemplate",
        "-RunSmokeTest",
        "-Json",
    ]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", check=False)


def make_fixture(root: Path) -> Path:
    fixture = root / ".omx" / "test-artifacts" / f"pyside6-preview-{uuid.uuid4().hex[:8]}"
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / "pyproject.toml").write_text(
        "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n",
        encoding="utf-8",
    )
    (fixture / "README.md").write_text("# Sample\n", encoding="utf-8")
    return fixture


def snapshot_files(root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    helper = root / HELPER_PATH

    if not helper.exists():
        errors.append(f"Missing PySide6 GUI preview helper: {HELPER_PATH}")
    else:
        text = read_text(helper)
        for snippet in REQUIRED_SCRIPT_SNIPPETS:
            if snippet not in text:
                errors.append(f"{HELPER_PATH} missing required snippet: {snippet}")
        for snippet in FORBIDDEN_WRITE_SNIPPETS:
            if snippet in text:
                errors.append(f"{HELPER_PATH} contains forbidden preview-mode write or launch snippet: {snippet}")

    fixture_payload: dict[str, Any] | None = None
    if helper.exists() and not errors:
        fixture = make_fixture(root)
        before = snapshot_files(fixture)
        try:
            result = run_helper(root, fixture)
        except RuntimeError as exc:
            errors.append(str(exc))
        else:
            after = snapshot_files(fixture)
            if before != after:
                errors.append("Preview helper changed fixture files; preview mode must be read-only.")
            if result.returncode != 0:
                errors.append(f"Preview helper returned {result.returncode}: {result.stderr or result.stdout}")
            try:
                fixture_payload = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"Preview helper did not emit valid JSON with -Json: {exc}: {result.stdout!r}")
            if fixture_payload:
                if not fixture_payload.get("ok"):
                    errors.append(f"Preview helper reported blockers for a valid pyproject fixture: {fixture_payload.get('blockers')}")
                for field in REQUIRED_JSON_FIELDS:
                    if field not in fixture_payload:
                        errors.append(f"Preview helper JSON missing required field `{field}`.")
                if fixture_payload.get("mode") != "preview":
                    errors.append("Preview helper JSON must report mode=preview.")
                if fixture_payload.get("dependency_style") != "pyproject-extra":
                    errors.append("Preview helper should detect pyproject fixture as dependency_style=pyproject-extra.")
                planned = fixture_payload.get("planned_file_changes") or []
                if not any(item.get("path") == "pyproject.toml" for item in planned if isinstance(item, dict)):
                    errors.append("Preview helper did not plan pyproject.toml dependency update for pyproject fixture.")
                if not any("src/sample_gui/app.py" == item.get("path") for item in planned if isinstance(item, dict)):
                    errors.append("Preview helper did not plan sample_gui app template creation when -CreateTemplate is set.")

    info.append("PySide6 GUI preview helper is preview-first, structured, and read-only.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "helper": str(helper),
        "preview_sample": fixture_payload,
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
    parser = argparse.ArgumentParser(description="Check PySide6 GUI preview helper contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 GUI preview helper contract check passed." if payload["ok"] else "PySide6 GUI preview helper contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
