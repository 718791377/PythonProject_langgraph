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

REGISTRY_RELATIVE_PATH = "docs_bilingual/governance/codex_skills_profiles.registry.yaml"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


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
        "preferred_sources": {},
        "known_same_layer_exceptions": [],
        "description_limits": {"user": 180, "repo": 220},
        "description_enforcement": {"user": "warning", "repo": "error"},
        "plugin_rules": {},
    }
    if not path.exists():
        return data

    section: str | None = None
    subsection: str | None = None
    current_exception: dict[str, str] | None = None
    current_plugin: str | None = None

    for raw_line in read_text(path).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            subsection = None
            current_exception = None
            current_plugin = None
            continue

        if section == "settings":
            if indent == 2 and stripped.endswith(":"):
                subsection = stripped[:-1]
                continue
            if indent == 4 and ":" in stripped and subsection == "description_limits":
                key, value = stripped.split(":", 1)
                if value.strip().isdigit():
                    data["description_limits"][key.strip()] = int(value.strip())
                continue
            if indent == 4 and ":" in stripped and subsection == "description_enforcement":
                key, value = stripped.split(":", 1)
                data["description_enforcement"][key.strip()] = value.strip().strip('"').strip("'")
                continue

        if section == "duplicate_skill_policy":
            if indent == 2 and stripped.endswith(":"):
                subsection = stripped[:-1]
                current_exception = None
                continue
            if subsection == "preferred_sources" and indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                data["preferred_sources"][key.strip()] = value.strip().strip('"').strip("'")
                continue
            if subsection == "known_same_layer_exceptions":
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

        if section == "plugin_rules":
            if indent == 2 and stripped.endswith(":"):
                current_plugin = stripped[:-1]
                data["plugin_rules"].setdefault(current_plugin, {})
                continue
            if current_plugin and indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                value = value.strip()
                data["plugin_rules"][current_plugin][key.strip()] = (
                    parse_inline_list(value) if value.startswith("[") else value.strip('"').strip("'")
                )
                continue

    return data


def has_exception(name: str, layer: str, exceptions: list[dict[str, str]]) -> bool:
    return any(
        item.get("layer") == layer and fnmatch.fnmatch(name, item.get("name_pattern", ""))
        for item in exceptions
    )


def skill_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": row.get("name"),
        "source_layer": row.get("source_layer"),
        "source_detail": row.get("source_detail"),
        "file_path": row.get("file_path"),
        "description_length": row.get("description_length"),
        "status_suggestion": row.get("status_suggestion"),
    }


def add_candidate(candidates: list[dict[str, Any]], **kwargs: Any) -> None:
    candidates.append(
        {
            "candidate_id": f"C{len(candidates) + 1:04d}",
            "cleanup_action_performed": False,
            **kwargs,
        }
    )


