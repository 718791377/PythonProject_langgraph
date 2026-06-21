#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "document_pair_policy"
TARGET_ROOTS = ("docs_bilingual", "openspec", "docs")
CHINESE_SUFFIX = ".zh-CN.md"


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def is_target_markdown(path: str) -> bool:
    path = normalize(path)
    return path.endswith(".md") and any(path == root or path.startswith(root + "/") for root in TARGET_ROOTS)


def companion_for(path: Path) -> Path:
    name = path.name
    if name.endswith(CHINESE_SUFFIX):
        return path.with_name(name[: -len(CHINESE_SUFFIX)] + ".md")
    return path.with_name(path.stem + CHINESE_SUFFIX)


def changed_markdown(root: Path, base_ref: str) -> dict[str, str]:
    changed: dict[str, str] = {}
    merge_base = run_git(root, ["merge-base", base_ref, "HEAD"])
    base = merge_base.stdout.strip() if merge_base.returncode == 0 and merge_base.stdout.strip() else base_ref
    diff = run_git(root, ["diff", "--name-status", "--diff-filter=ACMRD", f"{base}...HEAD"])
    if diff.returncode == 0:
        for raw in diff.stdout.splitlines():
            if not raw.strip():
                continue
            parts = raw.split("\t")
            status = parts[0][:1]
            paths = [normalize(item) for item in parts[1:]]
            if status in {"R", "C"} and len(paths) >= 2:
                source_path, target_path = paths[-2], paths[-1]
                if is_target_markdown(source_path):
                    changed[source_path] = "D"
                if is_target_markdown(target_path):
                    changed[target_path] = "A"
                continue
            path = paths[-1] if paths else ""
            if is_target_markdown(path):
                changed[path] = status
    # Include staged, unstaged, and untracked files for pre-commit / dirty guard runs.
    status = run_git(root, ["status", "--porcelain", "--untracked-files=all"])
    if status.returncode == 0:
        for raw in status.stdout.splitlines():
            if not raw.strip():
                continue
            code = raw[:2]
            path_text = raw[3:] if len(raw) > 3 else ""
            if " -> " in path_text:
                source_text, target_text = path_text.split(" -> ", 1)
                source_path = normalize(source_text)
                target_path = normalize(target_text)
                if is_target_markdown(source_path):
                    changed[source_path] = "D"
                if is_target_markdown(target_path):
                    changed[target_path] = "A"
                continue
            path = normalize(path_text)
            if is_target_markdown(path):
                if "D" in code:
                    changed[path] = "D"
                elif "?" in code or "A" in code:
                    changed[path] = "A"
                else:
                    changed[path] = "M"
    return changed


def evaluate(root: Path, base_ref: str, require_companion_changed: bool) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    changed = changed_markdown(root, base_ref)
    changed_set = set(changed)
    checked_files: list[str] = []

    for rel, status in sorted(changed.items()):
        path = root / rel
        checked_files.append(rel)
        companion = companion_for(path)
        companion_rel = companion.relative_to(root).as_posix()
        companion_status = changed.get(companion_rel)
        if status == "D":
            if companion_status != "D":
                errors.append(f"{rel} was deleted without deleting its bilingual companion: {companion_rel}")
            continue
        if not path.exists():
            errors.append(f"Changed target Markdown file is missing from disk: {rel}")
            continue
        is_chinese = rel.endswith(CHINESE_SUFFIX)
        if not companion.exists():
            errors.append(f"{rel} is missing bilingual companion: {companion_rel}")
        elif require_companion_changed and companion_rel not in changed_set:
            errors.append(f"{rel} changed without changing its bilingual companion: {companion_rel}")
        if not is_chinese:
            text = path.read_text(encoding="utf-8", errors="strict")
            try:
                text.encode("ascii")
            except UnicodeEncodeError as exc:
                errors.append(f"{rel} English primary contains non-ASCII text at character index {exc.start}.")
        else:
            try:
                path.read_text(encoding="utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                errors.append(f"{rel} is not valid UTF-8: {exc}")

    if not changed:
        info.append("No changed target Markdown files under docs_bilingual/, openspec/, or docs/.")
    else:
        info.append("Changed target Markdown files must be bilingual pairs with ASCII English primaries.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "base_ref": base_ref,
        "require_companion_changed": require_companion_changed,
        "checked_files": checked_files,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "changed_target_markdown": len(changed),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check forward bilingual Markdown pair policy for docs_bilingual, openspec, and docs.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default="main", help="Base ref for changed-file detection.")
    parser.add_argument(
        "--allow-unchanged-companion",
        action="store_true",
        help="Only require companion existence, not same-diff companion updates.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = evaluate(Path(args.root), args.base_ref, not args.allow_unchanged_companion)
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
