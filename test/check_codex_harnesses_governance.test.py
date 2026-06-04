from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_codex_harnesses_governance.py"


class CodexHarnessesGovernanceCheckerTests(unittest.TestCase):
    maxDiff = None

    def test_repo_codex_harnesses_lane_is_checker_backed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(ROOT), "--json"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "codex_harnesses_governance")
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertTrue(payload["registry_guard_ci"]["rule_found"])
        self.assertEqual(payload["registry_guard_ci"]["missing_tests"], [])
        self.assertEqual(set(payload["source_urls"]), {
            "https://blog.can.ac/2026/02/12/the-harness-problem",
            "https://github.com/can1357/oh-my-pi",
            "https://pi.dev/",
            "https://pi.dev/packages",
        })
        for plan in payload["plans"].values():
            self.assertGreaterEqual(plan["source_rows"], 4)


if __name__ == "__main__":
    unittest.main()
