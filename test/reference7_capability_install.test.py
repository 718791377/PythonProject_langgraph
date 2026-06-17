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
RUNTIME = ROOT / "tools" / "reference7_capability_install.py"
CHECKER = ROOT / "tools" / "check_reference7_capability_install.py"


class Reference7CapabilityInstallTests(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        base = ROOT / ".omx" / "test-artifacts" / f"reference7-{name}-{uuid.uuid4().hex[:8]}"
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

    def test_plan_exposes_25_capabilities_layers_and_adapter_policy(self) -> None:
        code, payload = self.run_json(RUNTIME, "plan")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability_count"], 25)
        self.assertEqual(payload["layer_counts"], {"user_level": 16, "project_template_general": 5, "project_template_general_2": 4})
        for item in payload["capabilities"]:
            self.assertTrue(item["requires_codex_adapter_before_live_executed"])
            self.assertFalse(item["raw_upstream_live_executed_allowed"])
            self.assertIn("adapter_kind", item)
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
        self.assertTrue((home / "skills" / "opc-orchestrator" / "SKILL.md").is_file())
        self.assertTrue((home / "agents" / "agency-agents.toml").is_file())
        self.assertTrue((general / "template_assets" / "reference7-active" / "adapters" / "html-video.md").is_file())
        self.assertTrue((general2 / "template_assets" / "inert-samples" / "reference7" / "adapters" / "golutra.md").is_file())
        self.assertEqual(len(payload["receipt_summaries"]), 25)
        sample_smoke = payload["receipt_summaries"][0]["smoke"]
        self.assertIn(sample_smoke["adapter_kind"], {"codex-skill", "codex-agent-toml", "codex-project-runtime-wrapper", "codex-project-inert-template", "reference6-dedupe"})
        self.assertTrue(sample_smoke["requires_codex_adapter_before_live_executed"])
        self.assertFalse(sample_smoke["raw_upstream_live_executed_allowed"])
        rendered = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(str(home), rendered)
        self.assertNotIn(str(general), rendered)
        self.assertNotIn(str(general2), rendered)
        check_code, check_payload = self.run_json(
            RUNTIME,
            "check",
            "--require-installed",
            "--require-smoke-tested",
            "--codex-home",
            str(home),
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
        )
        self.assertEqual(check_code, 0)
        self.assertTrue(check_payload["ok"], check_payload["errors"])
        self.assertEqual(check_payload["update_receipt_count"], 25)
        self.assertEqual(check_payload["smoke_receipt_count"], 25)

    def test_checker_passes_repo_surfaces(self) -> None:
        code, payload = self.run_json(CHECKER, "--root", str(ROOT))
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["manifest"]["capability_count"], 25)
        self.assertTrue(payload["registry_guard_ci"]["test_registered"])

    def test_checker_can_require_installed_against_temp_home_and_templates(self) -> None:
        base = self.make_root("checker")
        home = base / "codex-home"
        general = base / "General"
        general2 = base / "General_2"
        self.run_json(RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home), "--general-root", str(general), "--general2-root", str(general2), "--sync-templates")
        code, payload = self.run_json(
            CHECKER,
            "--root",
            str(ROOT),
            "--codex-home",
            str(home),
            "--require-user-level-installed",
            "--require-smoke-tested",
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
            "--require-template-sync",
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["user_level_check"]["smoke_receipt_count"], 25)

    def test_raw_upstream_only_receipt_is_rejected(self) -> None:
        home = self.make_root("negative") / "codex-home"
        receipt_dir = home / "state" / "reference7-capability-install" / "receipts"
        receipt_dir.mkdir(parents=True)
        update = {
            "schema_version": 1,
            "receipt_kind": "reference7-update",
            "tool_name": "nuwa-skill",
            "capability_id": "nuwa-skill",
            "adapter_kind": "raw-upstream",
            "codex_adapter_present": False,
            "raw_upstream_install_only": True,
            "requires_codex_adapter_before_live_executed": True,
            "raw_upstream_live_executed_allowed": False,
            "installed_version": "raw-upstream",
            "source_url": "https://github.com/alchaincyf/nuwa-skill",
            "adapter_path": "upstream:nuwa-skill",
            "install_path": "upstream:nuwa-skill",
            "wrapper_path": "codex-home:tools/reference7-capability-install/reference7-smoke",
            "state_path": "codex-home:state/reference7-capability-install/nuwa-skill",
            "smoke_test_result": {"status": "blocked"},
            "updater_command": "git clone upstream",
            "rollback_pointer": "codex-home:state/reference7-capability-install/backups/raw",
            "owner_lane": "reference7-capability-install",
            "redaction_status": "no_secrets",
            "raw_paths_included": False,
            "remote_publication_mutated": False,
            "native_codex_files_mutated": False,
            "codex_config_toml_mutated": False,
            "blockers": [],
        }
        (receipt_dir / "nuwa-skill-update.json").write_text(json.dumps(update), encoding="utf-8")
        code, payload = self.run_json(RUNTIME, "check", "--codex-home", str(home), "--require-installed", check=False)
        self.assertEqual(code, 3)
        self.assertIn("invalid_update_receipt:nuwa-skill:raw_upstream_install_only_not_allowed", payload["errors"])


if __name__ == "__main__":
    unittest.main()
