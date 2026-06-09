#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools" / "r6_live_runtime.py"
CHECKER = ROOT / "tools" / "check_r6_live_runtime_receipts.py"


class R6LiveRuntimeTests(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        (root / "tools").mkdir()
        return root

    def run_runtime(self, root: Path, *args: str, env: dict[str, str] | None = None, expect: int = 0) -> dict:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        proc = subprocess.run(
            [sys.executable, str(RUNTIME), *args, "--root", str(root), "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=merged_env,
        )
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def run_checker(self, root: Path, receipt: Path, lane: str) -> dict:
        proc = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(root), "--lane", lane, "--receipt", str(receipt), "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def test_default_missing_evidence_writes_blocked_receipt_not_external_action(self) -> None:
        root = self.make_root()
        payload = self.run_runtime(root, "run", "--lane", "wxwork-cli")
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "blocked")
        self.assertFalse(data["live_executed"])
        self.assertIn("target_env_missing:R6_WXWORK_TARGET", data["execution_receipt"]["blockers"])
        self.assertFalse(payload["runs_external_tool"])
        checked = self.run_checker(root, receipt, "wxwork-cli")
        self.assertTrue(checked["receipt_summary"]["r6_live_valid"], checked["errors"])

    def test_repo_local_default_safe_lane_live_executes_without_external_side_effect(self) -> None:
        root = self.make_root()
        payload = self.run_runtime(root, "run", "--lane", "worktree-receipt-claim-lifecycle")
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "live-executed")
        self.assertTrue(data["live_executed"])
        self.assertEqual(data["external_side_effects"], "none")
        self.assertTrue(data["execution_receipt"]["repo_local_default_safe"])
        self.assertFalse(data["execution_receipt"]["external_action_invoked"])
        self.assertFalse(payload["runs_external_tool"])
        checked = self.run_checker(root, receipt, "worktree-receipt-claim-lifecycle")
        self.assertTrue(checked["receipt_summary"]["r6_live_valid"], checked["errors"])

    def test_authorized_default_path_becomes_live_ready_without_side_effect(self) -> None:
        root = self.make_root()
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_BROWSER_TARGET_URL": "https://example.invalid/redacted-target",
            "R6_BROWSER_ACTION": "snapshot",
        }
        payload = self.run_runtime(root, "run", "--lane", "browser-cli-adapter", env=env)
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "live-ready")
        self.assertFalse(data["live_executed"])
        self.assertEqual(data["external_side_effects"], "none")
        output = json.dumps(data, ensure_ascii=False)
        self.assertNotIn("https://example.invalid/redacted-target", output)
        checked = self.run_checker(root, receipt, "browser-cli-adapter")
        self.assertTrue(checked["receipt_summary"]["r6_live_valid"], checked["errors"])

    def test_env_file_live_action_mode_requires_external_proof_receipt(self) -> None:
        root = self.make_root()
        env_file = root / "r6-live.env"
        env_file.write_text(
            "\n".join(
                [
                    "R6_OPERATOR_AUTHORIZED=true",
                    "R6_OWNER_LEASE=true",
                    "R6_ROLLBACK_READY=true",
                    "R6_CLEANUP_READY=true",
                    "R6_BROWSER_TARGET_URL=https://example.invalid/r6-live",
                    "R6_BROWSER_ACTION=snapshot",
                    "R6_WXWORK_TARGET=official-wxwork-target",
                    "R6_WXWORK_MESSAGE_TEMPLATE=official R6 live marker",
                    "R6_HARNESS_CANDIDATE_ID=pi-runtime",
                    "R6_HARNESS_JOB_PROFILE=bounded-read-only",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        for lane in ("browser-cli-adapter", "wxwork-cli", "codex-harnesses"):
            with self.subTest(lane=lane):
                payload = self.run_runtime(root, "run", "--lane", lane, "--mode", "live-action", "--env-file", str(env_file))
                receipt = Path(payload["receipt_out"])
                data = json.loads(receipt.read_text(encoding="utf-8"))
                self.assertEqual(data["live_mode"], "blocked")
                self.assertFalse(data["live_executed"])
                self.assertTrue(any(str(item).startswith("external_execution_proof_missing") for item in data["execution_receipt"]["blockers"]))
                self.assertFalse(payload["starts_browser_or_gui"])
                self.assertFalse(payload["sends_external_message"])
                self.assertFalse(payload["starts_harness_job"])

    def test_live_action_mode_promotes_sensitive_lanes_with_redacted_external_proof(self) -> None:
        root = self.make_root()
        env_file = root / "r6-live.env"
        env_file.write_text(
            "\n".join(
                [
                    "R6_OPERATOR_AUTHORIZED=true",
                    "R6_OWNER_LEASE=true",
                    "R6_ROLLBACK_READY=true",
                    "R6_CLEANUP_READY=true",
                    "R6_BROWSER_TARGET_URL=https://example.invalid/r6-live",
                    "R6_BROWSER_ACTION=snapshot",
                    "R6_WXWORK_TARGET=official-wxwork-target",
                    "R6_WXWORK_MESSAGE_TEMPLATE=official R6 live marker",
                    "R6_HARNESS_CANDIDATE_ID=pi-runtime",
                    "R6_HARNESS_JOB_PROFILE=bounded-read-only",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        proof_dir = root / "proofs"
        proof_dir.mkdir()
        proofs = {
            "browser-cli-adapter": {
                "external_side_effects": "browser_gui",
                "action_performed": True,
                "raw_browser_data_stored": False,
                "browser_action_allowlisted": True,
            },
            "wxwork-cli": {
                "external_side_effects": "external_message",
                "action_performed": True,
                "external_message_sent": True,
                "message_body_hash": "message-hash-fixture",
                "message_body_included": False,
                "recipient_included": False,
            },
            "codex-harnesses": {
                "external_side_effects": "harness_job",
                "action_performed": True,
                "read_guard": {"status": "pass"},
                "write_guard": {"status": "pass"},
                "isolated_worktree": {"status": "pass"},
                "changed_paths_report": {"status": "pass", "paths": []},
                "job_state": {"status": "pass"},
                "no_codex_takeover": True,
                "active_sidecar_took_over_codex": False,
            },
        }
        flags = {
            "browser-cli-adapter": "starts_browser_or_gui",
            "wxwork-cli": "sends_external_message",
            "codex-harnesses": "starts_harness_job",
        }
        for lane, proof in proofs.items():
            with self.subTest(lane=lane):
                proof_path = proof_dir / f"{lane}.json"
                proof_path.write_text(json.dumps(proof, ensure_ascii=False), encoding="utf-8")
                payload = self.run_runtime(root, "run", "--lane", lane, "--mode", "live-action", "--env-file", str(env_file), "--proof-receipt", str(proof_path))
                receipt = Path(payload["receipt_out"])
                data = json.loads(receipt.read_text(encoding="utf-8"))
                self.assertEqual(data["live_mode"], "live-executed")
                self.assertTrue(data["live_executed"])
                self.assertIn("external_execution_proof_hash", data["execution_receipt"])
                self.assertTrue(payload[flags[lane]])
                output = json.dumps(data, ensure_ascii=False)
                self.assertNotIn("official-wxwork-target", output)
                self.assertNotIn("official R6 live marker", output)
                self.assertNotIn("https://example.invalid/r6-live", output)
                self.assertNotIn(str(proof_path), output)
                self.run_checker(root, receipt, lane)

    def test_stop_slop_user_level_install_rejects_native_codex_roots(self) -> None:
        root = self.make_root()
        native_root = root / "AppData" / "Roaming" / "npm"
        native_root.mkdir(parents=True)
        (native_root / "codex.ps1").write_text("# native codex launcher fixture\n", encoding="utf-8")
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_USER_LEVEL_INSTALL_ROOT": str(native_root),
        }
        payload = self.run_runtime(root, "run", "--lane", "stop-slop-caveman", "--mode", "user-level-install", env=env)
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "blocked")
        self.assertFalse(data["live_executed"])
        self.assertIn("install_root_must_not_target_native_codex_surface", data["execution_receipt"]["blockers"])
        self.assertFalse((native_root / "r6-live-runtime").exists())

    def test_spec_kit_sandbox_apply_creates_only_generated_sandbox_and_receipt(self) -> None:
        root = self.make_root()
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_SPEC_KIT_MODE": "sandbox",
            "R6_SPEC_KIT_TARGET_ROOT": str(root / "sandbox-target"),
        }
        payload = self.run_runtime(root, "run", "--lane", "spec-kit-subordinate", "--mode", "spec-kit-apply", env=env)
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "live-executed")
        self.assertEqual(data["execution_receipt"]["spec_kit_apply_mode"], "sandbox")
        self.assertFalse((root / ".specify").exists())
        self.assertFalse((root / "specs").exists())
        self.assertTrue((receipt.parent / "generated-sandbox").exists())
        self.run_checker(root, receipt, "spec-kit-subordinate")

    def test_spec_kit_repository_apply_creates_subordinate_repo_surfaces(self) -> None:
        root = self.make_root()
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_SPEC_KIT_MODE": "repository",
            "R6_SPEC_KIT_TARGET_ROOT": str(root),
        }
        payload = self.run_runtime(root, "run", "--lane", "spec-kit-subordinate", "--mode", "spec-kit-apply", env=env)
        receipt = Path(payload["receipt_out"])
        self.assertTrue((root / ".specify" / "r6-live-runtime" / "README.md").exists())
        self.assertTrue((root / "specs" / "r6-live-runtime" / "spec.md").exists())
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["execution_receipt"]["allowed_repo_surfaces"], [".specify/", "specs/"])
        self.run_checker(root, receipt, "spec-kit-subordinate")

    def test_template_apply_writes_repo_local_full_and_stub_sources(self) -> None:
        root = self.make_root()
        (root / "tools" / "user_level_receipt_governance.py").write_text("# fixture dependency\n", encoding="utf-8")
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_SPEC_KIT_MODE": "template",
            "R6_SPEC_KIT_TARGET_ROOT": str(root / "template-target"),
        }
        payload = self.run_runtime(root, "run", "--lane", "spec-kit-subordinate", "--mode", "spec-kit-apply", env=env)
        receipt = Path(payload["receipt_out"])
        self.assertTrue((root / "tools" / "r6_live_runtime_templates" / "project-general-full" / "README.md").exists())
        self.assertTrue((root / "tools" / "r6_live_runtime_templates" / "project-general-full" / "tools" / "user_level_receipt_governance.py").exists())
        self.assertTrue((root / "tools" / "r6_live_runtime_templates" / "project-general-2-stub" / "README.md").exists())
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["template_distribution"], "project-general-full")
        self.run_checker(root, receipt, "spec-kit-subordinate")

    def test_user_level_install_mode_writes_redacted_smoke_artifact(self) -> None:
        root = self.make_root()
        install_root = root / "user-level"
        env = {
            "R6_OPERATOR_AUTHORIZED": "true",
            "R6_OWNER_LEASE": "true",
            "R6_ROLLBACK_READY": "true",
            "R6_CLEANUP_READY": "true",
            "R6_USER_LEVEL_INSTALL_ROOT": str(install_root),
        }
        payload = self.run_runtime(root, "run", "--lane", "mcp-skills-cli", "--mode", "user-level-install", env=env)
        receipt = Path(payload["receipt_out"])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(data["live_mode"], "live-executed")
        self.assertTrue(data["execution_receipt"]["user_level_state_mutated"])
        self.assertIn("installed_path_hash", data["execution_receipt"])
        self.assertNotIn(str(install_root), json.dumps(data, ensure_ascii=False))
        self.run_checker(root, receipt, "mcp-skills-cli")

    def test_run_all_generates_one_coverage_receipt_per_lane_without_external_side_effects(self) -> None:
        root = self.make_root()
        payload = self.run_runtime(root, "run-all")
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["lanes"], 14)
        self.assertEqual(payload["coverage_summary"]["counts"]["accepted_lanes"], 14)
        self.assertFalse(payload["runs_external_tool"])
        self.assertFalse(payload["starts_browser_or_gui"])
        self.assertFalse(payload["sends_external_message"])
        self.assertFalse(payload["starts_harness_job"])
        receipts = sorted((root / ".omx" / "r6-live-runtime" / "receipts").glob("*.json"))
        self.assertEqual(len(receipts), 14)
        modes = {json.loads(path.read_text(encoding="utf-8"))["lane"]: json.loads(path.read_text(encoding="utf-8"))["live_mode"] for path in receipts}
        self.assertEqual(modes["worktree-receipt-claim-lifecycle"], "live-executed")
        self.assertEqual(modes["user-level-browser-cli-adapter-boundary"], "blocked")
        self.assertEqual(modes["codex-harnesses-governance"], "blocked")

    def test_sync_templates_copies_only_missing_files_to_full_and_stub_targets(self) -> None:
        root = self.make_root()
        general = root / "General"
        general2 = root / "General2"
        general.mkdir()
        general2.mkdir()
        proc = subprocess.run(
            [
                sys.executable,
                str(RUNTIME),
                "sync-templates",
                "--root",
                str(root),
                "--general-root",
                str(general),
                "--general2-root",
                str(general2),
                "--json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["overwrites_existing_files"])
        self.assertTrue((general / "README.md").exists())
        self.assertTrue((general2 / "README.md").exists())

    def test_sync_templates_update_managed_refreshes_existing_template_files(self) -> None:
        root = self.make_root()
        general = root / "General"
        general2 = root / "General2"
        general.mkdir()
        general2.mkdir()
        (general / "README.md").write_text("stale managed template\n", encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(RUNTIME),
                "sync-templates",
                "--root",
                str(root),
                "--general-root",
                str(general),
                "--general2-root",
                str(general2),
                "--update-managed",
                "--json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["overwrites_existing_files"])
        self.assertIn("R6 live runtime template", (general / "README.md").read_text(encoding="utf-8"))

    def test_template_sources_command_is_repo_local_and_declares_sync_targets(self) -> None:
        root = self.make_root()
        payload = self.run_runtime(root, "template-sources")
        self.assertTrue(payload["ok"])
        self.assertTrue((root / "tools" / "r6_live_runtime_templates" / "project-general-full" / "README.md").exists())
        self.assertIn("project-general-2-stub", payload["sync_targets"])


if __name__ == "__main__":
    unittest.main()
