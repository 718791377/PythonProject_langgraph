#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY_RELATIVE_PATH = "docs_bilingual/governance/codex_skills_profiles.registry.yaml"
MAPPING_DOC_ID = "codex_skills_profile_launcher_mapping"
REQUIRED_PROFILES = ["core", "browser", "web", "github", "full"]
EXPECTED_ALIASES = {
    "core": "codex-ohmy-core",
    "browser": "codex-ohmy-browser",
    "web": "codex-ohmy-web",
    "github": "codex-ohmy-github",
    "full": "codex-ohmy-full",
}
REQUIRED_BROWSER_SKILLS = ["agent-browser", "agent-browser-verify", "verification", "investigation-mode"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return value.strip('"').strip("'")


def parse_docs_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in read_text(path).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            stripped = stripped[2:]
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = str(parse_scalar(value))
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = str(parse_scalar(value))
    if current:
        entries.append(current)
    return entries


def parse_profiles_registry(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {
        "profiles": set(),
        "plugin_rules": {},
        "launcher_mapping": {},
    }
    section: str | None = None
    current_plugin: str | None = None
    in_launcher_aliases = False
    current_alias: str | None = None

    for raw_line in read_text(path).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_plugin = None
            in_launcher_aliases = False
            current_alias = None
            continue

        if section == "profiles" and indent == 2 and stripped.endswith(":"):
            data["profiles"].add(stripped[:-1])
            continue

        if section == "plugin_rules":
            if indent == 2 and stripped.endswith(":"):
                current_plugin = stripped[:-1]
                data["plugin_rules"].setdefault(current_plugin, {})
                continue
            if current_plugin and indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                data["plugin_rules"][current_plugin][key.strip()] = parse_scalar(value)
                continue

        if section == "launcher_mapping":
            mapping = data["launcher_mapping"]
            if indent == 2 and stripped == "aliases:":
                in_launcher_aliases = True
                mapping.setdefault("aliases", {})
                current_alias = None
                continue
            if not in_launcher_aliases and indent == 2 and ":" in stripped:
                key, value = stripped.split(":", 1)
                mapping[key.strip()] = parse_scalar(value)
                continue
            if in_launcher_aliases and indent == 4 and stripped.endswith(":"):
                current_alias = stripped[:-1]
                mapping.setdefault("aliases", {}).setdefault(current_alias, {})
                continue
            if in_launcher_aliases and current_alias and indent == 6 and ":" in stripped:
                key, value = stripped.split(":", 1)
                mapping["aliases"][current_alias][key.strip()] = parse_scalar(value)
                continue

    return data


def validate_docs_registry(root: Path, errors: list[str]) -> None:
    registry = root / "docs_bilingual" / "docs_registry.yaml"
    if not registry.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
        return
    entries = parse_docs_registry(registry)
    matches = [entry for entry in entries if entry.get("doc_id") == MAPPING_DOC_ID]
    if not matches:
        errors.append(f"docs_registry.yaml is missing `{MAPPING_DOC_ID}`.")
        return
    entry = matches[0]
    for key in ["canonical_path", "zh_cn_path"]:
        value = entry.get(key, "")
        if not value:
            errors.append(f"`{MAPPING_DOC_ID}` registry entry is missing {key}.")
        elif not (root / value).exists():
            errors.append(f"`{MAPPING_DOC_ID}` registry entry points to missing {key}: {value}")


def validate_mapping(parsed: dict[str, Any], errors: list[str], warnings: list[str], info: list[str]) -> None:
    profiles: set[str] = parsed["profiles"]
    mapping: dict[str, Any] = parsed.get("launcher_mapping", {})
    aliases: dict[str, dict[str, Any]] = mapping.get("aliases", {})

    if not mapping:
        errors.append(f"{REGISTRY_RELATIVE_PATH} is missing launcher_mapping.")
        return

    expected_top = {
        "status": "documented_only",
        "config_mutation": "forbidden",
        "installed_wrapper_mutation": "forbidden",
        "base_command": "codex-ohmy",
        "default_profile": "core",
        "future_aliases_installed": False,
    }
    for key, expected in expected_top.items():
        if mapping.get(key) != expected:
            errors.append(f"launcher_mapping.{key} must be `{expected}`, got `{mapping.get(key)}`.")

    for profile in REQUIRED_PROFILES:
        if profile not in profiles:
            errors.append(f"Required profile `{profile}` is missing from profiles registry.")
        if profile not in aliases:
            errors.append(f"launcher_mapping.aliases is missing required profile `{profile}`.")

    for profile, entry in sorted(aliases.items()):
        if profile not in profiles:
            errors.append(f"launcher mapping references unknown profile `{profile}`.")
        info.append(f"Launcher mapping checked for profile `{profile}`.")
        for field in ["alias", "lifecycle", "base_command", "purpose", "profile_set", "plugin_policy"]:
            if field not in entry:
                errors.append(f"launcher mapping `{profile}` is missing `{field}`.")
        if profile in EXPECTED_ALIASES and entry.get("alias") != EXPECTED_ALIASES[profile]:
            errors.append(f"launcher mapping `{profile}` alias must be `{EXPECTED_ALIASES[profile]}`.")
        if entry.get("base_command") != "codex-ohmy":
            errors.append(f"launcher mapping `{profile}` base_command must be `codex-ohmy`.")
        profile_set = entry.get("profile_set", [])
        if not isinstance(profile_set, list):
            errors.append(f"launcher mapping `{profile}` profile_set must be a list.")
            profile_set = []
        for item in profile_set:
            if item not in profiles:
                errors.append(f"launcher mapping `{profile}` profile_set references unknown profile `{item}`.")
        if entry.get("lifecycle") in {"future_optional", "temporary_troubleshooting"}:
            warnings.append(f"Launcher alias `{entry.get('alias')}` for `{profile}` is documented, not installed by this change.")
        else:
            errors.append(f"launcher mapping `{profile}` lifecycle must be future_optional or temporary_troubleshooting.")

    core = aliases.get("core", {})
    if core.get("reduced_default") is not True or core.get("default") is not True:
        errors.append("launcher mapping `core` must be the reduced default.")
    if core.get("broad_plugin_discovery") is not False:
        errors.append("launcher mapping `core` must not use broad plugin discovery.")
    core_policy = str(core.get("plugin_policy", "")).lower()
    if "vercel" in core_policy and not core_policy.startswith("no_vercel"):
        errors.append("launcher mapping `core` must not require Vercel-specific plugin policy.")

    full = aliases.get("full", {})
    if full.get("lifecycle") != "temporary_troubleshooting":
        errors.append("launcher mapping `full` must be temporary_troubleshooting.")
    if full.get("default") is not False:
        errors.append("launcher mapping `full` must not be default.")
    if full.get("broad_plugin_discovery") is not True:
        errors.append("launcher mapping `full` must explicitly allow broad plugin discovery.")

    browser = aliases.get("browser", {})
    browser_policy = str(browser.get("plugin_policy", "")).lower()
    if "preserve_vercel_bundle" not in browser_policy:
        errors.append("launcher mapping `browser` must preserve Vercel bundle behavior.")
    preserve = browser.get("preserve_plugin_skills", [])
    for skill in REQUIRED_BROWSER_SKILLS:
        if skill not in preserve:
            errors.append(f"launcher mapping `browser` must preserve plugin skill `{skill}`.")

    web = aliases.get("web", {})
    web_policy = str(web.get("plugin_policy", "")).lower()
    if "preserve_vercel_bundle" not in web_policy:
        errors.append("launcher mapping `web` must preserve Vercel bundle behavior.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex skills profile launcher mapping metadata.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    registry = root / REGISTRY_RELATIVE_PATH
    if not registry.exists():
        errors.append(f"{REGISTRY_RELATIVE_PATH} is missing.")
        parsed = {"profiles": set(), "launcher_mapping": {}}
    else:
        parsed = parse_profiles_registry(registry)
        validate_mapping(parsed, errors, warnings, info)
    validate_docs_registry(root, errors)

    aliases = parsed.get("launcher_mapping", {}).get("aliases", {})
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "codex_skills_profile_launcher_mapping",
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "root": str(root),
        "counts": {
            "profiles": len(parsed.get("profiles", set())),
            "launcher_mappings": len(aliases),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "launcher_mappings": {
            name: {
                "alias": entry.get("alias"),
                "lifecycle": entry.get("lifecycle"),
                "base_command": entry.get("base_command"),
                "profile_set": entry.get("profile_set"),
                "plugin_policy": entry.get("plugin_policy"),
            }
            for name, entry in sorted(aliases.items())
        },
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Codex skills profile launcher mapping check passed." if payload["ok"] else "Codex skills profile launcher mapping check failed:")
        for error in errors:
            print(f"  - {error}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
