import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_gui_preview_helper_contract.py"
HELPER_PATH = REPO_ROOT / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1"


class PySide6GuiPreviewHelperContractTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_helper(self, root: Path) -> None:
        destination = root / "tools" / "pyside6_gui_helpers"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HELPER_PATH, destination / "ensure-pyside6-gui.ps1")
        template_destination = root / "tools" / "pyside6_gui_templates"
        if template_destination.exists():
            shutil.rmtree(template_destination)
        shutil.copytree(REPO_ROOT / "tools" / "pyside6_gui_templates", template_destination)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_preview_and_apply_helper_passes(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        preview = payload["preview_sample"]
        self.assertEqual(preview["mode"], "preview")
        self.assertFalse(preview["apply_mode"])
        self.assertEqual(preview["dependency_style"], "pyproject-extra")
        self.assertEqual(preview["blockers"], [])
        apply = payload["apply_sample"]
        self.assertEqual(apply["mode"], "apply")
        self.assertTrue(apply["apply_mode"])
        self.assertEqual(apply["dependency_style"], "requirements")
        self.assertEqual(apply["rollback_note"], "docs/pyside6_gui_rollback.md")
        self.assertTrue(any(item["path"] == "requirements-gui.txt" for item in apply["applied_file_changes"]))
        fail_closed = payload["fail_closed_sample"]
        self.assertFalse(fail_closed["ok"])
        self.assertTrue(any(item["code"] == "unsafe_project_root" for item in fail_closed["blockers"]))
        uv_sample = payload["uv_sample"]
        self.assertEqual(uv_sample["package_manager"], "uv")
        self.assertEqual(uv_sample["dependency_style"], "group")
        self.assertEqual(uv_sample["package_manager_command_evidence"]["project_native_dependency_command"], "uv add --group gui PySide6")
        self.assertEqual(uv_sample["package_manager_command_evidence"]["install_command"], "uv sync --group gui")
        self.assertEqual(uv_sample["package_manager_command_evidence"]["lockfile_update_command"], "uv lock")
        poetry_sample = payload["poetry_sample"]
        self.assertEqual(poetry_sample["package_manager"], "poetry")
        self.assertEqual(poetry_sample["dependency_style"], "pyproject-extra")
        self.assertEqual(poetry_sample["package_manager_command_evidence"]["project_native_dependency_command"], "poetry add --optional PySide6")
        self.assertEqual(poetry_sample["package_manager_command_evidence"]["install_command"], "poetry install --extras gui")
        self.assertEqual(poetry_sample["package_manager_command_evidence"]["lockfile_update_command"], "poetry lock")

    def test_missing_preview_helper_fails(self) -> None:
        root = self.make_root("pyside6-preview-missing")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("ensure-pyside6-gui.ps1" in error for error in payload["errors"]))

    def test_helper_must_not_include_global_write_launch_or_remote_commands(self) -> None:
        root = self.make_root("pyside6-preview-write")
        self.copy_helper(root)
        helper = root / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1"
        helper.write_text(helper.read_text(encoding="utf-8") + "\nNew-Item -ItemType File marker.txt\nStart-Process notepad.exe\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("New-Item" in error for error in payload["errors"]))
        self.assertTrue(any("Start-Process" in error for error in payload["errors"]))

    def test_helper_requires_structured_fields(self) -> None:
        root = self.make_root("pyside6-preview-fields")
        self.copy_helper(root)
        helper = root / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1"
        helper.write_text(helper.read_text(encoding="utf-8").replace("applied_file_changes", "applied_files"), encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("applied_file_changes" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
