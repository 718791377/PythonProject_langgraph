import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "tools" / "langgraph_durable_orchestrator" / "cli.py"


class LangGraphDurableOrchestratorStateReducersTest(unittest.TestCase):
    maxDiff = None

    def make_repo_root(self, name: str) -> Path:
        repo_root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        repo_root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(repo_root, ignore_errors=True))
        return repo_root

    def invoke(self, repo_root: Path, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), *args, "--repo-root", str(repo_root)],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return json.loads(result.stdout)

    def merge_branch(self, repo_root: Path, thread_id: str, payload: dict) -> dict:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(payload, handle)
            temp_path = Path(handle.name)
        self.addCleanup(lambda: temp_path.unlink(missing_ok=True))
        return self.invoke(repo_root, "merge-branch", "--thread-id", thread_id, "--payload-file", str(temp_path))

    def test_reducer_merge_is_deterministic_and_idempotent(self) -> None:
        repo_root = self.make_repo_root("reducers")
        run_payload = self.invoke(repo_root, "run", "--task", "reducers task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        payload_a = {
            "branch_id": "branch-a",
            "fanout_state": "partial",
            "reducer_channels": {
                "branch_findings": [
                    {"finding_id": "finding-2", "message": "second"},
                    {"finding_id": "finding-1", "message": "first"},
                ],
                "branch_evidence_refs": [
                    {"evidence_id": "evidence-1", "pointer": "trace:a"},
                ],
            },
        }
        merge_a = self.merge_branch(repo_root, thread_id, payload_a)
        merge_a_repeat = self.merge_branch(repo_root, thread_id, payload_a)
        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)

        findings = inspect_payload["thread"]["reducer_state"]["channels"]["branch_findings"]["items"]
        self.assertEqual([item["finding_id"] for item in findings], ["finding-1", "finding-2"])
        self.assertEqual(merge_a["reducer_projection"]["channel_item_counts"]["branch_findings"], 2)
        self.assertEqual(merge_a_repeat["reducer_projection"]["channel_item_counts"]["branch_findings"], 2)
        self.assertEqual(inspect_payload["reducer_projection"]["compatibility"], "reducer_aware")
        self.assertEqual(inspect_payload["reducer_projection"]["fanout_state"], "partial")
        self.assertEqual(sorted(inspect_payload["reducer_projection"]["source_records"]), ["branch:branch-a"])

    def test_invalid_multi_writer_single_writer_update_is_surfaced(self) -> None:
        repo_root = self.make_repo_root("reducers-invalid")
        run_payload = self.invoke(repo_root, "run", "--task", "reducers invalid task", "--phase", "execute-parallel")
        thread_id = run_payload["thread_id"]

        invalid_payload = {
            "branch_id": "branch-b",
            "fanout_state": "active",
            "single_writer_updates": {
                "phase": "stabilize",
            },
        }
        merge_payload = self.merge_branch(repo_root, thread_id, invalid_payload)

        self.assertTrue(merge_payload["reducer_projection"]["invalid_multi_writer_detected"])
        self.assertEqual(merge_payload["thread"]["phase"], "execute-parallel")
        invalid_updates = merge_payload["reducer_projection"]["invalid_multi_writer_updates"]
        self.assertEqual(invalid_updates[0]["field"], "phase")
        self.assertEqual(invalid_updates[0]["reason"], "single_writer_field_conflict")

    def test_pre_reducer_thread_is_classified_explicitly(self) -> None:
        repo_root = self.make_repo_root("pre-reducer")
        state_root = repo_root / ".omx" / "state" / "langgraph"
        for path in [state_root / "threads", state_root / "checkpoints", state_root / "interrupts", state_root / "store"]:
            path.mkdir(parents=True, exist_ok=True)
        thread_id = "pre:reducer:thread"
        backend_path = state_root / "backend.json"
        thread_path = state_root / "threads" / "pre__reducer__thread.json"
        backend_path.write_text(
            json.dumps(
                {
                    "backend": "langgraph",
                    "thread_id": thread_id,
                    "repo_root": str(repo_root),
                    "phase": "execute-parallel",
                    "updated_at": "2026-04-18T00:00:00Z",
                    "layout": {
                        "root": str(state_root),
                        "threads": str(state_root / "threads"),
                        "checkpoints": str(state_root / "checkpoints"),
                        "interrupts": str(state_root / "interrupts"),
                        "store": str(state_root / "store"),
                        "backend": str(backend_path),
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        thread_path.write_text(
            json.dumps(
                {
                    "thread_id": thread_id,
                    "repo_root": str(repo_root),
                    "phase": "execute-parallel",
                    "status": "running",
                    "updated_at": "2026-04-18T00:00:00Z",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        inspect_payload = self.invoke(repo_root, "inspect", "--thread-id", thread_id)
        self.assertEqual(inspect_payload["reducer_projection"]["compatibility"], "pre_reducer")
        self.assertEqual(inspect_payload["reducer_projection"]["reducer_channels_present"], [])
        self.assertFalse(inspect_payload["reducer_projection"]["invalid_multi_writer_detected"])


if __name__ == "__main__":
    unittest.main()
