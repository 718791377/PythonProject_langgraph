from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "cli_anything_governance.py"


def run_cli_anything(args: list[str], *, expect: int = 0) -> tuple[dict, str]:
    cmd = [sys.executable, str(SCRIPT), *args, "--json"]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data, proc.stdout


class CLIAnythingGovernanceTests(unittest.TestCase):
    def test_install_record_writes_pinned_receipt_with_sanitized_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            install_path = root / "external" / "cli-anything"
            wrapper_path = root / "tools" / "cli-anything" / "cli-anything.cmd"
            state_path = root / "state" / "cli-anything"
            result, stdout = run_cli_anything([
                "install-record",
                "--receipt-dir", str(receipt_dir),
                "--pin", "v0.1.0",
                "--install-path", str(install_path),
                "--wrapper-path", str(wrapper_path),
                "--state-path", str(state_path),
                "--smoke-command", "cli-anything --help",
                "--rollback-pointer", "remove-created-cli-anything-directories",
            ])
            self.assertTrue(result["ok"])
            self.assertTrue(result["receipt_written"])
            self.assertEqual(result["summary"]["tool_name"], "CLI-Anything")
            self.assertEqual(result["summary"]["owner_lane"], "cli-anything")
            self.assertEqual(result["summary"]["status"], "reference-only")
            self.assertEqual(result["summary"]["pinned_ref"], "v0.1.0")
            self.assertTrue(result["summary"]["adapter_generation_only"])
            self.assertFalse(result["summary"]["hard_loads_skills"])
            self.assertFalse(result["safety"]["installs_cli_anything"])
            self.assertFalse(result["safety"]["hard_loads_skills"])
            self.assertTrue(result["safety"]["adapter_generation_boundary_only"])
            self.assertNotIn(str(root), stdout)
            self.assertNotIn(str(install_path), stdout)
            receipt = receipt_dir / "cli-anything.lock.json"
            self.assertTrue(receipt.exists())

            validated, _ = run_cli_anything(["validate", "--receipt", str(receipt)])
            self.assertTrue(validated["ok"])
            self.assertTrue(validated["receipt_valid"])

    def test_hard_load_skills_is_blocked_without_writing_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            result, _ = run_cli_anything([
                "install-record",
                "--receipt-dir", str(receipt_dir),
                "--pin", "v0.1.0",
                "--install-path", str(root / "external" / "cli-anything"),
                "--wrapper-path", str(root / "tools" / "cli-anything.cmd"),
                "--state-path", str(root / "state" / "cli-anything"),
                "--smoke-command", "cli-anything --help",
                "--rollback-pointer", "previous-version",
                "--hard-load-skills",
            ], expect=3)
            self.assertFalse(result["ok"])
            self.assertFalse(result["receipt_written"])
            self.assertIn("hard_load_skills_must_be_false", result["blockers"])
            self.assertFalse((receipt_dir / "cli-anything.lock.json").exists())

    def test_update_requires_smoke_pass_and_preserves_rollback_pin(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            run_cli_anything([
                "install-record",
                "--receipt-dir", str(receipt_dir),
                "--pin", "v0.1.0",
                "--install-path", str(root / "external" / "cli-anything"),
                "--wrapper-path", str(root / "tools" / "cli-anything.cmd"),
                "--state-path", str(root / "state" / "cli-anything"),
                "--smoke-command", "cli-anything --help",
                "--rollback-pointer", "remove-created-cli-anything-directories",
            ])
            current = receipt_dir / "cli-anything.lock.json"

            blocked, _ = run_cli_anything([
                "update-plan",
                "--current-receipt", str(current),
                "--new-pin", "v0.1.1",
                "--staging-dir", str(root / "staging" / "cli-anything"),
                "--smoke-status", "fail",
            ], expect=3)
            self.assertFalse(blocked["pin_switch_allowed"])
            self.assertIn("smoke_result_not_passed", blocked["blockers"])
            self.assertFalse(blocked["safety"]["network_fetch_performed"])

            updated, stdout = run_cli_anything([
                "update-record",
                "--current-receipt", str(current),
                "--receipt-dir", str(receipt_dir),
                "--new-pin", "v0.1.1",
                "--staging-dir", str(root / "staging" / "cli-anything"),
                "--smoke-command", "cli-anything --help",
                "--smoke-status", "pass",
            ])
            self.assertTrue(updated["pin_switch_allowed"])
            self.assertEqual(updated["rollback_pointer"]["previous_pin"], "v0.1.0")
            self.assertNotIn(str(root), stdout)

            update_files = sorted(receipt_dir.glob("cli-anything.update.*.json"))
            self.assertEqual(len(update_files), 1)
            rollback, _ = run_cli_anything(["rollback-plan", "--receipt", str(update_files[0])])
            self.assertTrue(rollback["rollback_allowed"])
            self.assertFalse(rollback["rollback_performed"])
            self.assertTrue(rollback["requires_operator_execution"])
            self.assertEqual(rollback["rollback_pointer"]["previous_pin"], "v0.1.0")

    def test_adapter_plan_is_generation_only_and_blocks_hard_load(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            allowed, stdout = run_cli_anything([
                "adapter-plan",
                "--capability", "design WXWork_CLI process inventory without reading message content",
                "--output-dir", str(root / "generated" / "wxwork-cli"),
                "--target-process", "WXWork.exe",
            ])
            self.assertTrue(allowed["ok"])
            self.assertTrue(allowed["adapter_generation_allowed"])
            self.assertTrue(allowed["repo_local_source_required"])
            self.assertEqual(allowed["wxwork_cli_control_surface"], "WXWork_CLI")
            self.assertTrue(allowed["authorization_gate_required_for_live_control"])
            self.assertFalse(allowed["safety"]["runs_cli_anything"])
            self.assertFalse(allowed["safety"]["hard_loads_skills"])
            self.assertNotIn(str(root), stdout)
            self.assertNotIn("harness", stdout.lower())

            blocked, _ = run_cli_anything([
                "adapter-plan",
                "--capability", "bulk-load skills into CLI-Anything",
                "--output-dir", str(root / "generated"),
                "--hard-load-skills",
            ], expect=3)
            self.assertFalse(blocked["adapter_generation_allowed"])
            self.assertIn("hard_load_skills_must_be_false", blocked["blockers"])


if __name__ == "__main__":
    unittest.main()
