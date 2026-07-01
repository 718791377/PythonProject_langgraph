#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools" / "reference6_capability_install.py"
CHECKER = ROOT / "tools" / "check_reference6_capability_install.py"
RECEIPT_GOVERNANCE = ROOT / "tools" / "user_level_receipt_governance.py"


class Reference6CapabilityInstallTests(unittest.TestCase):
    maxDiff = None

    def make_home(self, name: str) -> Path:
        base = ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        home = base / "codex-home"
        home.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return home

    def run_json(self, script: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(script), *args, "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            env=env,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
        if check and proc.returncode != 0:
            self.fail(json.dumps(payload, ensure_ascii=False, indent=2) + "\n" + proc.stderr)
        return proc.returncode, payload

    def test_plan_exposes_all_reference6_capabilities_and_env_key_only_policy(self) -> None:
        code, payload = self.run_json(RUNTIME, "plan")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            {item["id"] for item in payload["capabilities"]},
            {
                "open-design",
                "html-anything",
                "browserbase-skills",
                "pymupdf",
                "mineru",
                "mineru-api-limit",
                "mineru-site",
                "book-to-skill",
                "mattpocock-skills",
            },
        )
        for item in payload["capabilities"]:
            self.assertIn("live_runtime_target", item)
            self.assertIn("live_smoke_kind", item)
        by_id = {item["id"]: item for item in payload["capabilities"]}
        self.assertEqual(by_id["browserbase-skills"]["live_runtime"]["completion_policy"], "optional_disabled")
        self.assertTrue(by_id["browserbase-skills"]["live_runtime"]["disabled"])
        self.assertEqual(payload["codex_provider_env"]["reuse_mode"], "env_key_name_only")
        self.assertFalse(payload["codex_provider_env"]["copy_secret_values"])
        self.assertFalse(payload["codex_config_toml_mutated"])

    def test_apply_requires_explicit_flag_and_operator_confirmation(self) -> None:
        code, payload = self.run_json(RUNTIME, "apply", check=False)
        self.assertEqual(code, 3)
        self.assertIn("apply_flag_required", payload["blockers"])

        home = self.make_home("needs-confirmation")
        code, payload = self.run_json(RUNTIME, "apply", "--apply", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertIn("operator_confirmation_required", payload["blockers"])

    def test_apply_writes_user_level_artifacts_receipts_and_blockers(self) -> None:
        home = self.make_home("apply")
        code, payload = self.run_json(
            RUNTIME,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--codex-home",
            str(home),
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["mutates_user_level_state"])
        self.assertTrue((home / "tools" / "reference6-capability-install" / "manifest.json").is_file())
        self.assertTrue((home / "tools" / "reference6-capability-install" / "reference6_capability_install.py").is_file())
        self.assertTrue((home / "bin" / "reference6-smoke.cmd").is_file())
        self.assertEqual(len(payload["receipt_summaries"]), 9)
        self.assertNotIn(str(home), json.dumps(payload, ensure_ascii=False))

        check_code, check_payload = self.run_json(
            RUNTIME,
            "check",
            "--require-installed",
            "--require-smoke-tested",
            "--codex-home",
            str(home),
        )
        self.assertEqual(check_code, 0)
        self.assertTrue(check_payload["ok"], check_payload["errors"])
        self.assertEqual(check_payload["update_receipt_count"], 9)
        self.assertEqual(check_payload["smoke_receipt_count"], 9)

    def test_checker_passes_repo_surfaces(self) -> None:
        code, payload = self.run_json(CHECKER, "--root", str(ROOT))
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["manifest"]["capability_count"], 9)
        self.assertTrue(payload["registry_guard_ci"]["test_registered"])

    def test_checker_can_require_installed_against_temp_home(self) -> None:
        home = self.make_home("checker")
        self.run_json(RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home))
        code, payload = self.run_json(
            CHECKER,
            "--root",
            str(ROOT),
            "--codex-home",
            str(home),
            "--require-user-level-installed",
            "--require-smoke-tested",
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["user_level_check"]["smoke_receipt_count"], 9)

    def test_strict_live_gate_allows_disabled_browserbase_but_blocks_missing_mineru_credentials(self) -> None:
        home = self.make_home("strict-blocked")
        env = dict(os.environ)
        env.pop("MINERU_API_KEY", None)
        env.pop("BROWSERBASE_API_KEY", None)
        env.pop("BROWSERBASE_PROJECT_ID", None)
        self.run_json(RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home), env=env)
        code, payload = self.run_json(
            RUNTIME,
            "check",
            "--require-installed",
            "--require-smoke-tested",
            "--require-live-executed",
            "--codex-home",
            str(home),
            check=False,
            env=env,
        )
        self.assertEqual(code, 3)
        self.assertFalse(payload["ok"])
        self.assertFalse(any("browserbase-skills" in error for error in payload["errors"]))
        self.assertTrue(any("mineru" in error for error in payload["errors"]))
        self.assertEqual(payload["disabled_count"], 1)
        self.assertIn("browserbase-skills", payload["optional_disabled_capabilities"])
        browserbase = payload["latest_receipts"]["smoke"]["browserbase-skills"]
        self.assertEqual(browserbase["runtime_stage"], "R6 disabled")
        self.assertTrue(browserbase["optional_disabled"])

    def test_generic_receipt_redaction_checker_accepts_update_receipt(self) -> None:
        home = self.make_home("receipt-gov")
        self.run_json(RUNTIME, "apply", "--apply", "--operator-confirmation", "--codex-home", str(home))
        receipt = home / "state" / "reference6-capability-install" / "receipts" / "open-design-update.json"
        code, payload = self.run_json(
            RECEIPT_GOVERNANCE,
            "update-check",
            "--receipt",
            str(receipt),
            "--tool-name",
            "open-design",
            "--owner-lane",
            "reference6-capability-install",
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["blockers"])


if __name__ == "__main__":
    unittest.main()
