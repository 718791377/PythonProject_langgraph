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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_trace_evidence.py"

spec = importlib.util.spec_from_file_location("check_orchestration_trace_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


VALID_TRACE = """Routing trace:
phase=verify-accept
capability_chain=subagent:auto > omx:on > langgraph:on
backend_default=langgraph
backend_ready=true
experts=none
durable_workflow=not_needed
persistent_team=not_needed
why=single validated checker slice; threshold_not_met:single_execution_slice.
"""


class OrchestrationTraceEvidenceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_trace(self, root: Path, content: str) -> Path:
        path = root / "trace.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def run_cli(self, trace_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--trace", str(trace_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_valid_trace_passes(self) -> None:
        root = self.make_root("trace-valid")
        path = self.write_trace(root, VALID_TRACE)

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["fields"]["backend_default"], "langgraph")
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_cli_emits_json(self) -> None:
        root = self.make_root("trace-cli")
        path = self.write_trace(root, VALID_TRACE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "orchestration_trace_evidence")

    def test_missing_required_field_fails(self) -> None:
        root = self.make_root("trace-missing")
        path = self.write_trace(root, VALID_TRACE.replace("backend_ready=true\n", ""))

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("backend_ready" in error for error in payload["errors"]), payload["errors"])

    def test_inconsistent_capability_chain_fails(self) -> None:
        root = self.make_root("trace-chain")
        path = self.write_trace(
            root,
            VALID_TRACE.replace(
                "capability_chain=subagent:auto > omx:on > langgraph:on",
                "capability_chain=subagent:off > omx:on > langgraph:on",
            ),
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("subagent:off" in error for error in payload["errors"]), payload["errors"])

    def test_ready_langgraph_chain_requires_langgraph_default(self) -> None:
        root = self.make_root("trace-default")
        path = self.write_trace(root, VALID_TRACE.replace("backend_default=langgraph", "backend_default=native_omx"))

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("backend_default must be langgraph" in error for error in payload["errors"]), payload["errors"])

    def test_unsupported_lane_state_fails(self) -> None:
        root = self.make_root("trace-lane-state")
        path = self.write_trace(root, VALID_TRACE.replace("persistent_team=not_needed", "persistent_team=maybe"))

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("persistent_team must be one of" in error for error in payload["errors"]), payload["errors"])

    def test_missing_user_reminder_reason_fails(self) -> None:
        root = self.make_root("trace-missing-reminder")
        path = self.write_trace(
            root,
            VALID_TRACE.replace(
                "why=single validated checker slice; threshold_not_met:single_execution_slice.",
                "why=user did not request parallelism.",
            ),
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("missing user reminders" in error for error in payload["errors"]), payload["errors"])

    def test_timeout_without_non_evidence_label_fails(self) -> None:
        root = self.make_root("trace-timeout")
        path = self.write_trace(root, VALID_TRACE + "\nVerifier expert timed out, proceeding with result.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("timeout or stall language" in error for error in payload["errors"]), payload["errors"])

    def test_timeout_with_non_evidence_label_passes(self) -> None:
        root = self.make_root("trace-timeout-labeled")
        path = self.write_trace(root, VALID_TRACE + "\nexpert timed out; not used as evidence. main session took over verification.\n")

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])


if __name__ == "__main__":
    unittest.main()
