#!/usr/bin/env python3
"""Shared Skills2CLI profile-routing registry contract.

This module intentionally centralizes only stable schema, path, alias, and
accessor contracts.  It does not own runtime ranking/scoring and it does not
own checker black-box smoke behavior; those surfaces must stay independently
verifiable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

PROFILE_REGISTRY_RELATIVE = Path("tools/skill_sources/plugin-modules/references/profiles.json")
INSTALLED_PROFILE_REGISTRY_RELATIVE = Path("skills/plugin-modules/references/profiles.json")
PLUGIN_MODULES_SKILL_RELATIVE = Path("tools/skill_sources/plugin-modules")
SKILLS2CLI_RELATIVE = Path("tools/skills2cli.py")

CANONICAL_PROFILE_IDS = (
    "core-dev",
    "web-saas",
    "company-ops",
    "market-research",
    "customer-comms",
    "creative-content",
    "pyside6-gui",
    "full",
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "scene_description",
    "scenario_description",
    "route_when",
    "negative_examples",
    "load_policy",
    "plugin_hints",
    "skill_doc_hints",
    "ranking_signals",
)

REQUIRED_TASK_FIELDS = (
    "scene_description",
    "scenario_description",
    "route_when",
    "negative_examples",
    "load_policy",
    "plugin_hints",
    "skill_doc_hints",
    "routing_explanation",
    "ranking_signals",
)

REQUIRED_SCENARIO_FIELDS = (
    "scene_description",
    "scenario_description",
    "route_when",
    "negative_examples",
    "load_policy",
    "ranking_signals",
)

# Runtime compatibility aliases.  The registry remains the primary source for
# scenario/profile route terms; these terms preserve existing user-facing
# triggers and are intentionally shared by runtime and checkers.
EXPLICIT_FULL_COMPAT_TERMS = (
    "full profile",
    "all plugins",
    "all-plugin",
    "all plugin",
    "troubleshoot all plugins",
    "diagnose missing plugin capability",
    "broad discovery",
    "排障所有插件",
    "全部插件",
    "完整 profile",
)


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def truthy_list(value: Any) -> bool:
    return any(str(item).strip() for item in as_string_list(value))


def unique_strings(values: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        item = str(value).strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def read_profile_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"modules": {}, "scenario_profiles": {}, "known_plugins": [], "_registry_source": str(path)}
    payload["_registry_source"] = str(path)
    return payload


def load_profile_registry(
    repo_root: Path,
    codex_home: Path | None = None,
    *,
    script_dir: Path | None = None,
    default_codex_home: Path | None = None,
) -> dict[str, Any]:
    candidates: list[Path] = [repo_root / PROFILE_REGISTRY_RELATIVE]
    if script_dir is not None:
        candidates.append(script_dir / "references" / "profiles.json")
    if codex_home is not None:
        candidates.append(codex_home / INSTALLED_PROFILE_REGISTRY_RELATIVE)
    if default_codex_home is not None:
        candidates.append(default_codex_home / INSTALLED_PROFILE_REGISTRY_RELATIVE)
    for path in candidates:
        try:
            if path.exists():
                return read_profile_registry(path)
        except (OSError, json.JSONDecodeError):
            continue
    return {"modules": {}, "scenario_profiles": {}, "known_plugins": [], "_registry_source": None}


def scene_description(entry: dict[str, Any] | None) -> str:
    """Return canonical scene text while preserving legacy alias fallback."""

    if not isinstance(entry, dict):
        return ""
    return str(entry.get("scene_description") or entry.get("scenario_description") or "")


def plugin_hints(entry: dict[str, Any] | None, *, limit: int | None = 12) -> list[str]:
    if not isinstance(entry, dict):
        return []
    hints = as_string_list(entry.get("plugin_hints"))
    if not hints:
        hints = [item for item in as_string_list(entry.get("plugins")) if item != "all_known_plugins"]
    result = unique_strings(hints)
    return result[:limit] if limit is not None else result


def skill_doc_hints(
    entry: dict[str, Any] | None,
    *,
    merge_soft_load: bool = True,
    limit: int | None = 12,
) -> list[str]:
    if not isinstance(entry, dict):
        return []
    hints = as_string_list(entry.get("skill_doc_hints"))
    if merge_soft_load:
        soft_load = entry.get("soft_load") if isinstance(entry.get("soft_load"), dict) else {}
        hints.extend(as_string_list(soft_load.get("skill_doc_hints")))
    result = unique_strings(hints)
    return result[:limit] if limit is not None else result


def collect_plugins(value: Any, out: set[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for key in ("plugins", "plugin_hints", "enable_plugins"):
            collect_plugins(value.get(key), out)
        for child_key in ("hard_load", "soft_load", "task_modules"):
            collect_plugins(value.get(child_key), out)
        return
    if isinstance(value, list):
        for item in value:
            collect_plugins(item, out)
        return
    if isinstance(value, str):
        item = value.strip()
        if item and item != "all_known_plugins":
            out.add(item)


def explicit_full_terms(registry: dict[str, Any] | None = None) -> tuple[str, ...]:
    values: list[Any] = [*EXPLICIT_FULL_COMPAT_TERMS]
    if isinstance(registry, dict):
        modules = registry.get("modules") if isinstance(registry.get("modules"), dict) else {}
        scenarios = registry.get("scenario_profiles") if isinstance(registry.get("scenario_profiles"), dict) else {}
        full_entry = modules.get("full") if isinstance(modules.get("full"), dict) else {}
        troubleshooting = scenarios.get("troubleshooting") if isinstance(scenarios.get("troubleshooting"), dict) else {}
        for entry in (full_entry, troubleshooting):
            values.extend(as_string_list(entry.get("route_when")))
            values.extend(as_string_list(entry.get("positive_examples")))
            values.extend(as_string_list(entry.get("scene_description")))
            values.extend(as_string_list(entry.get("scenario_description")))
    return tuple(item.lower() for item in unique_strings(values))


def is_explicit_full_request(query_text: str, registry: dict[str, Any] | None = None) -> bool:
    lowered = str(query_text).lower()
    return any(term and term in lowered for term in explicit_full_terms(registry))
