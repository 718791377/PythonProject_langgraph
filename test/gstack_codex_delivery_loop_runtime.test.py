#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools" / "gstack_codex_delivery_loop_runtime.py"
CHECKER = ROOT / "tools" / "check_gstack_codex_delivery_loop.py"


class GstackCodexDeliveryLoopRuntimeTests(unittest.TestCase):
    maxDiff = None

    def run_json(self, script: Path, *args: str, check: bool = True) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, str(script), *args, "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
        if check and proc.returncode != 0:
            self.fail(json.dumps(payload, ensure_ascii=False, indent=2) + "\n" + proc.stderr)
        return proc.returncode, payload, proc.stdout + proc.stderr

    def write_install_receipt(self, directory: Path) -> Path:
        receipt = {
            "tool_name": "gstack",
            "installed_version": "fixture-pin",
            "source_pin": "garrytan/gstack@fixture",
            "source_url": "https://github.com/garrytan/gstack",
            "install_path": str(directory / "fake-install"),
            "wrapper_path": sys.executable,
            "state_path": str(directory / "fake-state"),
            "smoke_test_command": "gstack --help",
            "smoke_test_result": {"status": "pass"},
            "updater_command": "git clone --depth 1 https://github.com/garrytan/gstack.git",
            "rollback_pointer": str(directory / "rollback-pointer"),
            "owner_lane": "gstack-codex-delivery-loop",
            "redaction_status": "no_secrets",
        }
        path = directory / "install-gstack.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_all_dry_run_commands_emit_authority_decision_and_never_mutate(self) -> None:
        for action in ("analyze", "plan-dry-run", "review-dry-run", "qa-dry-run", "ship-dry-run"):
            with self.subTest(action=action):
                code, payload, output = self.run_json(RUNTIME, action, "--root", str(ROOT))
                self.assertEqual(code, 0)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["action"], action)
                self.assertIn(payload["delivery_loop_stage"], ["Think", "Plan", "Build", "Review", "Test", "Ship", "Reflect"])
                self.assertGreaterEqual(len(payload["authority_decision"]), 1)
                self.assertEqual(payload["authority_decision"][0]["priority_order"], "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit")
                self.assertFalse(payload["mutation"]["file_write_performed"])
                self.assertFalse(payload["mutation"]["user_level_state_mutated"])
                self.assertFalse(payload["mutation"]["remote_state_mutated"])
                self.assertFalse(payload["safety"]["browser_launch_performed"])
                self.assertFalse(payload["safety"]["telemetry_enabled"])
                self.assertNotIn(str(ROOT), output)

    def test_smoke_without_install_receipt_writes_blocked_receipt_not_smoke_tested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp) / "receipts"
            code, payload, output = self.run_json(RUNTIME, "smoke", "--receipt-dir", str(receipt_dir))

            self.assertEqual(code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["counts"]["blocked"], 1)
            self.assertEqual(payload["counts"]["smoke_tested"], 0)
            self.assertNotIn(str(receipt_dir), output)
            receipts = list(receipt_dir.glob("*.json"))
            self.assertEqual(len(receipts), 1)
            receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
            self.assertFalse(receipt["smoke_tested"])
            self.assertEqual(receipt["r4_status"], "blocked")
            self.assertIn("install_receipt_required", receipt["blockers"])
            self.assertEqual(receipt["authority_decision"][0]["decision"], "blocked")

            check_code, check_payload, _ = self.run_json(CHECKER, "--root", str(ROOT), "--receipt-dir", str(receipt_dir))
            self.assertEqual(check_code, 0)
            self.assertTrue(check_payload["ok"])
            self.assertEqual(check_payload["counts"]["blocked_or_not_installed"], 1)
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 0)

    def test_valid_fixture_help_receipt_passes_require_smoke_tested_without_path_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            receipt_dir = base / "smoke"
            install_receipt = self.write_install_receipt(base)
            code, payload, output = self.run_json(
                RUNTIME,
                "smoke",
                "--receipt-dir",
                str(receipt_dir),
                "--install-receipt",
                str(install_receipt),
            )

            self.assertEqual(code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["counts"]["smoke_tested"], 1)
            self.assertEqual(payload["counts"]["blocked"], 0)
            self.assertNotIn(str(base), output)
            self.assertNotIn(sys.executable, output)

            check_code, check_payload, check_output = self.run_json(
                CHECKER,
                "--root",
                str(ROOT),
                "--receipt-dir",
                str(receipt_dir),
                "--require-smoke-tested",
            )
            self.assertEqual(check_code, 0)
            self.assertTrue(check_payload["ok"])
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 1)
            self.assertNotIn(str(base), check_output)
            self.assertNotIn(sys.executable, check_output)


if __name__ == "__main__":
    unittest.main()
