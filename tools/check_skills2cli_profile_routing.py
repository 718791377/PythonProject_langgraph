#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import subprocess
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "skills2cli_profile_routing"
REGISTRY_RELATIVE = Path("tools/skill_sources/plugin-modules/references/profiles.json")
INSTALL_RELATIVE = Path("skills/plugin-modules/references/profiles.json")
SKILLS2CLI_RELATIVE = Path("tools/skills2cli.py")
AUDIT_MEMORY_RELATIVE = Path("docs_bilingual/memory")
REQUIRED_PROFILES = {"core-dev", "web-saas", "company-ops", "market-research", "customer-comms", "creative-content", "pyside6-gui", "full"}
REQUIRED_TOP_LEVEL_FIELDS = ("scene_description", "scenario_description", "route_when", "negative_examples", "load_policy", "plugin_hints", "skill_doc_hints", "ranking_signals")
REQUIRED_TASK_FIELDS = ("scene_description", "scenario_description", "route_when", "negative_examples", "load_policy", "plugin_hints", "skill_doc_hints", "routing_explanation", "ranking_signals")
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
        for field in ("scene_description", "scenario_description", "route_when", "negative_examples", "load_policy", "ranking_signals"):
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
    full_terms = " ".join(
        str(item).lower()
        for item in as_list(full_entry.get("route_when"))
        + as_list(full_entry.get("scene_description"))
        + as_list(full_entry.get("scenario_description"))
    )
    if not any(term in full_terms for term in TROUBLESHOOTING_TERMS):
        errors.append("Profile `full` must be described as troubleshooting-only broad discovery.")

    profile_suggest_contract: dict[str, Any] = {
        "checked": False,
        "ok": False,
        "sanitized_audit_summaries_available": False,
        "audit_strong_evidence_available": False,
        "warning_pressure_available": False,
        "warning_pressure_penalty_applied_to_full": False,
        "error": None,
    }
    skills2cli = root / SKILLS2CLI_RELATIVE
    audit_summary_available = bool(list((root / AUDIT_MEMORY_RELATIVE).glob("skills_usage_audit_30d_summary_*.md"))) if (root / AUDIT_MEMORY_RELATIVE).exists() else False
    profile_suggest_contract["sanitized_audit_summaries_available"] = audit_summary_available
    if skills2cli.exists() and registry_path.exists():
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(skills2cli),
                    "profile",
                    "suggest",
                    "--query",
                    "Fix GitLab CI and perform security review",
                    "--root",
                    str(root),
                    "--json",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
            profile_suggest_contract["checked"] = True
            if completed.returncode != 0:
                profile_suggest_contract["error"] = f"profile_suggest_failed:{completed.returncode}"
                errors.append("skills2cli profile suggest smoke failed while checking audit/warning rerank contract.")
            else:
                suggestion = json.loads(completed.stdout)
                ranking_inputs = suggestion.get("ranking_inputs") if isinstance(suggestion, dict) else {}
                selected = suggestion.get("selected_profile") if isinstance(suggestion, dict) else {}
                profile_suggest_contract["audit_strong_evidence_available"] = bool(
                    ranking_inputs.get("audit_strong_evidence_available")
                )
                profile_suggest_contract["warning_pressure_available"] = bool(ranking_inputs.get("warning_pressure_available"))
                profile_suggest_contract["warning_pressure_penalty_applied_to_full"] = bool(
                    ranking_inputs.get("warning_pressure_penalty_applied_to_full")
                )
                base_contract_ok = bool(
                    "audit_strong_evidence_available" in ranking_inputs
                    and "warning_pressure" in ranking_inputs
                    and selected.get("target_profile") != "full"
                    and truthy_list(selected.get("plugin_hints"))
                    and truthy_list(selected.get("skill_doc_hints"))
                    and suggestion.get("mutates_config") is False
                    and suggestion.get("profile_apply_performed") is False
                )
                evidence_contract_ok = bool(
                    not audit_summary_available
                    or (
                        ranking_inputs.get("audit_evidence_sources")
                        and ranking_inputs.get("warning_pressure_available")
                        and ranking_inputs.get("warning_pressure_penalty_applied_to_full")
                    )
                )
                profile_suggest_contract["ok"] = base_contract_ok and evidence_contract_ok
                if not profile_suggest_contract["ok"]:
                    errors.append("skills2cli profile suggest must report audit/warning rerank contract, profile-level hints, non-full ordinary top-1, and preview-only safety.")
                if profile_suggest_contract["audit_strong_evidence_available"] is False:
                    warnings.append("No strong audit evidence was available in sanitized summaries; rerank still reports source availability and policy.")
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            profile_suggest_contract["checked"] = True
            profile_suggest_contract["error"] = f"{exc.__class__.__name__}"
            errors.append("skills2cli profile suggest audit/warning rerank contract check could not run.")
    else:
        warnings.append("skills2cli.py or profiles.json missing; skipped profile suggest rerank contract smoke.")

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
        "profile_suggest_rerank_contract": profile_suggest_contract,
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
