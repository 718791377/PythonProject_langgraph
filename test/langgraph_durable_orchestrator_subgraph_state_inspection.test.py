import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorSubgraphStateInspectionTest(unittest.TestCase):
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

    def test_research_subgraph_tracks_per_thread_stateful_posture(self) -> None:
        repo_root = self.make_repo_root("subgraph-state-research")
        run_payload = self.invoke(repo_root, "run", "--task", "research subgraph task", "--phase", "read-context")
        thread_id = run_payload["thread_id"]

        inspection_payload = self.invoke(repo_root, "subgraph-state", "--thread-id", thread_id)

        self.assertEqual(
            inspection_payload["subgraph_state_inspection_projection"]["active_subgraph"],
            "research",
        )
        self.assertEqual(
            inspection_payload["subgraph_state_inspection_projection"]["persistence_mode"],
            "per_thread",
        )
        self.assertEqual(
            inspection_payload["subgraph_state_inspection_projection"]["checkpointer_mode"],
            "separate_subgraph",
        )
        self.assertTrue(
            inspection_payload["subgraph_state_inspection_projection"]["state_inspection_available"]
        )
        self.assertFalse(
            inspection_payload["subgraph_state_inspection_projection"][
                "same_subgraph_parallel_calls_supported"
            ]
        )

    def test_planning_subgraph_tracks_per_invocation_inherited_checkpoint_posture(self) -> None:
        repo_root = self.make_repo_root("subgraph-state-planning")
        run_payload = self.invoke(repo_root, "run", "--task", "planning subgraph task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(
            inspect_payload["subgraph_state_inspection_projection"]["active_subgraph"],
            "planning",
        )
        self.assertEqual(
            inspect_payload["subgraph_state_inspection_projection"]["persistence_mode"],
            "per_invocation",
        )
        self.assertTrue(
            inspect_payload["subgraph_state_inspection_projection"]["inherits_parent_checkpointer"]
        )
        self.assertEqual(
            inspect_payload["subgraph_state_inspection_projection"]["state_inspection_scope"],
            "current_invocation",
        )
        self.assertIn(
            "subgraph_state_inspection_projection_fields",
            inspect_payload["contract"],
        )

    def test_verification_subgraph_tracks_stateless_uninspectable_posture(self) -> None:
        repo_root = self.make_repo_root("subgraph-state-verification")
        run_payload = self.invoke(repo_root, "run", "--task", "verification subgraph task", "--phase", "verify-accept")
        thread_id = run_payload["thread_id"]

        state_payload = self.invoke(repo_root, "subgraph-state", "--thread-id", thread_id)

        self.assertEqual(
            state_payload["subgraph_state_inspection_projection"]["active_subgraph"],
            "verification",
        )
        self.assertEqual(
            state_payload["subgraph_state_inspection_projection"]["persistence_mode"],
            "stateless",
        )
        self.assertFalse(
            state_payload["subgraph_state_inspection_projection"]["state_inspection_available"]
        )
        self.assertIn(
            "stateless_subgraph",
            state_payload["subgraph_state_inspection_projection"]["inspection_blockers"],
        )
        self.assertEqual(
            state_payload["subgraph_state_inspection_projection"]["helper_pointer"]["command"],
            "subgraph-state",
        )


if __name__ == "__main__":
    unittest.main()
