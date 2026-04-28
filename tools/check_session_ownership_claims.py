#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "session_ownership_claims"
DEFAULT_CLAIMS_SUBDIR = Path(".omx/session-claims")


@dataclass(frozen=True)
class Claim:
    file: Path
    containing_worktree: Path
    session_id: str
    status: str
    branch: str
    task_type: str
    openspec_changes: tuple[str, ...]
    paths: tuple[str, ...]


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_worktree_list(output: str) -> list[dict[str, str]]:
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        if " " in line:
            key, value = line.split(" ", 1)
        else:
            key, value = line, "true"
        if key == "worktree" and current:
            worktrees.append(current)
            current = {}
        current[key] = value
    if current:
        worktrees.append(current)
    return worktrees


def branch_name(worktree: dict[str, str]) -> str | None:
    branch = worktree.get("branch")
    if not branch:
        return None
    prefix = "refs/heads/"
    return branch[len(prefix) :] if branch.startswith(prefix) else branch


def normalize_repo_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/") or "."


def path_overlaps(left: str, right: str) -> bool:
    left = normalize_repo_path(left)
    right = normalize_repo_path(right)
    if left == "." or right == ".":
        return True
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def parse_status_porcelain(output: str) -> list[str]:
    paths: list[str] = []
    for raw_line in output.splitlines():
        if not raw_line.strip() or raw_line.startswith("##"):
            continue
        path_text = raw_line[3:] if len(raw_line) > 3 else ""
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append(normalize_repo_path(path_text))
    return paths


def require_string_list(data: dict[str, Any], key: str, claim_file: Path, errors: list[str]) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        value = []
    if not isinstance(value, list):
        errors.append(f"{claim_file}: `{key}` must be a list of strings.")
        return ()
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{claim_file}: `{key}` contains an invalid entry: {item!r}.")
            continue
        result.append(normalize_repo_path(item) if key == "paths" else item.strip())
    return tuple(result)


