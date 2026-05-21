import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_pyside6_packaging_opt_in_contract.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_pyside6_packaging_opt_in_contract import PREFLIGHT_DOC, PREFLIGHT_SCRIPT, add_packaging_evidence  # noqa: E402
from check_pyside6_project_opt_in_contract import make_valid_fixture  # noqa: E402


class PySide6PackagingOptInContractTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def make_project(self, name: str, tool: str = "PyInstaller") -> Path:
        project = make_valid_fixture(REPO_ROOT, f"{name}-{uuid.uuid4().hex[:8]}")
        self.addCleanup(lambda: shutil.rmtree(project, ignore_errors=True))
        add_packaging_evidence(project, tool=tool)
        return project

    def run_check(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args, "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_repository_self_test_passes(self) -> None:
        result = self.run_check("--root", str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "self-test")
        self.assertEqual(payload["check_name"], "pyside6_packaging_opt_in_contract")
        self.assertIn("valid", payload["samples"])

    def test_valid_packaging_fixture_passes(self) -> None:
        project = self.make_project("pyside6-packaging-valid", tool="Nuitka")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["selected_packaging_tool"], "Nuitka")
        self.assertEqual(payload["packaging_state"], "preflight_ready")
        self.assertEqual(payload["build_output_evidence"]["output_directory"], "dist")
        self.assertEqual(payload["build_output_evidence"]["generated_artifacts"], ["build", "dist"])
        self.assertTrue(payload["build_output_evidence"]["output_directory_project_relative"])
        self.assertTrue(payload["build_output_evidence"]["generated_artifacts_project_relative"])
        self.assertFalse(payload["build_output_evidence"]["packaged_inferred_from_output_evidence"])
        self.assertFalse(payload["build_output_evidence"]["release_ready_inferred_from_output_evidence"])
        self.assertFalse(payload["packaged"])
        self.assertFalse(payload["release_ready"])

    def test_missing_preflight_script_fails(self) -> None:
        project = self.make_project("pyside6-packaging-missing-preflight")
        (project / PREFLIGHT_SCRIPT).unlink()
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("Missing required PySide6 packaging opt-in files" in error for error in payload["errors"]))

    def test_ambiguous_packaging_tool_fails(self) -> None:
        project = self.make_project("pyside6-packaging-ambiguous-tool")
        (project / PREFLIGHT_DOC).write_text(
            "packaging_tool: PyInstaller\n"
            "packaging_tool: Nuitka\n"
            "qt platform plugin resource icon dpi chinese font startup log data directory antivirus "
            "reproducible build output directory separate approval rollback\n",
            encoding="utf-8",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("exactly one packaging_tool marker" in error for error in payload["errors"]))

    def test_missing_data_exclusion_and_approval_evidence_fails(self) -> None:
        project = self.make_project("pyside6-packaging-missing-evidence")
        script = project / PREFLIGHT_SCRIPT
        script.write_text(
            script.read_text(encoding="utf-8")
            .replace("  excludes_credentials = $true\n", "")
            .replace("  release_signing_distribution_requires_separate_approval = $true\n", ""),
            encoding="utf-8",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("excludes_credentials" in error for error in payload["errors"]))
        self.assertTrue(any("release_signing_distribution_requires_separate_approval" in error for error in payload["errors"]))

    def test_unsafe_release_or_destructive_script_fails(self) -> None:
        project = self.make_project("pyside6-packaging-unsafe-script")
        with (project / PREFLIGHT_SCRIPT).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\nStart-Process signtool.exe\nRemove-Item build\n")
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("Start-Process" in error for error in payload["errors"]))
        self.assertTrue(any("Remove-Item" in error for error in payload["errors"]))

    def test_absolute_output_directory_fails(self) -> None:
        project = self.make_project("pyside6-packaging-absolute-output")
        script = project / PREFLIGHT_SCRIPT
        script.write_text(
            script.read_text(encoding="utf-8").replace('  output_directory = "dist"\n', '  output_directory = "C:/temp/dist"\n'),
            encoding="utf-8",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("output_directory must be a project-relative" in error for error in payload["errors"]))
        self.assertFalse(payload["build_output_evidence"]["output_directory_project_relative"])

    def test_generated_artifacts_must_include_project_relative_output_directory(self) -> None:
        project = self.make_project("pyside6-packaging-unsafe-artifacts")
        script = project / PREFLIGHT_SCRIPT
        script.write_text(
            script.read_text(encoding="utf-8").replace('  generated_artifacts = @("build", "dist")\n', '  generated_artifacts = @("build", "../dist")\n'),
            encoding="utf-8",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("generated_artifacts must be project-relative" in error for error in payload["errors"]))
        self.assertTrue(any("generated_artifacts must include the output_directory" in error for error in payload["errors"]))

    def test_missing_generated_artifacts_fails(self) -> None:
        project = self.make_project("pyside6-packaging-missing-artifacts")
        script = project / PREFLIGHT_SCRIPT
        script.write_text(
            script.read_text(encoding="utf-8").replace('  generated_artifacts = @("build", "dist")\n', ''),
            encoding="utf-8",
        )
        result = self.run_check("--root", str(REPO_ROOT), "--project-root", str(project))
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any("generated_artifacts" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
