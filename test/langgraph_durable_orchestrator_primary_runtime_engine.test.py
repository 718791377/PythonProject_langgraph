import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorPrimaryRuntimeEngineTest(unittest.TestCase):
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

    def test_engine_projection_tracks_phase_and_identity(self) -> None:
        repo_root = self.make_repo_root("engine-phase")
        run_payload = self.invoke(repo_root, "run", "--task", "engine task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "engine", "--thread-id", thread_id)

        self.assertEqual(
            engine_payload["primary_runtime_engine_identity"]["graph_api_surface"],
            "StateGraph",
        )
        self.assertEqual(
            engine_payload["primary_runtime_engine_projection"]["current_execution_node"],
            "execute_parallel",
        )
        self.assertEqual(
            engine_payload["primary_runtime_engine_projection"]["mapped_phase"],
            "execute-parallel",
        )
        self.assertIn(
            engine_payload["primary_runtime_engine_projection"]["execution_posture"],
            {"compiled_ready", "compiled_unavailable"},
        )
        self.assertTrue(
            isinstance(engine_payload["primary_runtime_engine_projection"]["compile_supported"], bool)
        )

    def test_engine_projection_tracks_interrupt_wait(self) -> None:
        repo_root = self.make_repo_root("engine-wait")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "engine wait task",
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
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(
            waiting_payload["primary_runtime_engine_projection"]["execution_posture"],
            "interrupt_wait",
        )
        self.assertEqual(
            waiting_payload["primary_runtime_engine_projection"]["current_execution_node"],
            "approval_wait",
        )
        self.assertIn(
            "primary_runtime_engine_projection_fields",
            inspect_payload["contract"],
        )
        self.assertIn(
            "current_execution_node",
            inspect_payload["contract"]["primary_runtime_engine_projection_fields"],
        )


if __name__ == "__main__":
    unittest.main()
