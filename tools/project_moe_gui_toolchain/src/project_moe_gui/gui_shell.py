from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from project_moe_gui import CLI_CONTRACT
from project_moe_gui.qfluent_runtime import check_qfluent_runtime, qfluent_license_manifest


SCHEMA_VERSION = 1
GUI_SHELL_CONTRACT = "project-moe-gui-shell-v1"
WINDOW_TITLE = "Project MOE Agent Console"
QML_SHELL_RELATIVE = Path("qml/ProjectMoeGui.qml")
TARGET_QML_SHELL_RELATIVE = Path("tools/project_moe_gui/qml/ProjectMoeGui.qml")
DEFAULT_MODE_CLI = "tools/thesis_moe_mode.py"
READ_ACTIONS = {"refresh", "project-status", "list-sessions", "list-lenses", "status"}
WRITE_ACTIONS = {"project-on", "project-off", "session-on", "session-off", "session-set-lenses", "session-clear-lenses"}
ACTION_COMMANDS = {
    "project-status": ["project-status", "--json"],
    "list-sessions": ["list-sessions", "--json"],
    "list-lenses": ["list-lenses", "--json"],
    "status": ["status", "--json"],
    "project-on": ["project-on", "--json"],
    "project-off": ["project-off", "--json"],
    "session-on": ["on", "--json"],
    "session-off": ["off", "--json"],
    "session-set-lenses": ["set-lenses", "--json"],
    "session-clear-lenses": ["clear-lenses", "--json"],
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
    "atomic_write",
)
WRITE_CLI_LOCK_OK_STATUSES = {
    "acquired",
    "lock_acquired",
    "lock_released",
    "no_lock_required",
    "not_locked",
    "not_locked_fixture",
    "released",
}
WRITE_CLI_LOCK_BLOCKED_STATUSES = {
    "blocked",
    "lock_failed",
    "lock_timeout",
    "locked",
    "stale_lock",
    "timeout",
}
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
    "session-set-lenses": "Alt+L",
    "session-clear-lenses": "Alt+Shift+L",
}

DEFAULT_EXPERT_LENSES = [
    {
        "id": "blind_review",
        "label": "Blind-review expert",
        "description": "Checks contribution, rigor, evidence, and likely reviewer objections.",
    },
    {
        "id": "advisor_interrogation",
        "label": "Advisor interrogation expert",
        "description": "Turns vague claims into hard advisor-style questions and required answers.",
    },
    {
        "id": "aigc_risk",
        "label": "AIGC / AI-like wording risk expert",
        "description": "Flags generic wording, unsupported certainty, and suspiciously synthetic phrasing.",
    },
    {
        "id": "novelty",
        "label": "Novelty / innovation expert",
        "description": "Tests whether the claimed innovation is explicit, defensible, and differentiated.",
    },
    {
        "id": "literature_evidence",
        "label": "Literature and evidence expert",
        "description": "Checks source coverage, citation fit, evidence gaps, and over-claim risk.",
    },
    {
        "id": "structure_expression",
        "label": "Structure and expression expert",
        "description": "Reviews organization, transitions, terminology, readability, and argument flow.",
    },
    {
        "id": "socratic_cbt",
        "label": "Socratic CBT-style questioning expert",
        "description": "Uses calm Socratic questions to expose assumptions and improve revision decisions.",
    },
    {
        "id": "thinking_dispatcher",
        "label": "Thinking-model dispatcher",
        "description": "Chooses the most suitable lens combination and decomposes the review brief.",
    },
]

DEFAULT_EXPERT_CATEGORIES = [
    {
        "id": "review",
        "label": "Review",
        "description": "Reviewer, advisor, novelty, literature, and expression lenses.",
        "lens_ids": ["blind_review", "advisor_interrogation", "novelty", "literature_evidence", "structure_expression"],
    },
    {
        "id": "risk",
        "label": "Risk",
        "description": "AIGC, evidence, blocker, and risk triage lenses.",
        "lens_ids": ["aigc_risk", "literature_evidence"],
    },
    {
        "id": "thinking",
        "label": "Thinking",
        "description": "Socratic and dispatch-oriented lenses for deciding next review steps.",
        "lens_ids": ["socratic_cbt", "thinking_dispatcher"],
    },
]

HANDOFF_TARGETS = [
    {
        "id": "main-session",
        "label": "Main session",
        "description": "The current leader session uses the selected MOE lenses directly.",
    },
    {
        "id": "subagent",
        "label": "Subagent",
        "description": "The leader may paste this package into a native subagent task; GUI does not spawn it.",
    },
    {
        "id": "durable-team",
        "label": "Durable team",
        "description": "The leader may hand this package to a durable team lane; GUI does not start workers.",
    },
    {
        "id": "langgraph-workflow",
        "label": "LangGraph workflow",
        "description": "The leader may use this package as a LangGraph workflow brief; GUI does not invoke LangGraph.",
    },
]

EXPERT_TASK_TEMPLATES = [
    {
        "id": "thesis_review",
        "label": "Thesis review brief",
        "objective": "Review the provided thesis section or objective and return actionable revision advice.",
        "prompt": "Assess the target with the selected expert lens. Return strengths, risks, required fixes, and next revision steps.",
    },
    {
        "id": "defense_questions",
        "label": "Defense Q&A brief",
        "objective": "Generate likely defense or advisor questions and concise answer requirements.",
        "prompt": "Generate tough questions, explain why each matters, and list evidence needed for defensible answers.",
    },
    {
        "id": "risk_triage",
        "label": "Risk triage brief",
        "objective": "Prioritize blocking issues before spending time on style or polish.",
        "prompt": "Classify risks as blocker/high/medium/low and propose the smallest safe next step for each.",
    },
]


