import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorAutomaticRuntimePoliciesTest(unittest.TestCase):
    maxDiff = None

    def make_repo_root(self, name: str) -> Path:
        repo_root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        repo_root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(repo_root, ignore_errors=True))
        return repo_root

    def invoke(self, repo_root: Path, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), *args, "--repo-root", str(repo_root)],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return json.loads(result.stdout)

    def test_auto_policy_projection_tracks_safe_migration_continue(self) -> None:
        repo_root = self.make_repo_root("auto-policy-safe")
        run_payload = self.invoke(repo_root, "run", "--task", "auto policy safe task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        policy_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id)

        self.assertEqual(
            policy_payload["automatic_runtime_policy_projection"]["migration_policy_posture"],
            "auto_continue_safe",
        )
        self.assertIn(
            "continue_on_migration_safe",
            policy_payload["automatic_runtime_policy_projection"]["automatic_actions_available"],
        )

    def test_auto_policy_projection_tracks_degraded_continue_with_notice(self) -> None:
        repo_root = self.make_repo_root("auto-policy-degraded")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "auto policy degraded task",
            "--phase",
            "freeze-plan",
            "--thread-topology-version",
            "1.1",
        )
        thread_id = run_payload["thread_id"]

        policy_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id)

        self.assertEqual(
            policy_payload["automatic_runtime_policy_projection"]["migration_policy_posture"],
            "auto_continue_with_notice",
        )
        self.assertIn(
            "continue_on_degraded_compatible",
            policy_payload["automatic_runtime_policy_projection"]["automatic_actions_available"],
        )

    def test_auto_policy_apply_resumes_after_resolved_queue(self) -> None:
        repo_root = self.make_repo_root("auto-policy-apply")
        run_payload = self.invoke(repo_root, "run", "--task", "auto policy apply task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        queue_payload = self.invoke(
            repo_root,
            "approval-queue",
            "--thread-id",
            thread_id,
            "--interrupt-item-json",
            '{"interrupt_point":"freeze-plan","value_summary":"review_plan","reason":"approve_plan"}',
        )
        pending_interrupt_id = queue_payload["approval_queue_projection"]["pending_interrupt_ids"][0]
        self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--resume-map-json",
            json.dumps({pending_interrupt_id: {"approved": True}}),
        )
        self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "status=waiting_for_approval",
            "--thread-field",
            "stop_reason=needs_human",
        )

        status_payload = self.invoke(repo_root, "status", "--thread-id", thread_id)
        resolved_ids = status_payload["approval_queue_projection"]["resolved_interrupt_ids"]
        self.assertTrue(resolved_ids)

        applied_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id, "--apply")

        self.assertEqual(applied_payload["thread"]["status"], "resumed")
        self.assertEqual(applied_payload["thread"]["stop_reason"], "")
        self.assertEqual(
            applied_payload["automatic_runtime_policy_projection"]["last_auto_action"],
            "continue_on_migration_safe,resume_after_resolved_queue,continue_after_safe_recovery",
        )

    def test_auto_policy_apply_continues_after_safe_recovery(self) -> None:
        repo_root = self.make_repo_root("auto-policy-recovery")
        run_payload = self.invoke(repo_root, "run", "--task", "auto policy recovery task", "--phase", "read-context")
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "phase=execute-parallel",
        )
        preview_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id)
        applied_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id, "--apply")

        self.assertEqual(
            preview_payload["automatic_runtime_policy_projection"]["recovery_policy_posture"],
            "auto_continue_safe",
        )
        self.assertEqual(applied_payload["thread"]["status"], "resumed")
        self.assertIn(
            "continue_after_safe_recovery",
            applied_payload["automatic_runtime_policy_projection"]["last_auto_action"],
        )

    def test_auto_policy_apply_clears_stale_interrupt(self) -> None:
        repo_root = self.make_repo_root("auto-policy-stale-interrupt")
        run_payload = self.invoke(repo_root, "run", "--task", "auto policy stale interrupt task", "--phase", "read-context")
        thread_id = run_payload["thread_id"]

        # Recover with an interrupt payload while leaving the queue empty to simulate a stale interrupt record.
        recovery_payload = self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--interrupt-field",
            "interrupt_point=freeze-plan",
            "--interrupt-field",
            "status=waiting_for_approval",
        )
        self.assertTrue(recovery_payload["interrupt"])

        status_payload = self.invoke(repo_root, "status", "--thread-id", thread_id)
        self.assertTrue(status_payload["interrupt"])

        applied_payload = self.invoke(repo_root, "auto-policy", "--thread-id", thread_id, "--apply")

        self.assertEqual(applied_payload["interrupt"], {})
        self.assertEqual(
            applied_payload["automatic_runtime_policy_projection"]["approval_policy_posture"],
            "auto_clear_stale_interrupt",
        )
        self.assertIn(
            "clear_stale_interrupt",
            applied_payload["automatic_runtime_policy_projection"]["last_auto_action"],
        )


if __name__ == "__main__":
    unittest.main()
