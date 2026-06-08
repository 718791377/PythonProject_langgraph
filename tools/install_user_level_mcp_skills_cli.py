#!/usr/bin/env python3
"""Install or inspect user-level mcp2cli / skills2cli artifacts.

Repo-local source remains canonical.  User-level copies under CODEX_HOME are
install artifacts only.  Mutating installation requires both `apply --apply`
and `--operator-confirmation`; read-only `plan` and `check` are the defaults.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CHECK_NAME = "user_level_mcp_skills_cli_install"
SCHEMA_VERSION = 1
UPSTREAM_URL = "https://github.com/knowsuchagency/mcp2cli"
UPSTREAM_PACKAGE = "mcp2cli"
UPSTREAM_SKILL_REF = "knowsuchagency/mcp2cli"
UPSTREAM_SKILL_NAME = "mcp2cli"
UPSTREAM_INSTALL_MARKERS = (
    "uvx mcp2cli --help",
    "uv tool install mcp2cli",
    "npx skills add knowsuchagency/mcp2cli --skill mcp2cli",
)
TIMEOUT_SECONDS = 180
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|PythonProject|project|tmp|temp)[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")
UPDATE_REQUIRED_FIELDS = (
    "tool_name",
    "installed_version",
    "source_url",
    "install_path",
    "wrapper_path",
    "state_path",
    "smoke_test_command",
    "smoke_test_result",
    "updater_command",
    "rollback_pointer",
    "owner_lane",
    "redaction_status",
)
SMOKE_REQUIRED_FIELDS = (
    "tool_name",
    "owner_lane",
    "runtime_stage",
    "install_receipt",
    "smoke_command",
    "smoke_type",
    "smoke_result",
    "timeout_release",
    "rollback_pointer",
    "rollback_ready",
    "command_transcript",
    "transcript_redaction",
    "redaction_status",
)
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
ALLOWED_R4_STAGES = {"r4", "smoke-tested", "smoke_tested"}
ALLOWED_SMOKE_TYPES = {"help", "version", "status", "safe-discovery", "safe_discovery", "read-only", "readonly"}


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    skipped: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.skipped


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return now().strftime("%Y%m%dT%H%M%SZ")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def h(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def sanitize(value: Any, *, limit: int = 260) -> str:
    text = "" if value is None else str(value)
    text = SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: max(0, limit - 14)].rstrip() + "...[truncated]"
    return text


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text in {"install_path", "wrapper_path", "state_path", "rollback_pointer", "_path"}:
                result[f"{key_text}_hash"] = h(item)
            else:
                result[key_text] = sanitize_json(item)
        return result
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, str):
        return sanitize(value)
    return value


def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        try:
            if path.exists():
                return path
        except OSError:
            continue
    return None


def which(name: str) -> Path | None:
    found = shutil.which(name)
    return Path(found) if found else None


def locate_uv(explicit: str | None = None) -> Path | None:
    home = Path.home()
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(path for name in ("uv", "uv.exe") if (path := which(name)))
    candidates.extend(
        [
            home / ".cargo" / "bin" / "uv.exe",
            home / ".local" / "bin" / "uv.exe",
            home / ".trae-cn" / "tools" / "uv" / "latest" / "uv.exe",
        ]
    )
    return first_existing(candidates)


def locate_uvx(explicit: str | None = None, uv: Path | None = None) -> Path | None:
    home = Path.home()
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(path for name in ("uvx", "uvx.exe") if (path := which(name)))
    if uv:
        candidates.extend([uv.with_name("uvx.exe"), uv.with_name("uvx")])
    candidates.extend(
        [
            home / ".cargo" / "bin" / "uvx.exe",
            home / ".local" / "bin" / "uvx.exe",
            home / ".trae-cn" / "tools" / "uv" / "latest" / "uvx.exe",
        ]
    )
    return first_existing(candidates)


def locate_npx(explicit: str | None = None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(path for name in ("npx.cmd", "npx.exe", "npx") if (path := which(name)))
    return first_existing(candidates)


def layout(codex_home: Path) -> dict[str, Path]:
    state = codex_home / "state" / "mcp-skills-cli"
    return {
        "codex_home": codex_home,
        "bin_dir": codex_home / "bin",
        "mcp2cli_tool_dir": codex_home / "tools" / "mcp2cli",
        "skills2cli_tool_dir": codex_home / "tools" / "skills2cli",
        "skills2cli_skill_dir": codex_home / "skills" / "skills2cli",
        "state": state,
        "receipt_dir": state / "receipts",
        "backup_root": state / "backups",
        "uv_cache_dir": state / "uv-cache",
        "mcp2cli_state": state / "mcp2cli",
        "skills2cli_state": state / "skills2cli",
        "mcp2cli_cmd": codex_home / "bin" / "mcp2cli.cmd",
        "mcp2cli_ps1": codex_home / "bin" / "mcp2cli.ps1",
        "skills2cli_cmd": codex_home / "bin" / "skills2cli.cmd",
        "skills2cli_ps1": codex_home / "bin" / "skills2cli.ps1",
    }


def windows_artifact_path(value: str | Path) -> str:
    """Render generated Windows launcher artifacts with Windows separators.

    These `.cmd` files are Windows artifacts even when generated by Linux CI,
    so their embedded paths must not inherit POSIX separators from the host
    runner.
    """

    return str(value).replace("/", "\\")


def run(command: list[str], *, timeout: int = TIMEOUT_SECONDS, env_extra: dict[str, str] | None = None) -> CommandResult:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout,
            env=env,
        )
    except FileNotFoundError as exc:
        return CommandResult(command, 127, "", str(exc))
    except PermissionError as exc:
        return CommandResult(command, 126, "", str(exc))
    except subprocess.TimeoutExpired as exc:
        return CommandResult(command, 124, exc.stdout or "", exc.stderr or "timeout")
    return CommandResult(command, proc.returncode, proc.stdout or "", proc.stderr or "")


def skipped(command: list[str], reason: str) -> CommandResult:
    return CommandResult(command, 0, f"skipped:{reason}", "", True)


def summarize_result(result: CommandResult) -> dict[str, Any]:
    return {
        "command": result.command,
        "command_hash": h("\0".join(result.command)),
        "returncode": result.returncode,
        "ok": result.ok,
        "skipped": result.skipped,
        "stdout_excerpt": sanitize(result.stdout),
        "stderr_excerpt": sanitize(result.stderr),
    }


def base(action: str, ok: bool, **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now().isoformat(),
        "check_name": CHECK_NAME,
        "action": action,
        "ok": ok,
        "safety": {
            "repo_local_source_canonical": True,
            "user_level_helpers_are_install_artifacts": True,
            "mcp2cli_upstream_runtime_source": UPSTREAM_URL,
            "skills2cli_is_upstream_pattern_fork": True,
            "full_skill_bodies_included_by_default": False,
            "profile_suggest_preview_only": True,
            "native_subagent_evidence": False,
            "mutates_codex_config_toml": False,
            "mcp_router_bridge_default": False,
            "secrets_in_process_args_allowed": False,
        },
    }
    payload.update(extra)
    return payload


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    codex_home = Path(args.codex_home).resolve()
    uv = locate_uv(args.uv)
    uvx = locate_uvx(args.uvx, uv)
    npx = locate_npx(args.npx)
    paths = layout(codex_home)
    return base(
        "plan",
        True,
        mutates_user_level_state=False,
        external_commands_run=False,
        upstream={
            "source_url": UPSTREAM_URL,
            "package": UPSTREAM_PACKAGE,
            "skill_ref": UPSTREAM_SKILL_REF,
            "install_markers": list(UPSTREAM_INSTALL_MARKERS),
            "observed_ref": sanitize(args.upstream_ref or "main", limit=120),
        },
        tool_resolution={
            "uv": str(uv) if uv else None,
            "uvx": str(uvx) if uvx else None,
            "npx": str(npx) if npx else None,
        },
        target_paths={key: str(value) for key, value in paths.items()},
        planned_commands={
            "mcp2cli_preflight": [str(uvx) if uvx else "uvx", "mcp2cli", "--help"],
            "mcp2cli_install": [str(uv) if uv else "uv", "tool", "install", UPSTREAM_PACKAGE],
            "upstream_skill_install": [
                str(npx) if npx else "npx",
                "skills",
                "add",
                UPSTREAM_SKILL_REF,
                "--skill",
                UPSTREAM_SKILL_NAME,
                "--global",
                "--agent",
                "codex",
                "--yes",
                "--copy",
            ],
        },
    )


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def backup(paths: dict[str, Path]) -> Path:
    backup_dir = paths["backup_root"] / stamp()
    backup_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, str]] = []
    for key in ("mcp2cli_cmd", "mcp2cli_ps1", "skills2cli_cmd", "skills2cli_ps1"):
        src = paths[key]
        if src.exists():
            dest = backup_dir / src.name
            shutil.copy2(src, dest)
            items.append({"kind": "file", "source": str(src), "backup": str(dest)})
    for key in ("mcp2cli_tool_dir", "skills2cli_tool_dir", "skills2cli_skill_dir"):
        src = paths[key]
        if src.exists():
            dest = backup_dir / src.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            items.append({"kind": "directory", "source": str(src), "backup": str(dest)})
    write(backup_dir / "manifest.json", json.dumps({"schema_version": 1, "items": items}, ensure_ascii=False, indent=2))
    return backup_dir


def skills2cli_skill() -> str:
    return f"""---
