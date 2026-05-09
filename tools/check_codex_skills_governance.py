#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from inventory_codex_skills import build_inventory  # noqa: E402

POLICY_DOC_ID = "codex_user_level_skills_governance_policy"
REGISTRY_RELATIVE_PATH = "docs_bilingual/governance/codex_skills_profiles.registry.yaml"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


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
                current[key.strip()] = value.strip()
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return [value.strip().strip('"').strip("'")]


def parse_profiles_registry(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {
        "profiles": set(),
        "projects": {},
        "known_same_layer_exceptions": [],
        "description_limits": {"user": 180, "repo": 220},
        "description_enforcement": {"user": "error", "repo": "error"},
    }
    section: str | None = None
    current_project: str | None = None
    current_exception: dict[str, str] | None = None
    in_description_limits = False
    in_description_enforcement = False

    for raw_line in read_text(path).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_project = None
            current_exception = None
            in_description_limits = False
            in_description_enforcement = False
            continue
        if section == "settings":
            if indent == 2 and stripped == "description_limits:":
                in_description_limits = True
                in_description_enforcement = False
                continue
            if indent == 2 and stripped == "description_enforcement:":
                in_description_limits = False
                in_description_enforcement = True
                continue
            if in_description_limits and indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                if value.strip().isdigit():
                    data["description_limits"][key.strip()] = int(value.strip())
                continue
            if in_description_enforcement and indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                data["description_enforcement"][key.strip()] = value.strip().strip('"').strip("'")
                continue
        if section == "profiles" and indent == 2 and stripped.endswith(":"):
            data["profiles"].add(stripped[:-1])
            continue
        if section == "projects":
            if indent == 2 and stripped.endswith(":"):
                current_project = stripped[:-1]
                data["projects"].setdefault(current_project, [])
                continue
            if current_project and indent == 4 and stripped.startswith("profiles:"):
                _, value = stripped.split(":", 1)
                data["projects"][current_project] = parse_inline_list(value)
                continue
        if section == "duplicate_skill_policy":
            if indent >= 4 and stripped.startswith("- "):
                current_exception = {}
                data["known_same_layer_exceptions"].append(current_exception)
                rest = stripped[2:]
                if ":" in rest:
                    key, value = rest.split(":", 1)
                    current_exception[key.strip()] = value.strip().strip('"').strip("'")
                continue
            if current_exception is not None and indent >= 6 and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_exception[key.strip()] = value.strip().strip('"').strip("'")
                continue
    return data


def has_exception(name: str, layer: str, exceptions: list[dict[str, str]]) -> bool:
    return any(
        item.get("layer") == layer and fnmatch.fnmatch(name, item.get("name_pattern", ""))
        for item in exceptions
    )


def validate_policy_registry(root: Path, errors: list[str]) -> None:
    docs_registry = root / "docs_bilingual" / "docs_registry.yaml"
    if not docs_registry.exists():
        errors.append("docs_bilingual/docs_registry.yaml is missing.")
        return
    entries = parse_docs_registry(docs_registry)
    matches = [entry for entry in entries if entry.get("doc_id") == POLICY_DOC_ID and entry.get("doc_class") == "governance"]
    if not matches:
        errors.append(f"docs_registry.yaml is missing governance doc_id `{POLICY_DOC_ID}`.")
        return
    entry = matches[0]
    for key in ["canonical_path", "zh_cn_path"]:
        value = entry.get(key, "")
        if not value:
            errors.append(f"Governance registry entry `{POLICY_DOC_ID}` is missing {key}.")
        elif not (root / value).exists():
            errors.append(f"Governance registry entry `{POLICY_DOC_ID}` points to missing {key}: {value}")


def validate_profile_registry(root: Path, errors: list[str]) -> dict[str, Any] | None:
    registry = root / REGISTRY_RELATIVE_PATH
    if not registry.exists():
        errors.append(f"{REGISTRY_RELATIVE_PATH} is missing.")
        return None
    parsed = parse_profiles_registry(registry)
    known = parsed["profiles"]
    if not known:
        errors.append(f"{REGISTRY_RELATIVE_PATH} has no profiles.")
    for project, profiles in parsed["projects"].items():
        for profile in profiles:
            if profile not in known:
                errors.append(f"{REGISTRY_RELATIVE_PATH} project `{project}` uses unknown profile `{profile}`.")
    return parsed


def validate_inventory(
    payload: dict[str, Any],
    parsed_registry: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
    deferred: list[str],
) -> None:
    exceptions = parsed_registry.get("known_same_layer_exceptions", []) if parsed_registry else []
    limits = parsed_registry.get("description_limits", {"user": 180, "repo": 220}) if parsed_registry else {"user": 180, "repo": 220}
    enforcement = parsed_registry.get("description_enforcement", {"user": "error", "repo": "error"}) if parsed_registry else {"user": "error", "repo": "error"}
    by_layer_name: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload.get("skills", []):
        by_layer_name[(row["source_layer"], row["name"])].append(row)
        by_name[row["name"]].append(row)
        if row["source_layer"] in {"user", "repo"}:
            limit = int(limits.get(row["source_layer"], 0) or 0)
            if limit and row.get("description_length", 0) > limit:
                message = (
                    f"{row['source_layer']} skill `{row['name']}` description length "
                    f"{row['description_length']} exceeds limit {limit}: {row['file_path']}"
                )
                if enforcement.get(row["source_layer"], "error") == "warning":
                    warnings.append(message)
                else:
                    errors.append(message)
    for (layer, name), rows in sorted(by_layer_name.items()):
        if len(rows) <= 1:
            continue
        if layer == "plugin":
            warnings.append(
                f"Plugin duplicate skill name `{name}` appears {len(rows)} times inside layer `plugin`; "
                "plugin skills are bundle-managed and report-only until fine-grained plugin filtering exists."
            )
        elif has_exception(name, layer, exceptions):
            deferred.append(
                f"Known same-layer duplicate cleanup candidate for {layer} skill `{name}`; "
                "requires clean-clone OpenSpec evidence before removal."
            )
        else:
            errors.append(f"Duplicate skill name `{name}` appears {len(rows)} times inside layer `{layer}`.")
    for name, rows in sorted(by_name.items()):
        layers = sorted({row["source_layer"] for row in rows})
        if len(layers) > 1 and set(layers).issubset({"user", "plugin"}):
            warnings.append(f"Cross-layer user/plugin duplicate `{name}` is report-only when policy declares a preferred source.")
    plugin_count = payload.get("counts", {}).get("by_source_layer", {}).get("plugin", 0)
    if plugin_count:
        warnings.append("Plugin skills are bundle-managed until fine-grained plugin filtering exists.")
    vercel_count = sum(1 for row in payload.get("skills", []) if row.get("source_layer") == "plugin" and "vercel" in str(row.get("source_detail", "")).lower())
    if vercel_count:
        warnings.append(f"Known Vercel plugin bulk load: {vercel_count} plugin skills detected; preserve browser/web capabilities.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Codex skills governance policy, registry, and inventory rules.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--no-plugins", action="store_true", help="Skip plugin cache scanning.")
    parser.add_argument("--user-skills-root", help="Override user-level skills root.")
    parser.add_argument("--plugin-cache-root", help="Override plugin cache root.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    user_profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
    user_root = Path(args.user_skills_root).resolve() if args.user_skills_root else user_profile / ".codex" / "skills"
    plugin_root = Path(args.plugin_cache_root).resolve() if args.plugin_cache_root else user_profile / ".codex" / "plugins" / "cache"
    errors: list[str] = []
    warnings: list[str] = []
    deferred: list[str] = []
    info: list[str] = []
    validate_policy_registry(root, errors)
    parsed = validate_profile_registry(root, errors)
    inventory = build_inventory(root, not args.no_plugins, user_root, plugin_root)
    validate_inventory(inventory, parsed, errors, warnings, deferred)
    info.append(f"Skills scanned: {inventory['counts']['total_skills']}")
    info.append(f"Duplicate name groups: {inventory['counts']['duplicate_name_groups']}")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "codex_skills_governance",
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "deferred": deferred,
        "info": info,
        "root": str(root),
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "deferred": len(deferred),
            "skills_total": inventory["counts"]["total_skills"],
            "duplicate_name_groups": inventory["counts"]["duplicate_name_groups"],
            "by_source_layer": inventory["counts"].get("by_source_layer", {}),
        },
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Codex skills governance check passed." if payload["ok"] else "Codex skills governance check failed:")
        for error in errors:
            print(f"  - {error}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        if deferred:
            print("Deferred cleanup:")
            for item in deferred:
                print(f"  - {item}")
        for item in info:
            print(f"  - {item}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
