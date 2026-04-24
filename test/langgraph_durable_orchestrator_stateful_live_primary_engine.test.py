import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorStatefulLivePrimaryEngineTest(unittest.TestCase):
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

    def test_stateful_engine_projects_transition_log_to_verify_accept_boundary(self) -> None:
        repo_root = self.make_repo_root("stateful-engine-multistep")
        run_payload = self.invoke(repo_root, "run", "--task", "stateful engine task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(
            repo_root,
            "stateful-engine",
            "--thread-id",
            thread_id,
            "--run-kind",
            "invoke",
            "--recursion-limit",
            "8",
        )

        projection = engine_payload["stateful_live_primary_engine_projection"]
        self.assertEqual(projection["mapped_phase"], "verify-accept")
        self.assertEqual(projection["stateful_phase_path"][0], "define-target")
        self.assertEqual(projection["stateful_phase_path"][-1], "verify-accept")
        self.assertEqual(projection["stop_boundary"], "phase_boundary")
        self.assertIn("sequential:define-target->read-context", projection["stateful_transition_log"])

    def test_stateful_engine_honors_command_boundary_with_transition_log(self) -> None:
        repo_root = self.make_repo_root("stateful-engine-command")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "stateful engine command task",
            "--phase",
            "execute-parallel",
            "--command-kind",
            "goto",
            "--command-goto",
            "stabilize",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "stateful-engine", "--thread-id", thread_id)
        projection = engine_payload["stateful_live_primary_engine_projection"]

        self.assertEqual(projection["stop_boundary"], "command_boundary")
        self.assertEqual(projection["stateful_phase_path"], ["execute-parallel", "stabilize"])
        self.assertIn("command:goto->stabilize", projection["stateful_transition_log"])

    def test_stateful_engine_honors_recursion_limit_boundary(self) -> None:
        repo_root = self.make_repo_root("stateful-engine-recursion-limit")
        run_payload = self.invoke(repo_root, "run", "--task", "stateful recursion task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(
            repo_root,
            "stateful-engine",
            "--thread-id",
            thread_id,
            "--recursion-limit",
            "2",
        )
        projection = engine_payload["stateful_live_primary_engine_projection"]

        self.assertEqual(projection["stop_boundary"], "recursion_limit_boundary")
        self.assertEqual(projection["recursion_limit"], 2)
        self.assertEqual(projection["stateful_phase_path"], ["define-target", "read-context", "freeze-plan"])
        self.assertIn("boundary:recursion_limit:2", projection["stateful_transition_log"])


if __name__ == "__main__":
    unittest.main()
