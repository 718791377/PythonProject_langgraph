from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from project_moe_gui import CLI_CONTRACT, TOOLCHAIN_VERSION
from project_moe_gui.qfluent_runtime import check_qfluent_runtime, qfluent_license_manifest
from project_moe_gui.workbench_artifacts import (
    create_handoff_package,
    export_handoff_package,
    list_handoff_artifacts,
    save_handoff_artifact,
)


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

THINKING_MODEL_LENS_IDS = [
    "feynman_learning",
    "first_principles",
    "pyramid_principle",
    "swot_analysis",
    "decision_tree",
]
DEPRECATED_LENS_ALIASES = {
    "thinking_dispatcher": THINKING_MODEL_LENS_IDS,
}

DEFAULT_EXPERT_LENSES = [
    {
        "id": "blind_review",
        "label": "Blind-review expert",
        "zh_label": "盲审专家镜头",
        "en_label": "Blind-review expert",
        "description": "Checks contribution, rigor, evidence, and likely reviewer objections.",
        "zh_description": "检查贡献、严谨性、证据链与潜在审稿人质疑。",
        "en_description": "Checks contribution, rigor, evidence, and likely reviewer objections.",
    },
    {
        "id": "advisor_interrogation",
        "label": "Advisor interrogation expert",
        "zh_label": "严苛导师追问镜头",
        "en_label": "Advisor interrogation expert",
        "description": "Turns vague claims into hard advisor-style questions and required answers.",
        "zh_description": "把模糊论断转化为导师式追问与必答证据。",
        "en_description": "Turns vague claims into hard advisor-style questions and required answers.",
    },
    {
        "id": "aigc_risk",
        "label": "AIGC / AI-like wording risk expert",
        "zh_label": "AIGC / AI 味风险镜头",
        "en_label": "AIGC / AI-like wording risk expert",
        "description": "Flags generic wording, unsupported certainty, and suspiciously synthetic phrasing.",
        "zh_description": "识别泛化表达、无证据确定性与疑似 AI 化措辞。",
        "en_description": "Flags generic wording, unsupported certainty, and suspiciously synthetic phrasing.",
    },
    {
        "id": "novelty",
        "label": "Novelty / innovation expert",
        "zh_label": "创新性与差异化镜头",
        "en_label": "Novelty / innovation expert",
        "description": "Tests whether the claimed innovation is explicit, defensible, and differentiated.",
        "zh_description": "检查创新点是否明确、可辩护、可区分。",
        "en_description": "Tests whether the claimed innovation is explicit, defensible, and differentiated.",
    },
    {
        "id": "literature_evidence",
        "label": "Literature and evidence expert",
        "zh_label": "文献与证据链镜头",
        "en_label": "Literature and evidence expert",
        "description": "Checks source coverage, citation fit, evidence gaps, and over-claim risk.",
        "zh_description": "检查文献覆盖、引用匹配、证据缺口与过度声明风险。",
        "en_description": "Checks source coverage, citation fit, evidence gaps, and over-claim risk.",
    },
    {
        "id": "structure_expression",
        "label": "Structure and expression expert",
        "zh_label": "结构与表达镜头",
        "en_label": "Structure and expression expert",
        "description": "Reviews organization, transitions, terminology, readability, and argument flow.",
        "zh_description": "检查组织结构、过渡、术语、可读性与论证流。",
        "en_description": "Reviews organization, transitions, terminology, readability, and argument flow.",
    },
    {
        "id": "socratic_cbt",
        "label": "Socratic CBT-style questioning expert",
        "zh_label": "认知行为式苏格拉底提问镜头",
        "en_label": "Socratic CBT-style questioning expert",
        "description": "Uses calm Socratic questions to expose assumptions and improve revision decisions.",
        "zh_description": "用温和但精确的苏格拉底提问暴露假设并改善修改决策。",
        "en_description": "Uses calm Socratic questions to expose assumptions and improve revision decisions.",
    },
    {
        "id": "feynman_learning",
        "label": "Feynman learning expert",
        "zh_label": "费曼学习法专家",
        "en_label": "Feynman learning expert",
        "description": "Explains, simplifies, and checks whether the brief can be taught clearly.",
        "zh_description": "用费曼学习法解释、简化并检查 brief 是否能被清楚讲授。",
        "en_description": "Explains, simplifies, and checks whether the brief can be taught clearly.",
    },
    {
        "id": "first_principles",
        "label": "First principles expert",
        "zh_label": "第一性原理专家",
        "en_label": "First principles expert",
        "description": "Reduces claims to base assumptions, constraints, and irreducible facts.",
        "zh_description": "把论断拆到基础假设、约束与不可再分事实。",
        "en_description": "Reduces claims to base assumptions, constraints, and irreducible facts.",
    },
    {
        "id": "pyramid_principle",
        "label": "Pyramid principle expert",
        "zh_label": "金字塔原理专家",
        "en_label": "Pyramid principle expert",
        "description": "Structures conclusions, reasons, and evidence into a clear top-down argument.",
        "zh_description": "用金字塔原理组织结论、理由与证据，形成清晰自上而下论证。",
        "en_description": "Structures conclusions, reasons, and evidence into a clear top-down argument.",
    },
    {
        "id": "swot_analysis",
        "label": "SWOT analysis expert",
        "zh_label": "SWOT 分析专家",
        "en_label": "SWOT analysis expert",
        "description": "Separates strengths, weaknesses, opportunities, and threats for revision choices.",
        "zh_description": "区分优势、劣势、机会与威胁，用于修改决策。",
        "en_description": "Separates strengths, weaknesses, opportunities, and threats for revision choices.",
    },
    {
        "id": "decision_tree",
        "label": "Decision tree model expert",
        "zh_label": "决策树模型专家",
        "en_label": "Decision tree model expert",
        "description": "Models competing revision paths, decision points, risks, and expected outcomes.",
        "zh_description": "建模不同修改路径、决策点、风险与预期结果。",
        "en_description": "Models competing revision paths, decision points, risks, and expected outcomes.",
    },
]

DEFAULT_EXPERT_CATEGORIES = [
    {
        "id": "strict_graduate_advisor",
        "label": "Strict Graduate Advisor Module",
        "zh_label": "严苛的研究生导师专家模块",
        "en_label": "Strict Graduate Advisor Module",
        "description": "Strict advisor, blind review, novelty, evidence, AIGC-risk, and expression lenses.",
        "zh_description": "覆盖严苛导师、盲审、创新性、证据链、AIGC 风险与表达结构。",
        "en_description": "Strict advisor, blind review, novelty, evidence, AIGC-risk, and expression lenses.",
        "lens_ids": ["blind_review", "advisor_interrogation", "aigc_risk", "novelty", "literature_evidence", "structure_expression"],
    },
    {
        "id": "socratic_questioning",
        "label": "Socratic Questioning Module",
        "zh_label": "认知行为式提问专家模块",
        "en_label": "Socratic Questioning Module",
        "description": "CBT-style Socratic questioning lens for assumptions, options, and next actions.",
        "zh_description": "用认知行为式苏格拉底提问澄清假设、选择与下一步行动。",
        "en_description": "CBT-style Socratic questioning lens for assumptions, options, and next actions.",
        "lens_ids": ["socratic_cbt"],
    },
    {
        "id": "five_classic_thinking_models",
        "label": "Five Classic Thinking Models Module",
        "zh_label": "五大经典思维模型专家模块",
        "en_label": "Five Classic Thinking Models Module",
        "description": "Five independent thinking-model lenses for decomposing and choosing review routes.",
        "zh_description": "用五个可独立开启的经典思维模型镜头拆解问题并选择审阅路径。",
        "en_description": "Five independent thinking-model lenses for decomposing and choosing review routes.",
        "lens_ids": THINKING_MODEL_LENS_IDS,
    },
]

LEGACY_CATEGORY_ID_ALIASES = {
    "review": "strict_graduate_advisor",
    "risk": "strict_graduate_advisor",
    "thinking": "five_classic_thinking_models",
}
LEGACY_CATEGORY_LENS_IDS = {
    "review": ["blind_review", "advisor_interrogation", "novelty", "literature_evidence", "structure_expression"],
    "risk": ["aigc_risk", "literature_evidence"],
    "thinking": THINKING_MODEL_LENS_IDS,
}

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


def expand_deprecated_lens_aliases(values: Any, valid_lens_ids: set[str] | None = None) -> list[str]:
    if not isinstance(values, list):
        values = [] if values is None else [values]
    result: list[str] = []
    for value in values:
        lens_id = str(value or "").strip()
        if not lens_id:
            continue
        expanded = DEPRECATED_LENS_ALIASES.get(lens_id, [lens_id])
        for item in expanded:
            canonical = str(item or "").strip()
            if not canonical:
                continue
            if valid_lens_ids is not None and canonical not in valid_lens_ids:
                continue
            if canonical not in result:
                result.append(canonical)
    return result


def _is_valid_lens_or_deprecated_alias(lens_id: str, valid_lens_ids: set[str]) -> bool:
    if lens_id in valid_lens_ids:
        return True
    if lens_id not in DEPRECATED_LENS_ALIASES:
        return False
    return all(item in valid_lens_ids for item in DEPRECATED_LENS_ALIASES[lens_id])


