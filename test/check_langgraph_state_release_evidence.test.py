from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_durable_artifact_state_surfaces.py"
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"
FIXTURE_DIR = REPO_ROOT / "test" / "fixtures" / "langgraph_state_release_evidence"

spec = importlib.util.spec_from_file_location("check_durable_artifact_state_surfaces", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class LangGraphStateReleaseEvidenceTest(unittest.TestCase):
    maxDiff = None


    def make_repo_root(self, name: str) -> Path:
        repo_root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        repo_root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(repo_root, ignore_errors=True))
        return repo_root

    def invoke_runtime(self, repo_root: Path, *args: str, check: bool = True) -> dict:
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), *args, "--repo-root", str(repo_root)],
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        return json.loads(result.stdout)

    def run_runtime_process(self, repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *args, "--repo-root", str(repo_root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def fixture(self, name: str) -> Path:
        path = FIXTURE_DIR / name
        self.assertTrue(path.exists(), f"missing fixture {path}")
        return path

    def run_cli(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--evidence", str(path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_fixture(self, name: str) -> dict:
        return module.run_evidence_check(self.fixture(name))

    def test_fixture_set_covers_completed_running_released_and_handoff_states(self) -> None:
        names = {path.name for path in FIXTURE_DIR.glob("*.json")}
        self.assertIn("completed_valid.json", names)
        self.assertIn("running_completed_invalid.json", names)
        self.assertIn("released_valid.json", names)
        self.assertIn("handoff_valid.json", names)

    def test_completed_release_fixture_passes(self) -> None:
        payload = self.run_fixture("completed_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_released_fixture_requires_release_fields_and_passes(self) -> None:
        payload = self.run_fixture("released_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_handoff_fixture_requires_handoff_fields_and_passes(self) -> None:
        payload = self.run_fixture("handoff_valid.json")

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_state_release", payload["detected"])

    def test_completed_running_state_fails_closed(self) -> None:
        payload = self.run_fixture("running_completed_invalid.json")

        self.assertFalse(payload["ok"])
        self.assertTrue(any("status=running" in error for error in payload["errors"]), payload["errors"])

    def test_handoff_missing_target_and_reason_fails(self) -> None:
        payload = self.run_fixture("handoff_missing_fields_invalid.json")

        self.assertFalse(payload["ok"])
        self.assertTrue(any("handoff_target" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("reason" in error for error in payload["errors"]), payload["errors"])

    def test_cli_rejects_completed_running_state(self) -> None:
        result = self.run_cli(self.fixture("running_completed_invalid.json"))

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("status=running" in error for error in payload["errors"]), payload["errors"])


    def test_runtime_close_thread_writes_release_receipt_and_projects_terminal_state(self) -> None:
        repo_root = self.make_repo_root("release-close")
        run_payload = self.invoke_runtime(repo_root, "run", "--task", "release task", "--phase", "verify-accept")
        thread_id = run_payload["thread_id"]

        release_payload = self.invoke_runtime(
            repo_root,
            "release-thread",
            "--thread-id",
            thread_id,
            "--release-action",
            "close",
            "--released-by",
            "codex-main-session",
            "--final-phase",
            "verify-accept",
            "--result-summary",
            "local validation accepted",
            "--rollback-restore-note",
            "replay checkpoint before release if this close was premature",
            "--redaction-status",
            "not_required",
        )

        self.assertEqual(release_payload["operation"], "release-thread")
        self.assertEqual(release_payload["thread"]["status"], "closed")
        self.assertNotEqual(release_payload["thread"]["status"], "running")
        self.assertEqual(release_payload["thread"]["final_phase"], "verify-accept")
        self.assertEqual(release_payload["thread"]["released_by"], "codex-main-session")
        self.assertTrue(release_payload["thread"]["completed_at"])
        self.assertTrue(release_payload["thread"]["released_at"])

        receipt_path = Path(release_payload["release_receipt_path"])
        self.assertIn("releases", receipt_path.parts)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["thread_id"], thread_id)
        self.assertEqual(receipt["backend_family"], "langgraph")
        self.assertEqual(receipt["previous_status"], "running")
        self.assertEqual(receipt["release_action"], "close")
        self.assertEqual(receipt["released_by"], "codex-main-session")
        self.assertEqual(receipt["survivor_queue_status"], "missing")
        self.assertEqual(receipt["handoff_target"], "")
        self.assertTrue(receipt["checkpoint_path"])
        self.assertTrue(receipt["artifact_path"])
        self.assertFalse(receipt["timeout_release"])
        self.assertEqual(
            receipt["rollback_restore_note"],
            "replay checkpoint before release if this close was premature",
        )
        self.assertEqual(receipt["redaction_status"], "not_required")

        status_payload = self.invoke_runtime(repo_root, "status", "--thread-id", thread_id)
        self.assertEqual(status_payload["thread"]["status"], "closed")
        self.assertEqual(status_payload["release_receipt"]["release_action"], "close")
        self.assertTrue(status_payload["release_projection"]["release_receipt_present"])
        self.assertFalse(status_payload["release_projection"]["active_running_state"])
        self.assertEqual(status_payload["backend_record"]["release_receipt_path"], str(receipt_path))
        self.assertEqual(status_payload["backend_record"]["release_projection"]["release_action"], "close")

        inspect_payload = self.invoke_runtime(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["release_receipt"]["thread_id"], thread_id)
        self.assertTrue(inspect_payload["release_projection"]["release_receipt_present"])
        self.assertEqual(inspect_payload["durable_artifacts"]["release_receipt_path"], str(receipt_path))

    def test_runtime_release_thread_records_timeout_release_without_backend_switch(self) -> None:
        repo_root = self.make_repo_root("release-timeout")
        run_payload = self.invoke_runtime(repo_root, "run", "--task", "timeout release task", "--phase", "stabilize")
        thread_id = run_payload["thread_id"]

        release_payload = self.invoke_runtime(
            repo_root,
            "release-thread",
            "--thread-id",
            thread_id,
            "--release-action",
            "release",
            "--released-by",
            "codex-main-session",
            "--timeout-release",
            "--rollback-restore-note",
            "restore from checkpoint if the timeout was transient",
            "--redaction-status",
            "needs_review",
        )

        self.assertEqual(release_payload["thread"]["status"], "released")
        self.assertEqual(release_payload["release_receipt"]["backend_family"], "langgraph")
        self.assertEqual(release_payload["release_receipt"]["release_action"], "release")
        self.assertTrue(release_payload["release_receipt"]["timeout_release"])
        self.assertEqual(release_payload["release_receipt"]["redaction_status"], "needs_review")
        self.assertEqual(release_payload["backend_record"]["backend"], "langgraph")
        self.assertEqual(release_payload["backend_record"]["status"], "released")
        self.assertEqual(release_payload["backend_record"]["release_projection"]["release_action"], "release")
        self.assertFalse(release_payload["backend_record"]["release_projection"]["active_running_state"])

    def test_runtime_handoff_release_requires_target_and_reason(self) -> None:
        repo_root = self.make_repo_root("release-handoff-required")
        run_payload = self.invoke_runtime(repo_root, "run", "--task", "handoff task", "--phase", "stabilize")
        thread_id = run_payload["thread_id"]

        result = self.run_runtime_process(
            repo_root,
            "release-thread",
            "--thread-id",
            thread_id,
            "--release-action",
            "handoff",
            "--released-by",
            "codex-main-session",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("handoff_target", result.stderr + result.stdout)
        self.assertIn("reason", result.stderr + result.stdout)

    def test_runtime_handoff_release_records_target_reason_and_keeps_langgraph_backend(self) -> None:
        repo_root = self.make_repo_root("release-handoff-success")
        run_payload = self.invoke_runtime(repo_root, "run", "--task", "handoff task", "--phase", "integrate-converge")
        thread_id = run_payload["thread_id"]

        release_payload = self.invoke_runtime(
            repo_root,
            "release-thread",
            "--thread-id",
            thread_id,
            "--release-action",
            "handoff",
            "--released-by",
            "codex-main-session",
            "--handoff-target",
            "native_omx:debugger-lane",
            "--reason",
            "blocking stabilization needs worker-centric mailbox flow",
            "--result-summary",
            "handoff recorded without starting target backend",
        )

        self.assertEqual(release_payload["thread"]["status"], "handoff")
        self.assertEqual(release_payload["thread"]["handoff_target"], "native_omx:debugger-lane")
        self.assertEqual(release_payload["thread"]["reason"], "blocking stabilization needs worker-centric mailbox flow")
        self.assertTrue(release_payload["thread"]["handoff_at"])
        self.assertEqual(release_payload["release_receipt"]["release_action"], "handoff")
        self.assertEqual(release_payload["release_receipt"]["handoff_target"], "native_omx:debugger-lane")
        self.assertEqual(release_payload["release_receipt"]["backend_family"], "langgraph")
        self.assertEqual(release_payload["backend_record"]["backend"], "langgraph")
        self.assertEqual(release_payload["backend_record"]["release_projection"]["handoff_target"], "native_omx:debugger-lane")
        self.assertFalse(release_payload["backend_record"]["release_projection"]["active_running_state"])


if __name__ == "__main__":
    unittest.main()
