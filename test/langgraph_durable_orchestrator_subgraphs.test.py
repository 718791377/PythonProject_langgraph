import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorSubgraphsTest(unittest.TestCase):
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

    def test_run_persists_active_subgraph_posture(self) -> None:
        repo_root = self.make_repo_root("subgraph-run")
        run_payload = self.invoke(repo_root, "run", "--task", "subgraph task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.assertEqual(run_payload["subgraph_projection"]["active_subgraph"], "planning")
        self.assertEqual(run_payload["thread"]["active_subgraph"], "planning")
        self.assertEqual(run_payload["thread"]["active_subgraph_posture"]["default_phase"], "freeze-plan")
        self.assertEqual(
            run_payload["thread"]["active_subgraph_posture"]["input_artifacts"],
            ["frozen_implementation_brief"],
        )

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["subgraph_projection"]["active_subgraph"], "planning")
        self.assertEqual(
            inspect_payload["subgraph_projection"]["active_subgraph_posture"]["output_artifacts"],
            ["execution_slice_plan", "ownership_boundaries"],
        )
        self.assertEqual(
            inspect_payload["subgraph_projection"]["helper_pointer"]["command"],
            "subgraphs",
        )

    def test_subgraphs_command_exposes_library_and_resume_updates_active_subgraph(self) -> None:
        repo_root = self.make_repo_root("subgraph-command")
        run_payload = self.invoke(repo_root, "run", "--task", "subgraph command task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]
        self.invoke(repo_root, "resume", "--thread-id", thread_id, "--phase", "execute-parallel")

        subgraphs_payload = self.invoke(repo_root, "subgraphs", "--thread-id", thread_id)

        self.assertIn("fresh_context_boundary", subgraphs_payload["subgraph_library_fields"])
        self.assertEqual(subgraphs_payload["subgraph_library"]["execution"]["durable_worker_default"], "team-executor")
        self.assertTrue(subgraphs_payload["subgraph_library"]["verification"]["read_only_default"])
        self.assertEqual(subgraphs_payload["subgraph_projection"]["active_subgraph"], "execution")
        self.assertIn("adversarial-review", subgraphs_payload["subgraph_projection"]["available_subgraphs"])
        self.assertEqual(subgraphs_payload["helper_pointers"]["subgraphs"]["command"], "subgraphs")


if __name__ == "__main__":
    unittest.main()
