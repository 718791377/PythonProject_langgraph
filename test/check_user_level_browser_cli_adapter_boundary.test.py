from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_user_level_browser_cli_adapter_boundary.py"


class BrowserCliAdapterBoundaryCheckerTests(unittest.TestCase):
    maxDiff = None

    def run_checker(self) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(ROOT), "--json"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        return json.loads(result.stdout)

    def test_repo_split_adapter_boundary_is_checker_backed(self) -> None:
        payload = self.run_checker()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "user_level_browser_cli_adapter_boundary")
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertTrue(payload["registry_guard_ci"]["rule_found"])
        self.assertEqual(payload["registry_guard_ci"]["missing_tests"], [])
        for plan in payload["plans"].values():
            self.assertTrue(plan["canonical_hits"]["chrome-devtools-mcp"])
            self.assertTrue(plan["canonical_hits"]["CDP Bridge"])
            self.assertTrue(plan["canonical_hits"]["OpenCLI"])
            self.assertEqual(plan["forbidden_terms"], [])
            self.assertTrue(all(plan["runtime_stage_markers"].values()))
            self.assertTrue(all(plan["runtime_status_markers"].values()))
            self.assertTrue(plan["not_installed_started_enabled"])
            self.assertTrue(plan["r5_sensitive_gate"])
        self.assertFalse(any(payload["old_plan_presence"].values()))


if __name__ == "__main__":
    unittest.main()
