#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "skills2cli_profile_routing"
REGISTRY_RELATIVE = Path("tools/skill_sources/plugin-modules/references/profiles.json")
INSTALL_RELATIVE = Path("skills/plugin-modules/references/profiles.json")
REQUIRED_PROFILES = {"core-dev", "web-saas", "company-ops", "market-research", "customer-comms", "creative-content", "pyside6-gui", "full"}
REQUIRED_TOP_LEVEL_FIELDS = ("scenario_description", "route_when", "negative_examples", "load_policy", "plugin_hints", "skill_doc_hints", "ranking_signals")
REQUIRED_TASK_FIELDS = ("scenario_description", "route_when", "negative_examples", "load_policy", "plugin_hints", "skill_doc_hints", "routing_explanation", "ranking_signals")
TROUBLESHOOTING_TERMS = ("all plugins", "full profile", "troubleshoot", "broad discovery", "diagnose missing plugin")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return [value]


def truthy_list(value: Any) -> bool:
    return any(str(item).strip() for item in as_list(value))


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
    if isinstance(value, str) and value != "all_known_plugins":
        if value.strip():
            out.add(value.strip())


def validate_registry(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    registry_path = root / REGISTRY_RELATIVE
    registry: dict[str, Any] = {}
    if not registry_path.exists():
        errors.append(f"Missing profile registry: {REGISTRY_RELATIVE.as_posix()}")
    else:
        try:
            registry = read_json(registry_path)
        except json.JSONDecodeError as exc:
            errors.append(f"profiles.json is invalid JSON: {exc}")
            registry = {}
    modules = registry.get("modules") if isinstance(registry.get("modules"), dict) else {}
    scenarios = registry.get("scenario_profiles") if isinstance(registry.get("scenario_profiles"), dict) else {}
    known_plugins = [str(item) for item in as_list(registry.get("known_plugins")) if str(item).strip()]

    missing = REQUIRED_PROFILES.difference(modules.keys())
    for profile in sorted(missing):
        errors.append(f"profiles.json missing canonical profile `{profile}`.")

    for profile_id, entry in modules.items():
        if not isinstance(entry, dict):
            errors.append(f"Profile `{profile_id}` must be an object.")
            continue
        for field in REQUIRED_TOP_LEVEL_FIELDS:
            if field == "plugin_hints" and profile_id == "pyside6-gui":
                continue
            if field == "skill_doc_hints" and profile_id == "full":
                continue
            if not truthy_list(entry.get(field)):
                errors.append(f"Profile `{profile_id}` missing routing field `{field}`.")
        if profile_id != "full":
            task_modules = entry.get("task_modules")
            if not isinstance(task_modules, dict) or not task_modules:
                errors.append(f"Profile `{profile_id}` must define at least one task module.")
            for task_id, task_entry in (task_modules or {}).items():
                if not isinstance(task_entry, dict):
                    errors.append(f"Task module `{profile_id}.{task_id}` must be an object.")
                    continue
                for field in REQUIRED_TASK_FIELDS:
                    if field == "plugin_hints" and profile_id == "pyside6-gui":
                        continue
                    if not truthy_list(task_entry.get(field)):
                        errors.append(f"Task module `{profile_id}.{task_id}` missing field `{field}`.")
        else:
            if (entry.get("task_modules") or {}) != {}:
                errors.append("Profile `full` must not define normal task modules.")
            if str(entry.get("load_policy")) != "troubleshooting-only":
                errors.append("Profile `full` load_policy must be troubleshooting-only.")

    for scenario_id, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            errors.append(f"Scenario profile `{scenario_id}` must be an object.")
            continue
        target = str(scenario.get("target_profile") or "")
        if target not in modules:
            errors.append(f"Scenario profile `{scenario_id}` target_profile `{target}` does not resolve to a canonical profile.")
        if scenario_id in modules:
            errors.append(f"Scenario profile `{scenario_id}` must not shadow a canonical hard-load profile ID.")
        for field in ("scenario_description", "route_when", "negative_examples", "load_policy", "ranking_signals"):
            if not truthy_list(scenario.get(field)):
                errors.append(f"Scenario profile `{scenario_id}` missing field `{field}`.")

    non_full_coverage: set[str] = set()
    for profile_id, entry in modules.items():
        if profile_id == "full":
            continue
        collect_plugins(entry, non_full_coverage)
    allow = registry.get("allow_full_only_plugins") if isinstance(registry.get("allow_full_only_plugins"), dict) else {}
    for plugin in known_plugins:
        if plugin in non_full_coverage:
            continue
        reason = allow.get(plugin)
        if not reason:
            errors.append(f"Known plugin `{plugin}` is reachable only through `full` without an allowlist reason.")

    full_entry = modules.get("full") if isinstance(modules.get("full"), dict) else {}
    full_terms = " ".join(str(item).lower() for item in as_list(full_entry.get("route_when")) + as_list(full_entry.get("scenario_description")))
    if not any(term in full_terms for term in TROUBLESHOOTING_TERMS):
        errors.append("Profile `full` must be described as troubleshooting-only broad discovery.")

    installed_path = Path.home() / ".codex" / INSTALL_RELATIVE
    drift_reported = False
    if installed_path.exists() and registry_path.exists():
        drift_reported = not filecmp.cmp(registry_path, installed_path, shallow=False)
        if drift_reported:
            warnings.append("Installed user-level plugin-modules profiles.json differs from repo source; report drift before treating installed copy as current.")
    else:
        info.append("Installed user-level plugin-modules profiles.json not found; source registry remains authoritative.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "registry": str(registry_path),
        "installed_copy": str(installed_path),
        "installed_copy_drift_reported": drift_reported,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "profiles": len(modules),
            "scenario_profiles": len(scenarios),
            "known_plugins": len(known_plugins),
            "non_full_plugin_coverage": len(non_full_coverage),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skills2cli scenario profile routing registry contract.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = validate_registry(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("Skills2CLI profile routing check passed." if payload["ok"] else "Skills2CLI profile routing check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        for warning in payload["warnings"]:
            print(f"  - warning: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
