#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "user_level_receipt_governance.py"


def run_cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic path
        raise AssertionError(f"invalid JSON stdout={proc.stdout!r} stderr={proc.stderr!r}") from exc
    return proc.returncode, payload


class UserLevelReceiptGovernanceTests(unittest.TestCase):
    def write_json(self, directory: Path, name: str, payload: dict) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_authorization_receipt_requires_all_fields_and_future_expiry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(Path(tmp), "auth.json", {"action": "mcp.call"})
            code, payload = run_cli(
                "auth-check",
                "--receipt",
                str(receipt),
                "--action",
                "mcp.call",
                "--target",
                "mcp:cloudflare",
                "--session",
                "session-a",
            )

        self.assertEqual(code, 3)
        self.assertFalse(payload["ok"])
        self.assertIn("authorization_receipt_missing_target", payload["blockers"])
        self.assertIn("authorization_receipt_operator_confirmation_not_true", payload["blockers"])
        self.assertFalse(payload["mutates_user_level_state"])

    def test_valid_authorization_receipt_is_summarized_without_raw_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = str(Path(tmp) / "auth.json")
            receipt = self.write_json(
                Path(tmp),
                "auth.json",
                {
                    "action": "browser.click",
                    "target": "tab:123",
                    "scope": ["browser.click"],
                    "expiry": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                    "session": "session-a",
                    "operator_confirmation": True,
                },
            )
            code, payload = run_cli(
                "auth-check",
                "--receipt",
                str(receipt),
                "--action",
                "browser.click",
                "--target",
                "tab:123",
                "--session",
                "session-a",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["authorization_valid"])
        self.assertIn("receipt_path_hash", payload["authorization_summary"])
        self.assertNotIn(raw_path, output)
        self.assertFalse(payload["contains_raw_private_paths_in_output"])

    def test_update_receipt_requires_rollback_and_smoke_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "skills2cli",
                    "installed_version": "abc123",
                    "source_url": "https://example.invalid/repo.git",
                    "install_path": r"C:\Users\lenovo\.codex\tools\skills2cli",
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\skills2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\skills2cli",
                    "smoke_test_command": "skills2cli index --json",
                    "smoke_test_result": {"status": "fail"},
                    "updater_command": "skills2cli-update --pin abc123",
                    "owner_lane": "skills2cli",
                    "redaction_status": "pass",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "skills2cli",
                "--owner-lane",
                "skills2cli",
            )

        self.assertEqual(code, 3)
        self.assertFalse(payload["update_receipt_valid"])
        self.assertIn("update_receipt_missing_rollback_pointer", payload["blockers"])
        self.assertIn("update_receipt_smoke_test_result_must_pass", payload["blockers"])

    def test_valid_update_receipt_hashes_private_paths_and_rollback_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "mcp2cli",
                    "installed_version": "v1.0.0",
                    "source_url": "https://example.invalid/mcp2cli.git",
                    "install_path": r"C:\Users\lenovo\.codex\tools\mcp2cli",
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\mcp2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\mcp2cli",
                    "smoke_test_command": "mcp2cli list --json",
                    "smoke_test_result": {"status": "pass"},
                    "updater_command": "mcp2cli-update --pin v1.0.0",
                    "rollback_pointer": r"C:\Users\lenovo\.codex\backup\mcp2cli-prev",
                    "owner_lane": "mcp2cli",
                    "redaction_status": "no_secrets",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "mcp2cli",
                "--owner-lane",
                "mcp2cli",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["rollback_ready"])
        self.assertIn("install_path_hash", payload["update_summary"])
        self.assertIn("rollback_pointer_hash", payload["update_summary"])
        self.assertNotIn(r"C:\Users\lenovo\.codex\tools\mcp2cli", output)
        self.assertNotIn(r"C:\Users\lenovo\.codex\backup\mcp2cli-prev", output)

    def test_update_receipt_local_path_evidence_requires_explicit_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_install_path = r"C:\Users\lenovo\.codex\tools\mcp2cli"
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "mcp2cli",
                    "installed_version": "v1.0.0",
                    "source_url": "https://example.invalid/mcp2cli.git",
                    "install_path": raw_install_path,
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\mcp2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\mcp2cli",
                    "smoke_test_command": "mcp2cli list --json",
                    "smoke_test_result": {"status": "pass"},
                    "updater_command": "mcp2cli-update --pin v1.0.0",
                    "rollback_pointer": r"C:\Users\lenovo\.codex\backup\mcp2cli-prev",
                    "owner_lane": "mcp2cli",
                    "redaction_status": "no_secrets",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "mcp2cli",
                "--owner-lane",
                "mcp2cli",
                "--include-local-path-evidence",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 3)
        self.assertIn("local_path_evidence_requires_explicit_authorization", payload["blockers"])
        self.assertFalse(payload["contains_raw_private_paths_in_output"])
        self.assertNotIn(raw_install_path, output)

    def test_update_receipt_local_path_evidence_can_be_explicitly_authorized_for_local_only_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_install_path = r"C:\Users\lenovo\.codex\tools\mcp2cli"
            raw_rollback_pointer = r"C:\Users\lenovo\.codex\backup\mcp2cli-prev"
            receipt = self.write_json(
                Path(tmp),
                "update.json",
                {
                    "tool_name": "mcp2cli",
                    "installed_version": "v1.0.0",
                    "source_url": "https://example.invalid/mcp2cli.git",
                    "install_path": raw_install_path,
                    "wrapper_path": r"C:\Users\lenovo\.codex\bin\mcp2cli.cmd",
                    "state_path": r"C:\Users\lenovo\.codex\state\mcp2cli",
                    "smoke_test_command": "mcp2cli list --json",
                    "smoke_test_result": {"status": "pass"},
                    "updater_command": "mcp2cli-update --pin v1.0.0",
                    "rollback_pointer": raw_rollback_pointer,
                    "owner_lane": "mcp2cli",
                    "redaction_status": "no_secrets",
                },
            )
            code, payload = run_cli(
                "update-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "mcp2cli",
                "--owner-lane",
                "mcp2cli",
                "--include-local-path-evidence",
                "--local-evidence-authorized",
            )

        self.assertEqual(code, 0)
        self.assertEqual(payload["local_path_evidence_scope"], "local-only")
        self.assertTrue(payload["local_path_evidence_authorized"])
        self.assertTrue(payload["contains_raw_private_paths_in_output"])
        self.assertEqual(payload["local_path_evidence"]["install_path"], raw_install_path)
        self.assertEqual(payload["local_path_evidence"]["rollback_pointer"], raw_rollback_pointer)

    def test_r6_live_template_and_check_delegate_to_r6_checker(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import check_r6_live_runtime_receipts as r6

        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "r6.json",
                r6.fixture_for_lane("wxwork-cli", live_mode="blocked"),
            )
            code, payload = run_cli(
                "r6-live-check",
                "--receipt",
                str(receipt),
                "--lane",
                "wxwork-cli",
            )
            template_code, template_payload = run_cli("template", "--kind", "r6-live")

        self.assertEqual(code, 0)
        self.assertTrue(payload["r6_live_valid"], payload["blockers"])
        self.assertEqual(payload["runtime_stage"], "R6")
        self.assertIn("live_mode", template_payload["required_fields"])
        self.assertEqual(template_code, 0)

    def test_redaction_check_blocks_raw_sensitive_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "bad.json",
                {
                    "tool_name": "browser",
                    "cookies": "sessionid=abc",
                    "plugin_description_dump": "large raw plugin description",
                    "message_contents": "raw WeCom message body",
                    "note": "token=raw-value",
                },
            )
            code, payload = run_cli("redact-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        self.assertFalse(payload["redaction_valid"])
        self.assertGreaterEqual(payload["finding_count"], 4)
        self.assertIn("cookies", json.dumps(payload["blockers"]))
        self.assertFalse(payload["reads_browser_data"])

    def test_valid_r4_smoke_receipt_hashes_runtime_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_install_receipt = r"C:\Users\lenovo\.codex\state\mcp2cli\install.json"
            raw_rollback_pointer = r"C:\Users\lenovo\.codex\backup\mcp2cli-prev"
            receipt = self.write_json(
                Path(tmp),
                "smoke.json",
                {
                    "tool_name": "mcp2cli",
                    "owner_lane": "mcp2cli",
                    "runtime_stage": "smoke-tested",
                    "install_receipt": raw_install_receipt,
                    "smoke_command": "mcp2cli --help",
                    "smoke_type": "help",
                    "smoke_result": {"status": "pass"},
                    "timeout_release": {"status": "pass", "released": True},
                    "rollback_pointer": raw_rollback_pointer,
                    "rollback_ready": True,
                    "command_transcript": "mcp2cli help output from local wrapper",
                    "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "abc123"},
                    "redaction_status": "no_secrets",
                    "write_performed": False,
                    "live_action_performed": False,
                    "sensitive_action_performed": False,
                    "user_level_state_mutated": False,
                    "reads_browser_data": False,
                    "external_message_sent": False,
                },
            )
            code, payload = run_cli("smoke-check", "--receipt", str(receipt))
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["smoke_receipt_valid"])
        self.assertEqual(payload["smoke_summary"]["runtime_stage"], "R4")
        self.assertTrue(payload["rollback_ready"])
        self.assertFalse(payload["runs_external_tool"])
        self.assertFalse(payload["mutates_user_level_state"])
        self.assertIn("install_receipt_hash", payload["smoke_summary"])
        self.assertIn("rollback_pointer_hash", payload["smoke_summary"])
        self.assertNotIn(raw_install_receipt, output)
        self.assertNotIn(raw_rollback_pointer, output)

    def test_r4_smoke_receipt_blocks_write_live_or_sensitive_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "bad-smoke.json",
                {
                    "tool_name": "WXWork_CLI",
                    "owner_lane": "wxwork-cli",
                    "runtime_stage": "R4",
                    "install_receipt": "install-receipt-ref",
                    "smoke_command": "WXWork_CLI send --to user --message hi",
                    "smoke_type": "send",
                    "smoke_result": {"status": "pass"},
                    "timeout_release": {"status": "pass", "released": True},
                    "rollback_pointer": "rollback-ref",
                    "rollback_ready": True,
                    "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "abc123"},
                    "redaction_status": "pass",
                    "write_performed": True,
                    "live_action_performed": True,
                    "sensitive_action_performed": True,
                },
            )
            code, payload = run_cli("smoke-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        self.assertFalse(payload["smoke_receipt_valid"])
        self.assertIn("smoke_receipt_smoke_type_not_read_only", payload["blockers"])
        self.assertIn("smoke_receipt_forbidden_write_performed", payload["blockers"])
        self.assertIn("smoke_receipt_forbidden_live_action_performed", payload["blockers"])
        self.assertIn("smoke_receipt_forbidden_sensitive_action_performed", payload["blockers"])


    def test_valid_r5_active_candidate_receipt_requires_authorization_lease_allowlist_and_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "active.json",
                {
                    "tool_name": "durable-smoke",
                    "owner_lane": "durable-smoke-adoption-gate",
                    "runtime_stage": "active-candidate",
                    "action": "durable.adopt.apply",
                    "target": "repo:D:/PythonProject_langgraph",
                    "authorization_receipt": {
                        "status": "pass",
                        "operator_confirmation": True,
                        "scope": ["durable.adopt.apply"],
                        "expiry": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                        "authorized_by": "main_session",
                    },
                    "owner_lease": {"status": "pass", "owner": "main-session", "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()},
                    "target_action_allowlist": {"targets": ["repo:D:/PythonProject_langgraph"], "actions": ["durable.adopt.apply"]},
                    "command_transcript": "bounded active candidate transcript",
                    "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "abc123"},
                    "redaction_status": "no_secrets",
                    "timeout_release": {"status": "pass", "released": True},
                    "rollback_pointer": r"C:\Users\lenovo\.codex\backup\durable-smoke-prev",
                    "rollback_ready": True,
                    "cleanup_evidence": {"status": "pass", "cleaned": True},
                    "remote_publication_mutated": False,
                    "user_level_state_mutated": False,
                    "authority_decision": {
                        "priority_order": "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit",
                        "decision": "allowed-subordinate",
                    },
                },
            )
            code, payload = run_cli(
                "active-check",
                "--receipt",
                str(receipt),
                "--tool-name",
                "durable-smoke",
                "--owner-lane",
                "durable-smoke-adoption-gate",
            )
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["active_candidate_valid"])
        self.assertEqual(payload["runtime_stage"], "R5")
        self.assertTrue(payload["authorization_valid"])
        self.assertTrue(payload["owner_lease_valid"])
        self.assertTrue(payload["allowlist_valid"])
        self.assertFalse(payload["remote_publication_mutated"])
        self.assertIn("rollback_pointer_hash", payload["active_candidate_summary"])
        self.assertNotIn(r"C:\Users\lenovo\.codex\backup\durable-smoke-prev", output)

    def test_blocked_r5_receipt_is_not_positive_active_candidate_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "blocked-active.json",
                {
                    "tool_name": "browser-cli-adapter",
                    "owner_lane": "browser-cli-adapter:chrome-devtools-mcp",
                    "runtime_stage": "blocked",
                    "blocked_reason": "blocked:operator_authorization_missing",
                    "authorization_receipt": {"status": "blocked", "operator_confirmation": False},
                    "remote_publication_mutated": False,
                },
            )
            code, payload = run_cli("active-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        self.assertFalse(payload["active_candidate_valid"])
        self.assertEqual(payload["runtime_stage"], "blocked")
        self.assertIn("active_candidate_runtime_stage_must_be_r5", payload["blockers"])
        self.assertIn("active_candidate_authorization_receipt_must_pass", payload["blockers"])


    def test_r4_smoke_receipt_blocks_active_candidate_or_adoption_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "bad-r4-adoption.json",
                {
                    "tool_name": "durable-smoke",
                    "owner_lane": "durable-smoke-adoption-gate",
                    "runtime_stage": "R4",
                    "install_receipt": "install-receipt-ref",
                    "smoke_command": "python tools/check_durable_routing_smoke_gate_template.py --json",
                    "smoke_type": "status",
                    "smoke_result": {"status": "pass"},
                    "timeout_release": {"status": "pass", "released": True},
                    "rollback_pointer": "rollback-ref",
                    "rollback_ready": True,
                    "command_transcript": "read only smoke",
                    "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "abc123"},
                    "redaction_status": "pass",
                    "active_candidate": True,
                    "runtime_adoption": True,
                    "adoption_performed": True,
                    "durable_workflow_selected": True,
                    "durable_workflow_running": True,
                    "durable_workflow_adopted": True,
                },
            )
            code, payload = run_cli("smoke-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        for field in (
            "active_candidate",
            "runtime_adoption",
            "adoption_performed",
            "durable_workflow_selected",
            "durable_workflow_running",
            "durable_workflow_adopted",
        ):
            self.assertIn(f"smoke_receipt_forbidden_{field}", payload["blockers"])

    def test_rollback_apply_receipt_requires_operator_authorization_without_executing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.write_json(
                Path(tmp),
                "rollback.json",
                {
                    "rollback_target": "mcp2cli",
                    "rollback_pointer": r"C:\Users\lenovo\.codex\backup\mcp2cli-prev",
                    "rollback_mode": "apply",
                    "restore_command": "restore-mcp2cli --from backup",
                    "dry_run_result": {"status": "pass"},
                    "apply_result": {"status": "pass"},
                    "post_rollback_verification": {"status": "pass"},
                    "owner_lane": "mcp2cli",
                    "operator_authorization": False,
                    "redaction_status": "pass",
                },
            )
            code, payload = run_cli("rollback-check", "--receipt", str(receipt))

        self.assertEqual(code, 3)
        self.assertFalse(payload["rollback_receipt_valid"])
        self.assertFalse(payload["rollback_performed"])
        self.assertIn("rollback_receipt_apply_requires_operator_authorization", payload["blockers"])
        self.assertFalse(payload["runs_external_tool"])

    def test_valid_rollback_dry_run_receipt_hashes_restore_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_rollback_pointer = r"C:\Users\lenovo\.codex\backup\skills2cli-prev"
            raw_restore_command = r"C:\Users\lenovo\.codex\bin\restore-skills2cli.cmd --dry-run"
            receipt = self.write_json(
                Path(tmp),
                "rollback-dry-run.json",
                {
                    "rollback_target": "skills2cli",
                    "rollback_pointer": raw_rollback_pointer,
                    "rollback_mode": "dry-run",
                    "restore_command": raw_restore_command,
                    "dry_run_result": {"status": "pass"},
                    "post_rollback_verification": {"status": "pass"},
                    "owner_lane": "skills2cli",
                    "operator_authorization": False,
                    "redaction_status": "no_secrets",
                },
            )
            code, payload = run_cli("rollback-check", "--receipt", str(receipt))
            output = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(code, 0)
        self.assertTrue(payload["rollback_receipt_valid"])
        self.assertFalse(payload["rollback_performed"])
        self.assertEqual(payload["rollback_summary"]["rollback_mode"], "dry-run")
        self.assertIn("rollback_pointer_hash", payload["rollback_summary"])
        self.assertIn("restore_command_hash", payload["rollback_summary"])
        self.assertNotIn(raw_rollback_pointer, output)
        self.assertNotIn(raw_restore_command, output)

    def test_templates_expose_required_fields(self) -> None:
        code, payload = run_cli("template", "--kind", "update")
        self.assertEqual(code, 0)
        self.assertIn("rollback_pointer", payload["required_fields"])
        self.assertIn("redaction_status", payload["required_fields"])

        code, payload = run_cli("template", "--kind", "smoke")
        self.assertEqual(code, 0)
        self.assertIn("runtime_stage", payload["required_fields"])
        self.assertIn("timeout_release", payload["required_fields"])

        code, payload = run_cli("template", "--kind", "active")
        self.assertEqual(code, 0)
        self.assertIn("authorization_receipt", payload["required_fields"])
        self.assertIn("owner_lease", payload["required_fields"])
        self.assertIn("target_action_allowlist", payload["required_fields"])

        code, payload = run_cli("template", "--kind", "rollback")
        self.assertEqual(code, 0)
        self.assertIn("rollback_mode", payload["required_fields"])
        self.assertIn("post_rollback_verification", payload["required_fields"])


if __name__ == "__main__":
    unittest.main()
