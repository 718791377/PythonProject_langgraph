from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from project_moe_gui import CLI_CONTRACT


SCHEMA_VERSION = 1
GUI_SHELL_CONTRACT = "project-moe-gui-shell-v1"
WINDOW_TITLE = "Project MOE Agent Console"
DEFAULT_MODE_CLI = "tools/thesis_moe_mode.py"
READ_ACTIONS = {"refresh", "project-status", "list-sessions", "status"}
WRITE_ACTIONS = {"project-on", "project-off", "session-on", "session-off"}
ACTION_COMMANDS = {
    "project-status": ["project-status", "--json"],
    "list-sessions": ["list-sessions", "--json"],
    "status": ["status", "--json"],
    "project-on": ["project-on", "--json"],
    "project-off": ["project-off", "--json"],
    "session-on": ["on", "--json"],
    "session-off": ["off", "--json"],
}
WRITE_CLI_REQUIRED_FIELDS = (
    "schema_version",
    "command",
    "ok",
    "token",
    "cli_contract",
    "before",
    "after",
    "changed_scope",
    "changed_paths",
    "skipped_invalid_records",
    "lock_status",
    "audit_path",
    "no_op",
)
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
KEYBOARD_SHORTCUTS = {
    "refresh": "F5",
    "project-on": "Alt+P",
    "project-off": "Alt+Shift+P",
    "session-on": "Alt+S",
    "session-off": "Alt+Shift+S",
}


def expected_cli_command_for_action(action: str) -> str:
    if action == "session-on":
        return "on"
    if action == "session-off":
        return "off"
    return action


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


