#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import check_implementation_plan_claim_lock as claim_lock

DEFAULT_SESSION_PREFIX = "codex-session"


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


def git_branch(root: Path) -> str:
    result = run_git(root, ["branch", "--show-current"])
    return result.stdout.strip() if result.returncode == 0 else ""


def slugify(value: str) -> str:
    value = value.lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9._/-]+", "-", value)
    value = re.sub(r"[-_/]+", "-", value)
    return value.strip("-.") or "implementation-plan"


def read_plan_doc_id(root: Path, plan: str) -> str:
    return claim_lock.plan_identity(root, plan)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def claim(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    plan = claim_lock.normalize_repo_path(args.plan)
    errors: list[str] = []
    normalized = claim_lock.validate_plan_path(root, Path("<cli>"), plan, errors)
    if errors or normalized is None:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    plan = normalized
    branch = args.branch or git_branch(root)
    if not branch:
        print(json.dumps({"ok": False, "errors": ["branch is required when it cannot be detected from git"]}, indent=2))
        return 1
    session_id = args.session_id or f"{DEFAULT_SESSION_PREFIX}-{slugify(Path(plan).stem)}"
    expires_at = utc_now() + timedelta(hours=max(1, int(args.expires_hours)))
    doc_id = read_plan_doc_id(root, plan)
    paths = [claim_lock.normalize_repo_path(path) for path in args.path]
    if plan not in paths:
        paths.insert(0, plan)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "session_id": session_id,
        "status": "active",
        "branch": branch,
        "worktree": str(Path(args.worktree).resolve() if args.worktree else root),
        "task_type": "implementation",
        "implementation_plan": plan,
        "implementation_plan_doc_id": doc_id,
        "paths": paths,
        "created_at": utc_now().isoformat(),
        "expires_at": expires_at.isoformat(),
    }
    claim_dir = root / args.claims_subdir
    claim_path = claim_dir / f"{slugify(session_id)}.json"
    if claim_path.exists() and not args.force:
        print(json.dumps({"ok": False, "errors": [f"claim file already exists: {claim_path}"]}, ensure_ascii=False, indent=2))
        return 1
    write_json(claim_path, payload)
    check = claim_lock.evaluate(root, Path(args.claims_subdir))
    if not check["ok"]:
        if not args.keep_conflicting:
            claim_path.unlink(missing_ok=True)
        print(json.dumps({"ok": False, "claim_path": str(claim_path), "check": check}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "claim_path": str(claim_path), "claim": payload, "check": check}, ensure_ascii=False, indent=2))
    return 0


def release(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    claim_dir = root / args.claims_subdir
    candidates = sorted(claim_dir.glob("*.json")) if claim_dir.exists() else []
    updated: list[str] = []
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if args.session_id and data.get("session_id") != args.session_id:
            continue
        if args.plan and claim_lock.normalize_repo_path(str(data.get("implementation_plan", ""))) != claim_lock.normalize_repo_path(args.plan):
            continue
        if not args.session_id and not args.plan:
            continue
        data["status"] = "released"
        data["released_at"] = utc_now().isoformat()
        write_json(path, data)
        updated.append(str(path))
    ok = bool(updated)
    print(json.dumps({"ok": ok, "released_claims": updated, "errors": [] if ok else ["no matching claim found"]}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or release portable implementation-plan session claims.")
    sub = parser.add_subparsers(dest="command", required=True)
    claim_parser = sub.add_parser("claim", help="Create an active implementation-plan claim.")
    claim_parser.add_argument("--root", default=".")
    claim_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    claim_parser.add_argument("--plan", required=True)
    claim_parser.add_argument("--session-id")
    claim_parser.add_argument("--branch")
    claim_parser.add_argument("--worktree")
    claim_parser.add_argument("--expires-hours", type=int, default=24)
    claim_parser.add_argument("--path", action="append", default=[])
    claim_parser.add_argument("--force", action="store_true")
    claim_parser.add_argument("--keep-conflicting", action="store_true")
    claim_parser.set_defaults(func=claim)
    release_parser = sub.add_parser("release", help="Release an active implementation-plan claim.")
    release_parser.add_argument("--root", default=".")
    release_parser.add_argument("--claims-subdir", default=claim_lock.DEFAULT_CLAIMS_SUBDIR.as_posix())
    release_parser.add_argument("--session-id")
    release_parser.add_argument("--plan")
    release_parser.set_defaults(func=release)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
