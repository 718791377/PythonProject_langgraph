#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_user_level_cloakbrowser_academic_runtime.py"
PLAN_EN = ROOT / "docs_bilingual" / "implementation_plans" / "user_level_cloakbrowser_academic_research_runtime_plan.md"
PLAN_ZH = ROOT / "docs_bilingual" / "implementation_plans" / "user_level_cloakbrowser_academic_research_runtime_plan.zh-CN.md"


class UserLevelCloakBrowserAcademicRuntimeTests(unittest.TestCase):
    maxDiff = None

    def run_checker(self, *args: str, expect: int = 0) -> dict:
        proc = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(ROOT), "--json", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc

    def test_plan_surfaces_are_registered_and_decision_complete(self) -> None:
        data = self.run_checker()
        self.assertTrue(data["ok"], data["errors"])
        self.assertIn(data["plans"][PLAN_EN.relative_to(ROOT).as_posix()]["status"], {"planned-local", "R6 live-executed"})
        self.assertIn(data["plans"][PLAN_ZH.relative_to(ROOT).as_posix()]["status"], {"planned-local", "R6 live-executed"})
        self.assertFalse(data["policy"]["docker_install_allowed"])
        self.assertFalse(data["policy"]["native_codex_files_mutated"])
        self.assertFalse(data["policy"]["remote_publication_allowed"])
        self.assertEqual(data["sources"]["cloakbrowser"]["pypi_version"], "0.3.31")
        self.assertEqual(data["sources"]["cloakbrowser"]["npm_version"], "0.3.31")

    def test_receipt_checker_accepts_hash_only_live_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "cloakbrowser-python",
                "runtime_stage": "R6 live-executed",
                "source_url": "https://github.com/CloakHQ/CloakBrowser",
                "source_ref": "main",
                "installed_version": "0.3.31",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "smoke_result": {"status": "pass", "command_hash": "d" * 16},
                "rollback_pointer_hash": "e" * 16,
                "redaction_status": "pass",
                "raw_paths_included": False,
                "remote_publication_mutated": False,
            }
            (receipt_dir / "cloakbrowser-python.json").write_text(json.dumps(receipt), encoding="utf-8")
            (receipt_dir / "summary.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir))
            self.assertEqual(data["receipt_summary"]["accepted"], ["cloakbrowser-python"])
            self.assertEqual(data["receipt_summary"]["sidecars_skipped"], ["summary.json"])

    def test_receipt_checker_rejects_raw_paths_and_remote_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "academic-research-suite",
                "runtime_stage": "R6 live-executed",
                "source_url": "https://github.com/Imbad0202/academic-research-skills-codex",
                "source_ref": "main",
                "installed_version": "0.1.11",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "smoke_result": {"status": "pass", "command_hash": "d" * 16},
                "rollback_pointer_hash": "e" * 16,
                "redaction_status": "pass",
                "raw_paths_included": True,
                "install_root": "C:/Users/lenovo/.codex/skills/academic-research-suite",
                "remote_publication_mutated": True,
            }
            (receipt_dir / "academic-research-suite.json").write_text(json.dumps(receipt), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir), "--require-live", expect=1)
            self.assertIn("receipt:academic-research-suite.json:raw_paths_included_must_be_false", data["errors"])
            self.assertIn("receipt:academic-research-suite.json:remote_publication_mutated_must_be_false", data["errors"])


if __name__ == "__main__":
    unittest.main()
