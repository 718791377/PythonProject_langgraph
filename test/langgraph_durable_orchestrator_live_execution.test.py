import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorLiveExecutionTest(unittest.TestCase):
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

    def test_live_execution_projection_tracks_current_node(self) -> None:
        repo_root = self.make_repo_root("live-execution")
        run_payload = self.invoke(repo_root, "run", "--task", "live execution task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        execution_payload = self.invoke(repo_root, "live-execution", "--thread-id", thread_id)

        self.assertEqual(
            execution_payload["live_execution_identity"]["compiler_surface"],
            "StateGraph.compile",
        )
        self.assertEqual(
            execution_payload["live_execution_projection"]["current_execution_node"],
            "execute_parallel",
        )
        self.assertEqual(
            execution_payload["live_execution_projection"]["mapped_phase"],
            "execute-parallel",
        )
        self.assertIn(
            execution_payload["live_execution_projection"]["execution_posture"],
            {"unavailable", "ready", "executed"},
        )

    def test_live_execution_command_records_run_kind_and_status(self) -> None:
        repo_root = self.make_repo_root("live-execution-kind")
        run_payload = self.invoke(repo_root, "run", "--task", "live execution kind task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        execution_payload = self.invoke(
            repo_root,
            "live-execution",
            "--thread-id",
            thread_id,
            "--run-kind",
            "invoke",
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(execution_payload["live_execution_projection"]["last_run_kind"], "invoke")
        self.assertIn(
            execution_payload["live_execution_projection"]["last_run_status"],
            {"ok", "unavailable", "blocked", "noop", "error"},
        )
        self.assertIn("live_execution_projection_fields", inspect_payload["contract"])


if __name__ == "__main__":
    unittest.main()