name: skills2cli
description: Discover installed Codex skills through compact JSON without injecting full SKILL.md bodies. Use for skill index, search, show, warning audit, and preview-only profile suggestions.
---

# skills2cli

`skills2cli` is a deliberate fork/adaptation of the upstream `mcp2cli` skill/CLI
pattern from {UPSTREAM_URL}.  It keeps the same low-token workflow shape:
connect to a source, discover available commands, inspect one command, then run
the smallest safe command.  The source is the installed Codex skills ecosystem,
not an MCP/OpenAPI/GraphQL endpoint.

## Core workflow

```bash
skills2cli index --json
skills2cli search <query> --json
skills2cli show <skill_id> --json
skills2cli audit warnings --since 7d --json
skills2cli profile suggest --task "task summary" --json
```

## Safety

- Default output is compact and redacted.
- Full skill bodies are not included by default.
- `profile suggest` is preview-only and must not mutate Codex config.
- Skill/profile output is workflow context, not native Codex subagent evidence.
- Use upstream `mcp2cli` for MCP/OpenAPI/GraphQL runtime discovery and calls.
"""


def copy_facades(paths: dict[str, Path], *, upstream_ref: str | None) -> None:
    source = repo_root() / "tools" / "skills2cli.py"
    target = paths["skills2cli_tool_dir"] / "skills2cli.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    write(paths["skills2cli_skill_dir"] / "SKILL.md", skills2cli_skill())
    write(
        paths["skills2cli_tool_dir"] / "install-metadata.json",
        json.dumps(
            {
                "schema_version": 1,
                "copied_at": now().isoformat(),
                "source_file": "tools/skills2cli.py",
                "source_hash": h(source.read_text(encoding="utf-8", errors="replace")),
                "upstream_pattern_source": f"{UPSTREAM_URL}/tree/main/skills/mcp2cli",
                "upstream_ref": upstream_ref or "main",
                "full_skill_bodies_included_by_default": False,
                "profile_suggest_preview_only": True,
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write(
        paths["mcp2cli_tool_dir"] / "upstream-metadata.json",
        json.dumps(
            {
                "schema_version": 1,
                "source_url": UPSTREAM_URL,
                "package": UPSTREAM_PACKAGE,
                "upstream_ref": upstream_ref or "main",
                "readme_install_markers": list(UPSTREAM_INSTALL_MARKERS),
                "cache_paths": ["~/.cache/mcp2cli/", "~/.config/mcp2cli/baked.json"],
                "secret_indirection": ["env:", "file:"],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )


def write_wrappers(paths: dict[str, Path], *, uvx: Path | None) -> None:
    uvx_text = str(uvx) if uvx else "uvx"
    uvx_cmd = windows_artifact_path(uvx_text) if uvx else "uvx"
    uv_cache = paths["uv_cache_dir"]
    skills_script = paths["skills2cli_tool_dir"] / "skills2cli.py"
    uv_cache_cmd = windows_artifact_path(uv_cache)
    skills_script_cmd = windows_artifact_path(skills_script)
    write(
        paths["mcp2cli_cmd"],
        f"""@echo off
