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

from skills2cli_profile_registry_contract import (
    CANONICAL_PROFILE_IDS,
    INSTALLED_PROFILE_REGISTRY_RELATIVE,
    ORTHOGONAL_SCOPE_FIELDS,
    PROFILE_REGISTRY_RELATIVE,
    REQUIRED_SCENARIO_FIELDS,
    REQUIRED_TASK_FIELDS,
    REQUIRED_TOP_LEVEL_FIELDS,
    SKILLS2CLI_RELATIVE,
    as_string_list,
    collect_plugins,
    entry_scope_mismatches,
    explicit_full_terms,
    installed_artifact_surface_paths,
    task_module_identity,
    truthy_list,
)

CHECK_NAME = "skills2cli_profile_routing"
AUDIT_MEMORY_RELATIVE = Path("docs_bilingual/memory")
REQUIRED_PROFILES = set(CANONICAL_PROFILE_IDS)

PROFILE_SUGGEST_SMOKE_MATRIX = (
    {
        "name": "core-dev-ci-security",
        "query": "Fix GitLab CI and perform security review",
        "target_profile": "core-dev",
        "task_modules": {"code-review", "security-review"},
        "explicit_full": False,
    },
    {
        "name": "core-dev-browser",
        "query": "Debug Chrome DevTools and CDP browser automation warnings",
        "target_profile": "core-dev",
        "scenario_profile": "browser-automation",
        "task_modules": {"browser-verification"},
        "explicit_full": False,
    },
    {
        "name": "core-dev-skills-budget-warning",
        "query": "Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.",
        "target_profile": "core-dev",
        "scenario_profile": "skills-budget-triage",
        "task_modules": {"skills-budget-triage"},
        "explicit_full": False,
        "budget_warning_intent": True,
    },
    {
        "name": "web-saas-mobile-observability",
        "query": "Expo mobile build and Sentry observability",
        "target_profile": "web-saas",
        "task_modules": {"mobile-app", "observability"},
        "explicit_full": False,
    },
    {
        "name": "customer-comms-messaging",
        "query": "Twilio WhatsApp customer notification",
        "target_profile": "customer-comms",
        "task_modules": {"messaging"},
        "explicit_full": False,
    },
    {
        "name": "company-ops-meeting-crm",
        "query": "Fireflies meeting notes and HubSpot CRM follow-up",
        "target_profile": "company-ops",
        "task_modules": {"meeting-intel", "crm-workflow"},
        "explicit_full": False,
    },
    {
        "name": "market-research-paper-report",
        "query": "PitchBook market research and Zotero paper citation report",
        "target_profile": "market-research",
        "task_modules": {"paper-citation", "company-research"},
        "explicit_full": False,
    },
    {
        "name": "creative-content-brand-assets",
        "query": "Canva Figma presentation video brand assets",
        "target_profile": "creative-content",
        "task_modules": {"brand-assets", "design-generation"},
        "explicit_full": False,
    },
    {
        "name": "pyside6-gui-packaging",
        "query": "PySide6 Qt desktop GUI packaging preflight",
        "target_profile": "pyside6-gui",
        "task_modules": {"qt-gui-dev", "gui-packaging-preflight"},
        "explicit_full": False,
    },
    {
        "name": "explicit-full-troubleshooting",
        "query": "Troubleshoot all plugins with full profile broad discovery",
        "target_profile": "full",
        "scenario_profile": "troubleshooting",
        "task_modules": set(),
        "explicit_full": True,
    },
    {
        "name": "explicit-full-zh",
        "query": "排障所有插件",
        "target_profile": "full",
        "scenario_profile": "troubleshooting",
        "task_modules": set(),
        "explicit_full": True,
    },
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    return list(as_string_list(value))


def file_sha256(path: Path) -> str | None:
    try:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def build_installed_artifact_report(root: Path) -> list[dict[str, Any]]:
    codex_home = Path.home() / ".codex"
    report: list[dict[str, Any]] = []
    for name, paths in installed_artifact_surface_paths(root, codex_home).items():
        repo_path = Path(paths["repo_path"])
        installed_path = Path(paths["installed_path"])
        repo_hash = file_sha256(repo_path)
        installed_hash = file_sha256(installed_path)
        item: dict[str, Any] = {
            "artifact": name,
            "repo_path": str(repo_path),
            "installed_path": str(installed_path),
            "repo_exists": repo_hash is not None,
            "installed_exists": installed_hash is not None,
            "hash_equal": bool(repo_hash and installed_hash and repo_hash == installed_hash),
            "drift_reported": bool(repo_hash and installed_hash and repo_hash != installed_hash),
        }
        if "plugin_modules_installed_path" in paths:
            plugin_modules_path = Path(paths["plugin_modules_installed_path"])
            plugin_modules_hash = file_sha256(plugin_modules_path)
            item["plugin_modules_installed_path"] = str(plugin_modules_path)
            item["plugin_modules_installed_exists"] = plugin_modules_hash is not None
            item["plugin_modules_hash_equal"] = bool(repo_hash and plugin_modules_hash and repo_hash == plugin_modules_hash)
            item["plugin_modules_drift_reported"] = bool(repo_hash and plugin_modules_hash and repo_hash != plugin_modules_hash)
        report.append(item)
    return report


def validate_registry(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    registry_path = root / PROFILE_REGISTRY_RELATIVE
    registry: dict[str, Any] = {}
    if not registry_path.exists():
        errors.append(f"Missing profile registry: {PROFILE_REGISTRY_RELATIVE.as_posix()}")
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
        for mismatch in entry_scope_mismatches(entry):
            errors.append(
                f"Profile `{profile_id}` orthogonal scope `{mismatch['field']}` expected `{mismatch['expected']}` but found `{mismatch['actual']}`."
            )
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
                identity = task_module_identity(str(profile_id), str(task_id), task_entry)
                if not identity["declared_matches_expected"]:
                    errors.append(
                        f"Task module `{profile_id}.{task_id}` qualified_name must be `{identity['expected_qualified_name']}`."
                    )
                for mismatch in entry_scope_mismatches(task_entry):
                    errors.append(
                        f"Task module `{profile_id}.{task_id}` orthogonal scope `{mismatch['field']}` expected `{mismatch['expected']}` but found `{mismatch['actual']}`."
                    )
        else:
            if (entry.get("task_modules") or {}) != {}:
                errors.append("Profile `full` must not define normal task modules.")
            if str(entry.get("load_policy")) != "troubleshooting-only":
                errors.append("Profile `full` load_policy must be troubleshooting-only.")
            if entry.get("explicit_full_request_required") is not True:
                errors.append("Profile `full` must declare explicit_full_request_required=true.")

    for scenario_id, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            errors.append(f"Scenario profile `{scenario_id}` must be an object.")
            continue
        target = str(scenario.get("target_profile") or "")
        if target not in modules:
            errors.append(f"Scenario profile `{scenario_id}` target_profile `{target}` does not resolve to a canonical profile.")
        if scenario_id in modules:
            errors.append(f"Scenario profile `{scenario_id}` must not shadow a canonical hard-load profile ID.")
        for field in REQUIRED_SCENARIO_FIELDS:
            if not truthy_list(scenario.get(field)):
                errors.append(f"Scenario profile `{scenario_id}` missing field `{field}`.")
        for mismatch in entry_scope_mismatches(scenario):
            errors.append(
                f"Scenario profile `{scenario_id}` orthogonal scope `{mismatch['field']}` expected `{mismatch['expected']}` but found `{mismatch['actual']}`."
            )

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
    full_terms = set(explicit_full_terms(registry))
    for term in ("all plugins", "full profile", "troubleshoot all plugins", "diagnose missing plugin capability", "broad discovery"):
        if term not in full_terms:
            errors.append(f"Profile `full` explicit-trigger contract missing term `{term}`.")
    if not any(term in full_terms for term in ("all plugins", "full profile", "troubleshoot all plugins")):
        errors.append("Profile `full` must be described as troubleshooting-only broad discovery.")

    budget_task = (modules.get("core-dev") or {}).get("task_modules", {}).get("skills-budget-triage")
    budget_scenario = scenarios.get("skills-budget-triage")
    required_budget_terms = {
        "skills context budget",
        "Exceeded skills context budget",
        "All skill descriptions were removed",
        "additional skills were not included",
        "compaction",
        "model-visible skills list",
    }
    required_budget_visibility_terms = {
        "skills2cli visibility plan",
        "skills2cli visibility apply",
        "skills2cli visibility restore",
        "standalone visibility reduction",
        "receipt-backed visibility reduction",
    }
    if not isinstance(budget_task, dict):
        errors.append("Missing required task module `core-dev.skills-budget-triage` for budget warning triage.")
    else:
        identity = task_module_identity("core-dev", "skills-budget-triage", budget_task)
        if not identity["declared_matches_expected"]:
            errors.append("Task module `core-dev.skills-budget-triage` must declare qualified_name `core-dev.skills-budget-triage`.")
        task_terms = set(as_list(budget_task.get("route_when"))) | set(as_list(budget_task.get("positive_examples"))) | set(as_list((budget_task.get("soft_load") or {}).get("use_for")))
        missing_terms = sorted(term for term in required_budget_terms if term not in task_terms)
        if missing_terms:
            errors.append(f"Task module `core-dev.skills-budget-triage` missing budget route terms: {', '.join(missing_terms)}.")
        missing_visibility_terms = sorted(term for term in required_budget_visibility_terms if term not in task_terms)
        if missing_visibility_terms:
            errors.append(
                "Task module `core-dev.skills-budget-triage` missing standalone visibility reduction terms: "
                + ", ".join(missing_visibility_terms)
                + "."
            )
        task_text = json.dumps(budget_task, ensure_ascii=False).lower()
        if "do not mutate user-level config" not in task_text and "do not mutate user-level" not in task_text:
            errors.append("Task module `core-dev.skills-budget-triage` must forbid profile suggest from mutating user-level config.")
        if "hard-load previews" not in task_text or "do not solve standalone user-skill pressure" not in task_text:
            errors.append("Task module `core-dev.skills-budget-triage` must state plugin hard-load is not the primary standalone-skill fix.")
    if not isinstance(budget_scenario, dict):
        errors.append("Missing required scenario profile `skills-budget-triage`.")
    else:
        if budget_scenario.get("target_profile") != "core-dev":
            errors.append("Scenario profile `skills-budget-triage` must target `core-dev`.")
        if "skills-budget-triage" not in as_list(budget_scenario.get("default_task_modules")):
            errors.append("Scenario profile `skills-budget-triage` must default to task module `skills-budget-triage`.")

    profile_suggest_contract: dict[str, Any] = {
        "checked": False,
        "ok": False,
        "matrix": [],
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
            profile_suggest_contract["checked"] = True
            matrix_ok = True
            first_suggestion: dict[str, Any] | None = None
            for case in PROFILE_SUGGEST_SMOKE_MATRIX:
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(skills2cli),
                        "profile",
                        "suggest",
                        "--query",
                        str(case["query"]),
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
                row: dict[str, Any] = {"name": case["name"], "query": case["query"], "ok": False}
                if completed.returncode != 0:
                    row["error"] = f"profile_suggest_failed:{completed.returncode}"
                    matrix_ok = False
                    profile_suggest_contract["matrix"].append(row)
                    continue
                suggestion = json.loads(completed.stdout)
                if first_suggestion is None:
                    first_suggestion = suggestion
                selected = suggestion.get("selected_profile") if isinstance(suggestion, dict) else {}
                task_modules = {
                    str(item.get("task_module"))
                    for item in suggestion.get("task_modules", [])
                    if isinstance(item, dict) and item.get("task_module")
                }
                expected_tasks = set(case.get("task_modules", set()))
                expected_profile = str(case["target_profile"])
                row.update(
                    {
                        "selected_profile": selected.get("target_profile"),
                        "scenario_profile": selected.get("scenario_profile"),
                        "task_modules": sorted(task_modules),
                        "explicit_full_request": suggestion.get("explicit_full_request"),
                        "budget_warning_intent": suggestion.get("budget_warning_intent"),
                        "skill_layer_pressure": suggestion.get("skill_layer_pressure"),
                        "excluded_candidates": suggestion.get("excluded_candidates", []),
                    }
                )
                ok = bool(
                    selected.get("target_profile") == expected_profile
                    and expected_tasks.issubset(task_modules)
                    and suggestion.get("mutates_config") is False
                    and suggestion.get("edits_plugin_cache") is False
                    and suggestion.get("profile_apply_performed") is False
                    and suggestion.get("approval_required_for_apply") is True
                )
                if case.get("scenario_profile"):
                    ok = ok and selected.get("scenario_profile") == case.get("scenario_profile")
                if case.get("budget_warning_intent"):
                    budget_intent = suggestion.get("budget_warning_intent") if isinstance(suggestion, dict) else {}
                    layer_pressure = suggestion.get("skill_layer_pressure") if isinstance(suggestion, dict) else {}
                    ok = (
                        ok
                        and isinstance(budget_intent, dict)
                        and budget_intent.get("detected") is True
                        and budget_intent.get("target_profile") == "core-dev"
                        and selected.get("target_profile") == "core-dev"
                        and selected.get("scenario_profile") == "skills-budget-triage"
                        and "skills-budget-triage" in task_modules
                        and isinstance(layer_pressure, dict)
                        and layer_pressure.get("available") is True
                    )
                if not case.get("explicit_full"):
                    ok = ok and selected.get("target_profile") != "full"
                    ok = ok and any(
                        item.get("target_profile") == "full" and item.get("reason") == "explicit_full_request_required"
                        for item in suggestion.get("excluded_candidates", [])
                    )
                else:
                    ok = (
                        ok
                        and selected.get("target_profile") == "full"
                        and bool(suggestion.get("hard_load_preview_command"))
                        and bool(selected.get("why_full_selected"))
                    )
                row["ok"] = ok
                if not ok:
                    row["error"] = "profile_suggest_matrix_expectation_failed"
                    matrix_ok = False
                profile_suggest_contract["matrix"].append(row)

            if not matrix_ok:
                errors.append("skills2cli profile suggest matrix must route ordinary profile queries away from `full`, allow explicit full troubleshooting, and preserve preview-only safety flags.")
            if first_suggestion is not None:
                suggestion = first_suggestion
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
                profile_suggest_contract["ok"] = matrix_ok and base_contract_ok and evidence_contract_ok
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

    installed_artifacts = build_installed_artifact_report(root)
    installed_path = Path.home() / ".codex" / INSTALLED_PROFILE_REGISTRY_RELATIVE
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
        "installed_artifact_drift_report": installed_artifacts,
        "orthogonal_scope_fields": list(ORTHOGONAL_SCOPE_FIELDS),
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
        data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            sys.stdout.buffer.write(data.encode("utf-8"))
        except AttributeError:  # pragma: no cover - nonstandard stdout shim.
            sys.stdout.write(data)
    else:
        print("Skills2CLI profile routing check passed." if payload["ok"] else "Skills2CLI profile routing check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        for warning in payload["warnings"]:
            print(f"  - warning: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
