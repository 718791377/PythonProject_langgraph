#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def default_rules_path(root: Path) -> Path:
    return root / "tools" / "current_repo_authority_language_rules.json"


def load_rules(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Rules file does not exist: {path}")
    return json.loads(read_text(path))


def compile_pattern_rules(entries: list, default_label: str) -> list[tuple[str, re.Pattern[str]]]:
    compiled: list[tuple[str, re.Pattern[str]]] = []
    for entry in entries:
        if isinstance(entry, str):
            label = default_label
            pattern = entry
        else:
            label = entry.get("label", default_label)
            pattern = entry["pattern"]
        compiled.append((label, re.compile(pattern)))
    return compiled


def compile_allow_all_paths(entries: list) -> dict[str, str]:
    compiled: dict[str, str] = {}
    for entry in entries:
        if isinstance(entry, str):
            compiled[entry] = "allow_all_relative_path"
        else:
            compiled[entry["path"]] = entry.get("label", "allow_all_relative_path")
    return compiled


def compile_rules(
    raw_rules: dict,
) -> tuple[
    list[tuple[str, re.Pattern[str]]],
    list[tuple[str, re.Pattern[str]]],
    dict[str, str],
    dict[str, list[tuple[str, re.Pattern[str]]]],
]:
    banned_patterns = compile_pattern_rules(raw_rules.get("banned_patterns", []), "banned_pattern")
    global_allowed_context_patterns = compile_pattern_rules(
        raw_rules.get("global_allowed_context_patterns", []),
        "global_allowed_context",
    )
    allow_all_relative_paths = compile_allow_all_paths(raw_rules.get("allow_all_relative_paths", []))
    file_allowed_context_patterns = {
        relative_path: compile_pattern_rules(patterns, "file_allowed_context")
        for relative_path, patterns in raw_rules.get("file_allowed_context_patterns", {}).items()
    }
    return (
        banned_patterns,
        global_allowed_context_patterns,
        allow_all_relative_paths,
        file_allowed_context_patterns,
    )


def iter_target_files(root: Path) -> list[Path]:
    targets: set[Path] = set()

    explicit_files = [
        root / "docs_bilingual" / "project_startup_summary.md",
        root / "docs_bilingual" / "project_startup_summary.zh-CN.md",
        root / "openspec" / "config.yaml",
    ]
    for path in explicit_files:
        if path.exists():
            targets.add(path)

    for path in (root / "docs_bilingual" / "governance").rglob("*.md"):
        targets.add(path)

    for path in (root / "docs_bilingual" / "implementation_plans").rglob("*.md"):
        targets.add(path)

    for path in (root / "openspec" / "specs").rglob("*.md"):
        targets.add(path)

    for path in (root / "openspec" / "changes").rglob("*.md"):
        if "archive" in path.parts:
            continue
        targets.add(path)

    return sorted(targets)


def context_is_allowed(
    relative_path: str,
    lines: list[str],
    index: int,
    global_allowed_context_patterns: list[tuple[str, re.Pattern[str]]],
    allow_all_relative_paths: dict[str, str],
    file_allowed_context_patterns: dict[str, list[tuple[str, re.Pattern[str]]]],
) -> str | None:
    if relative_path in allow_all_relative_paths:
        return allow_all_relative_paths[relative_path]

    start = max(0, index - 2)
    end = min(len(lines), index + 3)
    context = "\n".join(lines[start:end])

    for label, pattern in global_allowed_context_patterns:
        if pattern.search(context):
            return label

    for label, pattern in file_allowed_context_patterns.get(relative_path, []):
        if pattern.search(context):
            return label

    return None


def find_violations(root: Path, rules_path: Path) -> tuple[list[str], dict[str, int], int]:
    raw_rules = load_rules(rules_path)
    (
        banned_patterns,
        global_allowed_context_patterns,
        allow_all_relative_paths,
        file_allowed_context_patterns,
    ) = compile_rules(raw_rules)

    violations: list[str] = []
    allowed_counts: dict[str, int] = {}
    checked_files = 0

    for path in iter_target_files(root):
        text = read_text(path)
        lines = text.splitlines()
        relative_path = path.relative_to(root).as_posix()
        checked_files += 1

        for index, line in enumerate(lines):
            matched_banned_label = None
            for label, pattern in banned_patterns:
                if pattern.search(line):
                    matched_banned_label = label
                    break
            if matched_banned_label is None:
                continue
            allowed_label = context_is_allowed(
                relative_path,
                lines,
                index,
                global_allowed_context_patterns,
                allow_all_relative_paths,
                file_allowed_context_patterns,
            )
            if allowed_label is not None:
                allowed_counts[allowed_label] = allowed_counts.get(allowed_label, 0) + 1
                continue
            violations.append(f"[{matched_banned_label}] {relative_path}:{index + 1}: {line.strip()}")

    return violations, allowed_counts, checked_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check current active authority surfaces for stale old-repository wording."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--rules",
        default=None,
        help="Path to the authority-language rules JSON file. Defaults to tools/current_repo_authority_language_rules.json under the repository root.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")

    rules_path = Path(args.rules).resolve() if args.rules else default_rules_path(root)
    violations, allowed_counts, checked_files = find_violations(root, rules_path)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "current_repo_authority_language",
        "ok": len(violations) == 0,
        "errors": violations,
        "warnings": [],
        "info": [],
        "root": str(root),
        "counts": {
            "checked_files": checked_files,
            "violations": len(violations),
            "allowed_context_matches_total": sum(allowed_counts.values()),
        },
        "checked_files": checked_files,
        "violations": violations,
        "allowed_context_matches": allowed_counts,
        "rules_path": str(rules_path),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if violations:
        print("Current-repo authority wording check failed:")
        for violation in violations:
            print(f"  - {violation}")
        print(f"Checked files: {checked_files}")
        if allowed_counts:
            print("Allowed context matches:")
            for label in sorted(allowed_counts):
                print(f"  - {label}: {allowed_counts[label]}")
        return 1

    print("Current-repo authority wording check passed.")
    print(f"Checked files: {checked_files}")
    if allowed_counts:
        print("Allowed context matches:")
        for label in sorted(allowed_counts):
            print(f"  - {label}: {allowed_counts[label]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
