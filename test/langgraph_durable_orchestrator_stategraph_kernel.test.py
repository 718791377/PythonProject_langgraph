import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorStateGraphKernelTest(unittest.TestCase):
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

    def test_kernel_projection_tracks_phase_mapped_node(self) -> None:
        repo_root = self.make_repo_root("kernel-phase")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "kernel task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]
        kernel_payload = self.invoke(repo_root, "kernel", "--thread-id", thread_id)

        self.assertEqual(kernel_payload["graph_kernel_identity"]["graph_api_surface"], "StateGraph")
        self.assertEqual(kernel_payload["graph_kernel_projection"]["current_node_id"], "execute_parallel")
        self.assertEqual(kernel_payload["graph_kernel_projection"]["mapped_phase"], "execute-parallel")
        self.assertEqual(kernel_payload["graph_kernel_projection"]["node_posture"], "phase_active")
        self.assertIn("integrate_converge", kernel_payload["graph_kernel_projection"]["available_next_nodes"])
        self.assertIn("approval_wait", kernel_payload["graph_kernel_projection"]["available_next_nodes"])

    def test_kernel_projection_tracks_approval_wait_and_recovery_nodes(self) -> None:
        repo_root = self.make_repo_root("kernel-special")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "kernel wait task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]

        waiting_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--gate-verdict",
            "needs_human",
            "--gate-reason",
            "manual_approval_required",
        )
        self.assertEqual(waiting_payload["graph_kernel_projection"]["current_node_id"], "approval_wait")
        self.assertEqual(waiting_payload["graph_kernel_projection"]["node_posture"], "approval_wait")

        recovered_payload = self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "phase=stabilize",
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(recovered_payload["graph_kernel_projection"]["current_node_id"], "recovery_pending_resume")
        self.assertEqual(recovered_payload["graph_kernel_projection"]["node_posture"], "recovery_pending_resume")
        self.assertIn("graph_kernel_projection_fields", inspect_payload["contract"])
        self.assertIn("current_node_id", inspect_payload["contract"]["graph_kernel_projection_fields"])


if __name__ == "__main__":
    unittest.main()
