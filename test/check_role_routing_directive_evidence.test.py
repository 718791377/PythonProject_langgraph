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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_role_routing_directive_evidence.py"

spec = importlib.util.spec_from_file_location("check_role_routing_directive_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_EVIDENCE = """Run summary:
Explicit LangGraph hard routing directive was received.
Capability chain, preflight, and task thresholds are satisfied, so the LangGraph lane adoption is selected and running.
Selected experts role selection: experts=analystxN, verifier.
Bounded multi-face research first round used analystxN analyst-only fan-out.
Verifier trigger: final acceptance for behavior-changing multi-file local integration.
"""


class RoleRoutingDirectiveEvidenceCheckTest(unittest.TestCase):
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
        self.assertTrue(any("Missing required role/directive policy surface" in e for e in payload["errors"]))

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
        root = self.make_artifact_root("role-directive-valid")
        path = self.write_evidence(root, VALID_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("hard_directive", payload["detected"])
        self.assertIn("threshold_adoption", payload["detected"])
        self.assertIn("role_minimality", payload["detected"])
        self.assertIn("analyst_first", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("role-directive-cli")
        path = self.write_evidence(root, VALID_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_directive_as_optional_preference_fails(self) -> None:
        root = self.make_artifact_root("directive-optional")
        path = self.write_evidence(root, "Explicit omx directive was treated as an optional preference.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("optional preferences" in e for e in payload["errors"]), payload["errors"])

    def test_directive_without_adoption_or_blocker_fails(self) -> None:
        root = self.make_artifact_root("directive-no-adoption")
        path = self.write_evidence(root, "User explicitly requested LangGraph hard routing directive.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("selected/running" in e for e in payload["errors"]), payload["errors"])

    def test_thresholds_satisfied_explanation_only_fails(self) -> None:
        root = self.make_artifact_root("explanation-only")
        path = self.write_evidence(
            root,
            "Capability chain, preflight, and task thresholds are satisfied, but session stayed in explanation-only mode.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("explanation-only" in e for e in payload["errors"]), payload["errors"])

    def test_role_without_trigger_fails(self) -> None:
        root = self.make_artifact_root("role-no-trigger")
        path = self.write_evidence(root, "Role selection: experts=architect.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("architect" in e for e in payload["errors"]), payload["errors"])

    def test_roles_added_because_available_fails(self) -> None:
        root = self.make_artifact_root("roles-available")
        path = self.write_evidence(root, "Role selection added extra roles because they are available.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("merely because" in e for e in payload["errors"]), payload["errors"])

    def test_bounded_multiface_without_analyst_first_fails(self) -> None:
        root = self.make_artifact_root("multiface-no-analyst")
        path = self.write_evidence(root, "Bounded multi-face research first round used researcher fan-out.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("analyst-only" in e for e in payload["errors"]), payload["errors"])

    def test_bounded_multiface_first_round_architect_fails(self) -> None:
        root = self.make_artifact_root("multiface-architect")
        path = self.write_evidence(
            root,
            "Bounded multi-face research first round used analystxN analyst-only fan-out plus architect.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("first round" in e for e in payload["errors"]), payload["errors"])

    def test_bounded_multiface_after_fanin_allows_architect(self) -> None:
        root = self.make_artifact_root("multiface-after-fanin")
        path = self.write_evidence(
            root,
            "Bounded multi-face research first round used analystxN analyst-only fan-out. "
            "After analyst fan-in shows architecture concerns, selected experts role selection: experts=architect. "
            "Architect trigger: architecture across 2+ modules and shared interface.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])


if __name__ == "__main__":
    unittest.main()
