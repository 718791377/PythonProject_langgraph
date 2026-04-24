import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorCompiledInvocationTest(unittest.TestCase):
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

    def test_invocation_projection_tracks_current_execution_node(self) -> None:
        repo_root = self.make_repo_root("compiled-invocation")
        run_payload = self.invoke(repo_root, "run", "--task", "compiled invocation task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        invocation_payload = self.invoke(repo_root, "invocation", "--thread-id", thread_id)

        self.assertEqual(
            invocation_payload["compiled_invocation_identity"]["compiler_surface"],
            "StateGraph.compile",
        )
        self.assertEqual(
            invocation_payload["compiled_invocation_projection"]["current_execution_node"],
            "execute_parallel",
        )
        self.assertEqual(
            invocation_payload["compiled_invocation_projection"]["mapped_phase"],
            "execute-parallel",
        )
        self.assertTrue(
            isinstance(invocation_payload["compiled_invocation_projection"]["compile_supported"], bool)
        )

    def test_invocation_command_records_requested_invoke_kind(self) -> None:
        repo_root = self.make_repo_root("compiled-invocation-kind")
        run_payload = self.invoke(repo_root, "run", "--task", "compiled invocation kind task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        invocation_payload = self.invoke(
            repo_root,
            "invocation",
            "--thread-id",
            thread_id,
            "--invoke-kind",
            "invoke",
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(invocation_payload["compiled_invocation_projection"]["last_invoke_kind"], "invoke")
        self.assertEqual(
            inspect_payload["compiled_invocation_projection"]["last_invoke_reason"],
            "requested:invoke",
        )
        self.assertIn(
            "compiled_invocation_projection_fields",
            inspect_payload["contract"],
        )


if __name__ == "__main__":
    unittest.main()
