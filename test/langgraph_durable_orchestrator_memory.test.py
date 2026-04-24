import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorMemoryTest(unittest.TestCase):
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

    def test_run_persists_memory_store_and_semantic_memory_posture(self) -> None:
        repo_root = self.make_repo_root("memory-run")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "memory task",
            "--phase",
            "read-context",
            "--memory-store-configured",
            "--memory-store-kind",
            "long_term_store",
            "--memory-namespace",
            "codex/team",
            "--semantic-memory-enabled",
            "--semantic-store-kind",
            "semantic_index",
            "--semantic-namespace",
            "codex/team",
        )
        thread_id = run_payload["thread_id"]

        self.assertTrue(run_payload["memory_projection"]["memory_store_configured"])
        self.assertEqual(run_payload["memory_projection"]["memory_store_kind"], "long_term_store")
        self.assertEqual(run_payload["memory_projection"]["memory_namespaces"], ["codex/team"])
        self.assertTrue(run_payload["memory_projection"]["semantic_memory_enabled"])
        self.assertEqual(run_payload["memory_projection"]["semantic_store_kind"], "semantic_index")
        self.assertEqual(run_payload["memory_projection"]["semantic_namespaces"], ["codex/team"])

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["memory_projection"]["memory_store_kind"], "long_term_store")
        self.assertEqual(inspect_payload["memory_projection"]["helper_pointer"]["command"], "memory")

    def test_memory_command_updates_memory_and_semantic_posture(self) -> None:
        repo_root = self.make_repo_root("memory-command")
        run_payload = self.invoke(repo_root, "run", "--task", "memory command task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        memory_payload = self.invoke(
            repo_root,
            "memory",
            "--thread-id",
            thread_id,
            "--memory-store-configured",
            "--memory-store-kind",
            "shared_memory_store",
            "--memory-namespace",
            "codex/team",
            "--memory-namespace",
            "codex/bugs",
            "--semantic-memory-enabled",
            "--semantic-store-kind",
            "vector_store",
            "--semantic-namespace",
            "codex/team",
        )
        status_payload = self.invoke(repo_root, "status", "--thread-id", thread_id)

        self.assertEqual(memory_payload["memory_projection"]["memory_store_kind"], "shared_memory_store")
        self.assertEqual(
            memory_payload["memory_projection"]["memory_namespaces"],
            ["codex/bugs", "codex/team"],
        )
        self.assertEqual(memory_payload["memory_projection"]["semantic_store_kind"], "vector_store")
        self.assertTrue(status_payload["memory_projection"]["semantic_memory_enabled"])


if __name__ == "__main__":
    unittest.main()
