import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorStreamingTest(unittest.TestCase):
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

    def test_stream_command_persists_selected_modes_and_nested_subgraphs(self) -> None:
        repo_root = self.make_repo_root("stream-modes")
        run_payload = self.invoke(repo_root, "run", "--task", "stream task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        stream_payload = self.invoke(
            repo_root,
            "stream",
            "--thread-id",
            thread_id,
            "--stream-mode",
            "updates",
            "--stream-mode",
            "debug",
            "--subgraphs",
            "--event-kind",
            "debug",
            "--namespace",
            "execution",
            "--namespace",
            "verify",
            "--debug-summary",
            "entered verify branch",
        )

        self.assertEqual(stream_payload["stream_projection"]["selected_modes"], ["debug", "updates"])
        self.assertTrue(stream_payload["stream_projection"]["subgraphs"])
        self.assertEqual(stream_payload["stream_projection"]["latest_event_kind"], "debug")
        self.assertEqual(stream_payload["stream_projection"]["latest_namespace"], ["execution", "verify"])
        self.assertEqual(stream_payload["stream_projection"]["latest_debug_summary"], "entered verify branch")
        self.assertEqual(stream_payload["stream_projection"]["event_count"], 1)

    def test_stream_projection_tracks_checkpoint_and_task_signals(self) -> None:
        repo_root = self.make_repo_root("stream-events")
        run_payload = self.invoke(repo_root, "run", "--task", "stream event task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "stream",
            "--thread-id",
            thread_id,
            "--stream-mode",
            "checkpoints",
            "--stream-mode",
            "tasks",
            "--event-kind",
            "tasks",
            "--checkpoint-kind",
            "fanin_merge",
            "--task-path",
            "execution.verify.node",
            "--task-status",
            "running",
        )

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["stream_projection"]["selected_modes"], ["checkpoints", "tasks"])
        self.assertEqual(inspect_payload["stream_projection"]["latest_event_kind"], "tasks")
        self.assertEqual(inspect_payload["stream_projection"]["latest_checkpoint_kind"], "fanin_merge")
        self.assertEqual(inspect_payload["stream_projection"]["latest_task_path"], "execution.verify.node")
        self.assertEqual(inspect_payload["stream_projection"]["latest_task_status"], "running")
        self.assertEqual(inspect_payload["stream_projection"]["helper_pointer"]["command"], "stream")


if __name__ == "__main__":
    unittest.main()
