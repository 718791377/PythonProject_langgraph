#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "pyside6_gui_template_contract"
TEMPLATE_ROOT = Path("tools/pyside6_gui_templates")

REQUIRED_FILES: dict[str, list[str]] = {
    "README.md": ["project-local", "do not install PySide6 globally", "{{package_name}}", "{{window_title}}"],
    "requirements-gui.txt": ["PySide6"],
    "src/package_gui/__init__.py.template": ["{{project_name}}", "__version__"],
    "src/package_gui/app.py.template": ["QApplication", "MainWindow", "app.exec()", "explicit interactive verification"],
    "src/package_gui/main_window.py.template": ["QMainWindow", "ServiceAdapter", "WorkerAdapter", "ConfigDataDirectoryAdapter", "show_business_error", "{{window_title}}"],
    "tools/gui/check_pyside6_env.py.template": ["project_root_evidence", "python_path", "python_version", "package_manager", "dependency_style", "local_only_artifacts", "blockers", "rollback_steps"],
    "tools/gui/run_gui.ps1.template": [".venv\\Scripts\\python.exe", "Project-local Python", "{{package_name}}.app"],
    "tests/test_gui_import.py.template": ["imports_without_visible_window", "MainWindow", "WorkerAdapter", "ConfigDataDirectoryAdapter"],
    "packaging/pyside6_packaging_preflight.ps1.template": ["excludes_credentials", "excludes_browser_profiles", "release_signing_distribution_requires_separate_approval"],
}

FORBIDDEN_SNIPPETS: dict[str, list[str]] = {
    "all": ["pip install --user", "--global", "Remove-Item -Recurse $ProjectRoot"],
    "tools/gui/run_gui.ps1.template": ["pip install", "Start-Process"],
    "src/package_gui/app.py.template": ["requests.", "urllib.request", "socket."],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    template_root = root / TEMPLATE_ROOT

    if not template_root.exists():
        errors.append(f"Missing PySide6 GUI template root: {TEMPLATE_ROOT}")

    for relative, snippets in REQUIRED_FILES.items():
        path = template_root / relative
        if not path.exists():
            errors.append(f"Missing PySide6 GUI template file: {TEMPLATE_ROOT / relative}")
            continue
        text = read_text(path)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{TEMPLATE_ROOT / relative} missing required snippet: {snippet}")
        forbidden = FORBIDDEN_SNIPPETS.get("all", []) + FORBIDDEN_SNIPPETS.get(relative, [])
        for snippet in forbidden:
            if snippet in text:
                errors.append(f"{TEMPLATE_ROOT / relative} contains forbidden snippet: {snippet}")

    env_template = template_root / "tools/gui/check_pyside6_env.py.template"
    if env_template.exists():
        text = read_text(env_template)
        json_fields = [
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
        for field in json_fields:
            if f'"{field}"' not in text:
                errors.append(f"check_pyside6_env.py.template missing JSON field `{field}`.")

    import_template = template_root / "tests/test_gui_import.py.template"
    if import_template.exists():
        text = read_text(import_template)
        if "QApplication(" in text or ".show()" in text or "app.exec" in text:
            errors.append("Import smoke template must not create a visible QApplication or run the event loop.")

    info.append("PySide6 GUI templates are present and remain project-local, preview-first, and import-smoke friendly.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "template_root": str(template_root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_files": len(REQUIRED_FILES),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository PySide6 GUI template contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 GUI template contract check passed." if payload["ok"] else "PySide6 GUI template contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
