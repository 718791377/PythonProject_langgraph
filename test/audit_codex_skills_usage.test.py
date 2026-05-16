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
            "payload": {"message": "Using skills: `plugin-modules`, `and`, `unknown-skill`"},
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
        self.assertEqual(report["noise_review"]["explicit_skill_noise_removed"], {"and": 1, "unknown-skill": 1})
        self.assertEqual(
            report["noise_review"]["strong_evidence_policy"],
            "removed_noise_tokens_are_not_counted_as_strong_evidence",
        )

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
            "session_evidence",
            "module_evidence",
            "noise_review",
            "recommendations",
        }
        self.assertLessEqual(required_top_level, set(report))
        self.assertIn("state", report["audit_state"])
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
        self.assertIn("explicit_skills", report["session_evidence"])
        self.assertIsInstance(report["module_evidence"], list)
        self.assertIn("status", report["noise_review"])
        self.assertIn("manual_evidence", report)
        self.assertEqual(report["manual_evidence"]["valid_note_count"], 0)
        self.assertIn("field_contract", report)
        self.assertTrue(report["field_contract"]["passed"])
        self.assertEqual(report["field_contract"]["status"], "passed")
        self.assertIsInstance(report["recommendations"], list)

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
            manual_notes=[str(notes_path)],
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
        self.assertEqual(len(manual["invalid_notes"]), 1)
        self.assertEqual(manual["counts_by_evidence_level"], {"medium": 1})
        note = manual["notes"][0]
        self.assertIn("[REDACTED_PATH]", note["project"])
        self.assertIn("[REDACTED_SECRET]", note["requested_capability"])
        self.assertIn("[REDACTED_SECRET]", note["reason"])
        self.assertNotIn("sk-test-secret", json.dumps(manual, ensure_ascii=False))
        self.assertFalse(manual["raw_notes_retained"])

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

        baseline = audit.build_report(baseline_args)
        weekly = audit.build_report(weekly_args)
        summary = audit.build_report(summary_args)

        self.assertEqual(baseline["audit_state"]["state"], "running")
        self.assertEqual(baseline["audit_state"]["reason"], "baseline_generated")
        self.assertFalse(baseline["audit_state"]["profile_apply_allowed"])
        self.assertEqual(weekly["audit_state"]["state"], "running")
        self.assertEqual(weekly["audit_state"]["reason"], "audit_window_shorter_than_30_days")
        self.assertFalse(weekly["audit_state"]["profile_apply_allowed"])
        self.assertEqual(summary["audit_state"]["state"], "ready-for-summary")
        self.assertEqual(summary["audit_state"]["reason"], "audit_window_at_least_30_days")
        self.assertFalse(summary["audit_state"]["profile_apply_allowed"])

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
            output=None,
            summary_output=None,
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
        self.assertIn("Blockers: `summary_not_marked_reviewed`", summary)
        self.assertIn("Field contract: `failed`", summary)
        self.assertIn("Did not modify user-level `config.toml`.", summary)
        self.assertIn("Did not infer approval from generic continue/confirmation.", summary)

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
        self.assertIn("## Module evidence", summary)
        self.assertIn("## Noise review", summary)
        self.assertIn("## Manual evidence", summary)
        self.assertIn("## Decision recommendation", summary)
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
