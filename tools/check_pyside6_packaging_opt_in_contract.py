#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pyside6_project_opt_in_contract import make_valid_fixture, validate_project  # noqa: E402


CHECK_NAME = "pyside6_packaging_opt_in_contract"
PREFLIGHT_SCRIPT = Path("tools/gui/pyside6_packaging_preflight.ps1")
PREFLIGHT_DOC = Path("docs/pyside6_packaging_preflight.md")
ROLLBACK_DOC = Path("docs/pyside6_packaging_rollback.md")
REQUIRED_PACKAGING_FILES = [PREFLIGHT_SCRIPT, PREFLIGHT_DOC, ROLLBACK_DOC]
SUPPORTED_TOOLS = {"PyInstaller", "Nuitka"}

PREFLIGHT_SCRIPT_SNIPPETS = [
    "ConvertTo-Json",
    "packaging_tool",
    "qt_platform_plugin_checked",
    "resource_paths_checked",
    "icon_paths_checked",
    "windows_dpi_checked",
    "chinese_font_rendering_checked",
    "startup_logging_checked",
    "data_directory_checked",
    "excludes_credentials",
    "excludes_browser_profiles",
    "excludes_user_private_data",
    "reproducible_build_command",
    "output_directory",
    "rollback_steps",
    "release_signing_distribution_requires_separate_approval",
]

PREFLIGHT_DOC_SNIPPETS = [
    "packaging_tool:",
    "qt platform plugin",
    "resource",
    "icon",
    "dpi",
    "chinese font",
    "startup log",
    "data directory",
    "antivirus",
    "reproducible build",
    "output directory",
    "separate approval",
    "rollback",
]

ROLLBACK_DOC_SNIPPETS = [
    "rollback",
    "pyside6",
    "packaging",
    "output directory",
    "generated artifacts",
    "dependency",
]

