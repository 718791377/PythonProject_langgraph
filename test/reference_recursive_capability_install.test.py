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
RUNTIME = ROOT / "tools" / "reference_recursive_capability_install.py"
CHECKER = ROOT / "tools" / "check_reference_recursive_capability_install.py"
MANIFEST = ROOT / "tools" / "reference_recursive_capability_install" / "manifest.json"


class ReferenceRecursiveCapabilityInstallTests(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        base = ROOT / ".omx" / "test-artifacts" / f"reference-recursive-{name}-{uuid.uuid4().hex[:8]}"
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

    def manifest(self) -> dict:
        return json.loads(MANIFEST.read_text(encoding="utf-8-sig"))

    def test_plan_exposes_recursive_counts_and_policy(self) -> None:
        code, payload = self.run_json(RUNTIME, "plan")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        manifest = self.manifest()
        self.assertEqual(payload["summary"]["unit_count"], manifest["expected_counts"]["unit_count"])
        self.assertGreaterEqual(payload["summary"]["unit_count"], 2000)
        self.assertEqual(payload["browserbase_policy"], "disabled_by_user")
        self.assertFalse(payload["codex_config_toml_mutated"])
        self.assertFalse(payload["native_codex_files_mutated"])
        self.assertFalse(payload["raw_upstream_install_counts_as_live_executed"])
        states = payload["summary"]["by_child_state"]
        for state in ("live-executed", "disabled", "dedupe", "provision-recorded"):
            self.assertIn(state, states)
        self.assertEqual(states, manifest["expected_counts"]["by_child_state"])
        self.assertGreaterEqual(manifest["expected_counts"]["by_parent_capability"].get("mattpocock-skills", 0), 30)

    def test_apply_requires_explicit_flag_and_operator_confirmation(self) -> None:
        code, payload = self.run_json(RUNTIME, "apply", check=False)
        self.assertEqual(code, 3)
        self.assertIn("apply_flag_required", payload["blockers"])
        home = self.make_root("confirm") / "codex-home"
        code, payload = self.run_json(RUNTIME, "apply", "--apply", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertIn("operator_confirmation_required", payload["blockers"])

    def test_apply_check_strict_temp_home_and_templates(self) -> None:
        base = self.make_root("strict")
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
        self.assertEqual(payload["unit_count"], self.manifest()["expected_counts"]["unit_count"])
        self.assertNotIn(str(home), json.dumps(payload, ensure_ascii=False))
        self.assertNotIn(str(general), json.dumps(payload, ensure_ascii=False))
        self.assertNotIn(str(general2), json.dumps(payload, ensure_ascii=False))
        self.assertTrue((home / "tools" / "reference-recursive-capability-install" / "manifest.json").is_file())
        self.assertTrue((general / "template_assets" / "reference-recursive-active" / "README.md").is_file())
        self.assertTrue((general2 / "template_assets" / "inert-samples" / "reference-recursive" / "README.md").is_file())

        code, check = self.run_json(
            RUNTIME,
            "check",
            "--require-installed",
            "--require-smoke-tested",
            "--require-live-executed",
            "--require-template-sync",
            "--codex-home",
            str(home),
            "--general-root",
            str(general),
            "--general2-root",
            str(general2),
        )
        self.assertEqual(code, 0)
        self.assertTrue(check["ok"], check["errors"])
        expected = self.manifest()["expected_counts"]["by_child_state"]
        self.assertEqual(check["live_executed_count"], expected["live-executed"])
        self.assertEqual(check["disabled_count"], expected["disabled"])
        self.assertEqual(check["dedupe_count"], expected["dedupe"])
        self.assertEqual(check["provision_recorded_count"], expected["provision-recorded"])
        self.assertEqual(check["smoke_receipt_count"], self.manifest()["expected_counts"]["unit_count"])

    def test_browserbase_disabled_and_dedupe_are_not_counted_as_live(self) -> None:
        manifest = self.manifest()
        browserbase = [u for u in manifest["units"] if u["parent_capability_id"] == "browserbase-skills"]
        self.assertGreaterEqual(len(browserbase), 10)
        self.assertTrue(all(u["child_state"] == "disabled" for u in browserbase))
        dedupe = [u for u in manifest["units"] if u["child_state"] == "dedupe"]
        self.assertGreaterEqual(len(dedupe), 1000)
        self.assertTrue(all(u.get("dedupe_target") for u in dedupe))

    def test_checker_passes_repo_surfaces_after_registration(self) -> None:
        code, payload = self.run_json(CHECKER, "--root", str(ROOT))
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["manifest"]["unit_count"], self.manifest()["expected_counts"]["unit_count"])
        self.assertTrue(payload["registry_guard_ci"]["test_registered"])
        self.assertTrue(payload["registry_guard_ci"]["guard_registered"])
        self.assertTrue(payload["registry_guard_ci"]["safety_rule_found"])

    def test_raw_upstream_receipt_is_rejected_by_strict_check(self) -> None:
        base = self.make_root("negative")
        home = base / "codex-home"
        receipt_dir = home / "state" / "reference-recursive-capability-install" / "receipts"
        receipt_dir.mkdir(parents=True)
        unit = next(u for u in self.manifest()["units"] if u["child_state"] == "live-executed")
        bad = {
            "schema_version": 1,
            "receipt_kind": "reference-recursive-update",
            "tool_name": "reference_recursive_capability_install",
            "child_unit_id": unit["child_unit_id"],
            "raw_upstream_install_only": True,
            "source_reference_only": False,
            "codex_config_toml_mutated": False,
            "native_codex_files_mutated": False,
        }
        (receipt_dir / "bad-update.json").write_text(json.dumps(bad), encoding="utf-8")
        code, payload = self.run_json(RUNTIME, "check", "--require-installed", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertTrue(any("invalid_update_receipt" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
