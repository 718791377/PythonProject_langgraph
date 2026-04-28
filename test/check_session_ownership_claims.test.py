import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_session_ownership_claims.py"


class SessionOwnershipClaimsCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root.parent / f"{root.name}-wt-a", ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(root.parent / f"{root.name}-wt-b", ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
        return root

    def add_worktree(self, root: Path, suffix: str, branch: str) -> Path:
        worktree = root.parent / f"{root.name}-{suffix}"
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return worktree

    def write_claim(
        self,
        worktree: Path,
        *,
        session_id: str,
        branch: str,
        openspec_changes: list[str] | None = None,
        paths: list[str] | None = None,
    ) -> Path:
        claim_dir = worktree / ".omx" / "session-claims"
        claim_dir.mkdir(parents=True, exist_ok=True)
        claim_path = claim_dir / f"{session_id}.json"
        claim_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": session_id,
                    "status": "active",
                    "branch": branch,
                    "worktree": str(worktree),
                    "task_type": "implementation",
                    "openspec_changes": openspec_changes or [],
                    "paths": paths or [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return claim_path

    def run_check(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_without_claims_for_clean_repo(self) -> None:
        root = self.make_repo("claims-clean")
        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["active_claims"], 0)

    def test_requires_claim_for_current_dirty_feature_worktree(self) -> None:
        root = self.make_repo("claims-current-dirty")
        subprocess.run(["git", "checkout", "-b", "feature/current"], cwd=root, check=True, capture_output=True, text=True)
        (root / "feature.txt").write_text("dirty\n", encoding="utf-8")

        missing = self.run_check(root, "--allow-current-dirty")
        self.assertNotEqual(missing.returncode, 0)
        missing_payload = json.loads(missing.stdout)
        self.assertTrue(any("no active session ownership claim" in error for error in missing_payload["errors"]))

        self.write_claim(
            root,
            session_id="current-session",
            branch="feature/current",
            openspec_changes=["example-change"],
            paths=["feature.txt"],
        )
        claimed = self.run_check(root, "--allow-current-dirty")
        self.assertEqual(claimed.returncode, 0, claimed.stdout + "\n" + claimed.stderr)
        claimed_payload = json.loads(claimed.stdout)
        self.assertTrue(claimed_payload["ok"])
        self.assertEqual(claimed_payload["counts"]["active_claims"], 1)

    def test_fails_for_duplicate_openspec_change_claims(self) -> None:
        root = self.make_repo("claims-duplicate-change")
        left = self.add_worktree(root, "wt-a", "feature/a")
        right = self.add_worktree(root, "wt-b", "feature/b")
        self.write_claim(left, session_id="left", branch="feature/a", openspec_changes=["same-change"])
        self.write_claim(right, session_id="right", branch="feature/b", openspec_changes=["same-change"])

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("same-change" in error for error in payload["errors"]))

    def test_fails_for_overlapping_path_claims(self) -> None:
        root = self.make_repo("claims-overlap-path")
        left = self.add_worktree(root, "wt-a", "feature/a")
        right = self.add_worktree(root, "wt-b", "feature/b")
        self.write_claim(left, session_id="left", branch="feature/a", paths=["openspec/changes/example"])
        self.write_claim(right, session_id="right", branch="feature/b", paths=["openspec/changes/example/tasks.md"])

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Path scope overlap" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
