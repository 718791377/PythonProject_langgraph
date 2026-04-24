import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorDurableArtifactsTest(unittest.TestCase):
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

    def test_write_brief_persists_first_class_fields(self) -> None:
        repo_root = self.make_repo_root("brief")
        run_payload = self.invoke(repo_root, "run", "--task", "brief task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        brief_payload = self.invoke(
            repo_root,
            "write-brief",
            "--thread-id",
            thread_id,
            "--objective",
            "ship artifact contract",
            "--non-goals",
            "no backend policy changes",
            "--accepted-decisions",
            "artifact is first class",
            "--constraints",
            "keep additive backend",
            "--interfaces",
            "inspect surface",
            "--ownership-boundaries",
            "leader owns integration",
            "--acceptance-criteria",
            "brief persists",
            "--validation-plan",
            "unit tests",
            "--source-evidence-refs",
            "doc:proposal",
            "doc:design",
        )

        self.assertTrue(brief_payload["brief"]["brief_id"].startswith("brief-"))
        self.assertEqual(brief_payload["brief"]["thread_id"], thread_id)
        self.assertEqual(brief_payload["brief"]["source_evidence_refs"], ["doc:proposal", "doc:design"])
        self.assertTrue(brief_payload["brief"]["frozen_at"])
        self.assertTrue(brief_payload["durable_artifacts"]["implementation_brief_present"])

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["implementation_brief"]["thread_id"], thread_id)
        self.assertEqual(inspect_payload["implementation_brief"]["source_evidence_refs"], ["doc:proposal", "doc:design"])
        self.assertEqual(inspect_payload["durable_artifacts"]["survivor_count"], 0)

    def test_survivor_queue_persists_only_resumable_queue_metadata(self) -> None:
        repo_root = self.make_repo_root("survivors")
        run_payload = self.invoke(repo_root, "run", "--task", "survivor task", "--phase", "stabilize")
        thread_id = run_payload["thread_id"]

        queue_payload = self.invoke(
            repo_root,
            "enqueue-survivor",
            "--thread-id",
            thread_id,
            "--bug-id",
            "bug-1",
            "--title",
            "judge survivor",
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

        self.assertEqual(queue_payload["queue"]["queue_kind"], "judge_approved_survivor_queue")
        self.assertEqual(queue_payload["queue"]["thread_id"], thread_id)
        self.assertEqual(queue_payload["queue"]["items"][0]["verification_result"], "pending")
        self.assertTrue(queue_payload["queue"]["items"][0]["updated_at"])
        self.assertEqual(queue_payload["durable_artifacts"]["survivor_count"], 1)

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["survivor_queue"]["queue_kind"], "judge_approved_survivor_queue")
        self.assertEqual(len(inspect_payload["survivor_queue"]["items"]), 1)
        self.assertTrue(inspect_payload["durable_artifacts"]["survivor_queue_present"])


if __name__ == "__main__":
    unittest.main()