def load_claim_file(claim_file: Path, containing_worktree: Path, expected_branch: str | None, errors: list[str]) -> Claim | None:
    try:
        data = json.loads(claim_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        errors.append(f"{claim_file}: invalid JSON: {exc}.")
        return None
    except OSError as exc:
        errors.append(f"{claim_file}: cannot read claim file: {exc}.")
        return None

    if not isinstance(data, dict):
        errors.append(f"{claim_file}: claim must be a JSON object.")
        return None
    if data.get("schema_version") != 1:
        errors.append(f"{claim_file}: `schema_version` must be 1.")

    status = data.get("status", "active")
    if status != "active":
        return None

    session_id = data.get("session_id")
    branch = data.get("branch")
    task_type = data.get("task_type")
    for key, value in (("session_id", session_id), ("branch", branch), ("task_type", task_type)):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{claim_file}: `{key}` must be a non-empty string.")

    if isinstance(branch, str) and branch.strip() and expected_branch and branch.strip() != expected_branch:
        errors.append(
            f"{claim_file}: active claim branch `{branch.strip()}` does not match containing worktree branch `{expected_branch}`."
        )

    declared_worktree = data.get("worktree")
    if isinstance(declared_worktree, str) and declared_worktree.strip():
        declared_path = Path(declared_worktree)
        if not declared_path.is_absolute():
            declared_path = containing_worktree / declared_path
        try:
            if declared_path.resolve() != containing_worktree.resolve():
                errors.append(
                    f"{claim_file}: declared `worktree` does not match containing worktree {containing_worktree}."
                )
        except OSError:
            errors.append(f"{claim_file}: declared `worktree` cannot be resolved.")

    openspec_changes = require_string_list(data, "openspec_changes", claim_file, errors)
    paths = require_string_list(data, "paths", claim_file, errors)
    if not openspec_changes and not paths:
        errors.append(f"{claim_file}: active claim must declare at least one OpenSpec change or path scope.")

    return Claim(
        file=claim_file,
        containing_worktree=containing_worktree,
        session_id=session_id.strip() if isinstance(session_id, str) else "",
        status="active",
        branch=branch.strip() if isinstance(branch, str) else "",
        task_type=task_type.strip() if isinstance(task_type, str) else "",
        openspec_changes=openspec_changes,
        paths=paths,
    )


def discover_claims(
    worktrees: list[dict[str, str]],
    claims_subdir: Path,
    errors: list[str],
) -> list[Claim]:
    claims: list[Claim] = []
    for worktree in worktrees:
        raw_path = worktree.get("worktree")
        if not raw_path:
            continue
        worktree_path = Path(raw_path).resolve()
        claim_dir = worktree_path / claims_subdir
        if not claim_dir.exists():
            continue
        if not claim_dir.is_dir():
            errors.append(f"{claim_dir}: session claims path exists but is not a directory.")
            continue
        for claim_file in sorted(claim_dir.glob("*.json")):
            claim = load_claim_file(claim_file, worktree_path, branch_name(worktree), errors)
            if claim is not None:
                claims.append(claim)
    return claims


def summarize_claim(claim: Claim) -> dict[str, object]:
    return {
        "file": str(claim.file),
        "worktree": str(claim.containing_worktree),
        "session_id": claim.session_id,
        "branch": claim.branch,
        "task_type": claim.task_type,
        "openspec_changes": list(claim.openspec_changes),
        "paths": list(claim.paths),
    }


def run_check(root: Path, *, main_branch: str, claims_subdir: Path, allow_current_dirty: bool) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    top_result = run_git(root, ["rev-parse", "--show-toplevel"])
    if top_result.returncode != 0:
        errors.append(f"Not a Git worktree: {root}")
        return payload(root, claims_subdir, [], [], errors, warnings, info)

    current_root = Path(top_result.stdout.strip()).resolve()
    list_result = run_git(current_root, ["worktree", "list", "--porcelain"])
    if list_result.returncode != 0:
        errors.append("Unable to list Git worktrees.")
        if list_result.stderr.strip():
            errors.append(list_result.stderr.strip())
        return payload(root, claims_subdir, [], [], errors, warnings, info)

    worktrees = parse_worktree_list(list_result.stdout)
    claims = discover_claims(worktrees, claims_subdir, errors)

    claims_by_change: dict[str, list[Claim]] = {}
    for claim in claims:
        for change in claim.openspec_changes:
            claims_by_change.setdefault(change, []).append(claim)
    for change, owners in sorted(claims_by_change.items()):
        unique_files = sorted({str(owner.file) for owner in owners})
        if len(unique_files) > 1:
            errors.append(
                f"OpenSpec change `{change}` is claimed by multiple active sessions: {', '.join(unique_files)}. Serialize ownership before continuing."
            )

    for index, left in enumerate(claims):
        for right in claims[index + 1 :]:
            if left.file == right.file:
                continue
            for left_path in left.paths:
                for right_path in right.paths:
                    if path_overlaps(left_path, right_path):
                        errors.append(
                            "Path scope overlap between active session claims: "
                            f"`{left_path}` in {left.file} overlaps `{right_path}` in {right.file}."
                        )

    current_worktree = next(
        (item for item in worktrees if Path(item.get("worktree", "")).resolve() == current_root),
        {},
    )
    current_branch = branch_name(current_worktree)
    status_result = run_git(current_root, ["status", "--porcelain", "--untracked-files=all"])
    current_dirty_paths = parse_status_porcelain(status_result.stdout) if status_result.returncode == 0 else []
    current_claims = [claim for claim in claims if claim.containing_worktree.resolve() == current_root]

    if allow_current_dirty and current_dirty_paths and current_branch != main_branch and not current_claims:
        errors.append(
            f"Current dirty feature worktree {current_root} has no active session ownership claim under "
            f"{(current_root / claims_subdir).as_posix()}. Declare the OpenSpec change or path scope before continuing."
        )

    if not claims:
        info.append("No active local session ownership claims were detected.")
    else:
        info.append(f"Active local session ownership claims detected: {len(claims)}.")

    return payload(root, claims_subdir, worktrees, claims, errors, warnings, info)


def payload(
    root: Path,
    claims_subdir: Path,
    worktrees: list[dict[str, str]],
    claims: list[Claim],
    errors: list[str],
    warnings: list[str],
    info: list[str],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "claims_subdir": claims_subdir.as_posix(),
        "worktrees": [
            {
                "path": str(Path(item.get("worktree", "")).resolve()) if item.get("worktree") else "",
                "branch": branch_name(item),
                "head": item.get("HEAD"),
            }
            for item in worktrees
        ],
        "active_claims": [summarize_claim(claim) for claim in claims],
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "worktrees": len(worktrees),
            "active_claims": len(claims),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local session ownership claims without modifying the repository."
    )
    parser.add_argument("--root", default=".", help="Repository or worktree root to inspect.")
    parser.add_argument("--main-branch", default="main", help="Local main branch name.")
    parser.add_argument(
        "--claims-subdir",
        default=DEFAULT_CLAIMS_SUBDIR.as_posix(),
        help="Repository-relative local directory containing session claim JSON files.",
    )
    parser.add_argument(
        "--allow-current-dirty",
        action="store_true",
        help="Require an active claim when the current non-main worktree is dirty.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    result = run_check(
        Path(args.root),
        main_branch=args.main_branch,
        claims_subdir=Path(args.claims_subdir),
        allow_current_dirty=args.allow_current_dirty,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["info"]:
            print(message)
        for message in result["warnings"]:
            print(f"WARNING: {message}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
