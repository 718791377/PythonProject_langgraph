import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_gui_skill_contract.py"
SKILL_PATH = REPO_ROOT / ".codex" / "skills" / "pyside6-gui" / "SKILL.md"


class PySide6GuiSkillContractTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_skill(self, root: Path) -> Path:
        destination = root / ".codex" / "skills" / "pyside6-gui"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILL_PATH, destination / "SKILL.md")
        return destination / "SKILL.md"

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_skill_passes(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["frontmatter"]["name"], "pyside6-gui")
        self.assertLessEqual(len(payload["frontmatter"]["description"]), 180)

    def test_missing_skill_fails(self) -> None:
        root = self.make_root("pyside6-skill-missing")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("Missing PySide6 GUI skill" in error for error in payload["errors"]))

    def test_invalid_frontmatter_fails(self) -> None:
        root = self.make_root("pyside6-skill-frontmatter")
        skill = self.copy_skill(root)
        skill.write_text(skill.read_text(encoding="utf-8").replace("name: pyside6-gui", "name: wrong"), encoding="utf-8")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("frontmatter key name" in error for error in payload["errors"]))

    def test_global_install_guidance_fails(self) -> None:
        root = self.make_root("pyside6-skill-global")
        skill = self.copy_skill(root)
        skill.write_text(skill.read_text(encoding="utf-8") + "\npip install --user PySide6\n", encoding="utf-8")
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("pip install --user" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
