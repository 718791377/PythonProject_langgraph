#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_PREFIX = "openspec/changes/archive/"
CODE_CLASSES = {"code", "runtime", "mixed", "tooling", "ci"}
DOC_CLASSES = {"docs", "doc", "spec", "governance", "memory", "research", "plan", "status"}
CODE_SUFFIXES = {
    ".bat",
    ".c",
    ".cmd",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".ps1",
    ".psm1",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".ts",
    ".tsx",
}
CODE_HINTS = re.compile(
    r"\b(code|runtime|script|helper|tools?|tooling|tests?|checker|guard|CI)\b|"
    r"\.(bat|cmd|mjs|ps1|py)\b",
    re.IGNORECASE,
)


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
            entries.append(DiffEntry(status, path if "D" in status and "A" not in status else None, None if "D" in status and "A" not in status else path))
    return entries


def git_ref_exists(root: Path, ref: str) -> bool:
    return run(["git", "rev-parse", "--verify", "--quiet", ref], root).returncode == 0


def git_inside(root: Path) -> bool:
    git = shutil.which("git") or shutil.which("git.exe")
    if not git:
        return False
    result = run([git, "rev-parse", "--is-inside-work-tree"], root)
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def current_branch(root: Path) -> str:
    result = run(["git", "branch", "--show-current"], root)
    return result.stdout.strip() if result.returncode == 0 else ""


def merge_base(root: Path, ref: str) -> str | None:
    result = run(["git", "merge-base", "HEAD", ref], root)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def detect_base(root: Path) -> tuple[str | None, list[str]]:
    notes: list[str] = []
    for key in ("CI_MERGE_REQUEST_DIFF_BASE_SHA", "CI_MERGE_REQUEST_TARGET_BRANCH_SHA"):
        value = os.environ.get(key, "").strip()
        if value and git_ref_exists(root, value):
            return value, [f"Using {key} as archive evidence diff base."]
    branch = current_branch(root)
    if branch not in {"", "main", "master"}:
        for ref in ("gitlab/main", "origin/main", "github/main", "main", "master"):
            if git_ref_exists(root, ref):
                base = merge_base(root, ref)
                if base:
                    return base, [f"Using merge-base with {ref} as archive evidence diff base."]
    if git_ref_exists(root, "HEAD^1"):
        return "HEAD^1", ["Using HEAD^1 as archive evidence diff base."]
    notes.append("No git diff base detected; only working-tree changes will be inspected.")
    return None, notes


def collect_entries(root: Path) -> tuple[list[DiffEntry], list[str]]:
    if not git_inside(root):
        return [], ["Git work tree not detected; archive code evidence check is report-only."]
    entries: list[DiffEntry] = []
    base, notes = detect_base(root)
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


def archive_dir(path: str) -> str | None:
    path = norm(path)
    if not path.startswith(ARCHIVE_PREFIX):
        return None
    rest = path[len(ARCHIVE_PREFIX) :]
    if "/" not in rest:
        return None
    name = rest.split("/", 1)[0]
    return f"{ARCHIVE_PREFIX}{name}" if re.match(r"^\d{4}-\d{2}-\d{2}-.+", name) else None


def code_evidence(path: str) -> bool:
    path = norm(path)
    if path.startswith(("docs_bilingual/", "openspec/")):
        return False
    if path == ".gitlab-ci.yml" or path.startswith((".github/workflows/", ".githooks/")):
        return True
    if path.startswith("test/") and Path(path).suffix.lower() not in {".md", ".txt"}:
        return True
    return Path(path).suffix.lower() in CODE_SUFFIXES


def existing_declared_code_evidence(root: Path, declared: list[str]) -> list[str]:
    paths: list[str] = []
    for path in declared:
        normalized = norm(path)
        if code_evidence(normalized) and (root / normalized).is_file():
            paths.append(normalized)
    return sorted(set(paths))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def archive_text(root: Path, directory: str) -> str:
    base = root / directory
    chunks: list[str] = []
    for path in sorted(base.rglob("*")) if base.exists() else []:
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml"}:
            chunks.append(read_text(path))
    return "\n".join(chunks)


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match and match.group(1).strip() else None


def yaml_bool(text: str, key: str) -> bool | None:
    value = (yaml_scalar(text, key) or "").lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    return None


