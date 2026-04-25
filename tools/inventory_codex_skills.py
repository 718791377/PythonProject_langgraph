#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(path: Path) -> dict[str, Any]:
    lines = read_text(path).splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or not line.strip() or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def repo_relative(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def plugin_name_for(path: Path, plugin_cache_root: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(plugin_cache_root.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2:
        return ":".join(parts[:2])
    return None


def repo_skill_depth(path: Path, repo_skills_root: Path) -> int:
    try:
        return len(path.resolve().relative_to(repo_skills_root.resolve()).parts)
    except ValueError:
        return 0


def infer_name(path: Path, metadata: dict[str, Any]) -> str:
    name = str(metadata.get("name", "")).strip()
    return name or (path.parent.name if path.name.lower() == "skill.md" else path.stem)


def suspected_profile(name: str, description: str, layer: str, plugin: str | None) -> str:
    text = f"{name} {description} {plugin or ''}".lower()
    if name.startswith("openspec-") or "openspec" in text:
        return "openspec"
    if any(token in text for token in ["agent-browser", "browser", "playwright", "screenshot", "visual", "figma"]):
        return "browser"
    if any(token in text for token in ["vercel", "next.js", "nextjs", "react", "shadcn", "deployment", "frontend", "ai sdk", "web app"]):
        return "web"
    if any(token in text for token in ["github", "gh-", "pull request", "issue"]):
        return "github"
    if any(token in text for token in ["omx", "langgraph", "subagent", "team", "worker", "orchestration", "durable", "autopilot", "ralph", "ultra"]):
        return "orchestration"
    return "full" if layer == "plugin" else "core"


def initial_status(name: str, description: str, layer: str, repo_depth: int) -> str:
    if layer == "plugin":
        return "report_only_plugin_skill"
    if repo_depth > 2 and name.startswith("openspec-"):
        return "investigate_openspec_nested_duplicate_before_cleanup"
    if layer == "user" and len(description) > 180:
        return "shorten_user_description_after_inventory"
    if layer == "repo" and len(description) > 220:
        return "shorten_repo_description_after_inventory"
    return "keep"


def collect_skill_files(root: Path, include_plugins: bool, user_root: Path, plugin_root: Path) -> list[tuple[Path, str]]:
    repo_root = root / ".codex" / "skills"
    rows: list[tuple[Path, str]] = []
    if user_root.exists():
        rows.extend((path, "user") for path in sorted(user_root.rglob("SKILL.md")))
    if repo_root.exists():
        rows.extend((path, "repo") for path in sorted(repo_root.rglob("SKILL.md")))
    if include_plugins and plugin_root.exists():
        rows.extend((path, "plugin") for path in sorted(plugin_root.rglob("SKILL.md")))
    return rows


def build_inventory(root: Path, include_plugins: bool, user_root: Path, plugin_root: Path) -> dict[str, Any]:
    repo_root = root / ".codex" / "skills"
    skills: list[dict[str, Any]] = []
    for path, layer in collect_skill_files(root, include_plugins, user_root, plugin_root):
        metadata = parse_frontmatter(path)
        name = infer_name(path, metadata)
        description = str(metadata.get("description", "")).strip()
        plugin = plugin_name_for(path, plugin_root) if layer == "plugin" else None
        depth = repo_skill_depth(path, repo_root) if layer == "repo" else 0
        row = {
            "name": name,
            "description": description,
            "description_length": len(description),
            "source_layer": layer,
            "source_detail": plugin or ("repo_nested" if depth > 2 else layer),
            "file_path": repo_relative(path, root) or str(path.resolve()),
            "frontmatter_keys": sorted(metadata.keys()),
            "duplicate_name_group": None,
            "suspected_profile": suspected_profile(name, description, layer, plugin),
            "status_suggestion": initial_status(name, description, layer, depth),
        }
        skills.append(row)

    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in skills:
        by_name[row["name"]].append(row)

    duplicates: list[dict[str, Any]] = []
    for name, rows in sorted(by_name.items()):
        if len(rows) <= 1:
            continue
        group = {
            "name": name,
            "count": len(rows),
            "source_layers": sorted({row["source_layer"] for row in rows}),
            "file_paths": [row["file_path"] for row in rows],
        }
        duplicates.append(group)
        for row in rows:
            row["duplicate_name_group"] = {
                "name": name,
                "count": len(rows),
                "source_layers": group["source_layers"],
            }
            if row["status_suggestion"] == "keep":
                row["status_suggestion"] = "review_duplicate_preferred_source"

    by_layer: dict[str, int] = defaultdict(int)
    by_profile: dict[str, int] = defaultdict(int)
    for row in skills:
        by_layer[row["source_layer"]] += 1
        by_profile[row["suspected_profile"]] += 1

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "inventory_codex_skills",
        "root": str(root.resolve()),
        "scan_roots": {
            "user_skills": str(user_root),
            "repo_skills": str(repo_root),
            "plugin_cache": str(plugin_root) if include_plugins else None,
        },
        "counts": {
            "total_skills": len(skills),
            "by_source_layer": dict(sorted(by_layer.items())),
            "by_suspected_profile": dict(sorted(by_profile.items())),
            "duplicate_name_groups": len(duplicates),
        },
        "duplicates": duplicates,
        "skills": sorted(skills, key=lambda row: (row["source_layer"], row["name"], row["file_path"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory Codex user, repository, and plugin skills.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional path to write the JSON artifact.")
    parser.add_argument("--no-plugins", action="store_true", help="Skip plugin cache scanning.")
    parser.add_argument("--user-skills-root", help="Override user-level skills root.")
    parser.add_argument("--plugin-cache-root", help="Override plugin cache root.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    user_profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
    user_root = Path(args.user_skills_root).resolve() if args.user_skills_root else user_profile / ".codex" / "skills"
    plugin_root = Path(args.plugin_cache_root).resolve() if args.plugin_cache_root else user_profile / ".codex" / "plugins" / "cache"
    payload = build_inventory(root, not args.no_plugins, user_root, plugin_root)
    output = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8", newline="\n")
    if args.json or not args.output:
        print(output)
    else:
        print(f"Wrote skills inventory JSON to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
