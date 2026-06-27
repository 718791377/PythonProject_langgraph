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
        self.assertIn("core-dev-skills-budget-warning", names)
        self.assertTrue(all(item["ok"] for item in matrix))
        budget = next(item for item in matrix if item["name"] == "core-dev-skills-budget-warning")
        self.assertEqual(budget["selected_profile"], "core-dev")
        self.assertEqual(budget["scenario_profile"], "skills-budget-triage")
        self.assertIn("skills-budget-triage", budget["task_modules"])
        self.assertTrue(budget["budget_warning_intent"]["detected"])
        explicit_zh = next(item for item in matrix if item["name"] == "explicit-full-zh")
        self.assertEqual(explicit_zh["selected_profile"], "full")
        ordinary = [item for item in matrix if not item["name"].startswith("explicit-full")]
        self.assertTrue(all(item["selected_profile"] != "full" for item in ordinary))
        self.assertTrue(
            all(
                any(candidate["target_profile"] == "full" and candidate["reason"] == "explicit_full_request_required" for candidate in item["excluded_candidates"])
                for item in ordinary
            )
        )
        artifact_names = {item["artifact"] for item in payload["installed_artifact_drift_report"]}
        self.assertEqual(
            {"skills2cli.py", "skills2cli_profile_registry_contract.py", "profiles.json"},
            artifact_names,
        )
        self.assertEqual(
            set(payload["orthogonal_scope_fields"]),
            {"routing_scope", "activation_scope", "governance_scope", "evidence_scope"},
        )

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

    def test_fails_when_task_module_missing_qualified_name(self) -> None:
        root = self.make_root("missing-task-qualified-name")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["modules"]["web-saas"]["task_modules"]["mobile-app"]["qualified_name"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("web-saas.mobile-app" in error and "qualified_name" in error for error in parsed["errors"]))

    def test_fails_when_orthogonal_scope_mapping_is_wrong(self) -> None:
        root = self.make_root("wrong-orthogonal-scope")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        payload["modules"]["web-saas"]["activation_scope"] = "soft-load"
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("web-saas" in error and "activation_scope" in error for error in parsed["errors"]))

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

    def test_fails_when_budget_triage_task_module_missing(self) -> None:
        root = self.make_root("missing-budget-task")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["modules"]["core-dev"]["task_modules"]["skills-budget-triage"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("core-dev.skills-budget-triage" in error for error in parsed["errors"]))

    def test_fails_when_budget_scenario_targets_non_core_dev(self) -> None:
        root = self.make_root("wrong-budget-target")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        payload["scenario_profiles"]["skills-budget-triage"]["target_profile"] = "web-saas"
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("skills-budget-triage" in error and "core-dev" in error for error in parsed["errors"]))

    def test_fails_when_known_plugin_missing_config_id_mapping(self) -> None:
        root = self.make_root("missing-plugin-config-id")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        del payload["plugin_config_ids"]["GitHub"]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("GitHub" in error and "plugin_config_ids" in error for error in parsed["errors"]))

    def test_fails_when_managed_extra_config_id_missing(self) -> None:
        root = self.make_root("missing-managed-extra")
        profiles_path = self.copy_registry(root)
        payload = json.loads(profiles_path.read_text(encoding="utf-8"))
        payload["managed_extra_plugin_config_ids"] = [
            item for item in payload.get("managed_extra_plugin_config_ids", []) if item != "superpowers@openai-curated"
        ]
        profiles_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        parsed = json.loads(result.stdout)
        self.assertTrue(any("managed_extra_plugin_config_ids" in error and "superpowers@openai-curated" in error for error in parsed["errors"]))

    def test_set_plugin_profile_core_dev_uses_real_config_ids_without_display_names(self) -> None:
        root = self.make_root("set-plugin-profile-preview")
        codex_home = root / "codex-home"
        config_path = codex_home / "config.toml"
        script = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "scripts" / "set_plugin_profile.ps1"
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-File",
                str(script),
                "core-dev",
                "-CodexHome",
                str(codex_home),
                "-ConfigPath",
                str(config_path),
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
        targets = {item["plugin"]: item["enabled"] for item in payload["target_plugins"]}

        for plugin in ["browser@openai-bundled", "chrome@openai-bundled", "github@openai-curated"]:
            self.assertIs(targets.get(plugin), True)
        for plugin in ["vercel@openai-curated", "figma@openai-curated", "superpowers@openai-curated", "computer-use@openai-bundled"]:
            self.assertIs(targets.get(plugin), False)
        self.assertFalse(any("@" not in plugin for plugin in targets), sorted(plugin for plugin in targets if "@" not in plugin))


if __name__ == "__main__":
    unittest.main()
