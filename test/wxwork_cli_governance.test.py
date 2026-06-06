from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "wxwork_cli_governance.py"


def run_wxwork(args: list[str], *, expect: int = 0) -> tuple[dict, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"Expected exit {expect}, got {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout), result.stdout


def future_iso(minutes: int = 30) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


class WXWorkCliGovernanceTests(unittest.TestCase):
    def write_install_receipt(self, directory: Path) -> Path:
        receipt = {
            "schema_version": 1,
            "tool_name": "WXWork_CLI",
            "owner_lane": "wxwork_cli",
            "status": "installed-user-level",
            "source_url": "https://github.com/HKUDS/CLI-Anything",
            "installed_version": "fixture-pin",
            "wrapper_path": sys.executable,
            "install_path": str(directory / "wxwork-cli"),
            "state_path": str(directory / "state"),
            "smoke_test_command": "WXWork_CLI --help",
            "smoke_test_result": {"status": "pass"},
            "updater_command": "wxwork-cli update --pin fixture-pin",
            "rollback_pointer": str(directory / "rollback"),
            "redaction_status": "no_secrets",
        }
        path = directory / "wxwork-cli-install.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_api_status_is_safe_and_does_not_probe_wxwork(self):
        payload, stdout = run_wxwork(["api-status"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "WXWork_CLI")
        self.assertEqual(payload["control_surface"], "WXWork_CLI")
        self.assertEqual(payload["default_channel"], "api_or_webhook_first")
        self.assertFalse(payload["gui_automation_enabled"])
        self.assertFalse(payload["process_probe_performed"])
        self.assertFalse(payload["safety"]["attaches_to_wxwork"])
        self.assertFalse(payload["safety"]["reads_message_content"])
        self.assertNotIn("message text", stdout.lower())
        self.assertNotIn("wecom-cli", stdout.lower())

    def test_webhook_plan_rejects_inline_secret_values(self):
        allowed, _ = run_wxwork(["webhook-plan", "--name", "ops-alerts", "--secret-ref", "env:WXWORK_WEBHOOK_KEY"])
        self.assertTrue(allowed["ok"])
        self.assertTrue(allowed["plan_allowed"])
        self.assertFalse(allowed["calls_webhook"])
        self.assertNotIn("WXWORK_WEBHOOK_KEY", json.dumps(allowed))

        blocked, _ = run_wxwork(
            ["webhook-plan", "--name", "ops-alerts", "--secret-ref", "secret=raw-value"],
            expect=3,
        )
        self.assertFalse(blocked["ok"])
        self.assertIn("secret_ref_must_be_reference_not_value", blocked["blockers"])

    def test_gui_plan_is_dry_run_and_requires_operator_gates(self):
        payload, _ = run_wxwork(["gui-plan", "--target-process", "WXWork.exe"])
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["live_gui_control_allowed"])
        self.assertTrue(payload["global_lease_required"])
        self.assertTrue(payload["operator_confirmation_required"])
        self.assertTrue(payload["timeout_release_required"])
        self.assertTrue(payload["api_or_webhook_preferred"])
        self.assertFalse(payload["safety"]["controls_gui"])

    def test_gui_check_without_receipts_fails_closed(self):
        payload, _ = run_wxwork(["gui-check", "--action", "gui.attach", "--session", "session-a"], expect=3)
        self.assertFalse(payload["dispatch_allowed"])
        self.assertIn("operator_authorization_receipt_required", payload["blockers"])
        self.assertIn("global_wxwork_lease_required", payload["blockers"])
        self.assertFalse(payload["gui_control_performed"])
        self.assertFalse(payload["message_content_included"])

    def test_gui_check_with_valid_receipts_allows_only_dry_run_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            auth = root / "auth.json"
            lease = root / "lease.json"
            auth.write_text(
                json.dumps(
                    {
                        "action": "gui.attach",
                        "target": "WXWork.exe",
                        "scope": "attach-window-only-no-message-content",
                        "expiry": future_iso(),
                        "session": "session-a",
                        "operator_confirmation": True,
                        "owner_lane": "wxwork_cli",
                        "redaction_policy": "no message contents, tokens, cookies, or private paths",
                        "rollback_pointer": "release-global-wxwork-lease",
                    }
                ),
                encoding="utf-8",
            )
            lease.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "owner_lane": "wxwork_cli",
                        "lease_scope": "global-wxwork-gui",
                        "target_process": "WXWork.exe",
                        "session": "session-a",
                        "status": "active",
                        "expires_at": future_iso(),
                        "timeout_release_seconds": 300,
                        "rollback_pointer": "release-global-wxwork-lease",
                    }
                ),
                encoding="utf-8",
            )
            payload, stdout = run_wxwork(
                [
                    "gui-check",
                    "--action",
                    "gui.attach",
                    "--session",
                    "session-a",
                    "--authorization-receipt",
                    str(auth),
                    "--lease-receipt",
                    str(lease),
                ]
            )
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dispatch_allowed"])
            self.assertTrue(payload["dry_run_only"])
            self.assertFalse(payload["gui_control_performed"])
            self.assertFalse(payload["safety"]["controls_gui"])
            self.assertNotIn(str(root), stdout)

    def test_expired_or_mismatched_receipts_are_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            auth = root / "auth.json"
            lease = root / "lease.json"
            auth.write_text(
                json.dumps(
                    {
                        "action": "gui.attach",
                        "target": "WXWork.exe",
                        "scope": "attach-window-only-no-message-content",
                        "expiry": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                        "session": "session-a",
                        "operator_confirmation": True,
                        "owner_lane": "wxwork_cli",
                        "redaction_policy": "no message contents",
                        "rollback_pointer": "release",
                    }
                ),
                encoding="utf-8",
            )
            lease.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "owner_lane": "wxwork_cli",
                        "lease_scope": "global-wxwork-gui",
                        "target_process": "WXWork.exe",
                        "session": "session-b",
                        "status": "active",
                        "expires_at": future_iso(),
                        "timeout_release_seconds": 300,
                        "rollback_pointer": "release",
                    }
                ),
                encoding="utf-8",
            )
            payload, _ = run_wxwork(
                [
                    "gui-check",
                    "--action",
                    "gui.attach",
                    "--session",
                    "session-a",
                    "--authorization-receipt",
                    str(auth),
                    "--lease-receipt",
                    str(lease),
                ],
                expect=3,
            )
            self.assertIn("authorization_expired_or_invalid", payload["blockers"])
            self.assertIn("lease_session_mismatch", payload["blockers"])

    def test_r4_help_smoke_record_writes_sanitized_smoke_tested_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            install = self.write_install_receipt(root)
            receipt_dir = root / "smoke"
            payload, stdout = run_wxwork(
                [
                    "smoke-record",
                    "--install-receipt",
                    str(install),
                    "--receipt-dir",
                    str(receipt_dir),
                    "--smoke-type",
                    "help",
                    "--session",
                    "session-a",
                ]
            )

            self.assertTrue(payload["ok"])
            self.assertTrue(payload["receipt_written"])
            self.assertTrue(payload["smoke_tested"])
            self.assertEqual(payload["r4_status"], "smoke-tested")
            self.assertNotIn(str(root), stdout)
            self.assertNotIn(sys.executable, stdout)

            receipt_paths = list(receipt_dir.glob("*.json"))
            self.assertEqual(len(receipt_paths), 1)
            receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
            self.assertEqual(receipt["tool_name"], "WXWork_CLI")
            self.assertEqual(receipt["owner_lane"], "wxwork_cli")
            self.assertEqual(receipt["runtime_stage"], "smoke-tested")
            self.assertEqual(receipt["smoke_type"], "help")
            self.assertEqual(receipt["smoke_result"]["status"], "pass")
            self.assertTrue(receipt["timeout_release"]["released"])
            self.assertTrue(receipt["rollback_ready"])
            self.assertFalse(receipt["process_probe_performed"])
            self.assertFalse(receipt["gui_control_performed"])
            self.assertFalse(receipt["sends_messages"])
            self.assertFalse(receipt["message_body_included"])
            self.assertFalse(receipt["external_message_sent"])

            checked, check_stdout = run_wxwork(["smoke-check", "--receipt", str(receipt_paths[0])])
            self.assertTrue(checked["ok"])
            self.assertTrue(checked["smoke_receipt_valid"])
            self.assertNotIn(str(root), check_stdout)
            self.assertNotIn(sys.executable, check_stdout)

            generic = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "user_level_receipt_governance.py"),
                    "smoke-check",
                    "--receipt",
                    str(receipt_paths[0]),
                    "--tool-name",
                    "WXWork_CLI",
                    "--owner-lane",
                    "wxwork_cli",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(generic.returncode, 0, generic.stdout + "\n" + generic.stderr)
            generic_payload = json.loads(generic.stdout)
            self.assertTrue(generic_payload["smoke_receipt_valid"])
            self.assertNotIn(str(root), generic.stdout)
            self.assertNotIn(sys.executable, generic.stdout)

    def test_r4_smoke_with_named_gui_target_requires_global_lease(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            install = self.write_install_receipt(root)
            payload, _ = run_wxwork(
                [
                    "smoke-record",
                    "--install-receipt",
                    str(install),
                    "--receipt-dir",
                    str(root / "smoke"),
                    "--smoke-type",
                    "help",
                    "--session",
                    "session-a",
                    "--target-process",
                    "WXWork.exe",
                ],
                expect=3,
            )

            self.assertFalse(payload["smoke_tested"])
            self.assertIn("global_wxwork_lease_required", payload["blockers"])
            self.assertFalse(payload["gui_control_performed"])
            self.assertFalse(payload["message_body_included"])


if __name__ == "__main__":
    unittest.main()
