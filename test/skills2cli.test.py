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
        self.assertEqual(payload["routing_evidence"]["surface_type"], "skill_profile_suggestion")
        self.assertFalse(payload["routing_evidence"]["native_subagent_evidence"])
        self.assertFalse(payload["routing_evidence"]["expert_evidence"])
        self.assertTrue(payload["routing_evidence"]["separate_native_agent_required_for_expert_claims"])
        self.assertTrue(any(item["profile"] == "browser-automation" for item in payload["suggestions"]))

    def test_warning_audit_summarizes_and_redacts_warning_text(self) -> None:
        _repo, codex_home = self.make_workspace("warnings")
        sessions = codex_home / "sessions"
        sessions.mkdir(parents=True)
        now = datetime.now(timezone.utc).isoformat()
        warning_message = (
            r"? Exceeded skills context budget of 2%. All skill descriptions were removed. "
            r"? Skipped loading 2 skill(s) due to invalid SKILL.md files. "
            r"C:\Users\lenovo\.codex\plugins\cache\secret\SKILL.md api_key=sk-test-warning-secret"
        )
        (sessions / "session.jsonl").write_text(
            json.dumps({"timestamp": now, "type": "event_msg", "payload": {"message": warning_message}}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        payload = self.run_cli("audit", "warnings", "--since", "7d", "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["command"], "audit warnings")
        self.assertEqual(payload["budget_warning_count"], 1)
        self.assertGreaterEqual(payload["skipped_loading_count"], 1)
        self.assertFalse(payload["raw_log_paths_retained"])
        self.assertFalse(payload["raw_skill_bodies_retained"])
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-warning-secret", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)

    def test_warning_audit_also_reads_logs_2_sqlite_without_raw_paths(self) -> None:
        _repo, codex_home = self.make_workspace("sqlite-warnings")
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
                    "All skill descriptions were removed and 16 additional skills were not included. "
                    r"Skipped loading 286 skill(s) due to invalid SKILL.md files. "
                    r"C:\Users\lenovo\.codex\skills\bad\SKILL.md api_key=sk-test-sqlite-secret",
                ),
            )

        payload = self.run_cli("audit", "warnings", "--since", "1d", "--codex-home", str(codex_home), "--json")
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["command"], "audit warnings")
        self.assertEqual(payload["budget_warning_count"], 1)
        self.assertGreaterEqual(payload["skipped_loading_count"], 1)
        self.assertEqual(payload["all_descriptions_removed_count"], 1)
        self.assertEqual(payload["max_omitted_additional_skills"], 16)
        self.assertEqual({item["source"] for item in payload["sources"]}, {"sessions_jsonl", "logs_2.sqlite"})
        sqlite_source = next(item for item in payload["sources"] if item["source"] == "logs_2.sqlite")
        self.assertTrue(sqlite_source["available"])
        self.assertEqual(sqlite_source["budget_warning_count"], 1)
        self.assertIn("sessions_jsonl_and_logs_2_sqlite", payload["log_source_review"])
        self.assertFalse(payload["raw_log_paths_retained"])
        self.assertFalse(payload["raw_skill_bodies_retained"])
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-sqlite-secret", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)


if __name__ == "__main__":
    unittest.main()
