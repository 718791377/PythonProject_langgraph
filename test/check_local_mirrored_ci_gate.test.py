import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_local_mirrored_ci_gate.py"


class LocalMirroredCiGateCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_required_files(
        self,
        root: Path,
        *,
        gitlab_ci: str,
        github_ci: str,
        manifest: dict | None = None,
        local_gate_impl: str | None = None,
        run_guard_text: str | None = None,
        precommit_text: str | None = None,
        safety_registry: dict | None = None,
    ) -> None:
        (root / "tools" / "ci").mkdir(parents=True, exist_ok=True)
        (root / "tools").mkdir(parents=True, exist_ok=True)
        (root / "test").mkdir(parents=True, exist_ok=True)
        (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
        if manifest is None:
            manifest = {
                "schema_version": 1,
                "python_unittest": [
                    "check_local_mirrored_ci_gate.test.py",
                    "parallel_plan_checker_ci_integration.test.py",
                ],
                "node_mjs": [],
                "powershell_ps1": [],
            }
        (root / "tools" / "ci" / "ci_test_manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        for test_name in manifest.get("python_unittest", []):
            (root / "test" / test_name).write_text("import unittest\n\n", encoding="utf-8")
        if local_gate_impl is None:
            local_gate_impl = """
CHECK_NAME = 'local_ci_gate'
shared_with_remote_ci = True
guard_command = ['python', 'tools/run_openspec_guard.py']
flags = ['--refresh-managed-files', '--require-clean-git']
StepTimeoutSeconds = 'StepTimeoutSeconds'
timed_out = False
manifest = 'ci_test_manifest.json'
steps = []
steps.append(run_step('openspec_guard', guard_command, root, timeout))
steps.append(run_step('python_unittest', ['python', 'runner'], root, timeout))
steps.append(run_step('node_mjs_tests', ['node', 'runner'], root, timeout))
steps.append(run_step('powershell_ps1_tests', ['pwsh', 'runner'], root, timeout))
steps.append(run_step('git_diff_check', ['git', 'diff', '--check'], root, timeout))
reports = ['openspec-guard-report.json', 'local-gate-report.json']
"""
        (root / "tools" / "ci" / "local_gate.py").write_text(
            local_gate_impl,
            encoding="utf-8",
        )
        (root / "tools" / "ci" / "run_python_tests.py").write_text("print('ok')\n", encoding="utf-8")
        (root / "tools" / "ci" / "run_node_mjs_tests.mjs").write_text("console.log('ok');\n", encoding="utf-8")
        (root / "tools" / "ci" / "run_powershell_ps1_tests.ps1").write_text("Write-Host 'ok'\n", encoding="utf-8")
        (root / "tools" / "ci" / "local_gate.ps1").write_text(
            """
& python tools/ci/local_gate.py
""",
            encoding="utf-8",
        )
        (root / "tools" / "ci" / "local_mr_review.ps1").write_text(
            """
$result = @{ check_name = 'local_mr_review' }
git status --porcelain
$AllowDirty = $false
git diff --name-status
# Local MR Review changed-files command: git diff --name-status.
$changedFilesText = (Invoke-GitText -Arguments @('diff', '--name-status', 'main...HEAD')).stdout
# Local MR Review commit-log command: git log --oneline.
$logText = (Invoke-GitText -Arguments @('log', '--oneline', 'main..HEAD')).stdout
# Local MR Review diff-stat command: git diff --stat.
$diffStatText = (Invoke-GitText -Arguments @('diff', '--stat', 'main...HEAD')).stdout
$mergeTree = Invoke-GitText -Arguments @('merge-tree', $mergeBase, $BaseRef, $HeadRef)
""",
            encoding="utf-8",
        )
        (root / ".gitlab-ci.yml").write_text(gitlab_ci, encoding="utf-8")
        (root / ".github" / "workflows" / "openspec-guard.yml").write_text(github_ci, encoding="utf-8")
        if run_guard_text is None:
            run_guard_text = """
steps = [
  'check_precommit_update_archive',
  'check_safety_rule_script_backing',
  'check_local_mirrored_ci_gate',
]
"""
        (root / "tools" / "run_openspec_guard.py").write_text(run_guard_text, encoding="utf-8")
        if precommit_text is None:
            precommit_text = """
def check_new_tests_registered():
    return 'new_tests_must_be_registered_in_ci_manifest'

def check_new_checkers_registered():
    return 'new_checkers_must_be_registered_before_commit'
"""
        (root / "tools" / "check_precommit_update_archive.py").write_text(precommit_text, encoding="utf-8")
        if safety_registry is None:
            safety_registry = {
                "schema_version": 1,
                "rules": [
                    {
                        "id": "precommit-update-archive-gate",
                        "status": "implemented",
                        "script_controls": ["tools/check_precommit_update_archive.py"],
                        "guard_steps": ["check_precommit_update_archive"],
                    },
                    {
                        "id": "local-mirrored-ci-mr-gate",
                        "status": "implemented",
                        "script_controls": ["tools/ci/local_gate.ps1", "tools/ci/local_mr_review.ps1", "tools/check_local_mirrored_ci_gate.py"],
                        "guard_steps": ["check_local_mirrored_ci_gate"],
                    },
                    {
                        "id": "complete-local-flow-to-remote-gate",
                        "status": "implemented",
                        "script_controls": ["tools/complete_local_flow_to_remote_gate.py"],
                        "guard_steps": ["check_local_flow_scripted_enforcement"],
                    },
                ],
            }
        (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
            json.dumps(safety_registry),
            encoding="utf-8",
        )

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_when_remote_ci_calls_shared_local_gate(self) -> None:
        root = self.make_root("mirrored-ci-pass")
        self.write_required_files(
            root,
            gitlab_ci="script:\n  - pwsh -File tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
            github_ci="run: ./tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_passes_for_current_repository(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_when_remote_ci_duplicates_guard_logic(self) -> None:
        root = self.make_root("mirrored-ci-inline-fail")
        self.write_required_files(
            root,
            gitlab_ci="script:\n  - python tools/run_openspec_guard.py --root .\n",
            github_ci="run: ./tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("must call tools/ci/local_gate.ps1" in error for error in payload["errors"]))
        self.assertTrue(any("instead of run_openspec_guard.py directly" in error for error in payload["errors"]))

    def test_fails_when_required_manifest_test_is_missing(self) -> None:
        root = self.make_root("mirrored-ci-manifest-fail")
        self.write_required_files(
            root,
            gitlab_ci="script:\n  - pwsh -File tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
            github_ci="run: ./tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
            manifest={
                "schema_version": 1,
                "python_unittest": ["check_local_mirrored_ci_gate.test.py"],
                "node_mjs": [],
                "powershell_ps1": [],
            },
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("parallel_plan_checker_ci_integration.test.py" in error for error in payload["errors"]))

    def test_fails_when_remote_ci_runs_manifest_tests_directly(self) -> None:
        root = self.make_root("mirrored-ci-direct-tests-fail")
        self.write_required_files(
            root,
            gitlab_ci=(
                "script:\n"
                "  - pwsh -File tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n"
                "  - python tools/ci/run_python_tests.py --manifest tools/ci/ci_test_manifest.json\n"
            ),
            github_ci="run: ./tools/ci/local_gate.ps1 -RefreshManagedFiles -RequireCleanGit -Json\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("instead of running Python tests directly" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
