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
        self.assertEqual(preview["runtime_mode"], "shared")
        self.assertEqual(preview["dependency_style"], "pyproject-extra")
        self.assertEqual(preview["blockers"], [])
        self.assertFalse(any(item["path"] in {"pyproject.toml", "requirements-gui.txt"} for item in preview["planned_file_changes"]))
        apply = payload["apply_sample"]
        self.assertEqual(apply["mode"], "apply")
        self.assertTrue(apply["apply_mode"])
        self.assertEqual(apply["runtime_mode"], "shared")
        self.assertEqual(apply["dependency_style"], "requirements")
        self.assertEqual(apply["rollback_note"], "docs/pyside6_gui_rollback.md")
        self.assertTrue(any(item["path"] == "tools/gui/pyside6_runtime_contract.json" for item in apply["applied_file_changes"]))
        self.assertFalse((Path(apply["project_root"]) / "requirements-gui.txt").exists())
        override = payload["override_sample"]
        self.assertEqual(override["runtime_mode"], "project-local-override")
        self.assertTrue(any(item["path"] == "requirements-gui.txt" for item in override["applied_file_changes"]))
        fail_closed = payload["fail_closed_sample"]
        self.assertFalse(fail_closed["ok"])
        self.assertTrue(any(item["code"] == "unsafe_project_root" for item in fail_closed["blockers"]))
        missing_runtime = payload["missing_runtime_sample"]
        self.assertFalse(missing_runtime["ok"])
        self.assertTrue(any(item["code"] == "shared_runtime_missing" for item in missing_runtime["blockers"]))

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
