import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_worktree_session_hygiene.py"


class WorktreeSessionHygieneCheckTest(unittest.TestCase):
    maxDiff = None

    def make_repo(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "branch", "gitlab/main"], cwd=root, check=True)
        return root

    def run_check(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--main-ref", "gitlab/main", "--json", *extra],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def make_feature_worktree(self, root: Path, branch: str = "feature/test") -> Path:
        worktree = root.parent / f"{root.name}-feature-{uuid.uuid4().hex[:8]}"
        self.addCleanup(lambda: shutil.rmtree(worktree, ignore_errors=True))
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.addCleanup(
            lambda: subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
        )
        return worktree

    def test_passes_for_clean_main(self) -> None:
        root = self.make_repo("worktree-clean")
        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["dirty_worktrees"], 0)
        self.assertTrue(payload["primary_worktree_alignment"]["ok"])

    def test_fails_when_main_worktree_is_dirty(self) -> None:
        root = self.make_repo("worktree-main-dirty")
        (root / "README.md").write_text("# Dirty\n", encoding="utf-8")
        result = self.run_check(root, "--allow-current-dirty")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Main branch worktree is dirty" in error for error in payload["errors"]))

    def test_allows_current_dirty_feature_worktree_when_requested(self) -> None:
        root = self.make_repo("worktree-feature-dirty")
        feature_worktree = self.make_feature_worktree(root)
        (feature_worktree / "feature.txt").write_text("dirty\n", encoding="utf-8")
        result = self.run_check(feature_worktree, "--allow-current-dirty")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["dirty_worktrees"], 1)

    def test_fails_for_current_dirty_feature_worktree_without_override(self) -> None:
        root = self.make_repo("worktree-feature-dirty-fail")
        feature_worktree = self.make_feature_worktree(root)
        (feature_worktree / "feature.txt").write_text("dirty\n", encoding="utf-8")
        result = self.run_check(feature_worktree)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("Current non-main worktree is dirty" in error for error in payload["errors"]))

    def test_fails_when_primary_directory_is_not_on_local_main(self) -> None:
        root = self.make_repo("worktree-primary-feature")
        subprocess.run(["git", "checkout", "-b", "feature/test"], cwd=root, check=True, capture_output=True, text=True)
        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["primary_worktree_alignment"]["ok"])
        self.assertTrue(any("Primary repository directory is on feature/test" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
