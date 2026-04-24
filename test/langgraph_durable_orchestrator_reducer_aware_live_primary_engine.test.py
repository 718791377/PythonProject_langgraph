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


class LangGraphDurableOrchestratorReducerAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def merge_branch(self, repo_root: Path, thread_id: str, payload: dict) -> dict:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(payload, handle)
            temp_path = Path(handle.name)
        self.addCleanup(lambda: temp_path.unlink(missing_ok=True))
        return self.invoke(repo_root, "merge-branch", "--thread-id", thread_id, "--payload-file", str(temp_path))

    def test_reducer_engine_tracks_merge_channels_and_fanout(self) -> None:
        repo_root = self.make_repo_root("reducer-engine-merge")
        run_payload = self.invoke(repo_root, "run", "--task", "reducer engine task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        self.merge_branch(
            repo_root,
            thread_id,
            {
                "branch_id": "branch-a",
                "fanout_state": "partial",
                "reducer_channels": {
                    "branch_findings": [
                        {"finding_id": "finding-2", "message": "second"},
                        {"finding_id": "finding-1", "message": "first"},
                    ],
                    "branch_evidence_refs": [
                        {"evidence_id": "evidence-1", "pointer": "trace:a"},
                    ],
                },
            },
        )

        reducer_payload = self.invoke(repo_root, "reducer-engine", "--thread-id", thread_id)
        projection = reducer_payload["reducer_aware_live_primary_engine_projection"]

        self.assertEqual(projection["merge_state_kind"], "single_branch_merge")
        self.assertEqual(projection["reducer_compatibility"], "reducer_aware")
        self.assertEqual(projection["fanout_state"], "partial")
        self.assertIn("branch_findings", projection["merge_channels_updated"])
        self.assertEqual(projection["channel_item_counts"]["branch_findings"], 2)
        self.assertEqual(projection["source_records"], ["branch:branch-a"])

    def test_reducer_engine_surfaces_invalid_multi_writer_posture(self) -> None:
        repo_root = self.make_repo_root("reducer-engine-invalid")
        run_payload = self.invoke(repo_root, "run", "--task", "reducer invalid task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        self.merge_branch(
            repo_root,
            thread_id,
            {
                "branch_id": "branch-b",
                "fanout_state": "active",
                "single_writer_updates": {
                    "phase": "stabilize",
                },
            },
        )

        reducer_payload = self.invoke(repo_root, "reducer-engine", "--thread-id", thread_id)
        projection = reducer_payload["reducer_aware_live_primary_engine_projection"]

        self.assertEqual(projection["merge_state_kind"], "invalid_multi_writer_detected")
        self.assertTrue(projection["invalid_multi_writer_detected"])
        self.assertEqual(projection["invalid_multi_writer_updates"][0]["field"], "phase")
        self.assertEqual(projection["invalid_multi_writer_updates"][0]["reason"], "single_writer_field_conflict")

    def test_inspect_exposes_reducer_engine_contract_and_ready_state(self) -> None:
        repo_root = self.make_repo_root("reducer-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "reducer inspect task", "--phase", "verify-accept")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["reducer_aware_live_primary_engine_projection"]

        self.assertIn(
            "fanout_state",
            inspect_payload["contract"]["reducer_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["reducer_compatibility"], "reducer_aware")
        self.assertEqual(projection["merge_state_kind"], "reducer_ready")
        self.assertEqual(projection["helper_pointer"]["command"], "reducer-engine")


if __name__ == "__main__":
    unittest.main()
