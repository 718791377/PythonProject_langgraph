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

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback is not expected here.
    tomllib = None  # type: ignore[assignment]


CHECK_NAME = "pyside6_project_opt_in_contract"
ROLLBACK_NOTE = Path("docs/pyside6_gui_rollback.md")
REQUIRED_PROJECT_FILES = [
    Path("tools/gui/run_gui.ps1"),
    Path("tools/gui/check_pyside6_env.py"),
    Path("tests/test_gui_import.py"),
    ROLLBACK_NOTE,
]
GUI_PACKAGE_REQUIRED_FILES = ["__init__.py", "app.py", "main_window.py"]
REQUIRED_MAIN_WINDOW_SNIPPETS = [
    "QMainWindow",
    "ServiceAdapter",
    "WorkerAdapter",
    "ConfigDataDirectoryAdapter",
]
VISIBLE_TEST_SNIPPETS = [".show()", "app.exec()", "QApplication.exec("]
PYSIDE6_REQUIREMENT_RE = re.compile(r"^\s*PySide6(?:\s*(?:==|~=|>=|<=|>|<|!=).*)?\s*(?:#.*)?$", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_pyside6_requirement(value: object) -> bool:
    if isinstance(value, str):
        return PYSIDE6_REQUIREMENT_RE.match(value.strip()) is not None or value.strip().lower().startswith("pyside6[")
    if isinstance(value, dict):
        name = str(value.get("name", "")).strip().lower()
        return name == "pyside6"
    return False


def project_root_evidence(project_root: Path) -> list[str]:
    evidence = []
    for relative in [".git", "pyproject.toml", "requirements.txt", "requirements-gui.txt", "README.md", "setup.cfg", "setup.py", "poetry.lock", "uv.lock"]:
        if (project_root / relative).exists():
            evidence.append(relative)
    return evidence


def collect_requirement_surfaces(project_root: Path) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for path in sorted(project_root.glob("requirements*.txt")):
        matches = [
            line.strip()
            for line in read_text(path).splitlines()
            if line.strip() and not line.lstrip().startswith("#") and PYSIDE6_REQUIREMENT_RE.match(line.strip())
        ]
        if matches:
            surfaces.append(
                {
                    "kind": "requirements",
                    "path": str(path.relative_to(project_root)).replace("\\", "/"),
                    "entries": matches,
                    "preferred": path.name == "requirements-gui.txt",
                }
            )
    return surfaces


def collect_pyproject_surfaces(project_root: Path, errors: list[str]) -> list[dict[str, Any]]:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return []
    if tomllib is None:
        errors.append("tomllib is unavailable; cannot inspect pyproject.toml for PySide6 opt-in evidence.")
        return []
    try:
        data = tomllib.loads(read_text(pyproject))
    except Exception as exc:  # pragma: no cover - exact TOML parser exception is version-specific.
        errors.append(f"Cannot parse pyproject.toml: {exc}")
        return []

    surfaces: list[dict[str, Any]] = []
    optional = data.get("project", {}).get("optional-dependencies", {})
    if isinstance(optional, dict):
        gui = optional.get("gui")
        if isinstance(gui, list) and any(is_pyside6_requirement(item) for item in gui):
            surfaces.append({"kind": "pyproject-extra", "path": "pyproject.toml", "group": "project.optional-dependencies.gui"})

    dependency_groups = data.get("dependency-groups", {})
    if isinstance(dependency_groups, dict):
        gui_group = dependency_groups.get("gui")
        if isinstance(gui_group, list) and any(is_pyside6_requirement(item) for item in gui_group):
            surfaces.append({"kind": "dependency-group", "path": "pyproject.toml", "group": "dependency-groups.gui"})

    poetry = data.get("tool", {}).get("poetry", {})
    if isinstance(poetry, dict):
        gui_deps = poetry.get("group", {}).get("gui", {}).get("dependencies", {})
        if isinstance(gui_deps, dict) and any(key.lower() == "pyside6" for key in gui_deps):
            surfaces.append({"kind": "poetry-group", "path": "pyproject.toml", "group": "tool.poetry.group.gui.dependencies"})

    return surfaces


def collect_dependency_surfaces(project_root: Path, errors: list[str]) -> list[dict[str, Any]]:
    return collect_requirement_surfaces(project_root) + collect_pyproject_surfaces(project_root, errors)


def collect_lockfile_evidence(project_root: Path, dependency_surfaces: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    uv_lock = project_root / "uv.lock"
    poetry_lock = project_root / "poetry.lock"

    for surface in dependency_surfaces:
        kind = str(surface.get("kind", "unknown"))
        record: dict[str, Any] = {
            "dependency_surface": kind,
            "dependency_path": surface.get("path"),
            "lockfile_required": False,
            "lockfile_path": None,
            "lockfile_present": False,
            "manager": "unknown",
            "review_required": True,
            "env_ready_inferred_from_lockfile": False,
        }
        if kind == "requirements":
            record.update(
                {
                    "manager": "pip",
                    "lockfile_required": False,
                    "lockfile_path": "requirements-gui.txt",
                    "lockfile_present": True,
                    "note": "requirements-gui.txt declares the GUI dependency; no lockfile is required by this shared contract.",
                }
            )
        elif kind == "dependency-group" and uv_lock.exists():
            record.update(
                {
                    "manager": "uv",
                    "lockfile_required": True,
                    "lockfile_path": "uv.lock",
                    "lockfile_present": True,
                    "note": "uv.lock exists and must be reviewed with the PySide6 GUI opt-in diff before claiming environment readiness.",
                }
            )
        elif kind == "dependency-group":
            record.update(
                {
                    "manager": "dependency-group",
                    "lockfile_required": False,
                    "note": "No uv.lock marker was found; use the target project's native dependency-group lockfile workflow if one exists.",
                }
            )
            warnings.append("PySide6 is declared in a dependency group without uv.lock; verify the target project's lockfile workflow manually.")
        elif kind == "poetry-group":
            record.update(
                {
                    "manager": "poetry",
                    "lockfile_required": True,
                    "lockfile_path": "poetry.lock",
                    "lockfile_present": poetry_lock.exists(),
                    "note": "Poetry GUI group opt-in requires poetry.lock review before claiming environment readiness.",
                }
            )
            if not poetry_lock.exists():
                errors.append("Poetry GUI dependency group is present but poetry.lock is missing; generate or document the Poetry lockfile before accepting opt-in evidence.")
        elif kind == "pyproject-extra" and poetry_lock.exists():
            record.update(
                {
                    "manager": "poetry",
                    "lockfile_required": True,
                    "lockfile_path": "poetry.lock",
                    "lockfile_present": True,
                    "note": "poetry.lock exists and must be reviewed with the optional GUI extra before claiming environment readiness.",
                }
            )
        elif kind == "pyproject-extra":
            record.update(
                {
                    "manager": "pyproject",
                    "lockfile_required": False,
                    "note": "No project lockfile marker was found; do not infer env_ready from the optional dependency declaration alone.",
                }
            )
        else:
            record["note"] = "Unknown dependency surface; do not infer lockfile or environment readiness."
        evidence.append(record)

    return evidence


def find_gui_packages(project_root: Path) -> list[dict[str, Any]]:
    src = project_root / "src"
    if not src.exists():
        return []
    packages: list[dict[str, Any]] = []
    for directory in sorted(path for path in src.iterdir() if path.is_dir()):
        missing = [name for name in GUI_PACKAGE_REQUIRED_FILES if not (directory / name).exists()]
        if missing:
            continue
        main_window = read_text(directory / "main_window.py")
        app = read_text(directory / "app.py")
        missing_snippets = [snippet for snippet in REQUIRED_MAIN_WINDOW_SNIPPETS if snippet not in main_window]
        if "QApplication" not in app:
            missing_snippets.append("QApplication")
        packages.append(
            {
                "package": directory.name,
                "path": str(directory.relative_to(project_root)).replace("\\", "/"),
                "missing_boundary_snippets": missing_snippets,
            }
        )
    return packages


def validate_project(project_root: Path, *, allow_duplicate_dependency_surfaces: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    project_root = project_root.resolve()

    if not project_root.exists():
        errors.append(f"Project root does not exist: {project_root}")
    elif not project_root.is_dir():
        errors.append(f"Project root is not a directory: {project_root}")

    evidence = project_root_evidence(project_root) if project_root.exists() else []
    if not evidence:
        errors.append("No reliable project-root evidence found; expected .git, pyproject.toml, requirements, README, setup file, poetry.lock, or uv.lock.")

    dependency_surfaces = collect_dependency_surfaces(project_root, errors) if project_root.exists() else []
    if not dependency_surfaces:
        errors.append("No project-local PySide6 dependency declaration found in requirements-gui.txt, requirements*.txt, pyproject optional dependencies, dependency groups, or Poetry gui group.")
    if len(dependency_surfaces) > 1 and not allow_duplicate_dependency_surfaces:
        surface_names = ", ".join(f"{item.get('kind')}:{item.get('path')}" for item in dependency_surfaces)
        errors.append(f"PySide6 appears in multiple dependency surfaces; keep one project-native declaration or pass --allow-duplicate-dependency-surfaces after human review: {surface_names}")
    if any(item.get("kind") == "requirements" and not item.get("preferred") for item in dependency_surfaces):
        warnings.append("PySide6 is declared in a requirements*.txt file other than requirements-gui.txt; verify this matches the target project's dependency convention.")
    lockfile_evidence = collect_lockfile_evidence(project_root, dependency_surfaces, errors, warnings) if project_root.exists() else []

    existing_files = []
    missing_files = []
    for relative in REQUIRED_PROJECT_FILES:
        target = project_root / relative
        if target.exists():
            existing_files.append(str(relative).replace("\\", "/"))
        else:
            missing_files.append(str(relative).replace("\\", "/"))
    if missing_files:
        errors.append("Missing required PySide6 opt-in project files: " + ", ".join(missing_files))

    packages = find_gui_packages(project_root) if project_root.exists() else []
    if not packages:
        errors.append("No GUI package found under src/* with __init__.py, app.py, and main_window.py.")
    for package in packages:
        if package["missing_boundary_snippets"]:
            errors.append(
                f"GUI package {package['path']} is missing required GUI/business boundary snippets: "
                + ", ".join(package["missing_boundary_snippets"])
            )

    test_path = project_root / "tests" / "test_gui_import.py"
    if test_path.exists():
        test_text = read_text(test_path)
        for snippet in VISIBLE_TEST_SNIPPETS:
            if snippet in test_text:
                errors.append(f"Import smoke test must not launch a visible GUI or event loop; found `{snippet}` in tests/test_gui_import.py.")
        if "importlib.import_module" not in test_text and "from " not in test_text:
            warnings.append("tests/test_gui_import.py exists but does not clearly import the GUI package.")

    rollback = project_root / ROLLBACK_NOTE
    if rollback.exists():
        rollback_text = read_text(rollback).lower()
        for snippet in ["rollback", "pyside6", "dependency"]:
            if snippet not in rollback_text:
                errors.append(f"{ROLLBACK_NOTE} must mention {snippet!r}.")

    run_gui = project_root / "tools" / "gui" / "run_gui.ps1"
    if run_gui.exists():
        run_text = read_text(run_gui)
        for snippet in [".venv", "PYTHONPATH", "-m"]:
            if snippet not in run_text:
                errors.append(f"tools/gui/run_gui.ps1 must include project-local launch evidence snippet `{snippet}`.")

    env_check = project_root / "tools" / "gui" / "check_pyside6_env.py"
    if env_check.exists() and "PySide6" not in read_text(env_check):
        errors.append("tools/gui/check_pyside6_env.py must mention PySide6 import/environment evidence.")

    if not errors:
        info.append("Consumer project PySide6 opt-in has dependency, template, import-smoke, run-helper, and rollback evidence.")

    capability_state = "template_ready" if dependency_surfaces and packages and not missing_files else "declared" if dependency_surfaces else "candidate"
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "project",
        "ok": not errors,
        "project_root": str(project_root),
        "project_root_evidence": evidence,
        "capability_state": capability_state,
        "dependency_surfaces": dependency_surfaces,
        "lockfile_evidence": lockfile_evidence,
        "gui_packages": packages,
        "required_files_present": existing_files,
        "required_files_missing": missing_files,
        "verified": False,
        "packaged": False,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "dependency_surfaces": len(dependency_surfaces),
            "lockfile_evidence": len(lockfile_evidence),
            "gui_packages": len(packages),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_valid_fixture(root: Path, name: str) -> Path:
    fixture = root / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
    write(fixture / "README.md", "# Sample PySide6 opt-in fixture\n")
    write(fixture / "requirements-gui.txt", "PySide6\n")
    write(fixture / "src" / "sample_gui" / "__init__.py", '"""Sample GUI."""\n')
    write(
        fixture / "src" / "sample_gui" / "app.py",
        "from PySide6.QtWidgets import QApplication\nfrom .main_window import MainWindow\n\n"
        "def build_app(argv=None):\n    return QApplication(list(argv or []))\n",
    )
    write(
        fixture / "src" / "sample_gui" / "main_window.py",
        "from PySide6.QtWidgets import QMainWindow\n\n"
        "class ServiceAdapter: pass\nclass WorkerAdapter: pass\nclass ConfigDataDirectoryAdapter: pass\n"
        "class MainWindow(QMainWindow): pass\n",
    )
    write(
        fixture / "tests" / "test_gui_import.py",
        "import importlib\n\n"
        "def test_gui_package_imports_without_visible_window():\n"
        "    module = importlib.import_module('sample_gui.main_window')\n"
        "    assert hasattr(module, 'MainWindow')\n",
    )
    write(fixture / "tools" / "gui" / "run_gui.ps1", "$env:PYTHONPATH = Join-Path $ProjectRoot 'src'\n& .\\.venv\\Scripts\\python.exe -m sample_gui.app\n")
    write(fixture / "tools" / "gui" / "check_pyside6_env.py", "from PySide6.QtWidgets import QApplication\nprint('PySide6 ok')\n")
    write(fixture / "docs" / "pyside6_gui_rollback.md", "# PySide6 GUI rollback\n\nRemove the PySide6 dependency and generated GUI files.\n")
    return fixture


def run_self_test(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    samples: dict[str, Any] = {}
    fixtures: list[Path] = []
    try:
        valid = make_valid_fixture(root, "pyside6-optin-valid")
        fixtures.append(valid)
        samples["valid"] = validate_project(valid)
        if not samples["valid"]["ok"]:
            errors.append("Valid opt-in fixture did not pass: " + "; ".join(samples["valid"]["errors"]))

        missing_dependency = make_valid_fixture(root, "pyside6-optin-missing-dependency")
        fixtures.append(missing_dependency)
        (missing_dependency / "requirements-gui.txt").unlink()
        samples["missing_dependency"] = validate_project(missing_dependency)
        if samples["missing_dependency"]["ok"]:
            errors.append("Fixture without PySide6 dependency declaration unexpectedly passed.")

        duplicate_dependency = make_valid_fixture(root, "pyside6-optin-duplicate-dependency")
        fixtures.append(duplicate_dependency)
        write(
            duplicate_dependency / "pyproject.toml",
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n\n[project.optional-dependencies]\ngui = [\"PySide6\"]\n",
        )
        samples["duplicate_dependency"] = validate_project(duplicate_dependency)
        if samples["duplicate_dependency"]["ok"]:
            errors.append("Fixture with duplicate PySide6 dependency surfaces unexpectedly passed.")

        visible_test = make_valid_fixture(root, "pyside6-optin-visible-test")
        fixtures.append(visible_test)
        write(visible_test / "tests" / "test_gui_import.py", "def test_bad():\n    window.show()\n")
        samples["visible_test"] = validate_project(visible_test)
        if samples["visible_test"]["ok"]:
            errors.append("Fixture with visible GUI smoke-test launch unexpectedly passed.")
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
        "warnings": warnings,
        "info": ["Self-test validates pass/fail behavior for consumer-project PySide6 opt-in checks."],
        "counts": {
            "samples": len(samples),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check consumer-project PySide6 opt-in evidence or self-test the checker contract.")
    parser.add_argument("--root", default=".", help="Repository root for self-test artifacts.")
    parser.add_argument("--project-root", help="Consumer project root to validate. If omitted, run checker self-test fixtures.")
    parser.add_argument("--allow-duplicate-dependency-surfaces", action="store_true", help="Allow duplicated PySide6 dependency surfaces after human review.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.project_root:
        payload = validate_project(Path(args.project_root), allow_duplicate_dependency_surfaces=args.allow_duplicate_dependency_surfaces)
    else:
        payload = run_self_test(root)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("PySide6 project opt-in contract check passed." if payload["ok"] else "PySide6 project opt-in contract check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload.get("warnings"):
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
