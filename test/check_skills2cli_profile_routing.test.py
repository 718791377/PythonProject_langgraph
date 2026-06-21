import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_skills2cli_profile_routing.py"


class Skills2CliProfileRoutingCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_registry(self, root: Path) -> Path:
        destination = root / "tools" / "skill_sources" / "plugin-modules" / "references"
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / "profiles.json"
        shutil.copy2(REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json", target)
        return target

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_passes_for_repository_registry(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertGreaterEqual(payload["counts"]["scenario_profiles"], 6)

    def test_repository_checker_reports_profile_suggest_matrix(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        matrix = payload["profile_suggest_rerank_contract"]["matrix"]
        names = {item["name"] for item in matrix}

        self.assertIn("market-research-paper-report", names)
        self.assertIn("creative-content-brand-assets", names)
        self.assertIn("pyside6-gui-packaging", names)
        self.assertIn("explicit-full-zh", names)
        self.assertTrue(all(item["ok"] for item in matrix))
        explicit_zh = next(item for item in matrix if item["name"] == "explicit-full-zh")
        self.assertEqual(explicit_zh["selected_profile"], "full")
        ordinary = [item for item in matrix if not item["name"].startswith("explicit-full")]
        self.assertTrue(all(item["selected_profile"] != "full" for item in ordinary))

    def test_fails_when_known_plugin_is_only_full_without_allowlist(self) -> None:
        root = self.make_root("only-full-plugin")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        for profile, entry in payload["modules"].items():
            if profile == "full":
                continue
            entry["plugins"] = [plugin for plugin in entry.get("plugins", []) if plugin != "Expo"]
            entry["plugin_hints"] = [plugin for plugin in entry.get("plugin_hints", []) if plugin != "Expo"]
            if isinstance(entry.get("hard_load"), dict):
                entry["hard_load"]["enable_plugins"] = [plugin for plugin in entry["hard_load"].get("enable_plugins", []) if plugin != "Expo"]
            for task in entry.get("task_modules", {}).values():
                task["plugin_hints"] = [plugin for plugin in task.get("plugin_hints", []) if plugin != "Expo"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("Expo" in error and "full" in error for error in parsed["errors"]))

    def test_fails_when_scenario_target_is_missing(self) -> None:
        root = self.make_root("missing-scenario-target")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        payload["scenario_profiles"]["web-product"]["target_profile"] = "missing-profile"
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("web-product" in error and "missing-profile" in error for error in parsed["errors"]))

    def test_fails_when_task_module_missing_routing_explanation(self) -> None:
        root = self.make_root("missing-task-routing")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["modules"]["web-saas"]["task_modules"]["mobile-app"]["routing_explanation"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("web-saas.mobile-app" in error for error in parsed["errors"]))

    def test_fails_when_profile_lacks_scene_description_alias(self) -> None:
        root = self.make_root("missing-scene-description")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["modules"]["core-dev"]["scene_description"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("core-dev" in error and "scene_description" in error for error in parsed["errors"]))


if __name__ == "__main__":
    unittest.main()
