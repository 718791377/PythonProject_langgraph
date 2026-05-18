#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_output_retention"
RAW_AUDIT_JSON_PATTERNS = (
    re.compile(r"^skills-usage-(?:audit|baseline|warning|report)[\w.-]*\.json$", re.IGNORECASE),
)


def norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    git = shutil.which("git") or shutil.which("git.exe") or "git"
    return subprocess.run(
        [git, *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def git_paths(root: Path, args: list[str]) -> list[str]:
    result = run_git(root, args)
    if result.returncode != 0:
        return []
    return [norm(line) for line in result.stdout.splitlines() if line.strip()]


def parse_status_paths(status_text: str) -> list[str]:
    paths: list[str] = []
    for raw in status_text.splitlines():
        if len(raw) < 4:
            continue
        path = raw[3:]
        if " -> " in path:
            _, path = path.split(" -> ", 1)
        paths.append(norm(path))
    return paths


def git_status_paths(root: Path) -> list[str]:
    result = run_git(root, ["status", "--porcelain", "--untracked-files=all"])
    if result.returncode != 0:
        return []
    return parse_status_paths(result.stdout)


def is_raw_audit_json(path: str) -> bool:
    name = Path(path).name
    return any(pattern.match(name) for pattern in RAW_AUDIT_JSON_PATTERNS)


def classify_violation(path: str, source: str) -> list[dict[str, Any]]:
    normalized = norm(path)
    violations: list[dict[str, Any]] = []
    if normalized == ".tmp" or normalized.startswith(".tmp/"):
        violations.append(
            {
                "path": normalized,
                "source": source,
                "reason": "tmp_audit_artifact_retained",
                "policy": "audit_tmp_outputs_are_local_only_and_must_not_enter_git",
            }
        )
    if is_raw_audit_json(normalized):
        violations.append(
            {
                "path": normalized,
                "source": source,
                "reason": "raw_audit_json_retained",
                "policy": "raw_skills_usage_audit_json_reports_are_local_only_commit_sanitized_markdown_for_long_term_evidence",
            }
        )
    return violations


def build_report(root: Path) -> dict[str, Any]:
    tracked_paths = git_paths(root, ["ls-files"])
    changed_paths = git_status_paths(root)
    violations: list[dict[str, Any]] = []
    for path in tracked_paths:
        violations.extend(classify_violation(path, "tracked"))
    for path in changed_paths:
        violations.extend(classify_violation(path, "changed_or_untracked"))
    deduped = {
        (item["path"], item["source"], item["reason"]): item
        for item in violations
    }
    violations = list(deduped.values())
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not violations,
        "root": str(root),
        "policy": {
            "tmp_outputs_local_only": True,
            "raw_audit_json_local_only": True,
            "long_term_evidence_format": "sanitized_markdown_summary",
        },
        "violations": violations,
        "counts": {
            "tracked_paths": len(tracked_paths),
            "changed_paths": len(changed_paths),
            "violations": len(violations),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Block retained raw Skills usage audit outputs from Git evidence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = build_report(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print("skills_audit_output_retention: ok")
    else:
        for violation in report["violations"]:
            print(f"ERROR: {violation['reason']}: {violation['path']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
