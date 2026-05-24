from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from project_moe_gui import CLI_CONTRACT, TOOLCHAIN_NAME, TOOLCHAIN_VERSION
from project_moe_gui.gui_shell import GUI_SHELL_CONTRACT


SCHEMA_VERSION = 1
DEFAULT_MODE_CLI = Path("tools/thesis_moe_mode.py")
DEFAULT_SHARED_RUNTIME_ROOT = Path(r"D:\PythonProject_langgraph\.shared_runtimes\pyside6")
CONFIG_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.config.json")
MANIFEST_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.install-manifest.json")
LAUNCHER_RELATIVE = Path("tools/project_moe_gui/launcher.py")
README_RELATIVE = Path("tools/project_moe_gui/README.md")
CMD_RELATIVE = Path("project-moe-gui.cmd")
MANAGED_RELATIVES = [LAUNCHER_RELATIVE, CONFIG_RELATIVE, README_RELATIVE, CMD_RELATIVE]
PRIVATE_PROMPT_AGENT_DIR = Path(".codex/agents")
PRIVATE_PROMPT_STATE_DIR = Path(".omx/state")
PRIVATE_PROMPT_GUI_MANAGED_DIR = Path("tools/project_moe_gui")
PROJECT_EVIDENCE = [".git", "AGENTS.md", "pyproject.toml", "requirements.txt", "README.md", "setup.cfg", "setup.py", "poetry.lock", "uv.lock"]
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")
READ_CLI_CONTRACT_COMMANDS = ("project-status", "list-sessions", "status")
READ_ASSERTION_COMMANDS = ("assert-on",)
PHASE1_EXPECTED_WRITE_COMMANDS = ("project-on", "project-off", "on", "off", "assert-on")
BOOTSTRAP_BLOCKER_CAPABILITIES = {
    "blocked:missing_agent_toml": "agent_toml",
    "blocked:missing_private_prompt_source": "private_prompt_source",
    "blocked:missing_mode_cli": "mode_cli",
    "blocked:phase1_read_command_surface_incomplete": "mode_cli_read_commands",
    "blocked:phase1_write_command_surface_incomplete": "mode_cli_write_commands",
    "blocked:missing_phase1_wrapper": "phase1_wrapper",
    "blocked:missing_moe_activation_hook": "startup_activation_hook",
    "blocked:missing_phase1_operator_docs": "operator_docs",
}
PHASE1_REMEDIATION_PHASE_ORDER = {
    "preflight": 10,
    "bootstrap": 20,
    "repair": 30,
    "execute-read-contract": 40,
    "manual-review": 90,
}
PHASE1_REMEDIATION_ACTIONS: dict[str, dict[str, Any]] = {
    "blocked:dirty_target_project": {
        "category": "target_git_state",
        "phase": "preflight",
        "action": "classify_or_clean_dirty_target_worktree",
        "description": "Classify, preserve, commit, stash, or otherwise explicitly handle dirty target-project files before Phase 1 writes.",
        "requires_target_project_write": False,
    },
    "blocked:git_status_unavailable": {
        "category": "target_git_state",
        "phase": "preflight",
        "action": "restore_read_only_git_status_preflight",
        "description": "Restore a read-only git status surface for the target project before readiness can be trusted.",
        "requires_target_project_write": False,
    },
    "blocked:missing_agent_toml": {
        "category": "agent_toml",
        "phase": "bootstrap",
        "action": "create_project_moe_agent_toml",
        "description": "Create the project-local MOE agent TOML with required top-level fields and standard Project MOE extension sections.",
        "requires_target_project_write": True,
    },
    "blocked:agent_toml_missing_required_fields": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "complete_agent_toml_required_fields",
        "description": "Add non-empty name, description, and developer_instructions to the project-local MOE agent TOML.",
        "requires_target_project_write": True,
    },
    "blocked:agent_name_mismatch": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "align_agent_toml_name_with_requested_agent",
        "description": "Align the agent TOML top-level name with the Project MOE GUI configuration and readiness command.",
        "requires_target_project_write": True,
    },
    "blocked:agent_toml_missing_extension_sections": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "add_project_moe_standard_extension_sections",
        "description": "Add [project], [moe], [dispatch], and [extensions] standard sections to the existing agent TOML.",
        "requires_target_project_write": True,
    },
    "blocked:agent_project_boundary_invalid": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "repair_agent_project_boundary_fields",
        "description": "Repair [project] scope, namespace, and private prompt policy fields to match the Project MOE boundary contract.",
        "requires_target_project_write": True,
    },
    "blocked:agent_state_namespace_mismatch": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "align_agent_state_namespace",
        "description": "Align the agent TOML namespace and state paths with the requested Project MOE state namespace.",
        "requires_target_project_write": True,
    },
    "blocked:agent_moe_boundary_invalid": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "repair_agent_moe_boundary_fields",
        "description": "Repair [moe] kind, family, manual-enable, and state-path fields to the Project MOE standard.",
        "requires_target_project_write": True,
    },
    "blocked:agent_dispatch_boundary_incomplete": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "repair_agent_dispatch_boundary",
        "description": "Use brief-based dispatch, forbid full-history custom-role dispatch, and configure supported fallback paths.",
        "requires_target_project_write": True,
    },
    "blocked:invalid_agent_toml": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "repair_agent_toml_syntax",
        "description": "Fix the target agent TOML syntax before any semantic Project MOE checks can be trusted.",
        "requires_target_project_write": True,
    },
    "blocked:tomllib_unavailable": {
        "category": "checker_runtime",
        "phase": "preflight",
        "action": "run_checker_with_tomllib_capable_python",
        "description": "Run readiness with Python 3.11+ or an environment that can parse TOML.",
        "requires_target_project_write": False,
    },
    "blocked:missing_private_prompt_source": {
        "category": "private_prompt_source",
        "phase": "bootstrap",
        "action": "create_project_private_prompt_source_placeholder",
        "description": "Create the project-private prompt source placeholder inside the target project without copying private content elsewhere.",
        "requires_target_project_write": True,
    },
    "blocked:private_prompt_path_invalid": {
        "category": "private_prompt_source",
        "phase": "repair",
        "action": "repair_private_prompt_source_path",
        "description": "Replace the private prompt source with a safe project-relative path.",
        "requires_target_project_write": True,
    },
    "blocked:private_prompt_source_inside_agent_dir": {
        "category": "private_prompt_source",
        "phase": "repair",
        "action": "move_private_prompt_source_outside_agent_dir",
        "description": "Move the private prompt source out of .codex/agents and keep agent definitions separate from private prompt text.",
        "requires_target_project_write": True,
    },
    "blocked:private_prompt_source_inside_state": {
        "category": "private_prompt_source",
        "phase": "repair",
        "action": "move_private_prompt_source_outside_state_dir",
        "description": "Move the private prompt source out of .omx/state so runtime state is not treated as prompt source material.",
        "requires_target_project_write": True,
    },
    "blocked:private_prompt_source_managed_by_toolchain": {
        "category": "private_prompt_source",
        "phase": "repair",
        "action": "move_private_prompt_source_outside_gui_managed_artifacts",
        "description": "Keep private prompt source outside Project MOE GUI managed artifacts.",
        "requires_target_project_write": True,
    },
    "blocked:missing_mode_cli": {
        "category": "mode_cli",
        "phase": "bootstrap",
        "action": "create_phase1_mode_cli",
        "description": "Create the target project's Phase 1 mode CLI with read and write command surfaces.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_read_command_surface_incomplete": {
        "category": "mode_cli",
        "phase": "bootstrap",
        "action": "add_phase1_read_command_surface",
        "description": "Add project-status, list-sessions, status, and assert-on read-command tokens and JSON contract support.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_write_command_surface_incomplete": {
        "category": "mode_cli",
        "phase": "bootstrap",
        "action": "add_phase1_write_command_surface",
        "description": "Add project-on, project-off, on, off, and assert-on command-surface support.",
        "requires_target_project_write": True,
    },
    "blocked:mode_cli_path_invalid": {
        "category": "mode_cli",
        "phase": "repair",
        "action": "repair_mode_cli_path",
        "description": "Use a safe project-relative mode CLI path.",
        "requires_target_project_write": True,
    },
    "blocked:mode_cli_timeout": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_timeout",
        "description": "Make read-contract commands fast and bounded before GUI readiness can depend on them.",
        "requires_target_project_write": True,
    },
    "blocked:mode_cli_invocation_failed": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_invocation",
        "description": "Restore executable target mode CLI invocation for read-only readiness checks.",
        "requires_target_project_write": True,
    },
    "blocked:mode_cli_failed": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_read_contract_exit_codes",
        "description": "Make read-contract commands return supported exit codes and JSON envelopes.",
        "requires_target_project_write": True,
    },
    "blocked:mode_cli_invalid_json": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_json_output",
        "description": "Ensure read-contract commands emit valid JSON.",
        "requires_target_project_write": True,
    },
    "blocked:cli_contract_invalid": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_json_object_contract",
        "description": "Return a JSON object for every read-contract command.",
        "requires_target_project_write": True,
    },
    "blocked:cli_envelope_missing_fields": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_common_envelope_fields",
        "description": "Add schema_version, command, ok, token, and cli_contract envelope fields.",
        "requires_target_project_write": True,
    },
    "blocked:cli_command_echo_mismatch": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_command_echo",
        "description": "Make each JSON envelope echo the invoked command.",
        "requires_target_project_write": True,
    },
    "blocked:cli_read_command_not_ok": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_read_command_ok_tokens",
        "description": "Make read commands return ok=true and token=ok unless the command has an explicitly supported fail-closed token.",
        "requires_target_project_write": True,
    },
    "blocked:cli_contract_mismatch": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_contract_version",
        "description": "Align the target CLI contract with project-moe-cli-v1.",
        "requires_target_project_write": True,
    },
    "blocked:cli_contract_private_field_exposed": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "redact_private_fields_from_mode_cli_json",
        "description": "Remove raw session identifiers, private prompt text, and other private fields from CLI JSON.",
        "requires_target_project_write": True,
    },
    "blocked:project_status_contract_invalid": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_project_status_json_contract",
        "description": "Expose project default state and registered session counts in project-status --json.",
        "requires_target_project_write": True,
    },
    "blocked:list_sessions_contract_invalid": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_list_sessions_json_contract",
        "description": "Return redacted session rows and counts from list-sessions --json.",
        "requires_target_project_write": True,
    },
    "blocked:status_contract_invalid": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_status_json_contract",
        "description": "Expose effective_enabled, effective_source, and safe session metadata from status --json.",
        "requires_target_project_write": True,
    },
    "blocked:assert_on_contract_invalid": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_assert_on_read_only_contract",
        "description": "Make assert-on a read-only assertion with stable enabled/disabled/blocker tokens.",
        "requires_target_project_write": True,
    },
    "blocked:assert_on_not_read_only": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "remove_write_result_fields_from_assert_on",
        "description": "Remove write-result fields from assert-on output so it remains a read-only assertion.",
        "requires_target_project_write": True,
    },
    "blocked:missing_phase1_wrapper": {
        "category": "phase1_wrapper",
        "phase": "bootstrap",
        "action": "create_phase1_cmd_wrappers",
        "description": "Create thesis-moe-on.cmd and thesis-moe-off.cmd wrappers that delegate to the target mode CLI with --json.",
        "requires_target_project_write": True,
    },
    "blocked:wrapper_path_invalid": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "repair_wrapper_paths",
        "description": "Use safe project-relative wrapper paths.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_wrapper_not_bound_to_mode_cli": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "bind_wrappers_to_mode_cli",
        "description": "Make each wrapper invoke the configured target mode CLI.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_wrapper_command_mismatch": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "repair_wrapper_command_targets",
        "description": "Make on/off wrappers call the expected project-on/project-off commands.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_wrapper_json_output_missing": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "add_json_flag_to_phase1_wrappers",
        "description": "Pass --json through wrapper commands so automation can consume stable machine-readable output.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_wrapper_unsafe_shell_surface": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "remove_unsafe_shell_surface_from_wrappers",
        "description": "Remove arbitrary argument passthrough, shell chaining, redirection, and file-operation command tokens from wrappers.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_wrapper_direct_state_surface": {
        "category": "phase1_wrapper",
        "phase": "repair",
        "action": "remove_direct_state_access_from_wrappers",
        "description": "Make wrappers delegate state access to the mode CLI instead of touching .omx/state directly.",
        "requires_target_project_write": True,
    },
    "blocked:missing_moe_activation_hook": {
        "category": "startup_activation_hook",
        "phase": "bootstrap",
        "action": "add_moe_startup_activation_hook",
        "description": "Add startup/resume/continue/reload/phase-change status --json checks to the target project startup surface.",
        "requires_target_project_write": True,
    },
    "blocked:moe_activation_hook_incomplete": {
        "category": "startup_activation_hook",
        "phase": "repair",
        "action": "complete_moe_startup_activation_hook",
        "description": "Extend the existing MOE activation hook to cover all required activation checkpoints.",
        "requires_target_project_write": True,
    },
    "blocked:startup_hook_path_invalid": {
        "category": "startup_activation_hook",
        "phase": "repair",
        "action": "repair_startup_hook_candidate_paths",
        "description": "Use safe project-relative startup hook candidate paths.",
        "requires_target_project_write": True,
    },
    "blocked:missing_phase1_operator_docs": {
        "category": "operator_docs",
        "phase": "bootstrap",
        "action": "create_phase1_operator_docs",
        "description": "Create target-project operator documentation for Project MOE commands and wrappers.",
        "requires_target_project_write": True,
    },
    "blocked:phase1_operator_docs_incomplete": {
        "category": "operator_docs",
        "phase": "repair",
        "action": "complete_phase1_operator_docs",
        "description": "Document all required Project MOE commands, --json reads, --session-id, and wrapper entrypoints.",
        "requires_target_project_write": True,
    },
    "blocked:operator_doc_path_invalid": {
        "category": "operator_docs",
        "phase": "repair",
        "action": "repair_operator_doc_candidate_paths",
        "description": "Use safe project-relative operator documentation candidate paths.",
        "requires_target_project_write": True,
    },
}
DEFAULT_ON_WRAPPER = Path("thesis-moe-on.cmd")
DEFAULT_OFF_WRAPPER = Path("thesis-moe-off.cmd")
DEFAULT_STARTUP_HOOK_CANDIDATES = (
    Path("AGENTS.md"),
    Path("docs_bilingual/project_startup_summary.md"),
    Path("docs_bilingual/project_startup_summary.zh-CN.md"),
    Path("docs/project_startup_summary.md"),
)
DEFAULT_OPERATOR_DOC_CANDIDATES = (
    Path("docs_bilingual/operations/thesis_moe_mode_usage.zh-CN.md"),
    Path("docs_bilingual/operations/thesis_moe_mode_usage.md"),
    Path("docs/operations/thesis_moe_mode_usage.md"),
    Path("docs/thesis_moe_mode_usage.md"),
)
DEFAULT_PRIVATE_PROMPT_SOURCE = Path("MOE.md")
DEFAULT_BOOTSTRAP_STARTUP_HOOK = Path("AGENTS.md")
DEFAULT_BOOTSTRAP_OPERATOR_DOC = Path("docs_bilingual/operations/thesis_moe_mode_usage.zh-CN.md")
COMMON_CLI_ENVELOPE_KEYS = ("schema_version", "command", "ok", "token", "cli_contract")
STATUS_EFFECTIVE_SOURCES = {"session", "project-default", "fail-closed"}
ASSERT_ON_TOKENS = {"ok", "disabled", "blocked:moe_disabled"}
PHASE1_OPERATOR_DOC_REQUIRED_TOKENS = (
    "thesis_moe_mode.py",
    "project-on",
    "project-off",
    "project-status --json",
    "list-sessions --json",
    "status --json",
    "assert-on",
    "--session-id",
    "thesis-moe-on.cmd",
    "thesis-moe-off.cmd",
)
PHASE1_STARTUP_HOOK_REQUIRED_TOKENS = (
    "thesis_moe_mode.py",
    "status --json",
    "startup",
    "resume",
    "continue",
    "reload",
    "phase change",
)
PHASE1_AGENT_REQUIRED_EXTENSION_SECTIONS = ("project", "moe", "dispatch", "extensions")
PHASE1_AGENT_PROJECT_REQUIRED_VALUES = {
    "scope": "repo-local",
    "private_prompt_policy": "do-not-copy-full-content",
}
PHASE1_AGENT_MOE_REQUIRED_VALUES = {
    "kind": "project-moe-agent",
    "family": "project-specific",
    "requires_manual_enable": True,
}
PHASE1_AGENT_DISPATCH_REQUIRED_MODE = "brief-based"
PHASE1_AGENT_DISPATCH_REQUIRED_FORBIDDEN = ("full-history-fork-with-custom-role",)
PHASE1_AGENT_DISPATCH_REQUIRED_FALLBACKS = ("main-session-takeover", "durable-brief")
PRIVATE_CLI_FIELD_NAMES = {
    "developer_instructions",
    "moe_md",
    "moe_prompt",
    "private_prompt",
    "private_prompt_text",
    "raw_environment",
    "raw_env",
    "raw_session_id",
    "stderr_full",
    "stdout_full",
}
PHASE1_WRAPPER_UNSAFE_SHELL_TOKENS = (
    "%*",
    "&&",
    "||",
    "|",
    ">",
    "<",
    "cmd /c",
    "powershell ",
    "pwsh ",
    "start ",
    "del ",
    "erase ",
    "move ",
    "copy ",
    "xcopy ",
    "robocopy ",
)
PHASE1_WRAPPER_DIRECT_STATE_TOKENS = (
    ".omx",
    "project-default.json",
    "sessions/",
    "sessions\\",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def win_rel(path: str | Path) -> str:
    return str(path).replace("/", "\\")


def rel_matches(rel: str | Path, prefix: str | Path) -> bool:
    candidate = norm(rel).strip("./").lower()
    parent = norm(prefix).strip("./").lower()
    return candidate == parent or candidate.startswith(parent + "/")


def rel_equals(rel: str | Path, exact: str | Path) -> bool:
    return norm(rel).strip("./").lower() == norm(exact).strip("./").lower()


def blocker(code: str, message: str, **extra: Any) -> dict[str, Any]:
    payload = {"code": code, "message": message}
    payload.update(extra)
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def load_json(path: Path, code: str, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    try:
        return json.loads(read_text(path))
    except FileNotFoundError:
        errors.append(blocker(code, f"Required JSON file is missing: {norm(path)}"))
    except Exception as exc:
        errors.append(blocker("blocked:invalid_json", f"Cannot parse JSON file: {norm(path)}", error=str(exc)))
    return None


def write_text_if_changed(path: Path, text: str) -> str:
    old = read_text(path) if path.exists() else None
    if old == text:
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return "updated" if old is not None else "created"


def write_json_if_changed(path: Path, data: dict[str, Any]) -> str:
    return write_text_if_changed(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_project(value: str) -> tuple[Path | None, dict[str, Any] | None]:
    if not value.strip():
        return None, blocker("blocked:missing_target_project", "--target-project is required.")
    root = Path(value).expanduser().resolve(strict=False)
    if not root.exists() or not root.is_dir():
        return root, blocker("blocked:target_project_not_found", "Target project directory does not exist.", target_project=str(root))
    return root, None


def project_evidence(root: Path) -> list[str]:
    return [item for item in PROJECT_EVIDENCE if (root / item).exists()]


def git_status_summary(root: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )
    records = [line for line in result.stdout.splitlines() if line.strip()]
    return {
        "is_git_worktree": result.returncode == 0,
        "read_only_git_optional_locks": True,
        "git_optional_locks": "0",
        "dirty": bool(records) if result.returncode == 0 else None,
        "dirty_count": len(records) if result.returncode == 0 else None,
        "records_sample": records[:20],
        "token": "ok" if result.returncode == 0 and not records else ("blocked:dirty_target_project" if result.returncode == 0 else "blocked:git_status_unavailable"),
        "stderr": result.stderr[-800:] if result.returncode != 0 else "",
    }


def safe_relative(root: Path, relative: str | Path, token: str = "blocked:path_outside_project") -> tuple[Path | None, dict[str, Any] | None]:
    rel = Path(relative)
    if rel.is_absolute():
        return None, blocker(token, "Absolute project-managed paths are not allowed.", path=str(relative))
    if any(part == ".." for part in rel.parts):
        return None, blocker("blocked:path_traversal", "Relative path must not contain '..'.", path=str(relative))
    resolved_root = root.resolve(strict=False)
    full = (resolved_root / rel).resolve(strict=False)
    try:
        full.relative_to(resolved_root)
    except ValueError:
        return None, blocker(token, "Resolved path escapes target project root.", path=str(relative), resolved=str(full))
    return full, None


def validate_identifiers(agent_name: str, namespace: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not NAME_RE.match(agent_name or ""):
        errors.append(blocker("blocked:invalid_agent_name", "Agent name must be a stable file-safe identifier.", agent_name=agent_name))
    if not NAMESPACE_RE.match(namespace or "") or "/" in namespace or "\\" in namespace:
        errors.append(blocker("blocked:invalid_state_namespace", "State namespace must be a stable directory-safe identifier.", state_namespace=namespace))
    return errors


def check_agent_toml(root: Path, agent_name: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    rel = Path(".codex/agents") / f"{agent_name}.toml"
    path, err = safe_relative(root, rel, "blocked:agent_toml_path_invalid")
    if err:
        return [err]
    assert path is not None
    if not path.exists():
        return [blocker("blocked:missing_agent_toml", "Target project must define the MOE agent TOML before GUI install.", path=norm(rel))]
    if tomllib is not None:
        try:
            data = tomllib.loads(read_text(path))
            if data.get("name") != agent_name:
                errors.append(blocker("blocked:agent_name_mismatch", "Agent TOML top-level name must match --agent-name.", expected=agent_name, observed=data.get("name")))
        except Exception as exc:
            errors.append(blocker("blocked:invalid_agent_toml", "Cannot parse target agent TOML.", path=norm(rel), error=str(exc)))
    return errors


def inspect_agent_toml(root: Path, agent_name: str, namespace: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rel = Path(".codex/agents") / f"{agent_name}.toml"
    path, err = safe_relative(root, rel, "blocked:agent_toml_path_invalid")
    if err:
        return {"path": norm(rel), "exists": False, "required_fields_ok": False, "extension_sections": []}, [err]
    assert path is not None
    details: dict[str, Any] = {
        "path": norm(rel),
        "exists": path.exists(),
        "required_fields_ok": False,
        "extension_sections": [],
        "required_extension_sections": list(PHASE1_AGENT_REQUIRED_EXTENSION_SECTIONS),
        "extension_fields_ok": False,
        "private_prompt_source": "MOE.md",
        "standard_profile_ready": False,
    }
    if not path.exists():
        return details, [blocker("blocked:missing_agent_toml", "Target project must define the MOE agent TOML before Phase 1 readiness.")]
    if tomllib is None:
        return details, [blocker("blocked:tomllib_unavailable", "Cannot validate agent TOML without tomllib.")]
    errors: list[dict[str, Any]] = []
    try:
        data = tomllib.loads(read_text(path))
    except Exception as exc:
        return details, [blocker("blocked:invalid_agent_toml", "Cannot parse target agent TOML.", path=norm(rel), error=str(exc))]
    required = ["name", "description", "developer_instructions"]
    missing = [key for key in required if not str(data.get(key) or "").strip()]
    if missing:
        errors.append(blocker("blocked:agent_toml_missing_required_fields", "Agent TOML is missing required top-level fields.", missing=missing))
    if data.get("name") != agent_name:
        errors.append(blocker("blocked:agent_name_mismatch", "Agent TOML top-level name must match --agent-name.", expected=agent_name, observed=data.get("name")))
    project_section = data.get("project") if isinstance(data.get("project"), dict) else {}
    moe_section = data.get("moe") if isinstance(data.get("moe"), dict) else {}
    dispatch_section = data.get("dispatch") if isinstance(data.get("dispatch"), dict) else {}
    details["required_fields_ok"] = not missing
    details["extension_sections"] = [name for name in ["project", "moe", "dispatch", "extensions"] if isinstance(data.get(name), dict)]
    details["private_prompt_source"] = str(project_section.get("private_prompt_source") or "MOE.md")
    missing_sections = [section for section in PHASE1_AGENT_REQUIRED_EXTENSION_SECTIONS if not isinstance(data.get(section), dict)]
    if missing_sections:
        errors.append(
            blocker(
                "blocked:agent_toml_missing_extension_sections",
                "Agent TOML must include the standard Project MOE extension sections before Phase 1 readiness.",
                missing=missing_sections,
                required=list(PHASE1_AGENT_REQUIRED_EXTENSION_SECTIONS),
            )
        )
    for key, expected in PHASE1_AGENT_PROJECT_REQUIRED_VALUES.items():
        observed = project_section.get(key)
        if observed != expected:
            errors.append(
                blocker(
                    "blocked:agent_project_boundary_invalid",
                    "Agent TOML [project] boundary fields must match the Project MOE standard.",
                    field=f"project.{key}",
                    expected=expected,
                    observed=observed,
                )
            )
    project_namespace = project_section.get("state_namespace")
    if project_namespace != namespace:
        errors.append(
            blocker(
                "blocked:agent_state_namespace_mismatch",
                "Agent TOML [project].state_namespace must match --state-namespace.",
                field="project.state_namespace",
                expected=namespace,
                observed=project_namespace,
            )
        )
    if moe_section.get("state_namespace") not in {None, namespace}:
        errors.append(blocker("blocked:agent_state_namespace_mismatch", "Agent TOML [moe].state_namespace must match --state-namespace when present.", field="moe.state_namespace", expected=namespace, observed=moe_section.get("state_namespace")))
    expected_state_paths = {
        "project_default_state": f".omx/state/{namespace}/project-default.json",
        "session_state_dir": f".omx/state/{namespace}/sessions",
    }
    for key, expected in {**PHASE1_AGENT_MOE_REQUIRED_VALUES, **expected_state_paths}.items():
        observed = moe_section.get(key)
        if observed != expected:
            errors.append(
                blocker(
                    "blocked:agent_moe_boundary_invalid",
                    "Agent TOML [moe] fields must match the Project MOE state boundary.",
                    field=f"moe.{key}",
                    expected=expected,
                    observed=observed,
                )
            )
    dispatch_mode = dispatch_section.get("mode")
    if dispatch_mode != PHASE1_AGENT_DISPATCH_REQUIRED_MODE:
        errors.append(
            blocker(
                "blocked:agent_dispatch_boundary_incomplete",
                "Agent TOML [dispatch].mode must use the compatible Project MOE dispatch mode.",
                field="dispatch.mode",
                expected=PHASE1_AGENT_DISPATCH_REQUIRED_MODE,
                observed=dispatch_mode,
            )
        )
    forbidden_dispatch = dispatch_section.get("forbidden")
    missing_forbidden = [
        item
        for item in PHASE1_AGENT_DISPATCH_REQUIRED_FORBIDDEN
        if not isinstance(forbidden_dispatch, list) or item not in forbidden_dispatch
    ]
    if missing_forbidden:
        errors.append(
            blocker(
                "blocked:agent_dispatch_boundary_incomplete",
                "Agent TOML dispatch boundary must forbid incompatible full-history custom-role dispatch.",
                field="dispatch.forbidden",
                missing=missing_forbidden,
            )
        )
    fallback_dispatch = dispatch_section.get("fallback")
    missing_fallbacks = [
        item
        for item in PHASE1_AGENT_DISPATCH_REQUIRED_FALLBACKS
        if not isinstance(fallback_dispatch, list) or item not in fallback_dispatch
    ]
    if missing_fallbacks:
        errors.append(
            blocker(
                "blocked:agent_dispatch_boundary_incomplete",
                "Agent TOML dispatch boundary must define compatible fallback paths.",
                field="dispatch.fallback",
                missing=missing_fallbacks,
            )
        )
    extension_blocker_codes = {
        "blocked:agent_toml_missing_extension_sections",
        "blocked:agent_project_boundary_invalid",
        "blocked:agent_state_namespace_mismatch",
        "blocked:agent_moe_boundary_invalid",
        "blocked:agent_dispatch_boundary_incomplete",
    }
    details["extension_fields_ok"] = not any(error["code"] in extension_blocker_codes for error in errors)
    details["standard_profile_ready"] = details["required_fields_ok"] and details["extension_fields_ok"] and data.get("name") == agent_name
    return details, errors


def inspect_private_prompt(root: Path, source: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rel = Path(source or "MOE.md")
    path, err = safe_relative(root, rel, "blocked:private_prompt_path_invalid")
    base_details = {
        "path": norm(rel),
        "exists": False,
        "managed_by_toolchain": False,
        "under_state_dir": False,
        "under_agent_dir": False,
        "under_gui_managed_dir": False,
        "private_prompt_boundary_ok": False,
    }
    if err:
        return base_details, [err]
    assert path is not None
    under_agent_dir = rel_matches(rel, PRIVATE_PROMPT_AGENT_DIR)
    under_state_dir = rel_matches(rel, PRIVATE_PROMPT_STATE_DIR)
    under_gui_managed_dir = rel_matches(rel, PRIVATE_PROMPT_GUI_MANAGED_DIR)
    managed_by_toolchain = under_gui_managed_dir or any(rel_equals(rel, managed) for managed in MANAGED_RELATIVES)
    details = {
        **base_details,
        "exists": path.exists(),
        "managed_by_toolchain": managed_by_toolchain,
        "under_state_dir": under_state_dir,
        "under_agent_dir": under_agent_dir,
        "under_gui_managed_dir": under_gui_managed_dir,
    }
    errors: list[dict[str, Any]] = []
    if under_agent_dir:
        errors.append(
            blocker(
                "blocked:private_prompt_source_inside_agent_dir",
                "Project-private prompt source must not point at agent definitions.",
                path=norm(rel),
            )
        )
    if under_state_dir:
        errors.append(
            blocker(
                "blocked:private_prompt_source_inside_state",
                "Project-private prompt source must not point at MOE runtime state.",
                path=norm(rel),
            )
        )
    if managed_by_toolchain:
        errors.append(
            blocker(
                "blocked:private_prompt_source_managed_by_toolchain",
                "Project-private prompt source must not point at Project MOE GUI managed artifacts.",
                path=norm(rel),
            )
        )
    details["private_prompt_boundary_ok"] = not errors
    if not path.exists():
        errors.append(blocker("blocked:missing_private_prompt_source", "Project-private prompt source must exist inside the target project.", path=norm(rel)))
    return details, errors


def command_token_hits(text: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token in text]


def inspect_wrapper_safety(text: str) -> tuple[list[str], list[str]]:
    lowered = text.lower()
    normalized = lowered.replace("\\", "/")
    unsafe_shell_hits = [token for token in PHASE1_WRAPPER_UNSAFE_SHELL_TOKENS if token in lowered]
    direct_state_hits = []
    for token in PHASE1_WRAPPER_DIRECT_STATE_TOKENS:
        needle = token.lower().replace("\\", "/")
        if needle in normalized:
            direct_state_hits.append(token)
    return unsafe_shell_hits, direct_state_hits


def inspect_mode_cli_surface(root: Path, mode_cli: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path, err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if err:
        return {"path": norm(mode_cli), "exists": False, "read_commands_seen": [], "write_commands_seen": []}, [err]
    assert path is not None
    details: dict[str, Any] = {"path": norm(mode_cli), "exists": path.exists(), "read_commands_seen": [], "write_commands_seen": []}
    if not path.exists():
        return details, [blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli))]
    text = read_text(path)
    read_hits = command_token_hits(text, READ_CLI_CONTRACT_COMMANDS + READ_ASSERTION_COMMANDS)
    write_hits = command_token_hits(text, PHASE1_EXPECTED_WRITE_COMMANDS)
    details["read_commands_seen"] = read_hits
    details["write_commands_seen"] = write_hits
    missing_read = [command for command in READ_CLI_CONTRACT_COMMANDS + READ_ASSERTION_COMMANDS if command not in read_hits]
    missing_write = [command for command in PHASE1_EXPECTED_WRITE_COMMANDS if command not in write_hits]
    errors = []
    if missing_read:
        errors.append(blocker("blocked:phase1_read_command_surface_incomplete", "Mode CLI text does not expose all expected Phase 1 read command tokens.", missing=missing_read))
    if missing_write:
        errors.append(blocker("blocked:phase1_write_command_surface_incomplete", "Mode CLI text does not expose all expected Phase 1 write command tokens.", missing=missing_write))
    return details, errors


def inspect_wrapper(root: Path, relative: Path, expected_command: str, mode_cli: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path, err = safe_relative(root, relative, "blocked:wrapper_path_invalid")
    if err:
        return {"path": norm(relative), "exists": False, "expected_command": expected_command}, [err]
    assert path is not None
    details = {
        "path": norm(relative),
        "exists": path.exists(),
        "expected_command": expected_command,
        "references_mode_cli": False,
        "references_expected_command": False,
        "passes_json_flag": False,
        "unsafe_shell_tokens": [],
        "direct_state_path_references": [],
    }
    if not path.exists():
        return details, [blocker("blocked:missing_phase1_wrapper", "Expected Phase 1 wrapper is missing.", path=norm(relative))]
    text = read_text(path)
    lowered = text.lower()
    details["references_mode_cli"] = mode_cli.name.lower() in lowered or norm(mode_cli).lower() in lowered.replace("\\", "/")
    details["references_expected_command"] = expected_command.lower() in lowered
    details["passes_json_flag"] = "--json" in lowered
    unsafe_shell_hits, direct_state_hits = inspect_wrapper_safety(text)
    details["unsafe_shell_tokens"] = unsafe_shell_hits
    details["direct_state_path_references"] = direct_state_hits
    errors: list[dict[str, Any]] = []
    if not details["references_mode_cli"]:
        errors.append(blocker("blocked:phase1_wrapper_not_bound_to_mode_cli", "Wrapper must invoke the target project's mode CLI.", path=norm(relative), mode_cli=norm(mode_cli)))
    if not details["references_expected_command"]:
        errors.append(blocker("blocked:phase1_wrapper_command_mismatch", "Wrapper must invoke the expected project-level command.", path=norm(relative), expected_command=expected_command))
    if not details["passes_json_flag"]:
        errors.append(blocker("blocked:phase1_wrapper_json_output_missing", "Wrapper must pass --json so automation can rely on stable machine-readable output.", path=norm(relative), expected_command=expected_command))
    if unsafe_shell_hits:
        errors.append(blocker("blocked:phase1_wrapper_unsafe_shell_surface", "Wrapper must not expose arbitrary argument passthrough, shell chaining, redirection, or file-operation command tokens.", path=norm(relative), unsafe_tokens=unsafe_shell_hits))
    if direct_state_hits:
        errors.append(blocker("blocked:phase1_wrapper_direct_state_surface", "Wrapper must delegate state reads and writes to the target mode CLI instead of touching .omx/state or status JSON files directly.", path=norm(relative), direct_state_tokens=direct_state_hits))
    return details, errors


def inspect_startup_hooks(root: Path, startup_paths: list[Path]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checked: list[dict[str, Any]] = []
    hook_found = False
    basic_status_hook_found = False
    best_missing: list[str] = list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS)

    def has_required_token(text: str, token: str) -> bool:
        lowered = text.lower()
        if token == "status --json":
            return "status" in lowered and "--json" in lowered
        if token == "phase change":
            return "phase change" in lowered or "phase-change" in lowered
        return token in lowered

    for rel in startup_paths:
        path, err = safe_relative(root, rel, "blocked:startup_hook_path_invalid")
        if err:
            checked.append({"path": norm(rel), "exists": False, "token": err["code"], "missing_tokens": list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS)})
            continue
        assert path is not None
        exists = path.exists()
        has_hook = False
        matched: list[str] = []
        missing: list[str] = list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS)
        if exists:
            text = read_text(path).lower()
            matched = [token for token in PHASE1_STARTUP_HOOK_REQUIRED_TOKENS if has_required_token(text, token)]
            missing = [token for token in PHASE1_STARTUP_HOOK_REQUIRED_TOKENS if token not in matched]
            if len(missing) < len(best_missing):
                best_missing = missing
            basic_status_hook = "thesis_moe_mode.py" in text and "status" in text and "--json" in text
            basic_status_hook_found = basic_status_hook_found or basic_status_hook
            has_hook = not missing
            hook_found = hook_found or has_hook
        checked.append({"path": norm(rel), "exists": exists, "has_moe_status_hook": has_hook, "matched_tokens": matched, "missing_tokens": missing})
    details = {
        "candidates_checked": checked,
        "hook_found": hook_found,
        "basic_status_hook_found": basic_status_hook_found,
        "required_tokens": list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS),
    }
    if hook_found:
        return details, []
    if basic_status_hook_found:
        return details, [blocker("blocked:moe_activation_hook_incomplete", "Startup activation hook must cover startup/resume/continue/reload/phase-change checkpoints with status --json.", missing=best_missing, required=list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS))]
    return details, [blocker("blocked:missing_moe_activation_hook", "No startup or launcher file contains a complete MOE status --json activation checkpoint.", required=list(PHASE1_STARTUP_HOOK_REQUIRED_TOKENS))]


def inspect_operator_docs(root: Path, doc_paths: list[Path]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checked: list[dict[str, Any]] = []
    docs_found = False
    ready_doc = False
    best_missing: list[str] = list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)
    for rel in doc_paths:
        path, err = safe_relative(root, rel, "blocked:operator_doc_path_invalid")
        if err:
            checked.append({"path": norm(rel), "exists": False, "token": err["code"], "missing_tokens": list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)})
            continue
        assert path is not None
        exists = path.exists()
        if not exists:
            checked.append({"path": norm(rel), "exists": False, "missing_tokens": list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)})
            continue
        docs_found = True
        text = read_text(path).lower()
        matched = [token for token in PHASE1_OPERATOR_DOC_REQUIRED_TOKENS if token.lower() in text]
        missing = [token for token in PHASE1_OPERATOR_DOC_REQUIRED_TOKENS if token.lower() not in text]
        if len(missing) < len(best_missing):
            best_missing = missing
        ready = not missing
        ready_doc = ready_doc or ready
        checked.append({"path": norm(rel), "exists": True, "ready": ready, "matched_tokens": matched, "missing_tokens": missing})
    if ready_doc:
        return {"candidates_checked": checked, "docs_found": docs_found, "ready": True, "required_tokens": list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)}, []
    if not docs_found:
        return (
            {"candidates_checked": checked, "docs_found": False, "ready": False, "required_tokens": list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)},
            [blocker("blocked:missing_phase1_operator_docs", "No target-project operator documentation for thesis MOE mode was found.", expected_paths=[norm(path) for path in doc_paths])],
        )
    return (
        {"candidates_checked": checked, "docs_found": True, "ready": False, "required_tokens": list(PHASE1_OPERATOR_DOC_REQUIRED_TOKENS)},
        [blocker("blocked:phase1_operator_docs_incomplete", "Target-project operator documentation is missing required command and wrapper tokens.", missing=best_missing)],
    )


