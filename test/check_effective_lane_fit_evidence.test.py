from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_effective_lane_fit_evidence.py"

spec = importlib.util.spec_from_file_location("check_effective_lane_fit_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_NATIVE_EVIDENCE = """Run summary:
Effective lane selected: native_omx durable lane.
Task fit: worker-centric durable execution with worktree isolation, mailbox flow, and direct worker lifecycle control.
Backend family: one backend family at a time.
"""

VALID_LANGGRAPH_EVIDENCE = """Run summary:
Effective lane selected: LangGraph lane even though backend_default=langgraph and backend_ready=true are readiness only.
Task fit: graph-shaped multi-phase execution with checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues.
"""

VALID_HANDOFF_EVIDENCE = """Run summary:
The prior native_omx worker lifecycle was closed with an explicit handoff before switching to LangGraph.
New LangGraph lane is selected for graph-shaped multi-phase execution and checkpoint-driven recovery.
"""


class EffectiveLaneFitEvidenceCheckTest(unittest.TestCase):
    maxDiff = None

    def make_artifact_root(self, name: str) -> Path:
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

    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_repository_check(REPO_ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_missing_required_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = module.run_repository_check(Path(temp_dir))
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required effective lane-fit policy surface" in e for e in payload["errors"]))

    def test_missing_registry_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(snippets), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps({"schema_version": 1, "rules": []}), encoding="utf-8"
            )
            payload = module.run_repository_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(module.REGISTRY_RULE_ID in e for e in payload["errors"]), payload["errors"])

    def test_valid_native_omx_lane_passes(self) -> None:
        root = self.make_artifact_root("lane-native-valid")
        path = self.write_evidence(root, VALID_NATIVE_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("native_omx_lane", payload["detected"])

    def test_valid_langgraph_lane_passes(self) -> None:
        root = self.make_artifact_root("lane-langgraph-valid")
        path = self.write_evidence(root, VALID_LANGGRAPH_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("langgraph_lane", payload["detected"])
        self.assertIn("default_backend_not_enough", payload["detected"])

    def test_valid_backend_handoff_passes(self) -> None:
        root = self.make_artifact_root("lane-handoff-valid")
        path = self.write_evidence(root, VALID_HANDOFF_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("backend_family_consistency", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("lane-cli")
        path = self.write_evidence(root, VALID_LANGGRAPH_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_native_omx_without_worker_fit_fails(self) -> None:
        root = self.make_artifact_root("native-no-fit")
        path = self.write_evidence(root, "Effective lane selected: native_omx durable lane.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("worker-centric" in e for e in payload["errors"]), payload["errors"])

    def test_langgraph_without_graph_fit_fails(self) -> None:
        root = self.make_artifact_root("langgraph-no-fit")
        path = self.write_evidence(root, "Effective lane selected: LangGraph lane.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("graph-shaped" in e for e in payload["errors"]), payload["errors"])

    def test_backend_default_only_fails(self) -> None:
        root = self.make_artifact_root("default-only")
        path = self.write_evidence(root, "Effective lane selected: LangGraph because backend_default=langgraph and backend_ready=true.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("not enough" in e for e in payload["errors"]), payload["errors"])

    def test_mixed_backend_without_handoff_fails(self) -> None:
        root = self.make_artifact_root("mixed-no-handoff")
        path = self.write_evidence(
            root,
            "native_omx worker-centric durable execution and LangGraph graph-shaped multi-phase execution are both running for this selected task.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("explicit close/handoff" in e for e in payload["errors"]), payload["errors"])

    def test_silent_switch_fails(self) -> None:
        root = self.make_artifact_root("silent-switch")
        path = self.write_evidence(
            root,
            "Switched backend from native_omx to LangGraph without handoff while keeping selected lane running.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("silent" in e or "close/handoff" in e for e in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
