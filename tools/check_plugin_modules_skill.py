#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "plugin_modules_skill"
SKILL_RELATIVE = Path("tools/skill_sources/plugin-modules")
REQUIRED_MODULES = [
    "core-dev",
    "web-saas",
    "company-ops",
    "market-research",
    "customer-comms",
    "creative-content",
    "pyside6-gui",
    "full",
]
REQUIRED_FILES = [
    "SKILL.md",
    "references/profiles.json",
    "scripts/list_module.ps1",
    "scripts/load_module.ps1",
    "scripts/set_plugin_profile.ps1",
    "agents/openai.yaml",
]
PYSIDE6_REPO_HINTS = [
    "repo:.codex/skills/pyside6-gui/SKILL.md",
    "repo:tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1",
    "repo:tools/pyside6_gui_templates/README.md",
    "repo:tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template",
]
PYSIDE6_REPO_HINT_TARGETS = [
    Path(".codex/skills/pyside6-gui/SKILL.md"),
    Path("tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1"),
    Path("tools/pyside6_gui_templates/README.md"),
    Path("tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template"),
]
REQUIRED_SCRIPT_MARKERS = {
    "nested_hard_load_reject": "task_module_not_hard_load_target",
    "scenario_hard_load_reject": "scenario_profile_not_hard_load_target",
    "apply_gate": "[switch]$Apply",
    "restore_gate": "[switch]$RestoreLatest",
    "backup_function": "Backup-CodexPluginModulesConfig",
    "plugin_enabled_scope": "[plugins.`\"$escaped`\"]",
    "no_plugin_cache_edit_report": "plugin_cache_edited = $false",
    "restart_instructions": "restart_instructions",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    skill_root = root / SKILL_RELATIVE

    for relative in REQUIRED_FILES:
        path = skill_root / relative
        if not path.exists():
            errors.append(f"Missing plugin-modules skill file: {SKILL_RELATIVE / relative}")

    installer = root / "tools" / "install-plugin-modules-skill.ps1"
    if not installer.exists():
        errors.append("Missing user-level installer: tools/install-plugin-modules-skill.ps1")

    skill_md = skill_root / "SKILL.md"
    if skill_md.exists():
        metadata = parse_frontmatter(read_text(skill_md))
        if metadata.get("name") != "plugin-modules":
            errors.append("plugin-modules SKILL.md frontmatter name must be `plugin-modules`.")
        description = metadata.get("description", "")
        if not description:
            errors.append("plugin-modules SKILL.md must include a description.")
        if len(description) > 220:
            errors.append(f"plugin-modules description length {len(description)} exceeds repo limit 220.")
        body = read_text(skill_md)
        for phrase in ["soft-load", "hard-load", "config.toml", "Do not delete plugin cache"]:
            if phrase not in body:
                errors.append(f"plugin-modules SKILL.md missing required instruction phrase: {phrase}")

    profiles_path = skill_root / "references" / "profiles.json"
    profiles: dict[str, Any] | None = None
    if profiles_path.exists():
        try:
            profiles = json.loads(read_text(profiles_path))
        except json.JSONDecodeError as exc:
            errors.append(f"profiles.json is not valid JSON: {exc}")
        if profiles is not None:
            if profiles.get("schema_version") != 1:
                errors.append("profiles.json schema_version must be 1.")
            modules = profiles.get("modules", {})

            scenario_profiles = profiles.get("scenario_profiles", {})
            if not isinstance(scenario_profiles, dict) or not scenario_profiles:
                errors.append("profiles.json must define advisory scenario_profiles.")
            for scenario_name, scenario_entry in scenario_profiles.items() if isinstance(scenario_profiles, dict) else []:
                target = scenario_entry.get("target_profile") if isinstance(scenario_entry, dict) else None
                if target not in modules:
                    errors.append(f"Scenario profile `{scenario_name}` target_profile must resolve to a canonical module.")
                if scenario_name in modules:
                    errors.append(f"Scenario profile `{scenario_name}` must not be a canonical hard-load module.")
            for module in REQUIRED_MODULES:
                entry = modules.get(module)
                if not isinstance(entry, dict):
                    errors.append(f"profiles.json missing required module `{module}`.")
                    continue
                if not entry.get("description"):
                    errors.append(f"Module `{module}` is missing description.")
                hard_load = entry.get("hard_load", {})
                if "enable_plugins" not in hard_load:
                    errors.append(f"Module `{module}` is missing hard_load.enable_plugins.")
                soft_load = entry.get("soft_load", {})
                if "skill_doc_hints" not in soft_load:
                    errors.append(f"Module `{module}` is missing soft_load.skill_doc_hints.")
                if module != "full":
                    for field in ("scenario_description", "route_when", "negative_examples", "load_policy", "ranking_signals", "task_modules"):
                        if not entry.get(field):
                            errors.append(f"Module `{module}` is missing routing field `{field}`.")
                    task_modules = entry.get("task_modules", {})
                    if isinstance(task_modules, dict):
                        for task_name, task_entry in task_modules.items():
                            for field in ("scenario_description", "route_when", "negative_examples", "load_policy", "routing_explanation", "ranking_signals"):
                                if not task_entry.get(field):
                                    errors.append(f"Task module `{module}.{task_name}` is missing field `{field}`.")
                    else:
                        errors.append(f"Module `{module}` task_modules must be an object.")
            safety = profiles.get("safety", {})
            if safety.get("backup_before_config_write") is not True:
                errors.append("profiles.json safety.backup_before_config_write must be true.")
            if safety.get("do_not_edit_plugin_cache") is not True:
                errors.append("profiles.json safety.do_not_edit_plugin_cache must be true.")
            for target in PYSIDE6_REPO_HINT_TARGETS:
                if not (root / target).exists():
                    errors.append(f"Module `pyside6-gui` repo-local hint target is missing: {target.as_posix()}")
            pyside6 = modules.get("pyside6-gui")
            if isinstance(pyside6, dict):
                plugins = pyside6.get("plugins", [])
                if plugins not in ([], None):
                    errors.append("Module `pyside6-gui` must not enable plugin bundles; it is repo-local guidance only.")
                hard_load = pyside6.get("hard_load", {})
                if hard_load.get("enable_plugins") not in ([], None):
                    errors.append("Module `pyside6-gui` hard_load.enable_plugins must be an empty list.")
                if hard_load.get("disable_other_known_plugins") is not False:
                    errors.append("Module `pyside6-gui` hard_load.disable_other_known_plugins must be false.")
                soft_load = pyside6.get("soft_load", {})
                hints = soft_load.get("skill_doc_hints", [])
                for hint in PYSIDE6_REPO_HINTS:
                    if hint not in hints:
                        errors.append(f"Module `pyside6-gui` missing soft-load hint `{hint}`.")
                for hint in hints:
                    if "pyside6" in str(hint).lower() and not str(hint).startswith("repo:"):
                        errors.append("Module `pyside6-gui` PySide6 hints must use the repo: prefix.")
                notes = " ".join(str(item) for item in soft_load.get("notes", []))
                for phrase in ["does not install PySide6", "preview before apply", "Visible GUI launch", "packaging"]:
                    if phrase not in notes:
                        errors.append(f"Module `pyside6-gui` notes must preserve boundary phrase: {phrase}")

    load_script = skill_root / "scripts" / "load_module.ps1"
    if load_script.exists():
        text = read_text(load_script)
        for phrase in ["[string]$RepoRoot", "repo_root", "StartsWith('repo:'", "Join-Path $repoRootPath", "entry_kind", "target_profile", "task_module"]:
            if phrase not in text:
                errors.append(f"load_module.ps1 missing repo-local hint support marker: {phrase}")

    set_script = skill_root / "scripts" / "set_plugin_profile.ps1"
    if set_script.exists():
        text = read_text(set_script)
        for name, marker in REQUIRED_SCRIPT_MARKERS.items():
            if marker not in text:
                errors.append(f"set_plugin_profile.ps1 missing marker `{name}`.")
        if re.search(r"Remove-Item\s+.*plugin", text, flags=re.IGNORECASE):
            warnings.append("set_plugin_profile.ps1 contains Remove-Item near plugin text; confirm it never targets plugin cache.")

    if installer.exists():
        text = read_text(installer)
        for phrase in ["tools\\skill_sources\\plugin-modules", "backups\\plugin-modules-skill", "Restart codex-ohmy"]:
            if phrase not in text:
                errors.append(f"install-plugin-modules-skill.ps1 missing required phrase: {phrase}")

    info.append("plugin-modules source skill is repository-local and installs to user-level Codex skills via explicit installer.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "skill_root": str(skill_root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {"errors": len(errors), "warnings": len(warnings), "required_modules": len(REQUIRED_MODULES)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the plugin-modules user-level skill source and profile helper contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = validate(Path(args.root).resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Plugin modules skill check passed." if payload["ok"] else "Plugin modules skill check failed:")
        for error in payload["errors"]:
            print(f"  - {error}")
        if payload["warnings"]:
            print("Warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
