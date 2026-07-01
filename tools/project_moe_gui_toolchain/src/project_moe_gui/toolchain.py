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

from project_moe_gui import CANONICAL_TOOLCHAIN_NAME, CLI_CONTRACT, LEGACY_PRODUCT_DISPLAY_NAME, PRODUCT_DISPLAY_NAME, PRODUCT_DISPLAY_NAME_ZH, TOOLCHAIN_NAME, TOOLCHAIN_VERSION
from project_moe_gui.daemon import build_daemon_launch_plan, windows_daemon_artifact_plan
from project_moe_gui.gui_shell import (
    DEFAULT_EXPERT_CATEGORIES,
    DEFAULT_EXPERT_LENSES,
    DEPRECATED_LENS_ALIASES,
    LEGACY_CATEGORY_ID_ALIASES,
    GUI_SHELL_CONTRACT,
    qml_shell_path,
    qml_visual_contract,
)
from project_moe_gui.qfluent_runtime import expected_qfluent_dependency, qfluent_license_manifest


SCHEMA_VERSION = 1
PRODUCT_SHELL_CONTRACT = "project-moe-gui-product-widgets-v1"
DEFAULT_MODE_CLI = Path("tools/thesis_moe_mode.py")
DEFAULT_SHARED_RUNTIME_ROOT = Path(r"D:\PythonProject_langgraph\.shared_runtimes\pyside6")
DEFAULT_TOOLCHAIN_SOURCE_ROOT = Path(r"D:\PythonProject_langgraph\tools\project_moe_gui_toolchain")
DEFAULT_MODE_CLI_TIMEOUT_SECONDS = 60.0
MODE_CLI_TIMEOUT_ENV = "PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS"


def mode_cli_timeout_seconds(default: float = DEFAULT_MODE_CLI_TIMEOUT_SECONDS) -> float:
    raw = os.environ.get(MODE_CLI_TIMEOUT_ENV)
    if raw is None or not str(raw).strip():
        return default
    try:
        parsed = float(str(raw).strip())
    except ValueError:
        return default
    if parsed <= 0:
        return default
    return parsed


