import argparse
import importlib.util
import io
import json
import shutil
import sqlite3
import time
import unittest
import uuid
from datetime import timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "audit_codex_skills_usage.py"

spec = importlib.util.spec_from_file_location("audit_codex_skills_usage", SCRIPT_PATH)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


class FailingCp936Stdout:
    encoding = "cp936"

    def __init__(self) -> None:
        self.parts: list[str] = []

    def write(self, text: str) -> int:
        text.encode(self.encoding)
        self.parts.append(text)
        return len(text)


class CodexSkillsUsageAuditTest(unittest.TestCase):
    maxDiff = None

    def make_codex_home(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_emit_stdout_falls_back_on_non_utf8_console(self) -> None:
        fake = FailingCp936Stdout()
        original = audit.sys.stdout
        try:
            audit.sys.stdout = fake
            audit.emit_stdout("\u26a0 Exceeded skills context budget of 2%")
        finally:
            audit.sys.stdout = original

        self.assertEqual("".join(fake.parts), "\\u26a0 Exceeded skills context budget of 2%\n")

    def test_extracts_chinese_skill_announcement(self) -> None:
        payload = {
            "type": "event_msg",
            "payload": {"message": "\u4f7f\u7528\u6280\u80fd\uff1a`plugin-modules`"},
        }
        texts = audit.texts_from_jsonl_payload(payload)
        names: list[str] = []
        for text in texts:
            for pattern in audit.SKILL_ANNOUNCE_PATTERNS:
                for match in pattern.finditer(text):
                    names.extend(audit.extract_skill_names(match.group(1)))

        self.assertIn("plugin-modules", names)

    def test_extract_skill_names_filters_generic_noise_and_unknown_names(self) -> None:
        segment = "`plugin-modules`, `and`, `from`, `draft`, `unknown-skill`"

        names = audit.extract_skill_names(segment, {"plugin-modules"})

        self.assertEqual(names, ["plugin-modules"])

    def test_scan_sessions_does_not_count_generic_explicit_skill_noise(self) -> None:
        codex_home = self.make_codex_home("skills-audit-noise")
        sessions_dir = codex_home / "sessions"
        sessions_dir.mkdir(parents=True)
        payload = {
            "timestamp": audit.now_utc().isoformat(),
            "type": "event_msg",
            "payload": {
                "message": "Using skills: `plugin-modules`, `and`, `from`, `draft`, `unknown-skill`"
            },
        }
        (sessions_dir / "session.jsonl").write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")

        report = audit.scan_sessions(codex_home, REPO_ROOT, audit.now_utc() - timedelta(days=1), {"plugin-modules"})

        self.assertEqual(report["explicit_skills"], {"plugin-modules": 1})
        self.assertEqual(
            report["explicit_skill_noise_removed"],
            {"and": 1, "from": 1, "draft": 1, "unknown-skill": 1},
        )

    def test_scan_sessions_sanitizes_explicit_skill_noise_tokens(self) -> None:
        codex_home = self.make_codex_home("skills-audit-noise-privacy")
        sessions_dir = codex_home / "sessions"
        sessions_dir.mkdir(parents=True)
        private_token = (
            r"C:\Users\lenovo\.codex\sessions\secret.jsonl?api_key=sk-test-secret-1234567890"
            + "-very-long" * 10
        )
        long_noise_token = "unknown-" + ("x" * 180)
        payload_long = {
            "timestamp": audit.now_utc().isoformat(),
            "type": "event_msg",
            "payload": {"message": f"Using skills: `{long_noise_token}`, `{private_token}`"},
        }
        payload_private = {
            "timestamp": audit.now_utc().isoformat(),
            "type": "event_msg",
            "payload": {"message": f"Using skills: `{private_token}`"},
        }
        (sessions_dir / "session.jsonl").write_text(
            json.dumps(payload_long, ensure_ascii=False) + "\n" + json.dumps(payload_private, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        report = audit.scan_sessions(codex_home, REPO_ROOT, audit.now_utc() - timedelta(days=1), {"plugin-modules"})
        serialized_noise = json.dumps(report["explicit_skill_noise_removed"], ensure_ascii=False)
        token = next(iter(report["explicit_skill_noise_removed"]))

        self.assertIn("[REDACTED_PATH]", serialized_noise)
        self.assertIn("[truncated]", serialized_noise)
        self.assertLessEqual(len(token), audit.EXPLICIT_SKILL_NOISE_TOKEN_LIMIT + len("[truncated]"))
        self.assertNotIn(r"C:\Users\lenovo", serialized_noise)
        self.assertNotIn("sk-test-secret", serialized_noise)

    def test_report_includes_noise_review_for_removed_explicit_skill_tokens(self) -> None:
        codex_home = self.make_codex_home("skills-audit-noise-review")
        skill_dir = codex_home / "skills" / "plugin-modules"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: plugin-modules\ndescription: Test skill.\n---\n", encoding="utf-8")
        sessions_dir = codex_home / "sessions"
        sessions_dir.mkdir(parents=True)
        payload = {
            "timestamp": audit.now_utc().isoformat(),
            "type": "event_msg",
            "payload": {"message": "Using skills: `plugin-modules`, `and`, `from`, `draft`, `unknown-skill`"},
        }
        (sessions_dir / "session.jsonl").write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=1,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)

        self.assertEqual(report["noise_review"]["status"], "review_required")
        self.assertEqual(
            report["noise_review"]["explicit_skill_noise_removed"],
            {"and": 1, "from": 1, "draft": 1, "unknown-skill": 1},
        )
        self.assertEqual(
            report["noise_review"]["strong_evidence_policy"],
            "removed_noise_tokens_are_not_counted_as_strong_evidence",
        )
        self.assertFalse(report["noise_review"]["raw_noise_tokens_retained"])
        self.assertEqual(report["noise_review"]["max_noise_token_length"], audit.EXPLICIT_SKILL_NOISE_TOKEN_LIMIT)
        self.assertIn("sanitized", report["noise_review"]["token_privacy_policy"])

        summary = audit.render_markdown_summary(report)
        self.assertIn("Removed explicit-skill noise token samples:", summary)
        self.assertIn("`and`", summary)
        self.assertIn("`from`", summary)
        self.assertIn("`draft`", summary)
        self.assertIn("`unknown-skill`", summary)
        self.assertNotIn("and |", summary)

    def test_field_contract_requires_noise_review_privacy_fields(self) -> None:
        codex_home = self.make_codex_home("skills-audit-noise-contract")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        report = audit.build_report(args)
        broken = dict(report)
        broken["noise_review"] = {
            "status": "review_required",
            "explicit_skill_noise_removed": {r"C:\Users\lenovo\secret.txt": 1},
            "strong_evidence_policy": "removed_noise_tokens_are_not_counted_as_strong_evidence",
        }

        ok_contract = audit.validate_report_field_contract(report)
        broken_contract = audit.validate_report_field_contract(broken)

        self.assertEqual(ok_contract["status"], "passed")
        self.assertEqual(broken_contract["status"], "failed")
        self.assertIn("noise_review:raw_noise_tokens_retained_missing", broken_contract["blockers"])
        self.assertIn("noise_review:explicit_skill_noise_token_contains_private_path", broken_contract["blockers"])

    def test_scan_logs_captures_budget_warning_shape(self) -> None:
        codex_home = self.make_codex_home("skills-audit-logs")
        db = codex_home / "logs_2.sqlite"
        with sqlite3.connect(db) as con:
            con.execute("create table logs(ts integer, level text, target text, feedback_log_body text)")
            con.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    int(time.time()),
                    "WARN",
                    "codex_client::transport",
                    "Exceeded skills context budget of 2%. "
                    "All skill descriptions were removed and 16 additional skills were not included.",
                ),
            )

        report = audit.scan_logs(codex_home, audit.now_utc() - timedelta(days=1))

        self.assertTrue(report["available"])
        self.assertEqual(report["budget_warning_count"], 1)
        self.assertEqual(report["last_7d_budget_warning_count"], 1)
        self.assertEqual(report["all_descriptions_removed_count"], 1)
        self.assertEqual(report["last_7d_all_descriptions_removed_count"], 1)
        self.assertEqual(report["max_omitted_additional_skills"], 16)
        warning = report["recent_budget_warnings"][0]
        self.assertTrue(warning["all_descriptions_removed"])
        self.assertEqual(warning["omitted_additional_skills"], 16)

    def test_scan_logs_sanitizes_warning_message_excerpt(self) -> None:
        codex_home = self.make_codex_home("skills-audit-log-sanitize")
        db = codex_home / "logs_2.sqlite"
        with sqlite3.connect(db) as con:
            con.execute("create table logs(ts integer, level text, target text, feedback_log_body text)")
            con.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    int(time.time()),
                    "WARN",
                    "codex_client::transport",
                    "Exceeded skills context budget of 2%. "
                    r"Path C:\Users\lenovo\.codex\sessions\secret.jsonl "
                    "api_key=sk-test-secret cookie=session-secret",
                ),
            )

        report = audit.scan_logs(codex_home, audit.now_utc() - timedelta(days=1))
        excerpt = report["recent_budget_warnings"][0]["message_excerpt"]

        self.assertIn("[REDACTED_PATH]", excerpt)
        self.assertIn("api_key=[REDACTED_SECRET]", excerpt)
        self.assertIn("cookie=[REDACTED_SECRET]", excerpt)
        self.assertNotIn("sk-test-secret", excerpt)
        self.assertNotIn("session-secret", excerpt)
        self.assertNotIn(r"C:\Users\lenovo", excerpt)

    def test_sanitize_log_excerpt_preserves_redaction_markers_when_truncated(self) -> None:
        private_path = r"C:\Users\lenovo\.codex\sessions\secret.jsonl"
        secret = "api_key=sk-test-secret"

        path_excerpt = audit.sanitize_log_excerpt("x" * 490 + private_path + " tail", limit=500)
        secret_excerpt = audit.sanitize_log_excerpt("x" * 480 + secret + " tail", limit=500)

        self.assertIn("[REDACTED_PATH]", path_excerpt)
        self.assertIn("[REDACTED_SECRET]", secret_excerpt)
        self.assertIn("[truncated]", path_excerpt)
        self.assertIn("[truncated]", secret_excerpt)
        self.assertNotIn(r"C:\Users\lenovo", path_excerpt)
        self.assertNotIn("sk-test-secret", secret_excerpt)
        for marker in audit.REDACTION_MARKERS:
            for prefix_length in range(1, len(marker)):
                self.assertFalse(path_excerpt.endswith(marker[:prefix_length]))
                self.assertFalse(secret_excerpt.endswith(marker[:prefix_length]))

    def test_scan_logs_missing_database_keeps_log_evidence_shape(self) -> None:
        codex_home = self.make_codex_home("skills-audit-missing-logs")

        report = audit.scan_logs(codex_home, audit.now_utc() - timedelta(days=1))

        self.assertEqual(
            report,
            {
                "available": False,
                "budget_warning_count": 0,
                "last_7d_budget_warning_count": 0,
                "all_descriptions_removed_count": 0,
                "last_7d_all_descriptions_removed_count": 0,
                "max_omitted_additional_skills": 0,
                "recent_budget_warnings": [],
                "skipped_loading_count": 0,
                "recent_skipped_loading": [],
            },
        )

    def test_warning_severity_follows_plan_thresholds(self) -> None:
        unavailable = audit.build_warning_severity({"available": False})
        high_by_count = audit.build_warning_severity(
            {
                "available": True,
                "budget_warning_count": 3,
                "last_7d_budget_warning_count": 3,
                "recent_budget_warnings": [],
            }
        )
        high_by_removed_descriptions = audit.build_warning_severity(
            {
                "available": True,
                "budget_warning_count": 1,
                "all_descriptions_removed_count": 1,
                "recent_budget_warnings": [{"all_descriptions_removed": True}],
            }
        )
        medium = audit.build_warning_severity(
            {
                "available": True,
                "budget_warning_count": 1,
                "recent_budget_warnings": [{"all_descriptions_removed": False}],
            }
        )
        none = audit.build_warning_severity(
            {
                "available": True,
                "budget_warning_count": 0,
                "recent_budget_warnings": [],
            }
        )

        self.assertEqual(unavailable["level"], "unknown")
        self.assertEqual(high_by_count["level"], "high")
        self.assertEqual(high_by_removed_descriptions["level"], "high")
        self.assertEqual(medium["level"], "medium")
        self.assertEqual(none["level"], "none")

    def test_warning_triage_marker_requires_narrow_window(self) -> None:
        codex_home = self.make_codex_home("skills-audit-warning-triage-window")
        broad_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            warning_triage=True,
        )
        narrow_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=1,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            warning_triage=True,
        )
        since_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since="2026-05-16T08:00:00+08:00",
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            warning_triage=True,
        )

        broad = audit.build_report(broad_args)
        narrow = audit.build_report(narrow_args)
        since_based = audit.build_report(since_args)

        self.assertEqual(broad["audit_state"]["reason"], "warning_triage_window_too_broad")
        self.assertEqual(broad["warning_triage"]["status"], "blocked")
        self.assertFalse(broad["warning_triage"]["window_ok"])
        self.assertIn("warning_triage_window_not_narrow", broad["warning_triage"]["blockers"])
        self.assertTrue(narrow["warning_triage"]["requested"])
        self.assertTrue(narrow["warning_triage"]["window_ok"])
        self.assertEqual(narrow["warning_triage"]["days"], 1)
        self.assertTrue(since_based["warning_triage"]["window_ok"])
        self.assertTrue(since_based["warning_triage"]["uses_since_override"])

    def test_warning_triage_report_captures_recent_budget_warning(self) -> None:
        codex_home = self.make_codex_home("skills-audit-warning-triage-found")
        db = codex_home / "logs_2.sqlite"
        with sqlite3.connect(db) as con:
            con.execute("create table logs(ts integer, level text, target text, feedback_log_body text)")
            con.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    int(time.time()),
                    "WARN",
                    "codex_client::transport",
                    "Exceeded skills context budget of 2%. "
                    "All skill descriptions were removed and 16 additional skills were not included.",
                ),
            )
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=1,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            warning_triage=True,
        )

        report = audit.build_report(args)

        self.assertEqual(report["warning_triage"]["status"], "warning_found")
        self.assertEqual(report["warning_triage"]["budget_warning_count"], 1)
        self.assertEqual(report["warning_triage"]["all_descriptions_removed_count"], 1)
        self.assertEqual(report["warning_triage"]["max_omitted_additional_skills"], 16)
        self.assertEqual(report["field_contract"]["status"], "passed")

    def test_report_uses_repo_profile_fallback_and_expands_full_module(self) -> None:
        codex_home = self.make_codex_home("skills-audit-profile")
        (codex_home / "config.toml").write_text(
            '[plugins."Browser"]\n'
            "enabled = true\n"
            '[plugins."Vercel"]\n'
            "enabled = false\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=0,
            since=None,
            baseline=True,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)
        full_rows = [row for row in report["module_evidence"] if row["module"] == "full"]

        self.assertEqual(report["safety"]["audit_only"], True)
        self.assertEqual(report["config_summary"]["enabled_plugins"], ["Browser"])
        current_profile = report["config_summary"]["current_profile"]
        self.assertEqual(current_profile["inferred_profile"], "custom_or_unmatched")
        self.assertTrue(current_profile["manual_review_required"])
        self.assertEqual(len(full_rows), 1)
        self.assertIn("Browser", full_rows[0]["plugins"])
        self.assertNotIn("a", full_rows[0]["plugins"])

    def test_current_profile_summary_detects_exact_module_match(self) -> None:
        profiles = {
            "known_plugins": ["Browser", "GitHub", "Vercel"],
            "modules": {
                "daily": {"plugins": ["Browser", "GitHub"]},
                "web": {"plugins": ["Browser", "GitHub", "Vercel"]},
            },
        }

        summary = audit.build_current_profile_summary(profiles, ["browser-use@openai-bundled", "github@openai-curated"])

        self.assertEqual(summary["inferred_profile"], "daily")
        self.assertEqual(summary["exact_profile_matches"], ["daily"])
        self.assertEqual(summary["matched_enabled_known_plugins"], ["Browser", "GitHub"])
        self.assertFalse(summary["manual_review_required"])

    def test_module_evidence_recommendation_uses_plan_threshold(self) -> None:
        profiles = {
            "modules": {
                "web-saas": {
                    "plugins": ["Vercel"],
                }
            }
        }
        low = audit.build_module_evidence(
            profiles,
            {
                "profile_helper_calls": {"web-saas": 9},
                "skill_paths": {},
                "weak_plugin_mentions": {},
            },
        )[0]
        high = audit.build_module_evidence(
            profiles,
            {
                "profile_helper_calls": {"web-saas": 10},
                "skill_paths": {},
                "weak_plugin_mentions": {},
            },
        )[0]

        self.assertEqual(low["strong_total"], 9)
        self.assertEqual(low["default_candidate_threshold"], 10)
        self.assertEqual(low["recommendation"], "keep_module_on_demand_and_continue_audit")
        self.assertEqual(high["strong_total"], 10)
        self.assertEqual(high["default_candidate_threshold"], 10)
        self.assertEqual(high["recommendation"], "candidate_for_project_or_default_profile_review")

    def test_mapped_tool_calls_are_medium_evidence_only(self) -> None:
        profiles = {
            "modules": {
                "web-saas": {
                    "plugins": ["Vercel"],
                }
            }
        }

        row = audit.build_module_evidence(
            profiles,
            {
                "profile_helper_calls": {},
                "skill_paths": {},
                "tool_call_names": {"mcp__vercel__deploy": 4, "web_saas_preview": 2},
                "weak_plugin_mentions": {},
            },
        )[0]

        self.assertEqual(row["mapped_tool_call_mentions"], 6)
        self.assertEqual(row["mapped_tool_call_policy"], "medium_evidence_only_not_counted_as_strong_evidence")
        self.assertEqual(row["medium_evidence_rationale"], "mapped_tool_calls_present_manual_review_required")
        self.assertEqual(row["cross_project_utility"], "manual_review_required")
        self.assertEqual(row["strong_total"], 0)
        self.assertEqual(row["recommendation"], "no_recent_evidence_keep_dormant_not_deleted")

    def test_report_preserves_unknown_plugin_enabled_state(self) -> None:
        codex_home = self.make_codex_home("skills-audit-unknown-plugin")
        (codex_home / "config.toml").write_text(
            '[plugins."Browser"]\n'
            "enabled = true\n"
            '[plugins."Vercel"]\n'
            "enabled = false\n"
            '[plugins."Twilio Developer Kit"]\n',
            encoding="utf-8",
        )
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=0,
            since=None,
            baseline=True,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)

        self.assertEqual(report["config_summary"]["enabled_plugins"], ["Browser"])
        self.assertEqual(report["config_summary"]["disabled_plugins"], ["Vercel"])
        self.assertEqual(report["config_summary"]["unknown_enabled_state_plugins"], ["Twilio Developer Kit"])

    def test_report_includes_profile_decision_field_contract(self) -> None:
        codex_home = self.make_codex_home("skills-audit-contract")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)

        required_top_level = {
            "schema_version",
            "generated_at",
            "audit_state",
            "audit_window",
            "safety",
            "config_summary",
            "cadence_review",
            "inventory_summary",
            "log_evidence",
            "warning_severity",
            "warning_triage",
            "session_evidence",
            "module_evidence",
            "decision_recommendation",
            "noise_review",
            "script_capability_boundaries",
            "recommendations",
        }
        self.assertLessEqual(required_top_level, set(report))
        self.assertIn("state", report["audit_state"])
        self.assertIn("reason", report["audit_state"])
        self.assertIn("next_action", report["audit_state"])
        self.assertIn("profile_apply_allowed", report["audit_state"])
        self.assertEqual(report["audit_window"]["days"], 30)
        self.assertTrue(report["safety"]["audit_only"])
        self.assertFalse(report["safety"]["mutates_config"])
        self.assertFalse(report["safety"]["edits_plugin_cache"])
        self.assertFalse(report["safety"]["hard_load_apply_performed"])
        self.assertIn("enabled_plugins", report["config_summary"])
        self.assertIn("current_profile", report["config_summary"])
        self.assertEqual(report["cadence_review"]["weekly_report_review"], "manual_review_required")
        self.assertIn("last_7d_budget_warning_count", report["log_evidence"])
        self.assertIn("total_skills", report["inventory_summary"])
        self.assertIn("budget_warning_count", report["log_evidence"])
        self.assertIn("level", report["warning_severity"])
        self.assertIn("requested", report["warning_triage"])
        self.assertIn("status", report["warning_triage"])
        self.assertIn("window_policy", report["warning_triage"])
        self.assertIn("window_ok", report["warning_triage"])
        self.assertIn("blockers", report["warning_triage"])
        self.assertIn("recommended_action", report["warning_triage"])
        self.assertIn("explicit_skills", report["session_evidence"])
        self.assertIsInstance(report["module_evidence"], list)
        self.assertEqual(report["decision_recommendation"]["status"], "advisory_only_no_profile_apply")
        self.assertFalse(report["decision_recommendation"]["profile_apply_allowed"])
        self.assertIn("bucket_counts", report["decision_recommendation"])
        self.assertIn("status", report["noise_review"])
        self.assertIn("reliable_coverage", report["script_capability_boundaries"])
        self.assertIn("human_review_required_for", report["script_capability_boundaries"])
        self.assertIn("enhancement_triggers", report["script_capability_boundaries"])
        self.assertIn("manual_evidence", report)
        self.assertEqual(report["manual_evidence"]["valid_note_count"], 0)
        self.assertIn("field_contract", report)
        self.assertTrue(report["field_contract"]["passed"])
        self.assertEqual(report["field_contract"]["status"], "passed")
        self.assertEqual(
            audit.validate_report_field_contract(report, require_embedded=True)["status"],
            "passed",
        )
        self.assertIsInstance(report["recommendations"], list)

    def test_script_capability_boundaries_are_in_report_contract_and_summary(self) -> None:
        codex_home = self.make_codex_home("skills-audit-script-boundaries")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)
        summary = audit.render_markdown_summary(report)
        broken = json.loads(json.dumps(report))
        broken["script_capability_boundaries"]["human_review_required_for"] = []
        broken["field_contract"] = audit.validate_report_field_contract(broken)

        self.assertEqual(report["field_contract"]["status"], "passed")
        self.assertIn("## Script coverage and human review boundaries", summary)
        self.assertIn("weak_plugin_mentions_are_text_trends_not_real_invocation_evidence", summary)
        self.assertIn(
            "script_capability_boundaries:human_review_required_for_empty",
            broken["field_contract"]["blockers"],
        )
        self.assertIn(
            "field_contract:script_capability_boundaries:human_review_required_for_empty",
            audit.build_candidate_generation_gate(broken, summary_reviewed=True)["blockers"],
        )

    def test_cadence_review_contract_and_summary_are_explicit(self) -> None:
        codex_home = self.make_codex_home("skills-audit-cadence-review")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
            late_run=True,
            missed_weekly_runs=2,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)
        summary = audit.render_markdown_summary(report)
        broken = json.loads(json.dumps(report))
        del broken["cadence_review"]["weekly_report_review"]
        broken["cadence_review"]["missed_weekly_runs"] = -1
        broken["field_contract"] = audit.validate_report_field_contract(broken)

        self.assertEqual(report["field_contract"]["status"], "passed")
        self.assertIn("Late run: `True`", summary)
        self.assertIn("Missed weekly runs: `2`", summary)
        self.assertIn("Weekly report review: `manual_review_required`", summary)
        self.assertIn("cadence_review:weekly_report_review_missing", broken["field_contract"]["blockers"])
        self.assertIn("cadence_review:missed_weekly_runs_invalid_type", broken["field_contract"]["blockers"])
        self.assertIn(
            "field_contract:cadence_review:weekly_report_review_missing",
            audit.build_candidate_generation_gate(broken, summary_reviewed=True)["blockers"],
        )

    def test_warning_triage_contract_requires_decision_fields(self) -> None:
        codex_home = self.make_codex_home("skills-audit-warning-triage-contract")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        report = audit.build_report(args)
        report["warning_triage"].pop("window_policy")
        report["warning_triage"]["blockers"] = "warning_triage_window_not_narrow"

        contract = audit.validate_report_field_contract(report)
        gate = audit.build_candidate_generation_gate(report, summary_reviewed=True)

        self.assertFalse(contract["passed"])
        self.assertIn("warning_triage:window_policy_missing", contract["blockers"])
        self.assertIn("warning_triage:blockers_invalid_type", contract["blockers"])
        self.assertFalse(gate["allowed"])
        self.assertIn("field_contract:warning_triage:window_policy_missing", gate["blockers"])

    def test_audit_state_contract_requires_decision_fields(self) -> None:
        codex_home = self.make_codex_home("skills-audit-state-contract")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        report = audit.build_report(args)
        report["audit_state"].pop("next_action")
        report["audit_state"]["profile_apply_allowed"] = "false"

        contract = audit.validate_report_field_contract(report)
        gate = audit.build_candidate_generation_gate(report, summary_reviewed=True)

        self.assertFalse(contract["passed"])
        self.assertIn("audit_state:next_action_missing", contract["blockers"])
        self.assertIn("audit_state:profile_apply_allowed_invalid_type", contract["blockers"])
        self.assertFalse(gate["allowed"])
        self.assertIn("field_contract:audit_state:next_action_missing", gate["blockers"])

    def test_field_contract_failure_blocks_candidate_gate(self) -> None:
        report = {
            "schema_version": 1,
            "generated_at": "2026-05-16T00:00:00+00:00",
            "audit_window": {
                "since": "2026-04-16T00:00:00+00:00",
                "until": "2026-05-16T00:00:00+00:00",
                "days": 30,
            },
            "safety": {
                "mutates_config": False,
                "edits_plugin_cache": False,
                "hard_load_apply_performed": False,
                "audit_only": True,
            },
            "audit_state": {
                "state": "ready-for-summary",
                "reason": "audit_window_at_least_30_days",
                "next_action": "generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate",
                "profile_apply_allowed": False,
            },
            "config_summary": {"current_profile": {}},
            "inventory_summary": {},
            "log_evidence": {"budget_warning_count": 0, "last_7d_budget_warning_count": 0},
            "session_evidence": {},
            "module_evidence": [],
            "cadence_review": {},
            "recommendations": [],
        }

        contract = audit.validate_report_field_contract(report)
        gate = audit.build_candidate_generation_gate(report, summary_reviewed=True)

        self.assertFalse(contract["passed"])
        self.assertIn("missing_field:manual_evidence", contract["blockers"])
        self.assertFalse(gate["allowed"])
        self.assertIn("field_contract:missing_field:manual_evidence", gate["blockers"])
        self.assertEqual(gate["field_contract"]["status"], "failed")

    def test_embedded_field_contract_staleness_blocks_candidate_gate(self) -> None:
        report = {
            "schema_version": 1,
            "generated_at": "2026-05-16T00:00:00+00:00",
            "audit_window": {
                "since": "2026-04-16T00:00:00+00:00",
                "until": "2026-05-16T00:00:00+00:00",
                "days": 30,
            },
            "safety": {
                "mutates_config": False,
                "edits_plugin_cache": False,
                "hard_load_apply_performed": False,
                "audit_only": True,
            },
            "audit_state": {
                "state": "ready-for-summary",
                "reason": "audit_window_at_least_30_days",
                "next_action": "generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate",
                "profile_apply_allowed": False,
            },
            "config_summary": {"current_profile": {}},
            "inventory_summary": {},
            "log_evidence": {"budget_warning_count": 0, "last_7d_budget_warning_count": 0},
            "warning_triage": {
                "requested": False,
                "status": "not_requested",
                "blockers": [],
                "window_policy": "use_days_1_or_since_for_warning_triage",
                "window_ok": False,
                "budget_warning_count": 0,
                "recommended_action": "run_with_warning_triage_after_a_live_session_budget_warning",
            },
            "session_evidence": {},
            "manual_evidence": {
                "valid_note_count": 0,
                "raw_notes_retained": False,
                "source_paths_retained": False,
                "max_path_length": audit.MANUAL_NOTE_PATH_LIMIT,
                "path_privacy_policy": "manual_note_source_paths_are_redacted_and_bounded_before_report_retention",
            },
            "noise_review": {
                "status": "no_obvious_false_positives_found",
                "explicit_skill_noise_removed": {},
                "strong_evidence_policy": "removed_noise_tokens_are_not_counted_as_strong_evidence",
                "raw_noise_tokens_retained": False,
                "max_noise_token_length": audit.EXPLICIT_SKILL_NOISE_TOKEN_LIMIT,
                "token_privacy_policy": "explicit_skill_noise_tokens_are_sanitized_path_secret_redacted_and_truncated",
            },
            "script_capability_boundaries": audit.build_script_capability_boundaries(),
            "module_evidence": [],
            "decision_recommendation": {
                "status": "advisory_only_no_profile_apply",
                "policy": "decision_buckets_are_review_inputs_and_never_apply_profiles",
                "profile_apply_allowed": False,
                "buckets": {},
                "bucket_counts": {},
            },
            "cadence_review": {
                "late_run": False,
                "missed_weekly_runs": None,
                "weekly_report_review": "manual_review_required",
            },
            "recommendations": [],
            "field_contract": {"status": "failed", "passed": False, "blockers": ["stale"]},
        }

        contract = audit.validate_report_field_contract(report, require_embedded=True)
        gate = audit.build_candidate_generation_gate(report, summary_reviewed=True)

        self.assertFalse(contract["passed"])
        self.assertIn("embedded_field_contract:status_stale", contract["blockers"])
        self.assertIn("embedded_field_contract:passed_stale", contract["blockers"])
        self.assertIn("embedded_field_contract:blockers_stale", contract["blockers"])
        self.assertFalse(gate["allowed"])
        self.assertIn("field_contract:embedded_field_contract:status_stale", gate["blockers"])

    def test_manual_notes_are_sanitized_and_validated(self) -> None:
        codex_home = self.make_codex_home("skills-audit-manual-notes")
        notes_path = codex_home / "manual-notes.md"
        notes_path.write_text(
            "\n".join(
                [
                    "time: 2026-05-16T00:00:00Z",
                    "project: D:\\PythonProject_langgraph",
                    "task_type: web-saas",
                    "requested_capability: browser api_key=sk-test-secret",
                    "evidence_level: medium",
                    "reason: User asked for browser verification access_token=secret-token",
                    "action_taken: soft-load",
                    "restore_or_followup: keep on-demand",
                    "",
                    "time: 2026-05-16T00:00:00Z",
                    "project: test",
                    "task_type: web-saas",
                    "requested_capability: browser",
                    "evidence_level: invalid",
                    "reason: invalid evidence level",
                    "action_taken: none",
                ]
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[str(notes_path), r"C:\Users\lenovo\.codex\manual-notes-secret.md"],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)
        manual = report["manual_evidence"]

        self.assertEqual(manual["files_read"], 1)
        self.assertEqual(manual["valid_note_count"], 1)
        self.assertEqual(len(manual["invalid_notes"]), 2)
        self.assertEqual(manual["counts_by_evidence_level"], {"medium": 1})
        note = manual["notes"][0]
        self.assertIn("[REDACTED_PATH]", note["project"])
        self.assertIn("[REDACTED_SECRET]", note["requested_capability"])
        self.assertIn("[REDACTED_SECRET]", note["reason"])
        self.assertNotIn("sk-test-secret", json.dumps(manual, ensure_ascii=False))
        serialized_manual = json.dumps(manual, ensure_ascii=False)
        self.assertIn("[REDACTED_PATH]", serialized_manual)
        self.assertNotIn(r"C:\Users\lenovo", serialized_manual)
        self.assertNotIn(str(notes_path), serialized_manual)
        self.assertFalse(manual["raw_notes_retained"])
        self.assertFalse(manual["source_paths_retained"])
        self.assertEqual(manual["max_path_length"], audit.MANUAL_NOTE_PATH_LIMIT)
        self.assertIn("redacted", manual["path_privacy_policy"])
        self.assertEqual(report["field_contract"]["status"], "passed")

    def test_field_contract_rejects_raw_manual_evidence_paths(self) -> None:
        codex_home = self.make_codex_home("skills-audit-manual-path-contract")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        report = audit.build_report(args)
        broken = json.loads(json.dumps(report))
        broken["manual_evidence"]["source_paths_retained"] = True
        broken["manual_evidence"]["invalid_notes"] = [
            {
                "path": r"C:\Users\lenovo\.codex\manual-notes.md?api_key=sk-test-secret-123456",
                "reason": "missing_file",
            }
        ]

        contract = audit.validate_report_field_contract(broken)

        self.assertFalse(contract["passed"])
        self.assertIn("manual_evidence:source_paths_retained_not_false", contract["blockers"])
        self.assertIn("manual_evidence:manual_evidence_contains_private_path", contract["blockers"])
        self.assertIn("manual_evidence:manual_evidence_contains_raw_secret_assignment", contract["blockers"])

    def test_since_with_timezone_is_converted_to_utc_without_replacing_offset(self) -> None:
        parsed = audit.parse_since("2026-05-16T08:00:00+08:00")

        self.assertEqual(parsed.isoformat(), "2026-05-16T00:00:00+00:00")
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_report_audit_window_uses_timezone_aware_since(self) -> None:
        codex_home = self.make_codex_home("skills-audit-since")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since="2026-05-16T08:00:00+08:00",
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        report = audit.build_report(args)

        self.assertEqual(report["audit_window"]["since"], "2026-05-16T00:00:00+00:00")
        self.assertEqual(report["audit_window"]["days"], 30)

    def test_report_includes_audit_state_machine_boundary(self) -> None:
        codex_home = self.make_codex_home("skills-audit-state")
        planned_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=0,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            planned_audit=True,
        )
        baseline_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=0,
            since=None,
            baseline=True,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        weekly_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        summary_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        reviewed_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=True,
        )
        reviewed_missing_source_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=True,
        )
        paused_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            pause_audit="data-source-missing",
        )

        planned = audit.build_report(planned_args)
        baseline = audit.build_report(baseline_args)
        weekly = audit.build_report(weekly_args)
        summary = audit.build_report(summary_args)
        reviewed = audit.build_report(reviewed_args)
        reviewed_missing_source = audit.build_report(reviewed_missing_source_args)
        paused = audit.build_report(paused_args)

        self.assertEqual(planned["audit_state"]["state"], "planned")
        self.assertEqual(planned["audit_state"]["reason"], "audit_plan_recorded_baseline_not_generated")
        self.assertFalse(planned["audit_state"]["profile_apply_allowed"])
        self.assertEqual(baseline["audit_state"]["state"], "running")
        self.assertEqual(baseline["audit_state"]["reason"], "baseline_generated")
        self.assertFalse(baseline["audit_state"]["profile_apply_allowed"])
        self.assertEqual(weekly["audit_state"]["state"], "running")
        self.assertEqual(weekly["audit_state"]["reason"], "audit_window_shorter_than_30_days")
        self.assertFalse(weekly["audit_state"]["profile_apply_allowed"])
        self.assertEqual(summary["audit_state"]["state"], "ready-for-summary")
        self.assertEqual(summary["audit_state"]["reason"], "audit_window_at_least_30_days")
        self.assertFalse(summary["audit_state"]["profile_apply_allowed"])
        self.assertEqual(reviewed["audit_state"]["state"], "summary-reviewed")
        self.assertEqual(reviewed["audit_state"]["reason"], "summary_reviewed_and_source_reports_ready")
        self.assertFalse(reviewed["audit_state"]["profile_apply_allowed"])
        self.assertEqual(reviewed_missing_source["audit_state"]["state"], "ready-for-summary")
        self.assertEqual(reviewed_missing_source["audit_state"]["reason"], "summary_reviewed_source_report_paths_missing")
        self.assertEqual(reviewed_missing_source["audit_state"]["summary_review_blockers"], ["source_report_paths_missing"])
        self.assertEqual(paused["audit_state"]["state"], "paused")
        self.assertEqual(paused["audit_state"]["reason"], "audit_paused_data-source-missing")
        self.assertEqual(paused["audit_state"]["pause_blockers"], ["data-source-missing"])
        self.assertFalse(paused["audit_state"]["profile_apply_allowed"])

    def test_candidate_generation_gate_requires_30_day_summary_review(self) -> None:
        codex_home = self.make_codex_home("skills-audit-candidate-gate")
        short_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output="candidate.json",
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        reviewed_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output="candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
        )

        blocked_gate = audit.build_candidate_generation_gate(audit.build_report(short_args), summary_reviewed=False)
        allowed_report = audit.build_report(reviewed_args)
        allowed_gate = audit.build_candidate_generation_gate(allowed_report, summary_reviewed=True)

        self.assertFalse(blocked_gate["allowed"])
        self.assertEqual(blocked_gate["status"], "blocked")
        self.assertIn("audit_window_shorter_than_30_days", blocked_gate["blockers"])
        self.assertIn("summary_not_marked_reviewed", blocked_gate["blockers"])
        self.assertTrue(blocked_gate["ordinary_continue_or_generic_confirmation_is_not_apply_authorization"])
        self.assertTrue(allowed_gate["allowed"])
        self.assertEqual(allowed_gate["status"], "allowed")
        self.assertEqual(allowed_gate["blockers"], [])
        self.assertEqual(allowed_gate["field_contract"]["status"], "passed")
        self.assertEqual(allowed_report["audit_state"]["state"], "apply-candidate")
        self.assertFalse(allowed_report["audit_state"]["profile_apply_allowed"])

    def test_audit_closure_state_requires_reviewed_summary_and_source_paths(self) -> None:
        codex_home = self.make_codex_home("skills-audit-closure-state")
        blocked_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
            close_audit="no-change",
        )
        closed_no_change_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=True,
            close_audit="no-change",
        )
        closed_with_candidate_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output=".tmp/skills-profile-candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
            close_audit="with-candidate",
        )

        blocked = audit.build_report(blocked_args)
        closed_no_change = audit.build_report(closed_no_change_args)
        closed_with_candidate = audit.build_report(closed_with_candidate_args)
        blocked_summary = audit.render_markdown_summary(blocked)
        closed_summary = audit.render_markdown_summary(closed_no_change)

        self.assertEqual(blocked["audit_state"]["state"], "running")
        self.assertEqual(blocked["audit_state"]["reason"], "audit_closure_no-change_blocked")
        self.assertIn("audit_window_shorter_than_30_days", blocked["audit_state"]["close_blockers"])
        self.assertIn("summary_not_marked_reviewed", blocked["audit_state"]["close_blockers"])
        self.assertIn("source_report_paths_missing", blocked["audit_state"]["close_blockers"])
        self.assertIn("Audit next action: `resolve_closure_blockers_without_profile_apply`", blocked_summary)
        self.assertIn("Profile apply allowed: `False`", blocked_summary)
        self.assertIn(
            "Audit state blockers: `audit_window_shorter_than_30_days, summary_not_marked_reviewed, source_report_paths_missing`",
            blocked_summary,
        )
        self.assertEqual(closed_no_change["audit_state"]["state"], "closed-no-change")
        self.assertEqual(closed_no_change["audit_state"]["close_blockers"], [])
        self.assertFalse(closed_no_change["audit_state"]["profile_apply_allowed"])
        self.assertIn("Audit state blockers: `none`", closed_summary)
        self.assertEqual(closed_with_candidate["audit_state"]["state"], "closed-with-candidate")
        self.assertFalse(closed_with_candidate["audit_state"]["profile_apply_allowed"])

    def test_candidate_audit_state_blocks_missing_source_report_paths(self) -> None:
        codex_home = self.make_codex_home("skills-audit-candidate-state-source-paths")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output="candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
        )

        report = audit.build_report(args)

        self.assertEqual(report["audit_state"]["state"], "ready-for-summary")
        self.assertEqual(report["audit_state"]["reason"], "profile_apply_candidate_source_report_paths_missing")
        self.assertEqual(report["audit_state"]["candidate_blockers"], ["source_report_paths_missing"])

    def test_candidate_generation_gate_requires_source_report_paths_when_requested(self) -> None:
        codex_home = self.make_codex_home("skills-audit-candidate-source-gate")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output="candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
        )
        report = audit.build_report(args)

        blocked_gate = audit.build_candidate_generation_gate(
            report,
            summary_reviewed=True,
            require_source_reports=True,
        )
        allowed_gate = audit.build_candidate_generation_gate(
            report,
            summary_reviewed=True,
            json_report_path=".tmp/skills-usage-audit-30d.json",
            markdown_summary_path=".tmp/skills-usage-audit-30d-summary.md",
            require_source_reports=True,
        )

        self.assertFalse(blocked_gate["allowed"])
        self.assertIn("source_report_json_missing", blocked_gate["blockers"])
        self.assertIn("source_report_markdown_summary_missing", blocked_gate["blockers"])
        self.assertTrue(blocked_gate["source_reports_required"])
        self.assertFalse(blocked_gate["json_report_present"])
        self.assertFalse(blocked_gate["markdown_summary_present"])
        self.assertTrue(allowed_gate["allowed"])
        self.assertTrue(allowed_gate["json_report_present"])
        self.assertTrue(allowed_gate["markdown_summary_present"])

    def test_candidate_generation_gate_blocks_planned_or_paused_audit_state(self) -> None:
        codex_home = self.make_codex_home("skills-audit-not-ready-candidate-gate")
        planned_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output=".tmp/skills-profile-candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
            planned_audit=True,
        )
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=".tmp/skills-usage-audit-30d.json",
            summary_output=".tmp/skills-usage-audit-30d-summary.md",
            candidate_output=".tmp/skills-profile-candidate.json",
            candidate_summary_output=None,
            summary_reviewed=True,
            pause_audit="script-defect",
        )
        planned_report = audit.build_report(planned_args)
        report = audit.build_report(args)

        planned_gate = audit.build_candidate_generation_gate(
            planned_report,
            summary_reviewed=True,
            json_report_path=planned_args.output,
            markdown_summary_path=planned_args.summary_output,
            require_source_reports=True,
        )
        gate = audit.build_candidate_generation_gate(
            report,
            summary_reviewed=True,
            json_report_path=args.output,
            markdown_summary_path=args.summary_output,
            require_source_reports=True,
        )

        self.assertEqual(planned_report["audit_state"]["state"], "planned")
        self.assertFalse(planned_gate["allowed"])
        self.assertIn("audit_state_planned", planned_gate["blockers"])
        self.assertEqual(report["audit_state"]["state"], "paused")
        self.assertFalse(gate["allowed"])
        self.assertIn("audit_state_paused", gate["blockers"])

    def test_source_reports_sanitize_private_paths_and_tokens(self) -> None:
        source_reports = audit.build_source_reports(
            r"C:/Users/lenovo/.codex/sessions/audit.json",
            ".tmp/skills-usage-summary.md?access_token=sk-test-secret",
            [
                "/Users/lenovo/private/skills-usage-summary.md",
                r"\\server\share\client\manual-notes.md",
                r"D:\private\manual-notes.md?cookie=session-secret",
            ],
        )
        serialized = json.dumps(source_reports, ensure_ascii=False)

        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)
        self.assertNotIn("C:/Users/lenovo", serialized)
        self.assertNotIn("/Users/lenovo", serialized)
        self.assertNotIn(r"\\server\share", serialized)
        self.assertNotIn(r"D:\private", serialized)
        self.assertNotIn("sk-test-secret", serialized)
        self.assertNotIn("session-secret", serialized)
        privacy = audit.source_report_privacy_contract(source_reports)
        self.assertEqual(privacy["status"], "passed")
        self.assertTrue(privacy["passed"])

    def test_candidate_sanitizes_caller_provided_source_reports(self) -> None:
        report = {
            "generated_at": "2026-05-16T00:00:00+00:00",
            "config_summary": {
                "enabled_plugins": [],
                "disabled_plugins": [],
                "unknown_enabled_state_plugins": [],
                "current_profile": {
                    "source": "inferred_from_enabled_plugin_entries",
                    "inferred_profile": "core-dev",
                    "manual_review_required": False,
                    "matched_enabled_known_plugins": [],
                    "unmatched_enabled_plugin_entries": [],
                },
            },
            "warning_severity": {"level": "none"},
            "manual_evidence": {"valid_note_count": 0, "counts_by_evidence_level": {}, "counts_by_action": {}},
            "module_evidence": [],
        }

        candidate = audit.build_profile_apply_candidate(
            report,
            target_profile="core-dev",
            source_reports={
                "json_report": r"C:\Users\lenovo\.codex\sessions\raw.json",
                "markdown_summary": "/home/lenovo/private/raw-summary.md",
                "manual_notes": [r"D:\private\notes.md", ".tmp/notes.md?api_key=sk-test-secret"],
            },
        )
        serialized = json.dumps(candidate, ensure_ascii=False)

        self.assertEqual(candidate["source_reports_privacy"]["status"], "passed")
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("/home/lenovo", serialized)
        self.assertNotIn(r"D:\private", serialized)
        self.assertNotIn("sk-test-secret", serialized)

    def test_build_profile_apply_candidate_is_preview_only_and_reversible(self) -> None:
        report = {
            "generated_at": "2026-05-16T00:00:00+00:00",
            "config_summary": {
                "enabled_plugins": ["browser-use@openai-bundled", "github@openai-curated", "Legacy Plugin"],
                "disabled_plugins": ["Vercel"],
                "unknown_enabled_state_plugins": [],
                "current_profile": {
                    "source": "inferred_from_enabled_plugin_entries",
                    "inferred_profile": "custom_or_unmatched",
                    "manual_review_required": True,
                    "matched_enabled_known_plugins": ["Browser", "GitHub"],
                    "unmatched_enabled_plugin_entries": ["Legacy Plugin"],
                },
            },
            "warning_severity": {"level": "high", "reason": "all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3"},
            "manual_evidence": {
                "valid_note_count": 1,
                "counts_by_evidence_level": {"medium": 1},
                "counts_by_action": {"preview": 1},
            },
            "module_evidence": [
                {
                    "module": "web-saas",
                    "plugins": ["Browser", "GitHub", "Vercel", "Cloudflare"],
                    "strong_total": 10,
                    "strong_helper_calls": 6,
                    "strong_skill_path_reads": 4,
                    "medium_evidence_rationale": "mapped_tool_calls_present_manual_review_required",
                    "weak_plugin_mentions": 2,
                    "cross_project_utility": "manual_review_required",
                    "recommendation": "candidate_for_project_or_default_profile_review",
                }
            ],
        }

        candidate = audit.build_profile_apply_candidate(
            report,
            candidate_id="skills-profile-test",
            target_profile="web-saas",
            source_reports=audit.build_source_reports(
                r"D:\private\skills-usage-audit-30d.json",
                r"D:\private\skills-usage-summary.md",
                [r"D:\private\manual-notes.md"],
            ),
            candidate_gate={
                "status": "allowed",
                "allowed": True,
                "blockers": [],
                "summary_reviewed": True,
                "audit_window_at_least_30_days": True,
            },
        )

        self.assertEqual(candidate["candidate_id"], "skills-profile-test")
        self.assertEqual(candidate["approval_state"], "preview-only")
        self.assertFalse(candidate["mutates_config"])
        self.assertFalse(candidate["edits_plugin_cache"])
        self.assertFalse(candidate["hard_load_apply_performed"])
        self.assertTrue(candidate["explicit_authorization_required_for_apply"])
        self.assertTrue(candidate["ordinary_continue_or_generic_confirmation_is_not_apply_authorization"])
        self.assertEqual(candidate["target_profile"]["name"], "web-saas")
        self.assertEqual(candidate["plugin_diff"]["add_to_default"], ["Cloudflare", "Vercel"])
        self.assertEqual(candidate["plugin_diff"]["keep_enabled"], ["Browser", "GitHub"])
        self.assertIn("Legacy Plugin", candidate["plugin_diff"]["unknown_current_enabled_entries_requiring_manual_review"])
        self.assertEqual(candidate["evidence_basis"]["target_module_evidence"]["strong_total"], 10)
        self.assertEqual(candidate["rollback_path"]["restore_command"], "set_plugin_profile.ps1 -RestoreLatest -Apply")
        self.assertTrue(candidate["candidate_generation_gate"]["allowed"])
        self.assertTrue(candidate["validation_plan"])
        self.assertEqual(candidate["source_reports_privacy"]["status"], "passed")
        self.assertIn("[REDACTED_PATH]", json.dumps(candidate["source_reports"], ensure_ascii=False))
        self.assertNotIn(r"D:\private", json.dumps(candidate, ensure_ascii=False))

    def test_render_profile_apply_candidate_markdown_is_non_mutating(self) -> None:
        candidate = audit.build_profile_apply_candidate(
            {
                "generated_at": "2026-05-16T00:00:00+00:00",
                "config_summary": {
                    "enabled_plugins": [],
                    "disabled_plugins": [],
                    "unknown_enabled_state_plugins": [],
                    "current_profile": {
                        "inferred_profile": "core-dev",
                        "source": "inferred_from_enabled_plugin_entries",
                        "manual_review_required": False,
                        "matched_enabled_known_plugins": [],
                        "unmatched_enabled_plugin_entries": [],
                    },
                },
                "warning_severity": {"level": "none"},
                "manual_evidence": {},
                "module_evidence": [],
            },
            target_profile="core-dev",
            candidate_gate={
                "status": "blocked",
                "allowed": False,
                "blockers": ["summary_not_marked_reviewed"],
                "summary_reviewed": False,
                "audit_window_at_least_30_days": True,
                "field_contract": {"status": "failed"},
            },
        )

        summary = audit.render_candidate_markdown(candidate)

        self.assertIn("# Codex Skills Profile Apply Candidate", summary)
        self.assertIn("Approval state: `preview-only`", summary)
        self.assertIn("Gate status: `blocked`", summary)
        self.assertIn("Privacy contract: `passed`", summary)
        self.assertIn("Privacy violations: `none`", summary)
        self.assertIn("Blockers: `summary_not_marked_reviewed`", summary)
        self.assertIn("Field contract: `failed`", summary)
        self.assertIn("Did not modify user-level `config.toml`.", summary)
        self.assertIn("Did not infer approval from generic continue/confirmation.", summary)

    def test_decision_recommendation_buckets_are_advisory_and_rendered(self) -> None:
        codex_home = self.make_codex_home("skills-audit-decision-buckets")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )
        module_evidence = [
            {"module": "core-dev", "recommendation": "candidate_for_project_or_default_profile_review"},
            {"module": "pdf", "recommendation": "keep_module_on_demand_and_continue_audit"},
            {"module": "ops", "recommendation": "mentioned_only_do_not_apply_without_strong_evidence"},
            {"module": "twilio", "recommendation": "no_recent_evidence_keep_dormant_not_deleted"},
        ]
        decision = audit.build_decision_recommendation(
            module_evidence,
            {"level": "high"},
            {"state": "summary-reviewed", "next_action": "create_profile_apply_candidate"},
        )

        self.assertEqual(decision["buckets"]["profile_review_candidates"], ["core-dev"])
        self.assertEqual(decision["buckets"]["on_demand_soft_load"], ["pdf"])
        self.assertEqual(decision["buckets"]["manual_review_medium_or_weak"], ["ops"])
        self.assertEqual(decision["buckets"]["dormant_restorable"], ["twilio"])
        self.assertFalse(decision["profile_apply_allowed"])

        report = audit.build_report(args)
        report["decision_recommendation"] = decision
        summary = audit.render_markdown_summary(report)

        self.assertIn("Decision status: `advisory_only_no_profile_apply`", summary)
        self.assertIn("Warning pressure: `high`", summary)
        self.assertIn("Profile apply allowed by summary: `False`", summary)
        self.assertIn("Profile review candidates: `core-dev`", summary)
        self.assertIn("On-demand soft-load modules: `pdf`", summary)
        self.assertIn("Manual-review medium/weak modules: `ops`", summary)
        self.assertIn("Dormant/restorable modules: `twilio`", summary)

    def test_render_markdown_summary_is_sanitized_and_non_mutating(self) -> None:
        codex_home = self.make_codex_home("skills-audit-summary")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
            late_run=False,
            missed_weekly_runs=None,
            manual_notes=[],
            output=None,
            summary_output=None,
            candidate_output=None,
            candidate_summary_output=None,
            summary_reviewed=False,
        )

        summary = audit.render_markdown_summary(audit.build_report(args))

        self.assertIn("# Codex Skills Usage Audit Summary", summary)
        self.assertIn("## Audit window", summary)
        self.assertIn("Field contract: `passed`", summary)
        self.assertIn("## Current configuration surface", summary)
        self.assertIn("## Warning conclusion", summary)
        self.assertIn("## Warning triage", summary)
        self.assertIn("Window policy:", summary)
        self.assertIn("## Module evidence", summary)
        self.assertIn("## Noise review", summary)
        self.assertIn("Raw noise tokens retained:", summary)
        self.assertIn("Removed explicit-skill noise token samples: `none`", summary)
        self.assertIn("Max noise token length:", summary)
        self.assertIn("Token privacy policy:", summary)
        self.assertIn("## Manual evidence", summary)
        self.assertIn("Source paths retained:", summary)
        self.assertIn("Max source path length:", summary)
        self.assertIn("Source path privacy policy:", summary)
        self.assertIn("## Decision recommendation", summary)
        self.assertIn("Decision status: `advisory_only_no_profile_apply`", summary)
        self.assertIn("Profile review candidates:", summary)
        self.assertIn("On-demand soft-load modules:", summary)
        self.assertIn("Manual-review medium/weak modules:", summary)
        self.assertIn("Dormant/restorable modules:", summary)
        self.assertIn("Reports with failed field contracts must be rerun or fixed before profile decisions.", summary)
        self.assertIn("## Risks and restore path", summary)
        self.assertIn("Inferred current profile:", summary)
        self.assertIn("Last 7d budget warning count:", summary)
        self.assertIn("Cross-project utility", summary)
        self.assertIn("set_plugin_profile.ps1 -RestoreLatest -Apply", summary)
        self.assertIn("## Non-action list", summary)
        self.assertIn("Did not modify user-level `config.toml`.", summary)
        self.assertIn("Did not perform hard-load/profile apply.", summary)
        self.assertNotIn("sk-", summary)
        self.assertNotIn("access_token=", summary)


if __name__ == "__main__":
    unittest.main()
