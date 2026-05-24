from __future__ import annotations

import hashlib
import json
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
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    records = [line for line in result.stdout.splitlines() if line.strip()]
    return {
        "is_git_worktree": result.returncode == 0,
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
        return {"path": norm(mode_cli), "exists": False, "write_commands_seen": []}, [err]
    assert path is not None
    details: dict[str, Any] = {"path": norm(mode_cli), "exists": path.exists(), "write_commands_seen": []}
    if not path.exists():
        return details, [blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli))]
    text = read_text(path)
    hits = command_token_hits(text, PHASE1_EXPECTED_WRITE_COMMANDS)
    details["write_commands_seen"] = hits
    missing = [command for command in PHASE1_EXPECTED_WRITE_COMMANDS if command not in hits]
    errors = []
    if missing:
        errors.append(blocker("blocked:phase1_write_command_surface_incomplete", "Mode CLI text does not expose all expected Phase 1 command tokens.", missing=missing))
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
    for rel in startup_paths:
        path, err = safe_relative(root, rel, "blocked:startup_hook_path_invalid")
        if err:
            checked.append({"path": norm(rel), "exists": False, "token": err["code"]})
            continue
        assert path is not None
        exists = path.exists()
        has_hook = False
        if exists:
            text = read_text(path).lower()
            has_hook = "thesis_moe_mode.py" in text and "status" in text and "--json" in text
            hook_found = hook_found or has_hook
        checked.append({"path": norm(rel), "exists": exists, "has_moe_status_hook": has_hook})
    errors = [] if hook_found else [blocker("blocked:missing_moe_activation_hook", "No startup or launcher file contains a MOE status --json activation checkpoint.")]
    return {"candidates_checked": checked, "hook_found": hook_found}, errors


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


def check_cli_contract(root: Path, mode_cli: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    details: dict[str, Any] = {"mode_cli": norm(mode_cli), "commands_checked": [], "assertion_commands_checked": [], "validated_fields": {}}
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
    mode_cli = project_root / str(config.get("mode_cli", "tools/thesis_moe_mode.py"))
    if not mode_cli.exists():
        return emit({"schema_version": 1, "ok": False, "token": "blocked:missing_mode_cli", "exit_code": 5, "message": "Target project mode CLI is missing.", "project_root": str(project_root), "mode_cli": str(mode_cli)}, args.json)

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

    source_root = Path(str(config.get("toolchain_source_root") or ""))
    if source_root:
        sys.path.insert(0, str(source_root / "src"))
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
    if mode_cli_surface.get("exists"):
        cli_errors, cli_details = check_cli_contract(root, mode_cli)
        errors.extend(cli_errors)
    else:
        cli_details = {"mode_cli": norm(mode_cli), "commands_checked": [], "validated_fields": {}}
    on_details, on_errors = inspect_wrapper(root, on_wrapper, "project-on", mode_cli)
    off_details, off_errors = inspect_wrapper(root, off_wrapper, "project-off", mode_cli)
    errors.extend(on_errors)
    errors.extend(off_errors)
    hook_details, hook_errors = inspect_startup_hooks(root, startup_paths or list(DEFAULT_STARTUP_HOOK_CANDIDATES))
    errors.extend(hook_errors)
    operator_doc_details, operator_doc_errors = inspect_operator_docs(root, operator_doc_paths or list(DEFAULT_OPERATOR_DOC_CANDIDATES))
    errors.extend(operator_doc_errors)
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "check_project_moe_phase1_readiness",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "readiness_status": "ready" if not errors else "blocked",
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
