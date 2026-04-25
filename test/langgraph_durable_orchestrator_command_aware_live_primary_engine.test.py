import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorCommandAwareLivePrimaryEngineTest(unittest.TestCase):
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

    def test_command_engine_tracks_update_goto_control_state(self) -> None:
        repo_root = self.make_repo_root("command-engine-goto")
        run_payload = self.invoke(repo_root, "run", "--task", "command engine task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        self.invoke(
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

        engine_payload = self.invoke(repo_root, "command-engine", "--thread-id", thread_id)
        projection = engine_payload["command_aware_live_primary_engine_projection"]

        self.assertEqual(projection["control_state_kind"], "goto_control")
        self.assertEqual(projection["transition_kind"], "update_goto")
        self.assertEqual(projection["graph_scope"], "current")
        self.assertEqual(projection["source_subgraph"], "planning")
        self.assertEqual(projection["target_subgraph"], "execution")
        self.assertEqual(projection["goto_target"], "execute-parallel")
        self.assertEqual(projection["update_keys"], ["ownership_boundaries"])
        self.assertIn("command:update_goto", projection["command_transition_log"])

    def test_command_engine_tracks_parent_handoff_and_resume_payload(self) -> None:
        repo_root = self.make_repo_root("command-engine-handoff")
        run_payload = self.invoke(repo_root, "run", "--task", "parent handoff task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        self.invoke(
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
        waiting_engine = self.invoke(repo_root, "command-engine", "--thread-id", thread_id)
        waiting_projection = waiting_engine["command_aware_live_primary_engine_projection"]
        self.assertEqual(waiting_projection["control_state_kind"], "awaiting_command_resume")
        self.assertEqual(waiting_projection["resume_posture"], "awaiting_command_resume")
        self.assertEqual(waiting_projection["parent_handoff_target"], "verify-accept")

        self.invoke(
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
        resumed_engine = self.invoke(repo_root, "command-engine", "--thread-id", thread_id)
        resumed_projection = resumed_engine["command_aware_live_primary_engine_projection"]

        self.assertEqual(resumed_projection["control_state_kind"], "parent_handoff_control")
        self.assertEqual(resumed_projection["transition_kind"], "resume_parent_handoff")
        self.assertEqual(resumed_projection["resume_posture"], "resumed_with_payload")
        self.assertTrue(resumed_projection["resume_payload_present"])
        self.assertEqual(resumed_projection["resume_payload_keys"], ["approved", "route"])
        self.assertEqual(resumed_projection["target_subgraph"], "verification")

    def test_inspect_exposes_command_engine_contract_and_projection(self) -> None:
        repo_root = self.make_repo_root("command-engine-inspect")
        run_payload = self.invoke(repo_root, "run", "--task", "command inspect task", "--phase", "define-target")
        thread_id = run_payload["thread_id"]

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        projection = inspect_payload["command_aware_live_primary_engine_projection"]

        self.assertIn(
            "parent_handoff_target",
            inspect_payload["contract"]["command_aware_live_primary_engine_projection_fields"],
        )
        self.assertEqual(projection["control_state_kind"], "ordinary")
        self.assertEqual(projection["transition_kind"], "")
        self.assertEqual(projection["resume_posture"], "ordinary")
        self.assertEqual(projection["helper_pointer"]["command"], "command-engine")


if __name__ == "__main__":
    unittest.main()
