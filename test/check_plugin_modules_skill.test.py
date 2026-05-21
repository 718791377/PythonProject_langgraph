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
        for relative in [
            ".codex/skills/pyside6-gui/SKILL.md",
            "tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1",
            "tools/pyside6_gui_templates/README.md",
            "tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template",
        ]:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / relative, target)

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

    def test_pyside6_gui_module_is_repo_local_soft_load_only(self) -> None:
        profiles_path = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        module = payload["modules"]["pyside6-gui"]

        self.assertEqual(module["plugins"], [])
        self.assertEqual(module["hard_load"]["enable_plugins"], [])
        self.assertFalse(module["hard_load"]["disable_other_known_plugins"])
        self.assertEqual(
            module["soft_load"]["skill_doc_hints"],
            [
                "repo:.codex/skills/pyside6-gui/SKILL.md",
                "repo:tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1",
                "repo:tools/pyside6_gui_templates/README.md",
                "repo:tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template",
            ],
        )

    def test_fails_when_pyside6_repo_hint_is_removed(self) -> None:
        root = self.make_root("plugin-modules-missing-pyside6-hint")
        self.copy_skill_source(root)
        profiles_path = root / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        hints = payload["modules"]["pyside6-gui"]["soft_load"]["skill_doc_hints"]
        hints.remove("repo:.codex/skills/pyside6-gui/SKILL.md")
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("repo:.codex/skills/pyside6-gui/SKILL.md" in error for error in parsed["errors"]))

    def test_fails_when_pyside6_hard_load_enables_plugins(self) -> None:
        root = self.make_root("plugin-modules-pyside6-hard-load-plugin")
        self.copy_skill_source(root)
        profiles_path = root / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        payload["modules"]["pyside6-gui"]["hard_load"]["enable_plugins"] = ["Browser"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("hard_load.enable_plugins" in error for error in parsed["errors"]))

    @unittest.skipUnless(shutil.which("powershell") or shutil.which("pwsh"), "PowerShell is required for plugin module loader tests.")
    def test_load_module_resolves_pyside6_repo_local_docs(self) -> None:
        shell = shutil.which("powershell") or shutil.which("pwsh")
        script = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "scripts" / "load_module.ps1"
        result = subprocess.run(
            [
                shell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "pyside6-gui",
                "-RepoRoot",
                str(REPO_ROOT),
                "-Json",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["module"], "pyside6-gui")
        self.assertEqual(payload["plugins"], [])
        self.assertEqual(payload["missing_hints"], [])
        self.assertEqual(Path(payload["repo_root"]), REPO_ROOT)
        skill_docs = [Path(item) for item in payload["skill_docs"]]
        self.assertIn(REPO_ROOT / ".codex" / "skills" / "pyside6-gui" / "SKILL.md", skill_docs)
        self.assertIn(REPO_ROOT / "tools" / "pyside6_gui_helpers" / "ensure-pyside6-gui.ps1", skill_docs)


if __name__ == "__main__":
    unittest.main()
