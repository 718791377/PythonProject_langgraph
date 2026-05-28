from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRACE_SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_trace_evidence.py"
COLLAB_SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_collaboration_evidenceguard.py"

trace_spec = importlib.util.spec_from_file_location("check_orchestration_trace_evidence", TRACE_SCRIPT_PATH)
trace_module = importlib.util.module_from_spec(trace_spec)
assert trace_spec and trace_spec.loader
trace_spec.loader.exec_module(trace_module)

collab_spec = importlib.util.spec_from_file_location(
    "check_orchestration_collaboration_evidenceguard",
    COLLAB_SCRIPT_PATH,
)
collab_module = importlib.util.module_from_spec(collab_spec)
assert collab_spec and collab_spec.loader
collab_spec.loader.exec_module(collab_module)


class MainSessionEscalationVisibilityTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_text(self, root: Path, content: str) -> Path:
        path = root / "trace.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, root: Path, payload: dict) -> Path:
        path = root / "evidence.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_trace_requires_main_session_escalation_fields(self) -> None:
        root = self.make_root("main-session-escalation-trace-missing")
        path = self.write_text(
            root,
            """Routing trace:
phase=freeze-plan
capability_chain=subagent:auto > omx:on > langgraph:on
backend_default=langgraph
backend_ready=true
experts=none
durable_workflow=blocked
persistent_team=not_needed
why=blocked:human_approval_required; threshold_not_met:single_execution_slice; approval_wait pending in LangGraph.
""",
        )

        payload = trace_module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("main_session_escalation" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_pending_approval_requires_receipt_and_main_session_owner(self) -> None:
        root = self.make_root("main-session-escalation-invalid")
        path = self.write_json(
            root,
            {
                "schema_version": 1,
                "case_type": "main_session_escalation_visibility",
                "case_id": "missing_receipt",
                "main_session_escalation": "pending_approval",
                "pending_approval": True,
                "approval_timeout_risk": "high",
                "approval_receipt": "none",
                "main_session_only": False,
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("approval_receipt" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("main_session_only" in error for error in payload["errors"]), payload["errors"])

    def test_repository_main_session_escalation_fixtures_pass(self) -> None:
        payload = collab_module.run_fixture_check(REPO_ROOT)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("main_session_escalation_pending.json", payload["checked_cases"])
        self.assertIn("main_session_escalation_timed_out.json", payload["checked_cases"])


if __name__ == "__main__":
    unittest.main()
