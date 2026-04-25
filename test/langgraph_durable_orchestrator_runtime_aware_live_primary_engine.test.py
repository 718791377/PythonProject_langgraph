import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorRuntimeAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_runtime_engine_tracks_context_and_store_from_run(self) -> None:
        repo_root = self.make_repo_root("runtime-engine-run")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "runtime engine task",
            "--phase",
            "read-context",
            "--context-schema",
            "operator_context",
            "--runtime-context-json",
            '{"user_id":"u-1","model_provider":"openai","db_dependency":"sqlite"}',
            "--store-configured",
            "--store-access-expected",
            "--store-kind",
            "repo_local",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "runtime-engine", "--thread-id", thread_id)
        projection = engine_payload["runtime_aware_live_primary_engine_projection"]

        self.assertEqual(projection["runtime_state_kind"], "runtime_context_and_store_ready")
        self.assertEqual(projection["context_schema"], "operator_context")
        self.assertTrue(projection["runtime_context_present"])
        self.assertEqual(projection["runtime_context_keys"], ["db_dependency", "model_provider", "user_id"])
        self.assertTrue(projection["store_configured"])
        self.assertTrue(projection["store_access_expected"])
        self.assertEqual(projection["store_kind"], "repo_local")
        self.assertIn("context_schema:operator_context", projection["runtime_transition_log"])

    def test_runtime_engine_tracks_runtime_command_updates(self) -> None:
        repo_root = self.make_repo_root("runtime-engine-command")
        run_payload = self.invoke(repo_root, "run", "--task", "runtime command task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump({"session_id": "sess-1", "cache_dependency": "redis"}, handle)
            temp_path = Path(handle.name)
        self.addCleanup(lambda: temp_path.unlink(missing_ok=True))

        self.invoke(
            repo_root,
            "runtime",
            "--thread-id",
            thread_id,
            "--context-schema",
            "session_context",
            "--runtime-context-file",
            str(temp_path),
            "--store-configured",
            "--store-access-expected",
            "--store-kind",
            "shared_store",
        )

        engine_payload = self.invoke(repo_root, "runtime-engine", "--thread-id", thread_id)
        projection = engine_payload["runtime_aware_live_primary_engine_projection"]

        self.assertEqual(projection["runtime_state_kind"], "runtime_context_and_store_ready")
        self.assertEqual(projection["context_schema"], "session_context")
        self.assertEqual(projection["runtime_context_keys"], ["cache_dependency", "session_id"])
        self.assertEqual(projection["store_kind"], "shared_store")
        self.assertIn("store:shared_store", projection["runtime_transition_log"])

    def test_inspect_exposes_runtime_engine_contract_and_projection(self) -> None:
        repo_root = self.make_repo_root("runtime-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "runtime inspect task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["runtime_aware_live_primary_engine_projection"]

        self.assertIn(
            "store_kind",
            inspect_payload["contract"]["runtime_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["runtime_state_kind"], "ordinary")
        self.assertEqual(projection["context_schema"], "")
        self.assertFalse(projection["runtime_context_present"])
        self.assertEqual(projection["helper_pointer"]["command"], "runtime-engine")


if __name__ == "__main__":
    unittest.main()
