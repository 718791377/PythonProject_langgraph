import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_windows_cleanup_output_control.py"
LAUNCHER_BOUNDARY_SCRIPT_PATH = REPO_ROOT / "tools" / "check_launcher_payload_context_boundary.py"
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


    def run_launcher_boundary_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LAUNCHER_BOUNDARY_SCRIPT_PATH), "--root", str(root), "--json"],
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

    def test_requires_taskkill_exe_default_to_be_windows_only(self) -> None:
        root = self.make_root("windows-cleanup-missing-taskkill-platform-gate")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "$taskkillExeShimRequested = [bool]$InstallTaskkillExeShim -or ($isWindowsPlatform -and -not [bool]$SkipTaskkillExeShim)",
            "$taskkillExeShimRequested = -not [bool]$SkipTaskkillExeShim",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("taskkill_exe_default_requested" in error for error in payload["errors"]))

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

    def test_fails_when_login_profile_cleanup_shim_bridge_is_removed(self) -> None:
        root = self.make_root("windows-cleanup-missing-login-profile-bridge")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY",
            "CODEX_USER_LEVEL_REMOVED_CLEANUP_SHIM_DIRECTORY",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("cleanup_shim_env_name" in error for error in payload["errors"]))
        self.assertTrue(any("profile_cleanup_shim_bridge" in error for error in payload["errors"]))

    def test_fails_when_framework_compiler_fallback_is_removed(self) -> None:
        root = self.make_root("windows-cleanup-missing-framework-csc-fallback")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "(Join-Path $env:WINDIR 'Microsoft.NET\\Framework64'),\n"
            "      (Join-Path $env:WINDIR 'Microsoft.NET\\Framework')",
            "(Join-Path $env:WINDIR 'Missing.NET\\Framework64'),\n"
            "      (Join-Path $env:WINDIR 'Missing.NET\\Framework')",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("taskkill_exe_framework64_compiler_fallback" in error for error in payload["errors"]))
        self.assertTrue(any("taskkill_exe_framework32_compiler_fallback" in error for error in payload["errors"]))

    def test_requires_taskkill_exe_success_output_suppression_before_forwarding(self) -> None:
        root = self.make_root("windows-cleanup-missing-success-suppression")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "if (process.ExitCode == 0)",
            "if (false && process.ExitCode == 0)",
        )
        self.write_installer_copy(root, source)

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("taskkill_exe_success_exit_suppresses_output" in error for error in payload["errors"]))

    def test_chinese_taskkill_success_line_is_benign_when_exit_code_is_zero(self) -> None:
        # The generated EXE shim suppresses *all* stdout/stderr when taskkill exits 0,
        # so localized success lines such as this Chinese Windows output never reach
        # the resumed Codex session.
        chinese_success = "成功: 已终止 PID 32992 (属于 PID 16312 子进程)的进程。"
        source = INSTALLER_PATH.read_text(encoding="utf-8")
        self.assertIn("if (process.ExitCode == 0)", source)
        self.assertIn("return 0;", source)
        self.assertLess(source.index("if (process.ExitCode == 0)"), source.index("Console.Error.Write(stdout);"))
        self.assertTrue(chinese_success.startswith("成功: 已终止 PID "))


    def test_launcher_payload_boundary_passes_for_current_repository(self) -> None:
        result = self.run_launcher_boundary_check(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["evidence"]["exactly_one_model_instructions_file_startup_arg"])
        self.assertTrue(payload["evidence"]["startup_args_never_embed_developer_instructions"])

    def test_launcher_payload_boundary_fails_when_model_file_override_is_removed(self) -> None:
        root = self.make_root("launcher-payload-missing-model-file")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "model_instructions_file=",
            "removed_model_instructions_file=",
        )
        self.write_installer_copy(root, source)

        result = self.run_launcher_boundary_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("model_instructions_file" in error for error in payload["errors"]))

    def test_launcher_payload_boundary_fails_when_developer_instructions_are_inlined(self) -> None:
        root = self.make_root("launcher-payload-inline-developer-instructions")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "('model_instructions_file=' + (ConvertTo-CodexUserLevelTomlLiteralString -Value $modelInstructionsFilePath))",
            "('developer_instructions=' + $DeveloperInstructions)",
        )
        self.write_installer_copy(root, source)

        result = self.run_launcher_boundary_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("developer_instructions" in error for error in payload["errors"]))

    def test_launcher_payload_boundary_requires_utf8_state_file_write(self) -> None:
        root = self.make_root("launcher-payload-missing-utf8-write")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "Set-Content -LiteralPath $path -Value $managedContent -Encoding UTF8 -NoNewline",
            "Set-Content -LiteralPath $path -Value $Content -Encoding ASCII -NoNewline",
        )
        self.write_installer_copy(root, source)

        result = self.run_launcher_boundary_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("model_instructions_utf8_write" in error for error in payload["errors"]))

    def test_launcher_payload_boundary_requires_launcher_to_use_startup_arg_builder(self) -> None:
        root = self.make_root("launcher-payload-missing-startup-arg-builder")
        source = INSTALLER_PATH.read_text(encoding="utf-8").replace(
            "`$startupArgs = Get-CodexUserLevelTeamModeStartupArgs -Status `$status -DeveloperInstructions `$instructions",
            "`$startupArgs = @('-c', 'notify=[]')",
        )
        self.write_installer_copy(root, source)

        result = self.run_launcher_boundary_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("startup_args_builder" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
