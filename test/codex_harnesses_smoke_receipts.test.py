#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_codex_harnesses_smoke.py"
CHECKER = ROOT / "tools" / "check_codex_harnesses_smoke_receipts.py"
HARNESSES = ("Pi", "oh-my-pi")


class CodexHarnessesSmokeReceiptTests(unittest.TestCase):
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

    def write_install_receipt(self, directory: Path, harness: str) -> Path:
        receipt = {
            "tool_name": harness,
            "installed_version": "fixture-pin",
            "source_pin": f"fixture-source-pin-{harness}",
            "source_url": "https://pi.dev/" if harness == "Pi" else "https://github.com/can1357/oh-my-pi",
            "install_path": "install-ref",
            "wrapper_path": sys.executable,
            "state_path": "state-ref",
            "smoke_test_command": f"{harness} --help",
            "smoke_test_result": {"status": "pass"},
            "updater_command": f"{harness} update --pin fixture-pin",
            "rollback_pointer": f"rollback-ref-{harness}",
            "owner_lane": f"codex-harnesses:{harness.lower()}",
            "redaction_status": "no_secrets",
        }
        path = directory / f"install-{harness.lower().replace(' ', '-')}.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def valid_smoke_receipt(self, harness: str) -> dict:
        return {
            "tool_name": harness,
            "owner_lane": f"codex-harnesses:{harness.lower()}",
            "runtime_stage": "smoke-tested",
            "install_receipt": f"receipt-sha256:{harness}",
            "smoke_command": f"{harness} --help",
            "smoke_type": "help",
            "smoke_result": {"status": "pass"},
            "timeout_release": {"status": "pass", "released": True},
            "rollback_pointer": f"rollback-sha256:{harness}",
            "rollback_ready": True,
            "command_transcript": f"{harness} help output",
            "transcript_redaction": {"status": "pass", "redacted_transcript_hash": f"hash-{harness}"},
            "redaction_status": "no_secrets",
            "smoke_tested": True,
            "read_guard": {
                "status": "pass",
                "scope": "help/version/status/read-only",
                "read_only": True,
                "sidecar_state_read": False,
            },
            "write_guard": {
                "status": "pass",
                "write_allowed": False,
                "write_performed": False,
                "write_capable_harness_job": False,
            },
            "job_state": {
                "status": "smoke-tested",
                "job_kind": "r4-read-only-smoke",
                "write_capable": False,
                "sidecar_started": False,
                "isolated_worktree_required_for_write": True,
            },
            "no_codex_takeover": True,
            "write_performed": False,
            "live_action_performed": False,
            "sensitive_action_performed": False,
            "user_level_state_mutated": False,
            "reads_browser_data": False,
            "external_message_sent": False,
            "write_capable_harness_job": False,
            "codex_launcher_mutated": False,
            "native_codex_replaced": False,
            "native_subagents_replaced": False,
            "native_omx_replaced": False,
            "langgraph_replaced": False,
            "apply_patch_replaced": False,
            "local_main_gate_bypassed": False,
            "active_candidate": False,
            "sidecar_takeover": False,
        }

    def write_smoke_receipts(self, directory: Path, overrides: dict[str, dict] | None = None) -> list[Path]:
        overrides = overrides or {}
        paths: list[Path] = []
        for harness in HARNESSES:
            payload = self.valid_smoke_receipt(harness)
            payload.update(overrides.get(harness, {}))
            path = directory / f"smoke-{harness.lower().replace(' ', '-')}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            paths.append(path)
        return paths

    def test_runner_without_install_receipts_writes_blocked_receipts_not_smoke_tested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp) / "receipts"
            code, payload, output = self.run_json(RUNNER, "run", "--receipt-dir", str(receipt_dir))

            self.assertEqual(code, 0)
            self.assertEqual(payload["counts"]["harnesses"], 2)
            self.assertEqual(payload["counts"]["smoke_tested"], 0)
            self.assertEqual(payload["counts"]["blocked"], 2)
            self.assertNotIn(str(receipt_dir), output)
            self.assertEqual(len(list(receipt_dir.glob("*.json"))), 2)
            for path in receipt_dir.glob("*.json"):
                receipt = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(receipt["smoke_tested"])
                self.assertNotEqual(receipt["r4_status"], "smoke-tested")
                self.assertTrue(receipt["no_codex_takeover"])
                self.assertFalse(receipt["write_capable_harness_job"])

            check_code, check_payload, _ = self.run_json(CHECKER, "--root", str(ROOT), "--receipt-dir", str(receipt_dir))
            self.assertEqual(check_code, 0)
            self.assertTrue(check_payload["ok"])
            self.assertEqual(check_payload["counts"]["blocked_or_not_installed"], 2)
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 0)

    def test_valid_simulated_r4_help_receipts_for_all_harnesses_pass_checker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            receipt_dir = base / "smoke"
            install_receipts = [self.write_install_receipt(base, harness) for harness in HARNESSES]
            args = ["run", "--receipt-dir", str(receipt_dir)]
            for harness, install_receipt in zip(HARNESSES, install_receipts):
                args.extend(["--install-receipt", f"{harness}={install_receipt}"])

            code, payload, output = self.run_json(RUNNER, *args)
            self.assertEqual(code, 0)
            self.assertEqual(payload["counts"]["smoke_tested"], 2)
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
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 2)
            self.assertNotIn(str(base), check_output)
            self.assertNotIn(sys.executable, check_output)

    def test_checker_blocks_write_or_takeover_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            self.write_smoke_receipts(
                receipt_dir,
                {
                    "Pi": {
                        "smoke_command": "Pi run-job --write",
                        "write_performed": True,
                        "write_capable_harness_job": True,
                        "native_codex_replaced": True,
                    }
                },
            )

            code, payload, _ = self.run_json(
                CHECKER,
                "--root",
                str(ROOT),
                "--receipt-dir",
                str(receipt_dir),
                "--require-smoke-tested",
                check=False,
            )
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            errors = "\n".join(payload["errors"])
            self.assertIn("sensitive_command", errors)
            self.assertIn("smoke_receipt_forbidden_write_performed", errors)
            self.assertIn("smoke_receipt_forbidden_write_capable_harness_job", errors)
            self.assertIn("smoke_receipt_forbidden_native_codex_replaced", errors)

    def test_checker_rejects_forbidden_sibling_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            self.write_smoke_receipts(receipt_dir, {"oh-my-pi": {"tool_name": "OpenCLI"}})

            code, payload, _ = self.run_json(
                CHECKER,
                "--root",
                str(ROOT),
                "--receipt-dir",
                str(receipt_dir),
                check=False,
            )
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            errors = "\n".join(payload["errors"])
            self.assertIn("forbidden_sibling_lane_term:OpenCLI", errors)
            self.assertIn("missing_receipt:oh-my-pi", errors)

    def test_checker_output_does_not_echo_raw_paths_or_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            raw_path = r"C:\Users\lenovo\.codex\state\harnesses\secret.json"
            self.write_smoke_receipts(
                receipt_dir,
                {
                    "Pi": {
                        "install_receipt": raw_path,
                        "command_transcript": "token=super-secret-value",
                    }
                },
            )

            code, payload, output = self.run_json(
                CHECKER,
                "--root",
                str(ROOT),
                "--receipt-dir",
                str(receipt_dir),
                check=False,
            )
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertNotIn(raw_path, output)
            self.assertNotIn("super-secret-value", output)
            self.assertIn("raw_private_path", output)
            self.assertIn("raw_secret", output)


if __name__ == "__main__":
    unittest.main()
