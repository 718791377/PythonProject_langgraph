import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorHandoffStateLivePrimaryEngineTest(unittest.TestCase):
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

    def test_handoff_engine_tracks_subgraph_transition_on_command_goto(self) -> None:
        repo_root = self.make_repo_root("handoff-engine-command-goto")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "handoff engine command goto task",
            "--phase",
            "read-context",
            "--command-kind",
            "update_goto",
            "--command-goto",
            "execute-parallel",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "handoff-engine", "--thread-id", thread_id)
        projection = engine_payload["handoff_state_live_primary_engine_projection"]

        self.assertEqual(projection["handoff_state_kind"], "subgraph_transition")
        self.assertEqual(projection["source_subgraph"], "research")
        self.assertEqual(projection["target_subgraph"], "execution")
        self.assertEqual(projection["graph_scope"], "current")
        self.assertEqual(projection["stop_boundary"], "command_boundary")
        self.assertEqual(projection["handoff_subgraph_path"], ["research", "execution"])

    def test_handoff_engine_tracks_parent_handoff_state(self) -> None:
        repo_root = self.make_repo_root("handoff-engine-parent-handoff")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "handoff engine parent handoff task",
            "--phase",
            "execute-parallel",
            "--command-kind",
            "parent_handoff",
            "--command-graph-scope",
            "parent",
            "--parent-handoff-target",
            "verify-accept",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "handoff-engine", "--thread-id", thread_id)
        projection = engine_payload["handoff_state_live_primary_engine_projection"]

        self.assertEqual(projection["handoff_state_kind"], "parent_handoff")
        self.assertEqual(projection["source_subgraph"], "execution")
        self.assertEqual(projection["target_subgraph"], "verification")
        self.assertEqual(projection["parent_handoff_target"], "verify-accept")
        self.assertEqual(projection["graph_scope"], "parent")
        self.assertEqual(projection["stop_boundary"], "command_boundary")

    def test_handoff_engine_tracks_sequential_cross_subgraph_progression(self) -> None:
        repo_root = self.make_repo_root("handoff-engine-sequential")
        run_payload = self.invoke(repo_root, "run", "--task", "handoff engine sequential task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "handoff-engine", "--thread-id", thread_id, "--run-kind", "invoke")
        projection = engine_payload["handoff_state_live_primary_engine_projection"]

        self.assertIn("research", projection["handoff_subgraph_path"])
        self.assertIn("planning", projection["handoff_subgraph_path"])
        self.assertIn("verification", projection["handoff_subgraph_path"])
        self.assertEqual(projection["current_execution_node"], "verify_accept")
        self.assertEqual(projection["stop_boundary"], "phase_boundary")


if __name__ == "__main__":
    unittest.main()
