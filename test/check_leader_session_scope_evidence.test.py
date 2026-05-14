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
SCRIPT_PATH = REPO_ROOT / "tools" / "check_leader_session_scope_evidence.py"

spec = importlib.util.spec_from_file_location("check_leader_session_scope_evidence", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

VALID_EVIDENCE = """Run summary:
Current main Codex CLI session remains the leader for activation checks and release recommendations.
Leader-owned fan-in completed; evidence labeling recorded expert returned and absorbed plus main-session verification.
Leader-owned final integration completed after review.
No separate persistent leader pane replaces the current main session.
Startup or first activation trace used persistent_team=not_needed with threshold_not_met:single_execution_slice.
Routing decision used task-flow scoped adoption for the current task flow, not repository age.
Legacy resumed sessions are compatibility-scoped; current repository governance and capability-chain policy remain authoritative.
resume/continue/reload/restart/durable-state detection triggered activation check rerun.
"""


class LeaderSessionScopeEvidenceCheckTest(unittest.TestCase):
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
        self.assertTrue(any("Missing required leader/session scope policy surface" in e for e in payload["errors"]))

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
            (root / "tools" / "ci").mkdir(parents=True, exist_ok=True)
            (root / "tools" / "ci" / "ci_test_manifest.json").write_text(
                json.dumps({"schema_version": 1, "python_unittest": ["check_leader_session_scope_evidence.test.py"]}),
                encoding="utf-8",
            )
            payload = module.run_repository_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(module.REGISTRY_RULE_ID in e for e in payload["errors"]), payload["errors"])

    def test_missing_ci_manifest_entry_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(snippets), encoding="utf-8")
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
                                "script_controls": ["tools/check_leader_session_scope_evidence.py"],
                                "guard_steps": [module.GUARD_STEP],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (root / "tools" / "ci").mkdir(parents=True, exist_ok=True)
            (root / "tools" / "ci" / "ci_test_manifest.json").write_text(
                json.dumps({"schema_version": 1, "python_unittest": []}), encoding="utf-8"
            )
            payload = module.run_repository_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("CI test manifest" in e for e in payload["errors"]), payload["errors"])

    def test_valid_evidence_passes(self) -> None:
        root = self.make_artifact_root("leader-scope-valid")
        path = self.write_evidence(root, VALID_EVIDENCE)

        payload = module.run_evidence_check(path)

        self.assertTrue(payload["ok"], payload["errors"])
        self.assertIn("leader_ownership", payload["detected"])
        self.assertIn("no_separate_persistent_leader_pane", payload["detected"])
        self.assertIn("startup_threshold", payload["detected"])
        self.assertIn("task_flow_scope", payload["detected"])
        self.assertIn("legacy_boundary", payload["detected"])
        self.assertIn("retrofit_activation", payload["detected"])

    def test_cli_emits_json(self) -> None:
        root = self.make_artifact_root("leader-scope-cli")
        path = self.write_evidence(root, VALID_EVIDENCE)

        result = self.run_cli(path)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["check_name"], module.CHECK_NAME)
        self.assertTrue(payload["ok"])

    def test_missing_leader_ownership_fails(self) -> None:
        root = self.make_artifact_root("missing-leader")
        path = self.write_evidence(root, "Final report: work completed, but no leader ownership evidence was recorded.\n")

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("Leader evidence" in e for e in payload["errors"]), payload["errors"])

    def test_separate_persistent_leader_pane_replacement_fails(self) -> None:
        root = self.make_artifact_root("separate-leader")
        path = self.write_evidence(
            root,
            "Current main Codex CLI session remains the leader. Leader-owned fan-in and evidence labeling were present. "
            "Final integration was completed. separate persistent leader pane replaces the current main session.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("separate persistent leader pane" in e for e in payload["errors"]), payload["errors"])

    def test_startup_autolaunch_without_threshold_fails(self) -> None:
        root = self.make_artifact_root("startup-autolaunch")
        path = self.write_evidence(
            root,
            "Current main Codex CLI session remains the leader. Leader-owned fan-in and evidence labeling were present. "
            "Final integration was completed. startup auto-launches durable team on startup.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("auto-launch" in e for e in payload["errors"]), payload["errors"])

    def test_repo_status_as_adoption_basis_fails(self) -> None:
        root = self.make_artifact_root("repo-status")
        path = self.write_evidence(
            root,
            "Current main Codex CLI session remains the leader. Leader-owned fan-in and evidence labeling were present. "
            "Final integration was completed. adoption was based on whether the repository is new.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("current task flow" in e for e in payload["errors"]), payload["errors"])

    def test_legacy_resume_override_fails(self) -> None:
        root = self.make_artifact_root("legacy-override")
        path = self.write_evidence(
            root,
            "Current main Codex CLI session remains the leader. Leader-owned fan-in and evidence labeling were present. "
            "Final integration was completed. legacy resumed session overrides current repository governance and capability-chain policy. "
            "resume triggered activation check rerun.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("Legacy resumed sessions" in e for e in payload["errors"]), payload["errors"])

    def test_resume_continue_without_activation_check_fails(self) -> None:
        root = self.make_artifact_root("resume-no-activation")
        path = self.write_evidence(
            root,
            "Current main Codex CLI session remains the leader. Leader-owned fan-in and evidence labeling were present. "
            "Final integration was completed. resume and continue happened without rerun evidence.\n",
        )

        payload = module.run_evidence_check(path)

        self.assertFalse(payload["ok"])
        self.assertTrue(any("activation check" in e for e in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
