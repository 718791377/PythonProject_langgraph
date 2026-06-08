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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_repo_local_selector_ownership.py"
FIXTURE_ROOT = REPO_ROOT / "test" / "fixtures" / "repo_local_selector_ownership"
NOW = "2026-05-30T08:30:00Z"

spec = importlib.util.spec_from_file_location("check_repo_local_selector_ownership", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class RepoLocalSelectorOwnershipTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_fixture(self, fixture_name: str) -> Path:
        root = self.make_root(f"selector-{fixture_name}")
        source = FIXTURE_ROOT / fixture_name
        selectors = root / ".omx" / "state" / "selectors"
        leases = selectors / "leases"
        leases.mkdir(parents=True, exist_ok=True)
        active_text = (source / "active_selector.json").read_text(encoding="utf-8").replace("__ROOT__", root.as_posix())
        lease_text = (source / "selector_lease.json").read_text(encoding="utf-8").replace("__ROOT__", root.as_posix())
        (selectors / "active.json").write_text(active_text, encoding="utf-8")
        (leases / "selector-fixture.json").write_text(lease_text, encoding="utf-8")
        return root

    def test_same_repo_active_selector_allows_adoption(self) -> None:
        root = self.copy_fixture("same_repo")

        payload = module.run_check(root, now=module.parse_now(NOW))

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertTrue(payload["selector_found"])
        self.assertTrue(payload["adoption_allowed"])
        self.assertTrue(payload["selector_valid_for_routing"])
        self.assertFalse(payload["runtime_adoption_allowed"])
        self.assertIn("active_candidate_receipt_missing", payload["runtime_adoption_blockers"])
        self.assertEqual(payload["adoption_blockers"], [])


    def test_same_repo_selector_with_r5_receipt_allows_runtime_adoption(self) -> None:
        root = self.copy_fixture("same_repo")
        receipt_path = root / "r5-active.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "runtime_stage": "active-candidate",
                    "authorization_receipt": {"status": "pass", "operator_confirmation": True},
                    "owner_lease": {"status": "pass", "owner": "main-session"},
                    "target_action_allowlist": {"targets": ["selector"], "actions": ["runtime-adoption"]},
                    "timeout_release": {"status": "pass", "released": True},
                    "rollback_pointer": "rollback-ref",
                    "rollback_ready": True,
                    "cleanup_evidence": {"status": "pass"},
                    "remote_publication_mutated": False,
                }
            ),
            encoding="utf-8",
        )

        payload = module.run_check(root, now=module.parse_now(NOW), active_candidate_receipt_path=receipt_path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertTrue(payload["selector_valid_for_routing"])
        self.assertTrue(payload["runtime_adoption_allowed"])
        self.assertEqual(payload["runtime_adoption_blockers"], [])

    def test_cross_repo_active_selector_fails_closed(self) -> None:
        root = self.copy_fixture("cross_repo")

        payload = module.run_check(root, now=module.parse_now(NOW))

        self.assertFalse(payload["ok"])
        self.assertFalse(payload["adoption_allowed"])
        self.assertIn("selector_ownership_invalid", payload["adoption_blockers"])
        self.assertTrue(any("cross-repository selector adoption is blocked" in e for e in payload["errors"]), payload["errors"])

    def test_stale_selector_with_no_auto_adoption_passes_but_blocks_adoption(self) -> None:
        root = self.copy_fixture("stale_no_auto_adoption")

        payload = module.run_check(root, now=module.parse_now(NOW))

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertFalse(payload["adoption_allowed"])
        self.assertIn("selector_stale", payload["adoption_blockers"])
        self.assertTrue(payload["warnings"], payload)

    def test_stale_selector_with_routing_eligible_passes_but_blocks_adoption(self) -> None:
        root = self.copy_fixture("stale_routing_eligible")

        payload = module.run_check(root, now=module.parse_now(NOW))

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertFalse(payload["adoption_allowed"])
        self.assertIn("selector_stale", payload["adoption_blockers"])
        self.assertTrue(
            any("stale but `routing_eligible` is true" in warning for warning in payload["warnings"]),
            payload["warnings"],
        )

    def test_missing_selector_reports_refresh_gap_without_error(self) -> None:
        root = self.make_root("selector-missing")

        payload = module.run_check(root, now=module.parse_now(NOW))

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertFalse(payload["adoption_allowed"])
        self.assertIn("selector_refresh_gap", payload["adoption_blockers"])

    def test_cli_emits_json_and_fails_cross_repo_fixture(self) -> None:
        root = self.copy_fixture("cross_repo")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--now", NOW, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