def yaml_list(text: str, key: str) -> list[str]:
    inline = yaml_scalar(text, key)
    if inline and inline.startswith("[") and inline.endswith("]"):
        return [norm(item.strip().strip("\"'")) for item in inline[1:-1].split(",") if item.strip()]
    values: list[str] = []
    in_block = False
    base_indent = 0
    for line in text.splitlines():
        if not in_block:
            match = re.match(rf"^(\s*){re.escape(key)}\s*:\s*$", line)
            if match:
                in_block = True
                base_indent = len(match.group(1))
            continue
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent:
            break
        item = line.strip()
        if item.startswith("-"):
            values.append(norm(item[1:].strip().strip("\"'")))
    return values


def code_required(yaml_text: str, text: str) -> tuple[bool, list[str]]:
    explicit = yaml_bool(yaml_text, "x_code_evidence_required")
    if explicit is not None:
        return explicit, [f"x_code_evidence_required={str(explicit).lower()}"]
    change_class = (yaml_scalar(yaml_text, "x_change_class") or yaml_scalar(yaml_text, "change_class") or "").lower()
    if change_class in CODE_CLASSES:
        return True, [f"x_change_class={change_class}"]
    if change_class in DOC_CLASSES:
        return False, [f"x_change_class={change_class}"]
    if CODE_HINTS.search(text):
        return True, ["inferred code/runtime/script/test wording"]
    return False, ["no code-class marker detected"]


def check(root: Path) -> dict:
    root = root.resolve()
    entries, notes = collect_entries(root)
    archive_dirs = sorted({directory for entry in entries for path in entry.paths if (directory := archive_dir(path)) and not entry.status.startswith("D")})
    changed_evidence_paths = sorted({path for entry in entries for path in entry.paths if code_evidence(path)})
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "openspec_code_archive_evidence",
        "ok": True,
        "root": str(root),
        "errors": [],
        "warnings": [],
        "info": notes,
        "archives": [],
        "code_evidence_paths": changed_evidence_paths,
        "changed_code_evidence_paths": changed_evidence_paths,
        "declared_existing_code_evidence_paths": [],
        "counts": {
            "archive_dirs": len(archive_dirs),
            "code_required": 0,
            "code_evidence_paths": len(changed_evidence_paths),
            "changed_code_evidence_paths": len(changed_evidence_paths),
            "declared_existing_code_evidence_paths": 0,
            "errors": 0,
            "warnings": 0,
        },
    }
    if not archive_dirs:
        payload["info"].append("No newly archived OpenSpec change directories detected in the current diff.")
        return payload

    for directory in archive_dirs:
        yaml_text = read_text(root / directory / ".openspec.yaml")
        text = archive_text(root, directory)
        declared = yaml_list(yaml_text, "x_code_evidence_paths")
        required, reasons = code_required(yaml_text, text)
        changed_matching = sorted(set(declared or changed_evidence_paths).intersection(changed_evidence_paths))
        existing_declared = existing_declared_code_evidence(root, declared)
        matching = sorted(set(changed_matching + existing_declared))
        payload["declared_existing_code_evidence_paths"] = sorted(
            set(payload["declared_existing_code_evidence_paths"] + existing_declared)
        )
        record = {
            "archive_dir": directory,
            "code_required": required,
            "reasons": reasons,
            "declared_code_evidence_paths": declared,
            "changed_matching_code_evidence_paths": changed_matching,
            "existing_declared_code_evidence_paths": existing_declared,
            "matching_code_evidence_paths": matching,
            "ok": True,
        }
        if required:
            payload["counts"]["code_required"] += 1
            if not matching:
                record["ok"] = False
                if declared:
                    payload["errors"].append(
                        f"{directory}: declared x_code_evidence_paths did not change in this branch "
                        "and do not exist as source/test/CI evidence paths in the current repository."
                    )
                else:
                    payload["errors"].append(
                        f"{directory}: code-class OpenSpec archive has no code/test evidence in the current branch diff. "
                        "Land source or test changes before archiving, declare x_code_evidence_paths for code that already landed, "
                        "or mark the change as x_change_class: docs when it is truly docs-only."
                    )
        payload["archives"].append(record)

    payload["counts"]["errors"] = len(payload["errors"])
    payload["counts"]["warnings"] = len(payload["warnings"])
    payload["counts"]["declared_existing_code_evidence_paths"] = len(payload["declared_existing_code_evidence_paths"])
    payload["ok"] = not payload["errors"]
    if payload["ok"]:
        payload["info"].append("OpenSpec archive code evidence check passed.")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Require code/test evidence before archiving code-class OpenSpec changes.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = check(Path(args.root))
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