def default_lens_categories(lenses: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    known_lens_ids: set[str] = set()
    for item in lenses or DEFAULT_EXPERT_LENSES:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        known_lens_ids.update(expand_deprecated_lens_aliases([item.get("id")]))
    assigned: set[str] = set()
    categories: list[dict[str, Any]] = []
    for category in DEFAULT_EXPERT_CATEGORIES:
        lens_ids = expand_deprecated_lens_aliases(category.get("lens_ids", []), known_lens_ids)
        assigned.update(lens_ids)
        categories.append({**category, "lens_ids": lens_ids})
    unassigned = sorted(known_lens_ids - assigned)
    if unassigned and categories:
        categories[0] = {**categories[0], "lens_ids": sorted(set(categories[0].get("lens_ids", [])) | set(unassigned))}
    return categories


def normalize_expert_categories(categories: list[dict[str, Any]] | None, lenses: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return the product display-layer categories as the three governed MOE modules.

    Target projects may still emit older `review` / `risk` / `thinking` category
    ids or custom public lens ids. The GUI keeps the lens ids but normalizes the
    visible category layer to the three requested expert modules.
    """
    lens_ids: set[str] = set()
    for item in lenses or DEFAULT_EXPERT_LENSES:
        if isinstance(item, dict) and item.get("id"):
            lens_ids.update(expand_deprecated_lens_aliases([item.get("id")]))
    normalized = default_lens_categories(list(lenses or DEFAULT_EXPERT_LENSES))
    by_id = {str(item.get("id")): dict(item) for item in normalized}
    assigned = {lens_id for item in by_id.values() for lens_id in item.get("lens_ids", [])}
    for category in categories or []:
        if not isinstance(category, dict) or not category.get("id"):
            continue
        raw_category_id = str(category.get("id") or "")
        target_id = _canonical_category_id(raw_category_id)
        if target_id not in by_id:
            target_id = "strict_graduate_advisor"
        merged_ids = set(by_id[target_id].get("lens_ids", []))
        if raw_category_id in LEGACY_CATEGORY_LENS_IDS:
            merged_ids.update(_legacy_category_member_lenses(raw_category_id, lens_ids))
        else:
            merged_ids.update(expand_deprecated_lens_aliases(category.get("lens_ids", []), lens_ids))
        by_id[target_id]["lens_ids"] = sorted(merged_ids)
        assigned.update(merged_ids)
    unassigned = lens_ids - assigned
    if unassigned:
        merged_ids = set(by_id["strict_graduate_advisor"].get("lens_ids", [])) | unassigned
        by_id["strict_graduate_advisor"]["lens_ids"] = sorted(merged_ids)
    return [by_id[str(item.get("id"))] for item in DEFAULT_EXPERT_CATEGORIES]


def _canonical_category_id(category_id: Any, valid_category_ids: set[str] | None = None) -> str:
    raw = str(category_id or "").strip()
    canonical = LEGACY_CATEGORY_ID_ALIASES.get(raw, raw)
    if valid_category_ids is not None and canonical not in valid_category_ids:
        return raw
    return canonical


def _legacy_category_member_lenses(category_id: Any, lens_ids: set[str]) -> list[str]:
    return expand_deprecated_lens_aliases(LEGACY_CATEGORY_LENS_IDS.get(str(category_id or ""), []), lens_ids)


def _default_lens_metadata_by_id() -> dict[str, dict[str, Any]]:
    return {str(item.get("id")): item for item in DEFAULT_EXPERT_LENSES if item.get("id")}


def _enrich_lens_display_fields(lens: dict[str, Any]) -> dict[str, Any]:
    lens_id = str(lens.get("id") or "")
    default = _default_lens_metadata_by_id().get(lens_id, {})
    label = str(lens.get("label") or default.get("label") or lens_id)
    description = str(lens.get("description") or default.get("description") or "")
    zh_label = str(lens.get("zh_label") or default.get("zh_label") or label)
    en_label = str(lens.get("en_label") or default.get("en_label") or label)
    zh_description = str(lens.get("zh_description") or default.get("zh_description") or description)
    en_description = str(lens.get("en_description") or default.get("en_description") or description)
    return {
        **lens,
        "id": lens_id,
        "label": label,
        "description": description,
        "zh_label": zh_label,
        "en_label": en_label,
        "zh_description": zh_description,
        "en_description": en_description,
    }


def normalize_lens_display_fields(lenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for lens in lenses:
        if not isinstance(lens, dict) or not lens.get("id"):
            continue
        raw_lens_id = str(lens.get("id") or "")
        for lens_id in expand_deprecated_lens_aliases([raw_lens_id]):
            source = dict(lens)
            if lens_id != raw_lens_id:
                source = {**_default_lens_metadata_by_id().get(lens_id, {"id": lens_id}), "id": lens_id}
            enriched = _enrich_lens_display_fields(source)
            canonical_id = str(enriched.get("id"))
            if canonical_id in DEPRECATED_LENS_ALIASES or canonical_id in seen:
                continue
            seen.add(canonical_id)
            result.append(enriched)
    return result


def _localized_display_label(item: dict[str, Any], mode: str = "bilingual", *, include_id: bool = False) -> str:
    item_id = str(item.get("id") or "")
    zh = str(item.get("zh_label") or item.get("label") or item.get("en_label") or item_id)
    en = str(item.get("en_label") or item.get("label") or item.get("zh_label") or item_id)
    if mode == "zh":
        label = zh
    elif mode == "en":
        label = en
    else:
        label = zh if zh == en else f"{zh} / {en}"
    return f"{label} ({item_id})" if include_id and item_id else label


def _localized_description(item: dict[str, Any], mode: str = "bilingual") -> str:
    zh = str(item.get("zh_description") or item.get("description") or item.get("en_description") or "")
    en = str(item.get("en_description") or item.get("description") or item.get("zh_description") or "")
    if mode == "zh":
        return zh
    if mode == "en":
        return en
    if zh and en and zh != en:
        return f"{zh} / {en}"
    return zh or en


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
                category_id = _canonical_category_id(_safe_short(item, 80))
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
        lenses = normalize_lens_display_fields([item for item in raw_lenses if isinstance(item, dict) and item.get("id")] if isinstance(raw_lenses, list) else [])
        categories = [item for item in raw_categories if isinstance(item, dict) and item.get("id")] if isinstance(raw_categories, list) else []
        if lenses:
            return {
                "schema_version": SCHEMA_VERSION,
                "token": payload_token(lenses_payload, "ok"),
                "source": "phase1-cli-list-lenses",
                "lenses": lenses,
                "categories": normalize_expert_categories(categories, lenses),
                "selection_semantics": lenses_payload.get("selection_semantics")
                if isinstance(lenses_payload.get("selection_semantics"), dict)
                else {"empty_selection": "all", "scope": "session", "mode_field": "effective_lens_mode"},
                "private_prompt_source_read": bool(lenses_payload.get("private_prompt_source_read", False)),
            }
    lenses = normalize_lens_display_fields(list(fallback_lenses or DEFAULT_EXPERT_LENSES))
    return {
        "schema_version": SCHEMA_VERSION,
        "token": "ok",
        "source": "safe-default",
        "lenses": lenses,
        "categories": normalize_expert_categories(None, lenses),
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


def build_workbench_artifact_history(root: Path) -> dict[str, Any]:
    try:
        payload = list_handoff_artifacts(root)
    except Exception as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:workbench_history_unavailable",
            "message": "Cannot read Project MOE GUI workbench artifact history.",
            "error": short_text(str(exc), 400),
            "items": [],
            "count": 0,
            "read_only": True,
        }
    items: list[dict[str, Any]] = []
    for item in payload.get("items") or []:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "artifact_id": item.get("artifact_id"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "status": item.get("status"),
                "handoff_target": item.get("handoff_target"),
                "session_display_id": item.get("session_display_id"),
                "selected_lenses": string_list(item.get("selected_lenses")),
                "selected_categories": string_list(item.get("selected_categories")),
                "task_template_id": item.get("task_template_id"),
                "path": item.get("path"),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": payload.get("token") or "ok",
        "runtime_root": payload.get("runtime_root"),
        "items": items,
        "count": len(items),
        "read_only": True,
    }


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
    artifact_history = build_workbench_artifact_history(root)
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
        "artifact_history": artifact_history,
        "copy_action": {
            "id": "copy_handoff_package_to_clipboard",
            "label": "Copy handoff package",
            "persistence": "clipboard_only",
            "writes_git": False,
            "writes_disk": False,
        },
        "save_draft_action": {
            "id": "save_handoff_draft",
            "label": "Save draft",
            "persistence": "target_runtime_artifact",
            "writes_git": False,
            "writes_target_project_state": False,
            "requires_carrier_execution": False,
        },
        "export_action": {
            "id": "export_handoff_package",
            "label": "Export handoff package",
            "persistence": "target_runtime_artifact_and_clipboard_text",
            "writes_git": False,
            "writes_target_project_state": False,
            "requires_carrier_execution": False,
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


def save_workbench_handoff_draft(
    config: dict[str, Any],
    *,
    session_id: str | None = None,
    session_display_id: str | None = None,
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    handoff_target: str = "main-session",
    task_template_id: str = "default",
    brief_text: str = "",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    root = configured_project_root(config, project_root)
    package = create_handoff_package(
        target_project=root,
        session_id=session_id,
        session_display_id=session_display_id or redact_identifier(session_id) or "(no session)",
        selected_lenses=selected_lenses or [],
        selected_categories=selected_categories or [],
        handoff_target=handoff_target,
        task_template_id=task_template_id,
        brief_text=brief_text,
        status="draft",
    )
    saved = save_handoff_artifact(root, package)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": bool(saved.get("ok")),
        "token": saved.get("token") or "blocked:workbench_draft_save_failed",
        "action": "save_handoff_draft",
        "message": "Workbench handoff draft saved as a target runtime artifact." if saved.get("ok") else saved.get("message"),
        "package": package,
        "saved": saved,
        "artifact_history": build_workbench_artifact_history(root),
        "writes_git": False,
        "writes_target_project_state": False,
        "writes_runtime_artifact": bool(saved.get("ok")),
        "executes_carrier": False,
    }


def export_workbench_handoff_package(
    config: dict[str, Any],
    *,
    session_id: str | None = None,
    session_display_id: str | None = None,
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    handoff_target: str = "main-session",
    task_template_id: str = "default",
    brief_text: str = "",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    root = configured_project_root(config, project_root)
    package = create_handoff_package(
        target_project=root,
        session_id=session_id,
        session_display_id=session_display_id or redact_identifier(session_id) or "(no session)",
        selected_lenses=selected_lenses or [],
        selected_categories=selected_categories or [],
        handoff_target=handoff_target,
        task_template_id=task_template_id,
        brief_text=brief_text,
        status="draft",
    )
    exported = export_handoff_package(package, handoff_target)
    saved = save_handoff_artifact(root, exported)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": bool(saved.get("ok")),
        "token": saved.get("token") or "blocked:workbench_export_failed",
        "action": "export_handoff_package",
        "message": "Workbench handoff package exported as carrier-shaped text only." if saved.get("ok") else saved.get("message"),
        "package": exported,
        "export_text": exported.get("export_text") or "",
        "saved": saved,
        "artifact_history": build_workbench_artifact_history(root),
        "writes_git": False,
        "writes_target_project_state": False,
        "writes_runtime_artifact": bool(saved.get("ok")),
        "executes_carrier": False,
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


def validate_write_cli_payload(action: str, payload: dict[str, Any] | None, *, expected_session_id: str | None = None) -> list[dict[str, Any]]:
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
    elif action.startswith("session-") and expected_session_id is not None and str(payload.get("session_id")) != str(expected_session_id):
        errors.append(
            stable_blocker(
                "blocked:write_cli_session_id_mismatch",
                "Session write commands must echo the same session_id that the GUI invoked.",
                action=action,
                expected=expected_session_id,
                observed=payload.get("session_id"),
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
    value = config.get("runtime_project_root") or fallback or config.get("installed_target_project_root") or config.get("target_project_root") or "."
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


def session_table_controls() -> dict[str, list[dict[str, str]]]:
    return {
        "filter_modes": [
            {"id": "all", "label": "All"},
            {"id": "enabled", "label": "Enabled"},
            {"id": "disabled", "label": "Disabled"},
            {"id": "blocked-invalid", "label": "Blocked or invalid"},
        ],
        "sort_keys": [
            {"id": "last_seen", "label": "Last seen"},
            {"id": "display_id", "label": "Display id"},
            {"id": "label", "label": "State label"},
            {"id": "effective_lens_mode", "label": "Effective lens mode"},
        ],
    }


def session_empty_state_variants() -> dict[str, dict[str, str]]:
    return {
        "no-session": {
            "title": "No sessions",
            "message": "No registered sessions were returned by the target Phase 1 CLI.",
        },
        "no-search-result": {
            "title": "No matching sessions",
            "message": "Adjust search text, filter, or sort controls to find a session.",
        },
        "readiness-blocked": {
            "title": "Readiness blocked",
            "message": "Session controls stay read-only until the target project readiness contract is healthy.",
        },
    }


def session_effective_state_explanation(row: dict[str, Any], project_default_enabled: bool | None = None) -> str:
    source = str(row.get("source") or row.get("effective_source") or "unknown")
    enabled = state_label(bool_state(row.get("enabled")))
    project_default = state_label(project_default_enabled)
    if row.get("valid") is False or str(row.get("token") or "ok") != "ok":
        return f"Blocked or invalid session record; effective state is {enabled}."
    if "manual" in source or "session" in source or "override" in source:
        return f"Session override sets this session to {enabled}; project default is {project_default}."
    if "project" in source:
        return f"Project default currently provides this session state: {enabled}."
    return f"Effective state is {enabled}; source is {source}."


def override_conflict_hint(row: dict[str, Any], project_default_enabled: bool | None = None) -> str:
    source = str(row.get("source") or row.get("effective_source") or "unknown")
    if row.get("valid") is False or str(row.get("token") or "ok") != "ok":
        return "Blocked or invalid sessions cannot safely apply project defaults or session overrides."
    if "manual" in source or "session" in source or "override" in source:
        return f"Session override wins over project default ({state_label(project_default_enabled)})."
    if "project" in source:
        return "No session override; project default applies."
    return "No explicit conflict detected; verify target CLI readback before writing."


def filter_sort_session_rows(
    rows: list[dict[str, Any]],
    *,
    search_text: str = "",
    filter_mode: str = "all",
    sort_key: str = "last_seen",
) -> list[dict[str, Any]]:
    needle = str(search_text or "").strip().lower()

    def matches_search(row: dict[str, Any]) -> bool:
        if not needle:
            return True
        haystack = " ".join(
            str(row.get(key) or "")
            for key in [
                "session_id",
                "display_id",
                "label",
                "source",
                "token",
                "effective_lens_mode",
                "lens_selection_summary",
            ]
        ).lower()
        return needle in haystack

    def matches_filter(row: dict[str, Any]) -> bool:
        enabled = bool_state(row.get("enabled"))
        blocked = row.get("valid") is False or str(row.get("token") or "ok") != "ok"
        if filter_mode == "enabled":
            return enabled is True and not blocked
        if filter_mode == "disabled":
            return enabled is False and not blocked
        if filter_mode == "blocked-invalid":
            return blocked
        return True

    result = [row for row in rows if isinstance(row, dict) and matches_search(row) and matches_filter(row)]
    if sort_key == "display_id":
        result.sort(key=lambda row: str(row.get("display_id") or row.get("session_id") or "").lower())
    elif sort_key == "label":
        result.sort(key=lambda row: str(row.get("label") or "").lower())
    elif sort_key == "effective_lens_mode":
        result.sort(key=lambda row: str(row.get("effective_lens_mode") or "").lower())
    else:
        result.sort(key=lambda row: str(row.get("last_seen_at") or ""), reverse=True)
    return result


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
    normalized_selected_lenses = expand_deprecated_lens_aliases(selected_lenses or [])
    normalized_selected_categories = string_list(selected_categories or [])
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
        for lens_id in normalized_selected_lenses:
            argv.extend(["--lens", str(lens_id)])
        for category_id in normalized_selected_categories:
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
        "selected_lenses": normalized_selected_lenses,
        "selected_categories": normalized_selected_categories,
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


def build_session_display_block(row: dict[str, Any]) -> dict[str, Any]:
    """Build the stable Sessions-tab identity block shared by model, Widgets, and QML."""
    conversation = row.get("conversation") if isinstance(row.get("conversation"), dict) else {}
    session_value = str(row.get("visible_session_id") or row.get("full_session_id") or row.get("session_id") or row.get("display_id") or "")
    created_value = str(row.get("created_display") or row.get("created_at") or "")
    if row.get("created_relative") and created_value:
        created_value = f"{row.get('created_relative')} - {created_value}"
    elif row.get("created_relative"):
        created_value = str(row.get("created_relative"))
    updated_value = str(row.get("updated_display") or row.get("updated_at") or row.get("last_seen_at") or "")
    if row.get("updated_relative") and updated_value:
        updated_value = f"{row.get('updated_relative')} - {updated_value}"
    elif row.get("updated_relative"):
        updated_value = str(row.get("updated_relative"))
    branch_value = str(row.get("branch") or "unknown")
    title = str(conversation.get("title") or row.get("conversation_title") or "")
    preview = str(conversation.get("preview") or row.get("conversation_preview") or "")
    conversation_value = preview or title
    if title and preview and title != preview:
        conversation_value = f"{title}\n{preview}"
    fields = {
        "Session": session_value,
        "Created": created_value,
        "Updated": updated_value,
        "Directory": str(row.get("directory") or ""),
        "Branch": branch_value,
        "Conversation": short_text(conversation_value, 800),
    }
    labels = ["Session", "Created", "Updated", "Directory", "Branch", "Conversation"]
    lines = [f"{label}: {fields[label]}" for label in labels]
    return {
        "schema_version": SCHEMA_VERSION,
        "labels": labels,
        "fields": fields,
        "lines": lines,
        "text": "\n".join(lines),
    }


def normalize_session_row(
    config: dict[str, Any],
    row: Any,
    index: int,
    *,
    project_default_enabled: bool | None = None,
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
            "enabled": None,
            "label": "unknown",
            "source": "invalid-record",
            "selected_lenses": [],
            "selected_categories": [],
            "effective_lens_mode": "all",
            "lens_selection_scope": "session",
            "lens_selection_summary": "All lenses",
            "last_seen_at": None,
            "effective_state_explanation": "Blocked or invalid session record; effective state is unknown.",
            "override_conflict_hint": "Blocked or invalid sessions cannot safely apply project defaults or session overrides.",
            "actions": {},
        }
    session_id = row.get("session_id") or row.get("id")
    valid = bool(session_id) and row.get("valid", True) is not False
    token = str(row.get("token") or ("ok" if valid else "blocked:invalid_session_record"))
    enabled = bool_state(row.get("effective_enabled"))
    if enabled is None:
        enabled = bool_state(row.get("enabled") if "enabled" in row else row.get("status"))
    selected_lenses = expand_deprecated_lens_aliases(row.get("selected_lenses") or [])
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
    result = {
        "row_index": index,
        "valid": valid,
        "token": token,
        "message": short_text(row.get("message") or ("ok" if valid else "Invalid session record."), 240),
        "session_id": str(session_id) if session_id else None,
        "display_id": redact_identifier(session_id),
        "enabled": enabled,
        "label": state_label(enabled),
        "source": row.get("source") or row.get("effective_source") or "unknown",
        "session_id_source": row.get("session_id_source"),
        "created_at": row.get("created_at") or row.get("created"),
        "updated_at": row.get("updated_at") or row.get("last_seen_at") or row.get("updated"),
        "created_display": _display_timestamp(row.get("created_at") or row.get("created")),
        "updated_display": _display_timestamp(row.get("updated_at") or row.get("last_seen_at") or row.get("updated")),
        "created_relative": _relative_timestamp(row.get("created_at") or row.get("created")),
        "updated_relative": _relative_timestamp(row.get("updated_at") or row.get("last_seen_at") or row.get("updated")),
        "directory": row.get("directory") or row.get("cwd") or row.get("project_root"),
        "branch": row.get("branch") or row.get("git_branch"),
        "thread_source": row.get("thread_source") or "unknown",
        "conversation": row.get("conversation") if isinstance(row.get("conversation"), dict) else {},
        "conversation_title": (row.get("conversation") or {}).get("title") if isinstance(row.get("conversation"), dict) else "",
        "conversation_preview": (row.get("conversation") or {}).get("preview") if isinstance(row.get("conversation"), dict) else "",
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
    result["effective_state_explanation"] = session_effective_state_explanation(result, project_default_enabled)
    result["override_conflict_hint"] = override_conflict_hint(result, project_default_enabled)
    result["session_display_block"] = build_session_display_block(result)
    result["session_display_lines"] = result["session_display_block"]["lines"]
    return result


def build_session_table(
    config: dict[str, Any],
    sessions_payload: dict[str, Any] | None,
    *,
    project_default_enabled: bool | None = None,
    project_root: str | Path | None = None,
    pending_scope: str | None = None,
    pending_scope_key: str | None = None,
) -> dict[str, Any]:
    controls = session_table_controls()
    empty_state_variants = session_empty_state_variants()
    if sessions_payload is None:
        return {
            "token": "blocked:list_sessions_not_loaded",
            "rows": [],
            "empty_state": {"is_empty": True, "message": "Session list has not been loaded."},
            "invalid_count": 0,
            "controls": controls,
            "empty_state_variants": empty_state_variants,
        }
    if not sessions_payload.get("ok", True):
        return {
            "token": payload_token(sessions_payload, "blocked:list_sessions_failed"),
            "rows": [],
            "empty_state": {"is_empty": True, "message": short_text(sessions_payload.get("message") or "Session list load failed.", 240)},
            "invalid_count": 0,
            "controls": controls,
            "empty_state_variants": empty_state_variants,
        }
    sessions = sessions_payload.get("sessions", [])
    if not isinstance(sessions, list):
        return {
            "token": "blocked:list_sessions_contract_invalid",
            "rows": [],
            "empty_state": {"is_empty": True, "message": "list-sessions --json must return a sessions array."},
            "invalid_count": 0,
            "controls": controls,
            "empty_state_variants": empty_state_variants,
        }
    rows = [
        normalize_session_row(
            config,
            row,
            index,
            project_default_enabled=project_default_enabled,
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
        "controls": controls,
        "empty_state_variants": empty_state_variants,
    }




def build_ui_states(*, has_sessions: bool, blockers: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    blocker_tokens = [str(item.get("token") or "unknown") for item in blockers if isinstance(item, dict)]
    return {
        "loading": {
            "title": "Loading state",
            "message": "Refreshing Project MOE status, sessions, lenses, and runtime diagnostics.",
            "visible_when": "bridge_refresh_in_progress",
        },
        "empty": {
            "title": "Empty state",
            "message": "No sessions or handoff history are available yet." if not has_sessions else "No filtered rows match the current controls.",
            "visible_when": "no_sessions_or_no_search_results",
        },
        "error": {
            "title": "Error state",
            "message": "Stable blockers are shown in Diagnostics before any write action is enabled.",
            "visible_when": "blockers_present",
            "tokens": blocker_tokens,
        },
        "help": {
            "title": "Help",
            "message": "MOE lenses shape the brief; carriers such as main session, subagent, durable team, and LangGraph remain leader-controlled.",
            "visible_when": "operator_requests_help",
        },
    }


def build_multi_project_panel(config: dict[str, Any], *, source_toolchain_version: str = TOOLCHAIN_VERSION) -> dict[str, Any]:
    projects: list[dict[str, Any]] = []
    raw_projects = config.get("managed_projects")
    listed_projects = raw_projects if isinstance(raw_projects, list) else []
    for index, raw_project in enumerate(listed_projects):
        project_root = Path(str(raw_project)).expanduser().resolve(strict=False)
        config_path = project_root / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
        manifest_path = project_root / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json"
        installed_version = None
        readiness_status = "unknown"
        install_status = "not_installed"
        blockers: list[dict[str, str]] = []
        for path in [config_path, manifest_path]:
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                blockers.append({"token": "blocked:project_moe_gui_status_read_failed", "message": str(exc)})
                continue
            if isinstance(payload, dict):
                installed_version = installed_version or payload.get("toolchain_version") or payload.get("installed_toolchain_version")
                readiness_status = str(payload.get("readiness_status") or payload.get("status") or readiness_status)
                install_status = "installed"
        version_lag = bool(installed_version and str(installed_version) != str(source_toolchain_version))
        if version_lag:
            install_status = "upgrade_available"
        projects.append(
            {
                "index": index,
                "project_root": str(project_root),
                "config_path": str(config_path),
                "manifest_path": str(manifest_path),
                "listed_explicitly": True,
                "installed_version": str(installed_version) if installed_version is not None else None,
                "source_toolchain_version": source_toolchain_version,
                "install_status": install_status,
                "readiness_status": readiness_status,
                "version_lag": version_lag,
                "dirty_status": "not_checked_read_only_panel",
                "blockers": blockers,
                "dry_run_update_plan": {
                    "mode": "dry-run",
                    "writes_target_project": False,
                    "requires_installer_gate": True,
                    "would_update": version_lag,
                    "target_project": str(project_root),
                },
                "rollback_hint": "Use the target project's Project MOE GUI rollback note or install manifest rollback pointer before applying updates.",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "title": "Projects",
        "read_only": True,
        "writes_target_projects": False,
        "source_toolchain_version": source_toolchain_version,
        "project_registry_contract": "explicit-config-managed_projects-only",
        "projects": projects,
        "empty_state": {"is_empty": not projects, "message": "No managed projects are explicitly listed."},
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
    project_default = extract_project_default(project_status, status_payload)
    effective = extract_effective(status_payload, project_status)
    session_table = build_session_table(
        config,
        sessions_payload,
        project_default_enabled=project_default,
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
                {"id": "projects", "label": "Projects", "icon": "Folder", "target_region": "multi_project_panel"},
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
        "multi_project_panel": build_multi_project_panel(config),
        "ui_states": build_ui_states(has_sessions=bool(session_rows), blockers=banners),
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


_qml_build_view_model = build_view_model
_qml_build_gui_preflight = build_gui_preflight


def _product_language_mode(config: dict[str, Any] | None = None) -> str:
    configured = ""
    if isinstance(config, dict):
        configured = str(config.get("language_mode") or config.get("ui_language") or "").strip().lower()
    value = os.environ.get("PROJECT_MOE_GUI_LANGUAGE", "").strip().lower() or configured or "bilingual"
    return value if value in {"en", "zh", "bilingual"} else "bilingual"


_PRODUCT_I18N: dict[str, dict[str, str]] = {
    "app_title": {"zh": "Project MOE 控制台", "en": "Project MOE Agent Console"},
    "overview": {"zh": "概览", "en": "Overview"},
    "sessions": {"zh": "会话", "en": "Sessions"},
    "workbench": {"zh": "交接台", "en": "Workbench"},
    "diagnostics": {"zh": "诊断", "en": "Diagnostics"},
    "settings": {"zh": "设置", "en": "Settings"},
    "project_default": {"zh": "项目默认", "en": "Project default"},
    "effective_status": {"zh": "生效状态", "en": "Effective status"},
    "session_count": {"zh": "会话数量", "en": "Sessions"},
    "gui_runtime": {"zh": "GUI 运行时", "en": "GUI runtime"},
    "visual_shell": {"zh": "视觉外壳", "en": "Visual shell"},
    "target_project_only": {"zh": "只显示并控制当前项目会话", "en": "Shows and controls only this target project"},
    "session_list": {"zh": "会话列表", "en": "Session list"},
    "session_details": {"zh": "会话详情", "en": "Session details"},
    "moe_status_actions": {"zh": "MOE 状态与操作", "en": "MOE status and actions"},
    "moe_lens_selection": {"zh": "MOE 分类与镜头选择", "en": "MOE categories and lenses"},
    "session_moe_lenses": {"zh": "会话 MOE 镜头", "en": "Session MOE lenses"},
    "enable_session_moe": {"zh": "开启本会话 MOE", "en": "Enable session MOE"},
    "disable_session_moe": {"zh": "关闭本会话 MOE", "en": "Disable session MOE"},
    "apply_session_lenses": {"zh": "应用会话镜头", "en": "Apply session lenses"},
    "clear_session_lenses": {"zh": "清空会话镜头", "en": "Clear session lenses"},
    "moe_categories": {"zh": "MOE 分类", "en": "MOE categories"},
    "moe_lenses": {"zh": "MOE 镜头", "en": "MOE lenses"},
    "sessions_total": {"zh": "个会话", "en": "sessions"},
    "search_session_placeholder": {"zh": "搜索会话 ID、标题、目录、分支", "en": "Search session id, title, directory, branch"},
    "empty_selection_all": {"zh": "空选择 = 全部镜头", "en": "Empty selection = all lenses"},
}


def _product_text(key: str, mode: str = "bilingual") -> str:
    payload = _PRODUCT_I18N.get(key, {"zh": key, "en": key})
    zh = payload.get("zh") or key
    en = payload.get("en") or key
    if mode == "zh":
        return zh
    if mode == "en":
        return en
    return f"{zh} / {en}"


def _product_lens_selection_model(
    lenses: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    selected_lenses: list[str] | None = None,
    selected_categories: list[str] | None = None,
    language: str = "bilingual",
) -> dict[str, Any]:
    lens_ids = {str(item.get("id")) for item in lenses if item.get("id")}
    category_map = {
        str(item.get("id")): {str(lens_id) for lens_id in item.get("lens_ids", []) if str(lens_id) in lens_ids}
        for item in categories
        if item.get("id")
    }
    raw_explicit_lenses = string_list(selected_lenses or [])
    explicit_lenses = expand_deprecated_lens_aliases(raw_explicit_lenses, lens_ids)
    valid_category_ids = set(category_map)
    raw_categories = string_list(selected_categories or [])
    explicit_categories = [_canonical_category_id(item, valid_category_ids) for item in raw_categories]
    effective = {item for item in explicit_lenses if item in lens_ids}
    for raw_category_id, category_id in zip(raw_categories, explicit_categories):
        effective.update(category_map.get(category_id, set()))
        if raw_category_id != category_id:
            effective.update(_legacy_category_member_lenses(raw_category_id, lens_ids))
    mode = "selected" if explicit_lenses or explicit_categories else "all"
    effective_lenses = sorted(effective) if mode == "selected" else sorted(lens_ids)
    selected_set = set(effective_lenses)
    enriched_categories = []
    for category in categories:
        category_id = str(category.get("id"))
        ids = category_map.get(category_id, set())
        selected_count = len(ids & selected_set)
        enriched_categories.append(
            {
                **category,
                "lens_ids": sorted(ids),
                "selected": category_id in explicit_categories,
                "check_state": "checked" if ids and selected_count == len(ids) else ("partial" if selected_count else "unchecked"),
                "selected_lens_count": selected_count,
                "total_lens_count": len(ids),
                "display_label": _localized_display_label(category, language),
                "display_label_with_id": _localized_display_label(category, language, include_id=True),
                "display_description": _localized_description(category, language),
            }
        )
    enriched_lenses = [
        {
            **lens,
            "display_label": _localized_display_label(lens, language),
            "display_label_with_id": _localized_display_label(lens, language, include_id=True),
            "display_description": _localized_description(lens, language),
        }
        for lens in lenses
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "selected_lenses": explicit_lenses,
        "selected_categories": explicit_categories,
        "invalid_lenses": [item for item in raw_explicit_lenses if not _is_valid_lens_or_deprecated_alias(item, lens_ids)],
        "invalid_categories": [item for item in explicit_categories if item not in category_map],
        "effective_lenses": effective_lenses,
        "effective_lens_count": len(effective_lenses),
        "categories": enriched_categories,
        "lenses": enriched_lenses,
        "language": language,
        "tri_state_contract": {
            "category_change_updates_member_lenses": True,
            "manual_lens_change_updates_category_state": True,
        },
    }


def _path_is_inside_project(candidate: str | Path | None, root: Path) -> bool:
    if candidate is None or str(candidate).strip() == "":
        return False
    try:
        value = Path(str(candidate)).expanduser().resolve(strict=False)
        return value == root or root in value.parents
    except Exception:
        return False


def _session_sort_key(item: dict[str, Any]) -> str:
    return str(item.get("updated_at") or item.get("timestamp") or "")


def _timestamp_from_path_mtime(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        return None


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _relative_timestamp(value: Any) -> str:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return ""
    now = datetime.now(timezone.utc)
    delta = now - parsed.astimezone(timezone.utc)
    seconds = int(delta.total_seconds())
    future = seconds < 0
    seconds = abs(seconds)
    if seconds < 60:
        amount, unit = seconds, "s"
    elif seconds < 3600:
        amount, unit = seconds // 60, "m"
    elif seconds < 86400:
        amount, unit = seconds // 3600, "h"
    else:
        amount, unit = seconds // 86400, "d"
    suffix = "from now" if future else "ago"
    return f"{amount}{unit} {suffix}"


def _display_timestamp(value: Any) -> str:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return str(value or "")
    return parsed.astimezone().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def _codex_session_thread_source(meta: dict[str, Any]) -> str:
    explicit = str(meta.get("thread_source") or "").strip().lower()
    if explicit:
        return explicit
    source = meta.get("source")
    if isinstance(source, dict) and source.get("subagent"):
        return "subagent"
    if meta.get("forked_from_id"):
        return "subagent"
    return "user"


def _is_codex_child_agent_session(meta: dict[str, Any]) -> bool:
    if _codex_session_thread_source(meta) == "subagent":
        return True
    source = meta.get("source")
    if isinstance(source, dict) and source.get("subagent"):
        return True
    if meta.get("forked_from_id"):
        return True
    if meta.get("agent_role") and str(meta.get("source") or "").lower() != "cli":
        return True
    return False


def _codex_parent_thread_id(meta: dict[str, Any]) -> str | None:
    if meta.get("forked_from_id"):
        return str(meta.get("forked_from_id"))
    source = meta.get("source")
    if isinstance(source, dict):
        spawn = ((source.get("subagent") or {}) if isinstance(source.get("subagent"), dict) else {}).get("thread_spawn")
        if isinstance(spawn, dict) and spawn.get("parent_thread_id"):
            return str(spawn.get("parent_thread_id"))
    return None


def _text_parts_from_codex_content(value: Any) -> list[str]:
    parts: list[str] = []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        for item in value:
            parts.extend(_text_parts_from_codex_content(item))
        return parts
    if isinstance(value, dict):
        for key in ("text", "content"):
            if key in value:
                parts.extend(_text_parts_from_codex_content(value.get(key)))
        return parts
    return []


def _codex_item_role_and_text(item: dict[str, Any]) -> tuple[str | None, str]:
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
    message = payload.get("message") if isinstance(payload.get("message"), dict) else {}
    role = payload.get("role") or message.get("role") or item.get("role")
    if not isinstance(role, str) or role not in {"user", "assistant"}:
        return None, ""
    content = payload.get("content")
    if content is None and message:
        content = message.get("content")
    text = "\n".join(part for part in _text_parts_from_codex_content(content) if part.strip()).strip()
    return role, text


def _is_codex_injected_user_context(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped:
        return True
    injected_prefixes = (
        "# AGENTS.md instructions",
        "<environment_context>",
        "<codex_internal_context",
        "Another language model started to solve this problem",
    )
    return any(stripped.startswith(prefix) for prefix in injected_prefixes)


def _read_codex_session_preview(path: Path, meta: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    max_lines = int(config.get("codex_session_preview_max_lines") or 50000)
    title_chars = int(config.get("codex_session_title_max_chars") or 240)
    preview_chars = int(config.get("codex_session_preview_max_chars") or 900)
    first_user_text = ""
    last_assistant_text = ""
    last_user_text = ""
    first_visible_ts: str | None = None
    last_visible_ts: str | None = None
    user_count = 0
    assistant_count = 0
    scanned_lines = 0
    truncated = False
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for scanned_lines, line in enumerate(handle, start=1):
                if scanned_lines > max_lines:
                    truncated = True
                    break
                try:
                    item = json.loads(line)
                except Exception:
                    continue
                if not isinstance(item, dict):
                    continue
                role, text = _codex_item_role_and_text(item)
                if not role or not text:
                    continue
                timestamp = str(item.get("timestamp") or "")
                first_visible_ts = first_visible_ts or timestamp or None
                last_visible_ts = timestamp or last_visible_ts
                if role == "user":
                    if _is_codex_injected_user_context(text):
                        continue
                    user_count += 1
                    last_user_text = text
                    if not first_user_text:
                        first_user_text = text
                elif role == "assistant":
                    assistant_count += 1
                    last_assistant_text = text
    except Exception as exc:
        return {
            "title": "",
            "preview": "",
            "message_counts": {"user": user_count, "assistant": assistant_count},
            "preview_error": short_text(exc, 160),
            "preview_truncated": truncated,
        }
    created_at = str(meta.get("timestamp") or meta.get("created_at") or first_visible_ts or _timestamp_from_path_mtime(path) or "")
    updated_at = str(last_visible_ts or meta.get("updated_at") or meta.get("timestamp") or _timestamp_from_path_mtime(path) or "")
    return {
        "title": short_text(first_user_text, title_chars),
        "preview": short_text(last_assistant_text or last_user_text, preview_chars),
        "message_counts": {"user": user_count, "assistant": assistant_count},
        "created_at": created_at,
        "updated_at": updated_at,
        "preview_truncated": truncated,
        "scanned_lines": scanned_lines,
        "scope": "target_project_top_level_user_assistant_preview_only",
    }


def _read_codex_session_meta(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for line_index, line in enumerate(handle):
                if line_index >= 120:
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


def _discover_codex_session_logs(config: dict[str, Any], root: Path, home: Path) -> dict[str, Any]:
    sessions_root = Path(str(config.get("codex_sessions_root") or home / ".codex" / "sessions")).expanduser().resolve(strict=False)
    max_files = int(config.get("codex_session_discovery_max_files") or 20000)
    max_sessions = int(config.get("codex_session_discovery_max_sessions") or 5000)
    discovered: list[dict[str, Any]] = []
    scanned_files = 0
    skipped_other_project = 0
    skipped_without_meta = 0
    hidden_child_agent_sessions = 0
    truncated = False
    if sessions_root.exists() and sessions_root.is_dir():
        try:
            files = sorted(sessions_root.rglob("*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True)
        except Exception:
            files = []
        for path in files:
            if scanned_files >= max_files:
                truncated = True
                break
            scanned_files += 1
            meta = _read_codex_session_meta(path)
            if not meta:
                skipped_without_meta += 1
                continue
            cwd = meta.get("cwd") or meta.get("project_root") or meta.get("working_directory") or meta.get("repo_root")
            if not _path_is_inside_project(cwd, root):
                skipped_other_project += 1
                continue
            if _is_codex_child_agent_session(meta):
                hidden_child_agent_sessions += 1
                continue
            session_id = meta.get("id") or meta.get("session_id") or meta.get("thread_id") or meta.get("resume_id")
            if not session_id:
                skipped_without_meta += 1
                continue
            git = meta.get("git") if isinstance(meta.get("git"), dict) else {}
            preview = _read_codex_session_preview(path, meta, config)
            created_at = preview.get("created_at") or meta.get("timestamp") or meta.get("created_at")
            updated_at = preview.get("updated_at") or meta.get("timestamp") or meta.get("updated_at") or meta.get("created_at")
            discovered.append(
                {
                    "session_id": str(session_id),
                    "thread_id": str(meta.get("thread_id") or meta.get("resume_id") or session_id),
                    "project_root": str(cwd),
                    "cwd": str(cwd),
                    "directory": str(Path(str(cwd)).expanduser().resolve(strict=False)),
                    "source": str(path),
                    "source_kind": "codex-session-jsonl",
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "git_branch": git.get("branch"),
                    "branch": git.get("branch"),
                    "thread_source": _codex_session_thread_source(meta),
                    "parent_thread_id": _codex_parent_thread_id(meta),
                    "agent_role": meta.get("agent_role"),
                    "agent_nickname": meta.get("agent_nickname"),
                    "conversation": {
                        "title": preview.get("title") or "",
                        "preview": preview.get("preview") or "",
                        "message_counts": preview.get("message_counts") or {"user": 0, "assistant": 0},
                        "preview_truncated": preview.get("preview_truncated") is True,
                        "scope": preview.get("scope"),
                    },
                    "metadata_only": False,
                }
            )
            if len(discovered) >= max_sessions:
                truncated = True
                break
    deduped: dict[str, dict[str, Any]] = {}
    for item in sorted(discovered, key=_session_sort_key, reverse=True):
        deduped.setdefault(str(item["session_id"]), item)
    sessions = list(deduped.values())
    return {
        "path": str(sessions_root),
        "exists": sessions_root.exists(),
        "kind": "codex-session-jsonl-tree",
        "sessions": sessions,
        "count": len(sessions),
        "scanned_files": scanned_files,
        "skipped_other_project": skipped_other_project,
        "skipped_without_meta": skipped_without_meta,
        "hidden_child_agent_sessions": hidden_child_agent_sessions,
        "truncated": truncated,
        "max_files": max_files,
        "max_sessions": max_sessions,
    }


def _safe_codex_session_index(config: dict[str, Any], root: Path) -> dict[str, Any]:
    home = Path(os.environ.get("USERPROFILE") or str(Path.home()))
    index_path = Path(str(config.get("codex_session_index_path") or home / ".codex" / "session_index.jsonl")).expanduser().resolve(strict=False)
    log_discovery = _discover_codex_session_logs(config, root, home)
    sessions_by_id: dict[str, dict[str, Any]] = {
        str(item.get("session_id")): item
        for item in log_discovery.get("sessions", [])
        if isinstance(item, dict) and item.get("session_id")
    }
    index_sessions: list[dict[str, Any]] = []
    skipped_other_project_index = 0
    if index_path.exists() and index_path.is_file():
        try:
            with index_path.open("r", encoding="utf-8-sig", errors="replace") as handle:
                for line_index, line in enumerate(handle):
                    if line_index >= 400:
                        break
                    try:
                        item = json.loads(line.strip())
                    except Exception:
                        continue
                    if not isinstance(item, dict):
                        continue
                    session_id = item.get("session_id") or item.get("id") or item.get("thread_id") or item.get("resume_id")
                    if not session_id:
                        continue
                    item_project = item.get("project_root") or item.get("cwd") or item.get("working_directory") or item.get("repo_root")
                    in_scope = _path_is_inside_project(item_project, root)
                    if not in_scope:
                        skipped_other_project_index += 1
                        continue
                    index_sessions.append(
                        {
                            "session_id": str(session_id),
                            "thread_id": str(item.get("thread_id") or item.get("resume_id") or session_id),
                            "project_root": str(item_project or root),
                            "source": str(index_path),
                            "source_kind": "codex-session-index-jsonl",
                            "updated_at": item.get("updated_at") or item.get("last_seen_at") or item.get("created_at"),
                            "metadata_only": True,
                        }
                    )
        except Exception:
            index_sessions = []
    for item in index_sessions:
        session_id = str(item.get("session_id"))
        if session_id in sessions_by_id:
            sessions_by_id[session_id]["index_source"] = item.get("source")
            sessions_by_id[session_id]["index_updated_at"] = item.get("updated_at")
    sessions = sorted(sessions_by_id.values(), key=_session_sort_key, reverse=True)
    truncated = bool(log_discovery.get("truncated"))
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": "ok",
        "read_only": True,
        "project_scope": str(root),
        "sources": [
            {"path": str(index_path), "exists": index_path.exists(), "kind": "jsonl-index"},
            {key: value for key, value in log_discovery.items() if key != "sessions"},
        ],
        "sessions": sessions,
        "count": len(sessions),
        "skipped_other_project": int(log_discovery.get("skipped_other_project") or 0) + skipped_other_project_index,
        "hidden_child_agent_sessions": int(log_discovery.get("hidden_child_agent_sessions") or 0),
        "truncated": truncated,
        "privacy_policy": {
            "reads_session_file_bodies": True,
            "reads_message_bodies": True,
            "message_body_scope": "target_project_top_level_user_assistant_preview_only",
            "reads_credentials": False,
            "metadata_only": False,
            "authority": "session_meta.cwd plus top-level thread_source=user in Codex session jsonl is authoritative for project scope; session_index is supplemental only",
        },
    }


def build_compact_session_list_text(row: dict[str, Any], *, max_title_chars: int = 88) -> str:
    """Build the one-line Sessions list label.

    The full identity block stays in `session_display_block` for the right-side
    detail card and tooltip. This compact label deliberately avoids `Session:`,
    `Created:`, `Directory:` and other detail labels so the left list remains
    scannable.
    """
    conversation = row.get("conversation") if isinstance(row.get("conversation"), dict) else {}
    title = str(conversation.get("title") or row.get("conversation_title") or row.get("display_id") or row.get("visible_session_id") or row.get("session_id") or "")
    updated = str(row.get("updated_relative") or row.get("updated_display") or row.get("updated_at") or row.get("last_seen_at") or "").strip()
    state = str(row.get("label") or row.get("status_badge", {}).get("text") or "unknown")
    branch = str(row.get("branch") or "").strip()
    prefix = f"{updated}  " if updated else ""
    suffix_parts = [part for part in [state, f"@{branch}" if branch else ""] if part]
    suffix = f"  [{' · '.join(suffix_parts)}]" if suffix_parts else ""
    return f"{prefix}{short_text(title, max_title_chars)}{suffix}"


def _product_enrich_session_row(
    row: dict[str, Any],
    lenses: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    *,
    why_shown: str | None = None,
    language: str = "bilingual",
) -> dict[str, Any]:
    selected_lenses = expand_deprecated_lens_aliases(row.get("selected_lenses") or [])
    selected_categories = string_list(row.get("selected_categories"))
    selection_model = _product_lens_selection_model(lenses, categories, selected_lenses, selected_categories, language=language)
    full_id = str(row.get("session_id") or "")
    result = {
        **row,
        "full_session_id": full_id,
        "visible_session_id": full_id or str(row.get("display_id") or ""),
        "session_id_source": row.get("session_id_source") or "phase1-cli-list-sessions",
        "why_shown": why_shown
        or "Displayed because target Project MOE state returned this session and no explicit hidden_from_default_view=true gate was applied.",
        "testing_metadata": {
            "session_kind": str(row.get("session_kind") or row.get("kind") or "ordinary"),
            "is_test_session": row.get("is_test_session") is True,
            "hidden_from_default_view": row.get("hidden_from_default_view") is True,
            "name_heuristic_used": False,
            "classification_source": "explicit_metadata_only" if any(key in row for key in ["session_kind", "kind", "is_test_session", "hidden_from_default_view", "created_by"]) else "ordinary_by_default",
        },
        "name_heuristic_hidden": False,
        "selection_model": selection_model,
        "effective_lenses": selection_model.get("effective_lenses", []),
        "effective_lens_count": selection_model.get("effective_lens_count", 0),
    }
    result["session_display_block"] = build_session_display_block(result)
    result["session_display_lines"] = result["session_display_block"]["lines"]
    result["compact_list_text"] = build_compact_session_list_text(result)
    return result


def _merge_codex_discovery_into_registered_row(row: dict[str, Any], match: dict[str, Any] | None) -> dict[str, Any]:
    """Merge authoritative Codex session identity fields into a registered MOE state row.

    Project MOE state rows own control state such as enabled/disabled and lens selection.
    Codex session discovery owns user-visible session identity such as directory,
    created/updated timestamps, branch, and conversation preview.
    """
    if not isinstance(match, dict):
        return dict(row)
    conversation = match.get("conversation") if isinstance(match.get("conversation"), dict) else row.get("conversation")
    if not isinstance(conversation, dict):
        conversation = {}
    created_at = match.get("created_at") or row.get("created_at")
    updated_at = match.get("updated_at") or match.get("last_seen_at") or row.get("updated_at") or row.get("last_seen_at")
    merged = {
        **row,
        "moe_state_created_at": row.get("created_at"),
        "moe_state_updated_at": row.get("updated_at") or row.get("last_seen_at"),
        "created_at": created_at,
        "updated_at": updated_at,
        "last_seen_at": updated_at,
        "created_display": _display_timestamp(created_at),
        "updated_display": _display_timestamp(updated_at),
        "created_relative": _relative_timestamp(created_at),
        "updated_relative": _relative_timestamp(updated_at),
        "directory": match.get("directory") or match.get("cwd") or match.get("project_root") or row.get("directory"),
        "branch": match.get("branch") or match.get("git_branch") or row.get("branch"),
        "thread_source": match.get("thread_source") or row.get("thread_source") or "user",
        "conversation": conversation,
        "conversation_title": conversation.get("title") or row.get("conversation_title") or "",
        "conversation_preview": conversation.get("preview") or row.get("conversation_preview") or "",
    }
    return merged


def _reconcile_product_rows(
    rows: list[dict[str, Any]],
    discovery: dict[str, Any],
    config: dict[str, Any],
    *,
    project_root: Path,
    project_default_enabled: bool | None,
    lenses: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    language: str = "bilingual",
) -> list[dict[str, Any]]:
    discovered = [item for item in discovery.get("sessions", []) if isinstance(item, dict)] if isinstance(discovery, dict) else []
    by_id = {str(item.get("session_id")): item for item in discovered if item.get("session_id")}
    by_thread = {str(item.get("thread_id")): item for item in discovered if item.get("thread_id")}
    discovery_authoritative = bool(discovered)
    result: list[dict[str, Any]] = []
    supplemental_state_only_rows: list[dict[str, Any]] = []
    matched_ids: set[str] = set()
    for row in rows:
        full_id = str(row.get("session_id") or row.get("full_session_id") or "")
        match = by_id.get(full_id) or by_thread.get(full_id)
        confidence = "exact" if match else "unmatched"
        if match and match.get("session_id"):
            matched_ids.add(str(match.get("session_id")))
        row_origin = "registered-matched" if match else "state-only"
        merged_row = _merge_codex_discovery_into_registered_row(row, match)
        reconciled = {
            **merged_row,
            "row_origin": row_origin,
            "codex_mapping": {
                "confidence": confidence,
                "codex_thread_id": match.get("thread_id") if match else None,
                "source": match.get("source") if match else None,
                "message": "Codex session mapping matched exactly." if match else "Codex session mapping unavailable or not found for this project.",
                "read_only": True,
            },
            "mapping_confidence": confidence,
        }
        if match or not discovery_authoritative:
            result.append(
                _product_enrich_session_row(
                    reconciled,
                    lenses,
                    categories,
                    language=language,
                    why_shown=(
                        "Displayed because target Project MOE state matched authoritative Codex session metadata for this project."
                        if match
                        else None
                    ),
                )
            )
        else:
            supplemental_state_only_rows.append(
                {
                    **reconciled,
                    "visible_in_main_table": False,
                    "why_hidden": "Hidden from the main project session table because no target-project top-level Codex session metadata matched this Project MOE state record.",
                }
            )
    for item in discovered:
        session_id = str(item.get("session_id") or "")
        if not session_id or session_id in matched_ids or any(str(row.get("session_id")) == session_id for row in result):
            continue
        normalized = normalize_session_row(
            config,
            {
                "session_id": session_id,
                "enabled": project_default_enabled,
                "effective_enabled": project_default_enabled,
                "valid": True,
                "token": "ok",
                "source": "discovered-only",
                "effective_source": "project-default",
                "session_id_source": "codex-session-log",
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "last_seen_at": item.get("updated_at"),
                "directory": item.get("directory") or item.get("cwd") or item.get("project_root"),
                "branch": item.get("branch") or item.get("git_branch"),
                "thread_source": item.get("thread_source") or "user",
                "conversation": item.get("conversation") if isinstance(item.get("conversation"), dict) else {},
                "selected_lenses": [],
                "selected_categories": [],
                "effective_lens_mode": "all",
                "lens_selection_scope": "session",
                "message": "Discovered from Codex session metadata; no Project MOE session override has been written yet.",
            },
            len(result),
            project_default_enabled=project_default_enabled,
            project_root=project_root,
        )
        enriched = _product_enrich_session_row(
            normalized,
            lenses,
            categories,
            language=language,
            why_shown="Displayed because Codex session metadata says this session belongs to the target project; no MOE state file exists yet.",
        )
        result.append(
            {
                **enriched,
                "row_origin": "discovered-only",
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "directory": item.get("directory") or item.get("cwd") or item.get("project_root"),
                "branch": item.get("branch") or item.get("git_branch"),
                "thread_source": item.get("thread_source") or "user",
                "conversation": item.get("conversation") if isinstance(item.get("conversation"), dict) else {},
                "codex_mapping": {
                    "confidence": "exact",
                    "codex_thread_id": item.get("thread_id"),
                    "source": item.get("source"),
                    "message": "Codex session discovered from session_meta.cwd; no Project MOE state exists yet.",
                    "read_only": True,
                },
                "mapping_confidence": "exact",
            }
        )
    setattr(_reconcile_product_rows, "_last_supplemental_state_only_rows", supplemental_state_only_rows)
    return result


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
    model = _qml_build_view_model(
        config,
        project_root=project_root,
        project_status=project_status,
        sessions_payload=sessions_payload,
        lenses_payload=lenses_payload,
        status_payload=status_payload,
        pyside6_available=pyside6_available,
        qfluent_status=qfluent_status,
        pending_scope=pending_scope,
    )
    root = configured_project_root(config, project_root)
    language = _product_language_mode(config)
    qfluent_payload = qfluent_status or (((model.get("visual") or {}).get("legacy_qfluent") or {}).get("qfluentwidgets_status") if isinstance(model.get("visual"), dict) else None) or {
        "schema_version": SCHEMA_VERSION,
        "ok": False,
        "token": "blocked:qfluentwidgets_not_checked",
        "blockers": [],
    }
    lens_catalog = model.get("lens_catalog") if isinstance(model.get("lens_catalog"), dict) else normalize_lens_catalog(lenses_payload)
    lenses = normalize_lens_display_fields(list(lens_catalog.get("lenses") or []))
    categories = normalize_expert_categories(list(lens_catalog.get("categories") or []), lenses)
    lenses = [
        {
            **lens,
            "display_label": _localized_display_label(lens, language),
            "display_label_with_id": _localized_display_label(lens, language, include_id=True),
            "display_description": _localized_description(lens, language),
        }
        for lens in lenses
    ]
    categories = [
        {
            **category,
            "display_label": _localized_display_label(category, language),
            "display_label_with_id": _localized_display_label(category, language, include_id=True),
            "display_description": _localized_description(category, language),
        }
        for category in categories
    ]
    lens_catalog = {**lens_catalog, "lenses": lenses, "categories": categories}
    model["lens_catalog"] = lens_catalog
    if isinstance(model.get("session_lens_panel"), dict):
        model["session_lens_panel"] = {**model["session_lens_panel"], "lenses": lenses, "categories": categories}
    discovery = _safe_codex_session_index(config, root)
    table = dict(model.get("session_table") or {})
    enriched_rows: list[dict[str, Any]] = []
    for row in table.get("rows", []) if isinstance(table.get("rows"), list) else []:
        if not isinstance(row, dict):
            continue
        enriched_rows.append(_product_enrich_session_row(row, lenses, categories))
    table["rows"] = _reconcile_product_rows(
        enriched_rows,
        discovery,
        config,
        project_root=root,
        project_default_enabled=extract_project_default(project_status, status_payload),
        lenses=lenses,
        categories=categories,
        language=language,
    )
    supplemental_state_only_rows = list(getattr(_reconcile_product_rows, "_last_supplemental_state_only_rows", []))
    origin_counts: dict[str, int] = {}
    for row in table["rows"]:
        origin = str(row.get("row_origin") or "unknown")
        origin_counts[origin] = origin_counts.get(origin, 0) + 1
    supplemental_state_only_count = len(supplemental_state_only_rows)
    table["row_origin_counts"] = {
        "total": len(table["rows"]),
        "visible_total": len(table["rows"]),
        "registered_matched": origin_counts.get("registered-matched", 0),
        "discovered_only": origin_counts.get("discovered-only", 0),
        "state_only": origin_counts.get("state-only", 0) + supplemental_state_only_count,
        "visible_state_only": origin_counts.get("state-only", 0),
        "supplemental_state_only": supplemental_state_only_count,
        "invalid": sum(1 for row in table["rows"] if not row.get("valid") or row.get("token") != "ok"),
    }
    table["supplemental_state_only_rows"] = supplemental_state_only_rows
    table["default_visibility_policy"] = {
        "show_all_unless_explicitly_hidden": True,
        "name_heuristic_filtering": False,
        "smoke_named_sessions_are_ordinary_without_explicit_metadata": True,
        "discovered_only_sessions_visible": True,
        "state_only_rows_are_supplemental_when_codex_discovery_is_authoritative": True,
        "default_thread_source_filter": "top_level_user_sessions_only",
        "subagent_child_sessions_hidden_from_default_view": True,
    }
    table["codex_session_discovery"] = discovery
    table["invalid_count"] = sum(1 for row in table.get("rows", []) if not row.get("valid") or row.get("token") != "ok")
    model["session_table"] = table

    show_projects = bool(config.get("show_projects_page") or config.get("maintenance_console"))
    target_regions = {"overview": "status_overview_cards", "sessions": "session_table", "workbench": "expert_workbench", "diagnostics": "diagnostics_card", "settings": "settings_panel"}
    nav_items = [{"id": sid, "label": _product_text(sid, language), "target_region": target_regions[sid]} for sid in ["overview", "sessions", "workbench", "diagnostics", "settings"]]
    if show_projects:
        nav_items.insert(3, {"id": "projects", "label": "项目 / Projects", "target_region": "multi_project_panel", "diagnostic_only": True})
    model["navigation_sidebar"] = {"items": nav_items, "projects_page_hidden_by_default": not show_projects}
    model["product_ui"] = {
        "schema_version": SCHEMA_VERSION,
        "shell_contract": "project-moe-gui-product-widgets-v1",
        "primary_shell": "qfluentwidgets-qtwidgets",
        "fallback_shell": "qml-material",
        "target_project_console": True,
        "shows_only_target_project_sessions": True,
        "projects_page_hidden_by_default": not show_projects,
        "language": language,
        "i18n": {
            "schema_version": SCHEMA_VERSION,
            "default_language": "bilingual",
            "active_language": language,
            "language_modes": [
                {"id": "bilingual", "label": "中英对照 / Bilingual"},
                {"id": "zh", "label": "中文"},
                {"id": "en", "label": "English"},
            ],
            "labels": {key: _product_text(key, language) for key in _PRODUCT_I18N},
            "bilingual_format": "中文 / English",
        },
        "session_identity_policy": table["default_visibility_policy"],
        "workbench_executes_carriers": False,
        "sessions_layout_contract": {
            "left_list": "compact_one_line_rows_with_count",
            "right_regions": ["session_details_card", "moe_status_actions_card", "moe_category_lens_selection_card"],
            "full_identity_fields_only_in_detail_card": True,
            "lens_selection_independent_scroll_area": True,
            "category_selection_independent_scroll_area": True,
            "category_lens_selection_layout": "fixed_category_rows_plus_tall_independent_lens_scroll",
            "category_rows_use_tiny_scrollbar": False,
            "lens_selection_minimum_height_px": 220,
            "narrow_width_strategy": "avoid_horizontal_category_lens_splitter",
            "category_lens_i18n": True,
            "category_lens_tri_state_linkage": True,
            "category_clicks_write_lens_ids_for_phase1_compatibility": True,
            "selection_model_empty_selection_means_all": True,
            "left_list_text_source": "compact_list_text",
        },
    }
    model["settings_panel"] = {
        "title": _product_text("settings", language),
        "language": language,
        "language_modes": model["product_ui"]["i18n"]["language_modes"],
        "target_project_only": _product_text("target_project_only", language),
        "writes_business_state": False,
    }
    title_keys = {"project-default": "project_default", "effective-status": "effective_status", "session-count": "session_count", "runtime": "gui_runtime", "visual-shell": "visual_shell"}
    for card in model.get("status_cards", []) if isinstance(model.get("status_cards"), list) else []:
        if not isinstance(card, dict):
            continue
        if card.get("id") in title_keys:
            card["title"] = _product_text(title_keys[str(card["id"])], language)
        if card.get("id") == "visual-shell":
            card["value"] = "QFluentWidgets / Qt Widgets"
        if card.get("id") == "session-count":
            counts = table.get("row_origin_counts") or {}
            card["value"] = str(counts.get("total", len(table.get("rows", []))))
            card["breakdown"] = counts
        card["style"] = "fluent-card"
    model["visual"] = {
        **dict(model.get("visual") or {}),
        "library": "QFluentWidgets / Qt Widgets",
        "style": "Fluent Widgets",
        "primary_shell": "qfluentwidgets-qtwidgets",
        "fallback_shell": "qml-material",
        "product_shell_contract": "project-moe-gui-product-widgets-v1",
        "qfluentwidgets_required": True,
        "qfluentwidgets_status": qfluent_payload,
        "license_manifest": qfluent_payload.get("license_manifest") or qfluent_license_manifest(),
    }
    diagnostics = dict(model.get("diagnostics_card") or {})
    diagnostics["qfluentwidgets"] = qfluent_payload
    diagnostics["product_ui"] = model["product_ui"]
    diagnostics["suggested_next_actions"] = [
        "Use the QFluentWidgets / Qt Widgets shell as the default visible GUI.",
        "Use --preflight --json for automation before visible launch.",
        "Keep Projects hidden for ordinary target projects.",
        "Use Workbench exports as safe handoff packages; GUI does not execute carriers.",
    ]
    model["diagnostics_card"] = diagnostics
    model["window_structure"] = {**dict(model.get("window_structure") or {}), "window_title": _product_text("app_title", language), "product_shell_contract": "project-moe-gui-product-widgets-v1"}
    return model


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
    pyside6_ok = view_model.get("runtime", {}).get("pyside6_status") == "import_ok"
    qfluent_payload = view_model.get("visual", {}).get("qfluentwidgets_status") if isinstance(view_model.get("visual"), dict) else {}
    qfluent_ok = isinstance(qfluent_payload, dict) and qfluent_payload.get("ok") is True
    blockers = [banner for banner in view_model.get("banners", []) if isinstance(banner, dict) and banner.get("token") != "ok"]
    token = "ok" if pyside6_ok and qfluent_ok and not blockers else ("blocked:pyside6_unavailable" if not pyside6_ok else (str((qfluent_payload or {}).get("token") or "blocked:qfluentwidgets_unavailable") if not qfluent_ok else str(blockers[0].get("token"))))
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": token == "ok",
        "token": token,
        "exit_code": 0 if token == "ok" else 5,
        "message": "Project MOE GUI product shell preflight passed." if token == "ok" else "Project MOE GUI product shell preflight found blockers.",
        "gui_shell_contract": GUI_SHELL_CONTRACT,
        "product_shell_contract": "project-moe-gui-product-widgets-v1",
        "view_model": view_model,
        "blockers": blockers + ([] if qfluent_ok else list((qfluent_payload or {}).get("blockers") or [])),
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
        write_contract_errors = validate_write_cli_payload(action, write_payload, expected_session_id=session_id)
    readback: dict[str, Any] = {}
    readback_errors: list[dict[str, Any]] = []
    for read_plan in plan.get("readback_after_write", []):
        read_action = str(read_plan.get("action"))
        read_session_id = session_id if read_action == "status" and action.startswith("session-") else None
        payload, err = run_cli_json(config, read_action, session_id=read_session_id, timeout=timeout, project_root=root)
        readback[read_action] = payload
        if err:
            readback_errors.append(err)
    if action.startswith("session-"):
        status_payload = readback.get("status")
        if not isinstance(status_payload, dict):
            readback_errors.append(
                stable_blocker(
                    "blocked:write_cli_readback_missing_status",
                    "Session write readback must include a status payload for the same session.",
                    action=action,
                    expected=session_id,
                )
            )
        elif str(status_payload.get("session_id")) != str(session_id):
            readback_errors.append(
                stable_blocker(
                    "blocked:write_cli_readback_session_id_mismatch",
                    "Session write readback status must target the same session id as the GUI write.",
                    action=action,
                    expected=session_id,
                    observed=status_payload.get("session_id"),
                )
            )
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


def _qt_check_state(state_name: str) -> Any:
    from PySide6.QtCore import Qt
    if state_name == "checked":
        return Qt.CheckState.Checked
    if state_name == "partial":
        return Qt.CheckState.PartiallyChecked
    return Qt.CheckState.Unchecked


def _compact_visual_label(value: Any, *, max_chars: int = 64) -> str:
    text = str(value or "")
    if len(text) <= max_chars:
        return text
    keep = max(12, (max_chars - 3) // 2)
    return f"{text[:keep]}...{text[-keep:]}"


def create_product_widget_window(
    view_model: dict[str, Any],
    config: dict[str, Any] | None = None,
    project_root: str | Path | None = None,
) -> tuple[Any, Any]:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import qfluentwidgets  # noqa: F401
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSizePolicy, QSplitter, QStackedWidget, QTextEdit, QVBoxLayout, QWidget

    language = (view_model.get("product_ui") or {}).get("language", "bilingual")
    labels = (view_model.get("product_ui") or {}).get("i18n", {}).get("labels", {})

    def L(key: str) -> str:
        return str(labels.get(key) or _product_text(key, language))

    class ProductMoeWindow(QMainWindow):  # pragma: no cover - visible path is smoke-tested
        def __init__(self, vm: dict[str, Any]) -> None:
            super().__init__()
            self.view_model = vm
            self.setObjectName("projectMoeProductWindow")
            self.setWindowTitle(L("app_title"))
            self.resize(1180, 720)
            self._session_rows = list((vm.get("session_table") or {}).get("rows") or [])
            self._lens_rows = list((vm.get("lens_catalog") or {}).get("lenses") or [])
            self._category_rows = list((vm.get("lens_catalog") or {}).get("categories") or [])
            self._lens_checks: dict[str, QCheckBox] = {}
            self._category_checks: dict[str, QCheckBox] = {}
            self._category_lens_map: dict[str, set[str]] = {}
            self._updating_lens_selection = False
            self._lens_selection_dirty = False
            self._current_lens_mode = "all"
            self._build_ui()
            self._select_session(0)

        def _page(self, title: str) -> tuple[QWidget, QVBoxLayout]:
            page = QWidget()
            layout = QVBoxLayout(page)
            header = QLabel(title)
            header.setObjectName("pageHeader")
            header.setWordWrap(True)
            layout.addWidget(header)
            return page, layout

        def _card(self, title: str, value: str, token: str = "ok") -> QFrame:
            frame = QFrame()
            frame.setObjectName("fluentCard")
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            layout = QVBoxLayout(frame)
            for text, name in [(title, "cardTitle"), (value, "cardValue"), (token, "cardToken")]:
                label = QLabel(str(text))
                label.setObjectName(name)
                label.setWordWrap(True)
                layout.addWidget(label)
            return frame

        def _section_frame(self, title: str, object_name: str) -> tuple[QFrame, QVBoxLayout]:
            frame = QFrame()
            frame.setObjectName(object_name)
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            section_layout = QVBoxLayout(frame)
            header = QLabel(title)
            header.setObjectName("cardTitle")
            header.setWordWrap(True)
            section_layout.addWidget(header)
            return frame, section_layout

        def _build_ui(self) -> None:
            self.setStyleSheet('QMainWindow, QWidget { background: #0f172a; color: #e5e7eb; font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif; font-size: 10pt; } QListWidget { background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 4px; color: #e5e7eb; } QListWidget::item { border-radius: 6px; padding: 6px; margin: 2px; } QListWidget::item:selected { background: #2563eb; color: #ffffff; } QFrame#fluentCard, QFrame { background: #111827; border: 1px solid #334155; border-radius: 12px; } QLabel#pageHeader, QLabel#productAppTitle { font-size: 16pt; font-weight: 700; color: #f8fafc; } QLabel#cardTitle { color: #93c5fd; font-weight: 600; } QLabel#cardValue { font-size: 15pt; font-weight: 700; color: #f8fafc; } QLabel#cardToken { color: #cbd5e1; } QLineEdit, QTextEdit, QComboBox { background: #020617; border: 1px solid #334155; border-radius: 8px; padding: 6px; color: #e5e7eb; selection-background-color: #2563eb; } QPushButton { background: #2563eb; border: 1px solid #3b82f6; border-radius: 8px; padding: 7px 10px; color: #ffffff; font-weight: 600; } QPushButton:hover { background: #1d4ed8; } QCheckBox { padding: 3px; color: #e5e7eb; } QScrollArea { border: 0; background: transparent; } QSplitter::handle { background: #1e293b; }')
            central = QWidget()
            root_layout = QHBoxLayout(central)
            root_layout.setContentsMargins(12, 12, 12, 12)
            self.nav = QListWidget()
            self.nav.setFixedWidth(170)
            self.pages = QStackedWidget()
            self.pages.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.section_ids: list[str] = []
            for item in (self.view_model.get("navigation_sidebar") or {}).get("items", []):
                section_id = str(item.get("id"))
                if section_id == "projects":
                    continue
                self.section_ids.append(section_id)
                self.nav.addItem(QListWidgetItem(str(item.get("label") or section_id)))
            self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
            root_layout.addWidget(self.nav)
            root_layout.addWidget(self.pages, 1)
            self.setCentralWidget(central)
            self.pages.addWidget(self._overview_page())
            self.pages.addWidget(self._sessions_page())
            self.pages.addWidget(self._workbench_page())
            self.pages.addWidget(self._diagnostics_page())
            self.pages.addWidget(self._settings_page())
            self.nav.setCurrentRow(0)

        def _overview_page(self) -> QWidget:
            page, layout = self._page(L("overview"))
            app_title = QLabel(L("app_title"))
            app_title.setObjectName("productAppTitle")
            app_title.setWordWrap(True)
            layout.addWidget(app_title)
            banner = self.view_model.get("top_banner") or {}
            project = QLabel(f"{L('target_project_only')}: {banner.get('project_root')}")
            project.setWordWrap(True)
            layout.addWidget(project)
            grid = QGridLayout()
            for index, card in enumerate(self.view_model.get("status_cards", [])):
                grid.addWidget(self._card(str(card.get("title")), str(card.get("value")), str(card.get("token"))), index // 2, index % 2)
            layout.addLayout(grid)
            actions = QHBoxLayout()
            self.enable_project_btn = QPushButton("开启项目默认 / Enable project default")
            self.disable_project_btn = QPushButton("关闭项目默认 / Disable project default")
            self.enable_project_btn.clicked.connect(lambda: self._execute_project_action("project-on"))
            self.disable_project_btn.clicked.connect(lambda: self._execute_project_action("project-off"))
            actions.addWidget(self.enable_project_btn)
            actions.addWidget(self.disable_project_btn)
            actions.addStretch(1)
            layout.addLayout(actions)
            layout.addStretch(1)
            return page

        def _sessions_page(self) -> QWidget:
            page, layout = self._page(L("sessions"))
            splitter = QSplitter(Qt.Orientation.Horizontal)
            left = QWidget()
            left.setMinimumWidth(260)
            left.setMaximumWidth(380)
            left_layout = QVBoxLayout(left)
            left_layout.addWidget(QLabel(L("session_list")))
            self.session_count_label = QLabel()
            self.session_count_label.setObjectName("sessionCountLabel")
            left_layout.addWidget(self.session_count_label)
            self.session_search = QLineEdit()
            self.session_search.setPlaceholderText(L("search_session_placeholder"))
            self.session_search.textChanged.connect(self._refill_session_list)
            self.session_list = QListWidget()
            self.session_list.setWordWrap(False)
            self.session_list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
            self.session_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.session_list.currentRowChanged.connect(self._select_session)
            left_layout.addWidget(self.session_search)
            left_layout.addWidget(self.session_list, 1)
            right = QWidget()
            right.setObjectName("sessionsRightPane")
            right.setMinimumWidth(560)
            self.detail_layout = QVBoxLayout(right)
            self.detail_layout.setContentsMargins(8, 0, 0, 0)
            detail_card, detail_layout = self._section_frame(L("session_details"), "sessionDetailsCard")
            detail_scroll = QScrollArea()
            detail_scroll.setObjectName("sessionDetailsScroll")
            detail_scroll.setWidgetResizable(True)
            detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            detail_scroll.setMinimumHeight(96)
            detail_scroll.setMaximumHeight(118)
            detail_scroll_content = QWidget()
            detail_scroll_layout = QVBoxLayout(detail_scroll_content)
            detail_scroll_layout.setContentsMargins(2, 2, 2, 2)
            detail_scroll_layout.setSpacing(1)
            self.session_field_labels: dict[str, QLabel] = {}
            for field in ["Session", "Created", "Updated", "Directory", "Branch"]:
                label = QLabel()
                label.setObjectName(f"sessionIdentity{field}Field")
                label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                label.setMinimumWidth(0)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                label.setWordWrap(False)
                detail_scroll_layout.addWidget(label)
                self.session_field_labels[field] = label
            self.session_conversation_label = QLabel("Conversation:")
            self.session_conversation_label.setObjectName("sessionIdentityConversationField")
            self.session_conversation_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            self.session_conversation_label.setMinimumWidth(0)
            self.session_conversation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            detail_scroll_layout.addWidget(self.session_conversation_label)
            self.session_conversation = QTextEdit()
            self.session_conversation.setObjectName("sessionConversationPreview")
            self.session_conversation.setReadOnly(True)
            self.session_conversation.setMaximumHeight(46)
            detail_scroll_layout.addWidget(self.session_conversation)
            detail_scroll_layout.addStretch(1)
            detail_scroll.setWidget(detail_scroll_content)
            detail_layout.addWidget(detail_scroll)
            detail_card.setMaximumHeight(158)

            status_card, status_layout = self._section_frame(L("moe_status_actions"), "sessionMoeStatusActionsCard")
            status_card.setMinimumHeight(184)
            status_card.setMaximumHeight(214)
            self.session_mapping = QLabel()
            self.session_why = QLabel()
            self.session_effective = QLabel()
            for widget in [self.session_mapping, self.session_why, self.session_effective]:
                widget.setWordWrap(False)
                widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                widget.setMinimumWidth(0)
                widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                status_layout.addWidget(widget)
            self.effective_lenses_label = QLabel()
            self.effective_lenses_label.setWordWrap(False)
            self.effective_lenses_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            self.effective_lenses_label.setMinimumWidth(0)
            status_layout.addWidget(self.effective_lenses_label)
            actions = QGridLayout()
            buttons = [
                (QPushButton(L("enable_session_moe")), "session-on"),
                (QPushButton(L("disable_session_moe")), "session-off"),
                (QPushButton(L("apply_session_lenses")), "session-set-lenses"),
                (QPushButton(L("clear_session_lenses")), "session-clear-lenses"),
            ]
            for index, (button, action) in enumerate(buttons):
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.setMinimumHeight(32)
                button.clicked.connect(lambda _checked=False, a=action: self._execute_session_action(a))
                actions.addWidget(button, index // 2, index % 2)
            actions.setColumnStretch(0, 1)
            actions.setColumnStretch(1, 1)
            status_layout.addLayout(actions)

            selection_card, selection_layout = self._section_frame(L("moe_lens_selection"), "sessionLensSelectionCard")
            selection_card.setMinimumHeight(240)
            selection_layout.setSpacing(3)
            selection_layout.addWidget(QLabel(L("empty_selection_all")))
            self.category_box = QFrame()
            self.category_box.setObjectName("sessionMoeCategoryBox")
            self.category_box.setFrameShape(QFrame.Shape.StyledPanel)
            self.category_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.category_layout = QVBoxLayout(self.category_box)
            self.category_layout.setSpacing(2)
            self.category_layout.addWidget(QLabel(L("moe_categories")))
            self.lens_box = QFrame()
            self.lens_box.setObjectName("sessionMoeLensBox")
            self.lens_box.setFrameShape(QFrame.Shape.StyledPanel)
            self.lens_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.lens_layout = QVBoxLayout(self.lens_box)
            self.lens_layout.setSpacing(2)
            self.lens_layout.addWidget(QLabel(L("moe_lenses")))
            lens_scroll = QScrollArea()
            lens_scroll.setObjectName("sessionLensIndependentScrollArea")
            lens_scroll.setWidgetResizable(True)
            lens_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            lens_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            lens_scroll.setWidget(self.lens_box)
            self.category_box.setMinimumHeight(124)
            self.category_box.setMaximumHeight(156)
            lens_scroll.setMinimumHeight(220)
            selection_layout.addWidget(self.category_box, 0)
            selection_layout.addWidget(lens_scroll, 1)

            self.detail_layout.addWidget(detail_card, 0)
            self.detail_layout.addWidget(status_card, 0)
            self.detail_layout.addWidget(selection_card, 1)
            splitter.addWidget(left)
            splitter.addWidget(right)
            splitter.setSizes([340, 840])
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            layout.addWidget(splitter, 1)
            self._refill_session_list()
            return page

        def _workbench_page(self) -> QWidget:
            page, layout = self._page(L("workbench"))
            layout.addWidget(QLabel("专家交接台 / Expert Workbench (generated-only, no execution)"))
            layout.addWidget(QLabel("专家镜头 / Expert lenses"))
            self.handoff_target = QComboBox()
            for target in (self.view_model.get("expert_workbench") or {}).get("handoff_targets", []):
                self.handoff_target.addItem(str(target.get("label") or target.get("id")), str(target.get("id")))
            self.brief_text = QTextEdit()
            self.brief_text.setPlaceholderText("Task brief / 任务 brief")
            layout.addWidget(QLabel("交接目标 / Handoff target"))
            layout.addWidget(self.handoff_target)
            layout.addWidget(QLabel("任务 brief / Task brief"))
            layout.addWidget(self.brief_text, 1)
            buttons = QHBoxLayout()
            for text, method in [("复制交接包 / Copy handoff package", self._copy_handoff_package), ("保存草稿 / Save draft", self._save_handoff_draft), ("导出交接包 / Export package", self._export_handoff_package)]:
                button = QPushButton(text)
                button.clicked.connect(method)
                buttons.addWidget(button)
            layout.addLayout(buttons)
            history = QListWidget()
            for item in ((self.view_model.get("expert_workbench") or {}).get("artifact_history") or {}).get("items", []):
                history.addItem(f"{item.get('created_at')} | {item.get('handoff_target')} | {item.get('session_display_id')}")
            layout.addWidget(QLabel("Expert result history / 专家结果历史"))
            layout.addWidget(history)
            return page

        def _diagnostics_page(self) -> QWidget:
            page, layout = self._page(L("diagnostics"))
            text = QTextEdit()
            text.setReadOnly(True)
            text.setPlainText(json.dumps(self.view_model.get("diagnostics_card") or {}, ensure_ascii=False, indent=2))
            layout.addWidget(text, 1)
            return page

        def _settings_page(self) -> QWidget:
            page, layout = self._page(L("settings"))
            layout.addWidget(QLabel("语言 / Language"))
            combo = QComboBox()
            for mode in [{"id": "bilingual", "label": "中英对照 / Bilingual"}, {"id": "zh", "label": "中文"}, {"id": "en", "label": "English"}]:
                combo.addItem(mode["label"], mode["id"])
            layout.addWidget(combo)
            layout.addWidget(QLabel("只显示并控制当前项目会话 / Shows and controls only this target project"))
            for text in ["关闭行为 / Close behavior", "加载态 / Loading state", "空状态 / Empty state", "错误态 / Error state", "帮助 / Help"]:
                layout.addWidget(QLabel(text))
            layout.addStretch(1)
            return page

        def _refill_session_list(self) -> None:
            needle = self.session_search.text().strip().lower() if hasattr(self, "session_search") else ""
            self.session_list.clear()
            self._filtered_rows = []
            for row in self._session_rows:
                full_id = str(row.get("visible_session_id") or row.get("full_session_id") or row.get("session_id") or "")
                conversation = row.get("conversation") if isinstance(row.get("conversation"), dict) else {}
                haystack = " ".join(
                    [
                        full_id,
                        str(row.get("display_id") or ""),
                        str(row.get("directory") or ""),
                        str(row.get("branch") or ""),
                        str(row.get("thread_source") or ""),
                        str(conversation.get("title") or row.get("conversation_title") or ""),
                        str(conversation.get("preview") or row.get("conversation_preview") or ""),
                    ]
                ).lower()
                if needle and needle not in haystack:
                    continue
                self._filtered_rows.append(row)
                block = row.get("session_display_block") if isinstance(row.get("session_display_block"), dict) else build_session_display_block(row)
                item = QListWidgetItem(str(row.get("compact_list_text") or build_compact_session_list_text(row)))
                item.setToolTip(str(block.get("text") or ""))
                self.session_list.addItem(item)
            if hasattr(self, "session_count_label"):
                total = len(self._session_rows)
                shown = len(self._filtered_rows)
                count_word = L("sessions_total")
                self.session_count_label.setText(f"{shown}/{total} {count_word}")
            if self._filtered_rows:
                self.session_list.setCurrentRow(0)

        def _current_session(self) -> dict[str, Any] | None:
            rows = getattr(self, "_filtered_rows", self._session_rows)
            index = self.session_list.currentRow() if hasattr(self, "session_list") else 0
            return rows[index] if 0 <= index < len(rows) else None

        def _select_session(self, _index: int) -> None:
            row = self._current_session()
            if row is None:
                return
            block = row.get("session_display_block") if isinstance(row.get("session_display_block"), dict) else build_session_display_block(row)
            fields = block.get("fields") if isinstance(block.get("fields"), dict) else {}
            for field, label in self.session_field_labels.items():
                value = str(fields.get(field) or "")
                text = f"{field}: {_compact_visual_label(value, max_chars=68)}"
                label.setText(text)
                label.setToolTip(f"{field}: {value}")
            conversation_text = str(fields.get("Conversation") or "")
            self.session_conversation_label.setText("Conversation:")
            self.session_conversation_label.setToolTip("Conversation:")
            self.session_conversation.setPlainText(conversation_text)
            mapping = row.get("codex_mapping") or {}
            mapping_text = f"Codex 映射置信度 / Codex mapping confidence: {mapping.get('confidence', row.get('mapping_confidence', 'unmatched'))} - {mapping.get('message', '')}"
            why_text = f"显示原因 / Why shown: {row.get('why_shown')}"
            effective_text = f"生效状态 / Effective status: {row.get('label')} | {row.get('effective_state_explanation')} | {row.get('override_conflict_hint')}"
            for widget, text in [(self.session_mapping, mapping_text), (self.session_why, why_text), (self.session_effective, effective_text)]:
                widget.setText(_compact_visual_label(text, max_chars=74))
                widget.setToolTip(text)
            self._rebuild_lens_checks(row)

        def _clear_layout(self, layout: QVBoxLayout, keep_first: bool = True) -> None:
            while layout.count() > (1 if keep_first else 0):
                item = layout.takeAt(1 if keep_first else 0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    widget.setParent(None)
                    widget.deleteLater()

        def _rebuild_lens_checks(self, row: dict[str, Any]) -> None:
            self._clear_layout(self.category_layout)
            self._clear_layout(self.lens_layout)
            model = _product_lens_selection_model(self._lens_rows, self._category_rows, row.get("selected_lenses"), row.get("selected_categories"), language=language)
            self._current_lens_mode = str(model.get("mode") or "all")
            self._lens_selection_dirty = False
            self._lens_checks = {}
            self._category_checks = {}
            self._category_lens_map = {}
            self._updating_lens_selection = True
            for category in model.get("categories", []):
                category_id = str(category.get("id"))
                full_label = str(category.get("display_label") or _localized_display_label(category, language))
                description = str(category.get("display_description") or "")
                checkbox = QCheckBox(_compact_visual_label(full_label))
                checkbox.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                checkbox.setMinimumWidth(0)
                checkbox.setToolTip((full_label + ("\n" + description if description else "")).strip())
                checkbox.setTristate(True)
                checkbox.setCheckState(_qt_check_state(str(category.get("check_state") or "unchecked")))
                self._category_checks[category_id] = checkbox
                self._category_lens_map[category_id] = set(category.get("lens_ids") or [])
                self.category_layout.addWidget(checkbox)
            lens_display = {str(item.get("id")): item for item in model.get("lenses", []) if isinstance(item, dict)}
            for lens in self._lens_rows:
                lens_id = str(lens.get("id"))
                display_lens = lens_display.get(lens_id, lens)
                full_label = str(display_lens.get("display_label") or _localized_display_label(display_lens, language))
                description = str(display_lens.get("display_description") or "")
                checkbox = QCheckBox(_compact_visual_label(full_label))
                checkbox.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                checkbox.setMinimumWidth(0)
                checkbox.setToolTip((full_label + ("\n" + description if description else "")).strip())
                checkbox.setChecked(lens_id in set(model.get("effective_lenses") or []))
                self._lens_checks[lens_id] = checkbox
                self.lens_layout.addWidget(checkbox)
            self._updating_lens_selection = False
            for category_id, checkbox in self._category_checks.items():
                checkbox.stateChanged.connect(lambda _state, cid=category_id: self._on_category_state_changed(cid))
            for lens_id, checkbox in self._lens_checks.items():
                checkbox.stateChanged.connect(lambda _state, lid=lens_id: self._on_lens_state_changed(lid))
            lens_text = f"{L('session_moe_lenses')}: {', '.join(model.get('effective_lenses') or []) or 'all'}"
            self.effective_lenses_label.setText(_compact_visual_label(lens_text, max_chars=74))
            self.effective_lenses_label.setToolTip(lens_text)

        def _selected_lenses(self, *, preserve_all_when_pristine: bool = True) -> list[str]:
            if preserve_all_when_pristine and not self._lens_selection_dirty and self._current_lens_mode == "all":
                return []
            return [lens_id for lens_id, checkbox in self._lens_checks.items() if checkbox.isChecked()]

        def _selected_categories(self, *, preserve_all_when_pristine: bool = True) -> list[str]:
            if preserve_all_when_pristine and not self._lens_selection_dirty and self._current_lens_mode == "all":
                return []
            # The visible category layer is now governed display metadata. Target
            # Phase 1 CLIs may still accept legacy category ids, so persisted
            # writes stay lens-id based; category clicks only drive lens checks.
            return []

        def _refresh_effective_lenses_label(self) -> None:
            selected = self._selected_lenses(preserve_all_when_pristine=False)
            lens_text = f"{L('session_moe_lenses')}: {', '.join(selected) if selected else 'all'}"
            self.effective_lenses_label.setText(_compact_visual_label(lens_text, max_chars=74))
            self.effective_lenses_label.setToolTip(lens_text)

        def _on_category_state_changed(self, category_id: str) -> None:
            if self._updating_lens_selection:
                return
            checkbox = self._category_checks.get(category_id)
            if checkbox is None or checkbox.checkState() == Qt.CheckState.PartiallyChecked:
                return
            self._lens_selection_dirty = True
            self._updating_lens_selection = True
            try:
                checked = checkbox.checkState() == Qt.CheckState.Checked
                for lens_id in self._category_lens_map.get(category_id, set()):
                    if str(lens_id) in self._lens_checks:
                        self._lens_checks[str(lens_id)].setChecked(checked)
            finally:
                self._updating_lens_selection = False
            self._sync_category_states_from_lenses()
            self._refresh_effective_lenses_label()

        def _on_lens_state_changed(self, _lens_id: str) -> None:
            if self._updating_lens_selection:
                return
            self._lens_selection_dirty = True
            self._sync_category_states_from_lenses()
            self._refresh_effective_lenses_label()

        def _sync_category_states_from_lenses(self) -> None:
            self._updating_lens_selection = True
            try:
                for category_id, lens_ids in self._category_lens_map.items():
                    checkbox = self._category_checks.get(category_id)
                    if checkbox is None:
                        continue
                    checked_count = sum(1 for lens_id in lens_ids if str(lens_id) in self._lens_checks and self._lens_checks[str(lens_id)].isChecked())
                    if lens_ids and checked_count == len(lens_ids):
                        checkbox.setCheckState(Qt.CheckState.Checked)
                    elif checked_count:
                        checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
                    else:
                        checkbox.setCheckState(Qt.CheckState.Unchecked)
            finally:
                self._updating_lens_selection = False

        def _execute_session_action(self, action: str) -> None:
            row = self._current_session()
            if row is None:
                return
            payload = execute_write_action_with_readback(config or {}, action, session_id=str(row.get("session_id") or ""), selected_lenses=self._selected_lenses(), selected_categories=self._selected_categories(), project_root=project_root or (self.view_model.get("top_banner") or {}).get("project_root"))
            QMessageBox.information(self, "Project MOE", f"{payload.get('token')}: {payload.get('message')}")

        def _execute_project_action(self, action: str) -> None:
            payload = execute_write_action_with_readback(config or {}, action, project_root=project_root or (self.view_model.get("top_banner") or {}).get("project_root"))
            QMessageBox.information(self, "Project MOE", f"{payload.get('token')}: {payload.get('message')}")

        def _workbench_payload_common(self) -> dict[str, Any]:
            row = self._current_session() or {}
            return {"session_id": str(row.get("session_id") or ""), "session_display_id": str(row.get("visible_session_id") or row.get("session_id") or ""), "selected_lenses": self._selected_lenses(), "selected_categories": self._selected_categories(), "handoff_target": str(self.handoff_target.currentData() or "main-session"), "task_template_id": "custom", "brief_text": self.brief_text.toPlainText() if hasattr(self, "brief_text") else ""}

        def _copy_handoff_package(self) -> None:
            payload = export_workbench_handoff_package(config or {}, project_root=project_root, **self._workbench_payload_common())
            QApplication.clipboard().setText(str(payload.get("export_text") or json.dumps(payload.get("package") or {}, ensure_ascii=False, indent=2)))
            QMessageBox.information(self, "Project MOE", f"{payload.get('token')}: copied to clipboard")

        def _save_handoff_draft(self) -> None:
            payload = save_workbench_handoff_draft(config or {}, project_root=project_root, **self._workbench_payload_common())
            QMessageBox.information(self, "Project MOE", f"{payload.get('token')}: {payload.get('message')}")

        def _export_handoff_package(self) -> None:
            payload = export_workbench_handoff_package(config or {}, project_root=project_root, **self._workbench_payload_common())
            QMessageBox.information(self, "Project MOE", f"{payload.get('token')}: {payload.get('message')}")

        def set_selected_section(self, section_id: str) -> None:
            if section_id in self.section_ids:
                self.nav.setCurrentRow(self.section_ids.index(section_id))

        def closeEvent(self, event: Any) -> None:
            box = QMessageBox(self)
            box.setWindowTitle("Close Project MOE GUI?")
            box.setText("Choose whether to exit or hide to tray.")
            exit_button = box.addButton("Exit", QMessageBox.ButtonRole.AcceptRole)
            hide_button = box.addButton("Hide to tray", QMessageBox.ButtonRole.ActionRole)
            box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() is exit_button:
                event.accept()
            elif box.clickedButton() is hide_button:
                self.hide()
                event.ignore()
            else:
                event.ignore()

    app = QApplication.instance() or QApplication([])
    window = ProductMoeWindow(view_model)
    return app, window


def _launch_product_widgets(view_model: dict[str, Any], config: dict[str, Any] | None = None, project_root: str | Path | None = None) -> int:
    from PySide6.QtCore import QTimer

    app, window = create_product_widget_window(view_model, config, project_root)
    smoke_exit_ms = int(os.environ.get("PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS") or "0")
    if smoke_exit_ms > 0:
        timer = QTimer(window)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: app.exit(0))
        window._project_moe_gui_smoke_timer = timer  # type: ignore[attr-defined]
        timer.start(smoke_exit_ms)
    window.show()
    return int(app.exec())


def launch_visible(view_model: dict[str, Any], config: dict[str, Any] | None = None, project_root: str | Path | None = None) -> int:
    if os.environ.get("PROJECT_MOE_GUI_USE_QML_FALLBACK") != "1":
        return _launch_product_widgets(view_model, config, project_root)
    return _legacy_launch_visible_qml(view_model, config, project_root)


def launch_visible_qml_fallback(view_model: dict[str, Any], config: dict[str, Any] | None = None, project_root: str | Path | None = None) -> int:
    return _legacy_launch_visible_qml(view_model, config, project_root)


def _legacy_launch_visible_qml(view_model: dict[str, Any], config: dict[str, Any] | None = None, project_root: str | Path | None = None) -> int:
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

        @Slot(str, str, str, str, str, str, str, result=str)
        def saveHandoffDraft(
            self,
            session_id: str,
            session_display_id: str,
            selected_lenses_json: str,
            selected_categories_json: str,
            handoff_target: str,
            task_template_id: str,
            brief_text: str,
        ) -> str:
            try:
                payload = save_workbench_handoff_draft(
                    self._config,
                    session_id=str(session_id or "") or None,
                    session_display_id=str(session_display_id or "") or None,
                    selected_lenses=parse_json_string_list(selected_lenses_json),
                    selected_categories=parse_json_string_list(selected_categories_json),
                    handoff_target=str(handoff_target or "main-session"),
                    task_template_id=str(task_template_id or "default"),
                    brief_text=str(brief_text or ""),
                    project_root=self._root,
                )
            except Exception as exc:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "ok": False,
                    "token": "blocked:workbench_draft_save_failed",
                    "action": "save_handoff_draft",
                    "message": "Workbench draft save failed.",
                    "errors": [{"code": "blocked:workbench_draft_save_failed", "message": str(exc)}],
                }
            return json.dumps(payload, ensure_ascii=False)

        @Slot(str, str, str, str, str, str, str, result=str)
        def exportHandoffPackage(
            self,
            session_id: str,
            session_display_id: str,
            selected_lenses_json: str,
            selected_categories_json: str,
            handoff_target: str,
            task_template_id: str,
            brief_text: str,
        ) -> str:
            try:
                payload = export_workbench_handoff_package(
                    self._config,
                    session_id=str(session_id or "") or None,
                    session_display_id=str(session_display_id or "") or None,
                    selected_lenses=parse_json_string_list(selected_lenses_json),
                    selected_categories=parse_json_string_list(selected_categories_json),
                    handoff_target=str(handoff_target or "main-session"),
                    task_template_id=str(task_template_id or "default"),
                    brief_text=str(brief_text or ""),
                    project_root=self._root,
                )
            except Exception as exc:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "ok": False,
                    "token": "blocked:workbench_export_failed",
                    "action": "export_handoff_package",
                    "message": "Workbench handoff export failed.",
                    "errors": [{"code": "blocked:workbench_export_failed", "message": str(exc)}],
                }
            return json.dumps(payload, ensure_ascii=False)

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
