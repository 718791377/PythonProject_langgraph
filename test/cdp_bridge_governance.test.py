import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CDP_GOVERNANCE = ROOT / "tools" / "cdp_bridge_governance.py"
BROWSER_OWNER_REGISTRY = ROOT / "tools" / "browser_owner_registry.py"


def run_cdp(args, state_dir, expect=0):
    cmd = [sys.executable, str(CDP_GOVERNANCE), "--state-dir", str(state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


def run_owner_registry(args, owner_state_dir, expect=0):
    cmd = [sys.executable, str(BROWSER_OWNER_REGISTRY), "--state-dir", str(owner_state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


def write_authorization_receipt(path: Path, *, target: str, session: str, action: str = "cookie.read") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "action": "CDP Bridge sensitive browser action authorization",
                "target": target,
                "scope": f"one-task sensitive CDP action {action}",
                "expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(timespec="seconds"),
                "session": session,
                "operator_confirmation": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


class CdpBridgeGovernanceTests(unittest.TestCase):
    def test_read_only_tab_inventory_is_allowed_without_owner_or_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "tab.list",
                    "--target",
                    r"tab:C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--session",
                    "session-a",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dispatch_allowed"])
            self.assertEqual(result["action_kind"], "read-only")
            self.assertFalse(result["authorization_required"])
            self.assertFalse(result["owner_required"])
            self.assertFalse(result["safety"]["connects_to_cdp"])
            self.assertFalse(result["safety"]["reads_cookies"])
            self.assertNotIn(str(state), serialized)
            self.assertIn("[REDACTED_PATH]", serialized)

    def test_cookie_read_fails_closed_without_owner_or_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "cookie.read",
                    "--target",
                    "tab:debug-1",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["dispatch_allowed"])
            self.assertTrue(result["authorization_required"])
            self.assertTrue(result["owner_required"])
            self.assertIn("owner_lease_required", result["blockers"])
            self.assertIn("authorization_receipt_required", result["blockers"])
            self.assertTrue(result["safety"]["requested_action_would_read_cookies"])
            self.assertFalse(result["safety"]["reads_cookies"])

    def test_sensitive_action_passes_with_active_owner_and_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            target = "tab:debug-1"
            session = "session-a"
            reserved = run_owner_registry(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-isolated",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    session,
                    "--target",
                    target,
                    "--profile-path",
                    r"C:\Users\lenovo\.codex\state\browser-automation\isolated\session-a",
                    "--purpose",
                    "cdp governance unit test",
                    "--ttl",
                    "300",
                ],
                owner_state,
            )
            receipt = write_authorization_receipt(state / "auth.json", target=target, session=session, action="js.evaluate")
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "js.evaluate",
                    "--target",
                    target,
                    "--session",
                    session,
                    "--owner-lease-id",
                    reserved["lease"]["lease_id"],
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dispatch_allowed"])
            self.assertEqual(result["owner_lease"]["owner_class"], "codex-managed-isolated")
            self.assertTrue(result["owner_verified"])
            self.assertTrue(result["authorization_verified"])
            self.assertTrue(result["safety"]["requested_action_would_execute_javascript"])
            self.assertFalse(result["safety"]["executes_javascript"])
            self.assertNotIn(str(state), serialized)

    def test_click_type_and_navigate_are_sensitive_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            for action in ["mouse.click", "keyboard.type", "page.navigate"]:
                result = run_cdp(
                    [
                        "check",
                        "--action",
                        action,
                        "--target",
                        "tab:debug-1",
                        "--session",
                        "session-a",
                    ],
                    state,
                    expect=3,
                )
                self.assertFalse(result["dispatch_allowed"], action)
                self.assertEqual(result["action_kind"], "sensitive", action)
                self.assertIn("owner_lease_required", result["blockers"], action)
                self.assertIn("authorization_receipt_required", result["blockers"], action)

    def test_unknown_action_is_blocked_as_sensitive(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "experimental.do-anything",
                    "--target",
                    "tab:debug-1",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["action_kind"], "unknown")
            self.assertIn("unknown_action", result["blockers"])
            self.assertIn("owner_lease_required", result["blockers"])


if __name__ == "__main__":
    unittest.main()
