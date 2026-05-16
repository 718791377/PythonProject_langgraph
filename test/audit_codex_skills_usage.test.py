import argparse
import importlib.util
import io
import json
import shutil
import sqlite3
import time
import unittest
import uuid
from datetime import timedelta
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
            "audit_window",
            "safety",
            "config_summary",
            "inventory_summary",
            "log_evidence",
            "session_evidence",
            "module_evidence",
            "recommendations",
        }
        self.assertLessEqual(required_top_level, set(report))
        self.assertEqual(report["audit_window"]["days"], 30)
        self.assertTrue(report["safety"]["audit_only"])
        self.assertFalse(report["safety"]["mutates_config"])
        self.assertFalse(report["safety"]["edits_plugin_cache"])
        self.assertFalse(report["safety"]["hard_load_apply_performed"])
        self.assertIn("enabled_plugins", report["config_summary"])
        self.assertIn("total_skills", report["inventory_summary"])
        self.assertIn("budget_warning_count", report["log_evidence"])
        self.assertIn("explicit_skills", report["session_evidence"])
        self.assertIsInstance(report["module_evidence"], list)
        self.assertIsInstance(report["recommendations"], list)


if __name__ == "__main__":
    unittest.main()
