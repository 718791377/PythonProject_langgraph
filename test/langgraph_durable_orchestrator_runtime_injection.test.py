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


class LangGraphDurableOrchestratorRuntimeInjectionTest(unittest.TestCase):
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

    def test_run_persists_runtime_context_and_store_metadata(self) -> None:
        repo_root = self.make_repo_root("runtime-run")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "runtime task",
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

        self.assertEqual(run_payload["runtime_injection_projection"]["context_schema"], "operator_context")
        self.assertTrue(run_payload["runtime_injection_projection"]["runtime_context_present"])
        self.assertEqual(
            run_payload["runtime_injection_projection"]["runtime_context_keys"],
            ["db_dependency", "model_provider", "user_id"],
        )
        self.assertTrue(run_payload["runtime_injection_projection"]["store_configured"])
        self.assertTrue(run_payload["runtime_injection_projection"]["store_access_expected"])
        self.assertEqual(run_payload["runtime_injection_projection"]["store_kind"], "repo_local")

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["runtime_injection_projection"]["context_schema"], "operator_context")
        self.assertIn(
            "model_provider:model_scope",
            inspect_payload["runtime_injection_projection"]["runtime_context_kind_hints"],
        )
        self.assertEqual(inspect_payload["runtime_injection_projection"]["helper_pointer"]["command"], "runtime")

    def test_runtime_command_updates_runtime_injection_posture(self) -> None:
        repo_root = self.make_repo_root("runtime-command")
        run_payload = self.invoke(repo_root, "run", "--task", "runtime command task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump({"session_id": "sess-1", "cache_dependency": "redis"}, handle)
            temp_path = Path(handle.name)
        self.addCleanup(lambda: temp_path.unlink(missing_ok=True))

        runtime_payload = self.invoke(
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
        status_payload = self.invoke(repo_root, "status", "--thread-id", thread_id)

        self.assertEqual(runtime_payload["runtime_injection_projection"]["context_schema"], "session_context")
        self.assertEqual(
            runtime_payload["runtime_injection_projection"]["runtime_context_keys"],
            ["cache_dependency", "session_id"],
        )
        self.assertEqual(runtime_payload["runtime_injection_projection"]["store_kind"], "shared_store")
        self.assertTrue(status_payload["runtime_injection_projection"]["store_access_expected"])


if __name__ == "__main__":
    unittest.main()
