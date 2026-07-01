#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "implementation_plan_claim_lock"
DEFAULT_CLAIMS_SUBDIR = Path(".omx/session-claims")
ACTIVE_STATUS = "active"
RELEASED_STATUSES = {
    "released",
    "inactive",
    "paused",
    "ready-to-merge",
    "merged-local-main",
    "cleaned",
    "remote-sync-needed",
    "completed",
    "superseded",
}
ALLOWED_STATUSES = {ACTIVE_STATUS, *RELEASED_STATUSES}
PLAN_PREFIX = "docs_bilingual/implementation_plans/"


@dataclass(frozen=True)
class PlanClaim:
    file: Path
    containing_worktree: Path
    session_id: str
    status: str
    branch: str
    worktree: str
    implementation_plan: str
    implementation_plan_doc_id: str
    created_at: str | None
    expires_at: str | None
    expired: bool


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_worktree_list(output: str) -> list[Path]:
    roots: list[Path] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith("worktree "):
            roots.append(Path(line.split(" ", 1)[1]).resolve())
    return roots


def discover_worktrees(root: Path) -> list[Path]:
    result = run_git(root, ["worktree", "list", "--porcelain"])
    if result.returncode != 0:
        return [root.resolve()]
    roots = parse_worktree_list(result.stdout)
    return roots or [root.resolve()]


def normalize_repo_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def parse_timestamp(value: str | None, *, path: Path, field: str, errors: list[str]) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: `{field}` must be a non-empty ISO-8601 string when present")
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        errors.append(f"{path}: `{field}` must be ISO-8601: {value!r}")
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    except OSError as exc:
        errors.append(f"{path}: cannot read claim file: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: claim must be a JSON object")
        return None
    return data


def yaml_scalar(text: str, key: str) -> str | None:
    prefix = f"{key}:"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            value = line[len(prefix) :].strip().strip('"\'')
            return value or None
    return None


def plan_identity(root: Path, plan_path: str) -> str:
    path = root / plan_path
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return plan_path
    return yaml_scalar(text, "doc_id") or plan_path


