import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "complete_local_flow_to_remote_gate.py"
PLAN = "docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md"


class CompleteLocalFlowSelfRetirePreflightTest(unittest.TestCase):
    maxDiff = None

    def run_git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(cwd), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def git_ok(self, cwd: Path, *args: str) -> str:
        result = self.run_git(cwd, *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def make_repo_with_feature_worktree(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, str, str, str]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base_dir = Path(temp.name)
        root = base_dir / "repo"
        worktree = base_dir / "feature-wt"
        root.mkdir()
        self.git_ok(root, "init", "-b", "main")
        self.git_ok(root, "config", "user.email", "codex@example.invalid")
        self.git_ok(root, "config", "user.name", "Codex Test")
        (root / "README.md").write_text("base\n", encoding="utf-8")
        (root / ".gitignore").write_text(".omx/\n", encoding="utf-8")
        self.git_ok(root, "add", "README.md", ".gitignore")
        self.git_ok(root, "commit", "-m", "base")
        base_main = self.git_ok(root, "rev-parse", "main")

        branch = "feature/self-retire"
        self.git_ok(root, "worktree", "add", "-b", branch, str(worktree), "main")
        (worktree / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.git_ok(worktree, "add", "feature.txt")
        self.git_ok(worktree, "commit", "-m", "feature")
        feature_head = self.git_ok(worktree, "rev-parse", "HEAD")
        return temp, root, worktree, branch, base_main, feature_head

    def write_receipt(self, worktree: Path, *, plan: str = PLAN) -> None:
        path = worktree / ".omx" / "worktree-task-receipt.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": "session-self",
                    "implementation_plan": plan,
                    "lifecycle_status": "active",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def write_rob_entry(self, root: Path, worktree: Path, branch_name: str, **overrides: object) -> None:
        entry = {
            "schema_version": 1,
            "entry_id": "self-entry",
            "state": "ready",
            "session_id": "session-self",
            "implementation_plan": PLAN,
            "branch": branch_name,
            "worktree": str(worktree),
            "base_main": "base",
            "predicted_write_set": ["tools/complete_local_flow_to_remote_gate.py"],
            "actual_write_set": ["tools/complete_local_flow_to_remote_gate.py"],
            "hotspots": ["local-main"],
            "dependencies": [],
            "gate_status": {
                "precommit_update_archive": "passed",
                "local_gate": "passed",
                "local_mr_review": "passed",
            },
            "evidence": ["local verification"],
        }
        entry.update(overrides)
        path = root / ".omx" / "commit-rob" / "entries" / "self-entry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def run_flow(self, root: Path, worktree: Path, branch: str, *, entry_id: str = "self-entry") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(root),
                "--worktree",
                str(worktree),
                "--branch",
                branch,
                "--self-retire",
                "--session-id",
                "session-self",
                "--rob-entry-id",
                entry_id,
                "--execute",
                "--skip-local-gate",
                "--skip-local-mr-review",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(worktree),
        )

    def assert_failed_before_local_main_mutation(
        self,
        result: subprocess.CompletedProcess[str],
        root: Path,
        base_main: str,
        expected_error: str,
    ) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"], payload)
        self.assertTrue(
            any(expected_error in error for error in payload["errors"]),
            payload["errors"],
        )
        self.assertEqual(self.git_ok(root, "rev-parse", "main"), base_main)
        backup_refs = self.git_ok(root, "for-each-ref", "refs/backup/local-main", "--format=%(refname)")
        self.assertEqual(backup_refs, "")
        self.assertFalse((root / ".omx" / "locks" / "local-main-retire.lock").exists())
        self.assertFalse((root / ".omx" / "locks" / "archive").exists())

    def test_self_retire_missing_rob_entry_fails_before_local_main_mutation(self) -> None:
        _temp, root, worktree, branch, base_main, _feature_head = self.make_repo_with_feature_worktree()
        self.write_receipt(worktree)

        result = self.run_flow(root, worktree, branch, entry_id="missing-entry")

        self.assert_failed_before_local_main_mutation(result, root, base_main, "ROB entry not found")

    def test_self_retire_preflight_rejects_unready_mismatched_or_missing_gate_entries_before_mutation(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = [
            ("unready", {"state": "executing"}, "state must be ready"),
            ("session mismatch", {"session_id": "other-session"}, "session_id mismatch"),
            ("branch mismatch", {"branch": "feature/other"}, "branch mismatch"),
            ("implementation plan mismatch", {"implementation_plan": "docs_bilingual/implementation_plans/other.md"}, "implementation_plan mismatch"),
            ("missing gate", {"gate_status": {"precommit_update_archive": "passed", "local_mr_review": "passed"}}, "gate_status.local_gate"),
        ]
        for label, overrides, expected_error in cases:
            with self.subTest(label=label):
                _temp, root, worktree, branch, base_main, _feature_head = self.make_repo_with_feature_worktree()
                self.write_receipt(worktree)
                self.write_rob_entry(root, worktree, branch, **overrides)

                result = self.run_flow(root, worktree, branch)

                self.assert_failed_before_local_main_mutation(result, root, base_main, expected_error)

    def test_self_retire_valid_ready_entry_merges_and_records_retired_metadata(self) -> None:
        _temp, root, worktree, branch, _base_main, feature_head = self.make_repo_with_feature_worktree()
        self.write_receipt(worktree)
        self.write_rob_entry(root, worktree, branch)

        result = self.run_flow(root, worktree, branch)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(self.git_ok(root, "rev-parse", "main"), feature_head)
        entry = json.loads((root / ".omx" / "commit-rob" / "entries" / "self-entry.json").read_text(encoding="utf-8"))
        self.assertEqual(entry["state"], "retired")
        self.assertEqual(entry["retire_mode"], "self_retire_lock")
        self.assertEqual(entry["retire_owner_session_id"], "session-self")
        self.assertTrue(entry["retire_lock_nonce"])


if __name__ == "__main__":
    unittest.main()
