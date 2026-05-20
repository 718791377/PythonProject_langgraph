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

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_preview_helper_passes(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        sample = payload["preview_sample"]
        self.assertEqual(sample["mode"], "preview")
        self.assertEqual(sample["dependency_style"], "pyproject-extra")
        self.assertEqual(sample["blockers"], [])

    def test_missing_preview_helper_fails(self) -> None:
        root = self.make_root("pyside6-preview-missing")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("ensure-pyside6-gui.ps1" in error for error in payload["errors"]))

    def test_preview_helper_must_not_write_or_launch(self) -> None:
        root = self.make_root("pyside6-preview-write")
        self.copy_helper(root)
        helper = root / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1"
        helper.write_text(helper.read_text(encoding="utf-8") + "\nNew-Item -ItemType File marker.txt\nStart-Process notepad.exe\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("New-Item" in error for error in payload["errors"]))
        self.assertTrue(any("Start-Process" in error for error in payload["errors"]))

    def test_preview_helper_requires_structured_fields(self) -> None:
        root = self.make_root("pyside6-preview-fields")
        self.copy_helper(root)
        helper = root / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1"
        helper.write_text(helper.read_text(encoding="utf-8").replace("planned_file_changes", "planned_files"), encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("planned_file_changes" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
