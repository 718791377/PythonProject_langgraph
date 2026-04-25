import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorMigrationAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_migration_engine_tracks_safe_contract_state(self) -> None:
        repo_root = self.make_repo_root("migration-engine-safe")
        run_payload = self.invoke(repo_root, "run", "--task", "migration engine task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "migration-engine", "--thread-id", thread_id)
        projection = engine_payload["migration_aware_live_primary_engine_projection"]

        self.assertEqual(projection["compatibility_state_kind"], "migration_safe_thread")
        self.assertEqual(projection["compatibility"], "migration_safe")
        self.assertEqual(projection["current_graph_contract"]["graph_contract_id"], "codex_user_level_langgraph")
        self.assertEqual(projection["thread_graph_contract"]["topology_version"], "1.0")
        self.assertIn("compatibility:migration_safe", projection["compatibility_transition_log"])

    def test_migration_engine_tracks_incompatible_thread_state(self) -> None:
        repo_root = self.make_repo_root("migration-engine-incompatible")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "migration engine incompatible task",
            "--phase",
            "execute-parallel",
            "--thread-topology-version",
            "2.0",
            "--thread-state-schema-version",
            "1.0",
        )
        thread_id = run_payload["thread_id"]

        engine_payload = self.invoke(repo_root, "migration-engine", "--thread-id", thread_id)
        projection = engine_payload["migration_aware_live_primary_engine_projection"]

        self.assertEqual(projection["compatibility_state_kind"], "incompatible_thread")
        self.assertEqual(projection["compatibility"], "incompatible")
        self.assertEqual(projection["topology_compatibility"], "incompatible")
        self.assertIn("topology_major_drift", projection["reason_codes"])

    def test_inspect_exposes_migration_engine_contract_and_projection(self) -> None:
        repo_root = self.make_repo_root("migration-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "migration inspect task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["migration_aware_live_primary_engine_projection"]

        self.assertIn(
            "reason_codes",
            inspect_payload["contract"]["migration_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["compatibility_state_kind"], "migration_safe_thread")
        self.assertEqual(projection["helper_pointer"]["command"], "migration-engine")


if __name__ == "__main__":
    unittest.main()
