import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorDurableArtifactAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_artifact_engine_tracks_frozen_brief_fields(self) -> None:
        repo_root = self.make_repo_root("artifact-engine-brief")
        run_payload = self.invoke(repo_root, "run", "--task", "artifact brief task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "write-brief",
            "--thread-id",
            thread_id,
            "--objective",
            "ship durable artifact engine",
            "--source-evidence-refs",
            "doc:proposal",
            "doc:design",
        )

        artifact_payload = self.invoke(repo_root, "artifact-engine", "--thread-id", thread_id)
        projection = artifact_payload["durable_artifact_aware_live_primary_engine_projection"]

        self.assertEqual(projection["artifact_state_kind"], "implementation_brief_present")
        self.assertTrue(projection["implementation_brief_present"])
        self.assertTrue(projection["implementation_brief_id"].startswith("brief-"))
        self.assertEqual(projection["implementation_brief_source_evidence_ref_count"], 2)
        self.assertFalse(projection["survivor_queue_present"])
        self.assertIn(f"brief:{projection['implementation_brief_id']}", projection["artifact_transition_log"])

    def test_artifact_engine_tracks_survivor_queue_fields(self) -> None:
        repo_root = self.make_repo_root("artifact-engine-survivors")
        run_payload = self.invoke(repo_root, "run", "--task", "artifact survivor task", "--phase", "stabilize")
        thread_id = run_payload["thread_id"]

        self.invoke(
            repo_root,
            "enqueue-survivor",
            "--thread-id",
            thread_id,
            "--bug-id",
            "bug-1",
            "--title",
            "artifact survivor",
            "--severity",
            "high",
            "--evidence",
            "trace pointer",
            "--judge-verdict",
            "survives",
            "--owner-lane",
            "debugger",
            "--status",
            "queued",
            "--verification-result",
            "pending",
        )

        artifact_payload = self.invoke(repo_root, "artifact-engine", "--thread-id", thread_id)
        projection = artifact_payload["durable_artifact_aware_live_primary_engine_projection"]

        self.assertEqual(projection["artifact_state_kind"], "survivor_queue_present")
        self.assertTrue(projection["survivor_queue_present"])
        self.assertEqual(projection["survivor_queue_kind"], "judge_approved_survivor_queue")
        self.assertEqual(projection["survivor_count"], 1)
        self.assertFalse(projection["implementation_brief_present"])
        self.assertIn("survivor_queue:judge_approved_survivor_queue", projection["artifact_transition_log"])

    def test_inspect_exposes_artifact_engine_contract_and_projection(self) -> None:
        repo_root = self.make_repo_root("artifact-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "artifact inspect task", "--phase", "verify-accept")
        thread_id = run_payload["thread_id"]

        brief_payload = self.invoke(
            repo_root,
            "write-brief",
            "--thread-id",
            thread_id,
            "--objective",
            "ship artifact projection",
            "--source-evidence-refs",
            "doc:proposal",
            "doc:design",
        )
        self.invoke(
            repo_root,
            "enqueue-survivor",
            "--thread-id",
            thread_id,
            "--bug-id",
            "bug-2",
            "--title",
            "artifact inspect survivor",
            "--severity",
            "medium",
            "--evidence",
            "judge log",
            "--judge-verdict",
            "survives",
            "--owner-lane",
            "debugger",
            "--status",
            "queued",
            "--verification-result",
            "pending",
        )

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["durable_artifact_aware_live_primary_engine_projection"]

        self.assertIn(
            "implementation_brief_id",
            inspect_payload["contract"]["durable_artifact_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["artifact_state_kind"], "brief_and_survivor_queue_present")
        self.assertEqual(projection["implementation_brief_id"], brief_payload["brief"]["brief_id"])
        self.assertEqual(projection["survivor_queue_kind"], "judge_approved_survivor_queue")
        self.assertEqual(projection["survivor_count"], 1)
        self.assertEqual(projection["helper_pointer"]["command"], "artifact-engine")


if __name__ == "__main__":
    unittest.main()
