import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "chrome_devtools_mcp_managed.py"


def run_cmd(args, state_dir, expect=0):
    cmd = [sys.executable, str(SCRIPT), "--state-dir", str(state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


class ChromeDevToolsMcpManagedTests(unittest.TestCase):
    def test_plan_isolated_session_is_dry_run_and_redacts_profile_path(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "plan",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dry_run"])
            self.assertFalse(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            self.assertFalse(result["safety"]["launches_browser"])
            self.assertFalse(result["safety"]["connects_to_cdp"])
            self.assertFalse(result["safety"]["mutates_user_codex_config"])
            self.assertEqual(result["plan"]["owner_class"], "codex-managed-isolated")
            self.assertEqual(result["plan"]["port_policy"]["codex_browser_range"].split()[0], "39500-39699")
            self.assertIn("profile_path_hash", result["plan"])
            self.assertIn("[REDACTED_PATH]", serialized)
            self.assertNotIn(str(state), serialized)
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_reserve_isolated_session_writes_owner_lease_and_wrapper_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test reserve",
                    "--ttl",
                    "120",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            lease = result["owner_lease"]
            self.assertEqual(lease["owner_class"], "codex-managed-isolated")
            self.assertTrue(lease["cleanup_allowed"])
            self.assertEqual(lease["status"], "active")
            self.assertTrue(result["wrapper_receipt"]["receipt_written"])
            self.assertIn("receipt_path_hash", result["wrapper_receipt"])
            self.assertNotIn(str(state), serialized)

            registry = json.loads((state / "owner-registry" / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(len(registry["leases"]), 1)
            self.assertEqual(registry["leases"][0]["owner_class"], "codex-managed-isolated")
            self.assertTrue(list((state / "receipts").glob("*-reserve-isolated-session-*.json")))

    def test_live_start_without_install_receipt_fails_closed_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test start",
                ],
                state,
                expect=3,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "install_receipt_required")
            self.assertFalse(result["start_performed"])
            self.assertFalse(result["safety"]["launches_browser"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())
            self.assertNotIn(str(state), serialized)

    def test_release_delegates_to_owner_registry(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            reserved = run_cmd(
                [
                    "isolated-session",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test release",
                ],
                state,
            )
            lease_id = reserved["owner_lease"]["lease_id"]
            released = run_cmd(["isolated-session", "release", "--lease-id", lease_id, "--session", "session-a"], state)
            self.assertTrue(released["ok"])
            self.assertEqual(released["owner_lease"]["status"], "released")
            self.assertTrue(released["wrapper_receipt"]["receipt_written"])

            status = run_cmd(["isolated-session", "status"], state)
            self.assertEqual(status["leases"][0]["status"], "released")


if __name__ == "__main__":
    unittest.main()
