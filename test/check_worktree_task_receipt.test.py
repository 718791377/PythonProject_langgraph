from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_worktree_task_receipt.py"
FIXTURE_DIR = REPO_ROOT / "test" / "fixtures" / "worktree_task_receipts"
spec = importlib.util.spec_from_file_location("check_worktree_task_receipt", SCRIPT_PATH)
receipt = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(receipt)


class WorktreeTaskReceiptTest(unittest.TestCase):
    def base_receipt(self, *, lifecycle_status: str = "active", status: str | None = "active") -> dict[str, object]:
        data: dict[str, object] = {
            "schema_version": 1,
            "session_id": "s1",
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
            "lifecycle_status": lifecycle_status,
            "paths": ["docs/example.md"],
        }
        if status is not None:
            data["status"] = status
        return data

    def complete_receipt(self, *, lifecycle_status: str = "completed") -> dict[str, object]:
        data = self.base_receipt(lifecycle_status=lifecycle_status, status=lifecycle_status)
        data.update(
            {
                "document_plan_only": False,
                "requires_code_implementation": True,
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
        )
        return data

    def validate(self, data: dict[str, object], *, require_completion: bool = False) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        receipt.validate_metadata(
            data,
            path=Path("receipt.json"),
            branch="feature/demo",
            worktree_path=Path.cwd(),
            errors=errors,
            warnings=warnings,
            require_completion=require_completion,
        )
        return errors, warnings

    def test_validate_metadata_accepts_required_lifecycle_fields(self) -> None:
        errors: list[str] = []
        warnings: list[str] = []
        summary = receipt.validate_metadata(
            self.base_receipt(),
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

    def test_fixture_covers_every_allowed_lifecycle_state(self) -> None:
        fixture_statuses = {path.stem for path in FIXTURE_DIR.glob("*.json")}
        self.assertEqual(fixture_statuses, receipt.ALLOWED_LIFECYCLE_STATUSES)

        for fixture in sorted(FIXTURE_DIR.glob("*.json")):
            with self.subTest(fixture=fixture.name):
                data = json.loads(fixture.read_text(encoding="utf-8"))
                data["worktree"] = str(Path.cwd())
                errors, _warnings = self.validate(data)
                self.assertEqual(errors, [])

    def test_stale_receipt_and_claim_status_are_allowed_without_completion_fields(self) -> None:
        errors, _warnings = self.validate(self.base_receipt(lifecycle_status="stale", status="stale"))
        self.assertEqual(errors, [])

    def test_branch_matching_claim_accepts_stale_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            claim_dir = worktree / ".omx" / "session-claims"
            claim_dir.mkdir(parents=True)
            (claim_dir / "claim.json").write_text(
                json.dumps({"schema_version": 1, "branch": "feature/demo", "status": "stale"}),
                encoding="utf-8",
            )
            errors: list[str] = []

            matches = receipt.matching_claims(worktree, "feature/demo", errors)

        self.assertEqual(len(matches), 1)
        self.assertEqual(errors, [])

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
        data = self.complete_receipt()
        errors, _warnings = self.validate(data, require_completion=True)
        self.assertEqual(errors, [])
        del data["completion"]["rollback_ref"]
        errors, _warnings = self.validate(data, require_completion=True)
        self.assertIn("receipt.json: completion `rollback_ref` is required for lifecycle `completed`", errors)

    def test_completion_evidence_required_only_for_integration_lifecycle_states(self) -> None:
        completion_required = receipt.COMPLETION_REQUIRED_LIFECYCLE_STATUSES
        no_completion_required = receipt.ALLOWED_LIFECYCLE_STATUSES - completion_required

        for lifecycle in sorted(completion_required):
            with self.subTest(lifecycle=lifecycle):
                errors, _warnings = self.validate(self.base_receipt(lifecycle_status=lifecycle, status=lifecycle))
                self.assertTrue(
                    any("completion `completed_at` is required" in error for error in errors),
                    errors,
                )

        for lifecycle in sorted(no_completion_required):
            with self.subTest(lifecycle=lifecycle):
                errors, _warnings = self.validate(self.base_receipt(lifecycle_status=lifecycle, status=lifecycle))
                self.assertEqual(errors, [])

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

    def test_classifies_unmanaged_team_and_completed_langgraph_residue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            team_dir = root / ".omx" / "state" / "team" / "legacy-team"
            team_dir.mkdir(parents=True)
            (team_dir / "state.json").write_text('{"status":"paused"}\n', encoding="utf-8")
            langgraph_root = root / ".omx" / "state" / "langgraph"
            (langgraph_root / "threads").mkdir(parents=True)
            (langgraph_root / "backend.json").write_text(
                json.dumps(
                    {
                        "backend": "langgraph",
                        "thread_id": "legacy-thread",
                        "repo_root": str(root),
                        "status": "completed",
                    }
                ),
                encoding="utf-8",
            )
            (langgraph_root / "threads" / "legacy-thread.json").write_text(
                json.dumps({"thread_id": "legacy-thread", "status": "completed"}),
                encoding="utf-8",
            )

            records = receipt.classify_durable_residue(root)

        by_kind = {record["kind"]: record for record in records}
        unmanaged = by_kind["non_empty_unmanaged_native_team_directory"]
        self.assertEqual(unmanaged["state_class"], "protected_residue")
        self.assertEqual(unmanaged["safe_next_action"], "manual-inspection-required")
        self.assertFalse(unmanaged["auto_adopt_allowed"])
        langgraph = by_kind["completed_langgraph_state"]
        self.assertEqual(langgraph["state_class"], "legacy_completed_state")
        self.assertEqual(langgraph["safe_next_action"], "inspect-or-archive; do-not-auto-resume")
        self.assertFalse(langgraph["auto_adopt_allowed"])

    def test_classifies_stale_and_active_selectors_without_auto_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as stale_tmp, tempfile.TemporaryDirectory() as active_tmp:
            stale_root = Path(stale_tmp)
            stale_selector = stale_root / ".omx" / "state" / "selectors" / "active.json"
            stale_selector.parent.mkdir(parents=True)
            stale_selector.write_text(
                json.dumps(
                    {
                        "backend_family": "langgraph",
                        "repo_root": str(stale_root / "other-repo"),
                        "thread_id": "old-thread",
                    }
                ),
                encoding="utf-8",
            )

            active_root = Path(active_tmp)
            active_selector = active_root / ".omx" / "state" / "selectors" / "active.json"
            active_selector.parent.mkdir(parents=True)
            active_selector.write_text(
                json.dumps(
                    {
                        "backend_family": "native_omx",
                        "repo_root": str(active_root),
                        "team_name": "current-team",
                    }
                ),
                encoding="utf-8",
            )

            stale_records = receipt.classify_durable_residue(stale_root)
            active_records = receipt.classify_durable_residue(active_root)

        stale = {record["kind"]: record for record in stale_records}["stale_selector"]
        self.assertEqual(stale["state_class"], "stale_selector")
        self.assertEqual(stale["safe_next_action"], "refresh-selector-or-ignore-as-stale")
        self.assertFalse(stale["auto_adopt_allowed"])

        active = {record["kind"]: record for record in active_records}["active_current_selector"]
        self.assertEqual(active["state_class"], "selector_authority")
        self.assertEqual(active["safe_next_action"], "inspect-as-current-authority; do-not-auto-adopt-by-itself")
        self.assertFalse(active["auto_adopt_allowed"])

    def test_evaluate_includes_durable_residue_classification_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
            empty_team = root / ".omx" / "state" / "team" / "empty-team"
            empty_team.mkdir(parents=True)

            payload = receipt.evaluate(root, require_all_feature_worktrees=False, require_completion_for_completed=False)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("durable_residue_classification", payload)
        self.assertIn("durable_residue_classification_summary", payload)
        self.assertEqual(
            payload["durable_residue_classification_summary"]["by_kind"]["empty_unmanaged_native_team_directory"], 1
        )


if __name__ == "__main__":
    unittest.main()
