import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorMultiInterruptQueueTest(unittest.TestCase):
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

    def test_multi_interrupt_queue_tracks_pending_and_resolved_items(self) -> None:
        repo_root = self.make_repo_root("multi-interrupt")
        run_payload = self.invoke(repo_root, "run", "--task", "approval queue task", "--phase", "read-context")
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

        self.assertEqual(queue_payload["approval_queue_projection"]["queue_posture"], "pending")
        self.assertEqual(queue_payload["approval_queue_projection"]["queue_size"], 2)
        self.assertEqual(queue_payload["approval_queue_projection"]["pending_count"], 2)
        self.assertEqual(len(pending_ids), 2)
        self.assertEqual(queue_payload["interrupt"]["interrupt_id"], pending_ids[0])

        partial_resume_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--resume-map-json",
            json.dumps({pending_ids[0]: {"approved": True}}, ensure_ascii=True),
        )
        self.assertEqual(partial_resume_payload["approval_queue_projection"]["queue_posture"], "partially_resolved")
        self.assertEqual(partial_resume_payload["approval_queue_projection"]["pending_count"], 1)
        self.assertEqual(partial_resume_payload["approval_queue_projection"]["resolved_count"], 1)
        self.assertEqual(partial_resume_payload["thread"]["status"], "waiting_for_approval")
        self.assertEqual(
            partial_resume_payload["approval_queue_projection"]["current_interrupt_id"],
            pending_ids[1],
        )

        final_resume_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--resume-map-json",
            json.dumps({pending_ids[1]: "approved"}, ensure_ascii=True),
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(final_resume_payload["approval_queue_projection"]["queue_posture"], "resolved")
        self.assertEqual(final_resume_payload["approval_queue_projection"]["pending_count"], 0)
        self.assertEqual(final_resume_payload["approval_queue_projection"]["resolved_count"], 2)
        self.assertEqual(final_resume_payload["interrupt"], {})
        self.assertEqual(final_resume_payload["thread"]["status"], "resumed")
        self.assertEqual(
            inspect_payload["approval_queue_projection"]["resume_map_keys"],
            sorted(pending_ids),
        )
        self.assertEqual(
            inspect_payload["approval_queue_projection"]["helper_pointer"]["command"],
            "approval-queue",
        )

    def test_needs_human_gate_auto_seeds_single_item_queue(self) -> None:
        repo_root = self.make_repo_root("auto-queue")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "loop queue task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]

        approval_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--gate-verdict",
            "needs_human",
            "--gate-reason",
            "manual_approval_required",
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(approval_payload["approval_queue_projection"]["queue_posture"], "pending")
        self.assertEqual(approval_payload["approval_queue_projection"]["queue_size"], 1)
        self.assertEqual(approval_payload["approval_queue_projection"]["pending_count"], 1)
        self.assertEqual(approval_payload["interrupt"]["status"], "waiting_for_approval")
        self.assertEqual(
            approval_payload["interrupt"]["interrupt_id"],
            approval_payload["approval_queue_projection"]["current_interrupt_id"],
        )
        self.assertIn("approval_queue_projection_fields", inspect_payload["contract"])
        self.assertIn("queue_posture", inspect_payload["contract"]["approval_queue_projection_fields"])


if __name__ == "__main__":
    unittest.main()
