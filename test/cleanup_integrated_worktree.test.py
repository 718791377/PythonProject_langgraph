import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "cleanup_integrated_worktree.py"

spec = importlib.util.spec_from_file_location("cleanup_integrated_worktree", SCRIPT_PATH)
cleanup = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cleanup)

ADVANCE_LIFECYCLE_SCRIPT_PATH = REPO_ROOT / "tools" / "advance_worktree_task_lifecycle.py"
advance_spec = importlib.util.spec_from_file_location(
    "advance_worktree_task_lifecycle", ADVANCE_LIFECYCLE_SCRIPT_PATH
)
assert advance_spec is not None
advance_lifecycle_module = importlib.util.module_from_spec(advance_spec)
assert advance_spec.loader is not None
advance_spec.loader.exec_module(advance_lifecycle_module)


class IntegratedWorktreeCleanupTest(unittest.TestCase):
    def run_git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def make_repo(self, root: Path) -> None:
        self.run_git(root, "init", "-b", "main")
        self.run_git(root, "config", "user.name", "Test User")
        self.run_git(root, "config", "user.email", "test@example.com")
        (root / ".gitignore").write_text(".omx/session-claims/\n", encoding="utf-8")
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        self.run_git(root, "add", ".gitignore", "README.md")
        self.run_git(root, "commit", "-m", "init")

    def test_safe_claim_name_is_path_safe(self) -> None:
        self.assertEqual(cleanup.safe_claim_name("feature/foo\\bar"), "feature__foo__bar")

    def test_path_is_relative_to_blocks_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = root / ".worktrees" / "feature"
            sibling = root / "other"
            allowed.mkdir(parents=True)
            sibling.mkdir()

            self.assertTrue(cleanup.path_is_relative_to(allowed, root / ".worktrees"))
            self.assertFalse(cleanup.path_is_relative_to(sibling, root / ".worktrees"))

    def test_primary_root_from_common_dir_handles_linked_worktree_common_dir(self) -> None:
        self.assertEqual(
            cleanup.primary_root_from_common_dir(Path("repo/.git").resolve()),
            Path("repo").resolve(),
        )

    def test_backup_refs_for_branch_filters_by_before_suffix(self) -> None:
        refs_output = "\n".join(
            [
                "refs/backup/local-main/20260518120000-before-topic",
                "refs/backup/local-main/20260518120000-before-other",
                "refs/heads/topic",
            ]
        )

        class Result:
            returncode = 0
            stdout = refs_output

        original = cleanup.run_git
        try:
            cleanup.run_git = lambda root, args, check=False: Result()  # type: ignore[assignment]
            self.assertEqual(
                cleanup.backup_refs_for_branch(Path("."), "topic"),
                ["refs/backup/local-main/20260518120000-before-topic"],
            )
        finally:
            cleanup.run_git = original  # type: ignore[assignment]

    def test_payload_documents_non_destructive_policy(self) -> None:
        payload = cleanup.payload(
            Path("repo"),
            "topic",
            Path("repo/.worktrees/topic"),
            "main",
            "main-head",
            "branch-head",
            ["refs/backup/local-main/20260518120000-before-topic"],
            {"status": "completed", "_source_claim_path": "claim.json"},
            [],
            [],
            [],
        )

        self.assertTrue(payload["cleanup_ready"])
        self.assertFalse(payload["safety_policy"]["deletes_remote_refs"])
        self.assertFalse(payload["safety_policy"]["deletes_backup_refs"])
        self.assertFalse(payload["safety_policy"]["uses_force_branch_delete"])

    def test_copy_claim_to_primary_preserves_cleanup_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = cleanup.payload(
                root,
                "topic",
                root / ".worktrees" / "topic",
                "main",
                "main-head",
                "branch-head",
                ["refs/backup/local-main/20260518120000-before-topic"],
                {"status": "completed"},
                [],
                [],
                [],
            )

            target = cleanup.copy_claim_to_primary(root, {"status": "completed"}, "topic", result)
            data = json.loads(target.read_text(encoding="utf-8"))

            self.assertEqual(data["status"], "completed")
            self.assertEqual(data["cleanup"]["cleanup_check"]["branch"], "topic")
            self.assertTrue(target.as_posix().endswith(".omx/session-claims/completed/topic.json"))

    def test_execute_cleanup_removes_integrated_worktree_and_branch_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.make_repo(root)
            branch = "topic-cleanup"
            worktree = root / ".worktrees" / branch
            self.run_git(root, "worktree", "add", "-b", branch, str(worktree), "main")

            (worktree / "feature.txt").write_text("feature\n", encoding="utf-8")
            self.run_git(worktree, "add", "feature.txt")
            self.run_git(worktree, "commit", "-m", "feature")

            backup_ref = f"refs/backup/local-main/test-before-{branch}"
            pre_merge_head = self.run_git(root, "rev-parse", "main").stdout.strip()
            self.run_git(root, "update-ref", backup_ref, "main")
            self.run_git(root, "merge", "--ff-only", branch)

            claim_dir = worktree / ".omx" / "session-claims"
            claim_dir.mkdir(parents=True)
            claim = {
                "schema_version": 1,
                "session_id": branch,
                "status": "completed",
                "branch": branch,
                "worktree": str(worktree),
            }
            (claim_dir / f"{branch}.json").write_text(json.dumps(claim), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--root",
                    str(root),
                    "--branch",
                    branch,
                    "--worktree",
                    str(worktree),
                    "--execute",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["executed"])
            self.assertFalse(worktree.exists())
            self.assertEqual(self.run_git(root, "rev-parse", "--verify", backup_ref).stdout.strip(), pre_merge_head)
            deleted_branch = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--verify", branch],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(deleted_branch.returncode, 0)
            preserved_claim = root / ".omx" / "session-claims" / "completed" / f"{branch}.json"
            self.assertTrue(preserved_claim.exists())
            preserved = json.loads(preserved_claim.read_text(encoding="utf-8"))
            self.assertEqual(preserved["branch"], branch)
            self.assertEqual(preserved["status"], "cleaned")
            self.assertEqual(preserved["lifecycle_status"], "cleaned")
            self.assertEqual(preserved["cleanup"]["cleanup_check"]["backup_refs"], [backup_ref])
            self.assertTrue(preserved["cleanup"]["cleaned_lifecycle_recorded"])
            self.assertEqual(preserved["completion"]["cleaned_worktree"], str(worktree))
            self.assertEqual(preserved["completion"]["deleted_branch"], branch)
            transition = preserved["lifecycle_transitions"][-1]
            self.assertEqual(transition["previous_state"], "completed")
            self.assertEqual(transition["next_state"], "cleaned")
            self.assertEqual(transition["owner"], "tools/cleanup_integrated_worktree.py")


