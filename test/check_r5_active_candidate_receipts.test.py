#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_r5_active_candidate_receipts.py"
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

spec = importlib.util.spec_from_file_location("check_r5_active_candidate_receipts", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class R5ActiveCandidateReceiptTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str, expect: int = 0) -> dict:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def write_receipt(self, lane: str, overrides: dict | None = None) -> Path:
        payload = module.fixture_for_lane(lane)
        if overrides:
            payload.update(overrides)
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        path = tmp / f"{lane}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_self_test_covers_all_r5_lanes(self) -> None:
        payload = self.run_cli("--root", str(ROOT))
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["self_test"]["counts"]["profiles"], len(module.PROFILES))
        self.assertIn("mcp-skills-cli", payload["known_lanes"])
        self.assertIn("spec-kit-subordinate", payload["known_lanes"])

    def test_valid_mcp_skills_active_candidate_passes_and_is_non_mutating(self) -> None:
        receipt = self.write_receipt("mcp-skills-cli")
        payload = self.run_cli(
            "--root",
            str(ROOT),
            "--lane",
            "mcp-skills-cli",
            "--receipt",
            str(receipt),
        )
        self.assertTrue(payload["receipt_summary"]["active_candidate_valid"], payload["errors"])
        self.assertFalse(payload["mutates_user_level_state"])
        self.assertFalse(payload["runs_external_tool"])
        self.assertFalse(payload["mutates_remote_publication"])

    def test_remote_publication_mutation_fails_for_every_lane(self) -> None:
        for lane in module.PROFILES:
            with self.subTest(lane=lane):
                receipt = self.write_receipt(lane, {"remote_publication_mutated": True})
                payload = self.run_cli(
                    "--root",
                    str(ROOT),
                    "--lane",
                    lane,
                    "--receipt",
                    str(receipt),
                    expect=1,
                )
                self.assertFalse(payload["receipt_summary"]["active_candidate_valid"])
                self.assertIn("remote_publication", "\n".join(payload["errors"]))

    def test_blocked_or_dry_run_receipts_do_not_count_as_r5_active_candidate(self) -> None:
        for lane in module.PROFILES:
            with self.subTest(lane=lane):
                receipt = self.write_receipt(
                    lane,
                    {
                        "runtime_stage": "blocked",
                        "blocked": True,
                        "dry_run_only": True,
                        "adoption_decision": "blocked",
                    },
                )
                payload = self.run_cli(
                    "--root",
                    str(ROOT),
                    "--lane",
                    lane,
                    "--receipt",
                    str(receipt),
                    expect=1,
                )
                self.assertFalse(payload["receipt_summary"]["active_candidate_valid"])
                self.assertIn("active_candidate_runtime_stage_must_be_r5", payload["errors"])

    def test_spec_kit_subordinate_rejects_live_specify_surface(self) -> None:
        receipt = self.write_receipt("spec-kit-subordinate", {"runs_specify": True})
        payload = self.run_cli(
            "--root",
            str(ROOT),
            "--lane",
            "spec-kit-subordinate",
            "--receipt",
            str(receipt),
            expect=1,
        )
        self.assertIn("runs_specify_must_be_false", payload["errors"])


if __name__ == "__main__":
    unittest.main()
