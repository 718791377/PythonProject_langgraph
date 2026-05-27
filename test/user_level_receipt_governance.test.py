#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "user_level_receipt_governance.py"


def run_cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic path
        raise AssertionError(f"invalid JSON stdout={proc.stdout!r} stderr={proc.stderr!r}") from exc
    return proc.returncode, payload


class UserLevelReceiptGovernanceTests(unittest.TestCase):
    def write_json(self, directory: Path, name: str, payload: dict) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_authorization_receipt_requires_all_fields_and_future_expiry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "auth.json", {"action": "mcp.call"})
            code, payload = run_cli(
                "auth-check",
                "--receipt",
                str(receipt),
                "--action",
                "mcp.call",
                "--target",
                "mcp:cloudflare",
                "--session",
                "session-a",
            )

        self.assertEqual(code, 3)
        self.assertFalse(payload["ok"])
        self.assertIn("authorization_receipt_missing_target", payload["blockers"])
        self.assertIn("authorization_receipt_operator_confirmation_not_true", payload["blockers"])
        self.assertFalse(payload["mutates_user_level_state"])

    def test_valid_authorization_receipt_is_summarized_without_raw_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = str(Path(tmp) / "auth.json")
            receipt = self.write_json(
                Path(tmp),
                "auth.json",
                {
                    "action": "browser.click",
                    "target": "tab:123",
                    "scope": ["browser.click"],
                    "expiry": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                    "session": "session-a",
                    "operator_confirmation": True,
                },
            )
            code, payload = run_cli(
                "auth-check",
                "--receipt",
                str(receipt),
                "--action",
                "browser.click",
                "--target",
                "tab:123",
                "--session",
                "session-a",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["authorization_valid"])
        self.assertIn("receipt_path_hash", payload["authorization_summary"])
        self.assertNotIn(raw_path, output)
        self.assertFalse(payload["contains_raw_private_paths_in_output"])

    def test_update_receipt_requires_rollback_and_smoke_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "skills2cli",
                    "installed_version": "abc123",
                    "source_url": "https://example.invalid/repo.git",
                    "install_path": r"C:\Users\lenovo\.codex\tools\skills2cli",
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\skills2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\skills2cli",
                    "smoke_test_command": "skills2cli index --json",
                    "smoke_test_result": {"status": "fail"},
                    "updater_command": "skills2cli-update --pin abc123",
                    "owner_lane": "skills2cli",
                    "redaction_status": "pass",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "skills2cli",
                "--owner-lane",
                "skills2cli",
            )

        self.assertEqual(code, 3)
        self.assertFalse(payload["update_receipt_valid"])
        self.assertIn("update_receipt_missing_rollback_pointer", payload["blockers"])
        self.assertIn("update_receipt_smoke_test_result_must_pass", payload["blockers"])

    def test_valid_update_receipt_hashes_private_paths_and_rollback_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "mcp2cli",
                    "installed_version": "v1.0.0",
                    "source_url": "https://example.invalid/mcp2cli.git",
                    "install_path": r"C:\Users\lenovo\.codex\tools\mcp2cli",
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\mcp2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\mcp2cli",
                    "smoke_test_command": "mcp2cli list --json",
                    "smoke_test_result": {"status": "pass"},
                    "updater_command": "mcp2cli-update --pin v1.0.0",
                    "rollback_pointer": r"C:\Users\lenovo\.codex\backup\mcp2cli-prev",
                    "owner_lane": "mcp2cli",
                    "redaction_status": "no_secrets",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "mcp2cli",
                "--owner-lane",
                "mcp2cli",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["rollback_ready"])
        self.assertIn("install_path_hash", payload["update_summary"])
        self.assertIn("rollback_pointer_hash", payload["update_summary"])
        self.assertNotIn(r"C:\Users\lenovo\.codex\tools\mcp2cli", output)
        self.assertNotIn(r"C:\Users\lenovo\.codex\backup\mcp2cli-prev", output)

    def test_redaction_check_blocks_raw_sensitive_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "bad.json",
                {
                    "tool_name": "browser",
                    "cookies": "sessionid=abc",
                    "plugin_description_dump": "large raw plugin description",
                    "note": "token=raw-value",
                },
            )
            code, payload = run_cli("redact-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        self.assertFalse(payload["redaction_valid"])
        self.assertGreaterEqual(payload["finding_count"], 3)
        self.assertIn("cookies", json.dumps(payload["blockers"]))
        self.assertFalse(payload["reads_browser_data"])

    def test_templates_expose_required_fields(self) -> None:
        code, payload = run_cli("template", "--kind", "update")
        self.assertEqual(code, 0)
        self.assertIn("rollback_pointer", payload["required_fields"])
        self.assertIn("redaction_status", payload["required_fields"])


if __name__ == "__main__":
    unittest.main()
