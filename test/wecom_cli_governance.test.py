from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "wecom_cli_governance.py"


def run_wecom(args: list[str], *, expect: int = 0) -> tuple[dict, str]:
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


class WeComCliGovernanceTests(unittest.TestCase):
    def test_api_status_is_safe_and_does_not_probe_wxwork(self):
        payload, stdout = run_wecom(["api-status"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["default_channel"], "api_or_webhook_first")
        self.assertFalse(payload["gui_automation_enabled"])
        self.assertFalse(payload["process_probe_performed"])
        self.assertFalse(payload["safety"]["attaches_to_wxwork"])
        self.assertFalse(payload["safety"]["reads_message_content"])
        self.assertNotIn("message text", stdout.lower())

    def test_webhook_plan_rejects_inline_secret_values(self):
        allowed, _ = run_wecom(["webhook-plan", "--name", "ops-alerts", "--secret-ref", "env:WECOM_WEBHOOK_KEY"])
        self.assertTrue(allowed["ok"])
        self.assertTrue(allowed["plan_allowed"])
        self.assertFalse(allowed["calls_webhook"])
        self.assertNotIn("WECOM_WEBHOOK_KEY", json.dumps(allowed))

        blocked, _ = run_wecom(
            ["webhook-plan", "--name", "ops-alerts", "--secret-ref", "secret=raw-value"],
            expect=3,
        )
        self.assertFalse(blocked["ok"])
        self.assertIn("secret_ref_must_be_reference_not_value", blocked["blockers"])

    def test_gui_plan_is_dry_run_and_requires_operator_gates(self):
        payload, _ = run_wecom(["gui-plan", "--target-process", "WXWork.exe"])
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["live_gui_control_allowed"])
        self.assertTrue(payload["global_lease_required"])
        self.assertTrue(payload["operator_confirmation_required"])
        self.assertTrue(payload["timeout_release_required"])
        self.assertTrue(payload["api_or_webhook_preferred"])
        self.assertFalse(payload["safety"]["controls_gui"])

    def test_gui_check_without_receipts_fails_closed(self):
        payload, _ = run_wecom(["gui-check", "--action", "gui.attach", "--session", "session-a"], expect=3)
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
                        "owner_lane": "wecom-cli",
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
                        "owner_lane": "wecom-cli",
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
            payload, stdout = run_wecom(
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
                        "owner_lane": "wecom-cli",
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
                        "owner_lane": "wecom-cli",
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
            payload, _ = run_wecom(
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


if __name__ == "__main__":
    unittest.main()
