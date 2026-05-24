import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "browser_owner_registry.py"


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


def write_receipt(path: Path, *, target: str, session: str) -> Path:
    receipt = path / "authorization.json"
    expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    receipt.write_text(
        json.dumps(
            {
                "action": "browser profile delegation",
                "target": target,
                "scope": "one-task browser owner registry unit test",
                "expiry": expiry,
                "session": session,
                "operator_confirmation": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return receipt


class BrowserOwnerRegistryTests(unittest.TestCase):
    def test_isolated_lease_round_trip_writes_receipts_and_sanitizes_path(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            raw_profile = r"C:\Users\lenovo\.codex\state\browser-automation\isolated\session-a"
            reserved = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-isolated",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--target",
                    "tab:debug-1",
                    "--profile-path",
                    raw_profile,
                    "--purpose",
                    "unit test",
                    "--ttl",
                    "300",
                ],
                state,
            )
            serialized = json.dumps(reserved, ensure_ascii=False)
            self.assertTrue(reserved["ok"])
            self.assertEqual(reserved["lease"]["owner_class"], "codex-managed-isolated")
            self.assertTrue(reserved["cleanup_allowed"])
            self.assertTrue(Path(reserved["receipt"]).exists())
            self.assertNotIn(raw_profile, serialized)
            self.assertIn("[REDACTED_PATH]", serialized)
            self.assertIn("profile_path_hash", serialized)

            listed = run_cmd(["lease", "list", "--project", "pythonproject-langgraph"], state)
            self.assertEqual(len(listed["leases"]), 1)

            released = run_cmd(["lease", "release", "--lease-id", reserved["lease"]["lease_id"], "--session", "session-a"], state)
            self.assertEqual(released["lease"]["status"], "released")
            self.assertTrue(Path(released["receipt"]).exists())

    def test_project_profile_requires_authorization_and_is_exclusive(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            profile = r"C:\Users\lenovo\.codex\state\browser-automation\projects\langgraph"
            missing = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-project",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--target",
                    "profile:langgraph",
                    "--profile-path",
                    profile,
                    "--purpose",
                    "project profile",
                    "--ttl",
                    "300",
                ],
                state,
                expect=3,
            )
            self.assertFalse(missing["ok"])
            self.assertEqual(missing["error"], "authorization_required")

            receipt = write_receipt(state, target="profile:langgraph", session="session-a")
            reserved = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-project",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--target",
                    "profile:langgraph",
                    "--profile-path",
                    profile,
                    "--purpose",
                    "project profile",
                    "--ttl",
                    "300",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            self.assertTrue(reserved["ok"])
            self.assertFalse(reserved["cleanup_allowed"])

            receipt_b = write_receipt(state, target="profile:langgraph-copy", session="session-b")
            duplicate = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-project",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-b",
                    "--target",
                    "profile:langgraph-copy",
                    "--profile-path",
                    profile,
                    "--purpose",
                    "same profile",
                    "--ttl",
                    "300",
                    "--authorization-receipt",
                    str(receipt_b),
                ],
                state,
                expect=2,
            )
            self.assertEqual(duplicate["error"], "project_profile_already_owned")

    def test_human_owned_is_never_managed_and_human_delegated_needs_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            human_owned = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "human-owned",
                    "--project",
                    "personal",
                    "--session",
                    "session-a",
                    "--target",
                    "tab:personal",
                    "--profile-path",
                    r"C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--purpose",
                    "bad",
                    "--ttl",
                    "300",
                ],
                state,
                expect=2,
            )
            self.assertEqual(human_owned["error"], "human_owned_not_managed")

            delegated = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "human-delegated",
                    "--project",
                    "personal",
                    "--session",
                    "session-a",
                    "--target",
                    "tab:personal",
                    "--profile-path",
                    r"C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--purpose",
                    "needs auth",
                    "--ttl",
                    "300",
                ],
                state,
                expect=3,
            )
            self.assertEqual(delegated["error"], "authorization_required")

    def test_same_target_can_only_have_one_owner(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            base = [
                "lease",
                "reserve",
                "--owner-class",
                "codex-managed-isolated",
                "--project",
                "pythonproject-langgraph",
                "--target",
                "tab:shared",
                "--purpose",
                "target exclusivity",
                "--ttl",
                "300",
            ]
            first = run_cmd([*base, "--session", "session-a", "--profile-path", r"C:\tmp\a"], state)
            self.assertTrue(first["ok"])
            second = run_cmd([*base, "--session", "session-b", "--profile-path", r"C:\tmp\b"], state, expect=2)
            self.assertEqual(second["error"], "target_already_owned")

    def test_stale_scan_and_cleanup_dry_run_never_delete_human_or_project_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            isolated = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-isolated",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--target",
                    "tab:stale",
                    "--profile-path",
                    r"C:\tmp\isolated",
                    "--purpose",
                    "expired isolated",
                    "--ttl",
                    "-1",
                ],
                state,
            )
            receipt = write_receipt(state, target="profile:project", session="session-b")
            project = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-project",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-b",
                    "--target",
                    "profile:project",
                    "--profile-path",
                    r"C:\tmp\project",
                    "--purpose",
                    "expired project",
                    "--ttl",
                    "-1",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            delegated_receipt = write_receipt(state, target="tab:delegated", session="session-c")
            delegated = run_cmd(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "human-delegated",
                    "--project",
                    "personal",
                    "--session",
                    "session-c",
                    "--target",
                    "tab:delegated",
                    "--profile-path",
                    r"C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--purpose",
                    "expired delegated human tab",
                    "--ttl",
                    "-1",
                    "--authorization-receipt",
                    str(delegated_receipt),
                ],
                state,
            )

            stale = run_cmd(["stale-scan", "--dry-run"], state)
            self.assertTrue(stale["dry_run"])
            self.assertFalse(stale["registry_mutated"])
            self.assertEqual(
                {item["lease_id"] for item in stale["stale_candidates"]},
                {isolated["lease"]["lease_id"], project["lease"]["lease_id"], delegated["lease"]["lease_id"]},
            )

            cleanup = run_cmd(["cleanup", "dry-run"], state)
            self.assertFalse(cleanup["cleanup_performed"])
            self.assertFalse(cleanup["human_owned_cleanup_performed"])
            self.assertEqual([item["lease_id"] for item in cleanup["cleanup_candidates"]], [isolated["lease"]["lease_id"]])
            self.assertEqual(
                {item["lease_id"] for item in cleanup["protected_profiles"]},
                {project["lease"]["lease_id"], delegated["lease"]["lease_id"]},
            )
            self.assertEqual(cleanup["deleted_profiles"], [])


if __name__ == "__main__":
    unittest.main()