def current_toolchain_source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def stable_toolchain_source_root() -> Path:
    configured = os.environ.get("PROJECT_MOE_GUI_TOOLCHAIN_SOURCE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve(strict=False)
    current_root = current_toolchain_source_root().resolve(strict=False)
    default_root = DEFAULT_TOOLCHAIN_SOURCE_ROOT.resolve(strict=False)
    if DEFAULT_TOOLCHAIN_SOURCE_ROOT.exists():
        return default_root
    return current_root


def validate_toolchain_source_root(source_root: Path) -> tuple[str, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    root = source_root.resolve(strict=False)
    package_root = root / "src" / "project_moe_gui"
    init_py = package_root / "__init__.py"
    status = "import_skipped"
    if not root.exists():
        errors.append(blocker("blocked:toolchain_source_root_unavailable", "Configured Project Expert Lens GUI toolchain source root is missing.", toolchain_source_root=str(root)))
        return "missing", errors
    if not init_py.exists():
        errors.append(blocker("blocked:toolchain_source_root_invalid", "Configured Project Expert Lens GUI toolchain source root does not contain src/project_moe_gui.", toolchain_source_root=str(root), expected=str(init_py)))
        return "invalid", errors
    code = "import project_moe_gui, project_moe_gui.toolchain; print(project_moe_gui.TOOLCHAIN_NAME)"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src") + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, env=env)
    if result.returncode != 0:
        errors.append(blocker("blocked:toolchain_source_root_import_failed", "Configured Project Expert Lens GUI toolchain source root cannot import project_moe_gui.", toolchain_source_root=str(root), stderr=result.stderr[-800:]))
        status = "import_failed"
    else:
        status = "import_ok"
    return status, errors

CONFIG_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.config.json")
MANIFEST_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.install-manifest.json")
LAUNCHER_RELATIVE = Path("tools/project_moe_gui/launcher.py")
README_RELATIVE = Path("tools/project_moe_gui/README.md")
CMD_RELATIVE = Path("project-moe-gui.cmd")
SILENT_VBS_RELATIVE = Path("project-moe-gui-silent.vbs")
CANONICAL_CMD_RELATIVE = Path("project-expert-lens-gui.cmd")
CANONICAL_SILENT_VBS_RELATIVE = Path("project-expert-lens-gui-silent.vbs")
QML_RELATIVE = Path("tools/project_moe_gui/qml/ProjectMoeGui.qml")
TURN_GATE_RELATIVE = Path("tools/thesis_moe_turn_gate.py")
MANAGED_RELATIVES = [LAUNCHER_RELATIVE, CONFIG_RELATIVE, README_RELATIVE, CMD_RELATIVE, SILENT_VBS_RELATIVE, CANONICAL_CMD_RELATIVE, CANONICAL_SILENT_VBS_RELATIVE, QML_RELATIVE, TURN_GATE_RELATIVE]
UNINSTALL_MANAGED_ALLOWLIST = {
    "tools/project_moe_gui/launcher.py",
    "tools/project_moe_gui/project_moe_gui.config.json",
    "tools/project_moe_gui/project_moe_gui.install-manifest.json",
    "tools/project_moe_gui/README.md",
    "tools/project_moe_gui/qml/ProjectMoeGui.qml",
    "tools/thesis_moe_turn_gate.py",
    "project-moe-gui.cmd",
    "project-moe-gui-silent.vbs",
    "project-expert-lens-gui.cmd",
    "project-expert-lens-gui-silent.vbs",
}
RECOVERABLE_UPDATE_BLOCKER_CODES = {
    "blocked:toolchain_source_root_unavailable",
    "blocked:toolchain_source_root_invalid",
    "blocked:toolchain_source_root_import_failed",
}
PRIVATE_PROMPT_AGENT_DIR = Path(".codex/agents")
PRIVATE_PROMPT_STATE_DIR = Path(".omx/state")
PRIVATE_PROMPT_GUI_MANAGED_DIR = Path("tools/project_moe_gui")
PROJECT_EVIDENCE = [".git", "AGENTS.md", "pyproject.toml", "requirements.txt", "README.md", "setup.cfg", "setup.py", "poetry.lock", "uv.lock"]
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")
READ_CLI_CONTRACT_COMMANDS = ("project-status", "list-sessions", "list-lenses", "status")
READ_ASSERTION_COMMANDS = ("assert-on",)
PHASE1_EXPECTED_WRITE_COMMANDS = ("project-on", "project-off", "on", "off", "set-lenses", "clear-lenses", "assert-on")
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
        "action": "create_native_compatible_project_expert_lens_agent_toml",
        "description": "Create the project-local Project Expert Lens agent TOML with native Codex-compatible top-level fields only.",
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
        "description": "Align the agent TOML top-level name with the Project Expert Lens GUI configuration and readiness command.",
        "requires_target_project_write": True,
    },
    "blocked:agent_toml_unsupported_custom_fields": {
        "category": "agent_toml",
        "phase": "repair",
        "action": "remove_custom_project_expert_lens_tables_from_native_agent_toml",
        "description": "Remove custom Project Expert Lens tables or keys from native Codex agent TOML; readiness is proven through config, CLI, wrappers, startup hook, private prompt source, and .omx/state instead.",
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
        "description": "Keep private prompt source outside Project Expert Lens GUI managed artifacts.",
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
    "blocked:cli_envelope_schema_version_mismatch": {
        "category": "mode_cli_contract",
        "phase": "repair",
        "action": "repair_mode_cli_schema_version",
        "description": "Return the supported Project Expert Lens Agent GUI toolchain schema_version in every read-contract envelope.",
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
LENS_EFFECTIVE_MODES = {"all", "selected"}
PHASE1_OPERATOR_DOC_REQUIRED_TOKENS = (
    "thesis_moe_mode.py",
    "project-on",
    "project-off",
    "project-status --json",
    "list-sessions --json",
    "list-lenses --json",
    "status --json",
    "assert-on",
    "--session-id",
    "set-lenses",
    "clear-lenses",
    "thesis-moe-on.cmd",
    "thesis-moe-off.cmd",
)
PHASE1_STARTUP_HOOK_REQUIRED_TOKENS = (
    "thesis_moe_mode.py",
    "status --json",
    "thesis_moe_turn_gate.py",
    "user message",
    "next user message",
    "startup",
    "resume",
    "continue",
    "reload",
    "phase change",
)
PHASE1_AGENT_REQUIRED_FIELDS = ("name", "description", "developer_instructions")
PHASE1_AGENT_ALLOWED_TOP_LEVEL_KEYS = frozenset((*PHASE1_AGENT_REQUIRED_FIELDS, "model", "model_reasoning_effort"))
PHASE1_AGENT_LEGACY_CUSTOM_TABLES = ("project", "moe", "dispatch", "extensions")
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
        "records": records,
        "records_sample": records[:20],
        "token": "ok" if result.returncode == 0 and not records else ("blocked:dirty_target_project" if result.returncode == 0 else "blocked:git_status_unavailable"),
        "stderr": result.stderr[-800:] if result.returncode != 0 else "",
    }


def git_status_record_path(record: str) -> str:
    path = record[3:] if len(record) > 3 else record
    if " -> " in path:
        path = path.split(" -> ")[-1]
    return path.strip().strip('"').replace("\\", "/")


def runtime_state_dirty_details(git_status: dict[str, Any], namespace: str) -> dict[str, Any]:
    records = [str(record) for record in (git_status.get("records") or git_status.get("records_sample") or [])]
    allowed_prefix = f".omx/state/{namespace}/"
    allowed_records: list[str] = []
    unsafe_records: list[str] = []
    for record in records:
        path = git_status_record_path(record)
        if path == f".omx/state/{namespace}" or path.startswith(allowed_prefix):
            allowed_records.append(record)
        else:
            unsafe_records.append(record)
    return {
        "policy": "allow_only_project_moe_namespace_state_dirty_for_installed_launcher",
        "namespace": namespace,
        "allowed_prefixes": [allowed_prefix],
        "allowed_count": len(allowed_records),
        "unsafe_count": len(unsafe_records),
        "allowed_records_sample": allowed_records[:20],
        "unsafe_records_sample": unsafe_records[:20],
        "all_dirty_records_runtime_state_only": bool(records) and not unsafe_records,
    }


def dirty_target_runtime_warning(git_status: dict[str, Any], namespace: str, runtime_dirty: dict[str, Any] | None = None) -> dict[str, Any]:
    details = runtime_dirty if runtime_dirty is not None else runtime_state_dirty_details(git_status, namespace)
    return {
        "code": "warning:dirty_target_project_allowed_for_gui_runtime",
        "message": "Target project has dirty or untracked files. GUI launch, read, and MOE state writes may continue, but install/update/managed-file overwrite/local commit still require a clean target worktree.",
        "dirty_count": git_status.get("dirty_count"),
        "records_sample": git_status.get("records_sample") or [],
        "runtime_state_dirty_details": details,
        "blocks_install_update_or_commit": True,
        "blocks_gui_runtime": False,
    }


def strict_clean_git_errors(root: Path, *, operation: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    git_status = git_status_summary(root)
    if git_status["token"] == "ok":
        git_status["clean_worktree_enforced"] = True
        return [], git_status
    if git_status["token"] == "blocked:git_status_unavailable":
        # Some import-safe fixtures provide only a .git evidence directory instead of a
        # real Git repository. Production target projects such as A are real Git
        # worktrees and remain dirty-blocked by the branch below. Keep the
        # unavailable status visible as diagnostics without turning these fixtures
        # into write blockers.
        git_status["clean_worktree_enforced"] = False
        git_status["clean_worktree_enforcement_reason"] = "git_status_unavailable_diagnostic_only"
        return [], git_status
    code = "blocked:dirty_target_project"
    message = "Target project must be a clean Git worktree before install, update, or managed-file overwrite."
    git_status["clean_worktree_enforced"] = True
    return [blocker(code, message, operation=operation, git_status=git_status)], git_status


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


def _agent_toml_unknown_top_level_keys(data: dict[str, Any]) -> list[str]:
    return sorted(str(key) for key in set(data) - PHASE1_AGENT_ALLOWED_TOP_LEVEL_KEYS)


def _agent_toml_legacy_custom_tables(data: dict[str, Any]) -> list[str]:
    return [name for name in PHASE1_AGENT_LEGACY_CUSTOM_TABLES if isinstance(data.get(name), dict)]


def check_agent_toml(root: Path, agent_name: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    rel = Path(".codex/agents") / f"{agent_name}.toml"
    path, err = safe_relative(root, rel, "blocked:agent_toml_path_invalid")
    if err:
        return [err]
    assert path is not None
    if not path.exists():
        return [blocker("blocked:missing_agent_toml", "Target project must define the native-compatible Project Expert Lens agent TOML before GUI install.", path=norm(rel))]
    if tomllib is not None:
        try:
            data = tomllib.loads(read_text(path))
            if data.get("name") != agent_name:
                errors.append(blocker("blocked:agent_name_mismatch", "Agent TOML top-level name must match --agent-name.", expected=agent_name, observed=data.get("name")))
            unknown = _agent_toml_unknown_top_level_keys(data)
            if unknown:
                errors.append(
                    blocker(
                        "blocked:agent_toml_unsupported_custom_fields",
                        "Native Codex agent TOML must not contain custom Project Expert Lens top-level keys or tables.",
                        path=norm(rel),
                        unsupported_top_level_keys=unknown,
                        legacy_custom_tables=_agent_toml_legacy_custom_tables(data),
                        allowed_top_level_keys=sorted(PHASE1_AGENT_ALLOWED_TOP_LEVEL_KEYS),
                    )
                )
        except Exception as exc:
            errors.append(blocker("blocked:invalid_agent_toml", "Cannot parse target agent TOML.", path=norm(rel), error=str(exc)))
    return errors


def inspect_agent_toml(root: Path, agent_name: str, namespace: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rel = Path(".codex/agents") / f"{agent_name}.toml"
    path, err = safe_relative(root, rel, "blocked:agent_toml_path_invalid")
    base_details: dict[str, Any] = {
        "path": norm(rel),
        "exists": False,
        "required_fields_ok": False,
        "native_schema_compatible": False,
        "allowed_top_level_keys": sorted(PHASE1_AGENT_ALLOWED_TOP_LEVEL_KEYS),
        "unsupported_top_level_keys": [],
        "legacy_custom_tables": [],
        "extension_sections": [],
        "required_extension_sections": [],
        "extension_fields_ok": True,
        "project_lens_metadata_source": "config_cli_wrappers_startup_private_prompt_and_state",
        "private_prompt_source": "MOE.md",
        "state_namespace_source": "toolchain_config_and_mode_cli",
        "state_namespace": namespace,
        "standard_profile_ready": False,
    }
    if err:
        return base_details, [err]
    assert path is not None
    details = {**base_details, "exists": path.exists()}
    if not path.exists():
        return details, [blocker("blocked:missing_agent_toml", "Target project must define the native-compatible Project Expert Lens agent TOML before Phase 1 readiness.")]
    if tomllib is None:
        return details, [blocker("blocked:tomllib_unavailable", "Cannot validate agent TOML without tomllib.")]
    errors: list[dict[str, Any]] = []
    try:
        data = tomllib.loads(read_text(path))
    except Exception as exc:
        return details, [blocker("blocked:invalid_agent_toml", "Cannot parse target agent TOML.", path=norm(rel), error=str(exc))]
    missing = [key for key in PHASE1_AGENT_REQUIRED_FIELDS if not str(data.get(key) or "").strip()]
    if missing:
        errors.append(blocker("blocked:agent_toml_missing_required_fields", "Agent TOML is missing required top-level fields.", missing=missing))
    if data.get("name") != agent_name:
        errors.append(blocker("blocked:agent_name_mismatch", "Agent TOML top-level name must match --agent-name.", expected=agent_name, observed=data.get("name")))
    unsupported = _agent_toml_unknown_top_level_keys(data)
    legacy_custom_tables = _agent_toml_legacy_custom_tables(data)
    if unsupported:
        errors.append(
            blocker(
                "blocked:agent_toml_unsupported_custom_fields",
                "Native Codex agent TOML must contain only supported top-level fields; Project Expert Lens metadata belongs in config, CLI, wrappers, startup hooks, private prompt source, and .omx/state.",
                unsupported_top_level_keys=unsupported,
                legacy_custom_tables=legacy_custom_tables,
                allowed_top_level_keys=sorted(PHASE1_AGENT_ALLOWED_TOP_LEVEL_KEYS),
            )
        )
    details["required_fields_ok"] = not missing
    details["unsupported_top_level_keys"] = unsupported
    details["legacy_custom_tables"] = legacy_custom_tables
    details["extension_sections"] = legacy_custom_tables
    details["native_schema_compatible"] = not unsupported
    details["extension_fields_ok"] = not unsupported
    details["standard_profile_ready"] = details["required_fields_ok"] and details["native_schema_compatible"] and data.get("name") == agent_name
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
                "Project-private prompt source must not point at Project Expert Lens GUI managed artifacts.",
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
            timeout=mode_cli_timeout_seconds(),
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
    if "schema_version" in payload and payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            blocker(
                "blocked:cli_envelope_schema_version_mismatch",
                "Mode CLI JSON envelope schema_version is not supported by this Project Expert Lens Agent GUI toolchain.",
                command=command,
                expected=SCHEMA_VERSION,
                observed=payload.get("schema_version"),
            )
        )
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
        for field in ("selected_lenses", "selected_categories"):
            if field in row and not isinstance(row.get(field), list):
                errors.append(blocker("blocked:list_sessions_contract_invalid", f"Each session row {field} field must be an array when present.", row_index=index, field=field))
        effective_lens_mode = row.get("effective_lens_mode", "all")
        if effective_lens_mode not in LENS_EFFECTIVE_MODES:
            errors.append(blocker("blocked:list_sessions_contract_invalid", "Each session row effective_lens_mode must be all or selected.", row_index=index, observed=effective_lens_mode))
    return errors


def _validate_public_string_id_list(command: str, owner: str, values: Any, *, required: bool = False) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if required and not isinstance(values, list):
        return [blocker(f"blocked:{command.replace('-', '_')}_contract_invalid", f"{command} --json must expose a {owner} array.")]
    if values is None:
        return errors
    if not isinstance(values, list):
        return [blocker(f"blocked:{command.replace('-', '_')}_contract_invalid", f"{owner} must be a JSON array.", owner=owner)]
    seen: set[str] = set()
    for index, item in enumerate(values):
        item_id: Any = item.get("id") if isinstance(item, dict) else item
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(blocker(f"blocked:{command.replace('-', '_')}_contract_invalid", f"{owner} entries must expose a non-empty public id.", owner=owner, row_index=index))
            continue
        if item_id in seen:
            errors.append(blocker(f"blocked:{command.replace('-', '_')}_contract_invalid", f"{owner} ids must be unique.", owner=owner, row_index=index, id=item_id))
        seen.add(item_id)
    return errors


def validate_list_lenses_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    errors.extend(_validate_public_string_id_list("list-lenses", "lenses", payload.get("lenses"), required=True))
    errors.extend(_validate_public_string_id_list("list-lenses", "categories", payload.get("categories"), required=True))
    semantics = payload.get("selection_semantics")
    if not isinstance(semantics, dict):
        errors.append(blocker("blocked:list_lenses_contract_invalid", "list-lenses --json must describe selection_semantics."))
    elif semantics.get("empty_selection") not in {"all", "all-lenses"}:
        errors.append(
            blocker(
                "blocked:list_lenses_contract_invalid",
                "list-lenses selection_semantics.empty_selection must say that empty selected_lenses and selected_categories mean all lenses.",
                observed=semantics.get("empty_selection"),
            )
        )
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
    selected_lenses = payload.get("selected_lenses", [])
    selected_categories = payload.get("selected_categories", [])
    if not isinstance(selected_lenses, list):
        errors.append(blocker("blocked:status_contract_invalid", "status --json selected_lenses must be an array.", observed_type=type(selected_lenses).__name__))
    if not isinstance(selected_categories, list):
        errors.append(blocker("blocked:status_contract_invalid", "status --json selected_categories must be an array.", observed_type=type(selected_categories).__name__))
    effective_lens_mode = payload.get("effective_lens_mode")
    if effective_lens_mode not in LENS_EFFECTIVE_MODES:
        errors.append(blocker("blocked:status_contract_invalid", "status --json must include effective_lens_mode=all|selected.", observed=effective_lens_mode))
    if payload.get("lens_selection_scope") not in {None, "session"}:
        errors.append(blocker("blocked:status_contract_invalid", "status --json lens_selection_scope must be session when present.", observed=payload.get("lens_selection_scope")))
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
    elif command == "list-lenses":
        errors.extend(validate_list_lenses_payload(payload))
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


def build_phase1_readiness_warnings(execute_cli: bool, cli_details: dict[str, Any]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if not execute_cli:
        warnings.append(
            {
                "code": "warning:read_contract_cli_execution_skipped",
                "message": "Read-contract CLI execution was skipped because readiness ran in static-only mode.",
                "cli_execution_mode": "static-only",
                "skip_reason": cli_details.get("skip_reason") or "static_only_no_exec_cli",
                "blocks_control_mode": True,
            }
        )
    return warnings


def phase1_checked_file_record(role: str, path: str | Path, exists: Any, *, source: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": norm(path),
        "exists": bool(exists),
        "source": source,
    }


def build_phase1_checked_files(
    agent_details: dict[str, Any],
    prompt_details: dict[str, Any],
    mode_cli_surface: dict[str, Any],
    on_details: dict[str, Any],
    off_details: dict[str, Any],
    hook_details: dict[str, Any],
    operator_doc_details: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def append(role: str, details: dict[str, Any], *, source: str) -> None:
        path = details.get("path")
        if path is None:
            return
        records.append(phase1_checked_file_record(role, path, details.get("exists"), source=source))

    append("agent_toml", agent_details, source="agent_toml")
    append("private_prompt_source", prompt_details, source="private_prompt_source")
    append("mode_cli", mode_cli_surface, source="mode_cli_surface")
    append("on_wrapper", on_details, source="wrappers.on")
    append("off_wrapper", off_details, source="wrappers.off")

    for item in hook_details.get("candidates_checked") or []:
        if isinstance(item, dict):
            append("startup_hook", item, source="startup_activation_hooks.candidates_checked")
    for item in operator_doc_details.get("candidates_checked") or []:
        if isinstance(item, dict):
            append("operator_doc", item, source="operator_docs.candidates_checked")

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        key = (str(record["role"]), str(record["path"]), str(record["source"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def build_phase1_redacted_paths(checked_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters: dict[str, int] = {}
    redacted: list[dict[str, Any]] = []
    for record in checked_files:
        role = str(record.get("role") or "path")
        counters[role] = counters.get(role, 0) + 1
        alias = f"phase1.{role}" if counters[role] == 1 else f"phase1.{role}.{counters[role]}"
        redacted.append(
            {
                "alias": alias,
                "role": role,
                "path": str(record.get("path") or ""),
                "exists": bool(record.get("exists")),
            }
        )
    return redacted


def execution_blocking_static_codes(errors: list[dict[str, Any]]) -> list[str]:
    codes: list[str] = []
    for error in errors:
        code = str(error.get("code") or "")
        if code and code not in codes:
            codes.append(code)
    return sorted(codes)


def launcher_text() -> str:
    return '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Windows no-CMD daemon policy is delegated to project_moe_gui.daemon:
# CREATE_NO_WINDOW / DETACHED_PROCESS flags plus a duplicate-instance lock.

def emit(payload: dict, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload.get('token')}: {payload.get('message')}")
    return int(payload.get("exit_code", 0))


def maybe_reexec_with_runtime(config: dict, args: argparse.Namespace, launcher: Path, project_root: Path) -> int | None:
    if os.environ.get("PROJECT_MOE_GUI_RUNTIME_REEXEC") == "1":
        return None
    runtime_python = Path(str(config.get("runtime_python") or ""))
    if not runtime_python:
        return None
    try:
        current_python = Path(sys.executable).resolve(strict=False)
        configured_python = runtime_python.resolve(strict=False)
    except Exception:
        current_python = Path(sys.executable)
        configured_python = runtime_python
    if current_python == configured_python:
        return None
    if not runtime_python.exists():
        return None
    env = os.environ.copy()
    env["PROJECT_MOE_GUI_RUNTIME_REEXEC"] = "1"
    env.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(
        [str(runtime_python), str(launcher), *sys.argv[1:]],
        cwd=str(project_root),
        env=env,
        check=False,
    )
    return int(result.returncode)


def qfluent_status_summary() -> dict:
    try:
        from project_moe_gui import qfluent_runtime
        return qfluent_runtime.check_qfluent_runtime()
    except Exception as exc:
        return {
            "schema_version": 1,
            "ok": False,
            "token": "blocked:qfluentwidgets_unavailable",
            "import_status": "missing",
            "message": "QFluentWidgets runtime check failed.",
            "error": str(exc),
            "blockers": [{"code": "blocked:qfluentwidgets_unavailable", "message": "QFluentWidgets is unavailable."}],
        }


def _windows_process_flags() -> int:
    if not sys.platform.startswith("win"):
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)) | int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))


def _windows_process_flags_label(flags: int) -> str:
    if not flags:
        return "none"
    labels = []
    if flags & int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)):
        labels.append("CREATE_NO_WINDOW")
    if flags & int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008)):
        labels.append("DETACHED_PROCESS")
    return "|".join(labels) if labels else str(flags)


def _fallback_daemon_launch_plan(launcher: Path, args: argparse.Namespace, config: dict, project_root: Path) -> dict:
    no_args = not args.preflight and not args.json and not args.allow_visible
    if args.preflight and args.json:
        return {
            "schema_version": 1,
            "uses_daemon": False,
            "reason": "preflight_json_runs_in_foreground",
            "launcher": str(launcher),
            "cmd_window_policy": "foreground_machine_output",
            "fallback_embedded_daemon": True,
        }
    should_daemon = bool(no_args)
    flags = _windows_process_flags()
    runtime_dir = project_root / ".project-runtime" / "project_moe_gui"
    log_path = runtime_dir / "project_moe_gui.daemon.log"
    lock_path = runtime_dir / "project_moe_gui.daemon.lock"
    configured_python = str(config.get("runtime_python") or sys.executable)
    selected_python = configured_python
    pythonw_available = False
    configured_path = Path(configured_python)
    if should_daemon and configured_path.name.lower() == "python.exe":
        pythonw = configured_path.with_name("pythonw.exe")
        if pythonw.exists():
            selected_python = str(pythonw)
            pythonw_available = True
    return {
        "schema_version": 1,
        "uses_daemon": should_daemon,
        "reason": "no_argument_human_launch_uses_project_daemon" if should_daemon else "foreground_launch_requested",
        "launcher": str(launcher),
        "project_root": str(project_root),
        "configured_python_executable": configured_python,
        "selected_python_executable": selected_python,
        "pythonw_available": pythonw_available,
        "pythonw_policy": "prefer_pythonw_for_no_console_human_gui_daemon" if should_daemon else "foreground_keeps_configured_python",
        "argv": [selected_python, str(launcher), "--allow-visible"],
        "shell": False,
        "cmd_window_policy": "no_persistent_cmd" if should_daemon else "foreground",
        "windows_creation_flags": flags,
        "windows_creation_flags_label": _windows_process_flags_label(flags),
        "duplicate_instance_guard": {
            "enabled": True,
            "lock_path": str(lock_path),
            "pid_field": "pid",
            "stale_lock_cleanup": True,
        },
        "diagnostics_log": str(log_path),
        "stdout_stderr_policy": "append_to_diagnostics_log",
        "environment_overrides": {"PROJECT_MOE_GUI_DAEMON_CHILD": "1", "PYTHONUTF8": "1"},
        "fallback_embedded_daemon": True,
    }


def daemon_launch_plan(launcher: Path, args: argparse.Namespace, config: dict, project_root: Path) -> dict:
    try:
        from project_moe_gui.daemon import build_daemon_launch_plan
        return build_daemon_launch_plan(
            launcher,
            no_args=not args.preflight and not args.json and not args.allow_visible,
            preflight=args.preflight,
            json_mode=args.json,
            allow_visible=args.allow_visible,
            runtime_python=str(config.get("runtime_python") or sys.executable),
            project_root=project_root,
        )
    except Exception:
        return _fallback_daemon_launch_plan(launcher, args, config, project_root)


def _pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _fallback_spawn_daemon_child(plan: dict) -> dict:
    lock_info = plan.get("duplicate_instance_guard") or {}
    lock_path = Path(str(lock_info.get("lock_path") or ""))
    if lock_path.exists():
        try:
            payload = json.loads(lock_path.read_text(encoding="utf-8-sig"))
            pid = int(payload.get("pid") or 0)
        except Exception:
            pid = 0
        if _pid_running(pid):
            return {"schema_version": 1, "ok": True, "token": "ok:already_running", "exit_code": 0, "message": "Project MOE GUI daemon already appears to be running.", "daemon_launch": plan, "existing_pid": pid}
        try:
            lock_path.unlink()
        except Exception:
            pass
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in (plan.get("environment_overrides") or {}).items()})
    log_path = Path(str(plan.get("diagnostics_log") or lock_path.with_name("project_moe_gui.daemon.log")))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", errors="replace") as log_handle:
        log_handle.write("\\n=== Project MOE GUI daemon launch ===\\n")
        log_handle.write(f"argv={plan.get('argv')}\\n")
        log_handle.flush()
        kwargs = {"cwd": plan.get("project_root") or None, "env": env, "stdin": subprocess.DEVNULL, "stdout": log_handle, "stderr": subprocess.STDOUT, "shell": False}
        flags = int(plan.get("windows_creation_flags") or 0)
        if flags:
            kwargs["creationflags"] = flags
        process = subprocess.Popen([str(item) for item in plan.get("argv", [])], **kwargs)
    return {"schema_version": 1, "ok": True, "token": "ok", "exit_code": 0, "message": "Project MOE GUI daemon launch requested; launcher parent can exit without a persistent CMD window.", "daemon_launch": plan, "spawned_pid": process.pid, "diagnostics_log": str(log_path)}


