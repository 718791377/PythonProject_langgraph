import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorQualityLoopsTest(unittest.TestCase):
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

    def test_execution_loop_revise_and_needs_human(self) -> None:
        repo_root = self.make_repo_root("execution-loop")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "execution loop task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "2",
        )
        thread_id = run_payload["thread_id"]
        self.assertEqual(run_payload["loop_projection"]["active_loop"], "execution")
        self.assertEqual(run_payload["loop_projection"]["iteration_budget"], 2)

        revise_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--loop-kind",
            "execution",
            "--gate-verdict",
            "revise",
            "--gate-reason",
            "validation_failed",
        )
        self.assertEqual(revise_payload["thread"]["iteration_count"], 1)
        self.assertEqual(revise_payload["thread"]["last_gate_verdict"], "revise")
        self.assertEqual(revise_payload["thread"]["stop_reason"], "")

        approval_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--gate-verdict",
            "needs_human",
            "--gate-reason",
            "manual_approval_required",
        )
        self.assertEqual(approval_payload["thread"]["status"], "waiting_for_approval")
        self.assertEqual(approval_payload["interrupt"]["status"], "waiting_for_approval")
        self.assertEqual(approval_payload["loop_projection"]["active_loop"], "execution")

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["loop_projection"]["active_loop"], "execution")
        self.assertIn("active_loop", inspect_payload["contract"]["loop_projection_fields"])
        self.assertIn("needs_human", inspect_payload["contract"]["gate_verdicts"])

    def test_iteration_budget_exhaustion_stops_the_loop(self) -> None:
        repo_root = self.make_repo_root("budget-exhaustion")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "budget exhaustion task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "execution",
            "--iteration-budget",
            "1",
        )
        thread_id = run_payload["thread_id"]

        exhausted_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--loop-kind",
            "execution",
            "--gate-verdict",
            "revise",
            "--gate-reason",
            "retry_budget_hit",
        )
        self.assertEqual(exhausted_payload["thread"]["status"], "halted")
        self.assertEqual(exhausted_payload["thread"]["stop_reason"], "iteration_budget_exhausted")
        self.assertEqual(exhausted_payload["loop_projection"]["iteration_count"], 1)

    def test_review_loop_accept_advances_phase(self) -> None:
        repo_root = self.make_repo_root("review-accept")
        run_payload = self.invoke(
            repo_root,
            "run",
            "--task",
            "review acceptance task",
            "--phase",
            "execute-parallel",
            "--loop-kind",
            "review",
            "--iteration-budget",
            "3",
        )
        thread_id = run_payload["thread_id"]

        accept_payload = self.invoke(
            repo_root,
            "resume",
            "--thread-id",
            thread_id,
            "--gate-verdict",
            "accept",
            "--gate-reason",
            "quality_threshold_met",
        )
        self.assertEqual(accept_payload["thread"]["phase"], "integrate-converge")
        self.assertEqual(accept_payload["thread"]["status"], "accepted")
        self.assertEqual(accept_payload["thread"]["stop_reason"], "accepted")


if __name__ == "__main__":
    unittest.main()
