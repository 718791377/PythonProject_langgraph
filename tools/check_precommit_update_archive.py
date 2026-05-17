#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "precommit_update_archive"
ARCHIVE_PREFIX = "openspec/changes/archive/"
ACTIVE_CHANGE_PREFIX = "openspec/changes/"


@dataclass(frozen=True)
class DiffEntry:
    status: str
    old_path: str | None
    new_path: str | None

    @property
    def paths(self) -> list[str]:
        return [path for path in (self.old_path, self.new_path) if path]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def parse_name_status(text: str) -> list[DiffEntry]:
    entries: list[DiffEntry] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        code = status[:1]
        if code in {"R", "C"} and len(parts) >= 3:
            entries.append(DiffEntry(status, norm(parts[1]), norm(parts[2])))
        elif len(parts) >= 2:
            path = norm(parts[1])
            entries.append(DiffEntry(status, path if code == "D" else None, None if code == "D" else path))
    return entries


def parse_porcelain(text: str) -> list[DiffEntry]:
    entries: list[DiffEntry] = []
    for raw in text.splitlines():
        if len(raw) < 4:
            continue
        status = raw[:2]
        rest = raw[3:]
        if " -> " in rest:
            old, new = rest.split(" -> ", 1)
            entries.append(DiffEntry(status, norm(old), norm(new)))
        else:
            path = norm(rest)
            deleted = "D" in status and "A" not in status
            entries.append(DiffEntry(status, path if deleted else None, None if deleted else path))
    return entries


def git_inside(root: Path) -> bool:
    git = shutil.which("git") or shutil.which("git.exe")
    if not git:
        return False
    result = run([git, "rev-parse", "--is-inside-work-tree"], root)
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def git_ref_exists(root: Path, ref: str) -> bool:
    return run(["git", "rev-parse", "--verify", "--quiet", ref], root).returncode == 0


def current_branch(root: Path) -> str:
    result = run(["git", "branch", "--show-current"], root)
    return result.stdout.strip() if result.returncode == 0 else ""


def merge_base(root: Path, ref: str) -> str | None:
    result = run(["git", "merge-base", "HEAD", ref], root)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def detect_base(root: Path, explicit_base: str | None = None) -> tuple[str | None, list[str]]:
    notes: list[str] = []
    if explicit_base:
        if git_ref_exists(root, explicit_base):
            return explicit_base, [f"Using explicit base {explicit_base}."]
        return None, [f"Explicit base {explicit_base} was not found; only staged, unstaged, and untracked files will be inspected."]
    branch = current_branch(root)
    if branch not in {"", "main", "master"}:
        for ref in ("main", "gitlab/main", "origin/main", "github/main", "master"):
            if git_ref_exists(root, ref):
                base = merge_base(root, ref)
                if base:
                    return base, [f"Using merge-base with {ref} as update/archive diff base."]
    if git_ref_exists(root, "HEAD^1"):
        return "HEAD^1", ["Using HEAD^1 as update/archive diff base."]
    notes.append("No git diff base detected; only staged, unstaged, and untracked files will be inspected.")
    return None, notes


def collect_entries(root: Path, explicit_base: str | None = None) -> tuple[list[DiffEntry], list[str]]:
    if not git_inside(root):
        return [], ["Git work tree not detected; precommit update/archive check is report-only."]
    entries: list[DiffEntry] = []
    base, notes = detect_base(root, explicit_base)
    if base:
        result = run(["git", "diff", "--name-status", "-M", f"{base}...HEAD"], root)
        if result.returncode == 0:
            entries.extend(parse_name_status(result.stdout))
    for command in (
        ["git", "diff", "--name-status", "-M", "--cached"],
        ["git", "diff", "--name-status", "-M"],
    ):
        result = run(command, root)
        if result.returncode == 0:
            entries.extend(parse_name_status(result.stdout))
    status = run(["git", "status", "--porcelain", "--untracked-files=all"], root)
    if status.returncode == 0:
        entries.extend(parse_porcelain(status.stdout))
    return list({(e.status, e.old_path, e.new_path): e for e in entries}.values()), notes


def changed_paths(entries: list[DiffEntry]) -> set[str]:
    return {path for entry in entries for path in entry.paths}


def changed_new_paths(entries: list[DiffEntry]) -> set[str]:
    return {entry.new_path for entry in entries if entry.new_path}


def active_change_id(path: str) -> str | None:
    path = norm(path)
    if not path.startswith(ACTIVE_CHANGE_PREFIX) or path.startswith(ARCHIVE_PREFIX):
        return None
    rest = path[len(ACTIVE_CHANGE_PREFIX) :]
    if "/" not in rest:
        return None
    change = rest.split("/", 1)[0]
    return change or None


