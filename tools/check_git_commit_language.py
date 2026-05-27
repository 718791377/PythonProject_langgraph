#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "git_commit_language"
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
ZERO_SHA_RE = re.compile(r"^0{40}$")


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def subject_has_chinese(subject: str) -> bool:
    return bool(CJK_RE.search(subject))


def commit_ref_exists(root: Path, ref: str) -> bool:
    result = run_git(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    return result.returncode == 0


def fallback_base_refs(base_ref: str) -> list[str]:
    candidates: list[str] = []
    for env_name in (
        "CI_MERGE_REQUEST_DIFF_BASE_SHA",
        "CI_MERGE_REQUEST_TARGET_BRANCH_SHA",
        "CI_COMMIT_BEFORE_SHA",
    ):
        value = os.environ.get(env_name, "").strip()
        if value and not ZERO_SHA_RE.fullmatch(value):
            candidates.append(value)
    if "/" not in base_ref:
        candidates.extend(
            [
                f"origin/{base_ref}",
                f"gitlab/{base_ref}",
                f"refs/remotes/origin/{base_ref}",
                f"refs/remotes/gitlab/{base_ref}",
            ]
        )
    return candidates


def subjects_from_range(root: Path, base_ref: str, head_ref: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    candidates = [base_ref]
    if not commit_ref_exists(root, base_ref):
        candidates.extend(fallback_base_refs(base_ref))
    seen: set[str] = set()
    last_error = ""
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if not commit_ref_exists(root, candidate):
            continue
        result = run_git(root, ["log", "--format=%s", f"{candidate}..{head_ref}"])
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()], errors
        last_error = result.stderr.strip() or result.stdout.strip() or f"git log failed for {candidate}..{head_ref}"
    if last_error:
        errors.append(last_error)
    else:
        fallback_list = ", ".join(fallback_base_refs(base_ref))
        errors.append(
            f"Cannot resolve base ref '{base_ref}' for commit-language range; tried CI fallback refs and remotes: {fallback_list}"
        )
    return [], errors


def evaluate_subjects(root: Path, subjects: list[str], source: str) -> dict[str, Any]:
    errors: list[str] = []
    checked: list[dict[str, Any]] = []
    for subject in subjects:
        ok = subject_has_chinese(subject)
        checked.append({"subject": subject, "ok": ok})
        if not ok:
            errors.append(f"Commit subject must contain Chinese text: {subject}")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root.resolve()),
        "source": source,
        "commits": checked,
        "errors": errors,
        "warnings": [],
        "info": ["Commit subjects may use ASCII conventional prefixes, but the subject must contain Chinese text."],
        "counts": {"commits": len(checked), "errors": len(errors)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Require local Git commit subjects to contain Chinese text.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default="main", help="Base ref for commit range checks.")
    parser.add_argument("--head-ref", default="HEAD", help="Head ref for commit range checks.")
    parser.add_argument("--message", default=None, help="Single commit message subject or full message to check.")
    parser.add_argument("--message-file", default=None, help="Commit message file from a commit-msg hook.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    root = Path(args.root)
    source = "range"
    subjects: list[str]
    range_errors: list[str] = []
    if args.message_file:
        source = "message_file"
        text = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
        subjects = [next((line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")), "")]
    elif args.message is not None:
        source = "message"
        subjects = [next((line.strip() for line in args.message.splitlines() if line.strip()), "")]
    else:
        subjects, range_errors = subjects_from_range(root, args.base_ref, args.head_ref)
    payload = evaluate_subjects(root, subjects, source)
    if range_errors:
        payload["ok"] = False
        payload["errors"].extend(range_errors)
        payload["counts"]["errors"] = len(payload["errors"])
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
