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
SCRIPT = ROOT / "tools" / "check_r6_live_runtime_receipts.py"
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

spec = importlib.util.spec_from_file_location("check_r6_live_runtime_receipts", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class R6LiveRuntimeReceiptTests(unittest.TestCase):
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

    def write_receipt(self, lane: str, *, live_mode: str = "live-executed", overrides: dict | None = None) -> Path:
        payload = module.fixture_for_lane(lane, live_mode=live_mode)
        if overrides:
            payload.update(overrides)
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        path = tmp / f"{lane}-{live_mode}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_self_test_covers_all_r6_plan_lanes(self) -> None:
        payload = self.run_cli("--root", str(ROOT))
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["self_test"]["counts"]["profiles"], 14)
        self.assertIn("spec-kit-subordinate-adapter-governance", payload["known_lanes"])
        self.assertIn("R6_WXWORK_MESSAGE_TEMPLATE", payload["canonical_env_keys"])

    def test_valid_blocked_and_live_executed_receipts_pass_for_every_lane(self) -> None:
        for lane in module.LANE_PROFILES:
            for mode in ("blocked", "live-executed"):
                with self.subTest(lane=lane, mode=mode):
                    receipt = self.write_receipt(lane, live_mode=mode)
                    payload = self.run_cli("--root", str(ROOT), "--lane", lane, "--receipt", str(receipt))
                    self.assertTrue(payload["receipt_summary"]["r6_live_valid"], payload["errors"])

    def test_live_ready_accepts_env_hash_without_external_execution(self) -> None:
        receipt = self.write_receipt("user-level-browser-cli-adapter-boundary", live_mode="live-ready")
        payload = self.run_cli(
            "--root",
            str(ROOT),
            "--lane",
            "browser-cli-adapter",
            "--receipt",
            str(receipt),
        )
        self.assertTrue(payload["receipt_summary"]["r6_live_valid"], payload["errors"])
        self.assertFalse(payload["receipt_summary"]["live_executed"])
        self.assertEqual(payload["receipt_summary"]["external_side_effects"], "none")

    def test_rejects_remote_mutation_missing_lease_rollback_cleanup_and_authority_order(self) -> None:
        cases = {
            "remote": {"remote_publication_mutated": True},
            "missing_lease": {"owner_lease": {}},
            "missing_rollback": {"rollback_ready": False},
            "missing_cleanup": {"cleanup_evidence": {"status": "fail"}},
            "authority": {"authority_decision": {"decision": "r6", "priority_order": "Spec Kit > OpenSpec"}},
        }
        for name, override in cases.items():
            with self.subTest(name=name):
                receipt = self.write_receipt("codex-harnesses-governance", overrides=override)
                payload = self.run_cli("--root", str(ROOT), "--lane", "codex-harnesses", "--receipt", str(receipt), expect=1)
                joined = "\n".join(payload["errors"])
                self.assertIn("must", joined.lower() + " must")
                self.assertFalse(payload["receipt_summary"]["r6_live_valid"])

    def test_rejects_raw_secret_wxwork_body_and_browser_payload(self) -> None:
        wx = module.fixture_for_lane("wxwork-cli", live_mode="live-executed")
        wx["execution_receipt"]["message_body"] = "raw message body must not be committed"
        browser = module.fixture_for_lane("browser-cli-adapter", live_mode="live-executed")
        browser["execution_receipt"]["raw_browser_payload"] = {"cookies": "token=secret-value"}
        secret = module.fixture_for_lane("mcp-skills-cli", live_mode="live-executed")
        secret["execution_receipt"]["api_token"] = "token=raw-secret-value"
        for name, payload in {"wx": wx, "browser": browser, "secret": secret}.items():
            with self.subTest(name=name):
                tmp = Path(tempfile.mkdtemp())
                self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
                receipt = tmp / f"{name}.json"
                receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                result = self.run_cli("--root", str(ROOT), "--receipt", str(receipt), expect=1)
                self.assertIn("sensitive", "\n".join(result["errors"]))

    def test_wxwork_live_executed_requires_visual_menu_sequence_and_rejects_direct_paste(self) -> None:
        payload = module.fixture_for_lane("wxwork-cli", live_mode="live-executed")
        payload["execution_receipt"].update(
            {
                "cli_anything_visual_rendering_verified": False,
                "visual_control_verified": False,
                "right_click_member_performed": False,
                "mention_menu_selected": False,
                "direct_paste_mention_used": True,
            }
        )
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        receipt = tmp / "bad-wxwork-sequence.json"
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.run_cli("--root", str(ROOT), "--receipt", str(receipt), expect=1)
        joined = "\n".join(result["errors"])
        self.assertIn("execution_receipt_cli_anything_visual_rendering_verified_required", joined)
        self.assertIn("execution_receipt_visual_control_verified_required", joined)
        self.assertIn("execution_receipt_right_click_member_performed_required", joined)
        self.assertIn("execution_receipt_mention_menu_selected_required", joined)
        self.assertIn("direct_paste_mention_used_must_be_false", joined)

    def test_wxwork_live_executed_rejects_raw_group_member_and_screenshot_fields(self) -> None:
        payload = module.fixture_for_lane("wxwork-cli", live_mode="live-executed")
        payload["execution_receipt"].update(
            {
                "target_group": "raw group value",
                "target_member": "raw member value",
                "screenshot_path": "C:\\Users\\private\\Desktop\\wxwork.png",
            }
        )
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        receipt = tmp / "raw-wxwork-targets.json"
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.run_cli("--root", str(ROOT), "--receipt", str(receipt), expect=1)
        joined = "\n".join(result["errors"])
        self.assertIn("sensitive_field_present:$.execution_receipt.target_group", joined)
        self.assertIn("sensitive_field_present:$.execution_receipt.target_member", joined)
        self.assertIn("sensitive_field_present:$.execution_receipt.screenshot_path", joined)

    def test_spec_kit_apply_boundaries_are_distinct_and_checked(self) -> None:
        sandbox = module.fixture_for_lane("spec-kit-subordinate", live_mode="live-executed")
        sandbox["execution_receipt"].update({"spec_kit_apply_mode": "sandbox", "repository_surfaces_written": False})
        repo = module.fixture_for_lane("spec-kit-subordinate", live_mode="live-executed")
        repo["execution_receipt"].update({
            "spec_kit_apply_mode": "repository",
            "comet_openspec_owner": True,
            "allowed_repo_surfaces": [".specify/", "specs/"],
            "spec_kit_subordinate": True,
        })
        template = module.fixture_for_lane("spec-kit-subordinate", live_mode="live-executed")
        template["template_distribution"] = "project-general-full"
        template["execution_receipt"].update({"spec_kit_apply_mode": "template", "spec_kit_subordinate": True})
        for name, payload in {"sandbox": sandbox, "repository": repo, "template": template}.items():
            with self.subTest(name=name):
                blockers = module.validate_lane_receipt(payload, "spec-kit-subordinate")
                self.assertEqual(blockers, [])
        bad = module.fixture_for_lane("spec-kit-subordinate", live_mode="live-executed")
        bad["execution_receipt"].update({"spec_kit_apply_mode": "repository", "comet_openspec_owner": False})
        self.assertIn("spec_kit_repository_apply_requires_comet_openspec_owner", module.validate_lane_receipt(bad, "spec-kit-subordinate"))

    def test_directory_coverage_requires_all_lanes_and_accepts_blocked_sensitive_lanes(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        receipts = tmp / "receipts"
        receipts.mkdir()
        for lane, profile in module.LANE_PROFILES.items():
            mode = "live-executed" if profile.side_effect == "none" else "blocked"
            path = receipts / f"{lane}.json"
            path.write_text(json.dumps(module.fixture_for_lane(lane, live_mode=mode), ensure_ascii=False, indent=2), encoding="utf-8")
        payload = self.run_cli("--root", str(tmp), "--receipt-dir", str(receipts), "--require-coverage")
        self.assertTrue(payload["coverage_summary"]["coverage_ok"], payload["errors"])
        self.assertEqual(payload["coverage_summary"]["counts"]["accepted_lanes"], 14)
        self.assertEqual(payload["coverage_summary"]["missing_lanes"], [])

    def test_clean_checkout_coverage_uses_tracked_fixture_without_omx_receipts(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        fixture = tmp / "tools" / "r6_live_runtime_receipts" / "coverage-fixture"
        fixture.mkdir(parents=True)
        for lane, profile in module.LANE_PROFILES.items():
            mode = "live-executed" if profile.side_effect == "none" else "blocked"
            (fixture / f"{lane}.json").write_text(
                json.dumps(module.fixture_for_lane(lane, live_mode=mode), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        payload = self.run_cli("--root", str(tmp), "--require-coverage")
        self.assertTrue(payload["coverage_summary"]["coverage_ok"], payload["errors"])
        self.assertEqual(payload["coverage_summary"]["receipt_dir"], "tools/r6_live_runtime_receipts/coverage-fixture")
        self.assertEqual(payload["coverage_summary"]["counts"]["accepted_lanes"], 14)

    def test_directory_coverage_fails_when_default_safe_lane_is_only_blocked(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        receipts = tmp / "receipts"
        receipts.mkdir()
        for lane, profile in module.LANE_PROFILES.items():
            mode = "live-executed" if profile.side_effect == "none" else "blocked"
            if lane == "worktree-receipt-claim-lifecycle":
                mode = "blocked"
            path = receipts / f"{lane}.json"
            path.write_text(json.dumps(module.fixture_for_lane(lane, live_mode=mode), ensure_ascii=False, indent=2), encoding="utf-8")
        payload = self.run_cli("--root", str(tmp), "--receipt-dir", str(receipts), "--require-coverage", expect=1)
        self.assertIn("worktree-receipt-claim-lifecycle", payload["coverage_summary"]["missing_lanes"])
        self.assertIn("coverage_missing_lane:worktree-receipt-claim-lifecycle", payload["errors"])

    def test_directory_coverage_freshness_rejects_old_receipts(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda p=tmp: __import__("shutil").rmtree(p, ignore_errors=True))
        receipts = tmp / "receipts"
        receipts.mkdir()
        lane = "worktree-receipt-claim-lifecycle"
        payload = module.fixture_for_lane(lane, live_mode="live-executed")
        payload["generated_at"] = "2000-01-01T00:00:00+00:00"
        (receipts / f"{lane}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        result = self.run_cli("--root", str(tmp), "--receipt-dir", str(receipts), "--require-coverage", "--max-age-hours", "1", expect=1)
        self.assertTrue(result["coverage_summary"]["stale_receipts"])
        self.assertIn(lane, result["coverage_summary"]["missing_lanes"])


if __name__ == "__main__":
    unittest.main()
