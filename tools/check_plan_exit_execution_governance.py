#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "plan_exit_execution_governance"
DOC_PREFIXES = ("docs_bilingual/", "openspec/", "docs/")
DOC_EXACT_PATHS = {"完整提交流程.md"}
DOCS_BILINGUAL_PREFIX = "docs_bilingual/"


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def normalize_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    while value.startswith("./"):
        value = value[2:]
    return value


def changed_paths_for_commit(root: Path, commit: str) -> list[str]:
    result = run_git(root, ["diff-tree", "--no-commit-id", "--name-only", "-r", commit])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git diff-tree failed for {commit}")
    return [normalize_path(line) for line in result.stdout.splitlines() if line.strip()]


def range_commits(root: Path, base_ref: str, head_ref: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    result = run_git(root, ["rev-list", "--reverse", f"{base_ref}..{head_ref}"])
    if result.returncode != 0:
        errors.append(result.stderr.strip() or result.stdout.strip() or "git rev-list failed")
        return [], errors
    return [line.strip() for line in result.stdout.splitlines() if line.strip()], errors


def is_docs_path(path: str) -> bool:
    return path in DOC_EXACT_PATHS or path.startswith(DOC_PREFIXES)


def is_docs_bilingual_path(path: str) -> bool:
    return path.startswith(DOCS_BILINGUAL_PREFIX)


def evaluate(root: Path, base_ref: str, head_ref: str) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    commits, range_errors = range_commits(root, base_ref, head_ref)
    errors.extend(range_errors)

    commit_records: list[dict[str, Any]] = []
    all_changed_paths: list[str] = []
    for commit in commits:
        try:
            paths = changed_paths_for_commit(root, commit)
        except RuntimeError as exc:
            errors.append(str(exc))
            paths = []
        all_changed_paths.extend(paths)
        commit_records.append(
            {
                "commit": commit,
                "paths": paths,
                "docs_only": bool(paths) and all(is_docs_path(path) for path in paths),
                "touches_docs_bilingual": any(is_docs_bilingual_path(path) for path in paths),
                "non_docs_paths": [path for path in paths if not is_docs_path(path)],
            }
        )

    non_doc_paths = sorted({path for path in all_changed_paths if not is_docs_path(path)})
    docs_bilingual_paths = sorted({path for path in all_changed_paths if is_docs_bilingual_path(path)})
    docs_or_openspec_paths = sorted({path for path in all_changed_paths if path.startswith(("docs/", "openspec/"))})

    requires_governance_package = bool(non_doc_paths)
    if requires_governance_package:
        if not commits:
            errors.append("Non-document execution cannot be evaluated because the range has no commits.")
        first_record = commit_records[0] if commit_records else None
        if first_record and not first_record["docs_only"]:
            errors.append(
                "When a post-/plan task contains non-document changes, the first commit in the range must be a local governance package limited to docs_bilingual/, openspec/, or docs/."
            )
        if first_record and not first_record["touches_docs_bilingual"]:
            errors.append(
                "The first local governance package commit must update docs_bilingual/ first; openspec/ and docs/ may only be derived from that decision."
            )
        if not docs_bilingual_paths:
            errors.append("Non-document execution requires at least one docs_bilingual/ governance artifact in the range.")
    else:
        info.append("No non-document changed paths detected; post-/plan governance package rule is not required for this range.")

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "commits": len(commits),
            "changed_paths": len(set(all_changed_paths)),
            "non_doc_paths": len(non_doc_paths),
            "docs_bilingual_paths": len(docs_bilingual_paths),
            "docs_or_openspec_paths": len(docs_or_openspec_paths),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "requires_governance_package": requires_governance_package,
        "non_doc_paths": non_doc_paths,
        "docs_bilingual_paths": docs_bilingual_paths,
        "docs_or_openspec_paths": docs_or_openspec_paths,
        "commits": commit_records,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that post-/plan non-document execution starts with a local Comet governance package.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default="main", help="Base ref for the checked range.")
    parser.add_argument("--head-ref", default="HEAD", help="Head ref for the checked range.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = evaluate(Path(args.root), args.base_ref, args.head_ref)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("Post-/plan execution governance check passed.")
            for message in payload["info"]:
                print(f"  - {message}")
        else:
            print("Post-/plan execution governance check failed:")
            for error in payload["errors"]:
                print(f"  - {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
