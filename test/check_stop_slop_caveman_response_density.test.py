#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_stop_slop_caveman_response_density.py"
RUNTIME = ROOT / "tools" / "stop_slop_caveman_runtime.py"
SMOKE_CHECKER = ROOT / "tools" / "check_stop_slop_caveman_smoke_receipts.py"


def run_json(script: Path, *args: str, expect: int = 0) -> tuple[dict, str]:
    proc = subprocess.run(
        [sys.executable, str(script), *args, "--json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic only
        raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
    if proc.returncode != expect:
        raise AssertionError(
            f"expected exit {expect}, got {proc.returncode}\n"
            f"payload={json.dumps(payload, ensure_ascii=False, indent=2)}\nstderr={proc.stderr}"
        )
    return payload, proc.stdout + proc.stderr


class StopSlopCavemanResponseDensityTests(unittest.TestCase):
    maxDiff = None

    def test_checker_rejects_slop_but_accepts_dense_protected_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.md"
            good = root / "good.md"
            bad.write_text(
                "Sure! I'd be happy to help. Here's what this means — the implications are significant. "
                "This is not just a warning, it's a governance issue.",
                encoding="utf-8",
            )
            good.write_text(
                "Routing trace: phase=build, durable_team=threshold_not_met:single_execution_slice\n"
                "Updated Plan\n"
                "Fix parser. Keep `python tools/run.py --json`; path `tools/run.py`; "
                "URL https://example.invalid/a?b=c. 中文说明保留。",
                encoding="utf-8",
            )

            invalid, _ = run_json(CHECKER, "--sample-file", str(bad), expect=1)
            self.assertFalse(invalid["ok"])
            finding_ids = {finding["id"] for finding in invalid["findings"]}
            self.assertIn("throat_clearing", finding_ids)
            self.assertIn("em_dash", finding_ids)
            self.assertIn("binary_contrast", finding_ids)

            valid, _ = run_json(CHECKER, "--sample-file", str(good))
            self.assertTrue(valid["ok"])
            self.assertEqual(valid["counts"]["errors"], 0)
            self.assertIn("Routing trace", valid["protected_spans"]["labels"])
            self.assertIn("Updated Plan", valid["protected_spans"]["labels"])

    def test_checker_handles_real_unicode_punctuation_not_mojibake_only(self) -> None:
        sample = "Here\u2019s what changed \u2014 the implications are significant."

        payload, _ = run_json(CHECKER, "--sample-text", sample, expect=1)

        finding_ids = {finding["id"] for finding in payload["findings"]}
        self.assertIn("throat_clearing", finding_ids)
        self.assertIn("em_dash", finding_ids)

    def test_runtime_analyze_reports_diagnostics_without_rewriting_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.md"
            original = "Here's what changed — the reasons are structural. Use `--dry-run` first."
            sample.write_text(original, encoding="utf-8")

            payload, _ = run_json(RUNTIME, "analyze", "--file", str(sample))
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["action"], "analyze")
            self.assertFalse(payload["rewrite_performed"])
            self.assertGreater(payload["diagnostics"]["counts"]["errors"], 0)
            self.assertEqual(sample.read_text(encoding="utf-8"), original)

    def test_runtime_rewrite_dry_run_shortens_text_and_preserves_protected_spans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.md"
            original = (
                "Sure! I'd be happy to help. Here's what you need to do — first, keep this code:\n"
                "```python\nprint('do not rewrite')\n```\n"
                "Run `python tools/run.py --json`; keep path `tools/run.py`; keep URL "
                "https://example.invalid/a?b=c; keep JSON key `rollback_pointer`."
            )
            sample.write_text(original, encoding="utf-8")

            payload, _ = run_json(RUNTIME, "rewrite", "--file", str(sample), "--dry-run")
            rewritten = payload["rewritten_text"]
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["write_performed"])
            self.assertLess(payload["lengths"]["rewritten_chars"], payload["lengths"]["original_chars"])
            self.assertNotIn("Sure!", rewritten)
            self.assertNotIn("Here's what", rewritten)
            for protected in (
                "```python\nprint('do not rewrite')\n```",
                "`python tools/run.py --json`",
                "`tools/run.py`",
                "https://example.invalid/a?b=c",
                "`rollback_pointer`",
            ):
                self.assertIn(protected, rewritten)
            self.assertEqual(sample.read_text(encoding="utf-8"), original)

    def test_runtime_rewrite_apply_requires_operator_confirmation_and_preserves_spans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.md"
            original = "Certainly, here's what happened — the implications are significant. Keep `--json`."
            sample.write_text(original, encoding="utf-8")

            blocked, _ = run_json(RUNTIME, "rewrite", "--file", str(sample), "--apply", expect=3)
            self.assertFalse(blocked["ok"])
            self.assertIn("operator_confirmation_required", blocked["blockers"])
            self.assertEqual(sample.read_text(encoding="utf-8"), original)

            applied, _ = run_json(
                RUNTIME,
                "rewrite",
                "--file",
                str(sample),
                "--apply",
                "--operator-confirmation",
            )
            self.assertTrue(applied["ok"])
            self.assertTrue(applied["write_performed"])
            changed = sample.read_text(encoding="utf-8")
            self.assertIn("`--json`", changed)
            self.assertNotIn("Certainly", changed)
            self.assertLess(len(changed), len(original))

    def write_install_receipt(self, directory: Path) -> Path:
        receipt = {
            "schema_version": 1,
            "tool_name": "Stop-Slop-Caveman",
            "owner_lane": "stop-slop-caveman-response-density",
            "status": "installed-user-level",
            "source_url": "https://github.com/hardikpandya/stop-slop",
            "secondary_source_url": "https://github.com/JuliusBrussee/caveman",
            "installed_version": "fixture-pin",
            "wrapper_path": sys.executable,
            "install_path": str(directory / "install"),
            "state_path": str(directory / "state"),
            "smoke_test_command": "python --version",
            "smoke_test_result": {"status": "pass"},
            "updater_command": "no-op fixture update",
            "rollback_pointer": str(directory / "rollback"),
            "redaction_status": "no_secrets",
        }
        path = directory / "install.json"
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_smoke_record_without_r3_install_receipt_is_blocked_but_accepted_as_non_smoke_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp) / "receipts"
            payload, output = run_json(
                RUNTIME,
                "smoke-record",
                "--receipt-dir",
                str(receipt_dir),
                "--session",
                "session-a",
            )
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["receipt_written"])
            self.assertFalse(payload["smoke_tested"])
            self.assertEqual(payload["r4_status"], "blocked")
            self.assertNotIn(str(receipt_dir), output)

            checked, _ = run_json(SMOKE_CHECKER, "--receipt-dir", str(receipt_dir))
            self.assertTrue(checked["ok"])
            self.assertEqual(checked["counts"]["blocked_or_not_installed"], 1)
            self.assertEqual(checked["counts"]["positive_smoke_tested"], 0)

    def test_valid_fixture_smoke_tested_receipt_passes_and_sanitizes_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install = self.write_install_receipt(root)
            receipt_dir = root / "smoke"
            payload, output = run_json(
                RUNTIME,
                "smoke-record",
                "--install-receipt",
                str(install),
                "--receipt-dir",
                str(receipt_dir),
                "--smoke-type",
                "help",
                "--session",
                "session-a",
            )
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["smoke_tested"])
            self.assertEqual(payload["r4_status"], "smoke-tested")
            self.assertNotIn(str(root), output)
            self.assertNotIn(sys.executable, output)

            checked, check_output = run_json(SMOKE_CHECKER, "--receipt-dir", str(receipt_dir), "--require-smoke-tested")
            self.assertTrue(checked["ok"])
            self.assertEqual(checked["counts"]["positive_smoke_tested"], 1)
            self.assertNotIn(str(root), check_output)
            self.assertNotIn(sys.executable, check_output)

    def test_smoke_checker_blocks_write_live_sensitive_markers_and_redacts_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "Stop-Slop-Caveman",
                "owner_lane": "stop-slop-caveman-response-density",
                "runtime_stage": "smoke-tested",
                "r4_status": "smoke-tested",
                "install_receipt": "receipt-sha256:abc",
                "smoke_command": "stop-slop-caveman rewrite --apply",
                "smoke_type": "safe-rewrite",
                "smoke_result": {"status": "pass"},
                "timeout_release": {"status": "pass", "released": True},
                "rollback_pointer": str(root / "rollback"),
                "rollback_ready": True,
                "command_transcript": f"wrote {root}\\private token=sk-testsecret123",
                "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "fixture"},
                "redaction_status": "no_secrets",
                "smoke_tested": True,
                "write_performed": True,
                "live_action_performed": True,
                "sensitive_action_performed": True,
                "user_level_state_mutated": True,
                "external_message_sent": False,
            }
            path = root / "bad.json"
            path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

            payload, output = run_json(SMOKE_CHECKER, "--receipt", str(path), "--require-smoke-tested", expect=1)
            self.assertFalse(payload["ok"])
            joined = "\n".join(payload["errors"])
            self.assertIn("forbidden_write_performed", joined)
            self.assertIn("forbidden_live_action_performed", joined)
            self.assertIn("forbidden_sensitive_action_performed", joined)
            self.assertNotIn(str(root), output)
            self.assertNotIn("sk-testsecret123", output)


if __name__ == "__main__":
    unittest.main()