def spawn_daemon_if_needed(plan: dict) -> dict:
    if not plan.get("uses_daemon"):
        return {"schema_version": 1, "ok": False, "token": "blocked:daemon_not_selected", "exit_code": 2, "message": "Daemon launch was not selected for this invocation.", "daemon_launch": plan}
    try:
        from project_moe_gui.daemon import spawn_daemon_child
        return spawn_daemon_child(plan)
    except Exception:
        return _fallback_spawn_daemon_child(plan)


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch or preflight the project-local MOE GUI.")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--allow-visible", action="store_true", help="Launch a visible PySide6 window. Kept for compatibility; no-argument human launches are visible by default.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    launcher = Path(__file__).resolve()
    config_path = launcher.with_name("project_moe_gui.config.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:launcher_config_invalid", "exit_code": 5, "message": "Cannot read Project Expert Lens GUI config.", "error": str(exc)}, args.json)

    project_root = launcher.parents[2]
    source_root = Path(str(config.get("toolchain_source_root") or ""))
    if source_root:
        sys.path.insert(0, str(source_root / "src"))
    mode_cli_value = str(config.get("mode_cli", "tools/thesis_moe_mode.py"))
    mode_cli = project_root / mode_cli_value
    daemon_plan = daemon_launch_plan(launcher, args, config, project_root)
    if daemon_plan.get("uses_daemon") and os.environ.get("PROJECT_MOE_GUI_DAEMON_CHILD") != "1" and os.environ.get("PROJECT_MOE_GUI_DRY_RUN_VISIBLE") != "1":
        return emit(spawn_daemon_if_needed(daemon_plan), args.json)
    runtime_reexec = maybe_reexec_with_runtime(config, args, launcher, project_root)
    if runtime_reexec is not None:
        return runtime_reexec
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

    try:
        from project_moe_gui.toolchain import check_phase1_readiness
        readiness = check_phase1_readiness(
            project_root,
            str(config.get("agent_name") or ""),
            str(config.get("state_namespace") or ""),
            Path(mode_cli_value),
            execute_cli=True,
            allow_runtime_state_dirty=True,
            allow_dirty_target_warning=True,
        )
    except Exception as exc:
        return emit({
            "schema_version": 1,
            "ok": False,
            "token": "blocked:phase1_readiness_gate_unavailable",
            "exit_code": 5,
            "message": "Cannot run Project Expert Lens Phase 1 readiness gate before GUI preflight.",
            "project_root": str(project_root),
            "mode_cli": str(mode_cli),
            "error": str(exc),
            "control_mode_allowed": False,
            "target_project_write_allowed_by_launcher": False,
            "blockers": [{"code": "blocked:phase1_readiness_gate_unavailable", "message": "Cannot run Project Expert Lens Phase 1 readiness gate before GUI preflight.", "error": str(exc)}],
        }, args.json)

    if not (readiness.get("ok") and readiness.get("control_mode_allowed") is True and readiness.get("readiness_status") == "ready"):
        remediation = readiness.get("remediation_plan") if isinstance(readiness, dict) else {}
        return emit({
            "schema_version": 1,
            "ok": False,
            "token": str(readiness.get("token") or "blocked:phase1_readiness_gate_failed"),
            "exit_code": 5,
            "message": "Project Expert Lens Phase 1 readiness gate blocks GUI preflight before target CLI reads.",
            "project_root": str(project_root),
            "mode_cli": str(mode_cli),
            "readiness_status": readiness.get("readiness_status"),
            "adaptation_lane": readiness.get("adaptation_lane"),
            "bootstrap_required": readiness.get("bootstrap_required"),
            "repair_required": readiness.get("repair_required"),
            "control_mode_allowed": False,
            "target_project_write_allowed_by_launcher": False,
            "cli_contract_check": readiness.get("cli_contract_check"),
            "phase1_readiness_gate": readiness,
            "remediation_plan": remediation,
            "operator_next_steps": remediation.get("ordered_next_steps", []) if isinstance(remediation, dict) else [],
            "blockers": readiness.get("blockers", []),
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
    lenses_payload, lenses_error = run_mode("list-lenses")
    status_payload, status_error = run_mode("status")
    cli_errors = [err for err in [project_error, sessions_error, lenses_error, status_error] if err]
    if cli_errors:
        return emit({"schema_version": 1, "ok": False, "token": cli_errors[0]["token"], "exit_code": cli_errors[0].get("exit_code", 5), "message": cli_errors[0]["message"], "project_root": str(project_root), "blockers": cli_errors}, args.json)

    try:
        from project_moe_gui import gui_shell
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:gui_shell_unavailable", "exit_code": 5, "message": "Cannot import central Project Expert Lens GUI shell.", "toolchain_source_root": str(source_root), "error": str(exc)}, args.json)

    runtime_config = dict(config)
    runtime_config["runtime_project_root"] = str(project_root)
    qfluent_status = qfluent_status_summary()
    try:
        preflight = gui_shell.build_gui_preflight(runtime_config, project_status=project_status, sessions_payload=sessions_payload, lenses_payload=lenses_payload, status_payload=status_payload, project_root=project_root, qfluent_status=qfluent_status)
    except TypeError:
        preflight = gui_shell.build_gui_preflight(runtime_config, project_status=project_status, sessions_payload=sessions_payload, status_payload=status_payload, project_root=project_root)
        view_model = preflight.get("view_model") if isinstance(preflight, dict) else None
        if isinstance(view_model, dict):
            view_model.setdefault("visual", {"library": "QFluentWidgets", "package_name": "PySide6-Fluent-Widgets", "import_name": "qfluentwidgets", "qfluentwidgets_status": qfluent_status})
            view_model.setdefault("close_behavior", {"default_close_action": "ask", "auto_hide_to_tray": False, "dialog_options": ["exit", "hide_to_tray", "cancel"], "tray_menu_items": ["show", "exit"]})
    preflight["launcher_runtime_python"] = sys.executable
    preflight["launcher_runtime_reexec"] = os.environ.get("PROJECT_MOE_GUI_RUNTIME_REEXEC") == "1"
    preflight["daemon_launch"] = daemon_plan
    preflight["qfluentwidgets_status"] = qfluent_status
    preflight["phase1_warnings"] = list(readiness.get("warnings") or [])
    preflight["phase1_readiness_gate"] = {
        "readiness_status": readiness.get("readiness_status"),
        "adaptation_lane": readiness.get("adaptation_lane"),
        "control_mode_allowed": readiness.get("control_mode_allowed"),
        "cli_execution_mode": readiness.get("cli_execution_mode"),
        "git_status": readiness.get("git_status"),
        "warnings": list(readiness.get("warnings") or []),
    }
    if args.preflight:
        return emit(preflight, args.json)
    if args.json and not args.allow_visible:
        return emit({**preflight, "ok": False, "token": "blocked:json_requires_preflight_for_non_visible_automation", "exit_code": 2, "message": "Use --preflight --json for machine-readable automation, or run without --json to open the visible GUI."}, args.json)
    if os.environ.get("PROJECT_MOE_GUI_DRY_RUN_VISIBLE") == "1":
        return emit({**preflight, "ok": True, "token": "ok", "exit_code": 0, "message": "Visible GUI launch dry-run passed.", "visible_launch": {"dry_run": True, "default_visible_on_no_args": True, "allow_visible_argument": bool(args.allow_visible)}}, args.json)
    view_model = preflight.get("view_model") if isinstance(preflight, dict) else None
    if not preflight.get("ok") and not isinstance(view_model, dict):
        return emit(preflight, args.json)
    try:
        try:
            return gui_shell.launch_visible(view_model, runtime_config, project_root)
        except TypeError:
            return gui_shell.launch_visible(view_model)
    except RuntimeError as exc:
        return emit({"schema_version": 1, "ok": False, "token": str(exc), "exit_code": 5, "message": "Visible GUI launch failed.", "error": str(exc)}, args.json)
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:visible_gui_launch_failed", "exit_code": 5, "message": "Visible GUI launch failed.", "error": str(exc)}, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
'''


def cmd_text(runtime_root: Path = DEFAULT_SHARED_RUNTIME_ROOT) -> str:
    runtime_python = runtime_root / ".venv" / "Scripts" / "python.exe"
    return (
        '@echo off\n'
        'setlocal\n'
        'set PYTHONUTF8=1\n'
        'if not defined PROJECT_MOE_GUI_DAEMON_CHILD set PROJECT_MOE_GUI_DAEMON_CHILD=\n'
        'cd /d "%~dp0"\n'
        f'set "PROJECT_MOE_GUI_CONFIGURED_PYTHON={win_rel(runtime_python)}"\n'
        'if exist "%PROJECT_MOE_GUI_CONFIGURED_PYTHON%" (\n'
        '  "%PROJECT_MOE_GUI_CONFIGURED_PYTHON%" "%~dp0tools\\project_moe_gui\\launcher.py" %*\n'
        ') else (\n'
        '  python "%~dp0tools\\project_moe_gui\\launcher.py" %*\n'
        ')\n'
        'exit /b %ERRORLEVEL%\n'
    )


def silent_vbs_text(diagnostic_entry: str = "project-moe-gui.cmd") -> str:
    return f'''Option Explicit
Dim shell, fso, scriptDir, command, i
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
command = QuoteArg(scriptDir & "\\{diagnostic_entry}")
For i = 0 To WScript.Arguments.Count - 1
  command = command & " " & QuoteArg(WScript.Arguments(i))
Next
shell.CurrentDirectory = scriptDir
shell.Run command, 0, False

Function QuoteArg(value)
  QuoteArg = Chr(34) & Replace(CStr(value), Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function
'''


def qml_shell_text() -> str:
    return qml_shell_path(prefer_installed=False).read_text(encoding="utf-8")


def readme_text(agent_name: str, namespace: str) -> str:
    return f"""# Project Expert Lens Agent GUI managed artifacts

This directory is managed by `D:\\PythonProject_langgraph` Project Expert Lens Agent GUI toolchain.

- Agent: `{agent_name}`
- State namespace: `{namespace}`
- CLI contract: `{CLI_CONTRACT}`
- GUI shell contract: `{GUI_SHELL_CONTRACT}`

Do not place private `MOE.md` content or project state files in this directory.
Phase 2B provides an import-safe GUI shell and guarded visible-launch path through the central toolchain source. Human double-click or no-argument launches open the visible PySide6 GUI by default; automated checks must use `--preflight --json` and never rely on the no-argument human launcher as a machine interface.

Launch entries:

- `project-expert-lens-gui.cmd`: canonical diagnostic entry. It may show CMD/PowerShell output and supports `--preflight --json`.
- `project-expert-lens-gui-silent.vbs`: canonical no-console double-click entry for human GUI launch.
- `project-moe-gui.cmd`: legacy diagnostic alias, kept for compatibility.
- `project-moe-gui-silent.vbs`: legacy no-console alias, kept for compatibility.
"""


def config_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(existing or {})
    data.pop("target_project_root", None)
    data.pop("runtime_project_root", None)
    runtime_python = runtime_root / ".venv" / "Scripts" / "python.exe"
    daemon_plan = windows_daemon_artifact_plan(
        build_daemon_launch_plan(
            root / "tools" / "project_moe_gui" / "launcher.py",
            no_args=True,
            runtime_python=runtime_python,
            project_root=root,
        )
    )
    data.update(
        {
            "schema_version": SCHEMA_VERSION,
            "toolchain": TOOLCHAIN_NAME,
            "canonical_toolchain": CANONICAL_TOOLCHAIN_NAME,
            "product_display_name": PRODUCT_DISPLAY_NAME,
            "product_display_name_zh": PRODUCT_DISPLAY_NAME_ZH,
            "legacy_product_display_name": LEGACY_PRODUCT_DISPLAY_NAME,
            "toolchain_version": TOOLCHAIN_VERSION,
            "cli_contract": CLI_CONTRACT,
            "agent_name": agent_name,
            "state_namespace": namespace,
            "mode_cli": norm(mode_cli),
            "private_prompt_source": norm(DEFAULT_PRIVATE_PROMPT_SOURCE),
            "project_root_strategy": "launcher-parent-git-root",
            "pyside6_runtime": "shared-runtime",
            "python_runtime_strategy": "shared-gui-runtime",
            "python_utf8": True,
            "visual_dependency": {
                **expected_qfluent_dependency(),
                "library": "QFluentWidgets / Qt Widgets",
                "style": "Fluent Widgets",
                "primary_shell": "qfluentwidgets-qtwidgets",
                "fallback_shell": "qml-material",
            },
            "qml_shell": {
                "primary": False,
                "relative_path": norm(QML_RELATIVE),
                "style": "Material",
                "managed_artifact": True,
                "central_fallback_allowed": True,
                "fallback_role": "explicit-qml-fallback",
            },
            "legacy_visual_dependency": qml_visual_contract(),
            "gui_dependency_license_manifest": qfluent_license_manifest(),
            "product_shell_contract": PRODUCT_SHELL_CONTRACT,
            "product_shell": {
                "primary": True,
                "library": "QFluentWidgets / Qt Widgets",
                "style": "Fluent Widgets",
                "contract": PRODUCT_SHELL_CONTRACT,
                "qml_fallback_env": "PROJECT_MOE_GUI_USE_QML_FALLBACK=1",
            },
            "daemon_launch": daemon_plan,
            "silent_launch": {
                "entry": norm(SILENT_VBS_RELATIVE),
                "diagnostic_entry": norm(CMD_RELATIVE),
                "canonical_entry": norm(CANONICAL_SILENT_VBS_RELATIVE),
                "canonical_diagnostic_entry": norm(CANONICAL_CMD_RELATIVE),
                "uses_wscript_hidden_window": True,
                "keeps_preflight_on_cmd": True,
                "configured_python_executable": daemon_plan.get("configured_python_executable"),
                "selected_python_executable": daemon_plan.get("selected_python_executable"),
                "pythonw_available": daemon_plan.get("pythonw_available"),
            },
            "close_behavior": {
                "default_close_action": "ask",
                "auto_hide_to_tray": False,
                "dialog_options": ["exit", "hide_to_tray", "cancel"],
                "tray_menu_items": ["show", "exit"],
            },
            "shared_runtime_root": str(runtime_root),
            "runtime_python": str(runtime_python),
            "installed_target_project_root": str(root),
            "toolchain_source_root": str(stable_toolchain_source_root()),
            "gui_shell_contract": GUI_SHELL_CONTRACT,
            "codex_session_discovery": {
                "enabled": True,
                "strategy": "read-only-codex-session-jsonl-top-level-user-sessions-with-preview",
                "sessions_root": "%USERPROFILE%/.codex/sessions",
                "session_index_role": "supplemental-labels-only",
                "target_project_scope": "session_meta.cwd must be the installed target project or a child path, and thread_source must be top-level user session",
                "reads_message_bodies": True,
                "message_body_scope": "target_project_top_level_user_assistant_preview_only",
                "hides_child_agent_sessions_from_default_view": True,
                "discovered_only_rows_visible": True,
            },
            "running_session_turn_gate": {
                "enabled": True,
                "helper": norm(TURN_GATE_RELATIVE),
                "effect_timing": "next_user_message",
                "fail_closed_on_ambiguous_current_session": True,
            },
        }
    )
    return data


def artifacts(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing_config: dict[str, Any] | None = None) -> dict[Path, str]:
    return {
        LAUNCHER_RELATIVE: launcher_text(),
        CONFIG_RELATIVE: json.dumps(config_payload(root, agent_name, namespace, mode_cli, runtime_root, existing_config), ensure_ascii=False, indent=2) + "\n",
        README_RELATIVE: readme_text(agent_name, namespace),
        CMD_RELATIVE: cmd_text(runtime_root),
        SILENT_VBS_RELATIVE: silent_vbs_text(),
        CANONICAL_CMD_RELATIVE: cmd_text(runtime_root),
        CANONICAL_SILENT_VBS_RELATIVE: silent_vbs_text("project-expert-lens-gui.cmd"),
        QML_RELATIVE: qml_shell_text(),
        TURN_GATE_RELATIVE: phase1_turn_gate_template(mode_cli),
    }


def phase1_public_lens_catalog() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    category_by_lens: dict[str, str] = {}
    categories: list[dict[str, Any]] = []
    for category in DEFAULT_EXPERT_CATEGORIES:
        category_id = str(category["id"])
        lens_ids = [str(item) for item in category.get("lens_ids", [])]
        for lens_id in lens_ids:
            category_by_lens[lens_id] = category_id
        categories.append(
            {
                key: category[key]
                for key in (
                    "id",
                    "label",
                    "zh_label",
                    "en_label",
                    "description",
                    "zh_description",
                    "en_description",
                    "lens_ids",
                )
                if key in category
            }
        )
    lenses: list[dict[str, Any]] = []
    for lens in DEFAULT_EXPERT_LENSES:
        lens_id = str(lens["id"])
        payload = {
            key: lens[key]
            for key in ("id", "label", "zh_label", "en_label", "description", "zh_description", "en_description")
            if key in lens
        }
        payload["category"] = category_by_lens.get(lens_id, "strict_graduate_advisor")
        lenses.append(payload)
    return lenses, categories


def phase1_public_catalog_constants_text() -> str:
    lenses, categories = phase1_public_lens_catalog()
    thinking_model_lens_ids = list(DEPRECATED_LENS_ALIASES.get("thinking_dispatcher", []))
    lens_aliases = {str(key): [str(item) for item in value] for key, value in DEPRECATED_LENS_ALIASES.items()}
    category_aliases = {str(key): str(value) for key, value in LEGACY_CATEGORY_ID_ALIASES.items()}
    return "\n".join(
        [
            "THINKING_MODEL_LENS_IDS = " + json.dumps(thinking_model_lens_ids, ensure_ascii=False, indent=4),
            "DEPRECATED_LENS_ALIASES = " + json.dumps(lens_aliases, ensure_ascii=False, indent=4),
            "DEPRECATED_CATEGORY_ALIASES = " + json.dumps(category_aliases, ensure_ascii=False, indent=4),
            "PUBLIC_LENSES = " + json.dumps(lenses, ensure_ascii=False, indent=4),
            "PUBLIC_CATEGORIES = " + json.dumps(categories, ensure_ascii=False, indent=4),
            'LENS_IDS = {str(item["id"]) for item in PUBLIC_LENSES}',
            'CATEGORY_IDS = {str(item["id"]) for item in PUBLIC_CATEGORIES}',
            "",
        ]
    )


def _phase1_replace_catalog_constants(text: str) -> tuple[str, str | None]:
    public_start = text.find("PUBLIC_LENSES = [")
    if public_start < 0:
        return text, None
    constants_start = public_start
    for marker in ("THINKING_MODEL_LENS_IDS = [", "DEPRECATED_LENS_ALIASES = {", "DEPRECATED_CATEGORY_ALIASES = {"):
        marker_index = text.rfind("\n" + marker, 0, public_start)
        if marker_index >= 0:
            constants_start = min(constants_start, marker_index + 1)
    class_marker = "\n\nclass ThesisMoeError"
    end = text.find(class_marker, public_start)
    if end < 0:
        return text, "blocked:phase1_mode_cli_catalog_anchor_missing"
    return text[:constants_start] + phase1_public_catalog_constants_text() + text[end:], None


def _phase1_replace_selected_helpers(text: str) -> tuple[str, str | None]:
    replacement = '''def expand_lens_aliases(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        expanded = DEPRECATED_LENS_ALIASES.get(value, [value])
        for item in expanded:
            if item not in result:
                result.append(item)
    return result


def normalize_category_aliases(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        item = DEPRECATED_CATEGORY_ALIASES.get(value, value)
        if item not in result:
            result.append(item)
    return result


def selected_lenses_from(data: Optional[dict[str, Any]]) -> list[str]:
    return expand_lens_aliases(selected_list(data, "selected_lenses"))


def selected_categories_from(data: Optional[dict[str, Any]]) -> list[str]:
    return normalize_category_aliases(selected_list(data, "selected_categories"))


'''
    start_match = re.search(r"\ndef (?:expand_lens_aliases|normalize_category_aliases|selected_lenses_from)\(", text)
    if not start_match:
        return text, "blocked:phase1_mode_cli_selected_helper_anchor_missing"
    start = start_match.start() + 1
    end_match = re.search(r"\ndef effective_lens_mode\(", text[start:])
    if not end_match:
        return text, "blocked:phase1_mode_cli_selected_helper_anchor_missing"
    end = start + end_match.start() + 1
    return text[:start] + replacement + text[end:], None


def _phase1_replace_validate_lens_selection(text: str) -> tuple[str, str | None]:
    replacement = '''def validate_lens_selection(selected_lenses: list[str], selected_categories: list[str]) -> None:
    supported_lenses = set(LENS_IDS) | set(DEPRECATED_LENS_ALIASES)
    supported_categories = set(CATEGORY_IDS) | set(DEPRECATED_CATEGORY_ALIASES)
    invalid_lenses = [item for item in selected_lenses if item not in supported_lenses]
    invalid_categories = [item for item in selected_categories if item not in supported_categories]
    if invalid_lenses or invalid_categories:
        raise ThesisMoeError(
            "blocked:invalid_lens_selection",
            "selected MOE lens or category is not in the public list-lenses catalog",
            2,
            {
                "invalid_lenses": invalid_lenses,
                "invalid_categories": invalid_categories,
                "supported_lenses": sorted(supported_lenses),
                "supported_categories": sorted(supported_categories),
            },
        )
'''
    pattern = r"def validate_lens_selection\(selected_lenses: list\[str\], selected_categories: list\[str\]\) -> None:.*?(?=\n\ndef parsed_selection)"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        return text, "blocked:phase1_mode_cli_validate_anchor_missing"
    return new_text, None


def _phase1_replace_parsed_selection(text: str) -> tuple[str, str | None]:
    replacement = '''def parsed_selection(args: argparse.Namespace) -> tuple[Optional[list[str]], Optional[list[str]]]:
    lenses = getattr(args, "lens", None)
    categories = getattr(args, "category", None)
    selected_lenses = unique_preserve_order(lenses) if lenses is not None else None
    selected_categories = unique_preserve_order(categories) if categories is not None else None
    if selected_lenses is not None or selected_categories is not None:
        validate_lens_selection(selected_lenses or [], selected_categories or [])
    if selected_lenses is not None:
        selected_lenses = expand_lens_aliases(selected_lenses)
    if selected_categories is not None:
        selected_categories = normalize_category_aliases(selected_categories)
    return selected_lenses, selected_categories
'''
    pattern = r"def parsed_selection\(args: argparse.Namespace\) -> tuple\[Optional\[list\[str\]\], Optional\[list\[str\]\]\]:.*?(?=\n\ndef attach_lens_fields)"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        return text, "blocked:phase1_mode_cli_parsed_selection_anchor_missing"
    return new_text, None


def migrate_phase1_mode_cli_catalog_text(text: str) -> tuple[str, list[str]]:
    blockers: list[str] = []
    for migrate in (
        _phase1_replace_catalog_constants,
        _phase1_replace_selected_helpers,
        _phase1_replace_validate_lens_selection,
        _phase1_replace_parsed_selection,
    ):
        text, blocker_code = migrate(text)
        if blocker_code:
            blockers.append(blocker_code)
    return text, blockers


def phase1_mode_cli_catalog_migration_plan(root: Path, mode_cli: Path) -> dict[str, Any]:
    full, err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if err:
        return {"path": norm(mode_cli), "action": "blocked", "managed": False, "phase1_contract": True, "blocker": err}
    assert full is not None
    if not full.exists():
        return {"path": norm(mode_cli), "action": "unchanged", "managed": False, "phase1_contract": True, "reason": "mode_cli_missing"}
    original = read_text(full)
    if "PUBLIC_LENSES" not in original or "PUBLIC_CATEGORIES" not in original:
        return {"path": norm(mode_cli), "action": "unchanged", "managed": False, "phase1_contract": True, "reason": "public_catalog_not_detected"}
    migrated, blocker_codes = migrate_phase1_mode_cli_catalog_text(original)
    if blocker_codes:
        return {
            "path": norm(mode_cli),
            "action": "blocked",
            "managed": False,
            "phase1_contract": True,
            "blocker": blocker(blocker_codes[0], "Existing Phase 1 mode CLI catalog could not be safely migrated.", path=norm(mode_cli), blockers=blocker_codes),
        }
    if migrated == original:
        return {"path": norm(mode_cli), "action": "unchanged", "managed": False, "phase1_contract": True}
    return {
        "path": norm(mode_cli),
        "action": "update",
        "managed": False,
        "phase1_contract": True,
        "migration": "phase1_public_lens_catalog_0_2_41",
        "old_sha256": sha256_bytes(original.encode("utf-8")),
        "new_sha256": sha256_bytes(migrated.encode("utf-8")),
        "new_text": migrated,
    }


def apply_phase1_mode_cli_catalog_migration(root: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    if plan.get("action") != "update":
        return []
    rel = Path(str(plan.get("path") or ""))
    full, err = safe_relative(root, rel, "blocked:mode_cli_path_invalid")
    if err:
        raise RuntimeError(err["message"])
    assert full is not None
    status = write_text_if_changed(full, str(plan["new_text"]))
    return [{"path": norm(rel), "status": status, "managed": False, "phase1_contract": True}]


def public_phase1_cli_migration_action(plan: dict[str, Any]) -> dict[str, Any]:
    public = {key: value for key, value in plan.items() if key != "new_text"}
    if "new_text" in plan:
        public["new_text_redacted"] = True
    return public


def phase1_wrapper_migration_plan(root: Path, mode_cli: Path) -> list[dict[str, Any]]:
    planned: list[dict[str, Any]] = []
    for rel, command in [(DEFAULT_ON_WRAPPER, "project-on"), (DEFAULT_OFF_WRAPPER, "project-off")]:
        full, err = safe_relative(root, rel, "blocked:wrapper_path_invalid")
        canonical = phase1_wrapper_template(mode_cli, command)
        if err:
            planned.append({"path": norm(rel), "action": "blocked", "managed": False, "phase1_contract": True, "blocker": err})
            continue
        assert full is not None
        if not full.exists():
            planned.append({"path": norm(rel), "action": "unchanged", "managed": False, "phase1_contract": True, "reason": "wrapper_missing_phase1_scaffold_required"})
            continue
        old = read_text(full)
        action = "unchanged" if old == canonical else "update"
        planned.append(
            {
                "path": norm(rel),
                "action": action,
                "managed": False,
                "phase1_contract": True,
                "expected_command": command,
                "project_default_semantics": True,
                "hardcoded_lenses_or_categories": False,
                "reason": "already_current" if action == "unchanged" else "refresh_project_default_wrapper_contract",
                "new_text": canonical if action == "update" else None,
            }
        )
    return planned


def public_phase1_wrapper_migration_action(plan: dict[str, Any]) -> dict[str, Any]:
    public = {key: value for key, value in plan.items() if key != "new_text"}
    if plan.get("new_text") is not None:
        public["new_text_redacted"] = True
    return public


def apply_phase1_wrapper_migration(root: Path, plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for plan in plans:
        if plan.get("action") != "update":
            continue
        full, err = safe_relative(root, Path(str(plan.get("path") or "")), "blocked:wrapper_path_invalid")
        if err:
            raise RuntimeError(err["message"])
        assert full is not None
        applied.append({"path": str(plan["path"]), "status": write_text_if_changed(full, str(plan.get("new_text") or "")), "managed": False, "phase1_contract": True})
    return applied


def manifest_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, planned: dict[Path, str], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    managed = [{"path": norm(rel), "role": "managed", "sha256": sha256_bytes(text.encode("utf-8"))} for rel, text in planned.items()]
    managed.append({"path": norm(MANIFEST_RELATIVE), "role": "manifest", "sha256": None})
    return {
        "schema_version": SCHEMA_VERSION,
        "toolchain": TOOLCHAIN_NAME,
        "canonical_toolchain": CANONICAL_TOOLCHAIN_NAME,
        "product_display_name": PRODUCT_DISPLAY_NAME,
        "product_display_name_zh": PRODUCT_DISPLAY_NAME_ZH,
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
    private_prompt_source: Path = DEFAULT_PRIVATE_PROMPT_SOURCE,
    on_wrapper: Path = DEFAULT_ON_WRAPPER,
    off_wrapper: Path = DEFAULT_OFF_WRAPPER,
    startup_paths: list[Path] | None = None,
    operator_doc_paths: list[Path] | None = None,
    execute_cli: bool = True,
    allow_runtime_state_dirty: bool = False,
    allow_dirty_target_warning: bool = False,
) -> dict[str, Any]:
    errors = validate_identifiers(agent_name, namespace)
    evidence = project_evidence(root)
    if not evidence:
        errors.append(blocker("blocked:missing_project_evidence", "Target directory does not look like a project.", expected=PROJECT_EVIDENCE))
    git_status = git_status_summary(root)
    runtime_dirty = runtime_state_dirty_details(git_status, namespace) if git_status["token"] == "blocked:dirty_target_project" else None
    dirty_runtime_warnings: list[dict[str, Any]] = []
    if git_status["token"] == "blocked:dirty_target_project":
        if allow_runtime_state_dirty and runtime_dirty and runtime_dirty["all_dirty_records_runtime_state_only"]:
            git_status["token"] = "ok:runtime_state_dirty_allowed"
            git_status["runtime_state_dirty_allowed"] = True
            git_status["runtime_state_dirty_details"] = runtime_dirty
            dirty_runtime_warnings.append(dirty_target_runtime_warning(git_status, namespace, runtime_dirty))
        elif allow_dirty_target_warning:
            git_status["token"] = "ok:dirty_target_project_allowed_for_gui_runtime"
            git_status["dirty_target_warning_allowed"] = True
            git_status["runtime_state_dirty_details"] = runtime_dirty
            dirty_runtime_warnings.append(dirty_target_runtime_warning(git_status, namespace, runtime_dirty))
        else:
            errors.append(
                blocker(
                    "blocked:dirty_target_project",
                    "Target project has dirty or untracked files; preserve or classify them before Phase 1 writes.",
                    dirty_count=git_status["dirty_count"],
                    records_sample=git_status["records_sample"],
                    runtime_state_dirty_details=runtime_dirty,
                )
            )
    elif git_status["token"] == "blocked:git_status_unavailable":
        errors.append(blocker("blocked:git_status_unavailable", "Cannot run git status in target project.", stderr=git_status["stderr"]))

    agent_details, agent_errors = inspect_agent_toml(root, agent_name, namespace)
    errors.extend(agent_errors)
    prompt_details, prompt_errors = inspect_private_prompt(root, str(private_prompt_source or DEFAULT_PRIVATE_PROMPT_SOURCE))
    agent_details["private_prompt_source"] = norm(private_prompt_source or DEFAULT_PRIVATE_PROMPT_SOURCE)
    errors.extend(prompt_errors)
    mode_cli_surface, mode_surface_errors = inspect_mode_cli_surface(root, mode_cli)
    errors.extend(mode_surface_errors)
    cli_execution_mode = "execute-read-contract" if execute_cli else "static-only"
    on_details, on_errors = inspect_wrapper(root, on_wrapper, "project-on", mode_cli)
    off_details, off_errors = inspect_wrapper(root, off_wrapper, "project-off", mode_cli)
    errors.extend(on_errors)
    errors.extend(off_errors)
    hook_details, hook_errors = inspect_startup_hooks(root, startup_paths or list(DEFAULT_STARTUP_HOOK_CANDIDATES))
    errors.extend(hook_errors)
    operator_doc_details, operator_doc_errors = inspect_operator_docs(root, operator_doc_paths or list(DEFAULT_OPERATOR_DOC_CANDIDATES))
    errors.extend(operator_doc_errors)
    if mode_cli_surface.get("exists") and execute_cli and not errors:
        cli_errors, cli_details = check_cli_contract(root, mode_cli)
        errors.extend(cli_errors)
    elif mode_cli_surface.get("exists") and execute_cli:
        cli_details = skipped_cli_contract_details(mode_cli, "static_surface_blockers_present")
        cli_details["static_surface_blocking_codes"] = execution_blocking_static_codes(errors)
    elif mode_cli_surface.get("exists"):
        cli_details = skipped_cli_contract_details(mode_cli, "static_only_no_exec_cli")
    else:
        cli_details = skipped_cli_contract_details(mode_cli, "mode_cli_missing")
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
    warnings = [*dirty_runtime_warnings, *build_phase1_readiness_warnings(execute_cli, cli_details)]
    checked_files = build_phase1_checked_files(
        agent_details,
        prompt_details,
        mode_cli_surface,
        on_details,
        off_details,
        hook_details,
        operator_doc_details,
    )
    redacted_paths = build_phase1_redacted_paths(checked_files)
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
        "private_prompt_source_path": norm(private_prompt_source or DEFAULT_PRIVATE_PROMPT_SOURCE),
        "project_root_evidence": evidence,
        "git_status": git_status,
        "agent_toml": agent_details,
        "private_prompt_source": prompt_details,
        "mode_cli_surface": mode_cli_surface,
        "cli_contract_check": cli_details,
        "wrappers": {"on": on_details, "off": off_details},
        "startup_activation_hooks": hook_details,
        "operator_docs": operator_doc_details,
        "warnings": warnings,
        "checked_files": checked_files,
        "redacted_paths": redacted_paths,
        "blockers": errors,
        "next_actions": [] if not errors else sorted({error["code"] for error in errors}),
        "remediation_plan": remediation_plan,
    }


def phase1_agent_toml_template(agent_name: str, namespace: str, private_prompt_source: Path) -> str:
    private_prompt = norm(private_prompt_source)
    return (
        f'name = "{agent_name}"\n'
        'description = "Project-local Expert Lens agent. Replace this placeholder with a short project-specific description before enabling GUI control."\n'
        'developer_instructions = """\n'
        f'Project-local Expert Lens instructions live in the project-private prompt source `{private_prompt}`.\n'
        'Do not copy private prompt content into shared toolchain or user-level caches.\n'
        f'Project Expert Lens metadata is intentionally not stored as custom TOML tables; readiness is proven through GUI config, mode CLI, wrappers, startup hook, private prompt source, and .omx/state/{namespace}.\n'
        '"""\n'
    )

def phase1_private_prompt_placeholder(agent_name: str, namespace: str) -> str:
    return f"""# Project MOE private prompt placeholder

Agent: `{agent_name}`
State namespace: `{namespace}`

Replace this placeholder inside the target project only.
Do not copy another project's private `MOE.md` content into this file.
Do not move this content into `.codex/agents/`, `.omx/state/`, or Project Expert Lens GUI managed artifacts.
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
PUBLIC_LENSES = [
    {{"id": "blind_review", "label": "Blind-review expert", "zh_label": "盲审专家镜头", "en_label": "Blind-review expert", "description": "Public placeholder lens metadata only.", "category": "strict_graduate_advisor"}},
    {{"id": "aigc_risk", "label": "AIGC risk expert", "zh_label": "AIGC / AI 味风险镜头", "en_label": "AIGC risk expert", "description": "Public placeholder lens metadata only.", "category": "strict_graduate_advisor"}},
    {{"id": "socratic_cbt", "label": "Socratic CBT-style questioning expert", "zh_label": "认知行为式苏格拉底提问镜头", "en_label": "Socratic CBT-style questioning expert", "description": "Public placeholder lens metadata only.", "category": "socratic_questioning"}},
    {{"id": "feynman_learning", "label": "Feynman learning expert", "zh_label": "费曼学习法专家", "en_label": "Feynman learning expert", "description": "Public placeholder lens metadata only.", "category": "five_classic_thinking_models"}},
    {{"id": "first_principles", "label": "First principles expert", "zh_label": "第一性原理专家", "en_label": "First principles expert", "description": "Public placeholder lens metadata only.", "category": "five_classic_thinking_models"}},
    {{"id": "pyramid_principle", "label": "Pyramid principle expert", "zh_label": "金字塔原理专家", "en_label": "Pyramid principle expert", "description": "Public placeholder lens metadata only.", "category": "five_classic_thinking_models"}},
    {{"id": "swot_analysis", "label": "SWOT analysis expert", "zh_label": "SWOT 分析专家", "en_label": "SWOT analysis expert", "description": "Public placeholder lens metadata only.", "category": "five_classic_thinking_models"}},
    {{"id": "decision_tree", "label": "Decision tree model expert", "zh_label": "决策树模型专家", "en_label": "Decision tree model expert", "description": "Public placeholder lens metadata only.", "category": "five_classic_thinking_models"}},
]
PUBLIC_CATEGORIES = [
    {{"id": "strict_graduate_advisor", "label": "Strict Graduate Advisor Module", "zh_label": "严苛的研究生导师专家模块", "en_label": "Strict Graduate Advisor Module", "description": "Strict advisor public lenses.", "lens_ids": ["blind_review", "aigc_risk"]}},
    {{"id": "socratic_questioning", "label": "Socratic Questioning Module", "zh_label": "认知行为式提问专家模块", "en_label": "Socratic Questioning Module", "description": "Socratic public lenses.", "lens_ids": ["socratic_cbt"]}},
    {{"id": "five_classic_thinking_models", "label": "Five Classic Thinking Models Module", "zh_label": "五大经典思维模型专家模块", "en_label": "Five Classic Thinking Models Module", "description": "Five independent thinking-model public lenses.", "lens_ids": ["feynman_learning", "first_principles", "pyramid_principle", "swot_analysis", "decision_tree"]}},
]


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
    # project-on project-off project-status list-sessions list-lenses status on off set-lenses clear-lenses assert-on --json --session-id --lens --category
    payload = envelope(command)
    if command == "project-status":
        payload.update(project_default_enabled=False, registered_session_count=0, valid_session_count=0, invalid_session_count=0)
    elif command == "list-sessions":
        payload.update(sessions=[], counts={{"total": 0, "valid": 0, "invalid": 0}})
    elif command == "list-lenses":
        payload.update(
            lenses=PUBLIC_LENSES,
            categories=PUBLIC_CATEGORIES,
            selection_semantics={{"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"}},
            private_prompt_source_read=False,
        )
    elif command in {{"status", "assert-on"}}:
        payload.update(
            effective_enabled=False,
            effective_source="fail-closed",
            selected_lenses=[],
            selected_categories=[],
            effective_lens_mode="all",
            lens_selection_scope="session",
        )
    print(json.dumps(payload, ensure_ascii=False))
    return int(payload.get("exit_code", 5))


if __name__ == "__main__":
    raise SystemExit(main())
'''


def phase1_wrapper_template(mode_cli: Path, command: str) -> str:
    return (
        '@echo off\n'
        'setlocal\n'
        'set PYTHONUTF8=1\n'
        'rem Project-default MOE wrapper; lens/category selections are managed by the Project MOE CLI/GUI, not hard-coded here.\n'
        f'python "%~dp0{win_rel(mode_cli)}" {command} --json\n'
        'exit /b %ERRORLEVEL%\n'
    )


def phase1_startup_hook_template(mode_cli: Path) -> str:
    return f"""# Project startup MOE activation hook

Before every user message that leads to a substantive answer, and also on startup, resume, continue, reload, or phase change, run the turn gate when present:

```powershell
python .\\tools\\thesis_moe_turn_gate.py --json
```

Fallback when the turn gate is not available:

```powershell
python .\\{win_rel(mode_cli)} status --json
```

Only apply project MOE rules when the effective status says it is enabled.
If the command is missing, invalid, or returns a blocker, fail closed and report the stable token.
GUI changes to a running session do not interrupt the current response; they are applied on the next user message after this turn gate/status read.
"""


def phase1_turn_gate_template(mode_cli: Path) -> str:
    mode_cli_text = norm(mode_cli)
    return f'''#!/usr/bin/env python3
"""Per-turn Project Expert Lens status gate for running Codex sessions.

This helper is installed as a managed Project MOE GUI artifact. It reads only
Codex ``session_meta`` records to identify the current session and then delegates
all MOE state reads to the target project's Phase 1 CLI. It never reads message
bodies, credentials, private prompt files, or GUI-managed state JSON directly.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
CLI_CONTRACT = "{CLI_CONTRACT}"
DEFAULT_MODE_CLI = Path(r"{mode_cli_text}")
SESSION_ENV_CANDIDATES = (
    "THESIS_MOE_SESSION_ID",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
    "OPENAI_CODEX_SESSION_ID",
    "OH_MY_CODEX_SESSION_ID",
    "OMX_SESSION_ID",
    "CODEX_SESSION",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def emit(payload: dict[str, Any], json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{{payload.get('token')}}: {{payload.get('message') or payload.get('effective_enabled')}}")
    return int(payload.get("exit_code", 0 if payload.get("ok") else 1))


def blocker(code: str, message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {{
        "schema_version": SCHEMA_VERSION,
        "command": "turn-gate",
        "ok": False,
        "token": code,
        "exit_code": 1,
        "message": message,
        "generated_at": utc_now(),
        "effect_timing": "next_user_message",
        "effective_enabled": False,
        "effective_source": "fail-closed",
        "apply_project_moe_rules": False,
        "cli_contract": CLI_CONTRACT,
        "privacy_policy": {{
            "reads_codex_session_meta": True,
            "reads_message_bodies": False,
            "reads_credentials": False,
            "reads_private_prompt": False,
            "delegates_moe_state_to_mode_cli": True,
        }},
    }}
    payload.update(extra)
    return payload


def project_root_from_here() -> Path:
    return Path(__file__).resolve().parents[1]


def is_inside_project(candidate: str | Path | None, root: Path) -> bool:
    if candidate is None or str(candidate).strip() == "":
        return False
    try:
        path = Path(str(candidate)).expanduser().resolve(strict=False)
        root_resolved = root.resolve(strict=False)
        return path == root_resolved or root_resolved in path.parents
    except Exception:
        return False


def read_session_meta(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for index, line in enumerate(handle):
                if index >= 120:
                    break
                try:
                    item = json.loads(line)
                except Exception:
                    continue
                if not isinstance(item, dict) or item.get("type") != "session_meta":
                    continue
                payload = item.get("payload") if isinstance(item.get("payload"), dict) else item
                return payload if isinstance(payload, dict) else None
    except Exception:
        return None
    return None


def discover_project_sessions(root: Path, sessions_root: Path, *, max_files: int = 20000) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    scanned = 0
    skipped_other_project = 0
    skipped_without_meta = 0
    truncated = False
    if sessions_root.exists() and sessions_root.is_dir():
        try:
            files = sorted(sessions_root.rglob("*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True)
        except Exception:
            files = []
        for path in files:
            if scanned >= max_files:
                truncated = True
                break
            scanned += 1
            meta = read_session_meta(path)
            if not meta:
                skipped_without_meta += 1
                continue
            cwd = meta.get("cwd") or meta.get("project_root") or meta.get("working_directory") or meta.get("repo_root")
            if not is_inside_project(cwd, root):
                skipped_other_project += 1
                continue
            session_id = meta.get("id") or meta.get("session_id") or meta.get("thread_id") or meta.get("resume_id")
            if not session_id:
                skipped_without_meta += 1
                continue
            records.append(
                {{
                    "session_id": str(session_id),
                    "thread_id": str(meta.get("thread_id") or meta.get("resume_id") or session_id),
                    "updated_at": meta.get("timestamp") or meta.get("updated_at") or meta.get("created_at"),
                    "source": str(path),
                    "metadata_only": True,
                }}
            )
    deduped: dict[str, dict[str, Any]] = {{}}
    for item in records:
        deduped.setdefault(str(item["session_id"]), item)
    sessions = list(deduped.values())
    return {{
        "sessions_root": str(sessions_root),
        "sessions_root_exists": sessions_root.exists(),
        "sessions": sessions,
        "count": len(sessions),
        "scanned_files": scanned,
        "skipped_other_project": skipped_other_project,
        "skipped_without_meta": skipped_without_meta,
        "truncated": truncated,
        "reads_message_bodies": False,
    }}


def choose_current_session_id(root: Path, explicit_session_id: str | None, sessions_root: Path) -> tuple[str | None, str, dict[str, Any]]:
    if explicit_session_id:
        return explicit_session_id, "argument", {{"count": 0, "sessions": []}}
    for name in SESSION_ENV_CANDIDATES:
        value = os.environ.get(name)
        if value:
            return value, f"env:{{name}}", {{"count": 0, "sessions": []}}
    discovery = discover_project_sessions(root, sessions_root)
    sessions = discovery.get("sessions") if isinstance(discovery.get("sessions"), list) else []
    if len(sessions) == 1 and isinstance(sessions[0], dict):
        return str(sessions[0].get("session_id")), "codex-session-meta-unique", discovery
    if len(sessions) > 1:
        return None, "ambiguous-codex-session-meta", discovery
    return None, "missing", discovery


def public_status(payload: dict[str, Any], *, current_session_id_source: str, discovery: dict[str, Any]) -> dict[str, Any]:
    selected_lenses = payload.get("selected_lenses") if isinstance(payload.get("selected_lenses"), list) else []
    selected_categories = payload.get("selected_categories") if isinstance(payload.get("selected_categories"), list) else []
    effective_enabled = payload.get("effective_enabled") is True
    return {{
        "schema_version": SCHEMA_VERSION,
        "command": "turn-gate",
        "ok": payload.get("ok") is True,
        "token": str(payload.get("token") or "blocked:mode_cli_status_not_ok"),
        "exit_code": 0 if payload.get("ok") is True and payload.get("token") == "ok" else 1,
        "message": "Project MOE turn gate read effective session state.",
        "generated_at": utc_now(),
        "effect_timing": "next_user_message",
        "effective_enabled": effective_enabled,
        "effective_source": payload.get("effective_source") or "fail-closed",
        "apply_project_moe_rules": effective_enabled,
        "session_id": payload.get("session_id"),
        "session_id_source": payload.get("session_id_source"),
        "current_session_id_source": current_session_id_source,
        "selected_lenses": [str(item) for item in selected_lenses],
        "selected_categories": [str(item) for item in selected_categories],
        "effective_lens_mode": payload.get("effective_lens_mode") or ("selected" if selected_lenses or selected_categories else "all"),
        "lens_selection_scope": payload.get("lens_selection_scope") or "session",
        "project_default_enabled": payload.get("project_default_enabled"),
        "session_override_enabled": payload.get("session_override_enabled"),
        "status_reason": payload.get("status_reason"),
        "mode_cli_command": "status --json --session-id <current-session>",
        "cli_contract": payload.get("cli_contract") or CLI_CONTRACT,
        "codex_session_discovery": {{
            key: value for key, value in discovery.items() if key != "sessions"
        }},
        "privacy_policy": {{
            "reads_codex_session_meta": True,
            "reads_message_bodies": False,
            "reads_credentials": False,
            "reads_private_prompt": False,
            "delegates_moe_state_to_mode_cli": True,
        }},
    }}


def run_mode_cli(root: Path, mode_cli: Path, session_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    full_mode_cli = mode_cli if mode_cli.is_absolute() else root / mode_cli
    try:
        result = subprocess.run(
            [sys.executable, str(full_mode_cli), "status", "--json", "--session-id", str(session_id)],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return None, blocker("blocked:mode_cli_timeout", "Project MOE turn gate status read timed out.")
    except Exception as exc:
        return None, blocker("blocked:mode_cli_invocation_failed", "Project MOE turn gate could not invoke the target mode CLI.", error=str(exc))
    if result.returncode != 0:
        return None, blocker(
            "blocked:mode_cli_failed",
            "Project MOE turn gate status read returned non-zero.",
            exit_code=result.returncode,
            stderr=result.stderr[-800:],
        )
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        return None, blocker("blocked:mode_cli_invalid_json", "Project MOE turn gate status read did not emit JSON.", error=str(exc), stdout=result.stdout[-800:])
    if not isinstance(payload, dict):
        return None, blocker("blocked:mode_cli_invalid_json", "Project MOE turn gate status JSON must be an object.")
    return payload, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read Project Expert Lens status for the current running Codex session.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--session-id", help="Explicit current session id override.")
    parser.add_argument("--mode-cli", default=str(DEFAULT_MODE_CLI), help="Target-project Phase 1 mode CLI path.")
    parser.add_argument("--codex-sessions-root", help="Override Codex session log root for tests.")
    args = parser.parse_args(argv)

    root = project_root_from_here()
    sessions_root = Path(args.codex_sessions_root or Path(os.environ.get("USERPROFILE") or str(Path.home())) / ".codex" / "sessions").expanduser().resolve(strict=False)
    session_id, source, discovery = choose_current_session_id(root, args.session_id, sessions_root)
    if not session_id and source == "ambiguous-codex-session-meta":
        return emit(
            blocker(
                "blocked:ambiguous_current_session_id",
                "Multiple Codex sessions match this project; provide a runtime session environment variable or --session-id.",
                codex_session_discovery={{key: value for key, value in discovery.items() if key != "sessions"}},
                candidate_count=discovery.get("count"),
            ),
            args.json,
        )
    if not session_id:
        return emit(
            blocker(
                "blocked:current_session_id_unavailable",
                "No current Codex session id was available from environment or unique project session metadata.",
                codex_session_discovery={{key: value for key, value in discovery.items() if key != "sessions"}},
            ),
            args.json,
        )
    payload, error = run_mode_cli(root, Path(args.mode_cli), session_id)
    if error:
        error["current_session_id_source"] = source
        error["session_id"] = session_id
        return emit(error, args.json)
    assert payload is not None
    return emit(public_status(payload, current_session_id_source=source, discovery=discovery), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
'''


def phase1_operator_doc_template(mode_cli: Path, on_wrapper: Path, off_wrapper: Path) -> str:
    mode_cli_win = win_rel(mode_cli)
    return f"""# Project MOE Phase 1 operator guide

Use the project-local mode CLI and wrappers only; do not edit `.omx/state` JSON by hand.

Required commands:

- `python .\\{mode_cli_win} project-on`
- `python .\\{mode_cli_win} project-off`
- `python .\\{mode_cli_win} project-status --json`
- `python .\\{mode_cli_win} list-sessions --json`
- `python .\\{mode_cli_win} list-lenses --json`
- `python .\\{mode_cli_win} status --json`
- `python .\\{mode_cli_win} assert-on`
- `python .\\{mode_cli_win} on --session-id <id>`
- `python .\\{mode_cli_win} off --session-id <id>`
- `python .\\{mode_cli_win} set-lenses --session-id <id> --lens <lens-id> --category <category-id>`
- `python .\\{mode_cli_win} clear-lenses --session-id <id>`
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


def phase1_bootstrap_templates(
    agent_name: str,
    namespace: str,
    mode_cli: Path = DEFAULT_MODE_CLI,
    private_prompt_source: Path = DEFAULT_PRIVATE_PROMPT_SOURCE,
    on_wrapper: Path = DEFAULT_ON_WRAPPER,
    off_wrapper: Path = DEFAULT_OFF_WRAPPER,
    startup_hook: Path = DEFAULT_BOOTSTRAP_STARTUP_HOOK,
    operator_doc: Path = DEFAULT_BOOTSTRAP_OPERATOR_DOC,
) -> dict[Path, tuple[str, str, str]]:
    agent_rel = Path(".codex") / "agents" / f"{agent_name}.toml"
    return {
        agent_rel: ("agent_toml", phase1_agent_toml_template(agent_name, namespace, private_prompt_source), "manual-review-existing"),
        private_prompt_source: ("private_prompt_source", phase1_private_prompt_placeholder(agent_name, namespace), "preserve-existing-private-prompt"),
        mode_cli: ("mode_cli", phase1_mode_cli_template(agent_name, namespace), "manual-review-existing"),
        on_wrapper: ("phase1_wrapper_on", phase1_wrapper_template(mode_cli, "project-on"), "manual-review-existing"),
        off_wrapper: ("phase1_wrapper_off", phase1_wrapper_template(mode_cli, "project-off"), "manual-review-existing"),
        startup_hook: ("startup_activation_hook", phase1_startup_hook_template(mode_cli), "manual-update-existing"),
        operator_doc: ("operator_docs", phase1_operator_doc_template(mode_cli, on_wrapper, off_wrapper), "manual-update-existing"),
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

    templates = phase1_bootstrap_templates(agent_name, namespace, mode_cli, private_prompt_source, on_wrapper, off_wrapper, startup_hook, operator_doc)
    planned_writes = [
        bootstrap_plan_item(root, rel, role, content, existing_action=existing_action)
        for rel, (role, content, existing_action) in templates.items()
    ]
    plan_blockers = [item["blocker"] for item in planned_writes if item.get("action") == "blocked" and item.get("blocker")]
    errors.extend(plan_blockers)
    create_count = sum(1 for item in planned_writes if item.get("action") == "create")
    manual_review_count = sum(1 for item in planned_writes if str(item.get("action", "")).startswith("manual"))
    preserve_count = sum(1 for item in planned_writes if str(item.get("action", "")).startswith("preserve"))
    apply_blockers = phase1_bootstrap_apply_blockers(planned_writes, git_status, errors)
    operator_next_steps = phase1_bootstrap_operator_next_steps(planned_writes, git_status)
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "scaffold_project_moe_phase1",
        "mode": "dry-run",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "read_only": True,
        "writes_target_project": False,
        "apply_supported": True,
        "target_project_write_allowed_by_checker": not apply_blockers,
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
            "apply_blocked_count": len(apply_blockers),
        },
        "git_status": git_status,
        "project_root_evidence": evidence,
        "blockers": errors,
        "apply_blockers": apply_blockers,
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


def phase1_bootstrap_apply_blockers(planned_writes: list[dict[str, Any]], git_status: dict[str, Any], existing_errors: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    errors = list(existing_errors or [])
    git_token = str(git_status.get("token") or "")
    if git_token != "ok":
        errors.append(
            blocker(
                "blocked:dirty_target_project" if git_token == "blocked:dirty_target_project" else "blocked:git_status_unavailable",
                "Target project must be a clean Git worktree before applying Phase 1 scaffold files.",
                git_status=git_status,
            )
        )
    non_create = [item for item in planned_writes if item.get("action") != "create"]
    if non_create:
        errors.append(
            blocker(
                "blocked:existing_phase1_surface_requires_manual_review",
                "Scaffold --apply only creates missing Phase 1 files and never overwrites existing private or operator surfaces.",
                paths=[item.get("path") for item in non_create if item.get("path")],
                actions=[item.get("action") for item in non_create if item.get("action")],
            )
        )
    return errors


def phase1_bootstrap_scaffold_apply(
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
    plan = phase1_bootstrap_scaffold_plan(root, agent_name, namespace, mode_cli, private_prompt_source, on_wrapper, off_wrapper, startup_hook, operator_doc)
    templates = phase1_bootstrap_templates(agent_name, namespace, mode_cli, private_prompt_source, on_wrapper, off_wrapper, startup_hook, operator_doc)
    planned_writes = list(plan.get("planned_writes") or [])
    errors = phase1_bootstrap_apply_blockers(planned_writes, dict(plan.get("git_status") or {}), list(plan.get("blockers") or []))
    if errors:
        return {
            "schema_version": SCHEMA_VERSION,
            "command": "scaffold_project_moe_phase1",
            "mode": "apply",
            "ok": False,
            "token": errors[0]["code"],
            "exit_code": 4,
            "read_only": False,
            "writes_target_project": False,
            "apply_supported": True,
            "target_project_write_allowed_by_checker": False,
            "control_mode_allowed": False,
            "bootstrap_required": True,
            "adaptation_lane": "bootstrap",
            "target_project_root": str(root),
            "agent_name": agent_name,
            "state_namespace": namespace,
            "planned_writes": planned_writes,
            "git_status": plan.get("git_status"),
            "blockers": errors,
            "privacy_boundary": plan.get("privacy_boundary"),
        }

    applied: list[dict[str, Any]] = []
    for rel, (role, content, _existing_action) in templates.items():
        full, err = safe_relative(root, rel)
        if err:
            return {
                "schema_version": SCHEMA_VERSION,
                "command": "scaffold_project_moe_phase1",
                "mode": "apply",
                "ok": False,
                "token": err["code"],
                "exit_code": 4,
                "read_only": False,
                "writes_target_project": False,
                "apply_supported": True,
                "target_project_write_allowed_by_checker": False,
                "control_mode_allowed": False,
                "bootstrap_required": True,
                "adaptation_lane": "bootstrap",
                "target_project_root": str(root),
                "agent_name": agent_name,
                "state_namespace": namespace,
                "blockers": [err],
                "privacy_boundary": plan.get("privacy_boundary"),
            }
        assert full is not None
        if full.exists():
            err = blocker("blocked:scaffold_target_changed_before_apply", "Target scaffold path appeared before apply completed; refusing to overwrite.", path=norm(rel))
            return {
                "schema_version": SCHEMA_VERSION,
                "command": "scaffold_project_moe_phase1",
                "mode": "apply",
                "ok": False,
                "token": err["code"],
                "exit_code": 4,
                "read_only": False,
                "writes_target_project": False,
                "apply_supported": True,
                "target_project_write_allowed_by_checker": False,
                "control_mode_allowed": False,
                "bootstrap_required": True,
                "adaptation_lane": "bootstrap",
                "target_project_root": str(root),
                "agent_name": agent_name,
                "state_namespace": namespace,
                "blockers": [err],
                "privacy_boundary": plan.get("privacy_boundary"),
            }
        status = write_text_if_changed(full, content)
        applied.append({"path": norm(rel), "role": role, "status": status, "sha256": sha256_bytes(content.encode("utf-8")), "managed": False, "scaffold_owned": True})

    return {
        "schema_version": SCHEMA_VERSION,
        "command": "scaffold_project_moe_phase1",
        "mode": "apply",
        "ok": True,
        "token": "ok",
        "read_only": False,
        "writes_target_project": True,
        "apply_supported": True,
        "target_project_write_allowed_by_checker": True,
        "control_mode_allowed": False,
        "bootstrap_required": True,
        "adaptation_lane": "bootstrap",
        "lane_reason": "phase1_bootstrap_scaffold_applied_missing_files_only",
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "mode_cli": norm(mode_cli),
        "private_prompt_source": norm(private_prompt_source),
        "applied_writes": applied,
        "summary": {"created_count": len(applied), "blocked_count": 0},
        "git_status_before": plan.get("git_status"),
        "blockers": [],
        "next_actions": [
            "review_target_project_git_diff",
            "complete_placeholder_cli_and_private_prompt",
            "run_phase1_readiness_checker_static_only",
            "run_phase1_readiness_checker_execute_read_contract",
        ],
        "privacy_boundary": plan.get("privacy_boundary"),
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
    strict_errors, strict_git_status = strict_clean_git_errors(root, operation="install_project_moe_gui")
    if not dry_run and changed:
        errors.extend(strict_errors)
    manifest = manifest_payload(root, agent_name, namespace, mode_cli, planned, old_manifest)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": "install_project_moe_gui",
        "mode": "dry-run" if dry_run else "apply",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "toolchain": TOOLCHAIN_NAME,
        "canonical_toolchain": CANONICAL_TOOLCHAIN_NAME,
        "product_display_name": PRODUCT_DISPLAY_NAME,
        "product_display_name_zh": PRODUCT_DISPLAY_NAME_ZH,
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
        "git_status": strict_git_status,
        "clean_worktree_required_for_apply": True,
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


def managed_file_uninstall_plan(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    planned_deletes: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in manifest.get("managed_files", []):
        rel = norm(str(item.get("path") or "").strip())
        if not rel or rel in seen:
            continue
        seen.add(rel)
        expected = item.get("sha256")
        if rel not in UNINSTALL_MANAGED_ALLOWLIST:
            blocker_payload = blocker(
                "blocked:uninstall_path_not_in_managed_allowlist",
                "Uninstall may delete only the Project Expert Lens GUI managed artifact allowlist, even if a target manifest lists another path.",
                path=rel,
                allowed=sorted(UNINSTALL_MANAGED_ALLOWLIST),
            )
            errors.append(blocker_payload)
            planned_deletes.append({"path": rel, "action": "blocked", "safe_to_delete": False, "blocker": blocker_payload})
            continue
        if rel != norm(MANIFEST_RELATIVE) and not expected:
            blocker_payload = blocker(
                "blocked:managed_file_hash_missing",
                "Managed file must include a manifest hash before uninstall can delete it.",
                path=rel,
            )
            errors.append(blocker_payload)
            planned_deletes.append({"path": rel, "action": "blocked", "safe_to_delete": False, "blocker": blocker_payload})
            continue
        full, err = safe_relative(root, Path(rel))
        if err:
            errors.append(err)
            planned_deletes.append({"path": rel, "action": "blocked", "safe_to_delete": False, "blocker": err})
            continue
        assert full is not None
        exists = full.exists()
        action = "delete" if exists else "already_absent"
        observed = sha256_file(full) if exists and expected else None
        safe_to_delete = exists
        if exists and full.is_dir():
            blocker_payload = blocker(
                "blocked:managed_path_is_directory",
                "Uninstall deletes managed files only; directories are never removed from a manifest entry.",
                path=rel,
            )
            errors.append(blocker_payload)
            action = "blocked"
            safe_to_delete = False
        if exists and expected and observed != expected:
            blocker_payload = blocker(
                "blocked:managed_file_hash_mismatch",
                "Managed file hash does not match install manifest; uninstall plan must fail closed instead of deleting a locally changed file.",
                path=rel,
                expected=expected,
                observed=observed,
            )
            errors.append(blocker_payload)
            action = "blocked"
            safe_to_delete = False
        planned_deletes.append(
            {
                "path": rel,
                "role": item.get("role") or "managed",
                "action": action,
                "exists": exists,
                "safe_to_delete": safe_to_delete,
                "managed": True,
                "sha256_verified": bool(exists and expected and observed == expected),
            }
        )
    return planned_deletes, errors


def apply_managed_file_uninstall(root: Path, planned_deletes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for item in planned_deletes:
        rel = str(item.get("path") or "").strip()
        if item.get("action") != "delete" or item.get("safe_to_delete") is not True:
            applied.append({"path": rel, "status": "skipped", "reason": item.get("action") or "not_safe_to_delete"})
            continue
        full, err = safe_relative(root, Path(rel))
        if err:
            raise RuntimeError(err["message"])
        assert full is not None
        if not full.exists():
            applied.append({"path": rel, "status": "already_absent"})
            continue
        if full.is_dir():
            raise RuntimeError(f"Refusing to uninstall directory manifest entry: {rel}")
        full.unlink()
        applied.append({"path": rel, "status": "deleted"})
    return applied


def plan_uninstall(root: Path, apply_requested: bool = False) -> dict[str, Any]:
    manifest, config, load_errors = existing_install(root)
    errors: list[dict[str, Any]] = list(load_errors)
    planned_deletes: list[dict[str, Any]] = []
    protected_files: list[str] = []
    if not manifest or not config:
        errors.extend(load_errors or [blocker("blocked:not_installed", "Project Expert Lens GUI is not installed in target project.")])
    else:
        planned_deletes, delete_errors = managed_file_uninstall_plan(root, manifest)
        errors.extend(delete_errors)
        protected_files = list(manifest.get("protected_files") or [])
    applied_file_changes: list[dict[str, Any]] = []
    if apply_requested and not errors:
        try:
            applied_file_changes = apply_managed_file_uninstall(root, planned_deletes)
        except Exception as exc:
            errors.append(blocker("blocked:uninstall_apply_failed", "Project Expert Lens GUI uninstall apply failed before completing all planned deletes.", error=str(exc)))
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "plan_project_moe_gui_uninstall",
        "mode": "apply" if apply_requested and not errors else ("apply-requested" if apply_requested else "dry-run"),
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "read_only": not any(item.get("status") == "deleted" for item in applied_file_changes),
        "writes_target_project": any(item.get("status") == "deleted" for item in applied_file_changes),
        "apply_requested": apply_requested,
        "apply_supported": True,
        "delete_executed": any(item.get("status") == "deleted" for item in applied_file_changes),
        "target_project_root": str(root),
        "toolchain": TOOLCHAIN_NAME,
        "installed_toolchain_version": manifest.get("toolchain_version") if manifest else None,
        "target_toolchain_version": TOOLCHAIN_VERSION,
        "agent_name": (config or manifest or {}).get("agent_name") if (config or manifest) else None,
        "state_namespace": (config or manifest or {}).get("state_namespace") if (config or manifest) else None,
        "planned_deletes": planned_deletes,
        "protected_paths_preserved": protected_files,
        "state_deletion_allowed": False,
        "private_files_deletion_allowed": False,
        "blockers": errors,
        "rollback_hint": (manifest or {}).get("rollback_hint") or "Uninstall planning only covers managed GUI artifacts; preserve .omx/state, MOE.md, and .codex/agents/*.toml.",
        "applied_file_changes": applied_file_changes,
        "uninstall_receipt": {
            "schema_version": SCHEMA_VERSION,
            "executed": any(item.get("status") == "deleted" for item in applied_file_changes),
            "executed_at": now_utc() if any(item.get("status") == "deleted" for item in applied_file_changes) else None,
            "deleted_files": [item["path"] for item in applied_file_changes if item.get("status") == "deleted"],
            "skipped_private_files": protected_files,
            "state_deletion_allowed": False,
            "private_files_deletion_allowed": False,
            "rollback_hint": (manifest or {}).get("rollback_hint") or "Use target project Git history to restore managed GUI artifacts if needed.",
        },
    }


def check_install(root: Path, skip_runtime_import: bool = False) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    manifest, config, load_errors = existing_install(root)
    if not manifest or not config:
        errors.extend(load_errors or [blocker("blocked:not_installed", "Project Expert Lens GUI is not installed in target project.")])
    else:
        errors.extend(load_errors)
        errors.extend(hash_errors(root, manifest))
        agent = str(config.get("agent_name") or manifest.get("agent_name") or "")
        namespace = str(config.get("state_namespace") or manifest.get("state_namespace") or "")
        mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
        errors.extend(preflight(root, agent, namespace, mode_cli, True)[0])
        source_root = Path(str(config.get("toolchain_source_root") or ""))
        toolchain_source_status, toolchain_source_errors = validate_toolchain_source_root(source_root)
        errors.extend(toolchain_source_errors)
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
        "toolchain_source_root": str(config.get("toolchain_source_root")) if config else None,
        "toolchain_source_status": locals().get("toolchain_source_status", "unknown"),
        "blockers": errors,
        "rollback_hint": (manifest or {}).get("rollback_hint"),
    }


def update(root: Path, dry_run: bool, skip_runtime_import: bool = True) -> dict[str, Any]:
    current = check_install(root, skip_runtime_import=skip_runtime_import)
    current_blockers = list(current.get("blockers") or [])
    unrecoverable_blockers = [item for item in current_blockers if item.get("code") not in RECOVERABLE_UPDATE_BLOCKER_CODES]
    if unrecoverable_blockers:
        return {**current, "command": "update_project_moe_gui", "mode": "dry-run" if dry_run else "apply"}
    errors: list[dict[str, Any]] = []
    manifest = load_json(root / MANIFEST_RELATIVE, "blocked:not_installed", errors) or {}
    config = load_json(root / CONFIG_RELATIVE, "blocked:not_installed", errors) or {}
    agent = str(config.get("agent_name") or manifest.get("agent_name"))
    namespace = str(config.get("state_namespace") or manifest.get("state_namespace"))
    mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
    runtime_root = Path(str(config.get("shared_runtime_root") or DEFAULT_SHARED_RUNTIME_ROOT))
    planned = artifacts(root, agent, namespace, mode_cli, runtime_root, config)
    changes, managed_changed = planned_changes(root, planned)
    phase1_cli_migration = phase1_mode_cli_catalog_migration_plan(root, mode_cli)
    phase1_cli_actions = [public_phase1_cli_migration_action(phase1_cli_migration)]
    phase1_cli_changed = phase1_cli_migration.get("action") == "update"
    if phase1_cli_migration.get("action") == "blocked" and phase1_cli_migration.get("blocker"):
        errors.append(phase1_cli_migration["blocker"])
    phase1_wrapper_migrations = phase1_wrapper_migration_plan(root, mode_cli)
    phase1_wrapper_actions = [public_phase1_wrapper_migration_action(item) for item in phase1_wrapper_migrations]
    phase1_wrapper_changed = any(item.get("action") == "update" for item in phase1_wrapper_migrations)
    for item in phase1_wrapper_migrations:
        if item.get("action") == "blocked" and item.get("blocker"):
            errors.append(item["blocker"])
    changed = managed_changed or phase1_cli_changed or phase1_wrapper_changed
    strict_errors, strict_git_status = strict_clean_git_errors(root, operation="update_project_moe_gui")
    if not dry_run and changed:
        errors.extend(strict_errors)
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
        "migration_actions": changes + phase1_cli_actions + phase1_wrapper_actions,
        "phase1_cli_migration_actions": phase1_cli_actions,
        "phase1_wrapper_migration_actions": phase1_wrapper_actions,
        "no_op": not changed,
        "git_status": strict_git_status,
        "clean_worktree_required_for_apply": True,
        "recoverable_blockers": current_blockers,
        "blockers": errors,
        "rollback_hint": new_manifest["rollback_hint"],
    }
    if errors or dry_run:
        return payload
    payload["applied_file_changes"] = apply_artifacts(root, planned, new_manifest)
    payload["applied_file_changes"].extend(apply_phase1_mode_cli_catalog_migration(root, phase1_cli_migration))
    payload["applied_file_changes"].extend(apply_phase1_wrapper_migration(root, phase1_wrapper_migrations))
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
