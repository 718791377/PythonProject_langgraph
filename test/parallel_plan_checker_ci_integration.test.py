import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_local_mirrored_ci_gate.py"


class ParallelPlanCheckerCiIntegrationTest(unittest.TestCase):
    maxDiff = None

    def run_check(self) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(REPO_ROOT), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"], payload)
        return payload

    def test_current_repository_records_parallel_plan_ci_evidence(self) -> None:
        payload = self.run_check()
        evidence = payload["evidence"]

        self.assertTrue(
            evidence["ci_test_manifest"]["required_tests"]["check_local_mirrored_ci_gate.test.py"]
        )
        self.assertTrue(
            evidence["ci_test_manifest"]["required_tests"]["parallel_plan_checker_ci_integration.test.py"]
        )
        self.assertTrue(evidence["local_gate_step_order"]["in_order"])
        for step in (
            "check_precommit_update_archive",
            "check_safety_rule_script_backing",
            "check_local_mirrored_ci_gate",
        ):
            self.assertTrue(evidence["guard_steps"][step], step)
        for marker in (
            "new_tests_registered",
            "new_checkers_registered",
            "ci_manifest_policy",
            "checker_registration_policy",
        ):
            self.assertTrue(evidence["precommit_registration_enforcement"][marker], marker)
        for rule_id in (
            "precommit-update-archive-gate",
            "local-mirrored-ci-mr-gate",
            "complete-local-flow-to-remote-gate",
        ):
            rule = evidence["safety_rules"][rule_id]
            self.assertTrue(rule["present"], rule_id)
            self.assertTrue(rule["implemented"], rule_id)

    def test_remote_ci_surfaces_use_shared_gate_with_required_flags(self) -> None:
        payload = self.run_check()
        remote_ci = payload["evidence"]["remote_ci"]

        for path, record in remote_ci.items():
            self.assertTrue(record["calls_shared_local_gate"], path)
            self.assertTrue(record["required_shared_gate_flags"]["-RefreshManagedFiles"], path)
            self.assertTrue(record["required_shared_gate_flags"]["-RequireCleanGit"], path)
            self.assertFalse(any(record["forbidden_inline_markers"].values()), path)


if __name__ == "__main__":
    unittest.main()
