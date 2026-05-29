#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_SUBDIR = Path(".omx/commit-rob/entries")
ACTIVE_STATES = {"predicted", "executing", "ready", "blocked", "retiring"}
TERMINAL_STATES = {"retired", "flushed", "superseded"}
ALLOWED_STATES = ACTIVE_STATES | TERMINAL_STATES


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    value = value.lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9._/-]+", "-", value)
    value = re.sub(r"[-_/]+", "-", value)
    return value.strip("-") or "entry"


def repo_path(root: Path, value: str | None) -> Path:
    path = Path(value or ".")
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def state_dir(root: Path) -> Path:
    return root / STATE_SUBDIR


def entry_path(root: Path, entry_id: str) -> Path:
    safe = slugify(entry_id)
    return state_dir(root) / f"{safe}.json"


def normalize_list(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for part in str(value).split(","):
            item = part.strip().replace("\\", "/")
            while item.startswith("./"):
                item = item[2:]
            item = item.rstrip("/")
            if item and item not in result:
                result.append(item)
    return result


def parse_key_value(values: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values or []:
        if "=" not in value:
            raise ValueError(f"expected KEY=VALUE gate item, got {value!r}")
        key, status = value.split("=", 1)
        key = key.strip()
        status = status.strip()
        if not key or not status:
            raise ValueError(f"invalid gate item {value!r}")
        result[key] = status
    return result


def git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def default_base_main(root: Path) -> str:
    return git_output(root, ["rev-parse", "main"]) or "unknown"


def load_entry(root: Path, entry_id: str) -> dict[str, Any]:
    path = entry_path(root, entry_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ROB entry not found: {path}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"ROB entry must be a JSON object: {path}")
    return data


def write_entry(root: Path, data: dict[str, Any]) -> Path:
    entry_id = str(data.get("entry_id") or "").strip()
    if not entry_id:
        raise SystemExit("entry_id is required")
    path = entry_path(root, entry_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = utc_now()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def result(ok: bool, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": "commit_reorder_buffer",
        "ok": ok,
    }
    payload.update(extra)
    return payload


def print_payload(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


def cmd_predict(args: argparse.Namespace) -> int:
    root = repo_path(Path.cwd(), args.root)
    entry_id = args.entry_id or slugify(f"{args.session_id}-{args.implementation_plan}")
    now = utc_now()
    entry = {
        "schema_version": 1,
        "entry_id": entry_id,
        "state": "predicted",
        "session_id": args.session_id,
        "implementation_plan": args.implementation_plan,
        "branch": args.branch,
        "worktree": args.worktree or str(root),
        "base_main": args.base_main or default_base_main(root),
        "predicted_write_set": normalize_list(args.write_set),
        "actual_write_set": [],
        "hotspots": normalize_list(args.hotspot),
        "dependencies": normalize_list(args.dependency),
        "gate_status": {},
        "evidence": [],
        "created_at": now,
        "updated_at": now,
    }
    path = write_entry(root, entry)
    return print_payload(result(True, action="predict", entry=entry, path=str(path)))


def cmd_enqueue(args: argparse.Namespace) -> int:
    root = repo_path(Path.cwd(), args.root)
    entry = load_entry(root, args.entry_id)
    state = args.state or "ready"
    if state not in {"ready", "blocked", "executing"}:
        raise SystemExit("enqueue state must be ready, blocked, or executing")
    if args.actual_write_set:
        entry["actual_write_set"] = normalize_list(args.actual_write_set)
    if args.hotspot:
        entry["hotspots"] = normalize_list(args.hotspot)
    if args.dependency:
        entry["dependencies"] = normalize_list(args.dependency)
    if args.prediction_resolution:
        entry["prediction_resolution"] = args.prediction_resolution
    gates = dict(entry.get("gate_status") or {})
    gates.update(parse_key_value(args.gate))
    entry["gate_status"] = gates
    evidence = list(entry.get("evidence") or [])
    evidence.extend(normalize_list(args.evidence))
    entry["evidence"] = evidence
    entry["state"] = state
    path = write_entry(root, entry)
    return print_payload(result(True, action="enqueue", entry=entry, path=str(path)))


def cmd_status(args: argparse.Namespace) -> int:
    root = repo_path(Path.cwd(), args.root)
    entries = []
    for path in sorted(state_dir(root).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                data["path"] = str(path)
                entries.append(data)
        except json.JSONDecodeError:
            entries.append({"path": str(path), "state": "invalid"})
    counts: dict[str, int] = {}
    for entry in entries:
        state = str(entry.get("state", "unknown"))
        counts[state] = counts.get(state, 0) + 1
    return print_payload(result(True, action="status", entries=entries, counts=counts))


def cmd_retire(args: argparse.Namespace) -> int:
    root = repo_path(Path.cwd(), args.root)
    entry = load_entry(root, args.entry_id)
    if entry.get("state") != "ready" and not args.force:
        return print_payload(result(False, action="retire", errors=[f"entry {args.entry_id} is not ready"]))
    evidence = list(entry.get("evidence") or [])
    evidence.extend(normalize_list(args.evidence))
    entry.update(
        {
            "state": "retired",
            "rollback_ref": args.rollback_ref,
            "local_main_commit": args.local_main_commit,
            "retired_at": utc_now(),
            "evidence": evidence,
        }
    )
    path = write_entry(root, entry)
    return print_payload(result(True, action="retire", entry=entry, path=str(path)))


def cmd_flush(args: argparse.Namespace) -> int:
    root = repo_path(Path.cwd(), args.root)
    entry = load_entry(root, args.entry_id)
    state = args.state or "flushed"
    if state not in {"flushed", "superseded"}:
        raise SystemExit("flush state must be flushed or superseded")
    entry["state"] = state
    entry["flush_reason"] = args.reason
    entry["flushed_at"] = utc_now()
    path = write_entry(root, entry)
    return print_payload(result(True, action="flush", entry=entry, path=str(path)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage repo-local commit reorder-buffer entries.")
    sub = parser.add_subparsers(dest="command", required=True)

    predict = sub.add_parser("predict", help="Create a predicted ROB entry.")
    predict.add_argument("--root", default=".")
    predict.add_argument("--entry-id", default=None)
    predict.add_argument("--session-id", required=True)
    predict.add_argument("--implementation-plan", required=True)
    predict.add_argument("--branch", required=True)
    predict.add_argument("--worktree", default=None)
    predict.add_argument("--base-main", default=None)
    predict.add_argument("--write-set", action="append", default=[])
    predict.add_argument("--hotspot", action="append", default=[])
    predict.add_argument("--dependency", action="append", default=[])
    predict.set_defaults(func=cmd_predict)

    enqueue = sub.add_parser("enqueue", help="Move an entry to executing, blocked, or ready with actual evidence.")
    enqueue.add_argument("--root", default=".")
    enqueue.add_argument("--entry-id", required=True)
    enqueue.add_argument("--state", choices=["executing", "blocked", "ready"], default="ready")
    enqueue.add_argument("--actual-write-set", action="append", default=[])
    enqueue.add_argument("--hotspot", action="append", default=[])
    enqueue.add_argument("--dependency", action="append", default=[])
    enqueue.add_argument("--gate", action="append", default=[])
    enqueue.add_argument("--evidence", action="append", default=[])
    enqueue.add_argument("--prediction-resolution", default=None)
    enqueue.set_defaults(func=cmd_enqueue)

    status = sub.add_parser("status", help="Print ROB entries and state counts.")
    status.add_argument("--root", default=".")
    status.set_defaults(func=cmd_status)

    retire = sub.add_parser("retire", help="Mark a ready entry retired after leader-owned local-main integration.")
    retire.add_argument("--root", default=".")
    retire.add_argument("--entry-id", required=True)
    retire.add_argument("--rollback-ref", required=True)
    retire.add_argument("--local-main-commit", required=True)
    retire.add_argument("--evidence", action="append", default=[])
    retire.add_argument("--force", action="store_true")
    retire.set_defaults(func=cmd_retire)

    flush = sub.add_parser("flush", help="Mark an entry flushed or superseded.")
    flush.add_argument("--root", default=".")
    flush.add_argument("--entry-id", required=True)
    flush.add_argument("--reason", required=True)
    flush.add_argument("--state", choices=["flushed", "superseded"], default="flushed")
    flush.set_defaults(func=cmd_flush)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        return print_payload(result(False, action=args.command, errors=[str(exc)]))


if __name__ == "__main__":
    raise SystemExit(main())
