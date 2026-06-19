#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools" / "reference8_capability_install.py"
REF6_RUNTIME = ROOT / "tools" / "reference6_capability_install.py"
CHECKER = ROOT / "tools" / "check_reference8_capability_install.py"


class Reference8CapabilityInstallTests(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        base = ROOT / ".omx" / "test-artifacts" / f"reference8-{name}-{uuid.uuid4().hex[:8]}"
        base.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return base

    def run_json(self, script: Path, *args: str, check: bool = True) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(script), *args, "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
        if check and proc.returncode != 0:
            self.fail(json.dumps(payload, ensure_ascii=False, indent=2) + "\n" + proc.stderr)
        return proc.returncode, payload

    def test_plan_exposes_16_capabilities_layers_and_adapter_policy(self) -> None:
        code, payload = self.run_json(RUNTIME, "plan")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability_count"], 16)
        self.assertEqual(payload["layer_counts"], {"user_level": 8, "project_template_general": 5, "project_template_general_2": 3})
        self.assertEqual(payload["generated_policy"]["browserbase_policy"], "disabled_by_user_not_part_of_reference8")
        ids = {item["id"] for item in payload["capabilities"]}
        self.assertIn("open-design-ref8", ids)
        self.assertIn("agency-agents-zh", ids)
        for item in payload["capabilities"]:
            self.assertTrue(item["requires_codex_adapter_before_live_executed"])
            self.assertFalse(item["raw_upstream_live_executed_allowed"])
            self.assertIn("adapter_kind", item)
            self.assertIn("live_runtime_target", item)
            self.assertIn("live_smoke_kind", item)
        self.assertEqual(payload["codex_provider_env"]["reuse_mode"], "env_key_name_only")
        self.assertFalse(payload["codex_provider_env"]["copy_secret_values"])
        self.assertFalse(payload["codex_config_toml_mutated"])

    def test_apply_requires_explicit_flag_and_operator_confirmation(self) -> None:
        code, payload = self.run_json(RUNTIME, "apply", check=False)
        self.assertEqual(code, 3)
        self.assertIn("apply_flag_required", payload["blockers"])
        home = self.make_root("needs-confirmation") / "codex-home"
        code, payload = self.run_json(RUNTIME, "apply", "--apply", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertIn("operator_confirmation_required", payload["blockers"])

    def test_apply_writes_codex_adapters_templates_receipts_and_redacts_paths(self) -> None:
        base = self.make_root("apply")
        home = base / "codex-home"
        general = base / "General"
        general2 = base / "General_2"
        self.run_json(REF6_RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home), "--general-root", str(general), "--general2-root", str(general2), "--sync-templates")
        code, payload = self.run_json(
            RUNTIME,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--codex-home",
            str(home),
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
            "--sync-templates",
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue((home / "skills" / "codex-visio-paper-figure-skill" / "SKILL.md").is_file())
        self.assertTrue((home / "agents" / "agency-agents-zh.toml").is_file())
        self.assertTrue((general / "template_assets" / "reference8-active" / "adapters" / "fireworks-tech-graph.md").is_file())
        self.assertTrue((general / "template_assets" / "reference8-derived" / "adapters" / "markitdown.md").is_file())
        self.assertTrue((general2 / "template_assets" / "inert-samples" / "reference8" / "adapters" / "ansys-mcp-server.md").is_file())
        self.assertTrue((general2 / "template_assets" / "inert-samples" / "reference8-derived" / "adapters" / "codex-visio-paper-figure-skill.md").is_file())
        self.assertEqual(len(payload["receipt_summaries"]), 16)
        stages = {item["smoke"]["runtime_stage"] for item in payload["receipt_summaries"]}
        self.assertIn("R8 live-executed", stages)
        self.assertIn("R8 provision-recorded", stages)
        sample_smoke = payload["receipt_summaries"][0]["smoke"]
        self.assertIn(sample_smoke["adapter_kind"], {"codex-skill", "codex-agent-toml", "codex-project-runtime-wrapper", "codex-project-inert-template", "reference6-dedupe"})
        self.assertTrue(sample_smoke["requires_codex_adapter_before_live_executed"])
        self.assertFalse(sample_smoke["raw_upstream_live_executed_allowed"])
        self.assertIn("live_runtime_target", sample_smoke)
        self.assertNotEqual(sample_smoke["smoke_type"], "safe-discovery")
        rendered = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(str(home), rendered)
        self.assertNotIn(str(general), rendered)
        self.assertNotIn(str(general2), rendered)
        check_code, check_payload = self.run_json(
            RUNTIME,
            "check",
            "--require-installed",
            "--require-smoke-tested",
            "--require-live-executed",
            "--codex-home",
            str(home),
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
        )
        self.assertEqual(check_code, 0)
        self.assertTrue(check_payload["ok"], check_payload["errors"])
        self.assertEqual(check_payload["update_receipt_count"], 16)
        self.assertEqual(check_payload["smoke_receipt_count"], 16)
        self.assertEqual(check_payload["live_executed_count"] + check_payload["provision_recorded_count"], 16)

    def test_checker_passes_repo_surfaces(self) -> None:
        code, payload = self.run_json(CHECKER, "--root", str(ROOT))
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["manifest"]["capability_count"], 16)
        self.assertTrue(payload["registry_guard_ci"]["test_registered"])

    def test_checker_can_require_installed_against_temp_home_and_templates(self) -> None:
        base = self.make_root("checker")
        home = base / "codex-home"
        general = base / "General"
        general2 = base / "General_2"
        self.run_json(REF6_RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home), "--general-root", str(general), "--general2-root", str(general2), "--sync-templates")
        self.run_json(RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home), "--general-root", str(general), "--general2-root", str(general2), "--sync-templates")
        code, payload = self.run_json(
            CHECKER,
            "--root",
            str(ROOT),
            "--codex-home",
            str(home),
            "--require-user-level-installed",
            "--require-smoke-tested",
            "--require-live-executed",
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
            "--require-template-sync",
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["user_level_check"]["smoke_receipt_count"], 16)
        self.assertEqual(payload["user_level_check"]["live_executed_count"] + payload["user_level_check"]["provision_recorded_count"], 16)

    def test_raw_upstream_only_receipt_is_rejected(self) -> None:
        home = self.make_root("negative") / "codex-home"
        receipt_dir = home / "state" / "reference8-capability-install" / "receipts"
        receipt_dir.mkdir(parents=True)
        update = {
            "schema_version": 1,
            "receipt_kind": "reference8-update",
            "tool_name": "planning-with-files",
            "capability_id": "planning-with-files",
            "adapter_kind": "raw-upstream",
            "codex_adapter_present": False,
            "raw_upstream_install_only": True,
            "requires_codex_adapter_before_live_executed": True,
            "raw_upstream_live_executed_allowed": False,
            "live_runtime_target": "codex-home:skills/planning-with-files/SKILL.md",
            "live_smoke_kind": "planning_with_files_codex_state_fixture",
            "live_smoke_result": "blocked",
            "credential_gate": [],
            "source_reference_only": False,
            "installed_version": "raw-upstream",
            "source_url": "https://github.com/OthmanAdi/planning-with-files",
            "adapter_path": "upstream:planning-with-files",
            "install_path": "upstream:planning-with-files",
            "wrapper_path": "codex-home:tools/reference8-capability-install/reference8-smoke",
            "state_path": "codex-home:state/reference8-capability-install/planning-with-files",
            "smoke_test_result": {"status": "blocked"},
            "updater_command": "git clone upstream",
            "rollback_pointer": "codex-home:state/reference8-capability-install/backups/raw",
            "owner_lane": "reference8-capability-install",
            "redaction_status": "no_secrets",
            "raw_paths_included": False,
            "remote_publication_mutated": False,
            "native_codex_files_mutated": False,
            "codex_config_toml_mutated": False,
            "blockers": [],
        }
        (receipt_dir / "planning-with-files-update.json").write_text(json.dumps(update), encoding="utf-8")
        code, payload = self.run_json(RUNTIME, "check", "--codex-home", str(home), "--require-installed", check=False)
        self.assertEqual(code, 3)
        self.assertIn("invalid_update_receipt:planning-with-files:adapter_kind_not_codex_adapter", payload["errors"])
        self.assertIn("invalid_update_receipt:planning-with-files:raw_upstream_install_only_not_allowed", payload["errors"])


if __name__ == "__main__":
    unittest.main()
