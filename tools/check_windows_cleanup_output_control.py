#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "windows_cleanup_output_control"
INSTALLER_PATH = Path("tools/install-codex-user-level-team-mode.ps1")


REQUIRED_SOURCE_MARKERS = {
    "cmd_shim_function": "function Get-WindowsTaskkillCmdShimContent",
    "powershell_shim_function": "function Get-WindowsTaskkillPowerShellShimContent",
    "csharp_shim_source_function": "function Get-WindowsTaskkillCSharpShimSourceContent",
    "win_shims_directory": "win-shims",
    "taskkill_cmd_asset": "taskkill.cmd",
    "taskkill_ps1_asset": "taskkill.ps1",
    "taskkill_csharp_source_asset": "taskkill-shim-source.cs",
    "taskkill_exe_compat_switch": "[switch]$InstallTaskkillExeShim",
    "taskkill_exe_skip_switch": "[switch]$SkipTaskkillExeShim",
    "taskkill_exe_default_requested": "$taskkillExeShimRequested = -not [bool]$SkipTaskkillExeShim",
    "optional_taskkill_exe_compile_function": "function Try-CompileWindowsTaskkillExeShim",
    "taskkill_exe_framework64_compiler_fallback": "Microsoft.NET\\Framework64')",
    "taskkill_exe_framework32_compiler_fallback": "Microsoft.NET\\Framework')",
    "taskkill_exe_compile_local_temp_files": "taskkill-shim-compile-{0}.out",
    "taskkill_exe_success_exit_suppresses_output": "if (process.ExitCode == 0)",
    "optional_taskkill_exe_enabled_flag": "`$taskkillExeShimEnabled =",
    "taskkill_exe_runtime_presence_check": "Test-Path -LiteralPath `$taskkillExeShimPath",
    "optional_taskkill_exe_pathext_prepend": "`$env:PATHEXT = '.EXE;' + `$env:PATHEXT",
    "taskkill_exe_requested_report_field": "taskkill_exe_shim_requested",
    "optional_taskkill_exe_report_field": "taskkill_exe_shim_enabled",
    "scoped_cleanup_directory_variable": "`$cleanupShimDirectory = Join-Path `$PSScriptRoot 'win-shims'",
    "path_snapshot": "`$previousPath = [string]`$env:Path",
    "pathext_snapshot": "`$previousPathExt = [string]`$env:PATHEXT",
    "path_restore": "`$env:Path = `$previousPath",
    "pathext_restore": "`$env:PATHEXT = `$previousPathExt",
    "pathext_cmd_prepend": "`$env:PATHEXT = '.CMD;' + `$env:PATHEXT",
    "omx_state_enabled": "mcp_servers.omx_state.enabled=true",
    "omx_memory_enabled": "mcp_servers.omx_memory.enabled=true",
    "omx_code_intel_enabled": "mcp_servers.omx_code_intel.enabled=true",
    "omx_trace_enabled": "mcp_servers.omx_trace.enabled=true",
}


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    evidence: dict[str, bool] = {}

    installer = root / INSTALLER_PATH
    source = read_text(installer)
    if source is None:
        errors.append(f"Missing or unreadable installer source: {INSTALLER_PATH.as_posix()}")
        source = ""

    for name, marker in REQUIRED_SOURCE_MARKERS.items():
        present = marker in source
        evidence[name] = present
        if not present:
            errors.append(f"Missing cleanup-output control source marker: {name} ({marker})")

    if "Invoke-Expression" in source:
        warnings.append("Installer source contains Invoke-Expression; cleanup-output control did not add this, but review before broadening launcher logic.")

    if not errors:
        info.append("Windows cleanup-output control is script-backed and preserves direct omx_* MCP startup overrides.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "installer_path": INSTALLER_PATH.as_posix(),
        "evidence": evidence,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "evidence_markers": len(evidence),
            "present_markers": sum(1 for value in evidence.values() if value),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that wrapped codex-ohmy launches have script-backed Windows cleanup-output control."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
