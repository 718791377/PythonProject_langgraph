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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_durable_artifact_state_surfaces.py"

spec = importlib.util.spec_from_file_location("check_durable_artifact_state_surfaces", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_EVIDENCE = """Run summary:
Explorer question was specific, well-scoped, and read-only file discovery; it did not replace implementation.
When the implementation patch became clear, a bounded code-changing worker task handled the patch.
Graph phases and checkpoint gates used LangGraph entrypoints through omx-langgraph-cli with repo-local .omx/state/langgraph/thread-42 state.
Automatic durable-team adoption read .omx/state/selectors/active.json; compatibility records under .omx/state/team/codex-auto-managed-team.json were context only.
Open-ended research fan-in happened before implementation starts; frozen implementation brief persisted at .omx/state/langgraph/briefs/feature.json with scope, non-goals, acceptance evidence, ownership boundaries, and unresolved risks.
Bug-finder, bug-rebutter, and bug-judge stayed burst read-only leader-side roles; unresolved candidates went to a survivor queue at .omx/state/langgraph/survivors/bug.json for debugger-lane follow-up.
Durable artifacts are documented at .omx/state/langgraph/artifacts/run.json.
"""


class DurableArtifactStateSurfacesCheckTest(unittest.TestCase):
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
        self.assertTrue(
            any("Missing required durable artifact/state-surface policy surface" in e for e in payload["errors"])
        )

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

    def test_valid_evidence_passes(self) -> None:
        root = self.make_artifact_root("durable-valid")
        path = self.write_evidence(root, VALID_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("exploration", payload["detected"])
        self.assertIn("langgraph_state", payload["detected"])
        self.assertIn("durable_artifact", payload["detected"])
        self.assertIn("frozen_research_handoff", payload["detected"])
        self.assertIn("adversarial_survivor_queue", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("durable-cli")
        path = self.write_evidence(root, VALID_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_explorer_replacing_code_worker_fails(self) -> None:
        root = self.make_artifact_root("explorer-replaces-worker")
        path = self.write_evidence(
            root,
            "Explorer did specific read-only file discovery even though the implementation patch is clear and code change is needed.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("must not replace" in e for e in payload["errors"]), payload["errors"])

    def test_graph_without_langgraph_state_fails(self) -> None:
        root = self.make_artifact_root("graph-no-state")
        path = self.write_evidence(root, "Graph phases and checkpoint gates used LangGraph entrypoints only in notes.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any(".omx/state/langgraph/" in e for e in payload["errors"]), payload["errors"])

    def test_durable_artifact_only_in_chat_fails(self) -> None:
        root = self.make_artifact_root("artifact-chat-only")
        path = self.write_evidence(root, "Durable artifacts and frozen brief exist only in transient chat context.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("transient chat context" in e for e in payload["errors"]), payload["errors"])

    def test_research_handoff_missing_brief_fields_fails(self) -> None:
        root = self.make_artifact_root("research-missing-fields")
        path = self.write_evidence(
            root,
            "Open-ended research fan-in before implementation starts saved a frozen implementation brief at .omx/state/langgraph/briefs/x.json with scope only.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("non-goals" in e for e in payload["errors"]), payload["errors"])
        self.assertTrue(any("acceptance evidence" in e for e in payload["errors"]), payload["errors"])

    def test_bug_triad_persistent_workers_fail(self) -> None:
        root = self.make_artifact_root("bug-triad-persistent")
        path = self.write_evidence(root, "bug-finder bug-rebutter bug-judge stayed as persistent workers.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("survivor queue" in e for e in payload["errors"]), payload["errors"])
        self.assertTrue(any("debugger-lane" in e for e in payload["errors"]), payload["errors"])

    def test_selector_without_active_authority_fails(self) -> None:
        root = self.make_artifact_root("selector-missing")
        path = self.write_evidence(
            root,
            "Automatic durable-team adoption used compatibility records under .omx/state/team/codex-auto-managed-team.json.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any(".omx/state/selectors/active.json" in e for e in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
