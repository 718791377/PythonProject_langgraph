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

SELECTED_TRACE = """Routing trace:
phase=execute-parallel
capability_chain=subagent:auto > omx:on > langgraph:on
backend_default=langgraph
backend_ready=true
experts=verifier
durable_workflow=selected
persistent_team=running
why=triggered_threshold:frozen_plan_with_2+_independent_slices for execute-parallel.
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

    def test_not_needed_without_unmet_threshold_fails(self) -> None:
        root = self.make_root("trace-no-threshold")
        path = self.write_trace(
            root,
            VALID_TRACE.replace(
                "why=single validated checker slice; threshold_not_met:single_execution_slice.",
                "why=small checker slice.",
            ),
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("threshold_not_met" in error for error in payload["errors"]), payload["errors"])

    def test_blocked_requires_named_blocker_or_threshold(self) -> None:
        root = self.make_root("trace-blocked-threshold")
        path = self.write_trace(
            root,
            VALID_TRACE.replace("persistent_team=not_needed", "persistent_team=blocked").replace(
                "why=single validated checker slice; threshold_not_met:single_execution_slice.",
                "why=team cannot start yet.",
            ),
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("blocked" in error or "threshold" in error for error in payload["errors"]), payload["errors"])

    def test_selected_or_running_requires_triggered_threshold(self) -> None:
        root = self.make_root("trace-selected-no-trigger")
        path = self.write_trace(
            root,
            SELECTED_TRACE.replace(
                "why=triggered_threshold:frozen_plan_with_2+_independent_slices for execute-parallel.",
                "why=using durable team now.",
            ),
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("triggered threshold" in error for error in payload["errors"]), payload["errors"])

    def test_selected_or_running_with_triggered_threshold_passes(self) -> None:
        root = self.make_root("trace-selected-trigger")
        path = self.write_trace(root, SELECTED_TRACE)

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])


COLLAB_SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_collaboration_evidenceguard.py"
collab_spec = importlib.util.spec_from_file_location(
    "check_orchestration_collaboration_evidenceguard",
    COLLAB_SCRIPT_PATH,
)
collab_module = importlib.util.module_from_spec(collab_spec)
assert collab_spec and collab_spec.loader
collab_spec.loader.exec_module(collab_module)


class OrchestrationCollaborationEvidenceguardTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_repository_collaboration_evidenceguard_surfaces_pass(self) -> None:
        payload = collab_module.run_repository_check(REPO_ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_repository_collaboration_evidenceguard_requires_chinese_openspec_surface(self) -> None:
        root = self.make_root("collab-zh-surface")
        fixture_src = REPO_ROOT / collab_module.DEFAULT_FIXTURE_DIR
        fixture_dst = root / collab_module.DEFAULT_FIXTURE_DIR
        shutil.copytree(fixture_src, fixture_dst)
        for rel in collab_module.REQUIRED_SURFACE_SNIPPETS:
            if rel == "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md":
                continue
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        for rel in ("tools/run_openspec_guard.py", "tools/safety_rule_script_backing_registry.json"):
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        payload = collab_module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("spec.zh-CN.md" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_repository_collaboration_evidenceguard_requires_chinese_openspec_heading_parity(self) -> None:
        root = self.make_root("collab-zh-heading-parity")
        fixture_src = REPO_ROOT / collab_module.DEFAULT_FIXTURE_DIR
        fixture_dst = root / collab_module.DEFAULT_FIXTURE_DIR
        shutil.copytree(fixture_src, fixture_dst)
        for rel in collab_module.REQUIRED_SURFACE_SNIPPETS:
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if rel == "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md":
                dst.write_text(
                    "\n".join(
                        [
                            "# Codex 用户级 Orchestration Activation Policy",
                            "prompt-independent collaboration parity",
                            "durable/persistent evidenceguard",
                            "LangGraph state release",
                            "tools/check_orchestration_collaboration_evidenceguard.py",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )
            else:
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        for rel in ("tools/run_openspec_guard.py", "tools/safety_rule_script_backing_registry.json"):
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        payload = collab_module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("bilingual parity" in error or "Requirement/Scenario headings" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_prompt_independent_fixture_parity_passes(self) -> None:
        payload = collab_module.run_fixture_check(REPO_ROOT)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertGreaterEqual(payload["counts"]["checked_cases"], 6)

    def test_explicit_directive_without_threshold_requires_blocker(self) -> None:
        root = self.make_root("collab-directive-no-threshold")
        path = root / "evidence.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "activation_parity",
                "case_id": "explicit",
                "parity_group": "explicit",
                "collaboration_phrase_present": False,
                "prompt": "Use LangGraph for this single document edit.",
                "input": {"frozen_plan": False, "execution_slices": 1, "explicit_directive": "langgraph"},
                "expected": {
                    "phase": "verify-accept",
                    "capability_chain": "subagent:auto > omx:on > langgraph:on",
                    "backend_default": "langgraph",
                    "backend_ready": "true",
                    "experts": "none",
                    "durable_workflow": "candidate",
                    "persistent_team": "candidate",
                    "why": "using langgraph",
                },
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("without thresholds" in error for error in payload["errors"]), payload["errors"])

    def test_durable_running_claim_requires_heartbeat(self) -> None:
        root = self.make_root("collab-durable-no-heartbeat")
        path = root / "durable.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "durable_persistent_claim",
                "state": "running",
                "claim": "persistent team is running",
                "evidence": {
                    "active_selector": True,
                    "backend_family": "langgraph",
                    "preflight_passed": True,
                    "ownership_plan": True,
                    "team_manifest": True,
                },
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("heartbeat" in error for error in payload["errors"]), payload["errors"])

    def test_expert_result_requires_absorbed_event(self) -> None:
        root = self.make_root("collab-expert-result")
        path = root / "expert.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "expert_lifecycle_audit",
                "total_wait_bound_seconds": 30,
                "events": [
                    {
                        "event": "spawn",
                        "role": "verifier",
                        "task_summary": "check evidence",
                        "scope": ["test evidence"],
                        "non_goals": ["edit files"],
                    },
                    {"event": "wait", "agent_id": "agent-1", "wait_seconds": 30},
                    {"event": "result", "agent_id": "agent-1", "summary": "looks good"},
                ],
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("absorbed" in error for error in payload["errors"]), payload["errors"])

    def test_expert_timeout_must_be_non_evidence(self) -> None:
        root = self.make_root("collab-expert-timeout")
        path = root / "timeout.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "expert_lifecycle_audit",
                "total_wait_bound_seconds": 30,
                "events": [
                    {
                        "event": "spawn",
                        "role": "verifier",
                        "task_summary": "check evidence",
                        "scope": ["test evidence"],
                        "non_goals": ["edit files"],
                    },
                    {"event": "wait", "agent_id": "agent-1", "wait_seconds": 30},
                    {"event": "timeout", "agent_id": "agent-1", "classification": "success"},
                ],
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("non-evidence" in error for error in payload["errors"]), payload["errors"])

    def test_expert_lifecycle_jsonl_evidence_passes(self) -> None:
        root = self.make_root("collab-expert-jsonl")
        path = root / "expert-lifecycle.jsonl"
        events = [
            {
                "event": "spawn",
                "role": "verifier",
                "task_summary": "check evidence",
                "scope": ["test evidence"],
                "non_goals": ["edit files"],
            },
            {"event": "wait", "agent_id": "agent-1", "wait_seconds": 30},
            {"event": "result", "agent_id": "agent-1", "summary": "verified", "changed_paths": []},
            {"event": "absorbed", "agent_id": "agent-1", "leader_decision": "accepted"},
            {"event": "close", "agent_id": "agent-1", "retention_policy": "close"},
        ]
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")

        payload = collab_module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["evidence_format"], "jsonl")

    def test_expert_lifecycle_jsonl_rejects_unsupported_event(self) -> None:
        root = self.make_root("collab-expert-jsonl-unsupported")
        path = root / "expert-lifecycle-unsupported.jsonl"
        events = [
            {
                "event": "spawn",
                "role": "verifier",
                "task_summary": "check evidence",
                "scope": ["test evidence"],
                "non_goals": ["edit files"],
            },
            {"event": "bogus", "agent_id": "agent-1", "summary": "not a lifecycle event"},
        ]
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["evidence_format"], "jsonl")
        self.assertTrue(
            any("unsupported expert lifecycle event" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_expert_lifecycle_jsonl_rejects_missing_required_event_fields(self) -> None:
        root = self.make_root("collab-expert-jsonl-required-fields")
        path = root / "expert-lifecycle-missing-fields.jsonl"
        events = [
            {"event": "spawn", "role": "verifier"},
            {"event": "wait", "agent_id": "agent-1", "wait_seconds": 30},
            {"event": "result", "agent_id": "agent-1", "summary": "verified"},
            {"event": "absorbed", "agent_id": "agent-1", "leader_decision": "accepted"},
            {"event": "close", "agent_id": "agent-1", "retention_policy": "close"},
        ]
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["evidence_format"], "jsonl")
        self.assertTrue(any("task_summary" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("scope" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("non_goals" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("changed_paths" in error for error in payload["errors"]), payload["errors"])

    def test_expert_lifecycle_rejects_invalid_list_field_contents(self) -> None:
        root = self.make_root("collab-expert-invalid-list-values")
        path = root / "expert-lifecycle-invalid-list-values.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "expert_lifecycle_audit",
                "total_wait_bound_seconds": 30,
                "events": [
                    {
                        "event": "spawn",
                        "role": "verifier",
                        "task_summary": "check evidence",
                        "scope": [],
                        "non_goals": [""],
                    },
                    {"event": "wait", "agent_id": "agent-1", "wait_seconds": 30},
                    {"event": "result", "agent_id": "agent-1", "summary": "verified", "changed_paths": [123]},
                    {"event": "absorbed", "agent_id": "agent-1", "leader_decision": "accepted"},
                    {"event": "close", "agent_id": "agent-1", "retention_policy": "close"},
                ],
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["evidence_format"], "json")
        self.assertTrue(any("scope" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("non_goals" in error for error in payload["errors"]), payload["errors"])
        self.assertTrue(any("changed_paths" in error for error in payload["errors"]), payload["errors"])

    def test_langgraph_completed_state_must_release_running(self) -> None:
        root = self.make_root("collab-langgraph-release")
        path = root / "lg.json"
        self.write_json(
            path,
            {
                "schema_version": 1,
                "case_type": "langgraph_state_release",
                "task_completed": True,
                "thread_state": {"status": "running", "completed_at": "2026-05-27T00:00:00Z"},
            },
        )

        payload = collab_module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("status=running" in error for error in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
