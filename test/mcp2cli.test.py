import json
import shutil
import subprocess
import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "mcp2cli.py"
REGISTRY = REPO_ROOT / "tools" / "mcp2cli_allowed_profiles.json"


class Mcp2CliTest(unittest.TestCase):
    maxDiff = None

    def make_tmp(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def run_cli(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        )
        if check and completed.returncode != 0:
            self.fail(completed.stdout.decode("utf-8", "replace") + "\n" + completed.stderr.decode("utf-8", "replace"))
        return completed

    def parse(self, completed: subprocess.CompletedProcess[bytes]) -> dict:
        return json.loads(completed.stdout.decode("utf-8"))

    def test_registry_declares_allowed_profiles_and_risk_metadata(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        profiles = {profile["profile_id"]: profile for profile in registry["profiles"]}

        self.assertEqual(registry["schema_version"], 1)
        self.assertIn("core-readonly", profiles)
        self.assertIn("browser-readonly", profiles)
        self.assertIn("remote-infra-readonly", profiles)
        for profile in profiles.values():
            self.assertIsInstance(profile.get("tools"), list)
            for tool in profile["tools"]:
                self.assertIn("tool_id", tool)
                self.assertIn("risk_level", tool)
                self.assertIn("sensitive_categories", tool)
                self.assertIn("call", tool)

    def test_list_search_and_show_are_compact_by_default(self) -> None:
        listed = self.parse(self.run_cli("list", "--profile", "browser-readonly", "--json"))
        serialized = json.dumps(listed, ensure_ascii=False)

        self.assertEqual(listed["command"], "list")
        self.assertTrue(listed["ok"])
        self.assertTrue(listed["safety"]["compact_output"])
        self.assertFalse(listed["safety"]["full_schema_included_by_default"])
        self.assertNotIn("schema_summary", serialized)
        self.assertIn("browser.tabs.list", serialized)

        search = self.parse(self.run_cli("search", "browser", "--profile", "browser-readonly", "--json"))
        self.assertEqual(search["command"], "search")
        self.assertGreaterEqual(search["total_matches"], 1)
        self.assertNotIn("schema_summary", json.dumps(search, ensure_ascii=False))

        show = self.parse(self.run_cli("show", "browser.tabs.list", "--profile", "browser-readonly", "--json"))
        self.assertEqual(show["command"], "show")
        self.assertFalse(show["tool"]["full_metadata_included"])
        self.assertNotIn("schema_summary", json.dumps(show, ensure_ascii=False))

    def test_sensitive_call_without_receipt_fails_closed(self) -> None:
        completed = self.run_cli(
            "call",
            "browser.tabs.list",
            "--profile",
            "browser-readonly",
            "--json",
            "--args",
            "{}",
            check=False,
        )
        payload = self.parse(completed)

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["blocked"])
        self.assertTrue(payload["receipt_required"])
        self.assertFalse(payload["call_performed"])
        self.assertFalse(payload["external_mcp_invoked"])
        self.assertIn("authorization_receipt_missing", payload["receipt_blockers"])

    def test_incomplete_receipt_fails_closed_and_redacts_private_values(self) -> None:
        tmp = self.make_tmp("receipt")
        receipt = tmp / "bad-receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "action": "call",
                    "target": "browser.tabs.list",
                    "scope": r"C:\Users\lenovo\.codex\secret?api_key=sk-test-secret-value",
                    "session": "test-session",
                    "operator_confirmation": False,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        completed = self.run_cli(
            "call",
            "browser.tabs.list",
            "--profile",
            "browser-readonly",
            "--json",
            "--args",
            "{}",
            "--authorization-receipt",
            str(receipt),
            check=False,
        )
        payload = self.parse(completed)
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["blocked"])
        self.assertIn("authorization_receipt_missing_expiry", payload["receipt_blockers"])
        self.assertIn("authorization_receipt_operator_confirmation_not_true", payload["receipt_blockers"])
        self.assertNotIn(r"C:\Users\lenovo", serialized)
        self.assertNotIn("sk-test-secret-value", serialized)
        self.assertIn("[REDACTED_PATH]", serialized)
        self.assertIn("[REDACTED_SECRET]", serialized)

    def test_low_risk_call_returns_local_deterministic_facade_result(self) -> None:
        payload = self.parse(
            self.run_cli(
                "call",
                "repo.openspec.list",
                "--profile",
                "core-readonly",
                "--json",
                "--args",
                '{"note":"safe"}',
            )
        )

        self.assertTrue(payload["ok"])
        self.assertFalse(payload["blocked"])
        self.assertFalse(payload["receipt_required"])
        self.assertTrue(payload["call_performed"])
        self.assertFalse(payload["external_mcp_invoked"])
        self.assertEqual(payload["args_summary"], {"note": "safe"})
        self.assertIn("deterministic guarded facade", payload["result"]["message"])

    def test_valid_receipt_reaches_guarded_sensitive_block_without_live_mcp(self) -> None:
        tmp = self.make_tmp("valid-receipt")
        receipt = tmp / "receipt.json"
        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        receipt.write_text(
            json.dumps(
                {
                    "action": "call",
                    "target": "browser.tabs.list",
                    "scope": "one-task browser inventory smoke",
                    "expiry": expiry,
                    "session": "test-session",
                    "operator_confirmation": True,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        completed = self.run_cli(
            "call",
            "browser.tabs.list",
            "--profile",
            "browser-readonly",
            "--json",
            "--args",
            "{}",
            "--authorization-receipt",
            str(receipt),
            check=False,
        )
        payload = self.parse(completed)

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(payload["blocked"])
        self.assertEqual(payload["reason"], "blocked_until_browser_owner_registry")
        self.assertTrue(payload["receipt_required"])
        self.assertTrue(payload["receipt_valid"])
        self.assertFalse(payload["call_performed"])
        self.assertFalse(payload["external_mcp_invoked"])


if __name__ == "__main__":
    unittest.main()
