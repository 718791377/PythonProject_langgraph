#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "launcher_payload_context_boundary"
INSTALLER_PATH = Path("tools/install-codex-user-level-team-mode.ps1")

REQUIRED_SOURCE_MARKERS = {
    "model_instructions_path_function": "function Get-CodexUserLevelModelInstructionsFilePath",
    "model_instructions_state_filename": "user-level-team-mode-model-instructions.md",
    "model_instructions_writer_function": "function Write-CodexUserLevelModelInstructionsFile",
    "model_instructions_state_directory": "$directory = Split-Path -Parent $path",
    "model_instructions_directory_create": "New-Item -ItemType Directory -Force -Path $directory | Out-Null",
    "model_instructions_utf8_write": "Set-Content -LiteralPath $path -Value $Content -Encoding UTF8 -NoNewline",
    "startup_args_function": "function Get-CodexUserLevelTeamModeStartupArgs",
    "startup_args_writes_model_instructions_file": "$modelInstructionsFilePath = Write-CodexUserLevelModelInstructionsFile -Content $DeveloperInstructions",
    "startup_args_model_instructions_file_override": "model_instructions_file=",
    "startup_launcher_function": "function Get-StartupLauncherContent",
    "startup_launcher_uses_developer_instruction_builder": "`$instructions = Get-CodexUserLevelDeveloperInstructions -Status `$status",
    "startup_launcher_uses_startup_args_builder": "`$startupArgs = Get-CodexUserLevelTeamModeStartupArgs -Status `$status -DeveloperInstructions `$instructions",
    "startup_launcher_forwards_startup_args_before_user_args": "& `$nativeCodexCommandPath @startupArgs @Arguments",
}

FORBIDDEN_STARTUP_ARG_PATTERNS = {
    "inline_developer_instructions_override": "developer_instructions=",
    "inline_model_instruction_body_concat": "$startupArgs += @('-c', ('model_instructions='",
}

MODEL_INSTRUCTIONS_FILE_KEY_RE = re.compile(r"(?<![A-Za-z0-9_])model_instructions_file=")


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def function_body(source: str, name: str) -> str:
    pattern = re.compile(rf"(?ms)^function\s+{re.escape(name)}\b.*?(?=^function\s+|\Z)")
    match = pattern.search(source)
    return match.group(0) if match else ""


def startup_arg_lines(body: str) -> list[str]:
    return [line.strip() for line in body.splitlines() if "$startupArgs" in line]


def contains_model_instructions_file_key(text: str) -> bool:
    return bool(MODEL_INSTRUCTIONS_FILE_KEY_RE.search(text))


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

    startup_args_body = function_body(source, "Get-CodexUserLevelTeamModeStartupArgs")
    launcher_body = function_body(source, "Get-StartupLauncherContent")
    writer_body = function_body(source, "Write-CodexUserLevelModelInstructionsFile")

    for name, marker in REQUIRED_SOURCE_MARKERS.items():
        if name == "startup_args_model_instructions_file_override":
            present = contains_model_instructions_file_key(source)
        else:
            present = marker in source
        evidence[name] = present
        if not present:
            errors.append(f"Missing launcher-payload boundary source marker: {name} ({marker})")

    evidence["startup_args_body_found"] = bool(startup_args_body)
    evidence["startup_launcher_body_found"] = bool(launcher_body)
    evidence["writer_body_found"] = bool(writer_body)
    if not startup_args_body:
        errors.append("Cannot inspect Get-CodexUserLevelTeamModeStartupArgs body.")
    if not launcher_body:
        errors.append("Cannot inspect Get-StartupLauncherContent body.")
    if not writer_body:
        errors.append("Cannot inspect Write-CodexUserLevelModelInstructionsFile body.")

    forbidden_scopes = {
        "startup_args": startup_args_body,
        "startup_launcher": launcher_body,
    }
    for scope_name, scope in forbidden_scopes.items():
        for pattern_name, pattern in FORBIDDEN_STARTUP_ARG_PATTERNS.items():
            present = pattern in scope
            evidence[f"{scope_name}_omits_{pattern_name}"] = not present
            if present:
                errors.append(
                    f"{scope_name} contains forbidden inline startup payload marker `{pattern}`; "
                    "use model_instructions_file instead."
                )

    arg_lines = startup_arg_lines(startup_args_body)
    developer_instruction_arg_lines = [line for line in arg_lines if "DeveloperInstructions" in line]
    evidence["startup_args_never_embed_developer_instructions"] = not developer_instruction_arg_lines
    if developer_instruction_arg_lines:
        errors.append(
            "Get-CodexUserLevelTeamModeStartupArgs references $DeveloperInstructions while building $startupArgs; "
            "only Write-CodexUserLevelModelInstructionsFile may receive the large instruction body."
        )

    model_file_entries = [line for line in arg_lines if contains_model_instructions_file_key(line)]
    evidence["exactly_one_model_instructions_file_startup_arg"] = len(model_file_entries) == 1
    if len(model_file_entries) != 1:
        errors.append(
            "Get-CodexUserLevelTeamModeStartupArgs must add exactly one model_instructions_file startup override."
        )

    newline_in_startup_arg_literal = any("`n" in line or "`r" in line for line in arg_lines)
    evidence["startup_arg_literals_have_no_raw_newline_escape"] = not newline_in_startup_arg_literal
    if newline_in_startup_arg_literal:
        errors.append("Startup argument assembly contains raw newline escape markers; pass a short file reference instead.")

    if not errors:
        info.append("Launcher payload context boundary is file-backed, UTF-8 written, and short-argument based.")
    if "developer_instructions = \"\"\"" in source:
        warnings.append(
            "Installer still generates native agent TOML developer_instructions fields; this is allowed because the startup launcher does not pass them as command-line overrides."
        )

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
            "startup_arg_lines": len(arg_lines),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that wrapped Codex launchers pass large startup instructions through a file-backed short reference."
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
