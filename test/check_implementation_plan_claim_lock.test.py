from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO_ROOT / "tools" / "check_implementation_plan_claim_lock.py"
HELPER_PATH = REPO_ROOT / "tools" / "claim_implementation_plan.py"
spec = importlib.util.spec_from_file_location("check_implementation_plan_claim_lock", CHECK_PATH)
claim_lock = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = claim_lock
spec.loader.exec_module(claim_lock)


class ImplementationPlanClaimLockTest(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        plan_dir = root / "docs_bilingual" / "implementation_plans"
        plan_dir.mkdir(parents=True)
        (plan_dir / "example_plan.md").write_text(
            "---\n"
            "doc_id: example_plan\n"
            "lang: en\n"
            "status: active\n"
            "doc_class: implementation_plan\n"
            "zh_cn_path: docs_bilingual/implementation_plans/example_plan.zh-CN.md\n"
            "---\n"
            "# Example\n",
            encoding="utf-8",
        )
        (plan_dir / "example_plan.zh-CN.md").write_text(
            "---\n"
            "doc_id: example_plan\n"
            "lang: zh-CN\n"
            "status: active\n"
            "doc_class: implementation_plan\n"
            "translation_of: docs_bilingual/implementation_plans/example_plan.md\n"
            "---\n"
            "# Example zh\n",
            encoding="utf-8",
        )
        return root

    def write_claim(
        self,
        root: Path,
        name: str,
        *,
        status: str = "active",
        plan: str = "docs_bilingual/implementation_plans/example_plan.md",
        session_id: str | None = None,
        expires_at: str | None = None,
        extra: dict[str, object] | None = None,
    ) -> Path:
        claim_dir = root / ".omx" / "session-claims"
        claim_dir.mkdir(parents=True, exist_ok=True)
        data: dict[str, object] = {
            "schema_version": 1,
            "session_id": session_id or name,
            "status": status,
            "branch": f"feature/{name}",
            "worktree": str(root),
            "task_type": "implementation",
            "implementation_plan": plan,
            "implementation_plan_doc_id": "example_plan",
            "paths": [plan],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if expires_at is not None:
            data["expires_at"] = expires_at
        if extra:
            data.update(extra)
        path = claim_dir / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_passes_with_one_active_claim(self) -> None:
        root = self.make_root()
        self.write_claim(root, "one")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)

    def test_fails_for_conflicting_active_claims_for_same_plan_doc_id(self) -> None:
        root = self.make_root()
        self.write_claim(root, "left", plan="docs_bilingual/implementation_plans/example_plan.md")
        self.write_claim(root, "right", plan="docs_bilingual/implementation_plans/example_plan.zh-CN.md")

        payload = claim_lock.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("multiple active session claims" in error for error in payload["errors"]))

    def test_released_claim_is_ignored_for_conflict_detection(self) -> None:
        root = self.make_root()
        self.write_claim(root, "released", status="released")
        self.write_claim(root, "active")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)
        self.assertEqual(payload["counts"]["released_or_inactive_claims"], 1)

    def test_expired_active_claim_is_stale_warning_not_conflict(self) -> None:
        root = self.make_root()
        stale = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        self.write_claim(root, "stale", expires_at=stale)
        self.write_claim(root, "active")

        payload = claim_lock.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 1)
        self.assertEqual(payload["counts"]["stale_claims"], 1)
        self.assertTrue(any("stale" in warning for warning in payload["warnings"]))

    def test_malformed_implementation_plan_claim_fails_closed(self) -> None:
        root = self.make_root()
        self.write_claim(root, "bad", extra={"session_id": "", "implementation_plan": "../outside.md"})

        payload = claim_lock.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("session_id" in error for error in payload["errors"]))
        self.assertTrue(any("implementation_plan" in error for error in payload["errors"]))

    def test_helper_claim_and_release_round_trip(self) -> None:
        root = self.make_root()
        claim_cmd = [
            sys.executable,
            str(HELPER_PATH),
            "claim",
            "--root",
            str(root),
            "--plan",
            "docs_bilingual/implementation_plans/example_plan.md",
            "--session-id",
            "helper-session",
            "--branch",
            "feature/helper",
            "--worktree",
            str(root),
            "--expires-hours",
            "1",
        ]
        claimed = subprocess.run(claim_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(claimed.returncode, 0, claimed.stdout + claimed.stderr)
        claim_payload = json.loads(claimed.stdout)
        self.assertTrue(claim_payload["ok"])

        release_cmd = [
            sys.executable,
            str(HELPER_PATH),
            "release",
            "--root",
            str(root),
            "--session-id",
            "helper-session",
        ]
        released = subprocess.run(release_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        release_payload = json.loads(released.stdout)
        self.assertTrue(release_payload["ok"])

        payload = claim_lock.evaluate(root)
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["active_claims"], 0)
        self.assertEqual(payload["counts"]["released_or_inactive_claims"], 1)


if __name__ == "__main__":
    unittest.main()
