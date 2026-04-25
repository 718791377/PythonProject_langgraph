import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorCommandFlowTest(unittest.TestCase):
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

    def test_resume_persists_command_goto_metadata(self) -> None:
        repo_root = self.make_repo_root("command-goto")
        run_payload = self.invoke(repo_root, "run", "--task", "command goto task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        resume_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--phase",
            "execute-parallel",
            "--command-kind",
            "update_goto",
            "--command-goto",
            "execute-parallel",
            "--command-graph-scope",
            "current",
            "--command-update-json",
            '{"ownership_boundaries":["src/worker.py"]}',
        )

        self.assertEqual(resume_payload["command_projection"]["transition_kind"], "update_goto")
        self.assertEqual(resume_payload["command_projection"]["graph_scope"], "current")
        self.assertEqual(resume_payload["command_projection"]["source_subgraph"], "planning")
        self.assertEqual(resume_payload["command_projection"]["target_subgraph"], "execution")
        self.assertEqual(resume_payload["command_projection"]["goto_target"], "execute-parallel")
        self.assertEqual(resume_payload["command_projection"]["update_keys"], ["ownership_boundaries"])
        self.assertEqual(resume_payload["command_projection"]["resume_posture"], "ordinary")

    def test_parent_handoff_and_resume_payload_posture_are_inspectable(self) -> None:
        repo_root = self.make_repo_root("parent-handoff")
        run_payload = self.invoke(repo_root, "run", "--task", "parent handoff task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        waiting_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--phase",
            "verify-accept",
            "--command-kind",
            "parent_handoff",
            "--command-graph-scope",
            "parent",
            "--parent-handoff-target",
            "verify-accept",
            "--await-command-resume",
        )
        inspect_waiting = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        self.assertEqual(waiting_payload["command_projection"]["transition_kind"], "parent_handoff")
        self.assertEqual(waiting_payload["command_projection"]["graph_scope"], "parent")
        self.assertEqual(waiting_payload["command_projection"]["source_subgraph"], "execution")
        self.assertEqual(waiting_payload["command_projection"]["target_subgraph"], "verification")
        self.assertEqual(waiting_payload["command_projection"]["resume_posture"], "awaiting_command_resume")
        self.assertEqual(inspect_waiting["command_projection"]["helper_pointer"]["command"], "inspect")

        resumed_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--phase",
            "verify-accept",
            "--command-kind",
            "resume_parent_handoff",
            "--command-graph-scope",
            "parent",
            "--parent-handoff-target",
            "verify-accept",
            "--resume-payload-json",
            '{"approved":true,"route":"verify"}',
        )
        status_after_resume = self.invoke(repo_root, "status", "--thread-id", thread_id)

        self.assertEqual(resumed_payload["command_projection"]["transition_kind"], "resume_parent_handoff")
        self.assertEqual(resumed_payload["command_projection"]["resume_posture"], "resumed_with_payload")
        self.assertTrue(resumed_payload["command_projection"]["resume_payload_present"])
        self.assertEqual(
            resumed_payload["command_projection"]["resume_payload_keys"],
            ["approved", "route"],
        )
        self.assertEqual(status_after_resume["command_projection"]["resume_posture"], "resumed_with_payload")


if __name__ == "__main__":
    unittest.main()
