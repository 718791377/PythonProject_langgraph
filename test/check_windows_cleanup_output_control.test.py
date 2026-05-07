import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_windows_cleanup_output_control.py"
INSTALLER_PATH = REPO_ROOT / "tools" / "install-codex-user-level-team-mode.ps1"


class WindowsCleanupOutputControlCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_installer_copy(self, root: Path, text: str) -> Path:
        path = root / "tools" / "install-codex-user-level-team-mode.ps1"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_current_repository(self) -> None:
        result = self.run_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertEqual(payload["counts"]["present_markers"], payload["counts"]["evidence_markers"])

    def test_fails_when_win_shims_marker_is_missing(self) -> None:
        root = self.make_root("windows-cleanup-missing-win-shims")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace("win-shims", "missing-shims")
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("win_shims_directory" in error for error in payload["errors"]))

    def test_fails_when_omx_startup_override_is_removed(self) -> None:
        root = self.make_root("windows-cleanup-missing-omx-override")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "mcp_servers.omx_trace.enabled=true",
            "mcp_servers.omx_trace.enabled=false",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("omx_trace_enabled" in error for error in payload["errors"]))

    def test_fails_when_taskkill_exe_compat_switch_is_removed(self) -> None:
        root = self.make_root("windows-cleanup-missing-taskkill-exe-control")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "[switch]$InstallTaskkillExeShim",
            "[switch]$RemovedTaskkillExeShim",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("taskkill_exe_compat_switch" in error for error in payload["errors"]))

    def test_fails_when_taskkill_exe_runtime_presence_check_is_removed(self) -> None:
        root = self.make_root("windows-cleanup-missing-taskkill-exe-runtime-check")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "Test-Path -LiteralPath `$taskkillExeShimPath",
            "Test-Path -LiteralPath `$removedTaskkillExeShimPath",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("taskkill_exe_runtime_presence_check" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
