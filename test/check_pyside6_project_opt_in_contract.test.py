import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_project_opt_in_contract.py"


class PySide6ProjectOptInContractTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def make_valid_project(self, name: str) -> Path:
        root = self.make_root(name)
        self.write_file(root, "README.md", "# PySide6 fixture\n")
        self.write_file(root, "requirements-gui.txt", "PySide6\n")
        self.write_file(root, "src/sample_gui/__init__.py", '"""Sample GUI package."""\n')
        self.write_file(
            root,
            "src/sample_gui/app.py",
            "from PySide6.QtWidgets import QApplication\n"
            "from .main_window import MainWindow\n\n"
            "def build_app(argv=None):\n"
            "    return QApplication(list(argv or []))\n",
        )
        self.write_file(
            root,
            "src/sample_gui/main_window.py",
            "from PySide6.QtWidgets import QMainWindow\n\n"
            "class ServiceAdapter: pass\n"
            "class WorkerAdapter: pass\n"
            "class ConfigDataDirectoryAdapter: pass\n\n"
            "class MainWindow(QMainWindow): pass\n",
        )
        self.write_file(
            root,
            "tests/test_gui_import.py",
            "import importlib\n\n"
            "def test_gui_package_imports_without_visible_window():\n"
            "    module = importlib.import_module('sample_gui.main_window')\n"
            "    assert hasattr(module, 'MainWindow')\n",
        )
        self.write_file(
            root,
            "tools/gui/run_gui.ps1",
            "$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)\n"
            "$env:PYTHONPATH = Join-Path $ProjectRoot 'src'\n"
            "& (Join-Path $ProjectRoot '.venv/Scripts/python.exe') -m sample_gui.app\n",
        )
        self.write_file(
            root,
            "tools/gui/check_pyside6_env.py",
            "from PySide6.QtWidgets import QApplication\nprint('PySide6 ok')\n",
        )
        self.write_file(
            root,
            "docs/pyside6_gui_rollback.md",
            "# PySide6 GUI rollback\n\nRemove the PySide6 dependency and generated GUI files.\n",
        )
        return root

    def make_uv_project(self, name: str) -> Path:
        project = self.make_valid_project(name)
        (project / "requirements-gui.txt").unlink()
        self.write_file(
            project,
            "pyproject.toml",
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n\n"
            "[dependency-groups]\ngui = [\"PySide6\"]\n",
        )
        self.write_file(project, "uv.lock", "# fixture uv lockfile\n")
        return project

    def make_poetry_project(self, name: str, *, include_lockfile: bool = True) -> Path:
        project = self.make_valid_project(name)
        (project / "requirements-gui.txt").unlink()
        self.write_file(
            project,
            "pyproject.toml",
            "[tool.poetry]\n"
            "name = \"sample\"\n"
            "version = \"0.1.0\"\n"
            "description = \"fixture\"\n"
            "authors = []\n\n"
            "[tool.poetry.group.gui.dependencies]\n"
            "PySide6 = \"*\"\n",
        )
        if include_lockfile:
            self.write_file(project, "poetry.lock", "# fixture poetry lockfile\n")
        return project

    def run_check(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args, "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_self_test_passes(self) -> None:
        result = self.run_check("--root", str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "self-test")
        self.assertEqual(payload["check_name"], "pyside6_project_opt_in_contract")
        self.assertIn("valid", payload["samples"])

    def test_valid_generated_fixture_passes(self) -> None:
        project = self.make_valid_project("pyside6-project-valid")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "project")
        self.assertEqual(payload["capability_state"], "template_ready")
        self.assertFalse(payload["verified"])
        self.assertFalse(payload["packaged"])
        self.assertEqual(payload["lockfile_evidence"][0]["manager"], "pip")
        self.assertFalse(payload["lockfile_evidence"][0]["env_ready_inferred_from_lockfile"])

    def test_uv_dependency_group_reports_lockfile_evidence(self) -> None:
        project = self.make_uv_project("pyside6-project-uv")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["dependency_surfaces"][0]["kind"], "dependency-group")
        self.assertEqual(payload["lockfile_evidence"][0]["manager"], "uv")
        self.assertEqual(payload["lockfile_evidence"][0]["lockfile_path"], "uv.lock")
        self.assertTrue(payload["lockfile_evidence"][0]["lockfile_present"])
        self.assertFalse(payload["lockfile_evidence"][0]["env_ready_inferred_from_lockfile"])

    def test_poetry_group_requires_lockfile_evidence(self) -> None:
        project = self.make_poetry_project("pyside6-project-poetry")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["dependency_surfaces"][0]["kind"], "poetry-group")
        self.assertEqual(payload["lockfile_evidence"][0]["manager"], "poetry")
        self.assertEqual(payload["lockfile_evidence"][0]["lockfile_path"], "poetry.lock")
        self.assertTrue(payload["lockfile_evidence"][0]["lockfile_present"])

    def test_poetry_group_without_lockfile_fails(self) -> None:
        project = self.make_poetry_project("pyside6-project-poetry-missing-lock", include_lockfile=False)
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("poetry.lock is missing" in error for error in payload["errors"]))

    def test_missing_dependency_fails(self) -> None:
        project = self.make_valid_project("pyside6-project-missing-dependency")
        (project / "requirements-gui.txt").unlink()
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("No project-local PySide6 dependency declaration" in error for error in payload["errors"]))

    def test_duplicate_dependency_surface_fails_by_default(self) -> None:
        project = self.make_valid_project("pyside6-project-duplicate-dependency")
        self.write_file(
            project,
            "pyproject.toml",
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n\n"
            "[project.optional-dependencies]\ngui = [\"PySide6\"]\n",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("multiple dependency surfaces" in error for error in payload["errors"]))

    def test_duplicate_dependency_surface_can_be_allowed_after_review(self) -> None:
        project = self.make_valid_project("pyside6-project-duplicate-allowed")
        self.write_file(
            project,
            "pyproject.toml",
            "[project]\nname = \"sample\"\nversion = \"0.1.0\"\n\n"
            "[project.optional-dependencies]\ngui = [\"PySide6\"]\n",
        )
        result = self.run_check(
            "--root",
            str(REPO_ROOT),
            "--project-root",
            str(project),
            "--allow-duplicate-dependency-surfaces",
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["dependency_surfaces"], 2)

    def test_visible_gui_smoke_test_fails(self) -> None:
        project = self.make_valid_project("pyside6-project-visible-smoke")
        self.write_file(project, "tests/test_gui_import.py", "def test_bad(window):\n    window.show()\n")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("must not launch a visible GUI" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