def close_behavior_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "default_close_action": "ask",
        "auto_hide_to_tray": False,
        "dialog_title": "Close Project MOE GUI?",
        "dialog_message": "Choose whether to exit the Project MOE GUI or keep it available in the system tray.",
        "dialog_options": [
            {"id": "exit", "label": "Exit", "effect": "quit_application"},
            {"id": "hide_to_tray", "label": "Hide to tray", "effect": "hide_window_create_tray"},
            {"id": "cancel", "label": "Cancel", "effect": "ignore_close_event"},
        ],
        "tray_icon_created_only_after_explicit_hide": True,
        "tray_menu_items": [
            {"id": "show", "label": "Show", "effect": "show_window"},
            {"id": "exit", "label": "Exit", "effect": "quit_application"},
        ],
    }


def _safe_short(value: Any, limit: int = 220) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _agent_toml_candidates(root: Path, agent_name: str | None) -> list[Path]:
    agent_dir = root / ".codex" / "agents"
    if not agent_dir.exists():
        return []
    candidates = sorted(agent_dir.glob("*.toml"))
    if not agent_name:
        return candidates
    preferred = [path for path in candidates if path.stem == agent_name]
    return preferred + [path for path in candidates if path not in preferred]


def _structured_lenses_from_public_toml(payload: dict[str, Any]) -> list[dict[str, str]]:
    lens_values: Any = None
    for container_key in ("extensions", "moe"):
        container = payload.get(container_key)
        if isinstance(container, dict):
            lens_values = container.get("expert_lenses") or container.get("lenses")
            if lens_values:
                break
    lenses: list[dict[str, str]] = []
    if isinstance(lens_values, list):
        for item in lens_values:
            if isinstance(item, dict):
                lens_id = _safe_short(item.get("id") or item.get("name") or item.get("label"), 80)
                label = _safe_short(item.get("label") or item.get("name") or lens_id, 120)
                description = _safe_short(item.get("description") or item.get("purpose") or "", 220)
            else:
                lens_id = _safe_short(item, 80)
                label = lens_id
                description = ""
            if not lens_id or not label:
                continue
            lenses.append({"id": lens_id, "label": label, "description": description})
    return lenses


