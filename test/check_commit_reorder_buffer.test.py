from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO_ROOT / "tools" / "check_commit_reorder_buffer.py"
HELPER_PATH = REPO_ROOT / "tools" / "commit_reorder_buffer.py"
spec = importlib.util.spec_from_file_location("check_commit_reorder_buffer", CHECK_PATH)
commit_rob = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = commit_rob
spec.loader.exec_module(commit_rob)


class CommitReorderBufferTest(unittest.TestCase):
    maxDiff = None

    def make_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".omx" / "commit-rob" / "entries").mkdir(parents=True)
        return root

    def write_entry(self, root: Path, name: str, **overrides: object) -> Path:
        entry = {
            "schema_version": 1,
            "entry_id": name,
            "state": "ready",
            "session_id": f"session-{name}",
            "implementation_plan": f"docs_bilingual/implementation_plans/{name}.md",
            "branch": f"feature/{name}",
            "worktree": str(root / name),
            "base_main": "abc123",
            "predicted_write_set": [f"docs/{name}.md"],
            "actual_write_set": [f"docs/{name}.md"],
            "hotspots": [],
            "dependencies": [],
            "gate_status": {
                "precommit_update_archive": "passed",
                "local_gate": "passed",
                "local_mr_review": "passed",
            },
            "evidence": [f"reports/{name}.md"],
        }
        entry.update(overrides)
        path = root / ".omx" / "commit-rob" / "entries" / f"{name}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_disjoint_ready_entries_pass(self) -> None:
        root = self.make_root()
        self.write_entry(root, "one")
        self.write_entry(root, "two")

        payload = commit_rob.evaluate(root)

        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["counts"]["ready"], 2)

    def test_hotspot_conflict_fails_without_dependency_ordering(self) -> None:
        root = self.make_root()
        self.write_entry(
            root,
            "left",
            predicted_write_set=["docs_bilingual/docs_registry.yaml"],
            actual_write_set=["docs_bilingual/docs_registry.yaml"],
            hotspots=["docs_bilingual/docs_registry.yaml"],
        )
        self.write_entry(
            root,
            "right",
            predicted_write_set=["docs_bilingual/docs_registry.yaml"],
            actual_write_set=["docs_bilingual/docs_registry.yaml"],
            hotspots=["docs_bilingual/docs_registry.yaml"],
        )

        payload = commit_rob.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("share hotspot" in error for error in payload["errors"]))

    def test_branch_prediction_mismatch_cannot_be_ready(self) -> None:
        root = self.make_root()
        self.write_entry(root, "mismatch", predicted_write_set=["docs/planned.md"], actual_write_set=["tools/unplanned.py"])

        payload = commit_rob.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("branch prediction mismatch" in error for error in payload["errors"]))

    def test_retired_entry_requires_rollback_main_and_evidence(self) -> None:
        root = self.make_root()
        self.write_entry(root, "retired", state="retired", rollback_ref="", local_main_commit="", evidence=[])

        payload = commit_rob.evaluate(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("rollback_ref" in error for error in payload["errors"]))
        self.assertTrue(any("local_main_commit" in error for error in payload["errors"]))
        self.assertTrue(any("evidence" in error for error in payload["errors"]))

    def test_backpressure_is_warning_not_failure(self) -> None:
        root = self.make_root()
        for index in range(3):
            self.write_entry(root, f"ready-{index}")

        payload = commit_rob.evaluate(root, max_ready=2)

        self.assertTrue(payload["ok"], payload)
        self.assertTrue(any("backpressure" in warning for warning in payload["warnings"]))

    def run_helper(self, root: Path, *args: str) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(HELPER_PATH), *args, "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_helper_predict_enqueue_status_retire_and_flush_round_trip(self) -> None:
        root = self.make_root()
        predicted = self.run_helper(
            root,
            "predict",
            "--entry-id",
            "roundtrip",
            "--session-id",
            "session-roundtrip",
            "--implementation-plan",
            "docs_bilingual/implementation_plans/example.md",
            "--branch",
            "feature/roundtrip",
            "--worktree",
            str(root / "wt"),
            "--base-main",
            "base123",
            "--write-set",
            "docs/example.md",
        )
        self.assertTrue(predicted["ok"])

        enqueued = self.run_helper(
            root,
            "enqueue",
            "--entry-id",
            "roundtrip",
            "--actual-write-set",
            "docs/example.md",
            "--gate",
            "precommit_update_archive=passed",
            "--gate",
            "local_gate=passed",
            "--gate",
            "local_mr_review=passed",
            "--evidence",
            "reports/roundtrip.md",
        )
        self.assertTrue(enqueued["ok"])
        self.assertTrue(commit_rob.evaluate(root)["ok"])

        status = self.run_helper(root, "status")
        self.assertEqual(status["counts"]["ready"], 1)

        retired = self.run_helper(
            root,
            "retire",
            "--entry-id",
            "roundtrip",
            "--rollback-ref",
            "refs/backup/example",
            "--local-main-commit",
            "def456",
            "--evidence",
            "reports/retired.md",
        )
        self.assertTrue(retired["ok"])
        self.assertTrue(commit_rob.evaluate(root)["ok"])

        self.run_helper(
            root,
            "predict",
            "--entry-id",
            "flush-me",
            "--session-id",
            "session-flush",
            "--implementation-plan",
            "docs_bilingual/implementation_plans/flush.md",
            "--branch",
            "feature/flush",
            "--base-main",
            "base123",
            "--write-set",
            "docs/flush.md",
        )
        flushed = self.run_helper(root, "flush", "--entry-id", "flush-me", "--reason", "cancelled-by-user")
        self.assertTrue(flushed["ok"])
        final_status = self.run_helper(root, "status")
        self.assertEqual(final_status["counts"]["retired"], 1)
        self.assertEqual(final_status["counts"]["flushed"], 1)


if __name__ == "__main__":
    unittest.main()
