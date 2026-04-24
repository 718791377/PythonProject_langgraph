import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorApprovalAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_approval_engine_tracks_pending_queue_state(self) -> None:
        repo_root = self.make_repo_root("approval-engine-pending")
        run_payload = self.invoke(repo_root, "run", "--task", "approval engine task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        queue_payload = self.invoke(
            repo_root,
            "approval-queue",
            "--thread-id",
            thread_id,
            "--interrupt-item-json",
            '{"interrupt_point":"freeze-plan","value_summary":"review_plan","reason":"approve_plan"}',
        )
        self.assertTrue(queue_payload["interrupt"])

        engine_payload = self.invoke(repo_root, "approval-engine", "--thread-id", thread_id)
        projection = engine_payload["approval_aware_live_primary_engine_projection"]

        self.assertEqual(projection["queue_posture"], "pending")
        self.assertEqual(projection["pending_count"], 1)
        self.assertEqual(projection["resume_state_kind"], "awaiting_manual_approval")
        self.assertEqual(projection["stop_boundary"], "interrupt_boundary")
        self.assertEqual(projection["current_execution_node"], "approval_wait")

    def test_approval_engine_tracks_partially_resolved_queue_state(self) -> None:
        repo_root = self.make_repo_root("approval-engine-partial")
        run_payload = self.invoke(repo_root, "run", "--task", "approval partial task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        queue_payload = self.invoke(
            repo_root,
            "approval-queue",
            "--thread-id",
            thread_id,
            "--interrupt-item-json",
            '{"interrupt_point":"freeze-plan","value_summary":"review_plan","reason":"approve_plan"}',
            "--interrupt-item-json",
            '{"interrupt_point":"freeze-plan","value_summary":"review_budget","reason":"approve_budget"}',
        )
        pending_ids = queue_payload["approval_queue_projection"]["pending_interrupt_ids"]

        partial_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--resume-map-json",
            json.dumps({pending_ids[0]: {"approved": True}}),
        )
        self.assertEqual(partial_payload["approval_queue_projection"]["queue_posture"], "partially_resolved")

        engine_payload = self.invoke(repo_root, "approval-engine", "--thread-id", thread_id)
        projection = engine_payload["approval_aware_live_primary_engine_projection"]

        self.assertEqual(projection["queue_posture"], "partially_resolved")
        self.assertEqual(projection["pending_count"], 1)
        self.assertEqual(projection["resolved_count"], 1)
        self.assertEqual(projection["resume_state_kind"], "awaiting_manual_approval")
        self.assertEqual(len(projection["resume_map_keys"]), 1)

    def test_approval_engine_tracks_resolved_queue_resume_state(self) -> None:
        repo_root = self.make_repo_root("approval-engine-resolved")
        run_payload = self.invoke(repo_root, "run", "--task", "approval resolved task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        queue_payload = self.invoke(
            repo_root,
            "approval-queue",
            "--thread-id",
            thread_id,
            "--interrupt-item-json",
            '{"interrupt_point":"freeze-plan","value_summary":"review_plan","reason":"approve_plan"}',
        )
        pending_id = queue_payload["approval_queue_projection"]["pending_interrupt_ids"][0]

        self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--resume-map-json",
            json.dumps({pending_id: {"approved": True}}),
        )

        engine_payload = self.invoke(repo_root, "approval-engine", "--thread-id", thread_id)
        projection = engine_payload["approval_aware_live_primary_engine_projection"]

        self.assertEqual(projection["queue_posture"], "resolved")
        self.assertEqual(projection["pending_count"], 0)
        self.assertEqual(projection["resolved_count"], 1)
        self.assertEqual(projection["resume_state_kind"], "resolved_queue_retained")
        self.assertIn(pending_id, projection["resume_map_keys"])


if __name__ == "__main__":
    unittest.main()
