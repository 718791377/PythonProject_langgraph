import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_plugin_modules_skill.py"


class PluginModulesSkillCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_skill_source(self, root: Path) -> None:
        destination = root / "tools" / "skill_sources" / "plugin-modules"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(REPO_ROOT / "tools" / "skill_sources" / "plugin-modules", destination)
        shutil.copy2(REPO_ROOT / "tools" / "install-plugin-modules-skill.ps1", root / "tools" / "install-plugin-modules-skill.ps1")

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_passes_for_repository_skill_source(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_when_profiles_json_is_missing_required_module(self) -> None:
        root = self.make_root("plugin-modules-missing-module")
        self.copy_skill_source(root)
        profiles_path = root / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["modules"]["customer-comms"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("customer-comms" in error for error in parsed["errors"]))

    def test_fails_when_apply_gate_is_removed(self) -> None:
        root = self.make_root("plugin-modules-no-apply")
        self.copy_skill_source(root)
        script_path = root / "tools" / "skill_sources" / "plugin-modules" / "scripts" / "set_plugin_profile.ps1"
        script_path.write_text(
            script_path.read_text(encoding="utf-8").replace("[switch]$Apply", "[switch]$ReallyApply"),
            encoding="utf-8",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("apply_gate" in error for error in parsed["errors"]))


if __name__ == "__main__":
    unittest.main()
