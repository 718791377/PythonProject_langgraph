#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


CHECK_NAME = "session_ownership_claims"
DEFAULT_CLAIMS_SUBDIR = Path(".omx/session-claims")
DEFAULT_GUARD_SCANNED_DIRS = ("docs_bilingual", "openspec", "tools")
PRECHECK_STATE_ORDER = {
    "unclaimed": 0,
    "claimed-not-started": 1,
    "in-progress": 2,
}


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


def is_gitlab_ci_detached_checkout() -> bool:
    return bool(os.environ.get("GITLAB_CI") and os.environ.get("CI_COMMIT_SHA"))


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


def slugify(value: str) -> str:
    value = value.lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9/._-]+", "-", value)
    value = re.sub(r"[-_./]+", "-", value)
    return value.strip("-")


def add_precheck_term(terms: set[str], value: str | None) -> None:
    if not value:
        return
    normalized = slugify(value)
    if normalized:
        terms.add(normalized)


def matches_terms(value: str, terms: set[str]) -> bool:
    if not terms:
        return False
    normalized = slugify(value)
    return any(term and term in normalized for term in terms)


def git_output_lines(root: Path, args: list[str]) -> list[str]:
    result = run_git(root, args)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def branch_ahead_count(root: Path, main_branch: str, branch: str | None) -> int:
    if not branch or branch == main_branch:
        return 0
    result = run_git(root, ["rev-list", "--left-right", "--count", f"{main_branch}...{branch}"])
    if result.returncode != 0:
        return 0
    parts = result.stdout.split()
    if len(parts) < 2:
        return 0
    try:
        return int(parts[1])
    except ValueError:
        return 0


def advance_state(left: str, right: str) -> str:
    return right if PRECHECK_STATE_ORDER[right] > PRECHECK_STATE_ORDER[left] else left


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


def parse_gitlab_remote(remote_url: str) -> tuple[str, str] | None:
    remote_url = remote_url.strip()
    if not remote_url:
        return None
    ssh_match = re.match(r"git@(?P<host>[^:]+):(?P<project>.+?)(?:\.git)?$", remote_url)
    if ssh_match:
        return ssh_match.group("host"), ssh_match.group("project")
    https_match = re.match(r"https://(?P<host>[^/]+)/(?P<project>.+?)(?:\.git)?$", remote_url)
    if https_match:
        return https_match.group("host"), https_match.group("project")
    return None


