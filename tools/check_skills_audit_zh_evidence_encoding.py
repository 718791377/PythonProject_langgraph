#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_zh_evidence_encoding"
MEMORY_DIR = Path("docs_bilingual/memory")
TARGET_GLOB = "skills_usage_audit_*zh-CN.md"
PROTECTED_FROM = date(2026, 6, 21)
ALWAYS_PROTECTED_NAMES = {
    "skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md",
    "skills_usage_audit_human_review_decision_template_2026-06-15.zh-CN.md",
}
LATEST_PROTECTED_PATTERNS = (
    "skills_usage_audit_evidence_index_*zh-CN.md",
    "skills_usage_audit_review_pending_continuation_*zh-CN.md",
    "skills_usage_audit_human_review_decision_*zh-CN.md",
    "skills_usage_audit_final_review_precheck_*zh-CN.md",
)

DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
QUESTION_RUN_RE = re.compile(r"\?{3,}")
HAN_RE = re.compile(r"[\u4e00-\u9fff]")

# High-signal characters frequently produced when UTF-8 Chinese text is decoded
# through a legacy Windows/GBK path.  They are intentionally kept as codepoints
# so this checker stays ASCII-source-safe and does not copy corrupted examples
# back into source files.
MOJIBAKE_MARKERS = tuple(
    chr(codepoint)
    for codepoint in (
        0x951B,
        0x9286,
        0x9428,
        0x7480,
        0x9352,
        0x8930,
        0x6FC2,
        0x4E7B,
        0x4E7C,
        0x93C8,
        0x935A,
        0x93C0,
    )
)
MOJIBAKE_PHRASES = tuple(
    "".join(chr(codepoint) for codepoint in phrase)
    for phrase in (
        (0x935A, 0xE5E2),  # common mojibake prefix containing a private-use continuation
        (0x93C8, 0xE5B0),  # common mojibake prefix containing a private-use continuation
    )
)


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def extract_date(path: Path) -> date | None:
    match = DATE_RE.search(path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def is_target_rel(path: str) -> bool:
    rel = path.replace("\\", "/")
    return rel.startswith(f"{MEMORY_DIR.as_posix()}/") and fnmatch.fnmatch(Path(rel).name, TARGET_GLOB)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    git = shutil.which("git") or shutil.which("git.exe") or "git"
    return subprocess.run(
        [git, *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def add_git_paths(paths: set[str], root: Path, args: list[str]) -> None:
    result = run_git(root, args)
    if result.returncode != 0:
        return
    for line in result.stdout.splitlines():
        rel = line.strip().replace("\\", "/")
        if is_target_rel(rel):
            paths.add(rel)


def choose_diff_base(root: Path, requested_base: str | None) -> str | None:
    if requested_base:
        return requested_base
    branch = run_git(root, ["branch", "--show-current"]).stdout.strip()
    if branch and branch != "main":
        main_check = run_git(root, ["rev-parse", "--verify", "main"])
        if main_check.returncode == 0:
            merge_base = run_git(root, ["merge-base", "HEAD", "main"])
            if merge_base.returncode == 0 and merge_base.stdout.strip():
                return merge_base.stdout.strip()
    parent = run_git(root, ["rev-parse", "--verify", "HEAD^1"])
    if parent.returncode == 0 and parent.stdout.strip():
        return "HEAD^1"
    return None


def changed_or_new_target_paths(root: Path, requested_base: str | None = None) -> set[str]:
    inside = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
        return set()

    paths: set[str] = set()
    base = choose_diff_base(root, requested_base)
    if base:
        add_git_paths(paths, root, ["diff", "--name-only", "--diff-filter=ACMRTUXB", "-M", f"{base}...HEAD", "--", MEMORY_DIR.as_posix()])
    add_git_paths(paths, root, ["diff", "--name-only", "--diff-filter=ACMRTUXB", "-M", "--", MEMORY_DIR.as_posix()])
    add_git_paths(paths, root, ["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "-M", "--", MEMORY_DIR.as_posix()])
    add_git_paths(paths, root, ["ls-files", "--others", "--exclude-standard", "--", MEMORY_DIR.as_posix()])
    return paths


def latest_existing(memory_root: Path, pattern: str) -> Path | None:
    matches = sorted(memory_root.glob(pattern), key=lambda item: item.name)
    return matches[-1] if matches else None


def active_current_paths(root: Path, paths: list[Path]) -> set[str]:
    memory_root = root / MEMORY_DIR
    active: set[str] = set()
    for path in paths:
        if path.name in ALWAYS_PROTECTED_NAMES:
            active.add(norm(path.relative_to(root)))
        parsed = extract_date(path)
        if parsed is None or parsed >= PROTECTED_FROM:
            active.add(norm(path.relative_to(root)))
    for pattern in LATEST_PROTECTED_PATTERNS:
        latest = latest_existing(memory_root, pattern)
        if latest is not None:
            active.add(norm(latest.relative_to(root)))
    return active


def protection_reasons(path: Path, root: Path, active_paths: set[str], changed_paths: set[str]) -> list[str]:
    rel = norm(path.relative_to(root))
    reasons: list[str] = []
    if rel in active_paths:
        reasons.append("active_current_or_future_evidence")
    if rel in changed_paths:
        reasons.append("changed_or_new_target_file")
    return reasons


def read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8-sig", errors="strict"), None
    except UnicodeDecodeError as exc:
        return None, f"not_valid_utf8:{exc}"
    except OSError as exc:
        return None, f"unreadable:{type(exc).__name__}:{exc}"


def find_encoding_issues(text: str) -> list[str]:
    issues: list[str] = []
    if "\ufffd" in text:
        issues.append("unicode_replacement_character")
    if QUESTION_RUN_RE.search(text):
        issues.append("repeated_ascii_question_mark_placeholder")
    elif text.count("?") > 8:
        issues.append("excessive_ascii_question_mark_placeholders")
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        issues.append("known_utf8_as_legacy_codepage_mojibake_marker")
    if any(phrase in text for phrase in MOJIBAKE_PHRASES):
        issues.append("known_utf8_as_legacy_codepage_mojibake_phrase")
    return sorted(set(issues))


def build_finding(path: Path, root: Path, reasons: list[str]) -> dict[str, Any]:
    rel = norm(path.relative_to(root))
    text, read_error = read_text(path)
    if read_error:
        issues = [read_error]
        question_count = None
        han_count = None
    else:
        text = text or ""
        issues = find_encoding_issues(text)
        question_count = text.count("?")
        han_count = len(HAN_RE.findall(text))
    return {
        "path": rel,
        "protected": bool(reasons),
        "protection_reasons": reasons,
        "issues": issues,
        "question_mark_count": question_count,
        "han_character_count": han_count,
        "raw_content_retained": False,
    }


def scan(root: Path, base: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    memory_root = root / MEMORY_DIR
    errors: list[str] = []
    warning_messages: list[str] = []
    protected_findings: list[dict[str, Any]] = []
    legacy_findings: list[dict[str, Any]] = []

    paths = sorted(memory_root.glob(TARGET_GLOB), key=lambda item: norm(item.relative_to(root))) if memory_root.exists() else []
    if not paths:
        errors.append(f"{MEMORY_DIR.as_posix()}: no {TARGET_GLOB} evidence files found.")

    changed_paths = changed_or_new_target_paths(root, base)
    active_paths = active_current_paths(root, paths)

    for path in paths:
        reasons = protection_reasons(path, root, active_paths, changed_paths)
        finding = build_finding(path, root, reasons)
        if not finding["issues"]:
            continue
        if finding["protected"]:
            protected_findings.append(finding)
            errors.append(
                f"{finding['path']}: protected/current Skills audit zh-CN evidence has encoding issues "
                f"({', '.join(finding['protection_reasons'])}): "
                + ", ".join(finding["issues"])
            )
        else:
            legacy_findings.append(finding)

    if legacy_findings:
        sample = ", ".join(item["path"] for item in legacy_findings[:8])
        warning_messages.append(
            "legacy_mojibake_candidates_detected: "
            f"{len(legacy_findings)} untouched legacy Skills audit zh-CN evidence file(s) are reported without blocking; "
            f"sample={sample}"
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "policy": {
            "target_glob": f"{MEMORY_DIR.as_posix()}/{TARGET_GLOB}",
            "protected_from": PROTECTED_FROM.isoformat(),
            "always_protected_names": sorted(ALWAYS_PROTECTED_NAMES),
            "latest_protected_patterns": list(LATEST_PROTECTED_PATTERNS),
            "changed_or_new_target_files_fail_closed": True,
            "legacy_unchanged_evidence_warns_only": True,
            "raw_content_retained": False,
        },
        "changed_or_new_target_paths": sorted(changed_paths),
        "active_current_paths": sorted(active_paths),
        "errors": errors,
        "warnings": warning_messages,
        "protected_findings": protected_findings,
        "legacy_findings_sample": legacy_findings[:10],
        "counts": {
            "checked_paths": len(paths),
            "active_current_paths": len(active_paths),
            "changed_or_new_target_paths": len(changed_paths),
            "protected_findings": len(protected_findings),
            "legacy_findings": len(legacy_findings),
            "errors": len(errors),
            "warnings": len(warning_messages),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify current, future, and changed Codex Skills usage audit zh-CN evidence is "
            "UTF-8-readable and not retained as mojibake or placeholder question marks."
        )
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base", default=None, help="Optional git diff base for changed/new target detection.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = scan(Path(args.root), args.base)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(
            f"{CHECK_NAME}: ok checked={report['counts']['checked_paths']} "
            f"legacy_warnings={report['counts']['legacy_findings']}"
        )
        for warning in report["warnings"]:
            print(f"WARNING: {warning}")
    else:
        print(f"{CHECK_NAME}: failed")
        for error in report["errors"]:
            print(f"ERROR: {error}")
        for warning in report["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