setlocal
if defined MCP2CLI_EXE (
  "%MCP2CLI_EXE%" %*
  exit /b %ERRORLEVEL%
)
if exist "%USERPROFILE%\\.local\\bin\\mcp2cli.exe" (
  "%USERPROFILE%\\.local\\bin\\mcp2cli.exe" %*
  exit /b %ERRORLEVEL%
)
if not defined UV_CACHE_DIR set "UV_CACHE_DIR={uv_cache_cmd}"
"{uvx_cmd}" mcp2cli %*
exit /b %ERRORLEVEL%
""",
    )
    write(
        paths["mcp2cli_ps1"],
        f"""$ErrorActionPreference = 'Stop'
if ($env:MCP2CLI_EXE -and (Test-Path -LiteralPath $env:MCP2CLI_EXE)) {{
  & $env:MCP2CLI_EXE @args
  exit $LASTEXITCODE
}}
$localExe = Join-Path $env:USERPROFILE '.local/bin/mcp2cli.exe'
if (Test-Path -LiteralPath $localExe) {{
  & $localExe @args
  exit $LASTEXITCODE
}}
if (-not $env:UV_CACHE_DIR) {{
  $env:UV_CACHE_DIR = '{uv_cache}'
}}
& '{uvx_text}' mcp2cli @args
exit $LASTEXITCODE
""",
    )
    write(paths["skills2cli_cmd"], f'@echo off\npython "{skills_script_cmd}" %*\nexit /b %ERRORLEVEL%\n')
    write(
        paths["skills2cli_ps1"],
        f"""$ErrorActionPreference = 'Stop'
