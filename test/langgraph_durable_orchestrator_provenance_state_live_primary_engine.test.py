import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorProvenanceStateLivePrimaryEngineTest(unittest.TestCase):
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

    def test_provenance_engine_tracks_history_availability(self) -> None:
        repo_root = self.make_repo_root("provenance-engine-history")
        run_payload = self.invoke(repo_root, "run", "--task", "provenance history task", "--phase", "read-context")
        thread_id = run_payload["thread_id"]

        provenance_payload = self.invoke(repo_root, "provenance-engine", "--thread-id", thread_id)
        projection = provenance_payload["provenance_state_live_primary_engine_projection"]

        self.assertIn(projection["provenance_state_kind"], {"history_available", "synthetic_history"})
        self.assertGreaterEqual(projection["history_target_count"], 1)
        self.assertTrue(projection["source_records"])

    def test_provenance_engine_tracks_time_travel_recovery_target_and_sources(self) -> None:
        repo_root = self.make_repo_root("provenance-engine-time-travel")
        run_payload = self.invoke(repo_root, "run", "--task", "provenance time travel task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        history_payload = self.invoke(repo_root, "history", "--thread-id", thread_id)
        checkpoint_target = next(
            target
            for target in history_payload["history_projection"]["available_targets"]
            if target["target_kind"] == "checkpoint"
        )

        self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--target-id",
            checkpoint_target["target_id"],
        )

        provenance_payload = self.invoke(repo_root, "provenance-engine", "--thread-id", thread_id)
        projection = provenance_payload["provenance_state_live_primary_engine_projection"]

        self.assertEqual(projection["provenance_state_kind"], "time_travel_recovery")
        self.assertEqual(projection["recovery_action"], "time-travel")
        self.assertEqual(projection["recovery_target_id"], checkpoint_target["target_id"])
        self.assertEqual(projection["recovery_target_kind"], "checkpoint")
        self.assertEqual(projection["stop_boundary"], "recovery_boundary")
        self.assertTrue(projection["source_records"])

    def test_provenance_engine_tracks_update_state_recovery_fields(self) -> None:
        repo_root = self.make_repo_root("provenance-engine-update-state")
        run_payload = self.invoke(repo_root, "run", "--task", "provenance update state task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "phase=execute-parallel",
            "--clear-interrupt",
        )

        provenance_payload = self.invoke(repo_root, "provenance-engine", "--thread-id", thread_id)
        projection = provenance_payload["provenance_state_live_primary_engine_projection"]

        self.assertEqual(projection["provenance_state_kind"], "update_state_recovery")
        self.assertEqual(projection["recovery_action"], "update-state")
        self.assertEqual(projection["recovery_target_kind"], "update_state")
        self.assertIn("thread:phase", projection["recoverable_fields_touched"])


if __name__ == "__main__":
    unittest.main()