def default_lens_categories(lenses: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    known_lens_ids = {str(item.get("id")) for item in (lenses or DEFAULT_EXPERT_LENSES) if item.get("id")}
    categories: list[dict[str, Any]] = []
    for category in DEFAULT_EXPERT_CATEGORIES:
        lens_ids = [lens_id for lens_id in category.get("lens_ids", []) if lens_id in known_lens_ids]
        categories.append({**category, "lens_ids": lens_ids})
    return categories


def _structured_categories_from_public_toml(payload: dict[str, Any], lenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_values: Any = None
    for container_key in ("extensions", "moe"):
        container = payload.get(container_key)
        if isinstance(container, dict):
            category_values = container.get("expert_categories") or container.get("categories")
            if category_values:
                break
    categories: list[dict[str, Any]] = []
    if isinstance(category_values, list):
        for item in category_values:
            if isinstance(item, dict):
                category_id = _safe_short(item.get("id") or item.get("name") or item.get("label"), 80)
                label = _safe_short(item.get("label") or item.get("name") or category_id, 120)
                description = _safe_short(item.get("description") or item.get("purpose") or "", 220)
                lens_ids = [str(value) for value in item.get("lens_ids", []) if isinstance(value, str)]
            else:
                category_id = _safe_short(item, 80)
                label = category_id
                description = ""
                lens_ids = []
            if not category_id or not label:
                continue
            categories.append({"id": category_id, "label": label, "description": description, "lens_ids": lens_ids})
    return categories or default_lens_categories(lenses)


def load_public_expert_lenses(root: Path, agent_name: str | None) -> dict[str, Any]:
    source = {
        "type": "safe_default",
        "agent_toml_checked": False,
        "agent_toml_path": None,
        "private_prompt_source_read": False,
        "developer_instructions_copied": False,
    }
    if tomllib is None:
        lenses = list(DEFAULT_EXPERT_LENSES)
        return {"lenses": lenses, "categories": default_lens_categories(lenses), "source": {**source, "token": "blocked:tomllib_unavailable"}}
    for path in _agent_toml_candidates(root, agent_name):
        try:
            payload = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        observed_name = str(payload.get("name") or path.stem)
        if agent_name and observed_name != agent_name and path.stem != agent_name:
            continue
        structured_lenses = _structured_lenses_from_public_toml(payload)
        lenses = structured_lenses or list(DEFAULT_EXPERT_LENSES)
        categories = _structured_categories_from_public_toml(payload, lenses)
        source.update(
            {
                "type": "public_agent_toml" if structured_lenses else "public_agent_toml_with_safe_default_lenses",
                "token": "ok",
                "agent_toml_checked": True,
                "agent_toml_path": norm(path.relative_to(root)) if root in path.parents else str(path),
                "agent_name": observed_name,
                "agent_description": _safe_short(payload.get("description"), 220),
                "private_prompt_source_read": False,
                "developer_instructions_copied": False,
            }
        )
        return {"lenses": lenses, "categories": categories, "source": source}
    lenses = list(DEFAULT_EXPERT_LENSES)
    return {"lenses": lenses, "categories": default_lens_categories(lenses), "source": {**source, "token": "ok"}}


def normalize_lens_catalog(lenses_payload: dict[str, Any] | None, fallback_lenses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if isinstance(lenses_payload, dict) and lenses_payload.get("ok", True):
        raw_lenses = lenses_payload.get("lenses")
        raw_categories = lenses_payload.get("categories")
        lenses = [item for item in raw_lenses if isinstance(item, dict) and item.get("id")] if isinstance(raw_lenses, list) else []
        categories = [item for item in raw_categories if isinstance(item, dict) and item.get("id")] if isinstance(raw_categories, list) else []
        if lenses:
            return {
                "schema_version": SCHEMA_VERSION,
                "token": payload_token(lenses_payload, "ok"),
                "source": "phase1-cli-list-lenses",
                "lenses": lenses,
                "categories": categories or default_lens_categories(lenses),
                "selection_semantics": lenses_payload.get("selection_semantics")
                if isinstance(lenses_payload.get("selection_semantics"), dict)
                else {"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"},
                "private_prompt_source_read": bool(lenses_payload.get("private_prompt_source_read", False)),
            }
    lenses = list(fallback_lenses or DEFAULT_EXPERT_LENSES)
    return {
        "schema_version": SCHEMA_VERSION,
        "token": "ok",
        "source": "safe-default",
        "lenses": lenses,
        "categories": default_lens_categories(lenses),
        "selection_semantics": {"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"},
        "private_prompt_source_read": False,
    }


def generate_expert_handoff_package_preview(
    config: dict[str, Any],
    lenses: list[dict[str, Any]],
    templates: list[dict[str, Any]],
    handoff_targets: list[dict[str, Any]],
) -> str:
    selected_lenses = lenses[:2] if len(lenses) > 1 else (lenses or [DEFAULT_EXPERT_LENSES[0]])
    template = templates[0] if templates else EXPERT_TASK_TEMPLATES[0]
    target = handoff_targets[0] if handoff_targets else HANDOFF_TARGETS[0]
    lens_lines = [f"- {item.get('id')}: {item.get('label')}" for item in selected_lenses]
    return "\n".join(
        [
            "Project MOE Expert Workbench v2 Handoff Package (draft only; no GUI execution)",
            f"Project: {config.get('runtime_project_root') or config.get('target_project_root') or '<target-project>'}",
            f"Agent: {config.get('agent_name') or '<agent>'}",
            f"State namespace: {config.get('state_namespace') or '<namespace>'}",
            f"Handoff target: {target.get('id')} ({target.get('label')})",
            "Selected MOE lenses:",
            *lens_lines,
            f"Task template: {template.get('label')}",
            "",
            "Review target / objective:",
            "<paste target text, file path, or revision objective here>",
            "",
            "Instructions:",
            str(template.get("prompt") or ""),
            "",
            "Carrier instructions:",
            "- The GUI generated this package only; it did not start Codex, subagents, durable team, LangGraph, or model APIs.",
            "- Main session may use one or more selected MOE lenses directly, paste this package to a native subagent, or hand it to a durable team / LangGraph workflow.",
            "",
            "Output format:",
            "1. Key finding",
            "2. Evidence or missing evidence",
            "3. Recommended revision",
            "4. Follow-up question",
        ]
    )


def build_expert_workbench(config: dict[str, Any], root: Path, lens_catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    lens_payload = load_public_expert_lenses(root, str(config.get("agent_name") or ""))
    if isinstance(lens_catalog, dict) and lens_catalog.get("source") == "phase1-cli-list-lenses":
        catalog = lens_catalog
        lenses = list(catalog.get("lenses") or lens_payload.get("lenses") or DEFAULT_EXPERT_LENSES)
        categories = list(catalog.get("categories") or lens_payload.get("categories") or default_lens_categories(lenses))
    else:
        lenses = list(lens_payload.get("lenses") or DEFAULT_EXPERT_LENSES)
        categories = list(lens_payload.get("categories") or default_lens_categories(lenses))
        catalog = {
            "schema_version": SCHEMA_VERSION,
            "token": "ok",
            "source": (lens_payload.get("source") or {}).get("type") or "safe-default",
            "lenses": lenses,
            "categories": categories,
            "selection_semantics": {"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"},
            "private_prompt_source_read": False,
        }
    templates = list(EXPERT_TASK_TEMPLATES)
    handoff_targets = list(HANDOFF_TARGETS)
    package_preview = generate_expert_handoff_package_preview(config, lenses, templates, handoff_targets)
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "handoff_package_generation_only",
        "title": "Expert Workbench v2",
        "subtitle": "Generate a safe Project MOE handoff package without starting Codex, subagents, durable teams, LangGraph, or model APIs.",
        "lenses": lenses,
        "categories": categories,
        "task_templates": templates,
        "handoff_targets": handoff_targets,
        "default_lens_id": lenses[0]["id"] if lenses else None,
        "default_template_id": templates[0]["id"] if templates else None,
        "default_handoff_target_id": handoff_targets[0]["id"] if handoff_targets else None,
        "brief_preview": package_preview,
        "handoff_package_preview": package_preview,
        "copy_action": {
            "id": "copy_handoff_package_to_clipboard",
            "label": "Copy handoff package",
            "persistence": "clipboard_only",
            "writes_git": False,
            "writes_disk": False,
        },
        "execution_policy": {
            "starts_codex": False,
            "starts_subagents": False,
            "starts_durable_team": False,
            "starts_langgraph_workflow": False,
            "calls_model_api": False,
            "writes_target_project_state": False,
            "gui_direct_state_write": False,
        },
        "handoff_policy": {
            "targets_are_metadata_only": True,
            "main_session_can_use_lenses_directly": True,
            "main_session_can_send_to_subagent": True,
            "main_session_can_send_to_durable_team": True,
            "main_session_can_send_to_langgraph_workflow": True,
            "gui_executes_handoff_target": False,
        },
        "persistence_policy": {
            "runtime_memory": True,
            "clipboard": True,
            "disk_default": False,
            "git_default": False,
        },
        "privacy_boundary": {
            "private_prompt_source_read": False,
            "private_prompt_body_copied": False,
            "developer_instructions_copied": False,
            "raw_session_id_exposed": False,
            "full_stdout_stderr_copied": False,
            "source": lens_payload.get("source"),
            "lens_catalog_source": catalog.get("source"),
        },
    }


def _configured_qml_shell_relative(config: dict[str, Any] | None) -> Path | None:
    if not isinstance(config, dict):
        return None
    qml_shell = config.get("qml_shell")
    value: Any = None
    if isinstance(qml_shell, dict):
        value = qml_shell.get("relative_path")
    value = value or config.get("qml_shell_relative_path")
    if not value:
        return None
    rel = Path(str(value).strip())
    if rel.is_absolute():
        return None
    return rel


def qml_shell_path(
    config: dict[str, Any] | None = None,
    project_root: str | Path | None = None,
    *,
    prefer_installed: bool = True,
) -> Path:
    if prefer_installed and isinstance(config, dict):
        root = configured_project_root(config, project_root)
        configured_rel = _configured_qml_shell_relative(config)
        if configured_rel is not None:
            return (root / configured_rel).resolve(strict=False)
        target_path = (root / TARGET_QML_SHELL_RELATIVE).resolve(strict=False)
        if project_root is not None and target_path.exists():
            return target_path
    return Path(__file__).resolve().parent / QML_SHELL_RELATIVE


def qml_visual_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "library": "Qt Quick/QML",
        "runtime_modules": ["PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickControls2"],
        "style": "Material",
        "theme_modes": ["system", "light", "dark"],
        "source": str(QML_SHELL_RELATIVE).replace("\\", "/"),
        "default_target_relative_path": str(TARGET_QML_SHELL_RELATIVE).replace("\\", "/"),
        "license_family": "Qt/PySide6 runtime license",
        "external_template_copied": False,
        "reference_policy": "Official Qt Quick Controls patterns may be referenced; third-party templates require separate license review before copying.",
    }


def expected_cli_command_for_action(action: str) -> str:
    if action == "session-on":
        return "on"
    if action == "session-off":
        return "off"
    if action == "session-set-lenses":
        return "set-lenses"
    if action == "session-clear-lenses":
        return "clear-lenses"
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
    if not isinstance(payload.get("atomic_write"), bool):
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command atomic_write must be a boolean.",
                action=action,
            )
        )
    elif payload.get("atomic_write") is not True:
        errors.append(
            stable_blocker(
                "blocked:write_cli_atomic_write_required",
                "Write command must report atomic_write=true before the GUI accepts state changes.",
                action=action,
            )
        )
    lock_status = str(payload.get("lock_status") or "").strip().lower()
    if lock_status in WRITE_CLI_LOCK_BLOCKED_STATUSES or "stale" in lock_status or "timeout" in lock_status:
        errors.append(
            stable_blocker(
                "blocked:write_cli_lock_not_clean",
                "Write command lock_status reports a lock blocker and must fail closed.",
                action=action,
                lock_status=payload.get("lock_status"),
            )
        )
    elif lock_status not in WRITE_CLI_LOCK_OK_STATUSES:
        errors.append(
            stable_blocker(
                "blocked:write_cli_contract_invalid",
                "Write command lock_status must be a known safe state.",
                action=action,
                observed=payload.get("lock_status"),
                supported=sorted(WRITE_CLI_LOCK_OK_STATUSES),
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
    value = config.get("runtime_project_root") or fallback or config.get("target_project_root") or "."
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


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item).strip()]