def build_report(root: Path, include_plugins: bool, user_root: Path, plugin_root: Path) -> dict[str, Any]:
    inventory = build_inventory(root, include_plugins, user_root, plugin_root)
    registry_path = root / REGISTRY_RELATIVE_PATH
    registry = parse_profiles_registry(registry_path)
    candidates: list[dict[str, Any]] = []

    by_layer_name: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inventory.get("skills", []):
        by_layer_name[(row["source_layer"], row["name"])].append(row)
        by_name[row["name"]].append(row)

    exceptions = registry["known_same_layer_exceptions"]
    for (layer, name), rows in sorted(by_layer_name.items()):
        if len(rows) <= 1:
            continue
        is_openspec_nested = (
            layer == "repo"
            and name.startswith("openspec-")
            and any(row.get("source_detail") == "repo_nested" for row in rows)
        )
        disposition = (
            "deferred_requires_clean_clone_evidence"
            if is_openspec_nested or has_exception(name, layer, exceptions)
            else "needs_policy_decision"
        )
        add_candidate(
            candidates,
            candidate_type="openspec_nested_duplicate" if is_openspec_nested else "same_layer_duplicate",
            name=name,
            disposition=disposition,
            source_layers=[layer],
            skills=[skill_ref(row) for row in rows],
            required_evidence=[
                "clean temporary clone",
                "OpenSpec regeneration comparison",
                "OpenSpec guard with clean working tree",
                "explicit user approval before deletion",
            ]
            if disposition == "deferred_requires_clean_clone_evidence"
            else ["policy decision before any cleanup"],
        )

    preferred_sources = registry["preferred_sources"]
    for name, rows in sorted(by_name.items()):
        layers = sorted({row["source_layer"] for row in rows})
        if len(layers) <= 1:
            continue
        if set(layers).issubset({"user", "plugin"}):
            preferred = preferred_sources.get(name)
            add_candidate(
                candidates,
                candidate_type="cross_layer_user_plugin_duplicate",
                name=name,
                disposition="preferred_source_recorded_no_action" if preferred else "needs_preferred_source_decision",
                preferred_source=preferred,
                source_layers=layers,
                skills=[skill_ref(row) for row in rows],
                required_evidence=[
                    "explicit user approval before user-level cleanup",
                    "backup of affected user-level skill before mutation",
                ],
            )

    limits = registry["description_limits"]
    for row in inventory.get("skills", []):
        if row.get("source_layer") != "user":
            continue
        limit = int(limits.get("user", 180) or 180)
        if row.get("description_length", 0) > limit:
            add_candidate(
                candidates,
                candidate_type="user_long_description",
                name=row.get("name"),
                disposition="deferred_until_description_shortening_phase",
                source_layers=["user"],
                skills=[skill_ref(row)],
                required_evidence=[
                    "separate reviewable description-shortening change",
                    "no semantic loss in skill routing description",
                    "explicit approval before editing user-level skill",
                ],
            )

    for row in inventory.get("skills", []):
        if row.get("source_layer") != "plugin":
            continue
        add_candidate(
            candidates,
            candidate_type="plugin_managed_skill",
            name=row.get("name"),
            disposition="report_only_plugin_managed",
            source_layers=["plugin"],
            skills=[skill_ref(row)],
            required_evidence=["vendor or plugin-manager change required before plugin file mutation"],
        )

    by_type: dict[str, int] = defaultdict(int)
    by_disposition: dict[str, int] = defaultdict(int)
    for candidate in candidates:
        by_type[candidate["candidate_type"]] += 1
        by_disposition[candidate["disposition"]] += 1

    safety_constraints = [
        "No user-level skills were deleted, moved, renamed, or edited.",
        "No repository OpenSpec duplicate candidates were deleted.",
        "No plugin cache files were edited.",
        "No Vercel plugin capability was disabled.",
        "No user-level Codex config.toml was mutated.",
        "Browser and web verification capabilities remain preserved.",
    ]

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "report_codex_skills_cleanup_candidates",
        "root": str(root.resolve()),
        "input_scan_roots": inventory.get("scan_roots", {}),
        "source_inventory_counts": inventory.get("counts", {}),
        "policy": {
            "registry_path": REGISTRY_RELATIVE_PATH,
            "preferred_sources": preferred_sources,
            "description_limits": limits,
            "description_enforcement": registry["description_enforcement"],
        },
        "summary": {
            "cleanup_actions_performed": 0,
            "candidate_count": len(candidates),
            "by_candidate_type": dict(sorted(by_type.items())),
            "by_disposition": dict(sorted(by_disposition.items())),
        },
        "safety_constraints": safety_constraints,
        "phase3_gate": {
            "cleanup_allowed": False,
            "reason": "Phase 3 is a proposal and evidence phase only.",
            "required_before_cleanup": [
                "clean-clone OpenSpec regeneration evidence",
                "OpenSpec guard with --require-clean-git in a clean clone",
                "candidate-specific review",
                "explicit user approval",
            ],
        },
        "validation_notes": [
            "This report is generated from inventory and registry metadata.",
            "Candidate records are review evidence, not cleanup instructions.",
        ],
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report non-destructive Codex skills cleanup candidates.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional path to write the JSON report.")
    parser.add_argument("--no-plugins", action="store_true", help="Skip plugin cache scanning.")
    parser.add_argument("--user-skills-root", help="Override user-level skills root.")
    parser.add_argument("--plugin-cache-root", help="Override plugin cache root.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    user_profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
    user_root = Path(args.user_skills_root).resolve() if args.user_skills_root else user_profile / ".codex" / "skills"
    plugin_root = Path(args.plugin_cache_root).resolve() if args.plugin_cache_root else user_profile / ".codex" / "plugins" / "cache"

    report = build_report(root, not args.no_plugins, user_root, plugin_root)
    output = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8", newline="\n")
    if args.json or not args.output:
        print(output)
    else:
        print(f"Wrote Codex skills cleanup candidate report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
