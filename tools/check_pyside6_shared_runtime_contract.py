#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "pyside6_shared_runtime_contract"
HELPER = Path("tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1")
REQUIREMENTS_TEMPLATE = Path("tools/pyside6_gui_templates/shared_runtime/requirements-pyside6.txt.template")
RUNTIME_JSON_TEMPLATE = Path("tools/pyside6_gui_templates/shared_runtime/runtime.json.template")

REQUIRED_HELPER_SNIPPETS = [
    "preview",
    "provision",
    "verify",
    "RuntimeRoot",
    r"D:\PythonProject_langgraph\.shared_runtimes\pyside6",
    "requirements-pyside6.txt",
    "runtime.json",
    "PySide6",
    "import_only_verified",
    "runtime_root",
    "runtime_python",
    "python_version",
    "pyside6_version",
    "qt_version",
    "requirements_file",
    "local_only_artifacts",
    "blockers",
    "rollback_steps",
    "GetTempFileName",
    "WriteAllText($probePath",
    "Remove-Item -LiteralPath $probePath -Force",
    "Out-String",
]

FORBIDDEN_HELPER_SNIPPETS = [
    "Start-Process",
    "pip install --user",
    "--user",
    "global Python",
    "Set-ExecutionPolicy",
    "git push",
    "Remove-Item -Recurse",
    "-c $probe",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    gitignore = root / ".gitignore"
    if not gitignore.exists() or ".shared_runtimes/" not in read_text(gitignore):
        errors.append(".gitignore must contain `.shared_runtimes/` so shared PySide6 runtime binaries stay local-only.")

    helper = root / HELPER
    if not helper.exists():
        errors.append(f"Missing shared runtime helper: {HELPER.as_posix()}")
    else:
        helper_text = read_text(helper)
        for snippet in REQUIRED_HELPER_SNIPPETS:
            if snippet not in helper_text:
                errors.append(f"{HELPER.as_posix()} missing required snippet: {snippet}")
        for snippet in FORBIDDEN_HELPER_SNIPPETS:
            if snippet in helper_text:
                errors.append(f"{HELPER.as_posix()} contains forbidden snippet: {snippet}")
        if not re.search(r"ValidateSet\(\"preview\",\s*\"provision\",\s*\"verify\"\)", helper_text):
            errors.append(f"{HELPER.as_posix()} must validate exactly preview/provision/verify modes.")
        if "QApplication" in helper_text and ".show()" in helper_text:
            errors.append(f"{HELPER.as_posix()} must remain import-only and must not show a GUI window.")
        if "-m pip install -r $requirementsFile" not in helper_text:
            errors.append(f"{HELPER.as_posix()} must install only from requirements-pyside6.txt inside the shared runtime during provision.")
        if "runtime_root_outside_shared_runtime" not in helper_text:
            errors.append(f"{HELPER.as_posix()} must fail closed when RuntimeRoot is outside .shared_runtimes/pyside6.")
        if "GetTempFileName" not in helper_text or "-c $probe" in helper_text:
            errors.append(
                f"{HELPER.as_posix()} must run the import-only probe from a temporary UTF-8 Python file, "
                "not by passing a multi-line script through `python -c`, which drops quotes in Windows PowerShell."
            )

    for template in (REQUIREMENTS_TEMPLATE, RUNTIME_JSON_TEMPLATE):
        path = root / template
        if not path.exists():
            errors.append(f"Missing shared runtime template: {template.as_posix()}")

    requirements = root / REQUIREMENTS_TEMPLATE
    if requirements.exists() and "PySide6" not in read_text(requirements):
        errors.append(f"{REQUIREMENTS_TEMPLATE.as_posix()} must declare PySide6.")

    runtime_json = root / RUNTIME_JSON_TEMPLATE
    if runtime_json.exists():
        text = read_text(runtime_json)
        for snippet in [
            '"runtime_mode": "shared"',
            "runtime_python",
            "pyside6_version",
            "qt_version",
            "import_only_verified",
            "visible_gui_requires_explicit_request",
        ]:
            if snippet not in text:
                errors.append(f"{RUNTIME_JSON_TEMPLATE.as_posix()} missing required snippet: {snippet}")
        if (
            r"D:\PythonProject_langgraph\.shared_runtimes\pyside6" not in text
            and r"D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6" not in text
        ):
            errors.append(f"{RUNTIME_JSON_TEMPLATE.as_posix()} missing required default runtime path.")

    if not errors:
        info.append("Shared PySide6 runtime contract is helper-backed, gitignored, import-only, and local-only.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "helper": str(helper),
        "requirements_template": str(root / REQUIREMENTS_TEMPLATE),
        "runtime_json_template": str(root / RUNTIME_JSON_TEMPLATE),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "required_helper_snippets": len(REQUIRED_HELPER_SNIPPETS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shared PySide6 runtime repository contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 shared runtime contract check passed." if payload["ok"] else "PySide6 shared runtime contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
