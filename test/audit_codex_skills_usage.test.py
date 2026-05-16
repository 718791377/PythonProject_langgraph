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
                "recent_budget_warnings": [],
            }
        )
        high_by_removed_descriptions = audit.build_warning_severity(
            {
                "available": True,
                "budget_warning_count": 1,
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
        )

        report = audit.build_report(args)
        full_rows = [row for row in report["module_evidence"] if row["module"] == "full"]

        self.assertEqual(report["safety"]["audit_only"], True)
        self.assertEqual(report["config_summary"]["enabled_plugins"], ["Browser"])
        self.assertEqual(len(full_rows), 1)
        self.assertIn("Browser", full_rows[0]["plugins"])
        self.assertNotIn("a", full_rows[0]["plugins"])

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
        )

        report = audit.build_report(args)

        required_top_level = {
            "schema_version",
            "generated_at",
            "audit_state",
            "audit_window",
            "safety",
            "config_summary",
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
        self.assertIn("total_skills", report["inventory_summary"])
        self.assertIn("budget_warning_count", report["log_evidence"])
        self.assertIn("level", report["warning_severity"])
        self.assertIn("explicit_skills", report["session_evidence"])
        self.assertIsInstance(report["module_evidence"], list)
        self.assertIn("status", report["noise_review"])
        self.assertIsInstance(report["recommendations"], list)

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
        )
        weekly_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=7,
            since=None,
            baseline=False,
        )
        summary_args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
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

    def test_render_markdown_summary_is_sanitized_and_non_mutating(self) -> None:
        codex_home = self.make_codex_home("skills-audit-summary")
        args = argparse.Namespace(
            root=str(REPO_ROOT),
            codex_home=str(codex_home),
            days=30,
            since=None,
            baseline=False,
        )

        summary = audit.render_markdown_summary(audit.build_report(args))

        self.assertIn("# Codex Skills Usage Audit Summary", summary)
        self.assertIn("## Audit window", summary)
        self.assertIn("## Current configuration surface", summary)
        self.assertIn("## Warning conclusion", summary)
        self.assertIn("## Module evidence", summary)
        self.assertIn("## Noise review", summary)
        self.assertIn("## Decision recommendation", summary)
        self.assertIn("## Non-action list", summary)
        self.assertIn("Did not modify user-level `config.toml`.", summary)
        self.assertIn("Did not perform hard-load/profile apply.", summary)
        self.assertNotIn("sk-", summary)
        self.assertNotIn("access_token=", summary)


if __name__ == "__main__":
    unittest.main()