def validate_plan_path(plan_root: Path, claim_file: Path, value: Any, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{claim_file}: `implementation_plan` must be a non-empty repo-relative path")
        return None
    plan = normalize_repo_path(value)
    if plan.startswith("/") or ":" in plan.split("/", 1)[0]:
        errors.append(f"{claim_file}: `implementation_plan` must be repo-relative, got {value!r}")
        return None
    if not plan.startswith(PLAN_PREFIX) or not plan.endswith(".md"):
        errors.append(f"{claim_file}: `implementation_plan` must point under {PLAN_PREFIX} and end with .md")
        return None
    if not (plan_root / plan).exists():
        errors.append(f"{claim_file}: `implementation_plan` does not exist in claim worktree {plan_root}: {plan}")
        return None
    return plan


def validate_claim(root: Path, worktree: Path, claim_file: Path, data: dict[str, Any], errors: list[str], warnings: list[str]) -> PlanClaim | None:
    implementation_plan_value = data.get("implementation_plan", data.get("implementation_plan_path"))
    if implementation_plan_value is None:
        return None
    if data.get("schema_version") != 1:
        errors.append(f"{claim_file}: `schema_version` must be 1")
    status = data.get("status", ACTIVE_STATUS)
    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        errors.append(f"{claim_file}: `status` must be one of {sorted(ALLOWED_STATUSES)}")
        status = str(status)
    plan = validate_plan_path(worktree, claim_file, implementation_plan_value, errors) or ""
    required_strings = {}
    for field in ("session_id", "branch", "worktree"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{claim_file}: `{field}` must be a non-empty string")
            required_strings[field] = ""
        else:
            required_strings[field] = value.strip()
    created_at = data.get("created_at")
    if status == ACTIVE_STATUS and (not isinstance(created_at, str) or not created_at.strip()):
        errors.append(f"{claim_file}: active implementation-plan claim requires `created_at`")
    parse_timestamp(created_at, path=claim_file, field="created_at", errors=errors)
    expires_at = data.get("expires_at")
    expires = parse_timestamp(expires_at, path=claim_file, field="expires_at", errors=errors)
    expired = bool(expires and expires <= utc_now())
    if expired and status == ACTIVE_STATUS:
        warnings.append(f"{claim_file}: active implementation-plan claim is stale because `expires_at` is in the past")
    declared_doc_id = data.get("implementation_plan_doc_id")
    actual_doc_id = plan_identity(worktree, plan) if plan else ""
    if declared_doc_id is not None and isinstance(declared_doc_id, str) and declared_doc_id.strip() and actual_doc_id:
        if declared_doc_id.strip() != actual_doc_id:
            errors.append(
                f"{claim_file}: `implementation_plan_doc_id` must match plan doc_id `{actual_doc_id}`, got `{declared_doc_id.strip()}`"
            )
    return PlanClaim(
        file=claim_file,
        containing_worktree=worktree,
        session_id=required_strings.get("session_id", ""),
        status=status,
        branch=required_strings.get("branch", ""),
        worktree=required_strings.get("worktree", ""),
        implementation_plan=plan,
        implementation_plan_doc_id=actual_doc_id,
        created_at=created_at if isinstance(created_at, str) else None,
        expires_at=expires_at if isinstance(expires_at, str) else None,
        expired=expired,
    )


def collect_claims(root: Path, claims_subdir: Path, errors: list[str], warnings: list[str]) -> list[PlanClaim]:
    claims: list[PlanClaim] = []
    for worktree in discover_worktrees(root):
        claim_dir = worktree / claims_subdir
        if not claim_dir.exists():
            continue
        for claim_file in sorted(claim_dir.glob("*.json")):
            data = read_json(claim_file, errors)
            if data is None:
                continue
            claim = validate_claim(root, worktree, claim_file, data, errors, warnings)
            if claim is not None:
                claims.append(claim)
    return claims


def evaluate(root: Path, claims_subdir: Path = DEFAULT_CLAIMS_SUBDIR) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    claims = collect_claims(root, claims_subdir, errors, warnings)
    active = [claim for claim in claims if claim.status == ACTIVE_STATUS and not claim.expired]
    by_identity: dict[str, list[PlanClaim]] = {}
    for claim in active:
        identity = claim.implementation_plan_doc_id or claim.implementation_plan
        if not identity:
            continue
        by_identity.setdefault(identity, []).append(claim)
    for identity, matches in sorted(by_identity.items()):
        if len(matches) <= 1:
            continue
        files = ", ".join(str(match.file) for match in matches)
        errors.append(f"implementation plan `{identity}` has multiple active session claims: {files}")
    return {
        "schema_version": 1,
        "generated_at": utc_now().isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "claims_subdir": claims_subdir.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "claims": [
            {
                "file": str(claim.file),
                "worktree": str(claim.containing_worktree),
                "session_id": claim.session_id,
                "status": claim.status,
                "branch": claim.branch,
                "implementation_plan": claim.implementation_plan,
                "implementation_plan_doc_id": claim.implementation_plan_doc_id,
                "expires_at": claim.expires_at,
                "expired": claim.expired,
            }
            for claim in claims
        ],
        "counts": {
            "claims": len(claims),
            "active_claims": len(active),
            "stale_claims": sum(1 for claim in claims if claim.status == ACTIVE_STATUS and claim.expired),
            "released_or_inactive_claims": sum(1 for claim in claims if claim.status != ACTIVE_STATUS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate portable single-active-session locks for implementation plans.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--claims-subdir", default=DEFAULT_CLAIMS_SUBDIR.as_posix(), help="Worktree-relative claim directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    payload = evaluate(Path(args.root), Path(args.claims_subdir))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif payload["ok"]:
        print(f"{CHECK_NAME}: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
    else:
        print(f"{CHECK_NAME}: failed")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
