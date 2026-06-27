import json
import shutil
import sqlite3
import subprocess
import sys
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "skills2cli.py"


class Skills2CliTest(unittest.TestCase):
    maxDiff = None

    def make_workspace(self, name: str) -> tuple[Path, Path]:
        base = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        repo = base / "repo"
        codex_home = base / "codex-home"
        repo.mkdir(parents=True, exist_ok=True)
        codex_home.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return repo, codex_home

    def write_skill(self, root: Path, relative_dir: str, *, name: str, description: str, body: str = "Body") -> Path:
        skill_dir = root / relative_dir
        skill_dir.mkdir(parents=True, exist_ok=True)
        path = skill_dir / "SKILL.md"
        path.write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n{body}\n",
            encoding="utf-8",
        )
        return path

    def run_cli(self, *args: str, check: bool = True) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if check and completed.returncode != 0:
            self.fail(completed.stdout + "\n" + completed.stderr)
        return json.loads(completed.stdout)

    def test_index_and_search_use_compact_sanitized_output(self) -> None:
        repo, codex_home = self.make_workspace("compact")
        long_description = "Browser helper " + ("very-long-description " * 40)
        self.write_skill(repo / ".codex" / "skills", "browser-helper", name="browser-helper", description=long_description, body="FULL BODY SHOULD NOT APPEAR")
        self.write_skill(codex_home / "plugins" / "cache", "plugin/pkg/hash/skills/private", name="plugin-private", description=r"Use C:\Users\lenovo\.codex\secret with api_key=sk-test-secret-value for demos")

        payload = self.run_cli("index", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["command"], "index")
        self.assertEqual(payload["total"], 2)
        self.assertTrue(payload["safety"]["compact_output"])
        self.assertFalse(payload["safety"]["raw_paths_retained"])
        self.assertNotIn("FULL BODY SHOULD NOT APPEAR", serialized)
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-secret-value", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)
        self.assertLessEqual(max(len(item["description_summary"]) for item in payload["skills"]), 160)
        self.assertTrue(all("description_hash" in item for item in payload["skills"]))

        search = self.run_cli("search", "browser", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        self.assertEqual(search["command"], "search")
        self.assertGreaterEqual(search["total_matches"], 1)
        self.assertNotIn("FULL BODY SHOULD NOT APPEAR", json.dumps(search, ensure_ascii=False))

    def test_show_default_does_not_dump_full_body(self) -> None:
        repo, codex_home = self.make_workspace("show")
        self.write_skill(repo / ".codex" / "skills", "repo-skill", name="repo-skill", description="Repository skill.", body="SENSITIVE BODY CONTENT")

        payload = self.run_cli("show", "repo:repo-skill", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertTrue(payload["ok"])
        self.assertFalse(payload["skill"]["full_body_included"])
        self.assertNotIn("body", payload["skill"])
        self.assertNotIn("SENSITIVE BODY CONTENT", serialized)

    def test_index_reports_codex_frontmatter_compatibility_limits(self) -> None:
        repo, codex_home = self.make_workspace("compat")
        long_name = "skill-" + ("very-long-" * 8)
        long_description = "D" * 1030
        self.write_skill(repo / ".codex" / "skills", "bad-skill", name=long_name, description=long_description)

        payload = self.run_cli("index", "--root", str(repo), "--codex-home", str(codex_home), "--json")

        self.assertEqual(payload["total"], 1)
        skill = payload["skills"][0]
        self.assertFalse(skill["codex_frontmatter_compatible"])
        self.assertIn("name_too_long", skill["codex_frontmatter_errors"])
        self.assertIn("description_too_long", skill["codex_frontmatter_errors"])
        self.assertGreater(skill["name_length"], payload["safety"]["codex_frontmatter_name_limit"])
        self.assertGreater(skill["description_length"], payload["safety"]["codex_frontmatter_description_limit"])

    def test_bom_frontmatter_is_visible_but_reported_for_repair(self) -> None:
        repo, codex_home = self.make_workspace("bom")
        path = self.write_skill(repo / ".codex" / "skills", "bom-skill", name="bom-skill", description="Short.")
        path.write_text("\ufeff" + path.read_text(encoding="utf-8"), encoding="utf-8")

        payload = self.run_cli("show", "repo:bom-skill", "--root", str(repo), "--codex-home", str(codex_home), "--json")

        self.assertTrue(payload["ok"])
        skill = payload["skill"]
        self.assertTrue(skill["frontmatter_valid"])
        self.assertFalse(skill["codex_frontmatter_compatible"])
        self.assertIn("bom_present", skill["codex_frontmatter_errors"])

    def test_profile_suggest_is_preview_only_and_never_applies(self) -> None:
        payload = self.run_cli(
            "profile",
            "suggest",
            "--task",
            "Debug Chrome DevTools and CDP browser automation warnings",
            "--json",
        )

        self.assertEqual(payload["command"], "profile suggest")
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["edits_plugin_cache"])
        self.assertFalse(payload["profile_apply_performed"])
        self.assertTrue(payload["approval_required_for_apply"])
        self.assertIn("soft_hard_boundary", payload)
        self.assertEqual(payload["routing_evidence"]["surface_type"], "skill_profile_suggestion")
        self.assertFalse(payload["routing_evidence"]["native_subagent_evidence"])
        self.assertFalse(payload["routing_evidence"]["expert_evidence"])
        self.assertTrue(payload["routing_evidence"]["separate_native_agent_required_for_expert_claims"])
        self.assertTrue(any(item.get("scenario_profile") == "browser-automation" and item["target_profile"] == "core-dev" for item in payload["suggestions"]))

    def test_profile_suggest_returns_explainable_web_saas_task_modules(self) -> None:
        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Expo mobile build and Sentry observability",
            "--json",
        )

        self.assertEqual(payload["selected_profile"]["target_profile"], "web-saas")
        self.assertNotEqual(payload["selected_profile"]["target_profile"], "full")
        task_modules = {item["task_module"] for item in payload["task_modules"]}
        self.assertIn("mobile-app", task_modules)
        self.assertIn("observability", task_modules)
        self.assertIn("Expo", payload["selected_profile"]["plugin_hints"])
        self.assertTrue(payload["selected_profile"]["skill_doc_hints"])
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["profile_apply_performed"])
        self.assertTrue(payload["soft_load_commands"])
        self.assertIn("hard_load_preview_command", payload)

    def test_profile_suggest_uses_scene_description_compatibility_field(self) -> None:
        repo, codex_home = self.make_workspace("scene-description")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        payload = json.loads(registry_source.read_text(encoding="utf-8"))
        payload["scenario_profiles"]["web-product"]["scene_description"] = "orbital launch frontend"
        payload["scenario_profiles"]["web-product"].pop("scenario_description", None)
        payload["modules"]["web-saas"]["scene_description"] = "orbital launch deployment"
        payload["modules"]["web-saas"].pop("scenario_description", None)
        payload["modules"]["web-saas"]["task_modules"]["frontend-build"]["scene_description"] = "orbital launch ui"
        payload["modules"]["web-saas"]["task_modules"]["frontend-build"].pop("scenario_description", None)
        (registry_target / "profiles.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "orbital launch frontend",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertEqual(result["selected_profile"]["target_profile"], "web-saas")
        self.assertEqual(result["selected_profile"]["scenario_profile"], "web-product")
        self.assertIn("frontend-build", {item["task_module"] for item in result["task_modules"]})

    def test_profile_suggest_falls_back_to_legacy_scenario_description_field(self) -> None:
        repo, codex_home = self.make_workspace("legacy-scenario-description")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        payload = json.loads(registry_source.read_text(encoding="utf-8"))
        legacy_phrase = "spectral narwhal frontend"
        payload["scenario_profiles"]["web-product"]["scenario_description"] = legacy_phrase
        payload["scenario_profiles"]["web-product"].pop("scene_description", None)
        payload["modules"]["web-saas"]["scenario_description"] = legacy_phrase
        payload["modules"]["web-saas"].pop("scene_description", None)
        payload["modules"]["web-saas"]["task_modules"]["frontend-build"]["scenario_description"] = legacy_phrase
        payload["modules"]["web-saas"]["task_modules"]["frontend-build"].pop("scene_description", None)
        (registry_target / "profiles.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_cli(
            "profile",
            "suggest",
            "--query",
            legacy_phrase,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertEqual(result["selected_profile"]["target_profile"], "web-saas")
        self.assertEqual(result["selected_profile"]["scenario_profile"], "web-product")
        self.assertIn("frontend-build", {item["task_module"] for item in result["task_modules"]})

    def test_profile_suggest_penalizes_full_unless_explicit_troubleshooting(self) -> None:
        ordinary = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Fix GitLab CI and perform security review",
            "--json",
        )
        self.assertNotEqual(ordinary["selected_profile"]["target_profile"], "full")
        self.assertEqual(ordinary["selected_profile"]["target_profile"], "core-dev")
        self.assertNotEqual(ordinary["selected_profile"].get("scenario_profile"), "browser-automation")
        self.assertIn("code-review", {item["task_module"] for item in ordinary["task_modules"]})
        self.assertIn("security-review", {item["task_module"] for item in ordinary["task_modules"]})
        self.assertFalse(ordinary["explicit_full_request"])
        self.assertTrue(
            any(
                item["target_profile"] == "full" and item["reason"] == "explicit_full_request_required"
                for item in ordinary["excluded_candidates"]
            )
        )
        self.assertEqual(ordinary["selected_profile"]["eligibility"]["reason"], "eligible")
        self.assertIn("rank_factors", ordinary["selected_profile"])

        troubleshooting = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Troubleshoot all plugins with full profile broad discovery",
            "--json",
        )
        self.assertEqual(troubleshooting["selected_profile"]["target_profile"], "full")
        self.assertTrue(troubleshooting["explicit_full_request"])
        self.assertIn(
            troubleshooting["selected_profile"]["why_full_selected"],
            {"explicit_all_plugins", "explicit_broad_discovery", "explicit_missing_plugin_capability"},
        )

    def assert_advisory_only_profile_suggest(self, payload: dict) -> None:
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["edits_plugin_cache"])
        self.assertFalse(payload["profile_apply_performed"])
        self.assertTrue(payload["approval_required_for_apply"])
        self.assertIn("soft_hard_boundary", payload)
        self.assertEqual(payload["routing_evidence"]["surface_type"], "skill_profile_suggestion")
        self.assertFalse(payload["routing_evidence"]["native_subagent_evidence"])
        self.assertFalse(payload["routing_evidence"]["expert_evidence"])

    def test_profile_suggest_typical_query_matrix(self) -> None:
        cases = [
            (
                "Fix GitLab CI and perform security review",
                "core-dev",
                "repo-dev",
                {"code-review", "security-review"},
                False,
            ),
            (
                "Debug Chrome DevTools and CDP browser automation warnings",
                "core-dev",
                "browser-automation",
                {"browser-verification"},
                False,
            ),
            (
                "Codex compaction exceeded skills context budget additional skills removed",
                "core-dev",
                "skills-budget-triage",
                {"skills-budget-triage"},
                False,
            ),
            (
                "Expo mobile build and Sentry observability",
                "web-saas",
                "web-product",
                {"mobile-app", "observability"},
                False,
            ),
            (
                "Twilio WhatsApp customer notification",
                "customer-comms",
                "customer-messaging",
                {"messaging"},
                False,
            ),
            (
                "Fireflies meeting notes and HubSpot CRM follow-up",
                "company-ops",
                "ops-knowledge",
                {"meeting-intel", "crm-workflow"},
                False,
            ),
            (
                "PitchBook market research and Zotero paper citation report",
                "market-research",
                "research-analysis",
                {"paper-citation", "company-research"},
                False,
            ),
            (
                "Canva Figma presentation video brand assets",
                "creative-content",
                "design-media",
                {"brand-assets", "design-generation"},
                False,
            ),
            (
                "PySide6 Qt desktop GUI packaging preflight",
                "pyside6-gui",
                "repo-local-gui",
                {"qt-gui-dev", "gui-packaging-preflight"},
                False,
            ),
            (
                "Troubleshoot all plugins with full profile broad discovery",
                "full",
                "troubleshooting",
                set(),
                True,
            ),
            (
                "排障所有插件",
                "full",
                "troubleshooting",
                set(),
                True,
            ),
        ]
        for query, target_profile, scenario_profile, expected_tasks, explicit_full in cases:
            with self.subTest(query=query):
                payload = self.run_cli("profile", "suggest", "--query", query, "--json")
                self.assert_advisory_only_profile_suggest(payload)
                selected = payload["selected_profile"]
                self.assertEqual(selected["target_profile"], target_profile)
                self.assertEqual(selected["scenario_profile"], scenario_profile)
                task_modules = {item["task_module"] for item in payload["task_modules"]}
                self.assertTrue(expected_tasks.issubset(task_modules))
                if explicit_full:
                    self.assertEqual(selected["target_profile"], "full")
                    self.assertIsNotNone(payload["hard_load_preview_command"])
                    self.assertTrue(payload["explicit_full_request"])
                    self.assertTrue(selected["why_full_selected"])
                else:
                    self.assertNotEqual(selected["target_profile"], "full")
                    self.assertFalse(payload["explicit_full_request"])
                    self.assertTrue(
                        any(
                            item["target_profile"] == "full" and item["reason"] == "explicit_full_request_required"
                            for item in payload["excluded_candidates"]
                        )
                    )
                    for module in payload["task_modules"]:
                        self.assertEqual(module["qualified_name"], f'{selected["target_profile"]}.{module["task_module"]}')
                        self.assertEqual(module["identity"]["expected_qualified_name"], module["qualified_name"])

    def test_profile_suggest_preserves_scenario_to_canonical_mapping(self) -> None:
        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Twilio WhatsApp customer notification",
            "--json",
        )
        selected = payload["selected_profile"]
        self.assertEqual(selected["target_profile"], "customer-comms")
        self.assertEqual(selected["scenario_profile"], "customer-messaging")
        self.assertIn("messaging", {item["task_module"] for item in payload["task_modules"]})
        self.assertFalse(payload["routing_evidence"]["native_subagent_evidence"])

    def test_profile_suggest_routes_skills_budget_warning_to_core_dev_budget_triage(self) -> None:
        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.",
            "--json",
        )

        self.assert_advisory_only_profile_suggest(payload)
        self.assertTrue(payload["budget_warning_intent"]["detected"])
        self.assertEqual(payload["selected_profile"]["target_profile"], "core-dev")
        self.assertEqual(payload["selected_profile"]["scenario_profile"], "skills-budget-triage")
        self.assertIn("skills-budget-triage", {item["task_module"] for item in payload["task_modules"]})
        self.assertIn("core-dev.skills-budget-triage", {item["qualified_name"] for item in payload["task_modules"]})
        self.assertTrue(payload["selected_profile"]["rank_factors"]["budget_warning_intent"])
        self.assertNotEqual(payload["selected_profile"]["target_profile"], "market-research")
        self.assertNotEqual(payload["selected_profile"]["target_profile"], "web-saas")
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["edits_plugin_cache"])
        self.assertFalse(payload["profile_apply_performed"])

    def test_profile_suggest_budget_warning_reports_user_layer_pressure(self) -> None:
        repo, codex_home = self.make_workspace("budget-layer-pressure")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_source, registry_target / "profiles.json")
        for index in range(5):
            self.write_skill(codex_home / "skills", f"user-skill-{index}", name=f"user-skill-{index}", description="User standalone skill.")
        self.write_skill(codex_home / "plugins" / "cache", "plugin/pkg/hash/skills/plugin-skill", name="plugin-skill", description="Plugin skill.")
        self.write_skill(repo / ".codex" / "skills", "repo-skill", name="repo-skill", description="Repo skill.")

        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertTrue(payload["budget_warning_intent"]["detected"])
        self.assertEqual(payload["skill_layer_pressure"]["dominant_layer"], "user")
        self.assertGreater(payload["skill_layer_pressure"]["by_layer"]["user"], payload["skill_layer_pressure"]["by_layer"]["plugin"])
        self.assertTrue(payload["skill_layer_pressure"]["user_layer_pressure"])
        self.assertIn("standalone", payload["skill_layer_pressure"]["pressure_reason"])
        self.assertEqual(payload["standalone_user_skill_pressure"]["count"], 5)
        self.assertFalse(payload["visibility_preview"]["mutates_config"])
        self.assertTrue(payload["visibility_preview"]["requires_future_explicit_apply_receipt"])

    def test_profile_suggest_budget_warning_ignores_unrelated_audit_boost(self) -> None:
        repo, codex_home = self.make_workspace("budget-audit-override")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_source, registry_target / "profiles.json")
        memory = repo / "docs_bilingual" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "skills_usage_audit_30d_summary_2099-01-01-0000.md").write_text(
            "\n".join(
                [
                    "- Profile apply allowed: `False`",
                    "- Summary review state: `summary-reviewed`",
                    "- 30-day budget warning count: `9`",
                    "- All-descriptions-removed count: `9`",
                    "- Maximum omitted additional skills: `1111`",
                    "- Highest severity: `high`",
                    "- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`",
                    "",
                    "| profile | score | evidence reason | unused | review | bucket |",
                    "| --- | ---: | --- | ---: | --- | --- |",
                    "| web-saas | 9000 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                    "| core-dev | 1 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertEqual(payload["selected_profile"]["target_profile"], "core-dev")
        self.assertNotEqual(payload["selected_profile"]["target_profile"], "web-saas")
        self.assertTrue(payload["ranking_inputs"]["budget_warning_intent"]["audit_override_blocked"])
        self.assertIn("web-saas", payload["ranking_inputs"]["budget_warning_intent"]["blocked_unrelated_profiles"])

    def test_profile_suggest_consumes_sanitized_audit_summary_for_rerank(self) -> None:
        repo, codex_home = self.make_workspace("audit-rerank")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_source, registry_target / "profiles.json")
        memory = repo / "docs_bilingual" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "skills_usage_audit_30d_summary_2099-01-01-0000.md").write_text(
            "\n".join(
                [
                    "- Profile apply allowed: `False`",
                    "- Summary review state: `human_review_pending`",
                    "- 30-day budget warning count: `5`",
                    "- All-descriptions-removed count: `5`",
                    "- Maximum omitted additional skills: `16`",
                    "- Highest severity: `high`",
                    "- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`",
                    "",
                    "| profile | score | evidence reason | unused | review | bucket |",
                    "| --- | ---: | --- | ---: | --- | --- |",
                    "| web-saas | 9000 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                    "| core-dev | 100 | no_mapped_tool_call_medium_evidence | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Vercel deployment and Supabase backend",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertTrue(payload["ranking_inputs"]["audit_strong_evidence_available"])
        self.assertFalse(payload["ranking_inputs"]["audit_profile_apply_allowed"])
        selected_audit = payload["selected_profile"]["audit_evidence"]
        self.assertTrue(selected_audit["available"])
        self.assertGreater(selected_audit["boost"], 0)
        self.assertEqual(selected_audit["evidence_level"], "strong")
        self.assertIn("skills_usage_audit_30d_summary_2099-01-01-0000.md", selected_audit["source_file"])
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["profile_apply_performed"])

    def test_profile_suggest_warning_pressure_penalty_is_evidence_driven(self) -> None:
        repo, codex_home = self.make_workspace("warning-pressure-rerank")
        registry_source = REPO_ROOT / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        registry_target = repo / "tools" / "skill_sources" / "plugin-modules" / "references"
        registry_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_source, registry_target / "profiles.json")
        memory = repo / "docs_bilingual" / "memory"
        memory.mkdir(parents=True, exist_ok=True)
        (memory / "skills_usage_audit_30d_summary_2099-01-01-0000.md").write_text(
            "\n".join(
                [
                    "- Profile apply allowed: `False`",
                    "- Summary review state: `human_review_pending`",
                    "- 30-day budget warning count: `7`",
                    "- All-descriptions-removed count: `7`",
                    "- Maximum omitted additional skills: `62`",
                    "- Highest severity: `high`",
                    "- Severity recommended action: `avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit`",
                    "",
                    "| profile | score | evidence reason | unused | review | bucket |",
                    "| --- | ---: | --- | ---: | --- | --- |",
                    "| full | 9000 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                    "| core-dev | 100 | mapped_tool_calls_present_manual_review_required | None | manual_review_required | candidate_for_project_or_default_profile_review |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        payload = self.run_cli(
            "profile",
            "suggest",
            "--query",
            "Browser Cloudflare Canva GitHub Gmail Google Drive HubSpot Slack Stripe Supabase Vercel Figma Expo connector check",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertNotEqual(payload["selected_profile"]["target_profile"], "full")
        self.assertTrue(payload["ranking_inputs"]["warning_pressure_available"])
        self.assertTrue(payload["ranking_inputs"]["warning_pressure_penalty_applied_to_full"])
        self.assertEqual(payload["ranking_inputs"]["warning_pressure"]["budget_warning_count"], 7)
        self.assertEqual(payload["ranking_inputs"]["warning_pressure"]["all_descriptions_removed_count"], 7)
        self.assertEqual(payload["ranking_inputs"]["warning_pressure"]["max_omitted_additional_skills"], 62)
        self.assertLess(payload["ranking_inputs"]["warning_pressure"]["penalty_value"], 0)
        self.assertFalse(payload["profile_apply_performed"])

    def test_warning_audit_summarizes_and_redacts_warning_text(self) -> None:
        repo, codex_home = self.make_workspace("warnings")
        self.write_skill(codex_home / "skills", "valid-skill", name="valid-skill", description="Valid current skill.")
        sessions = codex_home / "sessions"
        sessions.mkdir(parents=True)
        now = datetime.now(timezone.utc).isoformat()
        warning_message = (
            r"Exceeded skills context budget of 2%. Skipped loading 2 skill(s). "
            r"C:\Users\lenovo\.codex\plugins\cache\secret\SKILL.md api_key=sk-test-warning-secret "
            r"thread_id=019ee780-f410-7c90-96c7-49928f42b6fa input_tokens=1234 "
            r"submission.id=\"019ee780-fae5-7c02-a192-abb289bf47db\" "
            r"function_call_output call_KRG60tVpaPmlKsJyGpcvufJJ resp_039ab27082c4ef3b"
        )
        (sessions / "session.jsonl").write_text(
            json.dumps({"timestamp": now, "type": "event_msg", "payload": {"message": warning_message}}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        payload = self.run_cli("audit", "warnings", "--since", "7d", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["command"], "audit warnings")
        self.assertEqual(payload["budget_warning_count"], 1)
        self.assertGreaterEqual(payload["skipped_loading_count"], 1)
        self.assertEqual(payload["current_frontmatter_compatibility"]["invalid_total"], 0)
        self.assertEqual(payload["current_frontmatter_compatibility"]["checked_with"], "tools/skills2cli.py index")
        self.assertFalse(payload["current_frontmatter_compatibility"]["raw_paths_retained"])
        self.assertFalse(payload["current_frontmatter_compatibility"]["raw_skill_bodies_retained"])
        self.assertFalse(payload["raw_log_paths_retained"])
        self.assertFalse(payload["raw_skill_bodies_retained"])
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-warning-secret", serialized)
        self.assertNotIn("019ee780-f410-7c90-96c7-49928f42b6fa", serialized)
        self.assertNotIn("019ee780-fae5-7c02-a192-abb289bf47db", serialized)
        self.assertNotIn("call_KRG60tVpaPmlKsJyGpcvufJJ", serialized)
        self.assertNotIn("resp_039ab27082c4ef3b", serialized)
        self.assertNotIn("input_tokens=1234", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)
        self.assertIn("[REDACTED_ID]", serialized)
        self.assertIn("[REDACTED_TOKEN_COUNT]", serialized)

    def test_warning_audit_also_reads_logs_2_sqlite_without_raw_paths(self) -> None:
        repo, codex_home = self.make_workspace("sqlite-warnings")
        self.write_skill(codex_home / "skills", "valid-skill", name="valid-skill", description="Valid current skill.")
        db = codex_home / "logs_2.sqlite"
        with sqlite3.connect(db) as con:
            con.execute("create table logs(ts integer, level text, target text, feedback_log_body text)")
            con.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    int(time.time()),
                    "WARN",
                    "codex_runtime",
                    "Exceeded skills context budget of 2%. "
                    r"output_tokens=5678 thread_id=019ee780-f410-7c90-96c7-49928f42b6fa "
                    r"C:\Users\lenovo\.codex\skills\bad\SKILL.md api_key=sk-test-sqlite-secret "
                    "All skill descriptions were removed and 16 additional skills were not included. "
                    r"Skipped loading 286 skill(s). "
                    r"submission.id=\"019ee780-fae5-7c02-a192-abb289bf47db\" "
                    r"call_hTEFffZpfgH3Ci0PPRbSyTB3 resp_039ab27082c4ef3b",
                ),
            )

        payload = self.run_cli("audit", "warnings", "--since", "1d", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["command"], "audit warnings")
        self.assertEqual(payload["budget_warning_count"], 1)
        self.assertGreaterEqual(payload["skipped_loading_count"], 1)
        self.assertEqual(payload["all_descriptions_removed_count"], 1)
        self.assertEqual(payload["max_omitted_additional_skills"], 16)
        self.assertEqual(payload["current_frontmatter_compatibility"]["invalid_total"], 0)
        self.assertEqual(payload["current_frontmatter_compatibility"]["total"], 1)
        self.assertEqual({item["source"] for item in payload["sources"]}, {"sessions_jsonl", "logs_2.sqlite"})
        sqlite_source = next(item for item in payload["sources"] if item["source"] == "logs_2.sqlite")
        self.assertTrue(sqlite_source["available"])
        self.assertEqual(sqlite_source["budget_warning_count"], 1)
        self.assertIn("sessions_jsonl_and_logs_2_sqlite", payload["log_source_review"])
        self.assertFalse(payload["raw_log_paths_retained"])
        self.assertFalse(payload["raw_skill_bodies_retained"])
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-sqlite-secret", serialized)
        self.assertNotIn("019ee780-f410-7c90-96c7-49928f42b6fa", serialized)
        self.assertNotIn("019ee780-fae5-7c02-a192-abb289bf47db", serialized)
        self.assertNotIn("call_hTEFffZpfgH3Ci0PPRbSyTB3", serialized)
        self.assertNotIn("resp_039ab27082c4ef3b", serialized)
        self.assertNotIn("output_tokens=5678", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)
        self.assertIn("[REDACTED_ID]", serialized)
        self.assertIn("[REDACTED_TOKEN_COUNT]", serialized)

    def test_warning_audit_session_scan_filters_old_files_by_mtime(self) -> None:
        repo, codex_home = self.make_workspace("old-session-filter")
        sessions = codex_home / "sessions"
        sessions.mkdir(parents=True)
        old_file = sessions / "old-session.jsonl"
        old_file.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "event_msg",
                    "payload": {"message": "Exceeded skills context budget of 2%."},
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        old_time = time.time() - 10 * 86400
        import os

        os.utime(old_file, (old_time, old_time))

        payload = self.run_cli("audit", "warnings", "--since", "1d", "--root", str(repo), "--codex-home", str(codex_home), "--json")

        session_source = next(item for item in payload["sources"] if item["source"] == "sessions_jsonl")
        self.assertEqual(session_source["budget_warning_count"], 0)
        self.assertEqual(payload["budget_warning_count"], 0)


if __name__ == "__main__":
    unittest.main()
