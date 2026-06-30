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

    def write_visibility_receipt(self, codex_home: Path, receipt_id: str, items: list[dict]) -> Path:
        receipt_root = codex_home / "state" / "skills2cli" / "visibility-receipts"
        receipt_root.mkdir(parents=True, exist_ok=True)
        receipt = receipt_root / f"{receipt_id}.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "receipt_id": receipt_id,
                    "status": "applied",
                    "items": items,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return receipt

    def visibility_restore_payload(self, repo: Path, codex_home: Path, receipt: str, *, check: bool = False) -> dict:
        return self.run_cli(
            "visibility",
            "restore",
            "--receipt",
            receipt,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
            check=check,
        )

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
        self.assertIn("--apply", payload["visibility_preview"]["visibility_apply_command"])

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


    def test_visibility_plan_is_preview_only_for_standalone_user_skills(self) -> None:
        repo, codex_home = self.make_workspace("visibility-plan")
        self.write_skill(codex_home / "skills", "skills2cli", name="skills2cli", description="Core skills2cli helper.")
        self.write_skill(codex_home / "skills", "code-review", name="code-review", description="Core code review helper.")
        for index in range(6):
            self.write_skill(codex_home / "skills", f"bulk-skill-{index}", name=f"bulk-skill-{index}", description="Bulk optional user skill.")

        payload = self.run_cli(
            "visibility",
            "plan",
            "--profile",
            "core-dev",
            "--max-visible-user-skills",
            "3",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )

        self.assertEqual(payload["command"], "visibility plan")
        self.assertEqual(payload["mode"], "plan-only")
        self.assertEqual(payload["active_user_skill_count"], 8)
        self.assertLessEqual(payload["expected_active_user_skill_count_after_apply"], 3)
        self.assertGreater(payload["hidden_user_skill_count"], 0)
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["edits_plugin_cache"])
        self.assertTrue(payload["moves_user_skill_dirs_on_apply"])
        self.assertTrue((codex_home / "skills" / "bulk-skill-0" / "SKILL.md").exists())
        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(str(codex_home), serialized)

    def test_visibility_apply_and_restore_are_receipt_backed(self) -> None:
        repo, codex_home = self.make_workspace("visibility-apply")
        self.write_skill(codex_home / "skills", "skills2cli", name="skills2cli", description="Core skills2cli helper.")
        self.write_skill(codex_home / "skills", "mcp2cli", name="mcp2cli", description="Core mcp2cli helper.")
        config_path = codex_home / "config.toml"
        config_path.write_text("[plugins]\n", encoding="utf-8")
        plugin_cache_skill = codex_home / "plugins" / "cache" / "plugin" / "hash" / "skills" / "plugin-skill"
        self.write_skill(plugin_cache_skill.parent, plugin_cache_skill.name, name="plugin-skill", description="Plugin cache skill.")
        for index in range(5):
            self.write_skill(codex_home / "skills", f"bulk-skill-{index}", name=f"bulk-skill-{index}", description="Bulk optional user skill.")

        denied = self.run_cli(
            "visibility",
            "apply",
            "--profile",
            "core-dev",
            "--max-visible-user-skills",
            "2",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
            check=False,
        )
        self.assertFalse(denied["ok"])
        self.assertEqual(denied["error"], "apply_flag_required")

        confirmation_denied = self.run_cli(
            "visibility",
            "apply",
            "--profile",
            "core-dev",
            "--max-visible-user-skills",
            "2",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--json",
            check=False,
        )
        self.assertFalse(confirmation_denied["ok"])
        self.assertEqual(confirmation_denied["error"], "operator_confirmation_required")
        self.assertTrue((codex_home / "skills" / "bulk-skill-0" / "SKILL.md").exists())

        applied = self.run_cli(
            "visibility",
            "apply",
            "--profile",
            "core-dev",
            "--max-visible-user-skills",
            "2",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
        )

        self.assertTrue(applied["ok"], applied.get("errors"))
        self.assertGreater(applied["moved_groups"], 0)
        self.assertGreater(applied["moved_skill_count"], 0)
        self.assertLessEqual(applied["post_apply_skill_layer_counts"]["user"], 2)
        self.assertTrue(applied["restart_required"])
        self.assertFalse(applied["mutates_config"])
        self.assertFalse(applied["edits_plugin_cache"])
        self.assertFalse((codex_home / "skills" / "bulk-skill-0" / "SKILL.md").exists())
        self.assertTrue((codex_home / "skills" / "skills2cli" / "SKILL.md").exists())
        self.assertEqual(config_path.read_text(encoding="utf-8"), "[plugins]\n")
        self.assertTrue((plugin_cache_skill / "SKILL.md").exists())
        receipt_files = sorted((codex_home / "state" / "skills2cli" / "visibility-receipts").glob("*.json"))
        self.assertTrue(receipt_files)
        receipt_payload = json.loads(receipt_files[-1].read_text(encoding="utf-8"))
        self.assertIn(receipt_payload["status"], {"applied", "partial_with_errors"})
        self.assertEqual(receipt_payload["receipt_backing"], "written_before_moves")

        receipt_id = applied["receipt_id"]
        restore_denied = self.run_cli(
            "visibility",
            "restore",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
            check=False,
        )
        self.assertFalse(restore_denied["ok"])
        self.assertEqual(restore_denied["error"], "apply_flag_required")

        restore_confirmation_denied = self.run_cli(
            "visibility",
            "restore",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--json",
            check=False,
        )
        self.assertFalse(restore_confirmation_denied["ok"])
        self.assertEqual(restore_confirmation_denied["error"], "operator_confirmation_required")
        self.assertFalse((codex_home / "skills" / "bulk-skill-0" / "SKILL.md").exists())

        restored = self.run_cli(
            "visibility",
            "restore",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
        )

        self.assertTrue(restored["ok"], restored.get("errors"))
        self.assertGreater(restored["restored_groups"], 0)
        self.assertEqual(restored["post_restore_skill_layer_counts"]["user"], 7)
        self.assertTrue((codex_home / "skills" / "bulk-skill-0" / "SKILL.md").exists())
        self.assertFalse(restored["mutates_config"])
        self.assertFalse(restored["edits_plugin_cache"])
        self.assertEqual(config_path.read_text(encoding="utf-8"), "[plugins]\n")
        self.assertTrue((plugin_cache_skill / "SKILL.md").exists())

    def test_visibility_status_summarizes_pressure_and_receipts_without_mutation(self) -> None:
        repo, codex_home = self.make_workspace("visibility-status")
        self.write_skill(codex_home / "skills", "skills2cli", name="skills2cli", description="Core skills2cli helper.")
        self.write_skill(codex_home / "skills", "bulk-skill", name="bulk-skill", description="Bulk optional user skill.")
        config_path = codex_home / "config.toml"
        config_path.write_text("[plugins]\n", encoding="utf-8")
        self.write_visibility_receipt(
            codex_home,
            "status-receipt",
            [{"top_dir": "bulk-skill", "source": str(codex_home / "skills" / "bulk-skill"), "destination": "redacted", "skill_count": 1}],
        )

        payload = self.run_cli("visibility", "status", "--root", str(repo), "--codex-home", str(codex_home), "--json")

        self.assertEqual(payload["command"], "visibility status")
        self.assertEqual(payload["skill_layer_counts"]["user"], 2)
        self.assertEqual(payload["standalone_user_skill_pressure"]["count"], 2)
        self.assertGreaterEqual(payload["receipt_count_sampled"], 1)
        self.assertEqual(payload["recent_receipts"][0]["receipt_id"], "status-receipt")
        self.assertFalse(payload["mutates_config"])
        self.assertFalse(payload["edits_plugin_cache"])
        self.assertFalse(payload["profile_apply_performed"])
        self.assertEqual(config_path.read_text(encoding="utf-8"), "[plugins]\n")
        self.assertTrue((codex_home / "skills" / "bulk-skill" / "SKILL.md").exists())

    def test_hidden_index_search_show_and_load_are_soft_load_only(self) -> None:
        repo, codex_home = self.make_workspace("hidden-soft-load")
        self.write_skill(codex_home / "skills", "visible-review", name="visible-review", description="Visible review helper.")
        hidden_root = codex_home / "state" / "skills2cli" / "visibility-disabled" / "receipt-a" / "skills"
        hidden_path = self.write_skill(
            hidden_root,
            "mattpocock-skills-skills-productivity-grill-me-skill-md",
            name="grill-me",
            description="Grill me with tough product feedback.",
            body="HIDDEN GRILL BODY",
        )

        indexed = self.run_cli("hidden", "index", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        self.assertEqual(indexed["command"], "hidden index")
        self.assertEqual(indexed["total_hidden"], 1)
        self.assertEqual(indexed["skills"][0]["visibility_state"], "hidden")
        self.assertFalse(indexed["global_restore_performed"])
        self.assertFalse(indexed["mutates_config"])

        search = self.run_cli("hidden", "search", "grill-me", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        self.assertEqual(search["alias_resolution"]["matched_alias"], "grill-me")
        hidden_result = next(item for item in search["results"] if item["visibility_state"] == "hidden")
        self.assertEqual(hidden_result["hidden_skill_id"], "mattpocock-skills-skills-productivity-grill-me-skill-md")
        self.assertEqual(hidden_result["matched_alias"], "grill-me")
        self.assertTrue((codex_home / "skills" / "visible-review" / "SKILL.md").exists())
        self.assertTrue(hidden_path.exists())

        shown = self.run_cli(
            "hidden",
            "show",
            "mattpocock-skills-skills-productivity-grill-me-skill-md",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )
        self.assertTrue(shown["ok"])
        self.assertFalse(shown["full_body_included"])
        self.assertNotIn("body", shown["skill"])

        loaded = self.run_cli(
            "hidden",
            "load",
            "mattpocock-skills-skills-productivity-grill-me-skill-md",
            "--query",
            r"please grill-me from C:\Users\lenovo\secret with api_key=sk-test-secret-value",
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
        )
        serialized = json.dumps(loaded, ensure_ascii=False)
        self.assertTrue(loaded["ok"])
        self.assertTrue(loaded["usage_event_recorded"])
        self.assertIn("HIDDEN GRILL BODY", loaded["skill"]["body"])
        self.assertEqual(loaded["visibility_state_after_load"], "hidden")
        self.assertTrue(hidden_path.exists())
        self.assertFalse((codex_home / "skills" / "mattpocock-skills-skills-productivity-grill-me-skill-md").exists())
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-secret-value", serialized)
        event_path = codex_home / "state" / "skills2cli" / "usage-events.jsonl"
        events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["event_type"], "hidden_load")
        self.assertEqual(event["hidden_skill_id"], "mattpocock-skills-skills-productivity-grill-me-skill-md")
        self.assertEqual(event["matched_alias"], None)
        self.assertIn("query_hash", event)
        self.assertFalse(event["raw_paths_retained"])
        self.assertNotIn(r"C:\Users\lenovo", json.dumps(event, ensure_ascii=False))

    def test_hidden_search_resolves_stop_slop_alias_to_ai_slop_cleaner(self) -> None:
        repo, codex_home = self.make_workspace("hidden-stop-slop")
        hidden_root = codex_home / "state" / "skills2cli" / "visibility-disabled" / "receipt-b" / "skills"
        self.write_skill(hidden_root, "ai-slop-cleaner", name="ai-slop-cleaner", description="Remove AI slop from prose.")

        for alias in ("stop-slop", "deslop", "anti-slop"):
            with self.subTest(alias=alias):
                payload = self.run_cli("hidden", "search", alias, "--root", str(repo), "--codex-home", str(codex_home), "--json")
                self.assertEqual(payload["alias_resolution"]["matched_alias"], alias)
                self.assertEqual(payload["alias_resolution"]["alias_target"], "ai-slop-cleaner")
                self.assertEqual(payload["results"][0]["hidden_skill_id"], "ai-slop-cleaner")
                self.assertEqual(payload["results"][0]["matched_alias"], alias)

    def test_visibility_recommend_and_apply_recommendations_are_manual_daily_limited_and_receipt_backed(self) -> None:
        repo, codex_home = self.make_workspace("visibility-recommend")
        self.write_skill(codex_home / "skills", "skills2cli", name="skills2cli", description="Core skills2cli helper.")
        self.write_skill(codex_home / "skills", "optional-visible", name="optional-visible", description="Optional visible helper.")
        hidden_root = codex_home / "state" / "skills2cli" / "visibility-disabled" / "receipt-c" / "skills"
        self.write_skill(hidden_root, "hot-hidden", name="hot-hidden", description="Hot hidden helper.")
        self.write_skill(hidden_root, "warm-hidden", name="warm-hidden", description="Warm hidden helper.")
        usage_path = codex_home / "state" / "skills2cli" / "usage-events.jsonl"
        usage_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for _ in range(10):
            rows.append({"schema_version": 1, "timestamp": now, "event_type": "hidden_load", "hidden_skill_id": "hot-hidden", "frontmatter_name": "hot-hidden", "raw_paths_retained": False})
        rows.append({"schema_version": 1, "timestamp": now, "event_type": "hidden_load", "hidden_skill_id": "warm-hidden", "frontmatter_name": "warm-hidden", "raw_paths_retained": False})
        usage_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")

        recommendation = self.run_cli("visibility", "recommend", "--days", "30", "--root", str(repo), "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(recommendation, ensure_ascii=False)
        self.assertEqual(recommendation["command"], "visibility recommend")
        self.assertEqual(recommendation["bucket_counts"]["promote"], 1)
        self.assertEqual(recommendation["bucket_counts"]["keep-soft-load"], 1)
        self.assertGreaterEqual(recommendation["bucket_counts"]["demote"], 1)
        self.assertFalse(recommendation["mutates_config"])
        self.assertNotIn(str(codex_home), serialized)
        receipt_id = recommendation["recommendation_id"]

        denied = self.run_cli(
            "visibility",
            "apply-recommendations",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--json",
            check=False,
        )
        self.assertFalse(denied["ok"])
        self.assertEqual(denied["error"], "apply_flag_required")

        confirmation_denied = self.run_cli(
            "visibility",
            "apply-recommendations",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--json",
            check=False,
        )
        self.assertFalse(confirmation_denied["ok"])
        self.assertEqual(confirmation_denied["error"], "operator_confirmation_required")

        applied = self.run_cli(
            "visibility",
            "apply-recommendations",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
        )
        self.assertTrue(applied["ok"], applied.get("errors"))
        self.assertLessEqual(applied["applied_move_count"], 3)
        self.assertGreaterEqual(applied["applied_move_count"], 1)
        self.assertFalse(applied["mutates_config"])
        receipts = sorted((codex_home / "state" / "skills2cli" / "visibility-recommendation-applies").glob("*.json"))
        self.assertTrue(receipts)
        receipt_payload = json.loads(receipts[-1].read_text(encoding="utf-8"))
        self.assertEqual(receipt_payload["receipt_backing"], "written_before_moves")
        self.assertIn(receipt_payload["status"], {"applied", "partial_with_errors"})

        second = self.run_cli(
            "visibility",
            "apply-recommendations",
            "--receipt",
            receipt_id,
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
            check=False,
        )
        self.assertFalse(second["ok"])
        self.assertEqual(second["error"], "daily_apply_limit_reached")

    def test_visibility_restore_rejects_receipt_path_outside_receipt_root(self) -> None:
        repo, codex_home = self.make_workspace("visibility-restore-receipt-scope")
        outside_receipt = codex_home / "outside-receipt.json"
        outside_receipt.write_text(json.dumps({"schema_version": 1, "receipt_id": "outside", "items": []}), encoding="utf-8")

        payload = self.run_cli(
            "visibility",
            "restore",
            "--receipt",
            str(outside_receipt),
            "--root",
            str(repo),
            "--codex-home",
            str(codex_home),
            "--apply",
            "--operator-confirmation",
            "--json",
            check=False,
        )

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "receipt_path_out_of_scope")

    def test_visibility_restore_rejects_source_mismatch_without_touching_plugin_cache(self) -> None:
        repo, codex_home = self.make_workspace("visibility-restore-source-mismatch")
        self.write_skill(codex_home / "skills", "skills2cli", name="skills2cli", description="Core skills2cli helper.")
        hidden_dir = codex_home / "state" / "skills2cli" / "visibility-disabled" / "bad" / "skills" / "bulk-skill"
        self.write_skill(hidden_dir.parent, hidden_dir.name, name="bulk-skill", description="Bulk optional user skill.")
        self.write_visibility_receipt(
            codex_home,
            "bad",
            [
                {
                    "top_dir": "bulk-skill",
                    "source": str(codex_home / "plugins" / "cache" / "bulk-skill"),
                    "destination": str(hidden_dir),
                    "skill_count": 1,
                }
            ],
        )

        payload = self.visibility_restore_payload(repo, codex_home, "bad")

        self.assertFalse(payload["ok"])
        self.assertIn("source_mismatch:bulk-skill", payload["errors"])
        self.assertTrue((hidden_dir / "SKILL.md").exists())
        self.assertFalse((codex_home / "plugins" / "cache" / "bulk-skill").exists())

    def test_visibility_restore_rejects_destination_out_of_scope(self) -> None:
        repo, codex_home = self.make_workspace("visibility-restore-destination-scope")
        hidden_dir = codex_home / "outside-hidden" / "bulk-skill"
        self.write_skill(hidden_dir.parent, hidden_dir.name, name="bulk-skill", description="Bulk optional user skill.")
        self.write_visibility_receipt(
            codex_home,
            "destination-scope",
            [
                {
                    "top_dir": "bulk-skill",
                    "source": str(codex_home / "skills" / "bulk-skill"),
                    "destination": str(hidden_dir),
                    "skill_count": 1,
                    "move_status": "moved",
                }
            ],
        )

        payload = self.visibility_restore_payload(repo, codex_home, "destination-scope")

        self.assertFalse(payload["ok"])
        self.assertIn("destination_out_of_scope:bulk-skill", payload["errors"])
        self.assertTrue((hidden_dir / "SKILL.md").exists())
        self.assertFalse((codex_home / "skills" / "bulk-skill").exists())

    def test_visibility_restore_rejects_destination_name_mismatch(self) -> None:
        repo, codex_home = self.make_workspace("visibility-restore-destination-name")
        hidden_dir = codex_home / "state" / "skills2cli" / "visibility-disabled" / "bad" / "skills" / "wrong-name"
        self.write_skill(hidden_dir.parent, hidden_dir.name, name="bulk-skill", description="Bulk optional user skill.")
        self.write_visibility_receipt(
            codex_home,
            "destination-name",
            [
                {
                    "top_dir": "bulk-skill",
                    "source": str(codex_home / "skills" / "bulk-skill"),
                    "destination": str(hidden_dir),
                    "skill_count": 1,
                    "move_status": "moved",
                }
            ],
        )

        payload = self.visibility_restore_payload(repo, codex_home, "destination-name")

        self.assertFalse(payload["ok"])
        self.assertIn("destination_name_mismatch:bulk-skill", payload["errors"])
        self.assertTrue((hidden_dir / "SKILL.md").exists())
        self.assertFalse((codex_home / "skills" / "bulk-skill").exists())

    def test_visibility_restore_rejects_invalid_top_dir(self) -> None:
        repo, codex_home = self.make_workspace("visibility-restore-invalid-top-dir")
        hidden_dir = codex_home / "state" / "skills2cli" / "visibility-disabled" / "bad" / "skills" / "bulk-skill"
        self.write_skill(hidden_dir.parent, hidden_dir.name, name="bulk-skill", description="Bulk optional user skill.")
        self.write_visibility_receipt(
            codex_home,
            "invalid-top-dir",
            [
                {
                    "top_dir": "../bulk-skill",
                    "source": str(codex_home / "skills" / "bulk-skill"),
                    "destination": str(hidden_dir),
                    "skill_count": 1,
                    "move_status": "moved",
                }
            ],
        )

        payload = self.visibility_restore_payload(repo, codex_home, "invalid-top-dir")

        self.assertFalse(payload["ok"])
        self.assertIn("invalid_receipt_item_top_dir", payload["errors"])
        self.assertTrue((hidden_dir / "SKILL.md").exists())
        self.assertFalse((codex_home / "skills" / "bulk-skill").exists())


if __name__ == "__main__":
    unittest.main()
