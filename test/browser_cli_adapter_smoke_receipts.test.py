#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_browser_cli_adapter_smoke.py"
CHECKER = ROOT / "tools" / "check_browser_cli_adapter_smoke_receipts.py"
ADAPTERS = ("chrome-devtools-mcp", "cdp-bridge-mcp", "OpenCLI")


class BrowserCliAdapterSmokeReceiptTests(unittest.TestCase):
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

    def write_install_receipt(self, directory: Path, adapter: str) -> Path:
        receipt = {
            "tool_name": adapter,
            "installed_version": "fixture-pin",
            "source_url": f"https://example.invalid/{adapter}",
            "install_path": "install-ref",
            "wrapper_path": sys.executable,
            "state_path": "state-ref",
            "smoke_test_command": f"{adapter} --help",
            "smoke_test_result": {"status": "pass"},
            "updater_command": f"{adapter} update --pin fixture-pin",
            "rollback_pointer": f"rollback-ref-{adapter}",
            "owner_lane": f"browser-cli-adapter:{adapter.lower()}",
            "redaction_status": "no_secrets",
        }
        path = directory / f"install-{adapter.lower()}.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def valid_smoke_receipt(self, adapter: str) -> dict:
        return {
            "tool_name": adapter,
            "owner_lane": f"browser-cli-adapter:{adapter.lower()}",
            "runtime_stage": "smoke-tested",
            "install_receipt": f"receipt-sha256:{adapter}",
            "smoke_command": f"{adapter} --help",
            "smoke_type": "help",
            "smoke_result": {"status": "pass"},
            "timeout_release": {"status": "pass", "released": True},
            "rollback_pointer": f"rollback-sha256:{adapter}",
            "rollback_ready": True,
            "command_transcript": f"{adapter} help output",
            "transcript_redaction": {"status": "pass", "redacted_transcript_hash": f"hash-{adapter}"},
            "redaction_status": "no_secrets",
            "smoke_tested": True,
            "write_performed": False,
            "live_action_performed": False,
            "sensitive_action_performed": False,
            "user_level_state_mutated": False,
            "reads_browser_data": False,
            "external_message_sent": False,
        }

    def write_smoke_receipts(self, directory: Path, overrides: dict[str, dict] | None = None) -> list[Path]:
        overrides = overrides or {}
        paths: list[Path] = []
        for adapter in ADAPTERS:
            payload = self.valid_smoke_receipt(adapter)
            payload.update(overrides.get(adapter, {}))
            path = directory / f"smoke-{adapter.lower()}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            paths.append(path)
        return paths

    def test_runner_without_install_receipts_writes_blocked_receipts_not_smoke_tested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp) / "receipts"
            code, payload, output = self.run_json(RUNNER, "run", "--receipt-dir", str(receipt_dir))

            self.assertEqual(code, 0)
            self.assertEqual(payload["counts"]["adapters"], 3)
            self.assertEqual(payload["counts"]["smoke_tested"], 0)
            self.assertEqual(payload["counts"]["blocked"], 3)
            self.assertNotIn(str(receipt_dir), output)
            self.assertEqual(len(list(receipt_dir.glob("*.json"))), 3)
            for path in receipt_dir.glob("*.json"):
                receipt = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(receipt["smoke_tested"])
                self.assertNotEqual(receipt["r4_status"], "smoke-tested")

            check_code, check_payload, _ = self.run_json(CHECKER, "--root", str(ROOT), "--receipt-dir", str(receipt_dir))
            self.assertEqual(check_code, 0)
            self.assertTrue(check_payload["ok"])
            self.assertEqual(check_payload["counts"]["blocked_or_not_installed"], 3)
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 0)

    def test_valid_simulated_r4_help_receipts_for_all_adapters_pass_checker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            receipt_dir = base / "smoke"
            install_receipts = [self.write_install_receipt(base, adapter) for adapter in ADAPTERS]
            args = ["run", "--receipt-dir", str(receipt_dir)]
            for adapter, install_receipt in zip(ADAPTERS, install_receipts):
                args.extend(["--install-receipt", f"{adapter}={install_receipt}"])

            code, payload, output = self.run_json(RUNNER, *args)
            self.assertEqual(code, 0)
            self.assertEqual(payload["counts"]["smoke_tested"], 3)
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
            self.assertEqual(check_payload["counts"]["positive_smoke_tested"], 3)
            self.assertNotIn(str(base), check_output)
            self.assertNotIn(sys.executable, check_output)

    def test_checker_blocks_sensitive_or_write_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            self.write_smoke_receipts(
                receipt_dir,
                {
                    "chrome-devtools-mcp": {
                        "smoke_command": "chrome-devtools-mcp cookie.read",
                        "write_performed": True,
                        "reads_browser_data": True,
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
            self.assertIn("smoke_receipt_forbidden_reads_browser_data", errors)

    def test_checker_rejects_forbidden_sibling_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            self.write_smoke_receipts(receipt_dir, {"OpenCLI": {"tool_name": "WXWork_CLI"}})

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
            self.assertIn("forbidden_adapter_term:WXWork_CLI", errors)
            self.assertIn("missing_receipt:OpenCLI", errors)

    def test_checker_output_does_not_echo_raw_paths_or_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            raw_path = r"C:\Users\lenovo\.codex\state\browser\secret.json"
            self.write_smoke_receipts(
                receipt_dir,
                {
                    "cdp-bridge-mcp": {
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