def archived_change_id(path: str) -> str | None:
    path = norm(path)
    if not path.startswith(ARCHIVE_PREFIX):
        return None
    rest = path[len(ARCHIVE_PREFIX) :]
    if "/" not in rest:
        return None
    archive_name = rest.split("/", 1)[0]
    match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", archive_name)
    return match.group(1) if match else None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def task_counts(tasks_text: str) -> tuple[int, int]:
    total = 0
    checked = 0
    for line in tasks_text.splitlines():
        match = re.search(r"- \[([ xX])\]", line)
        if not match:
            continue
        total += 1
        if match.group(1).lower() == "x":
            checked += 1
    return total, checked


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match and match.group(1).strip() else None


def active_change_completed(root: Path, change: str) -> tuple[bool, dict[str, Any]]:
    change_dir = root / "openspec" / "changes" / change
    tasks_text = read_text(change_dir / "tasks.md")
    yaml_text = read_text(change_dir / ".openspec.yaml")
    total, checked = task_counts(tasks_text)
    deferred_reason = yaml_scalar(yaml_text, "x_archive_deferred_reason")
    deferred_follow_up = yaml_scalar(yaml_text, "x_archive_follow_up")
    completed = total > 0 and checked == total
    return completed, {
        "change": change,
        "tasks_total": total,
        "tasks_checked": checked,
        "deferred_reason": deferred_reason,
        "deferred_follow_up": deferred_follow_up,
    }


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "tools" / "ci" / "ci_test_manifest.json"
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def is_new_path_status(status: str) -> bool:
    return status[:1] in {"A", "R", "C"} or "??" in status


def check_new_tests_registered(entries: list[DiffEntry], manifest: dict[str, Any]) -> list[str]:
    registered = set(manifest.get("python_unittest") if isinstance(manifest.get("python_unittest"), list) else [])
    errors: list[str] = []
    for entry in entries:
        path = entry.new_path
        if not path or not is_new_path_status(entry.status):
            continue
        if path.startswith("test/") and path.endswith(".test.py"):
            name = Path(path).name
            if name not in registered:
                errors.append(f"{path}: new test file must be added to tools/ci/ci_test_manifest.json before commit.")
    return errors


def check_new_checkers_registered(root: Path, entries: list[DiffEntry]) -> list[str]:
    guard_text = read_text(root / "tools" / "run_openspec_guard.py")
    registry_text = read_text(root / "tools" / "safety_rule_script_backing_registry.json")
    errors: list[str] = []
    for entry in entries:
        path = entry.new_path
        if not path or not is_new_path_status(entry.status):
            continue
        if not (path.startswith("tools/check_") and path.endswith(".py")):
            continue
        name = Path(path).name
        if name not in guard_text and name not in registry_text:
            errors.append(
                f"{path}: new checker must be registered in tools/run_openspec_guard.py "
                "or tools/safety_rule_script_backing_registry.json before commit."
            )
    return errors


def check_completed_active_changes(root: Path, entries: list[DiffEntry]) -> tuple[list[str], list[dict[str, Any]]]:
    paths = changed_paths(entries)
    new_paths = changed_new_paths(entries)
    changed_active = sorted({change for path in paths if (change := active_change_id(path))})
    changed_archived = sorted({change for path in paths if (change := archived_change_id(path))})
    archived_set = set(changed_archived)
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for change in changed_active:
        completed, record = active_change_completed(root, change)
        record["archived_in_current_diff"] = change in archived_set
        record["active_change_paths_still_present"] = any(
            path.startswith(f"openspec/changes/{change}/") for path in new_paths
        )
        records.append(record)
        if not completed:
            continue
        if change in archived_set:
            continue
        if record.get("deferred_reason") and record.get("deferred_follow_up"):
            record["deferred_archive_allowed"] = True
            continue
        errors.append(
            f"openspec/changes/{change}: all tasks are checked but the change is not archived in this diff. "
            "Archive it before commit, or record both x_archive_deferred_reason and x_archive_follow_up for an explicit two-step exception."
        )
    return errors, records


def check(root: Path, explicit_base: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    entries, notes = collect_entries(root, explicit_base)
    manifest = load_manifest(root)
    paths = sorted(changed_paths(entries))
    errors: list[str] = []
    warnings: list[str] = []
    active_errors, active_records = check_completed_active_changes(root, entries)
    errors.extend(active_errors)
    errors.extend(check_new_tests_registered(entries, manifest))
    errors.extend(check_new_checkers_registered(root, entries))
    if not paths:
        notes.append("No local or branch changes detected for update/archive review.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": notes,
        "changed_paths": paths,
        "active_change_reviews": active_records,
        "policy": {
            "before_local_git_commit": True,
            "review_existing_files_for_required_updates": True,
            "archive_completed_openspec_changes_before_commit": True,
            "new_tests_must_be_registered_in_ci_manifest": True,
            "new_checkers_must_be_registered_before_commit": True,
        },
        "counts": {
            "changed_paths": len(paths),
            "active_change_reviews": len(active_records),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check required existing-file updates and OpenSpec archive state before local git commit."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base", default=None, help="Optional git diff base.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = check(Path(args.root), args.base)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload['check_name']}: {'ok' if payload['ok'] else 'failed'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for info in payload["info"]:
            print(f"INFO: {info}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
