#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_durable_routing_smoke.py"
CHECKER = ROOT / "tools" / "check_durable_routing_smoke_receipts.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("run_durable_routing_smoke", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load durable routing smoke runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


class DurableRoutingSmokeReceiptTests(unittest.TestCase):
    maxDiff = None

    def write_json(self, directory: Path, name: str, payload: dict) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def valid_receipt(self) -> dict:
        return {
            "schema_version": 1,
            "receipt_type": "durable-routing-smoke",
            "runtime_stage": "R4",
            "stage": "smoke-tested",
            "target_repository_hash": "repo-hash",
            "phase": "verify-accept",
            "task": "receipt fixture",
            "operator_consent_boundary": "read-only smoke receipt only",
            "routing_mode": "read_only",
            "mutation_allowed": False,
            "read_only": True,
            "state_write_policy": "receipt_only",
            "validation_path": ["checker"],
            "rollback_path": ["git revert"],
            "smoke_command": ["python", "tools/check_durable_routing_smoke_gate_template.py", "--json"],
            "smoke_command_hash": "hash",
            "smoke_result": {"status": "pass", "exit_code": 0, "timed_out": False},
            "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30, "timed_out": False},
            "rollback_pointer": {"type": "git-head", "commit_hash": "deadbeef", "status": "ready"},
            "rollback_ready": True,
            "command_transcript": {
                "stdout_excerpt": "{}",
                "stderr_excerpt": "",
                "stdout_hash": "stdout-hash",
                "stderr_hash": "stderr-hash",
                "max_excerpt_chars": 4000,
                "raw_transcript_omitted": True,
            },
            "transcript_redaction": {
                "status": "pass",
                "redacted_transcript_hash": "redacted-hash",
                "raw_private_paths_redacted": True,
                "raw_secrets_redacted": True,
                "raw_transcript_omitted": True,
            },
            "command_safety": {
                "safe_local_command": True,
                "blockers": [],
                "forbidden_apply_markers_detected": False,
                "runs_external_tool": False,
            },
            "backend_family_evidence": {
                "candidate_backend_family": "langgraph",
                "observed_backend_family": "none",
                "adoption_state": "not_adopted",
                "adoption_claimed": False,
                "native_omx_launched": False,
                "langgraph_thread_started": False,
            },
            "adoption_performed": False,
            "durable_workflow_selected": False,
            "durable_workflow_running": False,
            "durable_workflow_adopted": False,
            "user_level_state_mutated": False,
            "durable_state_mutated": False,
            "durable_team_launched": False,
            "omx_apply_performed": False,
            "langgraph_thread_started": False,
            "remote_publication_authorized": False,
            "redaction_status": "pass",
        }

    def test_checker_self_test_covers_negative_adoption_and_transcript_fixtures(self) -> None:
        result = run_command([str(CHECKER), "--root", str(ROOT), "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["negative_self_test_fixtures"], 3)
        fixture_names = {item["name"] for item in payload["self_test"]["fixtures"]}
        self.assertIn("adoption_claim", fixture_names)
        self.assertIn("unbounded_transcript", fixture_names)

    def test_valid_receipt_passes_without_adoption_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "receipt.json", self.valid_receipt())
            result = run_command([str(CHECKER), "--root", str(ROOT), "--receipt", str(receipt), "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["receipt_summary"]["runtime_stage"], "R4")
        self.assertFalse(payload["receipt_summary"]["adoption_performed"])
        self.assertFalse(payload["mutates_user_level_state"])
        self.assertFalse(payload["launches_durable_team"])
        self.assertFalse(payload["runs_omx_apply"])
        self.assertFalse(payload["starts_langgraph_thread"])

    def test_adoption_claim_fails_closed(self) -> None:
        receipt_payload = self.valid_receipt()
        receipt_payload["adoption_performed"] = True
        receipt_payload["durable_workflow_selected"] = True
        receipt_payload["backend_family_evidence"]["adoption_state"] = "running"
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "receipt.json", receipt_payload)
            result = run_command([str(CHECKER), "--root", str(ROOT), "--receipt", str(receipt), "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("receipt_adoption_performed_must_be_false", payload["errors"])
        self.assertIn("receipt_durable_workflow_selected_must_be_false", payload["errors"])
        self.assertIn("receipt_backend_evidence_must_not_claim_adoption", payload["errors"])

    def test_unbounded_or_raw_transcript_fails_closed(self) -> None:
        receipt_payload = self.valid_receipt()
        receipt_payload["command_transcript"]["max_excerpt_chars"] = 999999
        receipt_payload["command_transcript"]["raw_transcript_omitted"] = False
        receipt_payload["command_transcript"]["raw_transcript"] = "secret=abc123"
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "receipt.json", receipt_payload)
            result = run_command([str(CHECKER), "--root", str(ROOT), "--receipt", str(receipt), "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertIn("receipt_transcript_max_excerpt_chars_must_be_bounded", payload["errors"])
        self.assertIn("receipt_command_transcript_raw_must_be_omitted", payload["errors"])
        self.assertTrue(any("raw_transcript" in error for error in payload["errors"]), payload["errors"])

    def test_runner_writes_receipt_and_checker_accepts_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "durable-routing-smoke.json"
            run_result = run_command([
                str(RUNNER),
                "--root", str(ROOT),
                "--receipt", str(receipt),
                "--phase", "verify-accept",
                "--task", "test durable smoke",
                "--candidate-backend-family", "langgraph",
                "--json",
            ])
            self.assertEqual(run_result.returncode, 0, run_result.stdout + run_result.stderr)
            run_payload = json.loads(run_result.stdout)
            self.assertTrue(run_payload["ok"])
            self.assertFalse(run_payload["adoption_performed"])
            self.assertFalse(run_payload["mutation_allowed"])
            self.assertFalse(run_payload["durable_team_launched"])
            self.assertFalse(run_payload["omx_apply_performed"])
            self.assertFalse(run_payload["langgraph_thread_started"])
            self.assertTrue(receipt.exists())
            check_result = run_command([str(CHECKER), "--root", str(ROOT), "--receipt", str(receipt), "--json"])
        check_payload = json.loads(check_result.stdout)
        self.assertEqual(check_result.returncode, 0, check_result.stdout + check_result.stderr)
        self.assertTrue(check_payload["ok"], check_payload["errors"])
        self.assertEqual(check_payload["receipt_summary"]["candidate_backend_family"], "langgraph")
        self.assertEqual(check_payload["receipt_summary"]["adoption_state"], "not_adopted")

    def test_runner_rejects_apply_command_and_still_records_non_adoption_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "bad-command-receipt.json"
            result = run_command([
                str(RUNNER),
                "--root", str(ROOT),
                "--receipt", str(receipt),
                "--json",
                "--command", sys.executable, "tools/check_durable_routing_smoke_gate_template.py", "--apply",
            ])
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("command_apply_flag_forbidden", payload["safe_command_blockers"])
            receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertFalse(receipt_payload["adoption_performed"])
        self.assertFalse(receipt_payload["mutation_allowed"])
        self.assertFalse(receipt_payload["durable_team_launched"])
        self.assertFalse(receipt_payload["omx_apply_performed"])
        self.assertFalse(receipt_payload["langgraph_thread_started"])

    def test_safe_command_allows_apply_suffix_in_paths_but_rejects_apply_flags(self) -> None:
        runner = load_runner_module()
        with tempfile.TemporaryDirectory(prefix="durable-smoke-apply-") as tmp:
            root = Path(tmp) / "fixture-apply"
            command = [
                sys.executable,
                str(root / "tools" / "check_fixture.py"),
                "--dry-run-apply",
            ]
            self.assertEqual(runner.validate_safe_command(command, root), [])
            for apply_flag in ("--apply", "-Apply", "/apply", "--apply=true"):
                flagged = command[:-1] + [apply_flag]
                self.assertIn("command_apply_flag_forbidden", runner.validate_safe_command(flagged, root))

    def valid_active_candidate_receipt(self) -> dict:
        return {
            "schema_version": 1,
            "receipt_type": "durable-routing-adoption",
            "tool_name": "durable-routing-adoption",
            "owner_lane": "durable-smoke-adoption-gate",
            "runtime_stage": "active-candidate",
            "action": "durable.adopt.apply",
            "target": "repo:D:/PythonProject_langgraph",
            "backend_family": "langgraph",
            "adoption_decision": "selected",
            "selector_source": ".omx/state/selectors/active.json",
            "authorization_receipt": {
                "status": "pass",
                "action": "durable.adopt.apply",
                "target": "repo:D:/PythonProject_langgraph",
                "scope": ["durable.adopt.apply"],
                "expiry": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                "session": "main-session",
                "operator_confirmation": True,
            },
            "owner_lease": {
                "status": "pass",
                "owner": "main-session",
                "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            },
            "target_action_allowlist": {
                "targets": ["repo:D:/PythonProject_langgraph"],
                "actions": ["durable.adopt.apply"],
            },
            "command_transcript": {"stdout_excerpt": "selected only", "stderr_excerpt": ""},
            "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "redacted"},
            "redaction_status": "pass",
            "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30},
            "rollback_pointer": "rollback-ref",
            "rollback_ready": True,
            "cleanup_evidence": {"status": "pass", "cleaned": True},
            "remote_publication_mutated": False,
            "authority_decision": {
                "decision": "selected",
                "priority_order": "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
            },
        }

    def test_r5_active_candidate_receipt_passes_apply_gate_without_remote_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "active.json", self.valid_active_candidate_receipt())
            result = run_command([
                str(CHECKER),
                "--root", str(ROOT),
                "--active-candidate-receipt", str(receipt),
                "--json",
            ])
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(payload["r5_apply_gate"]["active_candidate_valid"], payload["errors"])
        self.assertEqual(payload["r5_apply_gate"]["backend_family"], "langgraph")
        self.assertFalse(payload["r5_apply_gate"]["remote_publication_mutated"])
        self.assertFalse(payload["mutates_user_level_state"])

    def test_r5_active_candidate_receipt_rejects_remote_mutation(self) -> None:
        payload = self.valid_active_candidate_receipt()
        payload["remote_publication_mutated"] = True
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "bad-active.json", payload)
            result = run_command([
                str(CHECKER),
                "--root", str(ROOT),
                "--active-candidate-receipt", str(receipt),
                "--json",
            ])
        checked = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(checked["r5_apply_gate"]["active_candidate_valid"])
        self.assertIn("active_candidate_remote_publication_must_not_mutate", checked["errors"])


if __name__ == "__main__":
    unittest.main()
