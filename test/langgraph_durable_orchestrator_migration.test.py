import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorMigrationTest(unittest.TestCase):
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

    def test_run_seeds_graph_contract_and_migration_safe_projection(self) -> None:
        repo_root = self.make_repo_root("migration-run")
        run_payload = self.invoke(repo_root, "run", "--task", "migration task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.assertEqual(
            run_payload["migration_projection"]["current_graph_contract"]["graph_contract_id"],
            "codex_user_level_langgraph",
        )
        self.assertEqual(
            run_payload["migration_projection"]["thread_graph_contract"]["topology_version"],
            "1.0",
        )
        self.assertEqual(run_payload["migration_projection"]["compatibility"], "migration_safe")

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(
            inspect_payload["contract"]["graph_contract_fields"],
            ["graph_contract_id", "topology_version", "state_schema_version"],
        )
        self.assertIn("graph_contract_id_mismatch", inspect_payload["contract"]["migration_reason_codes"])

    def test_migration_command_classifies_minor_and_major_drift(self) -> None:
        repo_root = self.make_repo_root("migration-drift")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "migration drift task",
            "--phase",
            "execute-parallel",
            "--thread-topology-version",
            "1.0",
            "--thread-state-schema-version",
            "1.0",
        )
        thread_id = run_payload["thread_id"]

        degraded_payload = self.invoke(
            repo_root,
            "migration",
            "--thread-id",
            thread_id,
            "--current-topology-version",
            "1.1",
            "--current-state-schema-version",
            "1.1",
        )
        self.assertEqual(degraded_payload["migration_projection"]["compatibility"], "degraded_compatible")
        self.assertEqual(degraded_payload["migration_projection"]["topology_compatibility"], "degraded_compatible")
        self.assertEqual(
            degraded_payload["migration_projection"]["reason_codes"],
            ["state_schema_minor_drift", "topology_minor_drift"],
        )

        incompatible_payload = self.invoke(
            repo_root,
            "migration",
            "--thread-id",
            thread_id,
            "--current-topology-version",
            "2.0",
            "--current-state-schema-version",
            "1.0",
        )
        self.assertEqual(incompatible_payload["migration_projection"]["compatibility"], "incompatible")
        self.assertEqual(incompatible_payload["migration_projection"]["topology_compatibility"], "incompatible")
        self.assertIn("topology_major_drift", incompatible_payload["migration_projection"]["reason_codes"])
        self.assertEqual(
            incompatible_payload["migration_projection"]["helper_pointer"]["command"],
            "migration",
        )


if __name__ == "__main__":
    unittest.main()
