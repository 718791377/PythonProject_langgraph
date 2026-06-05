from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_user_level_cli_anything_wxwork_cli_governance.py"


class CLIAnythingWXWorkCheckerTests(unittest.TestCase):
    maxDiff = None

    def test_repo_cli_anything_wxwork_lane_is_checker_backed(self) -> None:
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
        self.assertEqual(payload["check_name"], "user_level_cli_anything_wxwork_cli_governance")
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertTrue(payload["helpers"]["cli_anything_helper_present"])
        self.assertTrue(payload["helpers"]["wxwork_helper_present"])
        self.assertFalse(payload["helpers"]["legacy_wecom_helper_present"])
        self.assertTrue(payload["registry_guard_ci"]["rule_found"])
        self.assertEqual(payload["registry_guard_ci"]["missing_tests"], [])
        for plan in payload["plans"].values():
            self.assertTrue(plan["implemented_local"])
            self.assertTrue(plan["has_stage_b_evidence"])
            self.assertTrue(all(plan["runtime_stage_markers"].values()))
            self.assertTrue(all(plan["runtime_status_markers"].values()))
            self.assertTrue(plan["send_allowed_only_r5"])
            self.assertTrue(plan["not_installed_started_enabled"])


if __name__ == "__main__":
    unittest.main()