def gitlab_token() -> str | None:
    for name in ("GITLAB_TOKEN", "GL_TOKEN", "GITLAB_PRIVATE_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value
    return None


def load_open_gitlab_mrs(root: Path) -> tuple[list[dict[str, Any]], str | None]:
    remote_result = run_git(root, ["remote", "get-url", "gitlab"])
    if remote_result.returncode != 0:
        return [], "GitLab MR inspection requested but `gitlab` remote is not configured."
    parsed = parse_gitlab_remote(remote_result.stdout.strip())
    if parsed is None:
        return [], f"GitLab MR inspection requested but remote URL is unsupported: {remote_result.stdout.strip()}"
    token = gitlab_token()
    if not token:
        return [], "GitLab MR inspection requested but no GitLab token environment variable is set."

    host, project_path = parsed
    query = urlencode({"state": "opened", "per_page": "100"})
    url = f"https://{host}/api/v4/projects/{quote(project_path, safe='')}/merge_requests?{query}"
    request = Request(url, headers={"PRIVATE-TOKEN": token, "User-Agent": "codex-session-ownership-checker"})
    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as exc:
        return [], f"GitLab MR inspection failed: {exc}"
    if not isinstance(data, list):
        return [], "GitLab MR inspection returned an unexpected payload."
    return [item for item in data if isinstance(item, dict)], None


def precheck_enabled(
    precheck_tasks: list[str],
    precheck_terms: list[str],
    target_paths: list[str],
    openspec_changes: list[str],
    check_gitlab_mrs: bool,
    require_gitlab_mrs: bool,
) -> bool:
    return bool(
        precheck_tasks
        or precheck_terms
        or target_paths
        or openspec_changes
        or check_gitlab_mrs
        or require_gitlab_mrs
    )


def run_task_ownership_precheck(
    root: Path,
    *,
    worktrees: list[dict[str, str]],
    claims: list[Claim],
    main_branch: str,
    precheck_tasks: list[str],
    precheck_terms: list[str],
    target_paths: list[str],
    openspec_changes: list[str],
    check_gitlab_mrs: bool,
    require_gitlab_mrs: bool,
    errors: list[str],
    warnings: list[str],
) -> dict[str, object]:
    terms: set[str] = set()
    for value in precheck_tasks + precheck_terms + openspec_changes:
        add_precheck_term(terms, value)
    normalized_targets = [normalize_repo_path(path) for path in target_paths if path.strip()]
    exact_changes = {change.strip() for change in openspec_changes if change.strip()}
    signals: list[dict[str, object]] = []
    state = "unclaimed"

    def add_signal(kind: str, signal_state: str, summary: str, **extra: object) -> None:
        nonlocal state
        state = advance_state(state, signal_state)
        signal: dict[str, object] = {
            "kind": kind,
            "state": signal_state,
            "summary": summary,
        }
        signal.update(extra)
        signals.append(signal)

    for worktree in worktrees:
        raw_path = worktree.get("worktree")
        if not raw_path:
            continue
        worktree_path = Path(raw_path).resolve()
        branch = branch_name(worktree)
        if not (
            matches_terms(str(worktree_path), terms)
            or matches_terms(worktree_path.name, terms)
            or matches_terms(branch or "", terms)
        ):
            continue
        status_result = run_git(worktree_path, ["status", "--porcelain", "--untracked-files=all"])
        dirty_paths = parse_status_porcelain(status_result.stdout) if status_result.returncode == 0 else []
        ahead = branch_ahead_count(root, main_branch, branch)
        signal_state = "in-progress" if dirty_paths or ahead > 0 else "claimed-not-started"
        add_signal(
            "git_worktree",
            signal_state,
            f"Registered Git worktree matches task terms: {worktree_path}",
            path=str(worktree_path),
            branch=branch,
            dirty_paths=dirty_paths,
            ahead_of_main=ahead,
        )

    local_branches = git_output_lines(root, ["for-each-ref", "--format=%(refname:short)", "refs/heads"])
    for branch in local_branches:
        if not matches_terms(branch, terms):
            continue
        ahead = branch_ahead_count(root, main_branch, branch)
        signal_state = "in-progress" if ahead > 0 else "claimed-not-started"
        add_signal(
            "local_branch",
            signal_state,
            f"Local branch matches task terms: {branch}",
            branch=branch,
            ahead_of_main=ahead,
        )

    remote_branches = [
        line
        for line in git_output_lines(root, ["for-each-ref", "--format=%(refname:short)", "refs/remotes"])
        if not line.endswith("/HEAD")
    ]
    for branch in remote_branches:
        if matches_terms(branch, terms):
            add_signal(
                "remote_branch",
                "claimed-not-started",
                f"Remote-tracking branch matches task terms: {branch}",
                branch=branch,
            )

    changes_root = root / "openspec" / "changes"
    if changes_root.is_dir():
        for change_dir in sorted(item for item in changes_root.iterdir() if item.is_dir() and item.name != "archive"):
            if change_dir.name in exact_changes or matches_terms(change_dir.name, terms):
                add_signal(
                    "active_openspec_change",
                    "in-progress",
                    f"Active OpenSpec change matches task: {change_dir.name}",
                    change=change_dir.name,
                    path=str(change_dir),
                )

    for claim in claims:
        change_match = any(change in exact_changes or matches_terms(change, terms) for change in claim.openspec_changes)
        term_match = any(
            matches_terms(value, terms)
            for value in (claim.session_id, claim.branch, claim.task_type, str(claim.file), str(claim.containing_worktree))
        )
        path_match = any(
            path_overlaps(target, claim_path)
            for target in normalized_targets
            for claim_path in claim.paths
        )
        path_term_match = any(matches_terms(claim_path, terms) for claim_path in claim.paths)
        if change_match or term_match or path_match or path_term_match:
            add_signal(
                "active_session_claim",
                "in-progress",
                f"Active session claim matches task: {claim.file}",
                claim=summarize_claim(claim),
                matched_by={
                    "change": change_match,
                    "term": term_match or path_term_match,
                    "path": path_match,
                },
            )

    guard_args = ["--", *DEFAULT_GUARD_SCANNED_DIRS]
    local_guard_paths = set(
        git_output_lines(root, ["ls-files", "--others", "--exclude-standard", *guard_args])
        + git_output_lines(root, ["ls-files", "--others", "--ignored", "--exclude-standard", *guard_args])
    )
    for local_path in sorted(normalize_repo_path(path) for path in local_guard_paths):
        path_match = any(path_overlaps(target, local_path) for target in normalized_targets)
        term_match = matches_terms(local_path, terms)
        if path_match or term_match:
            add_signal(
                "ignored_or_local_guard_file",
                "claimed-not-started",
                f"Ignored or local-only guard-scanned file matches task: {local_path}",
                path=local_path,
                matched_by={"path": path_match, "term": term_match},
            )

    gitlab_checked = False
    if check_gitlab_mrs or require_gitlab_mrs:
        mrs, gitlab_error = load_open_gitlab_mrs(root)
        if gitlab_error:
            message = f"Task ownership precheck could not inspect open GitLab MRs: {gitlab_error}"
            if require_gitlab_mrs:
                errors.append(message)
            else:
                warnings.append(message)
        else:
            gitlab_checked = True
            for mr in mrs:
                title = str(mr.get("title", ""))
                source_branch = str(mr.get("source_branch", ""))
                if matches_terms(title, terms) or matches_terms(source_branch, terms):
                    add_signal(
                        "open_gitlab_mr",
                        "in-progress",
                        f"Open GitLab MR matches task: !{mr.get('iid')} {title}",
                        iid=mr.get("iid"),
                        title=title,
                        source_branch=source_branch,
                        web_url=mr.get("web_url"),
                    )

    if state != "unclaimed":
        errors.append(
            f"Task ownership precheck classified this task as `{state}`. "
            "Serialize ownership, continue the existing worktree, or classify stale residue before writing."
        )

    return {
        "enabled": True,
        "state": state,
        "terms": sorted(terms),
        "target_paths": normalized_targets,
        "openspec_changes": sorted(exact_changes),
        "signals": signals,
        "gitlab_mrs_checked": gitlab_checked,
        "counts": {
            "signals": len(signals),
        },
    }


def run_check(
    root: Path,
    *,
    main_branch: str,
    claims_subdir: Path,
    allow_current_dirty: bool,
    precheck_tasks: list[str] | None = None,
    precheck_terms: list[str] | None = None,
    target_paths: list[str] | None = None,
    openspec_changes: list[str] | None = None,
    check_gitlab_mrs: bool = False,
    require_gitlab_mrs: bool = False,
) -> dict[str, object]:
    root = root.resolve()
    precheck_tasks = precheck_tasks or []
    precheck_terms = precheck_terms or []
    target_paths = target_paths or []
    openspec_changes = openspec_changes or []
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
        if is_gitlab_ci_detached_checkout() and current_branch is None:
            info.append(
                "GitLab CI detached checkout is dirty after managed refresh; local session ownership "
                "claims are not required for this ephemeral remote CI worktree."
            )
        else:
            errors.append(
                f"Current dirty feature worktree {current_root} has no active session ownership claim under "
                f"{(current_root / claims_subdir).as_posix()}. Declare the OpenSpec change or path scope before continuing."
            )

    task_ownership_precheck: dict[str, object] | None = None
    if precheck_enabled(
        precheck_tasks,
        precheck_terms,
        target_paths,
        openspec_changes,
        check_gitlab_mrs,
        require_gitlab_mrs,
    ):
        task_ownership_precheck = run_task_ownership_precheck(
            current_root,
            worktrees=worktrees,
            claims=claims,
            main_branch=main_branch,
            precheck_tasks=precheck_tasks,
            precheck_terms=precheck_terms,
            target_paths=target_paths,
            openspec_changes=openspec_changes,
            check_gitlab_mrs=check_gitlab_mrs,
            require_gitlab_mrs=require_gitlab_mrs,
            errors=errors,
            warnings=warnings,
        )

    if not claims:
        info.append("No active local session ownership claims were detected.")
    else:
        info.append(f"Active local session ownership claims detected: {len(claims)}.")

    return payload(root, claims_subdir, worktrees, claims, errors, warnings, info, task_ownership_precheck)


def payload(
    root: Path,
    claims_subdir: Path,
    worktrees: list[dict[str, str]],
    claims: list[Claim],
    errors: list[str],
    warnings: list[str],
    info: list[str],
    task_ownership_precheck: dict[str, object] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
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
    if task_ownership_precheck is not None:
        result["task_ownership_precheck"] = task_ownership_precheck
    return result


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
    parser.add_argument(
        "--precheck-task",
        action="append",
        default=[],
        help="Run task ownership precheck using this human-readable task description or slug.",
    )
    parser.add_argument(
        "--precheck-term",
        action="append",
        default=[],
        help="Add an explicit deterministic semantic matching term for task ownership precheck.",
    )
    parser.add_argument(
        "--target-path",
        action="append",
        default=[],
        help="Add a repository-relative target path for task ownership precheck.",
    )
    parser.add_argument(
        "--openspec-change",
        action="append",
        default=[],
        help="Add an OpenSpec change id for exact task ownership precheck matching.",
    )
    parser.add_argument(
        "--check-gitlab-mrs",
        action="store_true",
        help="Inspect open GitLab MRs during task ownership precheck when credentials are available.",
    )
    parser.add_argument(
        "--require-gitlab-mrs",
        action="store_true",
        help="Fail task ownership precheck if open GitLab MRs cannot be inspected.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    result = run_check(
        Path(args.root),
        main_branch=args.main_branch,
        claims_subdir=Path(args.claims_subdir),
        allow_current_dirty=args.allow_current_dirty,
        precheck_tasks=args.precheck_task,
        precheck_terms=args.precheck_term,
        target_paths=args.target_path,
        openspec_changes=args.openspec_change,
        check_gitlab_mrs=args.check_gitlab_mrs,
        require_gitlab_mrs=args.require_gitlab_mrs,
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
