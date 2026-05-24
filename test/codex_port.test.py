import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "codex_port.py"


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


class CodexPortTests(unittest.TestCase):
    def test_reserve_list_release_round_trip_with_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            reserved = run_cmd([
                "lease", "reserve",
                "--owner", "codex",
                "--project", "pythonproject-langgraph",
                "--tool", "mcp2cli",
                "--range", "codex-helper",
                "--purpose", "unit test",
                "--ttl", "300",
                "--owner-session", "session-a",
            ], state)
            self.assertTrue(reserved["ok"])
            self.assertEqual(reserved["port"], 39000)
            self.assertEqual(reserved["status"], "pending_bind")
            self.assertFalse(reserved["process_kill_performed"])
            self.assertTrue(Path(reserved["receipt"]).exists())

            renewed = run_cmd([
                "lease", "renew",
                "--lease-id", reserved["lease_id"],
                "--owner-session", "session-a",
                "--ttl", "600",
                "--activate",
            ], state)
            self.assertEqual(renewed["status"], "active")

            listed = run_cmd(["lease", "list", "--owner", "codex"], state)
            self.assertEqual(len(listed["leases"]), 1)
            self.assertEqual(listed["leases"][0]["status"], "active")

            released = run_cmd([
                "lease", "release",
                "--owner-session", "session-a",
                "--port", str(reserved["port"]),
            ], state)
            self.assertEqual(released["status"], "released")

    def test_owner_range_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd([
                "lease", "reserve",
                "--owner", "codex",
                "--project", "bad",
                "--tool", "openclaw-service",
                "--range", "openclaw",
                "--purpose", "bad range",
                "--ttl", "60",
                "--owner-session", "session-a",
            ], state, expect=2)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "owner_range_mismatch")
            self.assertFalse(result["process_kill_performed"])

    def test_live_socket_collision_is_skipped_without_kill(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", 39000))
                sock.listen(1)
                reserved = run_cmd([
                    "lease", "reserve",
                    "--owner", "codex",
                    "--project", "browser",
                    "--tool", "opencli",
                    "--range", "codex-helper",
                    "--purpose", "collision test",
                    "--ttl", "120",
                    "--owner-session", "session-a",
                ], state)
                self.assertEqual(reserved["port"], 39001)
                self.assertEqual(reserved["collision_warnings"][0]["port"], 39000)
                self.assertFalse(reserved["process_kill_performed"])
            finally:
                sock.close()

    def test_release_requires_matching_owner_session(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            reserved = run_cmd([
                "lease", "reserve",
                "--owner", "codex",
                "--project", "pythonproject-langgraph",
                "--tool", "skills2cli",
                "--range", "codex-helper",
                "--purpose", "owner session test",
                "--ttl", "300",
                "--owner-session", "session-a",
            ], state)
            result = run_cmd([
                "lease", "release",
                "--owner-session", "session-b",
                "--port", str(reserved["port"]),
            ], state, expect=2)
            self.assertEqual(result["error"], "owner_session_mismatch")

    def test_import_legacy_reserves_openclaw_port(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            imported = run_cmd([
                "lease", "import-legacy",
                "--owner", "openclaw",
                "--port", "40000",
                "--purpose", "existing OpenClaw service",
                "--project", "openclaw",
                "--tool", "local-control",
                "--owner-session", "session-a",
            ], state)
            self.assertEqual(imported["status"], "legacy_reserved")
            listed = run_cmd(["lease", "list", "--owner", "openclaw"], state)
            self.assertEqual(listed["leases"][0]["status"], "legacy_reserved")

    def test_gc_dry_run_reports_expired_pending_bind_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            reserved = run_cmd([
                "lease", "reserve",
                "--owner", "codex",
                "--project", "pythonproject-langgraph",
                "--tool", "short-lived",
                "--range", "codex-helper",
                "--purpose", "gc test",
                "--ttl", "-1",
                "--owner-session", "session-a",
            ], state)
            gc = run_cmd(["lease", "gc", "--dry-run"], state)
            self.assertTrue(gc["dry_run"])
            self.assertEqual(gc["stale_candidates"][0]["lease_id"], reserved["lease_id"])
            listed = run_cmd(["lease", "list", "--owner", "codex"], state)
            self.assertEqual(listed["leases"][0]["status"], "pending_bind")


if __name__ == "__main__":
    unittest.main()