FORBIDDEN_PREFLIGHT_SCRIPT_SNIPPETS = [
    "Invoke-WebRequest",
    "Start-Process",
    "Remove-Item",
    "Set-ExecutionPolicy",
    "git push",
    "twine upload",
    "signtool",
    "Browser\\User Data",
    ".ssh",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def detect_selected_tool(text: str) -> tuple[str | None, list[str]]:
    matches = re.findall(r"(?im)^\s*packaging_tool\s*:\s*(PyInstaller|Nuitka)\s*$", text)
    unique = sorted(set(matches))
    return (unique[0], unique) if len(unique) == 1 else (None, unique)


def lower_contains_all(text: str, snippets: list[str]) -> list[str]:
    lower = text.lower()
    return [snippet for snippet in snippets if snippet.lower() not in lower]


def validate_packaging_opt_in(project_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    project_root = project_root.resolve()

    base_project = validate_project(project_root)
    if not base_project["ok"]:
        errors.append("Project PySide6 opt-in contract must pass before packaging opt-in evidence can be accepted.")

    existing_files: list[str] = []
    missing_files: list[str] = []
    for relative in REQUIRED_PACKAGING_FILES:
        target = project_root / relative
        if target.exists():
            existing_files.append(str(relative).replace("\\", "/"))
        else:
            missing_files.append(str(relative).replace("\\", "/"))
    if missing_files:
        errors.append("Missing required PySide6 packaging opt-in files: " + ", ".join(missing_files))

    selected_tool = None
    selected_tool_markers: list[str] = []
    preflight_doc = project_root / PREFLIGHT_DOC
    if preflight_doc.exists():
        preflight_doc_text = read_text(preflight_doc)
        selected_tool, selected_tool_markers = detect_selected_tool(preflight_doc_text)
        if not selected_tool:
            if selected_tool_markers:
                errors.append("Packaging preflight doc must choose exactly one packaging_tool marker, not multiple.")
            else:
                errors.append("Packaging preflight doc must include exactly one marker: `packaging_tool: PyInstaller` or `packaging_tool: Nuitka`.")
        missing_doc_snippets = lower_contains_all(preflight_doc_text, PREFLIGHT_DOC_SNIPPETS)
        if missing_doc_snippets:
            errors.append(f"{PREFLIGHT_DOC} missing required packaging evidence snippets: " + ", ".join(missing_doc_snippets))

    preflight_script = project_root / PREFLIGHT_SCRIPT
    if preflight_script.exists():
        script_text = read_text(preflight_script)
        for snippet in PREFLIGHT_SCRIPT_SNIPPETS:
            if snippet not in script_text:
                errors.append(f"{PREFLIGHT_SCRIPT} missing required structured field/snippet `{snippet}`.")
        for snippet in FORBIDDEN_PREFLIGHT_SCRIPT_SNIPPETS:
            if snippet in script_text:
                errors.append(f"{PREFLIGHT_SCRIPT} contains forbidden automated packaging/release/destructive snippet `{snippet}`.")
        if selected_tool and selected_tool not in script_text:
            errors.append(f"{PREFLIGHT_SCRIPT} must mention selected packaging tool `{selected_tool}`.")

    rollback_doc = project_root / ROLLBACK_DOC
    if rollback_doc.exists():
        rollback_text = read_text(rollback_doc)
        missing_rollback_snippets = lower_contains_all(rollback_text, ROLLBACK_DOC_SNIPPETS)
        if missing_rollback_snippets:
            errors.append(f"{ROLLBACK_DOC} missing required rollback snippets: " + ", ".join(missing_rollback_snippets))

    if not errors:
        info.append("PySide6 packaging opt-in has preflight, rollback, data-exclusion, and separate release-approval evidence.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "project",
        "ok": not errors,
        "project_root": str(project_root),
        "base_project_ok": base_project["ok"],
        "selected_packaging_tool": selected_tool,
        "selected_tool_markers": selected_tool_markers,
        "packaging_state": "preflight_ready" if not errors else "candidate",
        "required_files_present": existing_files,
        "required_files_missing": missing_files,
        "packaged": False,
        "release_ready": False,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "required_files": len(REQUIRED_PACKAGING_FILES),
            "required_files_present": len(existing_files),
        },
    }


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def add_packaging_evidence(project: Path, *, tool: str = "PyInstaller") -> None:
    write(
        project / PREFLIGHT_SCRIPT,
        "param(\n"
        "  [ValidateSet(\"PyInstaller\", \"Nuitka\")]\n"
        f"  [string]$Tool = \"{tool}\"\n"
        ")\n"
        "$checks = [ordered]@{\n"
        "  schema_version = 1\n"
        "  packaging_tool = $Tool\n"
        "  qt_platform_plugin_checked = $true\n"
        "  resource_paths_checked = $true\n"
        "  icon_paths_checked = $true\n"
        "  windows_dpi_checked = $true\n"
        "  chinese_font_rendering_checked = $true\n"
        "  startup_logging_checked = $true\n"
        "  data_directory_checked = $true\n"
        "  excludes_credentials = $true\n"
        "  excludes_browser_profiles = $true\n"
        "  excludes_user_private_data = $true\n"
        "  reproducible_build_command = \"python -m PyInstaller --clean app.spec\"\n"
        "  output_directory = \"dist\"\n"
        "  rollback_steps = @(\"remove generated artifacts\", \"restore previous dependency files\")\n"
        "  release_signing_distribution_requires_separate_approval = $true\n"
        "}\n"
        "$checks | ConvertTo-Json -Depth 4\n",
    )
    write(
        project / PREFLIGHT_DOC,
        f"# PySide6 packaging preflight\n\n"
        f"packaging_tool: {tool}\n\n"
        "- Qt platform plugin checked before packaging.\n"
        "- Resource paths and icon paths are reviewed.\n"
        "- Windows DPI behavior and Chinese font rendering are reviewed.\n"
        "- Startup log behavior is documented.\n"
        "- Data directory and config-file locations are documented.\n"
        "- Antivirus false-positive risk is recorded.\n"
        "- Reproducible build command and output directory are recorded.\n"
        "- Release, signing, and distribution require separate approval.\n"
        "- Rollback path points to generated artifacts and dependency changes.\n",
    )
    write(
        project / ROLLBACK_DOC,
        "# PySide6 packaging rollback\n\n"
        "Rollback PySide6 packaging by removing generated artifacts from the output directory, "
        "restoring packaging dependency files, and keeping source templates intact.\n",
    )


def make_packaging_fixture(root: Path, name: str, *, tool: str = "PyInstaller") -> Path:
    project = make_valid_fixture(root, name)
    add_packaging_evidence(project, tool=tool)
    return project


def run_self_test(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    samples: dict[str, Any] = {}
    fixtures: list[Path] = []
    try:
        valid = make_packaging_fixture(root, f"pyside6-packaging-valid-{uuid.uuid4().hex[:8]}")
        fixtures.append(valid)
        samples["valid"] = validate_packaging_opt_in(valid)
        if not samples["valid"]["ok"]:
            errors.append("Valid packaging opt-in fixture did not pass: " + "; ".join(samples["valid"]["errors"]))

        missing_preflight = make_packaging_fixture(root, f"pyside6-packaging-missing-preflight-{uuid.uuid4().hex[:8]}")
        fixtures.append(missing_preflight)
        (missing_preflight / PREFLIGHT_SCRIPT).unlink()
        samples["missing_preflight"] = validate_packaging_opt_in(missing_preflight)
        if samples["missing_preflight"]["ok"]:
            errors.append("Fixture without packaging preflight script unexpectedly passed.")

        ambiguous_tool = make_packaging_fixture(root, f"pyside6-packaging-ambiguous-tool-{uuid.uuid4().hex[:8]}")
        fixtures.append(ambiguous_tool)
        write(
            ambiguous_tool / PREFLIGHT_DOC,
            "packaging_tool: PyInstaller\npackaging_tool: Nuitka\n"
            "qt platform plugin resource icon dpi chinese font startup log data directory antivirus "
            "reproducible build output directory separate approval rollback\n",
        )
        samples["ambiguous_tool"] = validate_packaging_opt_in(ambiguous_tool)
        if samples["ambiguous_tool"]["ok"]:
            errors.append("Fixture with multiple packaging_tool markers unexpectedly passed.")

        unsafe_script = make_packaging_fixture(root, f"pyside6-packaging-unsafe-script-{uuid.uuid4().hex[:8]}")
        fixtures.append(unsafe_script)
        with (unsafe_script / PREFLIGHT_SCRIPT).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\nStart-Process signtool.exe\n")
        samples["unsafe_script"] = validate_packaging_opt_in(unsafe_script)
        if samples["unsafe_script"]["ok"]:
            errors.append("Fixture with unsafe packaging/release automation unexpectedly passed.")
    finally:
        for fixture in fixtures:
            shutil.rmtree(fixture, ignore_errors=True)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "self-test",
        "ok": not errors,
        "root": str(root),
        "samples": samples,
        "errors": errors,
        "warnings": [],
        "info": ["Self-test validates pass/fail behavior for PySide6 packaging opt-in evidence checks."],
        "counts": {
            "samples": len(samples),
            "errors": len(errors),
            "warnings": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PySide6 packaging opt-in evidence or self-test the checker contract.")
    parser.add_argument("--root", default=".", help="Repository root for self-test artifacts.")
    parser.add_argument("--project-root", help="Consumer project root to validate. If omitted, run checker self-test fixtures.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = validate_packaging_opt_in(Path(args.project_root)) if args.project_root else run_self_test(root)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 packaging opt-in contract check passed." if payload["ok"] else "PySide6 packaging opt-in contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload.get("warnings"):
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
