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
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


CHECK_NAME = "pyside6_project_opt_in_contract"
ROLLBACK_NOTE = Path("docs/pyside6_gui_rollback.md")
RUNTIME_CONTRACT = Path("tools/gui/pyside6_runtime_contract.json")
ADAPTER_README = Path("tools/gui/adapters/README.md")
REQUIRED_PROJECT_FILES = [
    RUNTIME_CONTRACT,
    ADAPTER_README,
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
DEFAULT_SHARED_RUNTIME_ROOT = r"D:\PythonProject_langgraph\.shared_runtimes\pyside6"
SMOKE_EVIDENCE_REQUIRED_TRUE_FIELDS = ["import_only_verified"]
SMOKE_EVIDENCE_REQUIRED_FIELDS = [
    "project_root",
    "python_path",
    "runtime_mode",
    "shared_runtime_root",
    "shared_runtime_python",
    "shared_runtime_status",
    "pyside6_version",
    "qt_version",
    "import_only_verified",
    "blockers",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


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
        errors.append("tomllib is unavailable; cannot inspect pyproject.toml for PySide6 override evidence.")
        return []
    try:
        data = tomllib.loads(read_text(pyproject))
    except Exception as exc:  # pragma: no cover
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
            "project_local_override_only": True,
        }
        if kind == "requirements":
            record.update({"manager": "pip", "lockfile_path": "requirements-gui.txt", "lockfile_present": True})
        elif kind == "dependency-group" and uv_lock.exists():
            record.update({"manager": "uv", "lockfile_required": True, "lockfile_path": "uv.lock", "lockfile_present": True})
        elif kind == "dependency-group":
            record.update({"manager": "dependency-group"})
            warnings.append("PySide6 project-local override dependency group has no uv.lock marker; verify the lockfile workflow manually.")
        elif kind == "poetry-group":
            record.update({"manager": "poetry", "lockfile_required": True, "lockfile_path": "poetry.lock", "lockfile_present": poetry_lock.exists()})
            if not poetry_lock.exists():
                errors.append("Poetry GUI override dependency group is present but poetry.lock is missing.")
        elif kind == "pyproject-extra" and poetry_lock.exists():
            record.update({"manager": "poetry", "lockfile_required": True, "lockfile_path": "poetry.lock", "lockfile_present": True})
        elif kind == "pyproject-extra":
            record.update({"manager": "pyproject"})
        evidence.append(record)

    return evidence


def load_runtime_contract(project_root: Path, errors: list[str]) -> dict[str, Any]:
    path = project_root / RUNTIME_CONTRACT
    if not path.exists():
        return {}
    try:
        contract = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"{RUNTIME_CONTRACT} is not valid JSON: {exc}")
        return {}
    return contract


def validate_runtime_contract(contract: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if not contract:
        errors.append(f"Missing shared PySide6 runtime contract: {RUNTIME_CONTRACT}")
        return
    runtime_mode = contract.get("runtime_mode")
    if runtime_mode not in {"shared", "project-local-override"}:
        errors.append(f"{RUNTIME_CONTRACT} runtime_mode must be shared or project-local-override.")
    if runtime_mode == "shared":
        runtime_root = str(contract.get("runtime_root", ""))
        runtime_python = str(contract.get("runtime_python", ""))
        if DEFAULT_SHARED_RUNTIME_ROOT not in runtime_root:
            errors.append(f"{RUNTIME_CONTRACT} must point shared runtime root at {DEFAULT_SHARED_RUNTIME_ROOT}.")
        if DEFAULT_SHARED_RUNTIME_ROOT not in runtime_python:
            errors.append(f"{RUNTIME_CONTRACT} must point shared runtime Python at {DEFAULT_SHARED_RUNTIME_ROOT}.")
        if contract.get("project_local_override") is True:
            errors.append(f"{RUNTIME_CONTRACT} shared mode must not set project_local_override=true.")
    if runtime_mode == "project-local-override":
        if not contract.get("override_reason"):
            errors.append(f"{RUNTIME_CONTRACT} project-local-override mode requires override_reason.")
        warnings.append("Project-local PySide6 override is accepted only with dependency, lockfile/version, and rollback evidence.")
    for key in ["visible_gui_requires_explicit_request", "packaging_requires_explicit_request"]:
        if contract.get(key) is not True:
            errors.append(f"{RUNTIME_CONTRACT} must set {key}=true.")


def load_smoke_evidence(smoke_json: Path | None, project_root: Path, errors: list[str]) -> dict[str, Any]:
    if smoke_json is None:
        return {"provided": False, "verified": False}
    if not smoke_json.exists():
        errors.append(f"Smoke evidence file does not exist: {smoke_json}")
        return {"provided": True, "verified": False, "path": str(smoke_json)}
    try:
        payload = json.loads(read_text(smoke_json))
    except json.JSONDecodeError as exc:
        errors.append(f"Smoke evidence JSON is invalid: {smoke_json}: {exc}")
        return {"provided": True, "verified": False, "path": str(smoke_json)}

    for field in SMOKE_EVIDENCE_REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"Smoke evidence missing required field `{field}`.")
    for field in SMOKE_EVIDENCE_REQUIRED_TRUE_FIELDS:
        if payload.get(field) is not True:
            errors.append(f"Smoke evidence must set {field}=true before project_gui_verified_with_shared_runtime can be claimed.")
    if payload.get("blockers") not in ([], None):
        errors.append(f"Smoke evidence contains blockers: {payload.get('blockers')}")
    if payload.get("runtime_mode") != "shared":
        errors.append("Smoke evidence runtime_mode must be shared.")
    if payload.get("shared_runtime_status") != "import_only_verified":
        errors.append("Smoke evidence shared_runtime_status must be import_only_verified.")
    if DEFAULT_SHARED_RUNTIME_ROOT not in str(payload.get("shared_runtime_root", "")):
        errors.append(f"Smoke evidence shared_runtime_root must point at {DEFAULT_SHARED_RUNTIME_ROOT}.")
    if DEFAULT_SHARED_RUNTIME_ROOT not in str(payload.get("shared_runtime_python", "")):
        errors.append(f"Smoke evidence shared_runtime_python must point at {DEFAULT_SHARED_RUNTIME_ROOT}.")
    reported_root = Path(str(payload.get("project_root", ""))).resolve() if payload.get("project_root") else None
    if reported_root and reported_root != project_root.resolve():
        errors.append(f"Smoke evidence project_root does not match target project root: {reported_root} != {project_root.resolve()}")

    return {
        "provided": True,
        "verified": payload.get("import_only_verified") is True and payload.get("blockers") in ([], None),
        "path": str(smoke_json),
        "payload": payload,
    }


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


