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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_expert_lifecycle_wait_pacing_evidence.py"

spec = importlib.util.spec_from_file_location("check_expert_lifecycle_wait_pacing_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_EVIDENCE = """Run summary:
expert returned and absorbed: verifier result reviewed by leader.
completed agent closed after absorption via close_agent.
follow-up work will spawn fresh agent if needed.
wait_agent used bounded wait windows: 30s then 60s; total wait bound about 180s.
two consecutive progress checks stayed quiet; leader will inspect, redirect, respawn a narrower expert, durable handoff, or main session took over verification.
provider pacing budget saturated; treated as backpressure with local-first bounded fan-out and wait for a slot.
"""


class ExpertLifecycleWaitPacingEvidenceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_evidence(self, root: Path, content: str) -> Path:
        path = root / "evidence.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def run_cli(self, evidence_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--evidence", str(evidence_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_valid_evidence_passes(self) -> None:
        root = self.make_root("expert-lifecycle-valid")
        path = self.write_evidence(root, VALID_EVIDENCE)

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("completed_expert", payload["detected"])
        self.assertIn("wait", payload["detected"])
        self.assertIn("provider_pacing", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_root("expert-lifecycle-cli")
        path = self.write_evidence(root, VALID_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "expert_lifecycle_wait_pacing_evidence")

    def test_completed_expert_without_close_or_preserve_fails(self) -> None:
        root = self.make_root("expert-no-close")
        path = self.write_evidence(root, "expert returned and absorbed: verifier result reviewed.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("closure" in error or "preserved" in error for error in payload["errors"]), payload["errors"])

    def test_completed_expert_with_preserved_reason_passes(self) -> None:
        root = self.make_root("expert-preserved")
        path = self.write_evidence(
            root,
            "expert returned and absorbed. user explicitly asked to preserve thread; preserved-thread reason recorded.\n",
        )

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])

    def test_follow_up_without_fresh_agent_or_preserve_fails(self) -> None:
        root = self.make_root("follow-up-no-fresh")
        path = self.write_evidence(root, "follow-up work will continue in the previous expert thread.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("fresh agent" in error for error in payload["errors"]), payload["errors"])

    def test_wait_without_total_bound_fails(self) -> None:
        root = self.make_root("wait-no-total")
        path = self.write_evidence(root, "wait_agent used bounded wait windows: 30s then 60s.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("total wait bound" in error for error in payload["errors"]), payload["errors"])

    def test_indefinite_wait_fails(self) -> None:
        root = self.make_root("wait-indefinite")
        path = self.write_evidence(
            root,
            "wait_agent will wait indefinitely with bounded wait window 30s and total wait bound about 180s.\n",
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("indefinite" in error or "unbounded" in error for error in payload["errors"]), payload["errors"])

    def test_stall_without_action_fails(self) -> None:
        root = self.make_root("stall-no-action")
        path = self.write_evidence(root, "two consecutive progress checks stayed quiet and the expert stalled.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("Stall" in error or "handling action" in error for error in payload["errors"]), payload["errors"])

    def test_provider_pacing_without_backpressure_fails(self) -> None:
        root = self.make_root("pacing-no-backpressure")
        path = self.write_evidence(root, "provider pacing budget saturated; requests waited.\n")

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("backpressure" in error for error in payload["errors"]), payload["errors"])

    def test_provider_pacing_disablement_fails_even_with_backpressure(self) -> None:
        root = self.make_root("pacing-disable")
        path = self.write_evidence(
            root,
            "provider pacing is backpressure, but due to pacing do not use LangGraph orchestration.\n",
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("disable orchestration" in error or "Provider/upstream pacing" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_timeout_accepted_as_result_evidence_fails(self) -> None:
        root = self.make_root("timeout-as-result")
        path = self.write_evidence(
            root,
            "expert timed out after bounded wait and accepted as valid expert result evidence. "
            "wait_agent used bounded wait windows: 30s; total wait bound about 180s. "
            "main session took over verification.\n",
        )

        payload = module.run_check(path)

        self.assertFalse(payload["ok"])
        self.assertIn("timeout", payload["detected"])
        self.assertTrue(
            any("valid expert result" in error or "verification evidence" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_timeout_non_evidence_with_takeover_passes(self) -> None:
        root = self.make_root("timeout-non-evidence")
        path = self.write_evidence(
            root,
            "expert timed out; not used as evidence. "
            "wait_agent used bounded wait windows: 30s; total wait bound about 180s. "
            "main session took over verification.\n",
        )

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("timeout", payload["detected"])

    def test_no_markers_warns_without_failing(self) -> None:
        root = self.make_root("no-markers")
        path = self.write_evidence(root, "No delegated expert work occurred in this local-only task.\n")

        payload = module.run_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertGreaterEqual(payload["counts"]["warnings"], 1)


if __name__ == "__main__":
    unittest.main()