def run_cli(root: Path, mode_cli: Path, command: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    full, err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if err:
        return None, err
    assert full is not None
    if not full.exists():
        return None, blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli))
    try:
        result = subprocess.run(
            [sys.executable, str(full), command, "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, blocker("blocked:mode_cli_timeout", "Mode CLI timed out during read-only contract check.", command=command)
    except Exception as exc:
        return None, blocker("blocked:mode_cli_invocation_failed", "Cannot invoke target project mode CLI.", command=command, error=str(exc))
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        if result.returncode != 0:
            return None, blocker("blocked:mode_cli_failed", "Target project mode CLI returned non-zero and did not emit valid JSON.", command=command, exit_code=result.returncode, stderr=result.stderr[-800:], stdout=result.stdout[-800:])
        return None, blocker("blocked:mode_cli_invalid_json", "Target project mode CLI did not emit valid JSON.", command=command, error=str(exc), stdout=result.stdout[-800:])
    if result.returncode != 0 and command not in READ_ASSERTION_COMMANDS:
        return None, blocker("blocked:mode_cli_failed", "Target project mode CLI returned non-zero.", command=command, exit_code=result.returncode, stderr=result.stderr[-800:])
    return payload, None


def private_cli_field_hits(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).strip().lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if lowered in PRIVATE_CLI_FIELD_NAMES:
                hits.append(child_path)
            hits.extend(private_cli_field_hits(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(private_cli_field_hits(child, f"{path}[{index}]"))
    return hits


def require_cli_envelope(
    command: str,
    payload: dict[str, Any] | None,
    *,
    allow_non_ok_tokens: set[str] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return [blocker("blocked:cli_contract_invalid", "Mode CLI JSON payload must be an object.", command=command)]
    errors: list[dict[str, Any]] = []
    missing = [key for key in COMMON_CLI_ENVELOPE_KEYS if key not in payload]
    if missing:
        errors.append(blocker("blocked:cli_envelope_missing_fields", "Mode CLI JSON envelope is missing required fields.", command=command, missing=missing))
    if payload.get("command") != command:
        errors.append(blocker("blocked:cli_command_echo_mismatch", "Mode CLI JSON command field must match the invoked command.", command=command, observed=payload.get("command")))
    ok_value = payload.get("ok")
    token = str(payload.get("token") or "")
    allowed_tokens = allow_non_ok_tokens or {"ok"}
    if command == "assert-on":
        if token not in allowed_tokens:
            errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on must return a stable supported token.", command=command, token=payload.get("token"), supported=sorted(allowed_tokens)))
        if token == "ok" and ok_value is not True:
            errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on token=ok must report ok=true.", command=command, ok=ok_value))
        if token != "ok" and ok_value is not False:
            errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on disabled/blocker tokens must report ok=false.", command=command, token=payload.get("token"), ok=ok_value))
    elif ok_value is not True or token != "ok":
        errors.append(blocker("blocked:cli_read_command_not_ok", "Read-only Mode CLI contract command must return ok/token=ok.", command=command, token=payload.get("token")))
    if payload.get("cli_contract") != CLI_CONTRACT:
        errors.append(blocker("blocked:cli_contract_mismatch", "Target CLI contract does not match project-moe-cli-v1.", command=command, observed=payload.get("cli_contract")))
    private_hits = private_cli_field_hits(payload)
    if private_hits:
        errors.append(blocker("blocked:cli_contract_private_field_exposed", "Mode CLI JSON exposed private/raw fields that GUI contracts must not consume.", command=command, fields=private_hits[:12]))
    return errors


def validate_project_status_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if "project_default_enabled" not in payload and "project_default" not in payload:
        errors.append(blocker("blocked:project_status_contract_invalid", "project-status --json must expose project_default_enabled or project_default."))
    has_count = any(key in payload for key in ["registered_session_count", "valid_session_count", "invalid_session_count", "stale_session_count", "orphan_candidate_count"]) or isinstance(payload.get("counts"), dict)
    if not has_count:
        errors.append(blocker("blocked:project_status_contract_invalid", "project-status --json must expose registered session counts."))
    return errors


def validate_list_sessions_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    sessions = payload.get("sessions")
    if not isinstance(sessions, list):
        return [blocker("blocked:list_sessions_contract_invalid", "list-sessions --json must return a sessions array.")]
    if not isinstance(payload.get("counts"), dict):
        errors.append(blocker("blocked:list_sessions_contract_invalid", "list-sessions --json must return a counts object for GUI summaries."))
    for index, row in enumerate(sessions):
        if not isinstance(row, dict):
            errors.append(blocker("blocked:list_sessions_contract_invalid", "Each session row must be a JSON object.", row_index=index))
            continue
        if not (row.get("session_id") or row.get("display_id") or row.get("id")):
            errors.append(blocker("blocked:list_sessions_contract_invalid", "Each session row must include a redacted or normalized session identifier.", row_index=index))
        if "enabled" not in row and "effective_enabled" not in row:
            errors.append(blocker("blocked:list_sessions_contract_invalid", "Each session row must include enabled or effective_enabled.", row_index=index))
        if "token" not in row:
            errors.append(blocker("blocked:list_sessions_contract_invalid", "Each session row must include a stable token.", row_index=index))
    return errors


def validate_status_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(payload.get("effective_enabled"), bool):
        errors.append(blocker("blocked:status_contract_invalid", "status --json must include boolean effective_enabled."))
    source = payload.get("effective_source")
    if source not in STATUS_EFFECTIVE_SOURCES:
        errors.append(blocker("blocked:status_contract_invalid", "status --json must include a supported effective_source.", observed=source, supported=sorted(STATUS_EFFECTIVE_SOURCES)))
    if "session_id" in payload and payload.get("raw_session_id"):
        errors.append(blocker("blocked:cli_contract_private_field_exposed", "status --json must not expose raw_session_id."))
    return errors


def validate_assert_on_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(payload.get("effective_enabled"), bool):
        errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on --json must include boolean effective_enabled."))
    source = payload.get("effective_source")
    if source not in STATUS_EFFECTIVE_SOURCES:
        errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on --json must include a supported effective_source.", observed=source, supported=sorted(STATUS_EFFECTIVE_SOURCES)))
    if payload.get("token") == "ok" and payload.get("effective_enabled") is not True:
        errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on token=ok is only valid when effective_enabled=true."))
    if payload.get("token") != "ok" and payload.get("effective_enabled") is not False:
        errors.append(blocker("blocked:assert_on_contract_invalid", "assert-on disabled/blocker tokens are only valid when effective_enabled=false."))
    forbidden_write_fields = [field for field in ("before", "after", "changed_paths", "changed_scope", "atomic_write", "lock_status", "audit_path") if field in payload]
    if forbidden_write_fields:
        errors.append(blocker("blocked:assert_on_not_read_only", "assert-on must be a read-only assertion and must not expose write-result fields.", fields=forbidden_write_fields))
    return errors


def validate_cli_payload(command: str, payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    allow_non_ok_tokens = ASSERT_ON_TOKENS if command == "assert-on" else None
    errors = require_cli_envelope(command, payload, allow_non_ok_tokens=allow_non_ok_tokens)
    if not isinstance(payload, dict):
        return errors
    if command == "project-status":
        errors.extend(validate_project_status_payload(payload))
    elif command == "list-sessions":
        errors.extend(validate_list_sessions_payload(payload))
    elif command == "status":
        errors.extend(validate_status_payload(payload))
    elif command == "assert-on":
        errors.extend(validate_assert_on_payload(payload))
    return errors


def classify_phase1_adaptation_lane(errors: list[dict[str, Any]]) -> dict[str, Any]:
    if not errors:
        return {
            "adaptation_lane": "ready",
            "control_mode_allowed": True,
            "bootstrap_required": False,
            "bootstrap_missing_capabilities": [],
            "repair_required": False,
            "lane_reason": "phase1_readiness_checker_passed",
        }
    codes = [str(error.get("code") or "") for error in errors]
    missing_capabilities = sorted(
        {
            BOOTSTRAP_BLOCKER_CAPABILITIES[code]
            for code in codes
            if code in BOOTSTRAP_BLOCKER_CAPABILITIES
        }
    )
    if missing_capabilities:
        return {
            "adaptation_lane": "bootstrap",
            "control_mode_allowed": False,
            "bootstrap_required": True,
            "bootstrap_missing_capabilities": missing_capabilities,
            "repair_required": False,
            "lane_reason": "phase1_contract_surface_missing",
        }
    return {
        "adaptation_lane": "repair",
        "control_mode_allowed": False,
        "bootstrap_required": False,
        "bootstrap_missing_capabilities": [],
        "repair_required": True,
        "lane_reason": "phase1_contract_surface_present_but_blocked",
    }


def remediation_action_for_code(code: str) -> dict[str, Any]:
    action = dict(
        PHASE1_REMEDIATION_ACTIONS.get(
            code,
            {
                "category": "manual_review",
                "phase": "manual-review",
                "action": f"review_{re.sub(r'[^a-z0-9]+', '_', code.lower()).strip('_') or 'unknown_blocker'}",
                "description": "Review this blocker and add a stable remediation mapping before approving GUI control mode.",
                "requires_target_project_write": False,
            },
        )
    )
    action.update(
        {
            "code": code,
            "safe_to_auto_apply": False,
            "blocks_control_mode": True,
        }
    )
    return action


def build_phase1_remediation_plan(errors: list[dict[str, Any]], lane: dict[str, Any], execute_cli: bool) -> dict[str, Any]:
    lane_name = str(lane.get("adaptation_lane") or "unknown")
    cli_execution_mode = "execute-read-contract" if execute_cli else "static-only"
    ready_for_control = not errors and execute_cli and lane_name == "ready" and lane.get("control_mode_allowed") is True
    if ready_for_control:
        return {
            "schema_version": SCHEMA_VERSION,
            "ready_for_control": True,
            "lane": lane_name,
            "cli_execution_mode": cli_execution_mode,
            "target_project_write_allowed_by_checker": False,
            "summary": "no_remediation_required",
            "groups": [],
            "ordered_next_steps": [],
        }

    actions: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for error in errors:
        code = str(error.get("code") or "blocked:unknown")
        if code in seen_codes:
            continue
        seen_codes.add(code)
        actions.append(remediation_action_for_code(code))

    if not errors and not execute_cli:
        actions.append(
            {
                "code": "candidate:execute_read_contract_required",
                "category": "mode_cli_contract",
                "phase": "execute-read-contract",
                "action": "run_execute_read_contract_readiness_check",
                "description": "Run readiness without --static-only so the target read-contract CLI commands are executed and verified before GUI control.",
                "requires_target_project_write": False,
                "safe_to_auto_apply": False,
                "blocks_control_mode": True,
            }
        )

    actions.sort(
        key=lambda item: (
            PHASE1_REMEDIATION_PHASE_ORDER.get(str(item.get("phase")), 99),
            str(item.get("category") or ""),
            str(item.get("action") or ""),
            str(item.get("code") or ""),
        )
    )
    group_map: dict[tuple[str, str], dict[str, Any]] = {}
    for action in actions:
        key = (str(action["phase"]), str(action["category"]))
        group = group_map.setdefault(
            key,
            {
                "phase": action["phase"],
                "category": action["category"],
                "codes": [],
                "actions": [],
                "descriptions": [],
                "requires_target_project_write": False,
                "safe_to_auto_apply": True,
                "blocks_control_mode": False,
            },
        )
        group["codes"].append(action["code"])
        group["actions"].append(action["action"])
        group["descriptions"].append(action["description"])
        group["requires_target_project_write"] = group["requires_target_project_write"] or bool(action["requires_target_project_write"])
        group["safe_to_auto_apply"] = group["safe_to_auto_apply"] and bool(action["safe_to_auto_apply"])
        group["blocks_control_mode"] = group["blocks_control_mode"] or bool(action["blocks_control_mode"])

    if not errors and not execute_cli:
        summary = "execute_read_contract_required_before_control"
    elif lane_name == "bootstrap":
        summary = "bootstrap_phase1_surface_before_gui_control"
    elif lane_name == "repair":
        summary = "repair_existing_phase1_surface_before_gui_control"
    else:
        summary = "manual_review_required_before_gui_control"

    return {
        "schema_version": SCHEMA_VERSION,
        "ready_for_control": False,
        "lane": lane_name,
        "cli_execution_mode": cli_execution_mode,
        "target_project_write_allowed_by_checker": False,
        "summary": summary,
        "groups": list(group_map.values()),
        "ordered_next_steps": [str(action["action"]) for action in actions],
    }


def check_cli_contract(root: Path, mode_cli: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    details: dict[str, Any] = {
        "mode_cli": norm(mode_cli),
        "cli_execution_mode": "execute-read-contract",
        "execution_skipped": False,
        "commands_checked": [],
        "assertion_commands_checked": [],
        "validated_fields": {},
    }
    for command in READ_CLI_CONTRACT_COMMANDS + READ_ASSERTION_COMMANDS:
        payload, err = run_cli(root, mode_cli, command)
        if err:
            errors.append(err)
            continue
        if command in READ_ASSERTION_COMMANDS:
            details["assertion_commands_checked"].append(command)
        else:
            details["commands_checked"].append(command)
        command_errors = validate_cli_payload(command, payload)
        errors.extend(command_errors)
        details["validated_fields"][command] = sorted([key for key in (payload or {}).keys()])
    return errors, details


def skipped_cli_contract_details(mode_cli: Path, reason: str) -> dict[str, Any]:
    return {
        "mode_cli": norm(mode_cli),
        "cli_execution_mode": "static-only",
        "execution_skipped": True,
        "skip_reason": reason,
        "commands_checked": [],
        "assertion_commands_checked": [],
        "validated_fields": {},
    }


def launcher_text() -> str:
    return '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def emit(payload: dict, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload.get('token')}: {payload.get('message')}")
    return int(payload.get("exit_code", 0))


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch or preflight the project-local MOE GUI.")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--allow-visible", action="store_true", help="Launch a visible PySide6 window. Use only in an interactive session.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    launcher = Path(__file__).resolve()
    config_path = launcher.with_name("project_moe_gui.config.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:launcher_config_invalid", "exit_code": 5, "message": "Cannot read Project MOE GUI config.", "error": str(exc)}, args.json)

    project_root = launcher.parents[2]
    source_root = Path(str(config.get("toolchain_source_root") or ""))
    if source_root:
        sys.path.insert(0, str(source_root / "src"))
    mode_cli_value = str(config.get("mode_cli", "tools/thesis_moe_mode.py"))
    mode_cli = project_root / mode_cli_value
    if not mode_cli.exists():
        bootstrap_plan = None
        bootstrap_error = None
        try:
            from project_moe_gui.toolchain import phase1_bootstrap_scaffold_plan
            bootstrap_plan = phase1_bootstrap_scaffold_plan(
                project_root,
                str(config.get("agent_name") or ""),
                str(config.get("state_namespace") or ""),
                Path(mode_cli_value),
            )
        except Exception as exc:
            bootstrap_error = {"code": "blocked:bootstrap_plan_unavailable", "token": "blocked:bootstrap_plan_unavailable", "message": "Cannot build Bootstrap Lane scaffold plan.", "error": str(exc)}
        missing = {"code": "blocked:missing_mode_cli", "token": "blocked:missing_mode_cli", "message": "Target project mode CLI is missing.", "path": str(mode_cli)}
        blockers = [missing]
        if bootstrap_error:
            blockers.append(bootstrap_error)
        return emit({
            "schema_version": 1,
            "ok": False,
            "token": "blocked:missing_mode_cli",
            "exit_code": 5,
            "message": "Target project mode CLI is missing; Bootstrap Lane scaffold plan is available when possible.",
            "project_root": str(project_root),
            "mode_cli": str(mode_cli),
            "adaptation_lane": "bootstrap",
            "bootstrap_required": True,
            "control_mode_allowed": False,
            "target_project_write_allowed_by_launcher": False,
            "bootstrap_plan": bootstrap_plan,
            "operator_next_steps": bootstrap_plan.get("operator_next_steps", []) if isinstance(bootstrap_plan, dict) else [],
            "blockers": blockers,
        }, args.json)

    def run_mode(command: str) -> tuple[dict | None, dict | None]:
        result = subprocess.run([sys.executable, str(mode_cli), command, "--json"], cwd=str(project_root), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if result.returncode != 0:
            return None, {"token": "blocked:mode_cli_failed", "message": "Target project mode CLI failed.", "command": command, "exit_code": result.returncode, "stderr": result.stderr[-800:]}
        try:
            payload = json.loads(result.stdout)
        except Exception as exc:
            return None, {"token": "blocked:mode_cli_invalid_json", "message": "Target project mode CLI did not emit valid JSON.", "command": command, "error": str(exc), "stdout": result.stdout[-800:]}
        return payload, None

    project_status, project_error = run_mode("project-status")
    sessions_payload, sessions_error = run_mode("list-sessions")
    status_payload, status_error = run_mode("status")
    cli_errors = [err for err in [project_error, sessions_error, status_error] if err]
    if cli_errors:
        return emit({"schema_version": 1, "ok": False, "token": cli_errors[0]["token"], "exit_code": cli_errors[0].get("exit_code", 5), "message": cli_errors[0]["message"], "project_root": str(project_root), "blockers": cli_errors}, args.json)

    try:
        from project_moe_gui import gui_shell
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:gui_shell_unavailable", "exit_code": 5, "message": "Cannot import central Project MOE GUI shell.", "toolchain_source_root": str(source_root), "error": str(exc)}, args.json)

    preflight = gui_shell.build_gui_preflight(config, project_status=project_status, sessions_payload=sessions_payload, status_payload=status_payload)
    if args.preflight:
        return emit(preflight, args.json)
    if not args.allow_visible:
        return emit({**preflight, "ok": False, "token": "blocked:visible_gui_launch_requires_explicit_approval", "exit_code": 2, "message": "GUI shell is available. Visible PySide6 launch requires --allow-visible in an interactive session."}, args.json)
    if not preflight.get("ok"):
        return emit(preflight, args.json)
    try:
        return gui_shell.launch_visible(preflight["view_model"])
    except RuntimeError as exc:
        return emit({"schema_version": 1, "ok": False, "token": str(exc), "exit_code": 5, "message": "Visible GUI launch failed."}, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
'''


def cmd_text() -> str:
    return '@echo off\nsetlocal\ncd /d "%~dp0"\npython "%~dp0tools\\project_moe_gui\\launcher.py" %*\nexit /b %ERRORLEVEL%\n'


def readme_text(agent_name: str, namespace: str) -> str:
    return f"""# Project MOE GUI managed artifacts

This directory is managed by `D:\\PythonProject_langgraph` Project MOE GUI toolchain.

- Agent: `{agent_name}`
- State namespace: `{namespace}`
- CLI contract: `{CLI_CONTRACT}`
- GUI shell contract: `{GUI_SHELL_CONTRACT}`

Do not place private `MOE.md` content or project state files in this directory.
Phase 2B provides an import-safe GUI shell and guarded visible-launch path through the central toolchain source. Automated checks must use `--preflight`; visible PySide6 launch requires an explicit interactive command.
"""


def config_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(existing or {})
    runtime_python = runtime_root / ".venv" / "Scripts" / "python.exe"
    data.update(
        {
            "schema_version": SCHEMA_VERSION,
            "toolchain": TOOLCHAIN_NAME,
            "toolchain_version": TOOLCHAIN_VERSION,
            "cli_contract": CLI_CONTRACT,
            "agent_name": agent_name,
            "state_namespace": namespace,
            "mode_cli": norm(mode_cli),
            "project_root_strategy": "launcher-parent-git-root",
            "pyside6_runtime": "shared-runtime",
            "python_runtime_strategy": "shared-gui-runtime",
            "python_utf8": True,
            "shared_runtime_root": str(runtime_root),
            "runtime_python": str(runtime_python),
            "target_project_root": str(root),
            "toolchain_source_root": str(Path(__file__).resolve().parents[2]),
            "gui_shell_contract": GUI_SHELL_CONTRACT,
        }
    )
    return data


def artifacts(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing_config: dict[str, Any] | None = None) -> dict[Path, str]:
    return {
        LAUNCHER_RELATIVE: launcher_text(),
        CONFIG_RELATIVE: json.dumps(config_payload(root, agent_name, namespace, mode_cli, runtime_root, existing_config), ensure_ascii=False, indent=2) + "\n",
        README_RELATIVE: readme_text(agent_name, namespace),
        CMD_RELATIVE: cmd_text(),
    }


def manifest_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, planned: dict[Path, str], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    managed = [{"path": norm(rel), "role": "managed", "sha256": sha256_bytes(text.encode("utf-8"))} for rel, text in planned.items()]
    managed.append({"path": norm(MANIFEST_RELATIVE), "role": "manifest", "sha256": None})
    return {
        "schema_version": SCHEMA_VERSION,
        "toolchain": TOOLCHAIN_NAME,
        "toolchain_version": TOOLCHAIN_VERSION,
        "cli_contract": CLI_CONTRACT,
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "mode_cli": norm(mode_cli),
        "installed_at": (previous or {}).get("installed_at") or now_utc(),
        "updated_at": now_utc(),
        "managed_files": managed,
        "protected_files": ["MOE.md", ".codex/agents/*.toml", f".omx/state/{namespace}/"],
        "rollback_hint": "Use the target project's Git history to revert managed install artifacts; do not delete .omx/state as part of GUI rollback.",
    }


def existing_install(root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    manifest = load_json(root / MANIFEST_RELATIVE, "blocked:not_installed", errors) if (root / MANIFEST_RELATIVE).exists() else None
    config = load_json(root / CONFIG_RELATIVE, "blocked:not_installed", errors) if (root / CONFIG_RELATIVE).exists() else None
    return manifest, config, errors


def preflight(root: Path, agent_name: str, namespace: str, mode_cli: Path, check_cli: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors = validate_identifiers(agent_name, namespace)
    evidence = project_evidence(root)
    if not evidence:
        errors.append(blocker("blocked:missing_project_evidence", "Target directory does not look like a project.", expected=PROJECT_EVIDENCE))
    errors.extend(check_agent_toml(root, agent_name))
    mode_full, mode_err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if mode_err:
        errors.append(mode_err)
    elif mode_full and not mode_full.exists():
        errors.append(blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli)))
    cli_details: dict[str, Any] = {}
    if check_cli and not any(error["code"].startswith("blocked:mode_cli") or error["code"] == "blocked:path_traversal" for error in errors):
        cli_errors, cli_details = check_cli_contract(root, mode_cli)
        errors.extend(cli_errors)
    return errors, {"project_root_evidence": evidence, "cli_contract_check": cli_details}


def check_phase1_readiness(
    root: Path,
    agent_name: str,
    namespace: str,
    mode_cli: Path,
    on_wrapper: Path = DEFAULT_ON_WRAPPER,
    off_wrapper: Path = DEFAULT_OFF_WRAPPER,
    startup_paths: list[Path] | None = None,
    operator_doc_paths: list[Path] | None = None,
    execute_cli: bool = True,
) -> dict[str, Any]:
    errors = validate_identifiers(agent_name, namespace)
    evidence = project_evidence(root)
    if not evidence:
        errors.append(blocker("blocked:missing_project_evidence", "Target directory does not look like a project.", expected=PROJECT_EVIDENCE))
    git_status = git_status_summary(root)
    if git_status["token"] == "blocked:dirty_target_project":
        errors.append(blocker("blocked:dirty_target_project", "Target project has dirty or untracked files; preserve or classify them before Phase 1 writes.", dirty_count=git_status["dirty_count"], records_sample=git_status["records_sample"]))
    elif git_status["token"] == "blocked:git_status_unavailable":
        errors.append(blocker("blocked:git_status_unavailable", "Cannot run git status in target project.", stderr=git_status["stderr"]))

    agent_details, agent_errors = inspect_agent_toml(root, agent_name, namespace)
    errors.extend(agent_errors)
    prompt_details, prompt_errors = inspect_private_prompt(root, str(agent_details.get("private_prompt_source") or "MOE.md"))
    errors.extend(prompt_errors)
    mode_cli_surface, mode_surface_errors = inspect_mode_cli_surface(root, mode_cli)
    errors.extend(mode_surface_errors)
    cli_execution_mode = "execute-read-contract" if execute_cli else "static-only"
    if mode_cli_surface.get("exists") and execute_cli:
        cli_errors, cli_details = check_cli_contract(root, mode_cli)
        errors.extend(cli_errors)
    elif mode_cli_surface.get("exists"):
        cli_details = skipped_cli_contract_details(mode_cli, "static_only_no_exec_cli")
    else:
        cli_details = skipped_cli_contract_details(mode_cli, "mode_cli_missing")
    on_details, on_errors = inspect_wrapper(root, on_wrapper, "project-on", mode_cli)
    off_details, off_errors = inspect_wrapper(root, off_wrapper, "project-off", mode_cli)
    errors.extend(on_errors)
    errors.extend(off_errors)
    hook_details, hook_errors = inspect_startup_hooks(root, startup_paths or list(DEFAULT_STARTUP_HOOK_CANDIDATES))
    errors.extend(hook_errors)
    operator_doc_details, operator_doc_errors = inspect_operator_docs(root, operator_doc_paths or list(DEFAULT_OPERATOR_DOC_CANDIDATES))
    errors.extend(operator_doc_errors)
    lane = classify_phase1_adaptation_lane(errors)
    if not errors and not execute_cli:
        lane = {
            "adaptation_lane": "ready-candidate",
            "control_mode_allowed": False,
            "bootstrap_required": False,
            "bootstrap_missing_capabilities": [],
            "repair_required": False,
            "lane_reason": "static_surface_passed_cli_execution_skipped",
        }
    readiness_status = "ready" if not errors and execute_cli else ("static-ready-candidate" if not errors else "blocked")
    remediation_plan = build_phase1_remediation_plan(errors, lane, execute_cli)
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "check_project_moe_phase1_readiness",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "readiness_status": readiness_status,
        **lane,
        "cli_execution_mode": cli_execution_mode,
        "read_only": True,
        "writes_target_project": False,
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "mode_cli": norm(mode_cli),
        "project_root_evidence": evidence,
        "git_status": git_status,
        "agent_toml": agent_details,
        "private_prompt_source": prompt_details,
        "mode_cli_surface": mode_cli_surface,
        "cli_contract_check": cli_details,
        "wrappers": {"on": on_details, "off": off_details},
        "startup_activation_hooks": hook_details,
        "operator_docs": operator_doc_details,
        "blockers": errors,
        "next_actions": [] if not errors else sorted({error["code"] for error in errors}),
        "remediation_plan": remediation_plan,
    }


def phase1_agent_toml_template(agent_name: str, namespace: str, private_prompt_source: Path) -> str:
    return f'''name = "{agent_name}"
description = "Project-local MOE agent. Replace this placeholder with a short project-specific description before enabling GUI control."
developer_instructions = """
Project-local MOE instructions live in the project-private prompt source.
Do not copy private prompt content into shared toolchain or user-level caches.
"""

[project]
scope = "repo-local"
state_namespace = "{namespace}"
private_prompt_source = "{norm(private_prompt_source)}"
private_prompt_policy = "do-not-copy-full-content"

[moe]
kind = "project-moe-agent"
family = "project-specific"
requires_manual_enable = true
project_default_state = ".omx/state/{namespace}/project-default.json"
session_state_dir = ".omx/state/{namespace}/sessions"

[dispatch]
mode = "brief-based"
forbidden = ["full-history-fork-with-custom-role"]
fallback = ["main-session-takeover", "durable-brief"]

[extensions]
'''


def phase1_private_prompt_placeholder(agent_name: str, namespace: str) -> str:
    return f"""# Project MOE private prompt placeholder

Agent: `{agent_name}`
State namespace: `{namespace}`

Replace this placeholder inside the target project only.
Do not copy another project's private `MOE.md` content into this file.
Do not move this content into `.codex/agents/`, `.omx/state/`, or Project MOE GUI managed artifacts.
"""


def phase1_mode_cli_template(agent_name: str, namespace: str) -> str:
    return f'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

AGENT_NAME = "{agent_name}"
STATE_NAMESPACE = "{namespace}"
CLI_CONTRACT = "{CLI_CONTRACT}"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def envelope(command: str, **extra: object) -> dict:
    payload = {{
        "schema_version": 1,
        "command": command,
        "ok": False,
        "token": "blocked:bootstrap_placeholder",
        "exit_code": 5,
        "message": "Phase 1 bootstrap placeholder must be completed before GUI control.",
        "agent_name": AGENT_NAME,
        "state_namespace": STATE_NAMESPACE,
        "generated_at": now(),
        "warnings": ["complete this target-project CLI before enabling Project MOE GUI control"],
        "errors": [],
        "cli_contract": CLI_CONTRACT,
    }}
    payload.update(extra)
    return payload


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    # Command-surface tokens required by the readiness checker:
    # project-on project-off project-status list-sessions status on off assert-on --json --session-id
    payload = envelope(command)
    if command == "project-status":
        payload.update(project_default_enabled=False, registered_session_count=0, valid_session_count=0, invalid_session_count=0)
    elif command == "list-sessions":
        payload.update(sessions=[], counts={{"total": 0, "valid": 0, "invalid": 0}})
    elif command in {{"status", "assert-on"}}:
        payload.update(effective_enabled=False, effective_source="fail-closed")
    print(json.dumps(payload, ensure_ascii=False))
    return int(payload.get("exit_code", 5))


if __name__ == "__main__":
    raise SystemExit(main())
'''


def phase1_wrapper_template(mode_cli: Path, command: str) -> str:
    return f'@echo off\nsetlocal\npython "%~dp0{win_rel(mode_cli)}" {command} --json\nexit /b %ERRORLEVEL%\n'


def phase1_startup_hook_template(mode_cli: Path) -> str:
    return f"""# Project startup MOE activation hook

On startup, resume, continue, reload, or phase change, run:

```powershell
python .\\{win_rel(mode_cli)} status --json
```

Only apply project MOE rules when the effective status says it is enabled.
If the command is missing, invalid, or returns a blocker, fail closed and report the stable token.
"""


def phase1_operator_doc_template(mode_cli: Path, on_wrapper: Path, off_wrapper: Path) -> str:
    mode_cli_win = win_rel(mode_cli)
    return f"""# Project MOE Phase 1 operator guide

Use the project-local mode CLI and wrappers only; do not edit `.omx/state` JSON by hand.

Required commands:

- `python .\\{mode_cli_win} project-on`
- `python .\\{mode_cli_win} project-off`
- `python .\\{mode_cli_win} project-status --json`
- `python .\\{mode_cli_win} list-sessions --json`
- `python .\\{mode_cli_win} status --json`
- `python .\\{mode_cli_win} assert-on`
- `python .\\{mode_cli_win} on --session-id <id>`
- `python .\\{mode_cli_win} off --session-id <id>`
- `{norm(on_wrapper)}`
- `{norm(off_wrapper)}`

Startup, resume, continue, reload, and phase change checks must read `status --json` before applying MOE behavior.
"""


def bootstrap_plan_item(root: Path, rel: Path, role: str, content: str, *, existing_action: str = "manual-review-existing") -> dict[str, Any]:
    full, err = safe_relative(root, rel)
    if err:
        return {
            "path": norm(rel),
            "role": role,
            "action": "blocked",
            "blocker": err,
            "requires_target_project_write": False,
            "safe_to_auto_apply": False,
        }
    assert full is not None
    exists = full.exists()
    action = existing_action if exists else "create"
    return {
        "path": norm(rel),
        "role": role,
        "action": action,
        "exists": exists,
        "sha256": sha256_bytes(content.encode("utf-8")),
        "requires_target_project_write": not exists,
        "safe_to_auto_apply": False,
        "content_included": False,
        "template_size_bytes": len(content.encode("utf-8")),
    }


def phase1_bootstrap_operator_next_steps(planned_writes: list[dict[str, Any]], git_status: dict[str, Any]) -> list[dict[str, Any]]:
    create_items = [item for item in planned_writes if item.get("action") == "create"]
    manual_items = [item for item in planned_writes if str(item.get("action", "")).startswith("manual")]
    preserve_items = [item for item in planned_writes if str(item.get("action", "")).startswith("preserve")]
    dirty_count = int(git_status.get("dirty_count") or 0) if isinstance(git_status, dict) else 0
    git_token = str(git_status.get("token") or "") if isinstance(git_status, dict) else ""
    preflight_required = dirty_count > 0 or git_token == "blocked:git_status_unavailable"
    return [
        {
            "order": 1,
            "phase": "preflight",
            "action": "classify_or_clean_target_project_state",
            "required_now": preflight_required,
            "requires_target_project_write": False,
            "control_mode_allowed_after_step": False,
            "reason": "Target project git state must be understood before applying Phase 1 files.",
        },
        {
            "order": 2,
            "phase": "bootstrap",
            "action": "review_existing_private_surfaces",
            "required_now": bool(manual_items or preserve_items),
            "requires_target_project_write": False,
            "control_mode_allowed_after_step": False,
            "paths": [item["path"] for item in [*manual_items, *preserve_items] if item.get("path")],
            "reason": "Existing Agent TOML, startup, operator docs, or private prompt surfaces require manual review; private prompt bodies are not read.",
        },
        {
            "order": 3,
            "phase": "bootstrap",
            "action": "create_or_update_phase1_contract_files",
            "required_now": bool(create_items or manual_items),
            "requires_target_project_write": True,
            "control_mode_allowed_after_step": False,
            "paths": [item["path"] for item in [*create_items, *manual_items] if item.get("path")],
            "reason": "Phase 1 CLI, wrappers, startup checkpoint, operator docs, Agent TOML, and prompt placeholder must exist before Ready Lane.",
        },
        {
            "order": 4,
            "phase": "verify-static",
            "action": "run_static_only_readiness_check",
            "required_now": True,
            "requires_target_project_write": False,
            "control_mode_allowed_after_step": False,
            "command_template": "check_project_moe_phase1_readiness.py --target-project <project> --agent-name <agent> --state-namespace <namespace> --static-only --no-exec-cli --json",
            "reason": "Static-only readiness must pass before executing target CLI read contracts when CLI reads may have side effects.",
        },
        {
            "order": 5,
            "phase": "verify-execute-read-contract",
            "action": "run_execute_read_contract_readiness_check",
            "required_now": True,
            "requires_target_project_write": False,
            "control_mode_allowed_after_step": False,
            "command_template": "check_project_moe_phase1_readiness.py --target-project <project> --agent-name <agent> --state-namespace <namespace> --json",
            "reason": "Ready Lane requires executed read/assertion contract evidence, not only file-surface evidence.",
        },
        {
            "order": 6,
            "phase": "ready-lane",
            "action": "install_or_launch_gui_only_after_ready_lane",
            "required_now": False,
            "requires_target_project_write": False,
            "control_mode_allowed_after_step": "only_after_readiness_status_ready",
            "reason": "GUI install/control remains forbidden until the readiness checker returns the Ready Lane with control_mode_allowed=true.",
        },
    ]


def phase1_bootstrap_scaffold_plan(
    root: Path,
    agent_name: str,
    namespace: str,
    mode_cli: Path = DEFAULT_MODE_CLI,
    private_prompt_source: Path = DEFAULT_PRIVATE_PROMPT_SOURCE,
    on_wrapper: Path = DEFAULT_ON_WRAPPER,
    off_wrapper: Path = DEFAULT_OFF_WRAPPER,
    startup_hook: Path = DEFAULT_BOOTSTRAP_STARTUP_HOOK,
    operator_doc: Path = DEFAULT_BOOTSTRAP_OPERATOR_DOC,
) -> dict[str, Any]:
    errors = validate_identifiers(agent_name, namespace)
    evidence = project_evidence(root)
    if not evidence:
        errors.append(blocker("blocked:missing_project_evidence", "Target directory does not look like a project.", expected=PROJECT_EVIDENCE))
    git_status = git_status_summary(root)
    if git_status["token"] == "blocked:git_status_unavailable":
        errors.append(blocker("blocked:git_status_unavailable", "Cannot run git status in target project.", stderr=git_status["stderr"]))

    agent_rel = Path(".codex") / "agents" / f"{agent_name}.toml"
    templates = {
        agent_rel: ("agent_toml", phase1_agent_toml_template(agent_name, namespace, private_prompt_source), "manual-review-existing"),
        private_prompt_source: ("private_prompt_source", phase1_private_prompt_placeholder(agent_name, namespace), "preserve-existing-private-prompt"),
        mode_cli: ("mode_cli", phase1_mode_cli_template(agent_name, namespace), "manual-review-existing"),
        on_wrapper: ("phase1_wrapper_on", phase1_wrapper_template(mode_cli, "project-on"), "manual-review-existing"),
        off_wrapper: ("phase1_wrapper_off", phase1_wrapper_template(mode_cli, "project-off"), "manual-review-existing"),
        startup_hook: ("startup_activation_hook", phase1_startup_hook_template(mode_cli), "manual-update-existing"),
        operator_doc: ("operator_docs", phase1_operator_doc_template(mode_cli, on_wrapper, off_wrapper), "manual-update-existing"),
    }
    planned_writes = [
        bootstrap_plan_item(root, rel, role, content, existing_action=existing_action)
        for rel, (role, content, existing_action) in templates.items()
    ]
    plan_blockers = [item["blocker"] for item in planned_writes if item.get("action") == "blocked" and item.get("blocker")]
    errors.extend(plan_blockers)
    create_count = sum(1 for item in planned_writes if item.get("action") == "create")
    manual_review_count = sum(1 for item in planned_writes if str(item.get("action", "")).startswith("manual"))
    preserve_count = sum(1 for item in planned_writes if str(item.get("action", "")).startswith("preserve"))
    operator_next_steps = phase1_bootstrap_operator_next_steps(planned_writes, git_status)
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "scaffold_project_moe_phase1",
        "mode": "dry-run",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "read_only": True,
        "writes_target_project": False,
        "apply_supported": False,
        "target_project_write_allowed_by_checker": False,
        "control_mode_allowed": False,
        "bootstrap_required": True,
        "adaptation_lane": "bootstrap",
        "lane_reason": "phase1_bootstrap_scaffold_plan_only",
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "mode_cli": norm(mode_cli),
        "private_prompt_source": norm(private_prompt_source),
        "planned_writes": planned_writes,
        "operator_next_steps": operator_next_steps,
        "summary": {
            "create_count": create_count,
            "manual_review_count": manual_review_count,
            "preserve_existing_count": preserve_count,
            "blocked_count": len(plan_blockers),
            "next_step_count": len(operator_next_steps),
        },
        "git_status": git_status,
        "project_root_evidence": evidence,
        "blockers": errors,
        "next_actions": [
            "review_dry_run_plan",
            "obtain_explicit_target_project_write_approval",
            "apply_scaffold_in_target_project_worktree",
            "complete_placeholder_cli_and_private_prompt",
            "run_phase1_readiness_checker",
        ],
        "privacy_boundary": {
            "private_prompt_body_read": False,
            "template_content_included_in_payload": False,
            "copies_other_project_private_prompt": False,
        },
    }


def planned_changes(root: Path, planned: dict[Path, str]) -> tuple[list[dict[str, Any]], bool]:
    changes: list[dict[str, Any]] = []
    changed = False
    for rel, text in planned.items():
        full, err = safe_relative(root, rel)
        if err:
            changes.append({"path": norm(rel), "action": "blocked", "blocker": err})
            changed = True
            continue
        assert full is not None
        old = read_text(full) if full.exists() else None
        action = "unchanged" if old == text else ("update" if full.exists() else "create")
        changed = changed or action != "unchanged"
        changes.append({"path": norm(rel), "action": action, "managed": True})
    return changes, changed


def apply_artifacts(root: Path, planned: dict[Path, str], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for rel, text in planned.items():
        full, err = safe_relative(root, rel)
        if err:
            raise RuntimeError(err["message"])
        assert full is not None
        applied.append({"path": norm(rel), "status": write_text_if_changed(full, text), "managed": True})
    applied.append({"path": norm(MANIFEST_RELATIVE), "status": write_json_if_changed(root / MANIFEST_RELATIVE, manifest), "managed": True})
    return applied


def install(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, dry_run: bool, check_cli: bool = True) -> dict[str, Any]:
    errors, details = preflight(root, agent_name, namespace, mode_cli, check_cli)
    old_manifest, old_config, load_errors = existing_install(root)
    errors.extend(load_errors)
    planned = artifacts(root, agent_name, namespace, mode_cli, runtime_root, old_config)
    changes, changed = planned_changes(root, planned)
    manifest = manifest_payload(root, agent_name, namespace, mode_cli, planned, old_manifest)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": "install_project_moe_gui",
        "mode": "dry-run" if dry_run else "apply",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "toolchain": TOOLCHAIN_NAME,
        "toolchain_version": TOOLCHAIN_VERSION,
        "cli_contract": CLI_CONTRACT,
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "planned_writes": changes,
        "planned_skips": [],
        "planned_migrations": [],
        "no_op": not changed,
        "blockers": errors,
        "project_root_evidence": details["project_root_evidence"],
        "cli_contract_check": details["cli_contract_check"],
        "rollback_hint": manifest["rollback_hint"],
    }
    if errors or dry_run:
        return payload
    payload["applied_file_changes"] = apply_artifacts(root, planned, manifest)
    return payload


def hash_errors(root: Path, manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not manifest:
        return errors
    for item in manifest.get("managed_files", []):
        rel = item.get("path")
        expected = item.get("sha256")
        if not rel or not expected:
            continue
        full, err = safe_relative(root, rel)
        if err:
            errors.append(err)
            continue
        assert full is not None
        if not full.exists():
            errors.append(blocker("blocked:managed_file_missing", "Managed file is missing.", path=rel))
            continue
        observed = sha256_file(full)
        if observed != expected:
            errors.append(blocker("blocked:managed_file_hash_mismatch", "Managed file hash does not match install manifest.", path=rel, expected=expected, observed=observed))
    return errors


def check_install(root: Path, skip_runtime_import: bool = False) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    manifest, config, load_errors = existing_install(root)
    if not manifest or not config:
        errors.extend(load_errors or [blocker("blocked:not_installed", "Project MOE GUI is not installed in target project.")])
    else:
        errors.extend(load_errors)
        errors.extend(hash_errors(root, manifest))
        agent = str(config.get("agent_name") or manifest.get("agent_name") or "")
        namespace = str(config.get("state_namespace") or manifest.get("state_namespace") or "")
        mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
        errors.extend(preflight(root, agent, namespace, mode_cli, True)[0])
        runtime_status = "skipped_by_flag"
        if not skip_runtime_import:
            runtime_python = Path(str(config.get("runtime_python") or ""))
            if not runtime_python.exists():
                runtime_status = "missing"
                errors.append(blocker("blocked:python_runtime_unavailable", "Configured PySide6 runtime Python is missing.", runtime_python=str(runtime_python)))
            else:
                result = subprocess.run([str(runtime_python), "-c", "import PySide6; print('ok')"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
                runtime_status = "import_ok" if result.returncode == 0 else "pyside6_unavailable"
                if result.returncode != 0:
                    errors.append(blocker("blocked:pyside6_unavailable", "Configured runtime cannot import PySide6.", stderr=result.stderr[-800:]))
    installed_version = manifest.get("toolchain_version") if manifest else None
    status = "not_installed"
    if manifest and config:
        status = "blocked" if errors else ("up_to_date" if installed_version == TOOLCHAIN_VERSION else "upgrade_available")
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "check_project_moe_gui_install",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "status": status,
        "target_project_root": str(root),
        "installed_toolchain_version": installed_version,
        "target_toolchain_version": TOOLCHAIN_VERSION,
        "config_schema_version": config.get("schema_version") if config else None,
        "cli_contract": config.get("cli_contract") if config else CLI_CONTRACT,
        "migration_actions": [],
        "runtime_status": locals().get("runtime_status", "unknown"),
        "blockers": errors,
        "rollback_hint": (manifest or {}).get("rollback_hint"),
    }


def update(root: Path, dry_run: bool, skip_runtime_import: bool = True) -> dict[str, Any]:
    current = check_install(root, skip_runtime_import=skip_runtime_import)
    if current.get("blockers"):
        return {**current, "command": "update_project_moe_gui", "mode": "dry-run" if dry_run else "apply"}
    errors: list[dict[str, Any]] = []
    manifest = load_json(root / MANIFEST_RELATIVE, "blocked:not_installed", errors) or {}
    config = load_json(root / CONFIG_RELATIVE, "blocked:not_installed", errors) or {}
    agent = str(config.get("agent_name") or manifest.get("agent_name"))
    namespace = str(config.get("state_namespace") or manifest.get("state_namespace"))
    mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
    runtime_root = Path(str(config.get("shared_runtime_root") or DEFAULT_SHARED_RUNTIME_ROOT))
    planned = artifacts(root, agent, namespace, mode_cli, runtime_root, config)
    changes, changed = planned_changes(root, planned)
    new_manifest = manifest_payload(root, agent, namespace, mode_cli, planned, manifest)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": "update_project_moe_gui",
        "mode": "dry-run" if dry_run else "apply",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "status": "migration_required" if changed else "up_to_date",
        "target_project_root": str(root),
        "installed_toolchain_version": manifest.get("toolchain_version"),
        "target_toolchain_version": TOOLCHAIN_VERSION,
        "config_schema_version": config.get("schema_version"),
        "cli_contract": config.get("cli_contract"),
        "migration_actions": changes,
        "no_op": not changed,
        "blockers": errors,
        "rollback_hint": new_manifest["rollback_hint"],
    }
    if errors or dry_run:
        return payload
    payload["applied_file_changes"] = apply_artifacts(root, planned, new_manifest)
    payload["update_receipt"] = {
        "target_project_root": str(root),
        "old_toolchain_version": manifest.get("toolchain_version"),
        "new_toolchain_version": TOOLCHAIN_VERSION,
        "schema_version": SCHEMA_VERSION,
        "changed_files": [item["path"] for item in payload["applied_file_changes"] if item["status"] != "unchanged"],
        "skipped_private_files": ["MOE.md", ".codex/agents/*.toml", f".omx/state/{namespace}/"],
        "executed_at": now_utc(),
        "rollback_hint": new_manifest["rollback_hint"],
    }
    return payload


def emit(payload: dict[str, Any], json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload.get('token')}: {payload.get('status') or payload.get('command')}")
    return 0 if payload.get("ok") else 1


def root_or_error(target_project: str, command: str) -> tuple[Path | None, dict[str, Any] | None]:
    root, err = resolve_project(target_project)
    if err:
        return root, {"schema_version": SCHEMA_VERSION, "command": command, "ok": False, "token": err["code"], "target_project_root": str(root) if root else target_project, "blockers": [err]}
    assert root is not None
    return root, None
