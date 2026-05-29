import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_SCRIPT = REPO_ROOT / "tools" / "local_main_retire_lock.py"
CHECK_SCRIPT = REPO_ROOT / "tools" / "check_local_main_retire_lock.py"


class LocalMainRetireLockTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def run_lock(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LOCK_SCRIPT), *args, "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def acquire(self, root: Path, session_id: str = "session-a", entry_id: str = "entry-a", ttl: int = 120) -> dict:
        result = self.run_lock(
            root,
            "acquire",
            "--session-id",
            session_id,
            "--branch",
            "feature/self-retire",
            "--worktree",
            str(root / "worktree"),
            "--entry-id",
            entry_id,
            "--ttl-minutes",
            str(ttl),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        return payload

    def test_acquire_status_and_release_roundtrip(self) -> None:
        root = self.make_root("retire-lock-roundtrip")

        acquired = self.acquire(root)
        nonce = acquired["nonce"]
        self.assertEqual(acquired["lock"]["owner_session_id"], "session-a")

        status = self.run_lock(root, "status")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        status_payload = json.loads(status.stdout)
        self.assertTrue(status_payload["locked"])
        self.assertFalse(status_payload["expired"])

        check = self.run_check(root)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        check_payload = json.loads(check.stdout)
        self.assertTrue(check_payload["ok"])
        self.assertEqual(check_payload["counts"]["active_locks"], 1)

        released = self.run_lock(root, "release", "--nonce", nonce)
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        released_payload = json.loads(released.stdout)
        self.assertTrue(released_payload["ok"])
        self.assertFalse((root / ".omx/locks/local-main-retire.lock").exists())

        clean_check = self.run_check(root)
        self.assertEqual(clean_check.returncode, 0, clean_check.stdout + clean_check.stderr)
        self.assertEqual(json.loads(clean_check.stdout)["counts"]["active_locks"], 0)

    def test_second_session_is_denied_while_lock_is_active(self) -> None:
        root = self.make_root("retire-lock-deny")
        self.acquire(root, session_id="session-a")

        denied = self.run_lock(
            root,
            "acquire",
            "--session-id",
            "session-b",
            "--branch",
            "feature/other",
            "--worktree",
            str(root / "other"),
            "--entry-id",
            "entry-b",
        )

        self.assertNotEqual(denied.returncode, 0)
        payload = json.loads(denied.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("active local-main retire lock exists" in error for error in payload["errors"]))

    def test_nonce_mismatch_refuses_release(self) -> None:
        root = self.make_root("retire-lock-nonce")
        self.acquire(root)

        released = self.run_lock(root, "release", "--nonce", "wrong-nonce")

        self.assertNotEqual(released.returncode, 0)
        payload = json.loads(released.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("nonce mismatch" in error for error in payload["errors"]))
        self.assertTrue((root / ".omx/locks/local-main-retire.lock").exists())

    def test_stale_reclaim_requires_explicit_flag(self) -> None:
        root = self.make_root("retire-lock-stale")
        self.acquire(root, ttl=1)
        path = root / ".omx/locks/local-main-retire.lock"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["expires_at"] = "2000-01-01T00:00:00+00:00"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        denied = self.run_lock(
            root,
            "acquire",
            "--session-id",
            "session-b",
            "--branch",
            "feature/reclaim",
            "--worktree",
            str(root / "reclaim"),
            "--entry-id",
            "entry-b",
        )
        self.assertNotEqual(denied.returncode, 0)
        self.assertTrue(any("requires --reclaim-stale" in error for error in json.loads(denied.stdout)["errors"]))

        reclaimed = self.run_lock(
            root,
            "acquire",
            "--session-id",
            "session-b",
            "--branch",
            "feature/reclaim",
            "--worktree",
            str(root / "reclaim"),
            "--entry-id",
            "entry-b",
            "--reclaim-stale",
        )
        self.assertEqual(reclaimed.returncode, 0, reclaimed.stdout + reclaimed.stderr)
        payload = json.loads(reclaimed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["lock"]["owner_session_id"], "session-b")
        self.assertTrue(any("stale" in warning for warning in payload["warnings"]))
        self.assertTrue((root / ".omx/locks/archive").exists())


if __name__ == "__main__":
    unittest.main()