def lens_mode_for_selection(selected_lenses: list[str], selected_categories: list[str], observed: Any = None) -> str:
    if observed in {"all", "selected"}:
        return str(observed)
    return "selected" if selected_lenses or selected_categories else "all"


def lens_selection_summary(selected_lenses: list[str], selected_categories: list[str], mode: str) -> str:
    if mode == "all" and not selected_lenses and not selected_categories:
        return "All lenses"
    parts: list[str] = []
    if selected_lenses:
        parts.append("lenses=" + ", ".join(selected_lenses))
    if selected_categories:
        parts.append("categories=" + ", ".join(selected_categories))
    return "; ".join(parts) if parts else mode


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
        "list-lenses": "Read MOE lenses",
        "status": "Read effective status",
        "project-on": "Enable project default",
        "project-off": "Disable project default",
        "session-on": "Enable selected session",
        "session-off": "Disable selected session",
        "session-set-lenses": "Apply session lenses",
        "session-clear-lenses": "Clear session lenses",
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
    if action in {"session-set-lenses", "session-clear-lenses"}:
        specs.append(("list-lenses", None))
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
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
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

    if action.startswith("session-") and not session_id:
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
    if action.startswith("session-") or (action == "status" and session_id):
        argv.extend(["--session-id", str(session_id)])
    if action in {"session-on", "session-set-lenses"}:
        for lens_id in selected_lenses or []:
            argv.extend(["--lens", str(lens_id)])
        for category_id in selected_categories or []:
            argv.extend(["--category", str(category_id)])
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
        "selected_lenses": list(selected_lenses or []),
        "selected_categories": list(selected_categories or []),
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
            build_action_plan(config, "list-lenses", project_root=project_root, python_executable=python_executable),
            build_action_plan(config, "status", project_root=project_root, python_executable=python_executable),
        ],
        "keyboard_shortcut": KEYBOARD_SHORTCUTS["refresh"],
    }