def validate_write_cli_payload(action: str, payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return [
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command JSON payload must be an object.",
                action=action,
            )
        ]
    errors: list[dict[str, Any]] = []
    missing = [field for field in WRITE_CLI_REQUIRED_FIELDS if field not in payload]
    if missing:
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_missing_fields",
                "Write command JSON payload is missing required fields for GUI-safe state changes.",
                action=action,
                missing=missing,
            )
        )
    expected_command = expected_cli_command_for_action(action)
    if payload.get("command") != expected_command:
        errors.append(
            stable_blocker(
                "blocked:write_cli_command_echo_mismatch",
                "Write command JSON command field must match the invoked CLI command.",
                action=action,
                expected=expected_command,
                observed=payload.get("command"),
            )
        )
    if payload.get("ok") is not True or payload.get("token") != "ok":
        errors.append(
            stable_blocker(
                "blocked:write_cli_command_not_ok",
                "Write command JSON must return ok/token=ok before the GUI accepts the state change.",
                action=action,
                token=payload.get("token"),
            )
        )
    if payload.get("cli_contract") != CLI_CONTRACT:
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_mismatch",
                "Write command CLI contract does not match project-moe-cli-v1.",
                action=action,
                observed=payload.get("cli_contract"),
            )
        )
    expected_scope = "session" if action.startswith("session-") else "project-default"
    if payload.get("changed_scope") != expected_scope:
        errors.append(
            stable_blocker(
                "blocked:write_cli_scope_mismatch",
                "Write command changed_scope must match the GUI action scope.",
                action=action,
                expected=expected_scope,
                observed=payload.get("changed_scope"),
            )
        )
    if not isinstance(payload.get("changed_paths"), list):
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command changed_paths must be a list.",
                action=action,
            )
        )
    if not isinstance(payload.get("skipped_invalid_records"), list):
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command skipped_invalid_records must be a list.",
                action=action,
            )
        )
    if not isinstance(payload.get("no_op"), bool):
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command no_op must be a boolean.",
                action=action,
            )
        )
    if action.startswith("session-") and not payload.get("session_id"):
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Session write commands must echo the normalized/redacted session_id.",
                action=action,
            )
        )
    private_hits = private_cli_field_hits(payload)
    if private_hits:
        errors.append(
            stable_blocker(
                "blocked:write_cli_private_field_exposed",
                "Write command JSON exposed private/raw fields that GUI contracts must not consume.",
                action=action,
                fields=private_hits[:12],
            )
        )
    return errors


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def stable_blocker(code: str, message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": message}
    payload.update(extra)
    return payload


def is_pyside6_available() -> bool:
    return importlib.util.find_spec("PySide6") is not None


def load_config(config_path: str | Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    path = Path(config_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, stable_blocker("blocked:launcher_config_missing", "Project MOE GUI config file is missing.", path=str(path))
    except Exception as exc:
        return None, stable_blocker("blocked:launcher_config_invalid", "Cannot parse Project MOE GUI config.", path=str(path), error=str(exc))
    if not isinstance(payload, dict):
        return None, stable_blocker("blocked:launcher_config_invalid", "Project MOE GUI config must be a JSON object.", path=str(path))
    return payload, None


def configured_project_root(config: dict[str, Any], fallback: str | Path | None = None) -> Path:
    value = config.get("target_project_root") or fallback or "."
    return Path(str(value)).expanduser().resolve(strict=False)


def configured_mode_cli(config: dict[str, Any], project_root: str | Path | None = None) -> Path:
    root = Path(project_root) if project_root is not None else configured_project_root(config)
    mode_cli = Path(str(config.get("mode_cli") or DEFAULT_MODE_CLI))
    if mode_cli.is_absolute():
        return mode_cli
    return (root / mode_cli).resolve(strict=False)


def short_text(value: Any, limit: int = 800) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def redact_identifier(value: Any) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    if len(text) <= 12:
        return text
    return f"{text[:6]}…{text[-4:]}"


def payload_token(payload: dict[str, Any] | None, fallback: str = "blocked:payload_not_loaded") -> str:
    if not isinstance(payload, dict):
        return fallback
    token = payload.get("token")
    if token:
        return str(token)
    return "ok" if payload.get("ok", True) else fallback


def bool_state(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"on", "true", "enabled", "enable", "yes", "1"}:
            return True
        if lowered in {"off", "false", "disabled", "disable", "no", "0"}:
            return False
    return None


def state_label(value: bool | None) -> str:
    if value is True:
        return "enabled"
    if value is False:
        return "disabled"
    return "unknown"


def action_scope_key(action: str, session_id: str | None = None) -> str:
    if action.startswith("session-"):
        return f"session:{redact_identifier(session_id)}"
    if action in READ_ACTIONS:
        return "read"
    return "project-default"


def action_label(action: str) -> str:
    return {
        "refresh": "Refresh status",
        "project-status": "Read project status",
        "list-sessions": "Read sessions",
        "status": "Read effective status",
        "project-on": "Enable project default",
        "project-off": "Disable project default",
        "session-on": "Enable selected session",
        "session-off": "Disable selected session",
    }.get(action, action)


def scope_label(scope: str, scope_key: str | None = None) -> str:
    if scope == "project-default":
        return "Project default scope"
    if scope == "session":
        return f"Selected session scope {scope_key or ''}".strip()
    if scope == "read":
        return "Read-only refresh scope"
    return scope


def same_pending_scope(action_plan: dict[str, Any], pending_scope: str | None, pending_scope_key: str | None = None) -> bool:
    if not pending_scope and not pending_scope_key:
        return False
    scope = str(action_plan.get("scope") or "")
    scope_key = str(action_plan.get("scope_key") or scope)
    if pending_scope_key:
        return pending_scope_key == scope_key
    return bool(pending_scope and pending_scope == scope)


def decorate_action_for_button(
    action_plan: dict[str, Any],
    *,
    pending_scope: str | None = None,
    pending_scope_key: str | None = None,
) -> dict[str, Any]:
    decorated = dict(action_plan)
    action = str(decorated.get("action") or "")
    disabled_by_pending = same_pending_scope(decorated, pending_scope, pending_scope_key) and bool(decorated.get("writes_state"))
    enabled = bool(decorated.get("ok")) and not disabled_by_pending
    disabled_reason = ""
    if not decorated.get("ok"):
        disabled_reason = str(decorated.get("token") or "blocked:action_plan_invalid")
    elif disabled_by_pending:
        disabled_reason = "pending_same_scope_write"
    button = {
        "label": action_label(action),
        "enabled": enabled,
        "disabled_reason": disabled_reason,
        "scope": decorated.get("scope"),
        "scope_key": decorated.get("scope_key"),
        "scope_label": scope_label(str(decorated.get("scope") or ""), decorated.get("scope_key")),
        "keyboard_shortcut": KEYBOARD_SHORTCUTS.get(action),
        "accessible_name": f"{action_label(action)}; {scope_label(str(decorated.get('scope') or ''), decorated.get('scope_key'))}",
        "high_contrast_text": f"{action_label(action)} [{decorated.get('token', 'ok')}]",
    }
    decorated["button"] = button
    decorated["enabled"] = enabled
    decorated["disabled_reason"] = disabled_reason
    return decorated


def readback_specs_for_write_action(action: str, session_id: str | None = None) -> list[tuple[str, str | None]]:
    if action not in WRITE_ACTIONS:
        return []
    specs: list[tuple[str, str | None]] = [("project-status", None), ("list-sessions", None)]
    specs.append(("status", session_id if action.startswith("session-") else None))
    return specs


def extract_project_default(project_status: dict[str, Any] | None, status_payload: dict[str, Any] | None = None) -> bool | None:
    for payload in [project_status, status_payload]:
        if not isinstance(payload, dict):
            continue
        for key in ["project_default_enabled", "project_enabled", "default_enabled", "enabled"]:
            parsed = bool_state(payload.get(key))
            if parsed is not None:
                return parsed
        project = payload.get("project")
        if isinstance(project, dict):
            for key in ["default_enabled", "enabled"]:
                parsed = bool_state(project.get(key))
                if parsed is not None:
                    return parsed
    return None


def extract_effective(status_payload: dict[str, Any] | None, project_status: dict[str, Any] | None = None) -> bool | None:
    for payload in [status_payload, project_status]:
        if not isinstance(payload, dict):
            continue
        for key in ["effective_enabled", "effective", "enabled"]:
            parsed = bool_state(payload.get(key))
            if parsed is not None:
                return parsed
        effective = payload.get("effective")
        if isinstance(effective, dict):
            parsed = bool_state(effective.get("enabled"))
            if parsed is not None:
                return parsed
    return None


def extract_branch(project_status: dict[str, Any] | None) -> str:
    if not isinstance(project_status, dict):
        return "unknown"
    git = project_status.get("git")
    if isinstance(git, dict):
        for key in ["current_branch", "branch", "name"]:
            value = git.get(key)
            if value:
                return str(value)
    for key in ["current_branch", "git_branch", "branch"]:
        value = project_status.get(key)
        if value:
            return str(value)
    return "unknown"


def build_action_plan(
    config: dict[str, Any],
    action: str,
    *,
    session_id: str | None = None,
    project_root: str | Path | None = None,
    python_executable: str | None = None,
) -> dict[str, Any]:
    if action not in ACTION_COMMANDS:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:unsupported_gui_action",
            "action": action,
            "message": "Unsupported Project MOE GUI action.",
            "argv": [],
            "shell": False,
            "writes_state": False,
        }

    if action in {"session-on", "session-off"} and not session_id:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:missing_session_id",
            "action": action,
            "message": "Selected-session action requires a session id.",
            "argv": [],
            "shell": False,
            "writes_state": False,
        }

    root = configured_project_root(config, project_root)
    mode_cli = configured_mode_cli(config, root)
    argv = [python_executable or sys.executable, str(mode_cli), *ACTION_COMMANDS[action]]
    scope = "session" if action.startswith("session-") else ("read" if action in READ_ACTIONS else "project-default")
    scope_key = action_scope_key(action, session_id)
    if action in {"session-on", "session-off"}:
        argv.extend(["--session-id", str(session_id)])
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": "ok",
        "action": action,
        "scope": scope,
        "scope_key": scope_key,
        "scope_label": scope_label(scope, scope_key),
        "project_root": str(root),
        "mode_cli": str(mode_cli),
        "argv": argv,
        "shell": False,
        "writes_state": action in WRITE_ACTIONS,
        "direct_state_write": False,
        "keyboard_shortcut": KEYBOARD_SHORTCUTS.get(action),
        "requires_readback_after_write": action in WRITE_ACTIONS,
        "readback_after_write": [
            build_action_plan(config, read_action, session_id=read_session_id, project_root=root, python_executable=python_executable)
            for read_action, read_session_id in readback_specs_for_write_action(action, session_id)
        ],
    }


