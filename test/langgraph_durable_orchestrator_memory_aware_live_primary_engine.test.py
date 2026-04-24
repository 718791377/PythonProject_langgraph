import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorMemoryAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_memory_engine_tracks_memory_and_semantic_state_from_run(self) -> None:
        repo_root = self.make_repo_root("memory-engine-run")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "memory engine task",
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

        engine_payload = self.invoke(repo_root, "memory-engine", "--thread-id", thread_id)
        projection = engine_payload["memory_aware_live_primary_engine_projection"]

        self.assertEqual(projection["memory_state_kind"], "memory_and_semantic_ready")
        self.assertTrue(projection["memory_store_configured"])
        self.assertEqual(projection["memory_store_kind"], "long_term_store")
        self.assertEqual(projection["memory_namespaces"], ["codex/team"])
        self.assertTrue(projection["semantic_memory_enabled"])
        self.assertEqual(projection["semantic_store_kind"], "semantic_index")
        self.assertEqual(projection["semantic_namespaces"], ["codex/team"])
        self.assertIn("memory_store:long_term_store", projection["memory_transition_log"])

    def test_memory_engine_tracks_memory_command_updates(self) -> None:
        repo_root = self.make_repo_root("memory-engine-command")
        run_payload = self.invoke(repo_root, "run", "--task", "memory command task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.invoke(
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

        engine_payload = self.invoke(repo_root, "memory-engine", "--thread-id", thread_id)
        projection = engine_payload["memory_aware_live_primary_engine_projection"]

        self.assertEqual(projection["memory_state_kind"], "memory_and_semantic_ready")
        self.assertEqual(projection["memory_store_kind"], "shared_memory_store")
        self.assertEqual(projection["memory_namespaces"], ["codex/bugs", "codex/team"])
        self.assertEqual(projection["semantic_store_kind"], "vector_store")
        self.assertEqual(projection["semantic_namespaces"], ["codex/team"])

    def test_inspect_exposes_memory_engine_contract_and_projection(self) -> None:
        repo_root = self.make_repo_root("memory-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "memory inspect task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["memory_aware_live_primary_engine_projection"]

        self.assertIn(
            "semantic_store_kind",
            inspect_payload["contract"]["memory_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["memory_state_kind"], "ordinary")
        self.assertFalse(projection["memory_store_configured"])
        self.assertFalse(projection["semantic_memory_enabled"])
        self.assertEqual(projection["helper_pointer"]["command"], "memory-engine")


if __name__ == "__main__":
    unittest.main()
