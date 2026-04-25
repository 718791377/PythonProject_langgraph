import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorGeneralizedLiveRoutingTest(unittest.TestCase):
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

    def test_generalized_routing_projection_tracks_execution_loop_route(self) -> None:
        repo_root = self.make_repo_root("generalized-routing-loop")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "generalized routing loop task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]

        routing_payload = self.invoke(repo_root, "generalized-routing", "--thread-id", thread_id)
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(
            routing_payload["generalized_live_routing_identity"]["graph_api_surface"],
            "StateGraph",
        )
        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["current_execution_node"],
            "execute_parallel",
        )
        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["mapped_phase"],
            "execute-parallel",
        )
        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["current_route"],
            "loop:execution",
        )
        self.assertIn(
            "loop:execution",
            routing_payload["generalized_live_routing_projection"]["candidate_routes"],
        )
        self.assertIn(
            "generalized_live_routing_projection_fields",
            inspect_payload["contract"],
        )

    def test_generalized_routing_projection_tracks_command_selected_route(self) -> None:
        repo_root = self.make_repo_root("generalized-routing-command")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "generalized routing command task",
            "--phase",
            "execute-parallel",
            "--command-kind",
            "goto",
            "--command-goto",
            "stabilize",
        )
        thread_id = run_payload["thread_id"]

        routing_payload = self.invoke(repo_root, "generalized-routing", "--thread-id", thread_id)

        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["current_route"],
            "command:goto",
        )
        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["selected_route"],
            "phase:stabilize",
        )

    def test_generalized_routing_projection_tracks_approval_wait(self) -> None:
        repo_root = self.make_repo_root("generalized-routing-approval")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "generalized routing approval task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--gate-verdict",
            "needs_human",
            "--gate-reason",
            "manual_approval_required",
        )
        routing_payload = self.invoke(repo_root, "generalized-routing", "--thread-id", thread_id)

        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["route_posture"],
            "interrupt_wait",
        )
        self.assertEqual(
            routing_payload["generalized_live_routing_projection"]["selected_route"],
            "approval_wait",
        )
        self.assertTrue(
            routing_payload["generalized_live_routing_projection"]["approval_route_pending"]
        )


if __name__ == "__main__":
    unittest.main()
