import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_project_opt_in_contract.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_pyside6_project_opt_in_contract import (  # noqa: E402
    RUNTIME_CONTRACT,
    add_project_local_override,
    make_valid_fixture,
)


class PySide6ProjectOptInContractTest(unittest.TestCase):
    maxDiff = None

    def make_project(self, name: str) -> Path:
        project = make_valid_fixture(REPO_ROOT, f"{name}-{uuid.uuid4().hex[:8]}")
        self.addCleanup(lambda: shutil.rmtree(project, ignore_errors=True))
        return project

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

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
        self.assertIn("override_valid", payload["samples"])

    def test_valid_shared_runtime_fixture_passes_without_project_dependency(self) -> None:
        project = self.make_project("pyside6-project-shared-valid")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability_state"], "project_gui_template_ready")
        self.assertEqual(payload["runtime_contract"]["runtime_mode"], "shared")
        self.assertEqual(payload["dependency_surfaces"], [])
        self.assertFalse(payload["verified"])
        self.assertFalse(payload["packaged"])

    def test_missing_runtime_contract_fails(self) -> None:
        project = self.make_project("pyside6-project-missing-contract")
        (project / RUNTIME_CONTRACT).unlink()
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("runtime contract" in error.lower() for error in payload["errors"]))

    def test_shared_runtime_with_project_dependency_fails(self) -> None:
        project = self.make_project("pyside6-project-forbidden-dependency")
        self.write_file(project, "requirements-gui.txt", "PySide6\n")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("must not declare PySide6" in error for error in payload["errors"]))

    def test_project_local_override_with_dependency_passes(self) -> None:
        project = self.make_project("pyside6-project-override")
        add_project_local_override(project, kind="requirements")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability_state"], "project_local_override_ready")
        self.assertEqual(payload["dependency_surfaces"][0]["kind"], "requirements")
        self.assertEqual(payload["lockfile_evidence"][0]["manager"], "pip")
        self.assertFalse(payload["lockfile_evidence"][0]["env_ready_inferred_from_lockfile"])

    def test_poetry_override_requires_lockfile_evidence(self) -> None:
        project = self.make_project("pyside6-project-poetry-missing-lock")
        add_project_local_override(project, kind="poetry", include_lockfile=False)
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("poetry.lock is missing" in error for error in payload["errors"]))

    def test_duplicate_override_dependency_surface_fails_by_default(self) -> None:
        project = self.make_project("pyside6-project-duplicate-dependency")
        add_project_local_override(project, kind="requirements")
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

    def test_duplicate_override_dependency_surface_can_be_allowed_after_review(self) -> None:
        project = self.make_project("pyside6-project-duplicate-allowed")
        add_project_local_override(project, kind="requirements")
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
        project = self.make_project("pyside6-project-visible-smoke")
        self.write_file(project, "tests/test_gui_import.py", "def test_bad(window):\n    window.show()\n")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("must not launch a visible GUI" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