def validate_project(project_root: Path, *, allow_duplicate_dependency_surfaces: bool = False, smoke_json: Path | None = None) -> dict[str, Any]:
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

    runtime_contract = load_runtime_contract(project_root, errors) if project_root.exists() else {}
    validate_runtime_contract(runtime_contract, errors, warnings)
    runtime_mode = runtime_contract.get("runtime_mode", "unknown") if runtime_contract else "unknown"

    dependency_surfaces = collect_dependency_surfaces(project_root, errors) if project_root.exists() else []
    if dependency_surfaces and runtime_mode == "shared":
        errors.append("Shared runtime mode must not declare PySide6 in project-local dependency surfaces; use project-local-override with override_reason if needed.")
    if runtime_mode == "project-local-override" and not dependency_surfaces:
        errors.append("Project-local override requires a PySide6 dependency declaration in the target project.")
    if len(dependency_surfaces) > 1 and not allow_duplicate_dependency_surfaces:
        surface_names = ", ".join(f"{item.get('kind')}:{item.get('path')}" for item in dependency_surfaces)
        errors.append(f"PySide6 appears in multiple dependency surfaces; keep one project-native override declaration or pass --allow-duplicate-dependency-surfaces after human review: {surface_names}")
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
        errors.append("Missing required PySide6 shared-runtime project files: " + ", ".join(missing_files))

    packages = find_gui_packages(project_root) if project_root.exists() else []
    smoke_evidence = load_smoke_evidence(smoke_json, project_root, errors) if project_root.exists() else {"provided": bool(smoke_json), "verified": False}
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
        for snippet in ["rollback", "pyside6", "shared runtime"]:
            if snippet not in rollback_text:
                errors.append(f"{ROLLBACK_NOTE} must mention {snippet!r}.")

    run_gui = project_root / "tools" / "gui" / "run_gui.ps1"
    if run_gui.exists():
        run_text = read_text(run_gui)
        for snippet in ["pyside6_runtime_contract.json", "runtime_mode", "PYTHONPATH", "-AllowVisibleGui"]:
            if snippet not in run_text:
                errors.append(f"tools/gui/run_gui.ps1 must include shared runtime launch evidence snippet `{snippet}`.")
        if ".venv\\Scripts\\python.exe" in run_text and runtime_mode == "shared":
            errors.append("tools/gui/run_gui.ps1 must not hard-code a project .venv Python in shared runtime mode.")

    env_check = project_root / "tools" / "gui" / "check_pyside6_env.py"
    if env_check.exists():
        env_text = read_text(env_check)
        for snippet in ["PySide6", "shared_runtime_root", "shared_runtime_python", "import_only_verified"]:
            if snippet not in env_text:
                errors.append(f"tools/gui/check_pyside6_env.py must mention shared runtime evidence snippet `{snippet}`.")

    if not errors:
        info.append("Consumer project PySide6 opt-in has shared runtime contract, template, import-smoke, run-helper, adapter, and rollback evidence.")

    capability_state = "candidate"
    if runtime_contract:
        capability_state = "shared_runtime_declared"
    if runtime_contract and packages and not missing_files:
        capability_state = "project_gui_template_ready"
    if runtime_mode == "shared" and smoke_evidence.get("verified") and not errors:
        capability_state = "project_gui_verified_with_shared_runtime"
    if runtime_mode == "project-local-override" and dependency_surfaces and not errors:
        capability_state = "project_local_override_ready"

    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "project",
        "ok": not errors,
        "project_root": str(project_root),
        "project_root_evidence": evidence,
        "capability_state": capability_state,
        "runtime_contract": runtime_contract,
        "dependency_surfaces": dependency_surfaces,
        "lockfile_evidence": lockfile_evidence,
        "shared_runtime_smoke_evidence": smoke_evidence,
        "gui_packages": packages,
        "required_files_present": existing_files,
        "required_files_missing": missing_files,
        "verified": smoke_evidence.get("verified", False),
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
    write(fixture / "README.md", "# Sample PySide6 shared-runtime opt-in fixture\n")
    write(
        fixture / RUNTIME_CONTRACT,
        json.dumps(
            {
                "schema_version": 1,
                "runtime_mode": "shared",
                "runtime_owner_repo": "D:\\PythonProject_langgraph",
                "runtime_root": DEFAULT_SHARED_RUNTIME_ROOT,
                "runtime_python": DEFAULT_SHARED_RUNTIME_ROOT + "\\.venv\\Scripts\\python.exe",
                "project_root": str(fixture),
                "gui_package": "sample_gui",
                "business_runtime_mode": "project-local-adapter",
                "visible_gui_requires_explicit_request": True,
                "packaging_requires_explicit_request": True,
                "project_local_override": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write(fixture / ADAPTER_README, "# Adapters\n\nUse shared runtime and keep business dependencies project-local.\n")
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
    write(
        fixture / "tools" / "gui" / "run_gui.ps1",
        "$RuntimeContract = Join-Path $PSScriptRoot 'pyside6_runtime_contract.json'\n"
        "$contract = Get-Content -LiteralPath $RuntimeContract -Raw -Encoding UTF8 | ConvertFrom-Json\n"
        "if ($contract.runtime_mode -ne 'shared') { throw 'runtime_mode must be shared' }\n"
        "# Visible GUI launch requires the explicit -AllowVisibleGui operator flag.\n"
        "param([switch]$AllowVisibleGui)\n"
        "$env:PYTHONPATH = Join-Path $ProjectRoot 'src'\n"
        "& $contract.runtime_python -m sample_gui.app\n",
    )
    write(
        fixture / "tools" / "gui" / "check_pyside6_env.py",
        "from PySide6.QtWidgets import QApplication\n"
        "payload = {'shared_runtime_root': '', 'shared_runtime_python': '', 'import_only_verified': True}\n"
        "print('PySide6 shared runtime ok')\n",
    )
    write(fixture / ROLLBACK_NOTE, "# PySide6 GUI rollback\n\nRollback shared runtime GUI files; keep shared runtime unchanged.\n")
    return fixture


def add_project_local_override(project: Path, *, kind: str = "requirements", include_lockfile: bool = True) -> None:
    contract = json.loads(read_text(project / RUNTIME_CONTRACT))
    contract.update({"runtime_mode": "project-local-override", "project_local_override": True, "override_reason": "fixture requires isolated PySide6 version"})
    write(project / RUNTIME_CONTRACT, json.dumps(contract, ensure_ascii=False, indent=2) + "\n")
    if kind == "requirements":
        write(project / "requirements-gui.txt", "PySide6\n")
    elif kind == "uv":
        write(project / "pyproject.toml", "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n\n[dependency-groups]\ngui = [\"PySide6\"]\n")
        if include_lockfile:
            write(project / "uv.lock", "# fixture uv lockfile\n")
    elif kind == "poetry":
        write(project / "pyproject.toml", "[tool.poetry]\nname = \"sample\"\nversion = \"0.1.0\"\ndescription = \"fixture\"\nauthors = []\n\n[tool.poetry.group.gui.dependencies]\nPySide6 = \"*\"\n")
        if include_lockfile:
            write(project / "poetry.lock", "# fixture poetry lockfile\n")
    else:
        raise ValueError(kind)


def write_smoke_evidence(project: Path, *, import_only_verified: bool = True, blockers: list[str] | None = None) -> Path:
    path = project / ".tmp" / "pyside6_shared_gui_import_smoke.json"
    write(
        path,
        json.dumps(
            {
                "schema_version": 1,
                "project_root": str(project.resolve()),
                "project_root_evidence": ["README.md"],
                "python_path": DEFAULT_SHARED_RUNTIME_ROOT + "\\.venv\\Scripts\\python.exe",
                "python_version": "3.12.10",
                "python_architecture": "64bit",
                "runtime_mode": "shared",
                "shared_runtime_root": DEFAULT_SHARED_RUNTIME_ROOT,
                "shared_runtime_python": DEFAULT_SHARED_RUNTIME_ROOT + "\\.venv\\Scripts\\python.exe",
                "shared_runtime_status": "import_only_verified" if import_only_verified else "present",
                "pyside6_version": "6.11.1",
                "qt_version": "6.11.1",
                "import_only_verified": import_only_verified,
                "package_manager": "shared-runtime",
                "dependency_style": "none-shared-runtime",
                "blockers": blockers or [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    return path


def run_self_test(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    samples: dict[str, Any] = {}
    fixtures: list[Path] = []
    try:
        valid = make_valid_fixture(root, "pyside6-shared-optin-valid")
        fixtures.append(valid)
        samples["valid"] = validate_project(valid)
        if not samples["valid"]["ok"]:
            errors.append("Valid shared-runtime opt-in fixture did not pass: " + "; ".join(samples["valid"]["errors"]))

        smoke_path = write_smoke_evidence(valid)
        samples["valid_with_smoke"] = validate_project(valid, smoke_json=smoke_path)
        if not samples["valid_with_smoke"].get("verified"):
            errors.append("Valid shared-runtime opt-in fixture with smoke evidence did not become verified.")
        if samples["valid_with_smoke"].get("capability_state") != "project_gui_verified_with_shared_runtime":
            errors.append("Valid smoke evidence must promote capability_state to project_gui_verified_with_shared_runtime.")

        bad_smoke = make_valid_fixture(root, "pyside6-shared-optin-bad-smoke")
        fixtures.append(bad_smoke)
        bad_smoke_path = write_smoke_evidence(bad_smoke, import_only_verified=False, blockers=["import_only_failed:fixture"])
        samples["bad_smoke"] = validate_project(bad_smoke, smoke_json=bad_smoke_path)
        if samples["bad_smoke"].get("ok"):
            errors.append("Fixture with failed shared-runtime smoke evidence unexpectedly passed.")

        missing_contract = make_valid_fixture(root, "pyside6-shared-optin-missing-contract")
        fixtures.append(missing_contract)
        (missing_contract / RUNTIME_CONTRACT).unlink()
        samples["missing_contract"] = validate_project(missing_contract)
        if samples["missing_contract"]["ok"]:
            errors.append("Fixture without runtime contract unexpectedly passed.")

        shared_with_dependency = make_valid_fixture(root, "pyside6-shared-optin-forbidden-dependency")
        fixtures.append(shared_with_dependency)
        write(shared_with_dependency / "requirements-gui.txt", "PySide6\n")
        samples["shared_with_dependency"] = validate_project(shared_with_dependency)
        if samples["shared_with_dependency"]["ok"]:
            errors.append("Shared-runtime fixture with project-local PySide6 dependency unexpectedly passed.")

        override_valid = make_valid_fixture(root, "pyside6-override-valid")
        fixtures.append(override_valid)
        add_project_local_override(override_valid, kind="requirements")
        samples["override_valid"] = validate_project(override_valid)
        if not samples["override_valid"]["ok"]:
            errors.append("Valid project-local override fixture did not pass: " + "; ".join(samples["override_valid"]["errors"]))

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
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "self-test",
        "ok": not errors,
        "root": str(root),
        "samples": samples,
        "errors": errors,
        "warnings": warnings,
        "info": ["Self-test validates shared-runtime default and project-local override behavior for consumer-project PySide6 opt-in checks."],
        "counts": {
            "samples": len(samples),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check consumer-project PySide6 shared-runtime opt-in evidence or self-test the checker contract.")
    parser.add_argument("--root", default=".", help="Repository root for self-test artifacts.")
    parser.add_argument("--project-root", help="Consumer project root to validate. If omitted, run checker self-test fixtures.")
    parser.add_argument("--allow-duplicate-dependency-surfaces", action="store_true", help="Allow duplicated PySide6 override dependency surfaces after human review.")
    parser.add_argument("--smoke-json", help="Optional import-only shared-runtime smoke evidence JSON from tools/gui/check_pyside6_env.py.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.project_root:
        payload = validate_project(
            Path(args.project_root),
            allow_duplicate_dependency_surfaces=args.allow_duplicate_dependency_surfaces,
            smoke_json=Path(args.smoke_json) if args.smoke_json else None,
        )
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