def build_refresh_plan(config: dict[str, Any], *, project_root: str | Path | None = None, python_executable: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": "ok",
        "action": "refresh",
        "scope": "read",
        "shell": False,
        "writes_state": False,
        "direct_state_write": False,
        "commands": [
            build_action_plan(config, "project-status", project_root=project_root, python_executable=python_executable),
            build_action_plan(config, "list-sessions", project_root=project_root, python_executable=python_executable),
            build_action_plan(config, "status", project_root=project_root, python_executable=python_executable),
        ],
        "keyboard_shortcut": KEYBOARD_SHORTCUTS["refresh"],
    }


def build_project_default_card(
    project_status: dict[str, Any] | None,
    status_payload: dict[str, Any] | None,
    config: dict[str, Any],
    *,
    pending_scope: str | None = None,
    pending_scope_key: str | None = None,
) -> dict[str, Any]:
    project_default = extract_project_default(project_status, status_payload)
    effective = extract_effective(status_payload, project_status)
    token = payload_token(project_status, "blocked:project_status_not_loaded")
    return {
        "title": "Project default",
        "scope": "project-default",
        "agent_name": config.get("agent_name"),
        "state_namespace": config.get("state_namespace"),
        "token": token,
        "enabled": project_default,
        "label": state_label(project_default),
        "effective_enabled": effective,
        "effective_label": state_label(effective),
        "actions": {
            "enable_project_default": decorate_action_for_button(
                build_action_plan(config, "project-on"),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "disable_project_default": decorate_action_for_button(
                build_action_plan(config, "project-off"),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
        },
        "status_badge": {
            "text": state_label(project_default),
            "effective_text": state_label(effective),
            "token_text": token,
            "high_contrast_text": f"Project default: {state_label(project_default)}; effective: {state_label(effective)}; token: {token}",
        },
    }


def normalize_session_row(
    config: dict[str, Any],
    row: Any,
    index: int,
    *,
    pending_scope: str | None = None,
    pending_scope_key: str | None = None,
) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {
            "row_index": index,
            "valid": False,
            "token": "blocked:invalid_session_record",
            "message": "Session row must be a JSON object.",
            "session_id": None,
            "display_id": "(invalid session)",
            "actions": {},
        }
    session_id = row.get("session_id") or row.get("id")
    valid = bool(session_id) and row.get("valid", True) is not False
    token = str(row.get("token") or ("ok" if valid else "blocked:invalid_session_record"))
    enabled = bool_state(row.get("effective_enabled"))
    if enabled is None:
        enabled = bool_state(row.get("enabled") if "enabled" in row else row.get("status"))
    actions = {}
    if valid:
        raw_id = str(session_id)
        actions = {
            "enable_session": decorate_action_for_button(
                build_action_plan(config, "session-on", session_id=raw_id),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "disable_session": decorate_action_for_button(
                build_action_plan(config, "session-off", session_id=raw_id),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
        }
    return {
        "row_index": index,
        "valid": valid,
        "token": token,
        "message": short_text(row.get("message") or ("ok" if valid else "Invalid session record."), 240),
        "session_id": str(session_id) if session_id else None,
        "display_id": redact_identifier(session_id),
        "enabled": enabled,
        "label": state_label(enabled),
        "source": row.get("source") or row.get("effective_source") or "unknown",
        "last_seen_at": row.get("last_seen_at"),
        "actions": actions,
        "status_badge": {
            "text": state_label(enabled),
            "token_text": token,
            "high_contrast_text": f"Session {redact_identifier(session_id)}: {state_label(enabled)}; token: {token}",
        },
    }


def build_session_table(
    config: dict[str, Any],
    sessions_payload: dict[str, Any] | None,
    *,
    pending_scope: str | None = None,
    pending_scope_key: str | None = None,
) -> dict[str, Any]:
    if sessions_payload is None:
        return {
            "token": "blocked:list_sessions_not_loaded",
            "rows": [],
            "empty_state": {"is_empty": True, "message": "Session list has not been loaded."},
            "invalid_count": 0,
        }
    if not sessions_payload.get("ok", True):
        return {
            "token": payload_token(sessions_payload, "blocked:list_sessions_failed"),
            "rows": [],
            "empty_state": {"is_empty": True, "message": short_text(sessions_payload.get("message") or "Session list load failed.", 240)},
            "invalid_count": 0,
        }
    sessions = sessions_payload.get("sessions", [])
    if not isinstance(sessions, list):
        return {
            "token": "blocked:list_sessions_contract_invalid",
            "rows": [],
            "empty_state": {"is_empty": True, "message": "list-sessions --json must return a sessions array."},
            "invalid_count": 0,
        }
    rows = [
        normalize_session_row(
            config,
            row,
            index,
            pending_scope=pending_scope,
            pending_scope_key=pending_scope_key,
        )
        for index, row in enumerate(sessions)
    ]
    invalid_count = sum(1 for row in rows if not row["valid"] or row["token"] != "ok")
    return {
        "token": "ok",
        "rows": rows,
        "empty_state": {"is_empty": len(rows) == 0, "message": "No registered sessions." if not rows else ""},
        "invalid_count": invalid_count,
    }


def describe_window_structure() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "gui_shell_contract": GUI_SHELL_CONTRACT,
        "window_title": WINDOW_TITLE,
        "regions": [
            {"id": "top_banner", "purpose": "project root, branch, agent name, and state namespace"},
            {"id": "error_banner", "purpose": "stable token, short message, and redacted diagnostics"},
            {"id": "project_default_card", "purpose": "project-default effective state and explicit on/off controls"},
            {"id": "session_table", "purpose": "session effective state, invalid/empty/load-failed states, and selected-session controls"},
            {"id": "footer", "purpose": "read-only refresh status and GUI/runtime readiness"},
        ],
        "accessibility_contract": {
            "button_scope_labels_required": True,
            "status_badges_have_text": True,
            "system_theme_or_high_contrast_readable": "view_model_exposes_high_contrast_text_manual_or_qtest_visible_evidence_required",
            "keyboard_operation": "view_model_exposes_shortcuts_manual_or_qtest_visible_evidence_required",
            "write_buttons_disable_same_scope_while_pending": True,
            "write_actions_require_readback_after_write": True,
        },
        "automation_boundary": {
            "import_safe_without_pyside6": True,
            "automated_tests_do_not_show_windows": True,
            "visible_launch_requires_explicit_interactive_command": True,
        },
    }


def build_view_model(
    config: dict[str, Any],
    *,
    project_status: dict[str, Any] | None = None,
    sessions_payload: dict[str, Any] | None = None,
    status_payload: dict[str, Any] | None = None,
    pyside6_available: bool | None = None,
    pending_scope: str | None = None,
) -> dict[str, Any]:
    root = configured_project_root(config)
    pyside6_status = "import_ok" if (is_pyside6_available() if pyside6_available is None else pyside6_available) else "pyside6_unavailable"
    pending_scope_key = str(pending_scope) if pending_scope and ":" in pending_scope else None
    pending_scope_name = pending_scope.split(":", 1)[0] if pending_scope and ":" in pending_scope else pending_scope
    session_table = build_session_table(
        config,
        sessions_payload,
        pending_scope=pending_scope_name,
        pending_scope_key=pending_scope_key,
    )
    project_token = payload_token(project_status, "blocked:project_status_not_loaded")
    status_token = payload_token(status_payload, "blocked:status_not_loaded")
    table_token = session_table["token"]
    banners = []
    for token, message in [
        (project_token, "Project status is not fully available."),
        (status_token, "Effective status is not fully available."),
        (table_token, "Session list is not fully available."),
    ]:
        if token != "ok":
            banners.append({"token": token, "message": message})
    if pyside6_status != "import_ok":
        banners.append({"token": "blocked:pyside6_unavailable", "message": "PySide6 is not importable from the configured GUI runtime."})
    if session_table["invalid_count"]:
        banners.append({"token": "blocked:invalid_session_record", "message": f"{session_table['invalid_count']} session row(s) need review."})
    return {
        "schema_version": SCHEMA_VERSION,
        "gui_shell_contract": GUI_SHELL_CONTRACT,
        "window_structure": describe_window_structure(),
        "top_banner": {
            "project_root": str(root),
            "current_branch": extract_branch(project_status),
            "agent_name": config.get("agent_name"),
            "state_namespace": config.get("state_namespace"),
            "cli_contract": config.get("cli_contract"),
        },
        "project_default_card": build_project_default_card(
            project_status,
            status_payload,
            config,
            pending_scope=pending_scope_name,
            pending_scope_key=pending_scope_key,
        ),
        "session_table": session_table,
        "refresh_action": build_refresh_plan(config),
        "runtime": {
            "pyside6_status": pyside6_status,
            "shared_runtime_root": config.get("shared_runtime_root"),
            "runtime_python": config.get("runtime_python"),
        },
        "banners": banners,
        "button_state": {
            "pending_scope": pending_scope_name,
            "pending_scope_key": pending_scope_key,
            "same_scope_buttons_disabled": bool(pending_scope),
            "readback_required_after_write": True,
        },
        "keyboard_navigation": {
            "tab_order": ["refresh", "project-on", "project-off", "session-table", "session-on", "session-off"],
            "shortcuts": KEYBOARD_SHORTCUTS,
            "focus_policy": "buttons_and_session_table_are_keyboard_reachable",
        },
        "theme_accessibility": {
            "uses_system_theme": True,
            "status_not_color_only": True,
            "high_contrast_text_required": True,
            "badge_text_fields": ["text", "effective_text", "token_text", "high_contrast_text"],
        },
        "direct_state_write": False,
    }


def build_gui_preflight(
    config: dict[str, Any],
    *,
    project_status: dict[str, Any] | None = None,
    sessions_payload: dict[str, Any] | None = None,
    status_payload: dict[str, Any] | None = None,
    pyside6_available: bool | None = None,
) -> dict[str, Any]:
    view_model = build_view_model(
        config,
        project_status=project_status,
        sessions_payload=sessions_payload,
        status_payload=status_payload,
        pyside6_available=pyside6_available,
    )
    pyside6_ok = view_model["runtime"]["pyside6_status"] == "import_ok"
    blockers = [banner for banner in view_model["banners"] if banner["token"] != "ok"]
    token = "ok" if pyside6_ok and not blockers else ("blocked:pyside6_unavailable" if not pyside6_ok else blockers[0]["token"])
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": token == "ok",
        "token": token,
        "exit_code": 0 if token == "ok" else 5,
        "message": "Project MOE GUI shell preflight passed." if token == "ok" else "Project MOE GUI shell preflight found blockers.",
        "gui_shell_contract": GUI_SHELL_CONTRACT,
        "view_model": view_model,
        "blockers": blockers,
    }


def run_cli_json(
    config: dict[str, Any],
    action: str,
    *,
    session_id: str | None = None,
    timeout: int = 20,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    plan = build_action_plan(config, action, session_id=session_id)
    if not plan.get("ok"):
        return None, stable_blocker(str(plan["token"]), str(plan.get("message") or "Cannot build action plan."))
    try:
        result = subprocess.run(
            plan["argv"],
            cwd=str(configured_project_root(config)),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, stable_blocker("blocked:mode_cli_timeout", "Target project mode CLI timed out.", action=action)
    except Exception as exc:
        return None, stable_blocker("blocked:mode_cli_invocation_failed", "Cannot invoke target project mode CLI.", action=action, error=str(exc))
    if result.returncode != 0:
        return None, stable_blocker(
            "blocked:mode_cli_failed",
            "Target project mode CLI returned non-zero.",
            action=action,
            exit_code=result.returncode,
            stderr=short_text(result.stderr, 800),
        )
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        return None, stable_blocker("blocked:mode_cli_invalid_json", "Target project mode CLI did not emit JSON.", action=action, error=str(exc), stdout=short_text(result.stdout, 800))
    if not isinstance(payload, dict):
        return None, stable_blocker("blocked:mode_cli_invalid_json", "Target project mode CLI JSON must be an object.", action=action)
    return payload, None


def execute_write_action_with_readback(
    config: dict[str, Any],
    action: str,
    *,
    session_id: str | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    plan = build_action_plan(config, action, session_id=session_id)
    if not plan.get("ok"):
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": plan.get("token"),
            "action": action,
            "message": plan.get("message"),
            "write_payload": None,
            "readback": {},
            "button_state_during_command": {},
        }
    if action not in WRITE_ACTIONS:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:not_a_write_action",
            "action": action,
            "message": "Only write actions use execute_write_action_with_readback.",
            "write_payload": None,
            "readback": {},
            "button_state_during_command": {},
        }
    pending_key = str(plan.get("scope_key") or plan.get("scope") or "")
    pending_view_model = build_view_model(config, pending_scope=pending_key)
    write_payload, write_error = run_cli_json(config, action, session_id=session_id, timeout=timeout)
    write_contract_errors: list[dict[str, Any]] = []
    if write_error is None:
        write_contract_errors = validate_write_cli_payload(action, write_payload)
    readback: dict[str, Any] = {}
    readback_errors: list[dict[str, Any]] = []
    for read_plan in plan.get("readback_after_write", []):
        read_action = str(read_plan.get("action"))
        read_session_id = session_id if read_action == "status" and action.startswith("session-") else None
        payload, err = run_cli_json(config, read_action, session_id=read_session_id, timeout=timeout)
        readback[read_action] = payload
        if err:
            readback_errors.append(err)
    errors = [err for err in [write_error, *write_contract_errors, *readback_errors] if err]
    token = "ok" if not errors else str(errors[0]["code"])
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not errors,
        "token": token,
        "action": action,
        "scope": plan.get("scope"),
        "scope_key": plan.get("scope_key"),
        "message": "Write action completed and status was re-read." if not errors else "Write action or readback failed.",
        "write_payload": write_payload,
        "readback": readback,
        "readback_required": True,
        "readback_commands": [item.get("action") for item in plan.get("readback_after_write", [])],
        "errors": errors,
        "button_state_during_command": pending_view_model["button_state"],
    }


def launch_visible(view_model: dict[str, Any]) -> int:
    try:
        from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
    except Exception as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError("blocked:pyside6_unavailable") from exc

    app = QApplication.instance() or QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    central = QWidget()
    layout = QVBoxLayout(central)
    banner = view_model.get("top_banner", {})
    project_card = view_model.get("project_default_card", {})
    layout.addWidget(QLabel(f"Project: {banner.get('project_root')}"))
    layout.addWidget(QLabel(f"Branch: {banner.get('current_branch')}"))
    layout.addWidget(QLabel(f"Agent: {banner.get('agent_name')} / namespace: {banner.get('state_namespace')}"))
    layout.addWidget(QLabel(f"Project default: {project_card.get('label')} (effective: {project_card.get('effective_label')})"))
    layout.addWidget(QLabel(f"Sessions: {len(view_model.get('session_table', {}).get('rows', []))}"))
    window.setCentralWidget(central)
    window.resize(960, 540)
    window.show()
    return int(app.exec())
