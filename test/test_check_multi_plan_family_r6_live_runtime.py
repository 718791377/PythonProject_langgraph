#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_multi_plan_family_r6_live_runtime.py"
R6_SCRIPT = ROOT / "tools" / "check_r6_live_runtime_receipts.py"
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

spec = importlib.util.spec_from_file_location("check_multi_plan_family_r6_live_runtime", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

r6_spec = importlib.util.spec_from_file_location("check_r6_live_runtime_receipts_for_family_test", R6_SCRIPT)
r6_module = importlib.util.module_from_spec(r6_spec)
assert r6_spec and r6_spec.loader
sys.modules[r6_spec.name] = r6_module
r6_spec.loader.exec_module(r6_module)


class MultiPlanFamilyR6LiveRuntimeTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str, root: Path = ROOT, expect: int = 0) -> dict:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args, "--json"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def full_fixture_receipt_dir(self) -> Path:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: shutil.rmtree(p, ignore_errors=True))
        receipts = tmp / "receipts"
        receipts.mkdir()
        for lane in r6_module.LANE_PROFILES:
            payload = r6_module.fixture_for_lane(lane, live_mode="live-executed")
            (receipts / f"{lane}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return receipts

    def test_current_repository_family_has_exact_classifications_and_r6_coverage(self) -> None:
        payload = self.run_cli("--receipt-dir", str(self.full_fixture_receipt_dir()), "--require-coverage")
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["priority_order"], "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit")
        self.assertEqual(payload["counts"]["missing_classification"], 0)
        self.assertEqual(payload["counts"]["successor_owned_migration_source"], 2)
        self.assertGreaterEqual(payload["counts"]["direct_r6_lane"], 14)
        self.assertGreater(payload["counts"]["governance_checker_runtime"], 20)
        self.assertEqual(payload["counts"]["restored_deleted_migration_sources"], 0)
        self.assertEqual(payload["counts"]["stale_status_findings"], 0)
        direct = payload["classifications"]["user_level_cli_anything_wxwork_cli_governance_plan"]
        self.assertEqual(direct["classification"], "direct-r6-lane")
        self.assertEqual(direct["lane"], "user-level-cli-anything-wxwork-cli-governance")
        self.assertEqual(direct["r6_receipt_mode"], "live-executed")
        self.assertEqual(
            payload["classifications"]["user_level_mcp_skills_discovery_facade_plan"]["successor_plan"],
            "user_level_mcp_skills_cli_runtime_plan",
        )
        self.assertFalse(payload["mutates_remote_publication"])
        self.assertFalse(payload["runs_external_tool"])

    def test_rejects_missing_successor_for_deleted_migration_source(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        shutil.copytree(ROOT / "docs_bilingual", tmp / "docs_bilingual")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        # Keep receipt checker importable but simulate a bad migration map.
        payload = self.run_cli(
            "--receipt-dir",
            str(ROOT / ".omx" / "r6-live-runtime" / "receipts"),
            "--migration-source",
            "user_level_mcp_skills_discovery_facade_plan:missing_successor_plan:missing-lane",
            root=tmp,
            expect=1,
        )
        self.assertIn("migration_source_successor_missing:user_level_mcp_skills_discovery_facade_plan", payload["errors"])

    def test_rejects_restored_deleted_migration_source_plan(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        shutil.copytree(ROOT / "docs_bilingual", tmp / "docs_bilingual")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        restored = tmp / "docs_bilingual" / "implementation_plans" / "user_level_mcp_skills_discovery_facade_plan.md"
        restored.write_text(
            "\n".join(
                [
                    "---",
                    "doc_id: user_level_mcp_skills_discovery_facade_plan",
                    "lang: en",
                    "status: active",
                    "doc_class: implementation_plan",
                    "parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md",
                    "---",
                    "# Restored deleted migration source",
                ]
            ),
            encoding="utf-8",
        )
        payload = self.run_cli(
            "--receipt-dir",
            str(self.full_fixture_receipt_dir()),
            "--require-coverage",
            root=tmp,
            expect=1,
        )
        self.assertIn("restored_deleted_migration_source:user_level_mcp_skills_discovery_facade_plan", payload["errors"])
        self.assertEqual(payload["counts"]["restored_deleted_migration_sources"], 1)

    def test_rejects_stale_r5_wording_when_direct_r6_receipt_exists(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        shutil.copytree(ROOT / "docs_bilingual", tmp / "docs_bilingual")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        plan = tmp / "docs_bilingual" / "implementation_plans" / "user_level_cli_anything_wxwork_cli_governance_plan.md"
        text = plan.read_text(encoding="utf-8-sig")
        marker = "Status: implemented-local"
        self.assertIn(marker, text)
        plan.write_text(text.replace(marker, "Status: R5 checker-backed active-candidate gate implemented locally", 1), encoding="utf-8")
        payload = self.run_cli(
            "--receipt-dir",
            str(self.full_fixture_receipt_dir()),
            "--require-coverage",
            root=tmp,
            expect=1,
        )
        self.assertTrue(any(error.startswith("stale_status:user_level_cli_anything_wxwork_cli_governance_plan:") for error in payload["errors"]))


    def test_clean_checkout_family_coverage_uses_tracked_fixture_without_omx_receipts(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        shutil.copytree(ROOT / "docs_bilingual", tmp / "docs_bilingual")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        shutil.rmtree(tmp / ".omx", ignore_errors=True)
        payload = self.run_cli("--require-coverage", root=tmp)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(
            payload["coverage_summary"]["receipt_dir"],
            "tools/r6_live_runtime_receipts/coverage-fixture",
        )
        self.assertGreaterEqual(payload["counts"]["direct_r6_lane"], 14)
        self.assertEqual(payload["coverage_summary"]["counts"]["accepted_lanes"], 14)

    def test_rejects_missing_direct_r6_coverage(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        shutil.copytree(ROOT / "docs_bilingual", tmp / "docs_bilingual")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        receipt_dir = tmp / "receipts"
        receipt_dir.mkdir()
        # Empty receipt dir must fail direct-lane coverage, not silently classify as governance-only.
        payload = self.run_cli("--receipt-dir", str(receipt_dir), "--require-coverage", root=tmp, expect=1)
        self.assertTrue(any(error.startswith("direct_lane_missing_accepted_receipt:") for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
