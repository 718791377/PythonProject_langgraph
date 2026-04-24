import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorReplayRecoveryTest(unittest.TestCase):
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

    def invoke_raw(self, repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *args, "--repo-root", str(repo_root)],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

    def test_history_and_replay_are_read_only(self) -> None:
        repo_root = self.make_repo_root("history-replay")
        run_payload = self.invoke(repo_root, "run", "--task", "history task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        resume_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--phase",
            "execute-parallel",
        )
        status_before_replay = self.invoke(repo_root, "status", "--thread-id", thread_id)
        history_payload = self.invoke(repo_root, "history", "--thread-id", thread_id)

        self.assertEqual(history_payload["history_projection"]["compatibility"], "tracked_history")
        self.assertGreaterEqual(history_payload["history_projection"]["target_count"], 4)
        self.assertIn("replay", history_payload["helper_pointers"])

        checkpoint_target = next(
            target
            for target in history_payload["history_projection"]["available_targets"]
            if target["target_kind"] == "checkpoint" and target["checkpoint_kind"] == "skeleton"
        )
        replay_payload = self.invoke(
            repo_root,
            "replay",
            "--thread-id",
            thread_id,
            "--target-id",
            checkpoint_target["target_id"],
        )
        status_after_replay = self.invoke(repo_root, "status", "--thread-id", thread_id)

        self.assertTrue(replay_payload["read_only"])
        self.assertEqual(replay_payload["target_kind"], "checkpoint")
        self.assertEqual(replay_payload["thread_snapshot"]["phase"], "freeze-plan")
        self.assertEqual(status_before_replay["thread"]["phase"], status_after_replay["thread"]["phase"])
        self.assertEqual(status_before_replay["thread"]["status"], status_after_replay["thread"]["status"])
        self.assertEqual(resume_payload["thread"]["phase"], "execute-parallel")

    def test_time_travel_recovery_is_explicit_and_resumable(self) -> None:
        repo_root = self.make_repo_root("time-travel")
        run_payload = self.invoke(repo_root, "run", "--task", "recover task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]
        self.invoke(repo_root, "resume", "--thread-id", thread_id, "--phase", "execute-parallel")
        history_payload = self.invoke(repo_root, "history", "--thread-id", thread_id)
        target_id = next(
            target["target_id"]
            for target in history_payload["history_projection"]["available_targets"]
            if target["target_kind"] == "checkpoint" and target["checkpoint_kind"] == "skeleton"
        )

        recover_payload = self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--target-id",
            target_id,
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        resumed_payload = self.invoke(repo_root, "resume", "--thread-id", thread_id, "--phase", "execute-parallel")
        resumed_status = self.invoke(repo_root, "status", "--thread-id", thread_id)

        self.assertEqual(recover_payload["action"], "time-travel")
        self.assertEqual(recover_payload["recovery_projection"]["posture"], "recovered_pending_resume")
        self.assertEqual(recover_payload["thread"]["recovery_state"]["target_id"], target_id)
        self.assertEqual(inspect_payload["recovery_projection"]["last_action"], "time-travel")
        self.assertEqual(inspect_payload["thread"]["phase"], "freeze-plan")
        self.assertEqual(resumed_payload["thread"]["phase"], "execute-parallel")
        self.assertEqual(resumed_status["recovery_projection"]["posture"], "ordinary")

    def test_update_state_recovery_rejects_invalid_fields_and_can_clear_interrupt(self) -> None:
        repo_root = self.make_repo_root("update-state")
        run_payload = self.invoke(repo_root, "run", "--task", "update state task", "--phase", "freeze-plan")
        thread_id = run_payload["thread_id"]

        invalid_result = self.invoke_raw(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "reducer_state={}",
        )
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("Out-of-scope recoverable thread field", invalid_result.stderr)

        recover_payload = self.invoke(
            repo_root,
            "recover",
            "--thread-id",
            thread_id,
            "--mutation-intent",
            "explicit-recovery",
            "--thread-field",
            "phase=execute-parallel",
            "--thread-field",
            "iteration_budget=3",
            "--clear-interrupt",
        )
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        resumed_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--loop-kind",
            "execution",
            "--gate-verdict",
            "accept",
            "--gate-reason",
            "recovered_state_validated",
        )

        self.assertEqual(recover_payload["action"], "update-state")
        self.assertEqual(recover_payload["thread"]["phase"], "execute-parallel")
        self.assertEqual(recover_payload["thread"]["iteration_budget"], 3)
        self.assertEqual(recover_payload["recovery_projection"]["posture"], "recovered_pending_resume")
        self.assertIn("thread:phase", recover_payload["thread"]["recovery_state"]["recoverable_fields_touched"])
        self.assertIn("interrupt:clear", recover_payload["thread"]["recovery_state"]["recoverable_fields_touched"])
        self.assertEqual(inspect_payload["interrupt"], {})
        self.assertEqual(resumed_payload["recovery_projection"]["posture"], "ordinary")


if __name__ == "__main__":
    unittest.main()
