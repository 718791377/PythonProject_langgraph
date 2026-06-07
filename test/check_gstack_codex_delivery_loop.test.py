#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_gstack_codex_delivery_loop.py"


class CheckGstackCodexDeliveryLoopTests(unittest.TestCase):
    maxDiff = None

    def run_checker(self, *args: str, check: bool = True) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(ROOT), *args, "--json"],
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

    def valid_smoke_receipt(self) -> dict:
        return {
            "schema_version": 1,
            "tool_name": "gstack",
            "owner_lane": "gstack-codex-delivery-loop",
            "runtime_stage": "smoke-tested",
            "install_receipt": "receipt-sha256:fixture",
            "smoke_command": "gstack --help",
            "smoke_type": "help",
            "smoke_result": {"status": "pass"},
            "timeout_release": {"status": "pass", "released": True},
            "rollback_pointer": "rollback-sha256:fixture",
            "rollback_ready": True,
            "command_transcript": "gstack help output",
            "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "fixture"},
            "redaction_status": "no_secrets",
            "smoke_tested": True,
            "r4_status": "smoke-tested",
            "authority_decision": [
                {
                    "decision": "allow",
                    "scope": "r4-smoke",
                    "priority_order": "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
                    "reason": "bounded read-only help smoke with receipt evidence",
                }
            ],
            "read_guard": {"status": "pass", "read_only": True, "scope": "help/status/dry-run"},
            "write_guard": {"status": "pass", "write_allowed": False, "write_performed": False},
            "remote_publication_gate": {"status": "blocked", "remote_mutation_allowed": False},
            "browser_guard": {"status": "blocked", "browser_launch_performed": False},
            "telemetry_guard": {"status": "blocked", "telemetry_enabled": False},
            "write_performed": False,
            "live_action_performed": False,
            "sensitive_action_performed": False,
            "user_level_state_mutated": False,
            "remote_state_mutated": False,
            "browser_launch_performed": False,
            "telemetry_enabled": False,
            "codex_launcher_mutated": False,
            "local_main_gate_bypassed": False,
            "active_candidate": False,
        }

    def test_repository_surfaces_pass_default_checker(self) -> None:
        code, payload, _ = self.run_checker()
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["runtime_probe"]["all_required_actions_ok"])
        self.assertIn("gstack_delivery_loop_runtime_plan_ok", payload["info"])

    def test_checker_rejects_forbidden_live_write_and_missing_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            bad = self.valid_smoke_receipt()
            bad.pop("authority_decision")
            bad.update(
                {
                    "smoke_command": "gstack ship --apply --push",
                    "write_performed": True,
                    "remote_state_mutated": True,
                    "browser_launch_performed": True,
                    "telemetry_enabled": True,
                }
            )
            (receipt_dir / "smoke-gstack.json").write_text(json.dumps(bad, ensure_ascii=False, indent=2), encoding="utf-8")

            code, payload, output = self.run_checker("--receipt-dir", str(receipt_dir), "--require-smoke-tested", check=False)
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            errors = "\n".join(payload["errors"])
            self.assertIn("authority_decision_required", errors)
            self.assertIn("sensitive_command", errors)
            self.assertIn("smoke_receipt_forbidden_write_performed", errors)
            self.assertIn("smoke_receipt_forbidden_remote_state_mutated", errors)
            self.assertIn("smoke_receipt_forbidden_browser_launch_performed", errors)
            self.assertIn("smoke_receipt_forbidden_telemetry_enabled", errors)
            self.assertNotIn(str(receipt_dir), output)

    def test_checker_output_redacts_raw_paths_and_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            raw_path = r"C:\Users\lenovo\.codex\skills\gstack\secret.json"
            receipt = self.valid_smoke_receipt()
            receipt["install_receipt"] = raw_path
            receipt["command_transcript"] = "token=super-secret-value"
            (receipt_dir / "smoke-gstack.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

            code, payload, output = self.run_checker("--receipt-dir", str(receipt_dir), check=False)
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertNotIn(raw_path, output)
            self.assertNotIn("super-secret-value", output)
            self.assertIn("raw_private_path", output)
            self.assertIn("raw_secret", output)


if __name__ == "__main__":
    unittest.main()
