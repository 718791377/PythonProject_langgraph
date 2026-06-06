from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "repo_local_selector_runtime.py"
CHECKER = ROOT / "tools" / "check_repo_local_selector_ownership.py"

spec = importlib.util.spec_from_file_location("repo_local_selector_runtime", SCRIPT)
runtime = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runtime)

checker_spec = importlib.util.spec_from_file_location("check_repo_local_selector_ownership", CHECKER)
checker = importlib.util.module_from_spec(checker_spec)
assert checker_spec and checker_spec.loader
checker_spec.loader.exec_module(checker)


NOW = "2026-06-05T08:00:00Z"


class RepoLocalSelectorRuntimeTest(unittest.TestCase):
    maxDiff = None

    def run_cli(self, root: Path, *args: str) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args, "--json"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic path
            raise AssertionError(f"invalid JSON stdout={proc.stdout!r} stderr={proc.stderr!r}") from exc
        return proc.returncode, payload

    def test_write_dry_run_reports_selector_without_mutating_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, payload = self.run_cli(
                root,
                "write",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "cold-start-smoke",
                "--lease-seconds",
                "3600",
                "--now",
                NOW,
            )

            self.assertEqual(code, 0, payload)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["mode"], "dry-run")
            self.assertFalse(payload["mutates_repo_local_state"])
            self.assertTrue(payload["selector_preview"]["routing_eligible"])
            self.assertEqual(payload["selector_preview"]["owner_session"], "session-a")
            self.assertFalse((root / ".omx" / "state" / "selectors" / "active.json").exists())
            self.assertIn("rollback_pointer", payload["receipt_preview"])

    def test_write_apply_refreshes_active_selector_and_lease_with_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, payload = self.run_cli(
                root,
                "write",
                "--apply",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "operator-confirmed-r4",
                "--lease-seconds",
                "3600",
                "--now",
                NOW,
            )

            self.assertEqual(code, 0, payload)
            selector_path = root / ".omx" / "state" / "selectors" / "active.json"
            selector = json.loads(selector_path.read_text(encoding="utf-8"))
            self.assertEqual(selector["repo_root"], str(root.resolve()))
            self.assertEqual(selector["owner_session"], "session-a")
            self.assertEqual(selector["backend_family"], "langgraph")
            self.assertEqual(selector["selected_reason"], "operator-confirmed-r4")
            self.assertIn("lease_expires_at", selector)
            self.assertIn("selector_revision", selector)
            self.assertIn("rollback_pointer", selector)
            self.assertEqual(selector["layout"]["active_selector"], str(selector_path))

            lease_path = root / ".omx" / "state" / "selectors" / "leases" / "session-a.json"
            lease = json.loads(lease_path.read_text(encoding="utf-8"))
            self.assertEqual(lease["selector_id"], selector["selector_id"])
            self.assertEqual(lease["lease_nonce"], selector["lease_nonce"])
            self.assertEqual(lease["status"], "active")

            receipts = list((root / ".omx" / "state" / "selectors" / "receipts").glob("*.json"))
            self.assertEqual(len(receipts), 1)
            receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
            self.assertEqual(receipt["runtime_stage"], "R3-selector-refresh")
            self.assertEqual(receipt["owner_session"], "session-a")
            self.assertEqual(receipt["redaction_status"], "pass")

            check = checker.run_check(root, now=checker.parse_now(NOW))
            self.assertTrue(check["ok"], check)
            self.assertTrue(check["adoption_allowed"], check)

    def test_write_apply_fails_closed_on_cross_repo_active_selector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selector_path = root / ".omx" / "state" / "selectors" / "active.json"
            selector_path.parent.mkdir(parents=True)
            selector_path.write_text(
                json.dumps(
                    {
                        "backend_family": "langgraph",
                        "selector_id": "selector-cross",
                        "repo_root": str(root / "other-repo"),
                        "worktree_id": "other",
                        "thread_id": "thread",
                        "session_scope_id": "session-old",
                        "last_heartbeat_at": NOW,
                        "routing_eligible": True,
                        "layout": {"root": str(selector_path.parent), "active_selector": str(selector_path)},
                    }
                ),
                encoding="utf-8",
            )

            code, payload = self.run_cli(
                root,
                "write",
                "--apply",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "must-not-overwrite-cross-repo",
                "--now",
                NOW,
            )

            self.assertEqual(code, 3)
            self.assertFalse(payload["ok"])
            self.assertIn("cross_repo_selector_adoption_blocked", payload["blockers"])
            still_cross = json.loads(selector_path.read_text(encoding="utf-8"))
            self.assertEqual(still_cross["selector_id"], "selector-cross")

    def test_release_requires_matching_selector_id_and_nonce(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, write_payload = self.run_cli(
                root,
                "write",
                "--apply",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "release-test",
                "--now",
                NOW,
            )
            self.assertEqual(code, 0, write_payload)
            selector_id = write_payload["selector"]["selector_id"]
            lease_nonce = write_payload["selector"]["lease_nonce"]

            bad_code, bad_payload = self.run_cli(
                root,
                "release",
                "--apply",
                "--selector-id",
                selector_id,
                "--lease-nonce",
                "wrong-nonce",
                "--owner-session",
                "session-a",
                "--now",
                NOW,
            )
            self.assertEqual(bad_code, 3)
            self.assertIn("lease_nonce_mismatch", bad_payload["blockers"])

            good_code, good_payload = self.run_cli(
                root,
                "release",
                "--apply",
                "--selector-id",
                selector_id,
                "--lease-nonce",
                lease_nonce,
                "--owner-session",
                "session-a",
                "--now",
                NOW,
            )
            self.assertEqual(good_code, 0, good_payload)
            selector = json.loads((root / ".omx" / "state" / "selectors" / "active.json").read_text(encoding="utf-8"))
            self.assertFalse(selector["routing_eligible"])
            self.assertEqual(selector["released_at"], NOW.replace("Z", "+00:00"))
            lease = json.loads((root / ".omx" / "state" / "selectors" / "leases" / "session-a.json").read_text(encoding="utf-8"))
            self.assertEqual(lease["status"], "released")
            self.assertEqual(good_payload["receipt"]["action"], "release")

    def test_stale_reclaim_requires_expired_selector_and_matching_nonce(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, write_payload = self.run_cli(
                root,
                "write",
                "--apply",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "reclaim-test",
                "--lease-seconds",
                "1",
                "--now",
                NOW,
            )
            self.assertEqual(code, 0, write_payload)
            selector_id = write_payload["selector"]["selector_id"]
            lease_nonce = write_payload["selector"]["lease_nonce"]

            early_code, early_payload = self.run_cli(
                root,
                "reclaim",
                "--apply",
                "--selector-id",
                selector_id,
                "--lease-nonce",
                lease_nonce,
                "--owner-session",
                "session-b",
                "--now",
                NOW,
            )
            self.assertEqual(early_code, 3)
            self.assertIn("selector_lease_not_expired", early_payload["blockers"])

            reclaim_code, reclaim_payload = self.run_cli(
                root,
                "reclaim",
                "--apply",
                "--selector-id",
                selector_id,
                "--lease-nonce",
                lease_nonce,
                "--owner-session",
                "session-b",
                "--now",
                "2026-06-05T08:00:02Z",
            )
            self.assertEqual(reclaim_code, 0, reclaim_payload)
            selector = json.loads((root / ".omx" / "state" / "selectors" / "active.json").read_text(encoding="utf-8"))
            self.assertFalse(selector["routing_eligible"])
            self.assertEqual(selector["reclaimed_by"], "session-b")
            self.assertEqual(selector["reclaim_reason"], "stale-selector-reclaim")
            lease = json.loads((root / ".omx" / "state" / "selectors" / "leases" / "session-a.json").read_text(encoding="utf-8"))
            self.assertEqual(lease["status"], "stale-reclaimed")
            self.assertEqual(reclaim_payload["receipt"]["action"], "stale-reclaim")

    def test_smoke_apply_writes_r4_smoke_tested_receipt_without_changing_selector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, write_payload = self.run_cli(
                root,
                "write",
                "--apply",
                "--backend-family",
                "langgraph",
                "--owner-session",
                "session-a",
                "--selected-reason",
                "smoke-test",
                "--now",
                NOW,
            )
            self.assertEqual(code, 0, write_payload)
            before = (root / ".omx" / "state" / "selectors" / "active.json").read_text(encoding="utf-8")

            smoke_code, smoke_payload = self.run_cli(
                root,
                "smoke",
                "--apply",
                "--owner-session",
                "session-a",
                "--timeout-seconds",
                "30",
                "--now",
                NOW,
            )

            self.assertEqual(smoke_code, 0, smoke_payload)
            self.assertTrue(smoke_payload["ok"])
            self.assertEqual(smoke_payload["receipt"]["runtime_stage"], "R4-user-level-smoke-runtime")
            self.assertEqual(smoke_payload["receipt"]["status_marker"], "smoke-tested")
            self.assertFalse(smoke_payload["mutates_active_selector"])
            self.assertTrue(smoke_payload["receipt"]["timeout_release"])
            self.assertTrue(smoke_payload["receipt"]["rollback_ready"])
            after = (root / ".omx" / "state" / "selectors" / "active.json").read_text(encoding="utf-8")
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
