#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from datetime import datetime, timezone
from pathlib import Path


CHECK_NAME = "context_retention_canary_surface"

START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
END_CANARY = chr(21941) + "~"

ALLOWED_CANARY_PROMPT_PATHS = {
    Path("docs_bilingual/project_startup_summary.md"),
    Path("docs_bilingual/project_startup_summary.zh-CN.md"),
}

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".worktrees",
    ".omx",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".ps1",
    ".psm1",
    ".sh",
}

SKIP_FILE_NAMES = {
    "local-gate-report.json",
    "openspec-guard-report.json",
}

AGENTS_PATH = Path("AGENTS.md")

RECOVERY_ANCHORS = (
    "Recovery action:",
    "恢复动作：",
)


def normalize_relative_path(path: Path) -> Path:
    return Path(*path.parts)


def is_archived_openspec_path(relative_path: Path) -> bool:
    parts = relative_path.parts
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ("openspec", "changes", "archive"):
            return True
    return False


def load_root_gitignore_patterns(root: Path) -> list[str]:
    gitignore_path = root / ".gitignore"
    text = read_text(gitignore_path)
    if text is None:
        return []
    patterns: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        patterns.append(line.replace("\\", "/"))
    return patterns


def matches_root_gitignore(relative_path: Path, patterns: list[str]) -> bool:
    path_text = relative_path.as_posix()
    path_parts = relative_path.parts
    for pattern in patterns:
        directory_only = pattern.endswith("/")
        normalized = pattern.strip("/") if pattern.startswith("/") else pattern.rstrip("/")
        if not normalized:
            continue
        if directory_only:
            if path_text == normalized or path_text.startswith(normalized + "/"):
                return True
            if not pattern.startswith("/") and normalized in path_parts:
                return True
            continue
        if pattern.startswith("/"):
            if fnmatch.fnmatchcase(path_text, normalized):
                return True
            continue
        if fnmatch.fnmatchcase(path_text, normalized) or fnmatch.fnmatchcase(relative_path.name, normalized):
            return True
    return False


def iter_candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    root_gitignore_patterns = load_root_gitignore_patterns(root)
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIR_NAMES
        ]
        current_path = Path(current_root)
        for filename in filenames:
            if filename in SKIP_FILE_NAMES:
                continue
            path = current_path / filename
            try:
                relative_path = normalize_relative_path(path.relative_to(root))
            except ValueError:
                continue
            if is_archived_openspec_path(relative_path):
                continue
            if matches_root_gitignore(relative_path, root_gitignore_patterns):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            files.append(path)
    return files


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def find_line_numbers(text: str, needle: str) -> list[int]:
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), start=1)
        if needle in line
    ]


def recovery_mentions_agents(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if any(anchor in line for anchor in RECOVERY_ANCHORS):
            window = "\n".join(lines[index : index + 3])
            return "AGENTS.md" in window
    return False


def run_check(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    findings: list[dict] = []

    for relative_path in sorted(ALLOWED_CANARY_PROMPT_PATHS):
        path = root / relative_path
        text = read_text(path)
        if text is None:
            errors.append(f"Missing or unreadable startup summary canary source: {relative_path.as_posix()}")
            continue
        missing_parts = []
        if START_CANARY not in text:
            missing_parts.append("start marker")
        if END_CANARY not in text:
            missing_parts.append("end marker")
        if missing_parts:
            errors.append(
                f"{relative_path.as_posix()} is missing the startup-summary canary "
                f"{', '.join(missing_parts)}."
            )
        if not recovery_mentions_agents(text):
            errors.append(
                f"{relative_path.as_posix()} must state that canary recovery rereads AGENTS.md "
                "as part of cold-start recovery."
            )

    agents_text = read_text(root / AGENTS_PATH)
    if agents_text is None:
        errors.append("Missing or unreadable AGENTS.md recovery authority surface.")
    elif START_CANARY in agents_text or END_CANARY in agents_text:
        errors.append(
            "AGENTS.md must remain a recovery reread target but must not duplicate the literal canary prompt."
        )

    for path in iter_candidate_files(root):
        relative_path = normalize_relative_path(path.relative_to(root))
        if relative_path in ALLOWED_CANARY_PROMPT_PATHS:
            continue
        text = read_text(path)
        if text is None:
            warnings.append(f"Skipped unreadable text candidate: {relative_path.as_posix()}")
            continue
        start_lines = find_line_numbers(text, START_CANARY)
        end_lines = find_line_numbers(text, END_CANARY)
        if start_lines or end_lines:
            finding = {
                "path": relative_path.as_posix(),
                "start_marker_lines": start_lines,
                "end_marker_lines": end_lines,
            }
            findings.append(finding)
            errors.append(
                "Context-retention canary prompt text must live only in "
                f"project_startup_summary.*; duplicate marker found in {relative_path.as_posix()}."
            )

    if not findings and not errors:
        info.append("Context-retention canary prompt is confined to the startup summary pair.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "allowed_paths": sorted(path.as_posix() for path in ALLOWED_CANARY_PROMPT_PATHS),
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": len(findings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the context-retention canary prompt lives only in startup summaries."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
