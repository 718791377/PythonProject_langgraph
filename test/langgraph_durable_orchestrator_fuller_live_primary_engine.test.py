import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorFullerLivePrimaryEngineTest(unittest.TestCase):
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

    def test_fuller_engine_projection_tracks_sequential_phase_progression(self) -> None:
        repo_root = self.make_repo_root("fuller-engine-sequential")
        run_payload = self.invoke(repo_root, "run", "--task", "fuller engine task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(
            repo_root,
            "fuller-engine",
            "--thread-id",
            thread_id,
            "--run-kind",
            "invoke",
        )

        self.assertEqual(
            engine_payload["fuller_live_primary_engine_identity"]["graph_api_surface"],
            "StateGraph",
        )
        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["current_execution_node"],
            "execute_parallel",
        )
        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["resulting_phase"],
            "integrate-converge",
        )
        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["phase_transition_kind"],
            "sequential",
        )
        self.assertIn(
            "integrate_converge",
            engine_payload["fuller_live_primary_engine_projection"]["execution_node_path"],
        )
        self.assertIn(
            engine_payload["fuller_live_primary_engine_projection"]["last_run_status"],
            {"ok", "unavailable"},
        )

    def test_fuller_engine_projection_tracks_command_target_phase(self) -> None:
        repo_root = self.make_repo_root("fuller-engine-command")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "fuller engine command task",
            "--phase",
            "execute-parallel",
            "--command-kind",
            "goto",
            "--command-goto",
            "stabilize",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "fuller-engine", "--thread-id", thread_id)

        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["resulting_phase"],
            "stabilize",
        )
        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["phase_transition_kind"],
            "command",
        )

    def test_fuller_engine_projection_tracks_interrupt_wait(self) -> None:
        repo_root = self.make_repo_root("fuller-engine-wait")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "fuller engine wait task",
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

        engine_payload = self.invoke(repo_root, "fuller-engine", "--thread-id", thread_id)

        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["execution_posture"],
            "interrupt_wait",
        )
        self.assertEqual(
            engine_payload["fuller_live_primary_engine_projection"]["phase_transition_kind"],
            "interrupt",
        )


if __name__ == "__main__":
    unittest.main()
