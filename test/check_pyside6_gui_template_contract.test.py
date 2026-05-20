import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_gui_template_contract.py"
TEMPLATE_ROOT = REPO_ROOT / "tools" / "pyside6_gui_templates"


class PySide6GuiTemplateContractTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_templates(self, root: Path) -> None:
        destination = root / "tools" / "pyside6_gui_templates"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(TEMPLATE_ROOT, destination)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_templates_pass(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["required_files"], 9)

    def test_missing_template_file_fails(self) -> None:
        root = self.make_root("pyside6-template-missing")
        self.copy_templates(root)
        (root / "tools" / "pyside6_gui_templates" / "tools" / "gui" / "check_pyside6_env.py.template").unlink()

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("check_pyside6_env.py.template" in error for error in payload["errors"]))

    def test_import_smoke_template_must_not_show_gui(self) -> None:
        root = self.make_root("pyside6-template-visible-gui")
        self.copy_templates(root)
        path = root / "tools" / "pyside6_gui_templates" / "tests" / "test_gui_import.py.template"
        path.write_text(path.read_text(encoding="utf-8") + "\napp.exec()\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("Import smoke template" in error for error in payload["errors"]))

    def test_run_helper_must_not_install_packages(self) -> None:
        root = self.make_root("pyside6-template-install")
        self.copy_templates(root)
        path = root / "tools" / "pyside6_gui_templates" / "tools" / "gui" / "run_gui.ps1.template"
        path.write_text(path.read_text(encoding="utf-8") + "\npip install PySide6\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("pip install" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