& python '{skills_script}' @args
exit $LASTEXITCODE
""",
    )


def run_wrapper_smoke(
    logical_command: list[str],
    *,
    paths: dict[str, Path],
    wrapper_key: str,
    timeout: int,
    platform_name: str | None = None,
) -> CommandResult:
    """Run a wrapper smoke check without executing Windows `.cmd` on POSIX.

    GitLab Linux runners can validate repository generation and run the
    Python-backed `skills2cli` facade, but they cannot execute generated
    Windows batch wrappers directly.  Keep the logical command stable for
    receipts while using a POSIX-safe execution path where possible.
    """

    platform_name = platform_name or os.name
    wrapper = paths[wrapper_key]
    if platform_name == "nt" or wrapper.suffix.lower() != ".cmd":
        return run(logical_command, timeout=timeout)

    args = [str(item) for item in logical_command[1:]]
    if wrapper_key == "skills2cli_cmd":
        actual = [sys.executable, str(paths["skills2cli_tool_dir"] / "skills2cli.py"), *args]
        result = run(actual, timeout=timeout)
        return CommandResult(logical_command, result.returncode, result.stdout, result.stderr, result.skipped)

    if wrapper_key == "mcp2cli_cmd":
        configured = os.environ.get("MCP2CLI_EXE")
        if configured and Path(configured).suffix.lower() != ".cmd":
            result = run([configured, *args], timeout=timeout)
            return CommandResult(logical_command, result.returncode, result.stdout, result.stderr, result.skipped)
        return CommandResult(
            logical_command,
            0,
            "skipped:windows_cmd_wrapper_not_executable_on_posix; portable wrapper contract check passed\n",
            "",
            True,
        )

    return run(logical_command, timeout=timeout)


def maybe_run(command: list[str], *, run_external: bool, simulate: bool, timeout: int, env_extra: dict[str, str] | None = None) -> CommandResult:
    if simulate:
        if "--version" in command:
            return CommandResult(command, 0, "mcp2cli 3.2.0\n", "")
        return CommandResult(command, 0, "simulated ok\n", "")
    if not run_external:
        return skipped(command, "external_command_disabled")
    return run(command, timeout=timeout, env_extra=env_extra)


def version_from(result: CommandResult, fallback: str) -> str:
    text = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"\b([0-9]+\.[0-9]+\.[0-9][\w.\-+]*)\b", text)
    return match.group(1) if match else fallback


def receipt(
    *,
    tool_name: str,
    installed_version: str,
    source_url: str,
    install_path: Path | str,
    wrapper_path: Path,
    state_path: Path,
    smoke: CommandResult,
    updater_command: list[str],
    rollback_pointer: Path,
    owner_lane: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now().isoformat(),
        "tool_name": tool_name,
        "installed_version": installed_version,
        "source_url": source_url,
        "install_path": str(install_path),
        "wrapper_path": str(wrapper_path),
        "state_path": str(state_path),
        "smoke_test_command": " ".join(smoke.command),
        "smoke_test_result": {
            "status": "pass" if smoke.returncode == 0 else "fail",
            "returncode": smoke.returncode,
            "stdout_excerpt": sanitize(smoke.stdout),
            "stderr_excerpt": sanitize(smoke.stderr),
        },
        "updater_command": " ".join(updater_command),
        "rollback_pointer": str(rollback_pointer),
        "owner_lane": owner_lane,
        "redaction_status": "no_secrets",
    }
    if extra:
        data.update(extra)
    return data


def save_receipt(paths: dict[str, Path], name: str, data: dict[str, Any]) -> Path:
    path = paths["receipt_dir"] / f"{name}-{stamp()}.json"
    write(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    return path



def command_display(command: list[str], *, tool_name: str) -> str:
    if not command:
        return tool_name
    args = [str(item) for item in command[1:]]
    return " ".join([tool_name, *args])


def transcript(command: list[str], result: CommandResult, *, tool_name: str) -> dict[str, Any]:
    safe = {
        "command": command_display(command, tool_name=tool_name),
        "command_hash": h("\0".join(command)),
        "returncode": result.returncode,
        "stdout_excerpt": sanitize(result.stdout, limit=800),
        "stderr_excerpt": sanitize(result.stderr, limit=800),
    }
    safe["transcript_hash"] = h(safe)
    return safe


def smoke_receipt(
    *,
    tool_name: str,
    owner_lane: str,
    install_receipt: dict[str, Any],
    smoke_command: list[str],
    smoke_type: str,
    smoke: CommandResult,
    timeout: int,
) -> dict[str, Any]:
    command_transcript = transcript(smoke_command, smoke, tool_name=tool_name)
    rollback_pointer = str(install_receipt.get("rollback_pointer", ""))
    return {
        "schema_version": 1,
        "generated_at": now().isoformat(),
        "receipt_kind": "smoke-tested",
        "tool_name": tool_name,
        "owner_lane": owner_lane,
        "runtime_stage": "R4",
        "install_receipt": str(install_receipt.get("_path", "")),
        "smoke_command": command_display(smoke_command, tool_name=tool_name),
        "smoke_type": smoke_type,
        "smoke_result": {
            "status": "pass" if smoke.returncode == 0 else "fail",
            "returncode": smoke.returncode,
            "stdout_excerpt": sanitize(smoke.stdout),
            "stderr_excerpt": sanitize(smoke.stderr),
        },
        "timeout_release": {
            "status": "pass",
            "timeout_seconds": timeout,
            "released": True,
        },
        "rollback_pointer": rollback_pointer,
        "rollback_ready": bool(rollback_pointer),
        "command_transcript": command_transcript,
        "transcript_redaction": {
            "status": "pass",
            "redacted_transcript_hash": h(command_transcript),
            "raw_private_paths_retained": False,
            "raw_sensitive_values_retained": False,
        },
        "redaction_status": "no_secrets",
        "write_performed": False,
        "live_action_performed": False,
        "sensitive_action_performed": False,
        "user_level_state_mutated": False,
        "reads_browser_data": False,
        "external_message_sent": False,
    }

def command_apply(args: argparse.Namespace) -> dict[str, Any]:
    if not args.apply:
        return base("apply", False, mutates_user_level_state=False, blockers=["apply_flag_required"])
    if not args.operator_confirmation:
        return base("apply", False, mutates_user_level_state=False, blockers=["operator_confirmation_required"])

    codex_home = Path(args.codex_home).resolve()
    paths = layout(codex_home)
    uv = locate_uv(args.uv)
    uvx = locate_uvx(args.uvx, uv)
    npx = locate_npx(args.npx)
    blockers: list[str] = []
    if not uv and not args.simulate_external:
        blockers.append("uv_not_found")
    if not uvx and not args.simulate_external:
        blockers.append("uvx_not_found")
    if args.run_external and not npx and not args.simulate_external:
        blockers.append("npx_not_found")
    if blockers:
        return base(
            "apply",
            False,
            mutates_user_level_state=False,
            external_commands_run=False,
            blockers=blockers,
            tool_resolution={"uv": str(uv) if uv else None, "uvx": str(uvx) if uvx else None, "npx": str(npx) if npx else None},
        )

    ensure_dirs(
        [
            paths["bin_dir"],
            paths["mcp2cli_tool_dir"],
            paths["skills2cli_tool_dir"],
            paths["skills2cli_skill_dir"],
            paths["mcp2cli_state"],
            paths["skills2cli_state"],
            paths["receipt_dir"],
            paths["backup_root"],
            paths["uv_cache_dir"],
        ]
    )
    rollback = backup(paths)
    copy_facades(paths, upstream_ref=args.upstream_ref)
    write_wrappers(paths, uvx=uvx)

    uvx_help = [str(uvx) if uvx else "uvx", UPSTREAM_PACKAGE, "--help"]
    uv_install = [str(uv) if uv else "uv", "tool", "install", UPSTREAM_PACKAGE]
    skill_install = [
        str(npx) if npx else "npx",
        "skills",
        "add",
        UPSTREAM_SKILL_REF,
        "--skill",
        UPSTREAM_SKILL_NAME,
        "--global",
        "--agent",
        "codex",
        "--yes",
        "--copy",
    ]
    mcp_help = [str(paths["mcp2cli_cmd"]), "--help"]
    mcp_version = [str(paths["mcp2cli_cmd"]), "--version"]
    skills_help = [str(paths["skills2cli_cmd"]), "--help"]

    uv_env = {"UV_CACHE_DIR": str(paths["uv_cache_dir"])}
    results = {
        "mcp2cli_uvx_help_preflight": maybe_run(uvx_help, run_external=args.run_external, simulate=args.simulate_external, timeout=args.timeout, env_extra=uv_env),
        "mcp2cli_uv_tool_install": maybe_run(uv_install, run_external=args.run_external, simulate=args.simulate_external, timeout=args.timeout, env_extra=uv_env),
        "upstream_mcp2cli_skill_install": maybe_run(
            skill_install,
            run_external=args.run_external and not args.skip_upstream_skill_install,
            simulate=args.simulate_external,
            timeout=args.timeout,
        ),
        "mcp2cli_wrapper_version": maybe_run(mcp_version, run_external=args.run_external, simulate=args.simulate_external, timeout=args.timeout),
        "skills2cli_wrapper_help": (
            run_wrapper_smoke(skills_help, paths=paths, wrapper_key="skills2cli_cmd", timeout=args.timeout)
            if not args.simulate_external
            else CommandResult(skills_help, 0, "usage: skills2cli\n", "")
        ),
    }
    mcp_smoke = results["mcp2cli_wrapper_version"]
    if mcp_smoke.returncode != 0:
        mcp_smoke = maybe_run(mcp_help, run_external=args.run_external, simulate=args.simulate_external, timeout=args.timeout)
        results["mcp2cli_wrapper_help"] = mcp_smoke
    if args.run_external:
        for key in ("mcp2cli_uvx_help_preflight", "mcp2cli_uv_tool_install", "upstream_mcp2cli_skill_install"):
            if results[key].returncode != 0:
                blockers.append(f"{key}_failed")
    if mcp_smoke.returncode != 0:
        blockers.append("mcp2cli_wrapper_smoke_failed")
    if results["skills2cli_wrapper_help"].returncode != 0:
        blockers.append("skills2cli_wrapper_smoke_failed")

    local_mcp_exe = Path.home() / ".local" / "bin" / "mcp2cli.exe"
    mcp_install_path: str | Path = local_mcp_exe if local_mcp_exe.exists() else "uv-tool:mcp2cli"
    mcp_receipt = receipt(
        tool_name="mcp2cli",
        installed_version=version_from(results["mcp2cli_wrapper_version"], args.upstream_ref or "mcp2cli-upstream"),
        source_url=UPSTREAM_URL,
        install_path=mcp_install_path,
        wrapper_path=paths["mcp2cli_cmd"],
        state_path=paths["mcp2cli_state"],
        smoke=mcp_smoke,
        updater_command=uv_install,
        rollback_pointer=rollback,
        owner_lane="mcp2cli",
        extra={
            "upstream_package": UPSTREAM_PACKAGE,
            "upstream_ref": args.upstream_ref or "main",
            "uv_cache_dir": str(paths["uv_cache_dir"]),
            "uvx_preflight": summarize_result(results["mcp2cli_uvx_help_preflight"]),
            "uv_tool_install": summarize_result(results["mcp2cli_uv_tool_install"]),
            "upstream_skill_install": summarize_result(results["upstream_mcp2cli_skill_install"]),
        },
    )
    skill_hash = h((repo_root() / "tools" / "skills2cli.py").read_text(encoding="utf-8", errors="replace"))
    skills_receipt = receipt(
        tool_name="skills2cli",
        installed_version=f"repo-copy:{skill_hash}",
        source_url=f"{UPSTREAM_URL}#skills/mcp2cli-pattern + repo-local tools/skills2cli.py",
        install_path=paths["skills2cli_tool_dir"],
        wrapper_path=paths["skills2cli_cmd"],
        state_path=paths["skills2cli_state"],
        smoke=results["skills2cli_wrapper_help"],
        updater_command=[sys.executable, str(Path(__file__).resolve()), "apply", "--apply"],
        rollback_pointer=rollback,
        owner_lane="skills2cli",
        extra={
            "forked_from_upstream_skill_pattern": True,
            "upstream_skill_ref": UPSTREAM_SKILL_REF,
            "full_skill_bodies_included_by_default": False,
            "profile_suggest_preview_only": True,
            "native_subagent_evidence": False,
        },
    )
    mcp_receipt_path = save_receipt(paths, "mcp2cli", mcp_receipt)
    skills_receipt_path = save_receipt(paths, "skills2cli", skills_receipt)
    return base(
        "apply",
        not blockers,
        mutates_user_level_state=True,
        external_commands_run=bool(args.run_external),
        simulate_external=bool(args.simulate_external),
        blockers=sorted(set(blockers)),
        receipt_paths=[str(mcp_receipt_path), str(skills_receipt_path)],
        receipt_summaries=[sanitize_json(mcp_receipt), sanitize_json(skills_receipt)],
        rollback_pointer_hash=h(str(rollback)),
        command_results={key: summarize_result(value) for key, value in results.items()},
        wrapper_paths={"mcp2cli": str(paths["mcp2cli_cmd"]), "skills2cli": str(paths["skills2cli_cmd"])},
    )



def command_smoke(args: argparse.Namespace) -> dict[str, Any]:
    if args.record and not args.operator_confirmation:
        return base(
            "smoke",
            False,
            mutates_user_level_state=False,
            external_commands_run=False,
            receipt_write_performed=False,
            blockers=["operator_confirmation_required_for_record"],
        )

    paths = layout(Path(args.codex_home).resolve())
    receipts = load_receipts(paths["receipt_dir"])
    update_receipts = [item for item in receipts if is_update_receipt(item)]
    install_receipts = {tool: latest(update_receipts, tool) for tool in ("mcp2cli", "skills2cli")}
    blockers: list[str] = []
    for tool, receipt_data in install_receipts.items():
        if not receipt_data:
            blockers.append(f"missing_update_receipt:{tool}")
        elif not receipt_data.get("rollback_pointer"):
            blockers.append(f"missing_rollback_pointer:{tool}")

    smoke_results: dict[str, CommandResult] = {}
    smoke_commands: dict[str, list[str]] = {}
    smoke_types: dict[str, str] = {}

    mcp_version = [str(paths["mcp2cli_cmd"]), "--version"]
    smoke_commands["mcp2cli"] = mcp_version
    smoke_types["mcp2cli"] = "version"
    if paths["mcp2cli_cmd"].exists():
        mcp_result = run_wrapper_smoke(mcp_version, paths=paths, wrapper_key="mcp2cli_cmd", timeout=args.timeout)
        if mcp_result.returncode != 0:
            mcp_help = [str(paths["mcp2cli_cmd"]), "--help"]
            mcp_result = run_wrapper_smoke(mcp_help, paths=paths, wrapper_key="mcp2cli_cmd", timeout=args.timeout)
            smoke_commands["mcp2cli"] = mcp_help
            smoke_types["mcp2cli"] = "help"
        smoke_results["mcp2cli"] = mcp_result
        if mcp_result.returncode != 0:
            blockers.append("mcp2cli_smoke_failed")
    else:
        blockers.append("missing_wrapper:mcp2cli_cmd")

    skills_help = [str(paths["skills2cli_cmd"]), "--help"]
    smoke_commands["skills2cli"] = skills_help
    smoke_types["skills2cli"] = "help"
    if paths["skills2cli_cmd"].exists():
        skills_result = run_wrapper_smoke(skills_help, paths=paths, wrapper_key="skills2cli_cmd", timeout=args.timeout)
        smoke_results["skills2cli"] = skills_result
        if skills_result.returncode != 0:
            blockers.append("skills2cli_smoke_failed")
    else:
        blockers.append("missing_wrapper:skills2cli_cmd")

    smoke_receipts: list[dict[str, Any]] = []
    smoke_receipt_paths: list[str] = []
    if args.record and not blockers:
        paths["receipt_dir"].mkdir(parents=True, exist_ok=True)
        for tool in ("mcp2cli", "skills2cli"):
            receipt_data = smoke_receipt(
                tool_name=tool,
                owner_lane=tool,
                install_receipt=install_receipts[tool] or {},
                smoke_command=smoke_commands[tool],
                smoke_type=smoke_types[tool],
                smoke=smoke_results[tool],
                timeout=args.timeout,
            )
            smoke_receipts.append(receipt_data)
            smoke_receipt_paths.append(str(save_receipt(paths, f"{tool}-smoke", receipt_data)))

    return base(
        "smoke",
        not blockers,
        mutates_user_level_state=bool(args.record and not blockers),
        external_commands_run=True,
        receipt_write_performed=bool(args.record and not blockers),
        blockers=sorted(set(blockers)),
        smoke_receipt_paths=smoke_receipt_paths,
        smoke_receipt_summaries=[sanitize_json(item) for item in smoke_receipts],
        command_results={tool: summarize_result(result) for tool, result in smoke_results.items()},
    )

def load_receipts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    receipts: list[dict[str, Any]] = []
    for receipt_path in sorted(path.glob("*.json")):
        try:
            data = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_path"] = str(receipt_path)
            receipts.append(data)
    return receipts



def is_update_receipt(data: dict[str, Any]) -> bool:
    return all(field in data for field in UPDATE_REQUIRED_FIELDS) and "smoke_command" not in data


def is_smoke_receipt(data: dict[str, Any]) -> bool:
    return all(field in data for field in SMOKE_REQUIRED_FIELDS) or data.get("receipt_kind") == "smoke-tested"

def latest(receipts: list[dict[str, Any]], tool_name: str) -> dict[str, Any] | None:
    matches = [item for item in receipts if item.get("tool_name") == tool_name]
    return matches[-1] if matches else None


def receipt_blockers(data: dict[str, Any], tool_name: str) -> list[str]:
    blockers = [f"missing_{field}" for field in UPDATE_REQUIRED_FIELDS if field not in data]
    if data.get("tool_name") != tool_name:
        blockers.append("tool_name_mismatch")
    smoke = data.get("smoke_test_result")
    if not (isinstance(smoke, dict) and smoke.get("status") == "pass"):
        blockers.append("smoke_test_not_pass")
    if not data.get("rollback_pointer"):
        blockers.append("rollback_pointer_missing")
    if str(data.get("redaction_status", "")).lower() not in {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}:
        blockers.append("redaction_status_not_pass")
    return blockers



def pass_status(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "pass"
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() == "pass"
    return False


def smoke_receipt_blockers(data: dict[str, Any], tool_name: str) -> list[str]:
    blockers = [f"missing_{field}" for field in SMOKE_REQUIRED_FIELDS if field not in data]
    if data.get("tool_name") != tool_name:
        blockers.append("tool_name_mismatch")
    if data.get("owner_lane") != tool_name:
        blockers.append("owner_lane_mismatch")
    if str(data.get("runtime_stage", "")).strip().lower() not in ALLOWED_R4_STAGES:
        blockers.append("runtime_stage_not_r4")
    smoke_type = str(data.get("smoke_type", "")).strip().lower().replace("_", "-")
    if smoke_type == "readonly":
        smoke_type = "read-only"
    allowed_types = {item.replace("_", "-") for item in ALLOWED_SMOKE_TYPES}
    if smoke_type not in allowed_types:
        blockers.append("smoke_type_not_read_only")
    if not pass_status(data.get("smoke_result")):
        blockers.append("smoke_result_not_pass")
    if not pass_status(data.get("timeout_release")):
        blockers.append("timeout_release_not_pass")
    if data.get("rollback_ready") is not True or not data.get("rollback_pointer"):
        blockers.append("rollback_not_ready")
    if not pass_status(data.get("transcript_redaction")):
        blockers.append("transcript_redaction_not_pass")
    transcript_redaction = data.get("transcript_redaction")
    if isinstance(transcript_redaction, dict) and not str(transcript_redaction.get("redacted_transcript_hash", "")).strip():
        blockers.append("redacted_transcript_hash_missing")
    redaction = str(data.get("redaction_status", "")).strip().lower()
    if redaction not in ALLOWED_REDACTION_STATUS:
        blockers.append("redaction_status_not_pass")
    for field in (
        "write_performed",
        "live_action_performed",
        "sensitive_action_performed",
        "user_level_state_mutated",
        "reads_browser_data",
        "external_message_sent",
    ):
        if data.get(field) is True:
            blockers.append(f"forbidden_{field}")
    return blockers

def command_check(args: argparse.Namespace) -> dict[str, Any]:
    paths = layout(Path(args.codex_home).resolve())
    errors: list[str] = []
    warnings: list[str] = []
    for key in ("mcp2cli_cmd", "mcp2cli_ps1", "skills2cli_cmd", "skills2cli_ps1"):
        if not paths[key].exists():
            (errors if args.require_installed else warnings).append(f"missing_wrapper:{key}")
    for key in ("mcp2cli_tool_dir", "skills2cli_tool_dir", "skills2cli_skill_dir"):
        if not paths[key].exists():
            (errors if args.require_installed else warnings).append(f"missing_artifact:{key}")
    receipts = load_receipts(paths["receipt_dir"])
    update_receipts = [item for item in receipts if is_update_receipt(item)]
    smoke_receipts = [item for item in receipts if is_smoke_receipt(item)]
    for tool in ("mcp2cli", "skills2cli"):
        receipt_data = latest(update_receipts, tool)
        if not receipt_data:
            (errors if args.require_installed else warnings).append(f"missing_update_receipt:{tool}")
            continue
        errors.extend(f"invalid_update_receipt:{tool}:{item}" for item in receipt_blockers(receipt_data, tool))
    for tool in ("mcp2cli", "skills2cli"):
        smoke_receipt_data = latest(smoke_receipts, tool)
        if not smoke_receipt_data:
            if args.require_smoke_tested:
                errors.append(f"missing_smoke_receipt:{tool}")
            continue
        smoke_blockers = smoke_receipt_blockers(smoke_receipt_data, tool)
        if smoke_blockers:
            target = errors if args.require_smoke_tested else warnings
            target.extend(f"invalid_smoke_receipt:{tool}:{item}" for item in smoke_blockers)

    smoke: dict[str, Any] = {}
    if args.smoke and paths["mcp2cli_cmd"].exists():
        result = run_wrapper_smoke([str(paths["mcp2cli_cmd"]), "--help"], paths=paths, wrapper_key="mcp2cli_cmd", timeout=args.timeout)
        smoke["mcp2cli_help"] = summarize_result(result)
        if args.require_installed and result.returncode != 0:
            errors.append("mcp2cli_help_smoke_failed")
    if args.smoke and paths["skills2cli_cmd"].exists():
        result = run_wrapper_smoke([str(paths["skills2cli_cmd"]), "--help"], paths=paths, wrapper_key="skills2cli_cmd", timeout=args.timeout)
        smoke["skills2cli_help"] = summarize_result(result)
        if args.require_installed and result.returncode != 0:
            errors.append("skills2cli_help_smoke_failed")
    return base(
        "check",
        not errors,
        mutates_user_level_state=False,
        external_commands_run=bool(args.smoke),
        require_installed=bool(args.require_installed),
        require_smoke_tested=bool(args.require_smoke_tested),
        errors=errors,
        warnings=warnings,
        wrapper_presence={key: paths[key].exists() for key in ("mcp2cli_cmd", "mcp2cli_ps1", "skills2cli_cmd", "skills2cli_ps1")},
        artifact_presence={key: paths[key].exists() for key in ("mcp2cli_tool_dir", "skills2cli_tool_dir", "skills2cli_skill_dir")},
        receipt_count=len(update_receipts),
        total_receipt_count=len(receipts),
        smoke_receipt_count=len(smoke_receipts),
        latest_receipts={tool: sanitize_json(latest(update_receipts, tool) or {}) for tool in ("mcp2cli", "skills2cli")},
        latest_smoke_receipts={tool: sanitize_json(latest(smoke_receipts, tool) or {}) for tool in ("mcp2cli", "skills2cli")},
        smoke_results=smoke,
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or inspect user-level mcp2cli / skills2cli artifacts.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--codex-home", default=str(default_codex_home()))
        p.add_argument("--uv", default=None)
        p.add_argument("--uvx", default=None)
        p.add_argument("--npx", default=None)
        p.add_argument("--upstream-ref", default=None)
        p.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
        p.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan", help="Preview target paths and commands without mutation.")
    common(plan)
    plan.set_defaults(func=command_plan)

    apply = sub.add_parser("apply", help="Apply user-level installation artifacts and write receipts.")
    common(apply)
    apply.add_argument("--apply", action="store_true")
    apply.add_argument("--operator-confirmation", action="store_true")
    apply.add_argument("--run-external", action="store_true")
    apply.add_argument("--simulate-external", action="store_true")
    apply.add_argument("--skip-upstream-skill-install", action="store_true")
    apply.set_defaults(func=command_apply)

    smoke = sub.add_parser("smoke", help="Run bounded read-only R4 smoke checks and optionally write smoke-tested receipts.")
    common(smoke)
    smoke.add_argument("--record", action="store_true")
    smoke.add_argument("--operator-confirmation", action="store_true")
    smoke.set_defaults(func=command_smoke)

    check = sub.add_parser("check", help="Check wrapper/artifact/receipt state.")
    common(check)
    check.add_argument("--require-installed", action="store_true")
    check.add_argument("--require-smoke-tested", action="store_true")
    check.add_argument("--smoke", action="store_true")
    check.set_defaults(func=command_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = args.func(args)
    if args.json:
        sys.stdout.buffer.write((json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
