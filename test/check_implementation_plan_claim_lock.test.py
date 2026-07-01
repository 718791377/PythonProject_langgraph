from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO_ROOT / "tools" / "check_implementation_plan_claim_lock.py"
HELPER_PATH = REPO_ROOT / "tools" / "claim_implementation_plan.py"
spec = importlib.util.spec_from_file_location("check_implementation_plan_claim_lock", CHECK_PATH)
claim_lock = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = claim_lock
spec.loader.exec_module(claim_lock)


class ImplementationPlanClaimLockTest(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        plan_dir = root / "docs_bilingual" / "implementation_plans"
        plan_dir.mkdir(parents=True)
        (plan_dir / "example_plan.md").write_text(
            "---\n"
            "doc_id: example_plan\n"
            "lang: en\n"
            "status: active\n"
            "doc_class: implementation_plan\n"
            "zh_cn_path: docs_bilingual/implementation_plans/example_plan.zh-CN.md\n"
            "---\n"
            "# Example\n",
            encoding="utf-8",
        )
        (plan_dir / "example_plan.zh-CN.md").write_text(
            "---\n"
            "doc_id: example_plan\n"
            "lang: zh-CN\n"
            "status: active\n"
            "doc_class: implementation_plan\n"
            "translation_of: docs_bilingual/implementation_plans/example_plan.md\n"
            "---\n"
            "# Example zh\n",
            encoding="utf-8",
        )
        return root

    def write_claim(
        self,
        root: Path,
        name: str,
        *,
        status: str = "active",
        plan: str = "docs_bilingual/implementation_plans/example_plan.md",
        session_id: str | None = None,
        expires_at: str | None = None,
        extra: dict[str, object] | None = None,
    ) -> Path:
        claim_dir = root / ".omx" / "session-claims"
        claim_dir.mkdir(parents=True, exist_ok=True)
        data: dict[str, object] = {
            "schema_version": 1,
            "session_id": session_id or name,
            "status": status,
            "branch": f"feature/{name}",
            "worktree": str(root),
            "task_type": "implementation",
            "implementation_plan": plan,
            "implementation_plan_doc_id": "example_plan",
            "paths": [plan],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if expires_at is not None:
            data["expires_at"] = expires_at
        if extra:
            data.update(extra)
        path = claim_dir / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_passes_with_one_active_claim(self) -> None:
        root = self.make_root()
        self.write_claim(root, "one")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)

    def test_fails_for_conflicting_active_claims_for_same_plan_doc_id(self) -> None:
        root = self.make_root()
        self.write_claim(root, "left", plan="docs_bilingual/implementation_plans/example_plan.md")
        self.write_claim(root, "right", plan="docs_bilingual/implementation_plans/example_plan.zh-CN.md")

        payload = claim_lock.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("multiple active session claims" in error for error in payload["errors"]))

    def test_released_claim_is_ignored_for_conflict_detection(self) -> None:
        root = self.make_root()
        self.write_claim(root, "released", status="released")
        self.write_claim(root, "active")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)
        self.assertEqual(payload["counts"]["released_or_inactive_claims"], 1)

    def test_expired_active_claim_is_stale_warning_not_conflict(self) -> None:
        root = self.make_root()
        stale = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        self.write_claim(root, "stale", expires_at=stale)
        self.write_claim(root, "active")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)
        self.assertEqual(payload["counts"]["stale_claims"], 1)
        self.assertTrue(any("stale" in warning for warning in payload["warnings"]))

    def test_malformed_implementation_plan_claim_fails_closed(self) -> None:
        root = self.make_root()
        self.write_claim(root, "bad", extra={"session_id": "", "implementation_plan": "../outside.md"})

        payload = claim_lock.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("session_id" in error for error in payload["errors"]))
        self.assertTrue(any("implementation_plan" in error for error in payload["errors"]))

    def test_claim_plan_is_validated_in_claim_containing_worktree(self) -> None:
        primary = Path(tempfile.mkdtemp())
        sibling = self.make_root()
        self.addCleanup(lambda: __import__("shutil").rmtree(primary, ignore_errors=True))
        self.write_claim(sibling, "sibling")

        original_discover = claim_lock.discover_worktrees
        try:
            claim_lock.discover_worktrees = lambda root: [primary, sibling]  # type: ignore[assignment]
            payload = claim_lock.evaluate(primary)
        finally:
            claim_lock.discover_worktrees = original_discover  # type: ignore[assignment]

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)

    def test_helper_claim_and_release_round_trip(self) -> None:
        root = self.make_root()
        claim_cmd = [
            sys.executable,
            str(HELPER_PATH),
            "claim",
            "--root",
            str(root),
            "--plan",
            "docs_bilingual/implementation_plans/example_plan.md",
            "--session-id",
            "helper-session",
            "--branch",
            "feature/helper",
            "--worktree",
            str(root),
            "--expires-hours",
            "1",
        ]
        claimed = subprocess.run(claim_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(claimed.returncode, 0, claimed.stdout + claimed.stderr)
        claim_payload = json.loads(claimed.stdout)
        self.assertTrue(claim_payload["ok"])

        release_cmd = [
            sys.executable,
            str(HELPER_PATH),
            "release",
            "--root",
            str(root),
            "--session-id",
            "helper-session",
        ]
        released = subprocess.run(release_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        release_payload = json.loads(released.stdout)
        self.assertTrue(release_payload["ok"])

        payload = claim_lock.evaluate(root)
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 0)
        self.assertEqual(payload["counts"]["released_or_inactive_claims"], 1)


class PortableNoBackendParallelSessionTest(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        plan_dir = root / "docs_bilingual" / "implementation_plans"
        plan_dir.mkdir(parents=True)
        for name in ("alpha_plan", "beta_plan"):
            (plan_dir / f"{name}.md").write_text(
                "---\n"
                f"doc_id: {name}\n"
                "lang: en\n"
                "status: active\n"
                "doc_class: implementation_plan\n"
                f"zh_cn_path: docs_bilingual/implementation_plans/{name}.zh-CN.md\n"
                "---\n"
                f"# {name}\n",
                encoding="utf-8",
            )
            (plan_dir / f"{name}.zh-CN.md").write_text(
                "---\n"
                f"doc_id: {name}\n"
                "lang: zh-CN\n"
                "status: active\n"
                "doc_class: implementation_plan\n"
                f"translation_of: docs_bilingual/implementation_plans/{name}.md\n"
                "---\n"
                f"# {name} zh\n",
                encoding="utf-8",
            )
        return root

    def run_helper(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HELPER_PATH), *args, "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def start_session(
        self,
        root: Path,
        *,
        session_id: str,
        plan: str = "docs_bilingual/implementation_plans/alpha_plan.md",
        rob_entry_id: str = "rob-alpha",
    ) -> dict:
        result = self.run_helper(
            root,
            "start",
            "--plan",
            plan,
            "--session-id",
            session_id,
            "--branch",
            f"feature/{session_id}",
            "--worktree",
            str(root),
            "--task-name",
            f"Task {session_id}",
            "--task-summary",
            "Portable no-backend session test task.",
            "--path",
            "tools/example.py",
            "--rob-entry-id",
            rob_entry_id,
            "--base-main",
            "base123",
            "--implementation-confirmed-by-user",
            "--implementation-confirmation-recorded-at",
            "2026-05-30T00:00:00+00:00",
            "--governance-package-commit",
            "governance123",
            "--governance-package-merged-to-local-main",
            "--hotspot",
            "claim-lock-helper",
            "--dependency",
            "complete_local_commit_flow_scheduler_reorder_buffer_plan",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload)
        return payload

    def test_start_creates_claim_receipt_and_predicted_rob_entry(self) -> None:
        root = self.make_root()

        payload = self.start_session(root, session_id="session-alpha")

        claim = json.loads(Path(payload["claim_path"]).read_text(encoding="utf-8"))
        receipt = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
        rob_entry = json.loads(Path(payload["rob_entry_path"]).read_text(encoding="utf-8"))

        self.assertEqual(claim["status"], "active")
        self.assertEqual(claim["implementation_plan_doc_id"], "alpha_plan")
        self.assertIn("docs_bilingual/implementation_plans/alpha_plan.md", claim["paths"])
        self.assertIs(claim["requires_user_confirmation_before_implementation"], True)
        self.assertIs(claim["implementation_confirmed_by_user"], True)
        self.assertEqual(claim["implementation_stage"], "implementation")
        self.assertEqual(claim["governance_package_commit"], "governance123")
        self.assertIs(claim["governance_package_merged_to_local_main"], True)
        self.assertEqual(receipt["lifecycle_status"], "active")
        self.assertIs(receipt["implementation_confirmed_by_user"], True)
        self.assertEqual(receipt["implementation_confirmation_recorded_at"], "2026-05-30T00:00:00+00:00")
        self.assertEqual(receipt["rob_entry_id"], "rob-alpha")
        self.assertEqual(rob_entry["state"], "predicted")
        self.assertEqual(rob_entry["base_main"], "base123")
        self.assertIn("tools/example.py", rob_entry["predicted_write_set"])
        self.assertIn("claim-lock-helper", rob_entry["hotspots"])

    def test_same_plan_conflicts_but_different_child_plans_can_run_parallel(self) -> None:
        root = self.make_root()
        self.start_session(root, session_id="session-alpha", rob_entry_id="rob-alpha")

        denied = self.run_helper(
            root,
            "start",
            "--plan",
            "docs_bilingual/implementation_plans/alpha_plan.md",
            "--session-id",
            "session-alpha-2",
            "--branch",
            "feature/session-alpha-2",
            "--worktree",
            str(root),
            "--task-name",
            "Duplicate",
            "--task-summary",
            "Duplicate plan should fail.",
            "--path",
            "tools/duplicate.py",
            "--rob-entry-id",
            "rob-alpha-2",
        )
        self.assertNotEqual(denied.returncode, 0)
        denied_payload = json.loads(denied.stdout)
        self.assertFalse(denied_payload["ok"])
        self.assertIn("multiple active session claims", json.dumps(denied_payload, ensure_ascii=False))

        self.start_session(
            root,
            session_id="session-beta",
            plan="docs_bilingual/implementation_plans/beta_plan.md",
            rob_entry_id="rob-beta",
        )

        check = subprocess.run(
            [sys.executable, str(CHECK_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        check_payload = json.loads(check.stdout)
        self.assertEqual(check_payload["counts"]["active_claims"], 2)

        status = self.run_helper(root, "status", "--session-id", "session-beta")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        status_payload = json.loads(status.stdout)
        self.assertTrue(status_payload["ok"], status_payload)
        self.assertEqual(status_payload["claim"]["session_id"], "session-beta")
        self.assertEqual(status_payload["rob_entry"]["state"], "predicted")

    def test_release_marks_claim_receipt_and_rob_without_deleting_worktree(self) -> None:
        root = self.make_root()
        payload = self.start_session(root, session_id="session-alpha")
        sentinel = root / "worktree-contents-are-not-deleted.txt"
        sentinel.write_text("keep me\n", encoding="utf-8")

        released = self.run_helper(
            root,
            "release",
            "--session-id",
            "session-alpha",
            "--receipt-lifecycle-status",
            "superseded",
            "--flush-rob",
            "--reason",
            "operator-paused",
        )
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        release_payload = json.loads(released.stdout)
        self.assertTrue(release_payload["ok"], release_payload)

        self.assertTrue(sentinel.exists(), "release must not delete worktree contents")
        claim = json.loads(Path(payload["claim_path"]).read_text(encoding="utf-8"))
        receipt = json.loads(Path(payload["receipt_path"]).read_text(encoding="utf-8"))
        rob_entry = json.loads(Path(payload["rob_entry_path"]).read_text(encoding="utf-8"))
        self.assertEqual(claim["status"], "released")
        self.assertEqual(receipt["lifecycle_status"], "superseded")
        self.assertIn("No files were deleted", receipt["next_action"])
        self.assertEqual(rob_entry["state"], "flushed")
        self.assertEqual(rob_entry["flush_reason"], "operator-paused")


if __name__ == "__main__":
    unittest.main()
