from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_worktree_task_receipt.py"
spec = importlib.util.spec_from_file_location("check_worktree_task_receipt", SCRIPT_PATH)
receipt = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(receipt)


class WorktreeTaskReceiptTest(unittest.TestCase):
    def test_validate_metadata_accepts_required_lifecycle_fields(self) -> None:
        errors: list[str] = []
        warnings: list[str] = []
        data = {
            "schema_version": 1,
            "session_id": "s1",
            "status": "active",
            "branch": "feature/demo",
            "worktree": str(Path.cwd()),
            "task_type": "docs",
            "task_name": "demo task",
            "task_summary": "records why this worktree exists",
            "document_plan_only": True,
            "requires_code_implementation": False,
            "created_at": "2026-05-19T00:00:00+00:00",
            "expected_merge_or_pause": "merge after local gate",
            "next_action": "finish docs and cleanup",
            "requires_local_main_merge": True,
            "requires_remote_sync": False,
            "lifecycle_status": "active",
            "paths": ["docs/example.md"],
        }

        summary = receipt.validate_metadata(
            data,
            path=Path("receipt.json"),
            branch="feature/demo",
            worktree_path=Path.cwd(),
            errors=errors,
            warnings=warnings,
            require_completion=False,
        )

        self.assertEqual(errors, [])
        self.assertEqual(summary["task_name"], "demo task")
        self.assertEqual(summary["lifecycle_status"], "active")

    def test_validate_metadata_rejects_missing_lifecycle_and_conflicting_plan_flags(self) -> None:
        errors: list[str] = []
        warnings: list[str] = []
        data = {
            "schema_version": 1,
            "session_id": "s1",
            "branch": "feature/demo",
            "worktree": str(Path.cwd()),
            "task_name": "demo task",
            "task_summary": "records why this worktree exists",
            "document_plan_only": True,
            "requires_code_implementation": True,
            "created_at": "2026-05-19T00:00:00+00:00",
            "expected_merge_or_pause": "merge after local gate",
            "next_action": "finish docs and cleanup",
            "requires_local_main_merge": False,
            "requires_remote_sync": False,
            "lifecycle_status": "unknown",
            "paths": ["docs/example.md"],
        }

        receipt.validate_metadata(
            data,
            path=Path("receipt.json"),
            branch="feature/demo",
            worktree_path=Path.cwd(),
            errors=errors,
            warnings=warnings,
            require_completion=False,
        )

        self.assertIn("receipt.json: `lifecycle_status` must be one of", "\n".join(errors))
        self.assertIn("receipt.json: document-plan-only work cannot also require code implementation", errors)
        self.assertTrue(any("document-plan-only work should normally merge" in warning for warning in warnings))

    def test_completed_lifecycle_requires_completion_receipt(self) -> None:
        errors: list[str] = []
        data = {
            "schema_version": 1,
            "session_id": "s1",
            "branch": "feature/demo",
            "worktree": str(Path.cwd()),
            "task_name": "demo task",
            "task_summary": "records why this worktree exists",
            "document_plan_only": False,
            "requires_code_implementation": True,
            "created_at": "2026-05-19T00:00:00+00:00",
            "expected_merge_or_pause": "merge after local gate",
            "next_action": "cleanup",
            "requires_local_main_merge": True,
            "requires_remote_sync": False,
            "lifecycle_status": "completed",
            "paths": ["tools/example.py"],
            "completion": {
                "completed_at": "2026-05-19T00:30:00+00:00",
                "rollback_ref": "refs/backup/local-main/demo-before-feature-demo",
                "local_main_commit": "abc123",
                "cleaned_worktree": "D:/repo/.worktrees/demo",
                "deleted_branch": "feature/demo",
                "remote_sync_status": "not_synced",
            },
        }

        receipt.validate_metadata(
            data,
            path=Path("receipt.json"),
            branch="feature/demo",
            worktree_path=Path.cwd(),
            errors=errors,
            warnings=[],
            require_completion=True,
        )

        self.assertEqual(errors, [])
        del data["completion"]["rollback_ref"]
        receipt.validate_metadata(
            data,
            path=Path("receipt.json"),
            branch="feature/demo",
            worktree_path=Path.cwd(),
            errors=errors,
            warnings=[],
            require_completion=True,
        )
        self.assertIn("receipt.json: completion `rollback_ref` is required for lifecycle `completed`", errors)

    def test_evaluate_reports_missing_receipt_as_warning_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "worktree", "add", "-b", "feature/demo", ".worktrees/demo"], cwd=root, check=True, capture_output=True)

            soft = receipt.evaluate(root, require_all_feature_worktrees=False, require_completion_for_completed=False)
            strict = receipt.evaluate(root, require_all_feature_worktrees=True, require_completion_for_completed=False)

        self.assertTrue(soft["ok"])
        self.assertGreaterEqual(soft["counts"]["warnings"], 1)
        self.assertFalse(strict["ok"])
        self.assertGreaterEqual(strict["counts"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