class AdvanceWorktreeTaskLifecycleTest(unittest.TestCase):
    def make_worktree_metadata(self, root: Path, *, lifecycle_status: str = "active") -> tuple[Path, Path]:
        branch = "feature/demo"
        receipt_path = root / ".omx" / "worktree-task-receipt.json"
        claim_path = root / ".omx" / "session-claims" / "demo.json"
        common = {
            "schema_version": 1,
            "session_id": "session-demo",
            "status": lifecycle_status,
            "lifecycle_status": lifecycle_status,
            "branch": branch,
            "worktree": str(root),
            "task_name": "demo lifecycle",
            "task_summary": "exercise lifecycle helper",
            "document_plan_only": False,
            "requires_code_implementation": True,
            "created_at": "2026-06-05T00:00:00+00:00",
            "expected_merge_or_pause": "merge locally",
            "next_action": "advance lifecycle",
            "requires_local_main_merge": True,
            "requires_remote_sync": False,
            "remote_publication_authorized": False,
            "paths": ["tools/example.py"],
        }
        receipt_path.parent.mkdir(parents=True)
        claim_path.parent.mkdir(parents=True)
        receipt_path.write_text(json.dumps(common, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        claim_path.write_text(json.dumps(common, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return receipt_path, claim_path

    def test_active_to_ready_updates_receipt_and_claim_with_transition_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt_path, claim_path = self.make_worktree_metadata(root)

            result = advance_lifecycle_module.advance_lifecycle(
                worktree=root,
                branch="feature/demo",
                next_state="ready-to-merge",
                owner="codex-test",
                evidence_paths=["test/cleanup_integrated_worktree.test.py"],
                cleanup_decision="not-ready-for-cleanup",
                reason="focused test",
            )

            self.assertTrue(result["ok"], result)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            claim = json.loads(claim_path.read_text(encoding="utf-8"))
            for payload in (receipt, claim):
                self.assertEqual(payload["lifecycle_status"], "ready-to-merge")
                self.assertEqual(payload["status"], "ready-to-merge")
                self.assertFalse(payload["remote_publication_authorized"])
                transition = payload["lifecycle_transitions"][-1]
                self.assertEqual(transition["owner"], "codex-test")
                self.assertEqual(transition["previous_state"], "active")
                self.assertEqual(transition["next_state"], "ready-to-merge")
                self.assertEqual(transition["cleanup_decision"], "not-ready-for-cleanup")
                self.assertEqual(transition["evidence_paths"], ["test/cleanup_integrated_worktree.test.py"])

    def test_merged_local_main_requires_rollback_and_local_main_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_worktree_metadata(root, lifecycle_status="ready-to-merge")

            with self.assertRaises(ValueError):
                advance_lifecycle_module.advance_lifecycle(
                    worktree=root,
                    branch="feature/demo",
                    next_state="merged-local-main",
                    owner="codex-test",
                    evidence_paths=["local_gate"],
                    cleanup_decision="pending-automatic-safe-cleanup",
                )

            result = advance_lifecycle_module.advance_lifecycle(
                worktree=root,
                branch="feature/demo",
                next_state="merged-local-main",
                owner="codex-test",
                evidence_paths=["local_gate", "local_mr_review"],
                cleanup_decision="pending-automatic-safe-cleanup",
                rollback_ref="refs/backup/local-main/test-before-feature-demo",
                local_main_commit="abc123",
                cleaned_worktree="pending-automatic-safe-cleanup",
                deleted_branch="pending-automatic-safe-cleanup",
                remote_sync_status="not_authorized:remote_publication_gate_closed",
            )

            self.assertTrue(result["ok"], result)
            receipt = json.loads((root / ".omx" / "worktree-task-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["lifecycle_status"], "merged-local-main")
            self.assertEqual(receipt["completion"]["rollback_ref"], "refs/backup/local-main/test-before-feature-demo")
            self.assertEqual(receipt["completion"]["local_main_commit"], "abc123")
            self.assertEqual(receipt["completion"]["remote_sync_status"], "not_authorized:remote_publication_gate_closed")

    def test_exceptional_stale_transition_requires_reason_or_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_worktree_metadata(root)

            with self.assertRaises(ValueError):
                advance_lifecycle_module.advance_lifecycle(
                    worktree=root,
                    branch="feature/demo",
                    next_state="stale",
                    owner="codex-test",
                    evidence_paths=[],
                    cleanup_decision="preserve-for-classification",
                )

            result = advance_lifecycle_module.advance_lifecycle(
                worktree=root,
                branch="feature/demo",
                next_state="stale",
                owner="codex-test",
                evidence_paths=[],
                cleanup_decision="preserve-for-classification",
                reason="superseded by newer local-main package",
            )

            self.assertTrue(result["ok"], result)
            receipt = json.loads((root / ".omx" / "worktree-task-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["lifecycle_status"], "stale")
            self.assertNotIn("completion", receipt)

    def test_lifecycle_cli_outputs_json_and_updates_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_worktree_metadata(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ADVANCE_LIFECYCLE_SCRIPT_PATH),
                    "--worktree",
                    str(root),
                    "--branch",
                    "feature/demo",
                    "--next-state",
                    "paused",
                    "--owner",
                    "codex-test",
                    "--reason",
                    "waiting for operator",
                    "--cleanup-decision",
                    "preserve-for-resume",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"], payload)
            receipt = json.loads((root / ".omx" / "worktree-task-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["lifecycle_status"], "paused")


if __name__ == "__main__":
    unittest.main()