def build_project_default_card(
    project_status: dict[str, Any] | None,
    status_payload: dict[str, Any] | None,
    config: dict[str, Any],
    *,
    project_root: str | Path | None = None,
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
                build_action_plan(config, "project-on", project_root=project_root),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "disable_project_default": decorate_action_for_button(
                build_action_plan(config, "project-off", project_root=project_root),
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
    project_root: str | Path | None = None,
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
    selected_lenses = string_list(row.get("selected_lenses"))
    selected_categories = string_list(row.get("selected_categories"))
    effective_lens_mode = lens_mode_for_selection(selected_lenses, selected_categories, row.get("effective_lens_mode"))
    lens_selection_scope = str(row.get("lens_selection_scope") or "session")
    actions = {}
    if valid:
        raw_id = str(session_id)
        actions = {
            "enable_session": decorate_action_for_button(
                build_action_plan(config, "session-on", session_id=raw_id, project_root=project_root),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "disable_session": decorate_action_for_button(
                build_action_plan(config, "session-off", session_id=raw_id, project_root=project_root),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "apply_session_lenses": decorate_action_for_button(
                build_action_plan(
                    config,
                    "session-set-lenses",
                    session_id=raw_id,
                    selected_lenses=selected_lenses,
                    selected_categories=selected_categories,
                    project_root=project_root,
                ),
                pending_scope=pending_scope,
                pending_scope_key=pending_scope_key,
            ),
            "clear_session_lenses": decorate_action_for_button(
                build_action_plan(config, "session-clear-lenses", session_id=raw_id, project_root=project_root),
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
        "selected_lenses": selected_lenses,
        "selected_categories": selected_categories,
        "effective_lens_mode": effective_lens_mode,
        "lens_selection_scope": lens_selection_scope,
        "lens_selection_summary": lens_selection_summary(selected_lenses, selected_categories, effective_lens_mode),
        "last_seen_at": row.get("last_seen_at"),
        "actions": actions,
        "status_badge": {
            "text": state_label(enabled),
            "token_text": token,
            "lens_text": lens_selection_summary(selected_lenses, selected_categories, effective_lens_mode),
            "high_contrast_text": f"Session {redact_identifier(session_id)}: {state_label(enabled)}; lenses: {lens_selection_summary(selected_lenses, selected_categories, effective_lens_mode)}; token: {token}",
        },
    }


def build_session_table(
    config: dict[str, Any],
    sessions_payload: dict[str, Any] | None,
    *,
    project_root: str | Path | None = None,
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
            project_root=project_root,
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
            {"id": "navigation_sidebar", "purpose": "primary navigation between overview, sessions, diagnostics, and settings"},
            {"id": "top_banner", "purpose": "project root, branch, agent name, and state namespace"},
            {"id": "error_banner", "purpose": "stable token, short message, and redacted diagnostics"},
            {"id": "status_overview_cards", "purpose": "Qt Quick Material cards for project status, effective state, runtime, and visual shell status"},
            {"id": "project_default_card", "purpose": "project-default effective state and explicit on/off controls"},
            {"id": "session_table", "purpose": "session effective state, invalid/empty/load-failed states, and selected-session controls"},
            {"id": "expert_workbench", "purpose": "brief-only MOE expert lens selection, task-template drafting, runtime preview, and clipboard copy"},
            {"id": "diagnostics_card", "purpose": "readiness blockers, Qt Quick/QML shell status, optional QFluent legacy dependency status, and suggested next actions"},
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
        "visual_contract": {
            **qml_visual_contract(),
            "qfluentwidgets_required": False,
            "qfluentwidgets_legacy_optional": True,
        },
    }


def build_view_model(
    config: dict[str, Any],
    *,
    project_status: dict[str, Any] | None = None,
    sessions_payload: dict[str, Any] | None = None,
    lenses_payload: dict[str, Any] | None = None,
    status_payload: dict[str, Any] | None = None,
    pyside6_available: bool | None = None,
    qfluent_status: dict[str, Any] | None = None,
    pending_scope: str | None = None,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    root = configured_project_root(config, project_root)
    pyside6_status = "import_ok" if (is_pyside6_available() if pyside6_available is None else pyside6_available) else "pyside6_unavailable"
    if qfluent_status is None:
        qfluent_status = check_qfluent_runtime() if pyside6_status == "import_ok" else {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:qfluentwidgets_not_checked",
            "import_status": "not_checked",
            "license_manifest": qfluent_license_manifest(),
            "blockers": [],
        }
    pending_scope_key = str(pending_scope) if pending_scope and ":" in pending_scope else None
    pending_scope_name = pending_scope.split(":", 1)[0] if pending_scope and ":" in pending_scope else pending_scope
    session_table = build_session_table(
        config,
        sessions_payload,
        project_root=root,
        pending_scope=pending_scope_name,
        pending_scope_key=pending_scope_key,
    )
    lens_catalog = normalize_lens_catalog(lenses_payload)
    project_token = payload_token(project_status, "blocked:project_status_not_loaded")
    status_token = payload_token(status_payload, "blocked:status_not_loaded")
    table_token = session_table["token"]
    lenses_token = str(lens_catalog.get("token") or "ok")
    banners = []
    for token, message in [
        (project_token, "Project status is not fully available."),
        (status_token, "Effective status is not fully available."),
        (table_token, "Session list is not fully available."),
        (lenses_token, "MOE lens catalogue is not fully available."),
    ]:
        if token != "ok":
            banners.append({"token": token, "message": message})
    if pyside6_status != "import_ok":
        banners.append({"token": "blocked:pyside6_unavailable", "message": "PySide6 is not importable from the configured GUI runtime."})
    qml_path = qml_shell_path(config, root)
    central_qml_path = qml_shell_path(prefer_installed=False)
    qml_source_status = {
        "schema_version": SCHEMA_VERSION,
        "ok": qml_path.exists(),
        "token": "ok" if qml_path.exists() else "blocked:qml_shell_source_missing",
        "path": str(qml_path),
        "central_fallback_path": str(central_qml_path),
        "source": "target_project" if root in qml_path.parents else "central_toolchain",
    }
    if not qml_source_status["ok"]:
        banners.append({"token": "blocked:qml_shell_source_missing", "message": "Qt Quick/QML GUI shell source is missing from the installed target project and central fallback path."})
    if session_table["invalid_count"]:
        banners.append({"token": "blocked:invalid_session_record", "message": f"{session_table['invalid_count']} session row(s) need review."})
    project_default = extract_project_default(project_status, status_payload)
    effective = extract_effective(status_payload, project_status)
    session_rows = session_table.get("rows", [])
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
        "navigation_sidebar": {
            "items": [
                {"id": "overview", "label": "Project", "icon": "Home", "target_region": "status_overview_cards"},
                {"id": "sessions", "label": "Sessions", "icon": "People", "target_region": "session_table"},
                {"id": "workbench", "label": "Expert Workbench", "icon": "Edit", "target_region": "expert_workbench"},
                {"id": "diagnostics", "label": "Diagnostics", "icon": "Info", "target_region": "diagnostics_card"},
                {"id": "settings", "label": "Settings", "icon": "Setting", "target_region": "footer"},
            ]
        },
        "status_cards": [
            {
                "id": "project-default",
                "title": "Project default",
                "value": state_label(project_default),
                "token": project_token,
                "style": "fluent-card",
            },
            {
                "id": "effective-status",
                "title": "Effective status",
                "value": state_label(effective),
                "token": status_token,
                "style": "fluent-card",
            },
            {
                "id": "session-count",
                "title": "Sessions",
                "value": str(len(session_rows)),
                "token": table_token,
                "style": "fluent-card",
            },
            {
                "id": "runtime",
                "title": "GUI runtime",
                "value": pyside6_status,
                "token": "ok" if pyside6_status == "import_ok" else "blocked:pyside6_unavailable",
                "style": "qml-material-card",
            },
            {
                "id": "visual-shell",
                "title": "Visual shell",
                "value": "Qt Quick/QML",
                "token": str(qml_source_status["token"]),
                "style": "qml-material-card",
            },
        ],
        "project_default_card": build_project_default_card(
            project_status,
            status_payload,
            config,
            project_root=root,
            pending_scope=pending_scope_name,
            pending_scope_key=pending_scope_key,
        ),
        "session_table": session_table,
        "lens_catalog": lens_catalog,
        "session_lens_panel": {
            "schema_version": SCHEMA_VERSION,
            "scope": "session",
            "title": "Session MOE lenses",
            "selected_row_index": 0 if session_rows else None,
            "selected_row_source": "qml-selected-row",
            "empty_selection_means": "all",
            "lenses": lens_catalog.get("lenses", []),
            "categories": lens_catalog.get("categories", []),
            "selection_semantics": lens_catalog.get("selection_semantics"),
            "actions": {
                "apply": {
                    "action": "session-set-lenses",
                    "requires_selected_session": True,
                    "writes_state": True,
                    "direct_state_write": False,
                    "requires_readback_after_write": True,
                },
                "clear": {
                    "action": "session-clear-lenses",
                    "requires_selected_session": True,
                    "writes_state": True,
                    "direct_state_write": False,
                    "requires_readback_after_write": True,
                },
            },
        },
        "expert_workbench": build_expert_workbench(config, root, lens_catalog),
        "refresh_action": build_refresh_plan(config, project_root=root),
        "runtime": {
            "pyside6_status": pyside6_status,
            "shared_runtime_root": config.get("shared_runtime_root"),
            "runtime_python": config.get("runtime_python"),
        },
        "visual": {
            **qml_visual_contract(),
            "qml_source_status": qml_source_status,
            "primary_shell": "qml",
            "legacy_qfluent": {
                "library": "QFluentWidgets",
                "package_name": "PySide6-Fluent-Widgets",
                "import_name": "qfluentwidgets",
                "qfluentwidgets_status": qfluent_status,
                "license_manifest": qfluent_status.get("license_manifest") or qfluent_license_manifest(),
                "fail_closed_if_missing": False,
                "status": "optional_legacy_visual_surface",
            },
        },
        "diagnostics_card": {
            "title": "Diagnostics",
            "blockers": banners,
            "qml": qml_source_status,
            "qfluentwidgets": qfluent_status,
            "suggested_next_actions": [
                "Use --preflight --json for automation.",
                "Provision shared PySide6 Qt Quick runtime dependencies before visible GUI launch.",
                "Use the Qt Quick/QML shell as the primary visual surface.",
                "Review optional QFluentWidgets license only before re-enabling or redistributing the legacy QWidget visual surface.",
            ],
        },
        "banners": banners,
        "button_state": {
            "pending_scope": pending_scope_name,
            "pending_scope_key": pending_scope_key,
            "same_scope_buttons_disabled": bool(pending_scope),
            "readback_required_after_write": True,
        },
        "keyboard_navigation": {
            "tab_order": ["refresh", "project-on", "project-off", "session-table", "session-on", "session-off", "session-lenses", "expert-workbench", "copy-handoff-package"],
            "shortcuts": KEYBOARD_SHORTCUTS,
            "focus_policy": "buttons_and_session_table_are_keyboard_reachable",
        },
        "theme_accessibility": {
            "uses_system_theme": True,
            "status_not_color_only": True,
            "high_contrast_text_required": True,
            "badge_text_fields": ["text", "effective_text", "token_text", "high_contrast_text"],
        },
        "close_behavior": close_behavior_contract(),
        "direct_state_write": False,
    }


def build_gui_preflight(
    config: dict[str, Any],
    *,
    project_status: dict[str, Any] | None = None,
    sessions_payload: dict[str, Any] | None = None,
    lenses_payload: dict[str, Any] | None = None,
    status_payload: dict[str, Any] | None = None,
    pyside6_available: bool | None = None,
    qfluent_status: dict[str, Any] | None = None,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    view_model = build_view_model(
        config,
        project_root=project_root,
        project_status=project_status,
        sessions_payload=sessions_payload,
        lenses_payload=lenses_payload,
        status_payload=status_payload,
        pyside6_available=pyside6_available,
        qfluent_status=qfluent_status,
    )
    pyside6_ok = view_model["runtime"]["pyside6_status"] == "import_ok"
    qml_ok = view_model["visual"]["qml_source_status"].get("token") == "ok"
    blockers = [banner for banner in view_model["banners"] if banner["token"] != "ok"]
    token = "ok" if pyside6_ok and qml_ok and not blockers else ("blocked:pyside6_unavailable" if not pyside6_ok else blockers[0]["token"])
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
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    timeout: int = 20,
    project_root: str | Path | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    plan = build_action_plan(
        config,
        action,
        session_id=session_id,
        selected_lenses=selected_lenses,
        selected_categories=selected_categories,
        project_root=project_root,
    )
    if not plan.get("ok"):
        return None, stable_blocker(str(plan["token"]), str(plan.get("message") or "Cannot build action plan."))
    try:
        result = subprocess.run(
            plan["argv"],
            cwd=str(configured_project_root(config, project_root)),
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
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    timeout: int = 20,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    root = configured_project_root(config, project_root)
    plan = build_action_plan(
        config,
        action,
        session_id=session_id,
        selected_lenses=selected_lenses,
        selected_categories=selected_categories,
        project_root=root,
    )
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
    pending_view_model = build_view_model(config, pending_scope=pending_key, project_root=root)
    write_payload, write_error = run_cli_json(
        config,
        action,
        session_id=session_id,
        selected_lenses=selected_lenses,
        selected_categories=selected_categories,
        timeout=timeout,
        project_root=root,
    )
    write_contract_errors: list[dict[str, Any]] = []
    if write_error is None:
        write_contract_errors = validate_write_cli_payload(action, write_payload)
    readback: dict[str, Any] = {}
    readback_errors: list[dict[str, Any]] = []
    for read_plan in plan.get("readback_after_write", []):
        read_action = str(read_plan.get("action"))
        read_session_id = session_id if read_action == "status" and action.startswith("session-") else None
        payload, err = run_cli_json(config, read_action, session_id=read_session_id, timeout=timeout, project_root=root)
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


def parse_json_string_list(text: str | None) -> list[str]:
    if not text:
        return []
    try:
        payload = json.loads(text)
    except Exception:
        return []
    return string_list(payload)


def build_runtime_view_model(config: dict[str, Any], *, project_root: str | Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = configured_project_root(config, project_root)
    read_payloads: dict[str, dict[str, Any] | None] = {}
    read_errors: list[dict[str, Any]] = []
    for action in ["project-status", "list-sessions", "list-lenses", "status"]:
        payload, error = run_cli_json(config, action, project_root=root)
        read_payloads[action] = payload
        if error:
            read_errors.append(error)
    qfluent_status = check_qfluent_runtime() if is_pyside6_available() else {
        "schema_version": SCHEMA_VERSION,
        "ok": False,
        "token": "blocked:qfluentwidgets_not_checked",
        "import_status": "not_checked",
        "license_manifest": qfluent_license_manifest(),
        "blockers": [],
    }
    refreshed = build_view_model(
        config,
        project_root=root,
        project_status=read_payloads.get("project-status"),
        sessions_payload=read_payloads.get("list-sessions"),
        lenses_payload=read_payloads.get("list-lenses"),
        status_payload=read_payloads.get("status"),
        qfluent_status=qfluent_status,
    )
    if read_errors:
        refreshed.setdefault("banners", []).extend(read_errors)
        diagnostics = refreshed.setdefault("diagnostics_card", {})
        diagnostics["blockers"] = refreshed.get("banners", [])
    return refreshed, read_errors


def launch_visible(view_model: dict[str, Any], config: dict[str, Any] | None = None, project_root: str | Path | None = None) -> int:
    try:
        from PySide6.QtCore import QEvent, QObject, QTimer, QUrl, Slot
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtQuickControls2 import QQuickStyle
        from PySide6.QtWidgets import QApplication, QMessageBox, QStyle, QSystemTrayIcon
    except Exception as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError("blocked:qt_quick_qml_unavailable") from exc

    visual = view_model.get("visual") if isinstance(view_model, dict) else None
    qml_status = visual.get("qml_source_status") if isinstance(visual, dict) else None
    qml_path = Path(str(qml_status.get("path"))) if isinstance(qml_status, dict) and qml_status.get("path") else qml_shell_path()
    if not qml_path.exists():  # pragma: no cover - defensive visible path
        raise RuntimeError("blocked:qml_shell_source_missing")

    runtime_config = dict(config or {})
    if not runtime_config:
        banner = view_model.get("top_banner") if isinstance(view_model, dict) else {}
        if isinstance(banner, dict):
            runtime_config = {
                "runtime_project_root": banner.get("project_root"),
                "agent_name": banner.get("agent_name"),
                "state_namespace": banner.get("state_namespace"),
                "mode_cli": DEFAULT_MODE_CLI,
            }
    runtime_root = configured_project_root(runtime_config, project_root)

    class ProjectMoeBridge(QObject):  # pragma: no cover - visible GUI path
        def __init__(self, runtime_config: dict[str, Any], runtime_root: Path) -> None:
            super().__init__()
            self._config = dict(runtime_config)
            self._root = runtime_root

        def _with_refreshed_model(self, payload: dict[str, Any]) -> str:
            refreshed, read_errors = build_runtime_view_model(self._config, project_root=self._root)
            result = dict(payload)
            result["view_model"] = refreshed
            result["view_model_json"] = json.dumps(refreshed, ensure_ascii=False)
            if read_errors and result.get("ok"):
                result["ok"] = False
                result["token"] = read_errors[0].get("code") or read_errors[0].get("token") or "blocked:readback_failed"
                result["errors"] = [*list(result.get("errors") or []), *read_errors]
            return json.dumps(result, ensure_ascii=False)

        @Slot(result=str)
        def refreshViewModel(self) -> str:
            return self._with_refreshed_model(
                {
                    "schema_version": SCHEMA_VERSION,
                    "ok": True,
                    "token": "ok",
                    "action": "refresh",
                    "message": "View model refreshed from the target Phase 1 CLI.",
                }
            )

        @Slot(str, str, str, str, result=str)
        def executeWriteAction(self, action: str, session_id: str, selected_lenses_json: str, selected_categories_json: str) -> str:
            selected_lenses = parse_json_string_list(selected_lenses_json)
            selected_categories = parse_json_string_list(selected_categories_json)
            try:
                payload = execute_write_action_with_readback(
                    self._config,
                    str(action),
                    session_id=str(session_id or "") or None,
                    selected_lenses=selected_lenses,
                    selected_categories=selected_categories,
                    project_root=self._root,
                )
            except Exception as exc:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "ok": False,
                    "token": "blocked:gui_write_action_failed",
                    "action": str(action),
                    "message": "GUI write action failed before readback.",
                    "errors": [{"code": "blocked:gui_write_action_failed", "message": str(exc)}],
                }
            return self._with_refreshed_model(payload)

    class CloseEventFilter(QObject):  # pragma: no cover - visible GUI path
        def __init__(self, window: object, app: QApplication) -> None:
            super().__init__()
            self._window = window
            self._app = app
            self._tray: QSystemTrayIcon | None = None

        def eventFilter(self, watched: object, event: object) -> bool:
            if getattr(event, "type", lambda: None)() != QEvent.Type.Close:
                return False
            box = QMessageBox()
            box.setWindowTitle("Close Project MOE GUI?")
            box.setText("Choose whether to exit the Project MOE GUI or keep it available in the system tray.")
            exit_button = box.addButton("Exit", QMessageBox.ButtonRole.AcceptRole)
            hide_button = box.addButton("Hide to tray", QMessageBox.ButtonRole.ActionRole)
            box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            box.exec()
            clicked = box.clickedButton()
            if clicked is exit_button:
                return False
            elif clicked is hide_button:
                if hasattr(self._window, "hide"):
                    self._window.hide()
                if QSystemTrayIcon.isSystemTrayAvailable() and self._tray is None:
                    icon = self._app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
                    self._tray = QSystemTrayIcon(icon, self)
                    self._tray.setToolTip(WINDOW_TITLE)
                    self._tray.activated.connect(lambda *_: self._window.showNormal() if hasattr(self._window, "showNormal") else None)
                    self._tray.show()
                if hasattr(event, "ignore"):
                    event.ignore()
                return True
            else:
                if hasattr(event, "ignore"):
                    event.ignore()
                return True

    QQuickStyle.setStyle("Material")
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    bridge = ProjectMoeBridge(runtime_config, runtime_root)
    engine.rootContext().setContextProperty("viewModelJson", json.dumps(view_model, ensure_ascii=False))
    engine.rootContext().setContextProperty("projectMoeBridge", bridge)
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError("blocked:qml_shell_load_failed")
    window = engine.rootObjects()[0]
    close_filter = CloseEventFilter(window, app)
    window.installEventFilter(close_filter)
    window._project_moe_gui_close_filter = close_filter  # type: ignore[attr-defined]
    engine._project_moe_gui_window = window  # type: ignore[attr-defined]
    engine._project_moe_gui_bridge = bridge  # type: ignore[attr-defined]
    smoke_exit_ms = int(os.environ.get("PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS") or "0")
    if smoke_exit_ms > 0:
        smoke_timer = QTimer(window)
        smoke_timer.setSingleShot(True)
        smoke_timer.timeout.connect(lambda: app.exit(0))
        window._project_moe_gui_smoke_timer = smoke_timer  # type: ignore[attr-defined]
        smoke_timer.start(smoke_exit_ms)
    return int(app.exec())
