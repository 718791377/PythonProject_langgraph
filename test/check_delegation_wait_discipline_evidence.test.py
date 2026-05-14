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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_delegation_wait_discipline_evidence.py"

spec = importlib.util.spec_from_file_location("check_delegation_wait_discipline_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_EVIDENCE = """Run summary:
Delegation brief: leader identified immediate critical-path local work before delegation.
Delegated task is concrete, bounded, self-contained sidecar work and materially advances the main task.
Duplicate-work prevention: worker work is non-overlapping and disjoint from leader local work.
Code-changing worker brief includes file ownership for tools/check_example.py and disjoint write sets.
Worker is not alone in the codebase, must not revert or overwrite others, and must list changed paths.
wait_agent used sparingly only when blocked until result; leader continued meaningful non-overlapping leader work.
"""


def write_valid_registry(root: Path) -> None:
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
    (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rules": [
                    {
                        "id": module.REGISTRY_RULE_ID,
                        "prompt_reminders": [
                            "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"
                        ],
                        "script_controls": ["tools/check_delegation_wait_discipline_evidence.py"],
                        "guard_steps": [module.GUARD_STEP],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class DelegationWaitDisciplineEvidenceCheckTest(unittest.TestCase):
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
        self.assertTrue(any("Missing required delegation/wait discipline surface" in e for e in payload["errors"]))

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
        root = self.make_artifact_root("delegation-valid")
        path = self.write_evidence(root, VALID_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("delegation", payload["detected"])
        self.assertIn("code_worker", payload["detected"])
        self.assertIn("wait", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("delegation-cli")
        path = self.write_evidence(root, VALID_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_delegation_without_critical_path_planning_fails(self) -> None:
        root = self.make_artifact_root("delegation-no-critical")
        path = self.write_evidence(
            root,
            "Delegated task is concrete, bounded, self-contained sidecar work and materially advances. "
            "Duplicate-work prevention is non-overlapping.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("immediate critical-path local work" in e for e in payload["errors"]), payload["errors"])

    def test_vague_delegation_fails(self) -> None:
        root = self.make_artifact_root("delegation-vague")
        path = self.write_evidence(
            root,
            "Delegated expert work after leader identified immediate critical-path local work. "
            "Duplicate-work prevention is non-overlapping.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("concrete delegated task" in e for e in payload["errors"]), payload["errors"])
        self.assertTrue(any("bounded delegated task" in e for e in payload["errors"]), payload["errors"])

    def test_code_worker_without_ownership_fails(self) -> None:
        root = self.make_artifact_root("code-worker-no-ownership")
        path = self.write_evidence(
            root,
            "Code-changing worker has a bounded patch. Worker is not alone in the codebase and must list changed paths.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("file/module ownership" in e for e in payload["errors"]), payload["errors"])

    def test_wait_without_non_overlapping_work_or_blocker_fails(self) -> None:
        root = self.make_artifact_root("wait-no-work")
        path = self.write_evidence(root, "wait_agent used sparingly after delegation.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("non-overlapping leader work" in e for e in payload["errors"]), payload["errors"])

    def test_reflexive_wait_fails(self) -> None:
        root = self.make_artifact_root("wait-reflexive")
        path = self.write_evidence(
            root,
            "wait_agent used sparingly but waiting by reflex; leader continued meaningful non-overlapping leader work.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("reflexive" in e or "silent" in e for e in payload["errors"]), payload["errors"])

    def test_no_delegation_marker_warns_without_failing(self) -> None:
        root = self.make_artifact_root("no-delegation")
        path = self.write_evidence(root, "No delegated expert work occurred in this local-only task.\n")

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("no_delegation", payload["detected"])


if __name__ == "__main__":
    unittest.main()
