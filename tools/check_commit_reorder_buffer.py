#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_SUBDIR = Path(".omx/commit-rob/entries")
ACTIVE_STATES = {"predicted", "executing", "ready", "blocked", "retiring"}
ALLOWED_STATES = ACTIVE_STATES | {"retired", "flushed", "superseded"}
READY_GATE_REQUIREMENTS = ("precommit_update_archive", "local_gate", "local_mr_review")
PREDICTION_RESOLUTIONS = {"accepted", "reconciled", "split"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_path(value: str) -> str:
    value = str(value).strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.rstrip("/") or "."


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_items = [value]
    elif isinstance(value, list):
        raw_items = value
    else:
        return []
    result: list[str] = []
    for item in raw_items:
        if not isinstance(item, str):
            continue
        for part in item.split(","):
            normalized = normalize_path(part)
            if normalized and normalized not in result:
                result.append(normalized)
    return result


def overlaps(left: str, right: str) -> bool:
    left = normalize_path(left)
    right = normalize_path(right)
    if left == "." or right == ".":
        return True
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def load_entries(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    directory = root / STATE_SUBDIR
    if not directory.exists():
        return entries, errors
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        except OSError as exc:
            errors.append(f"{path}: cannot read entry: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: ROB entry must be a JSON object.")
            continue
        data["_path"] = str(path)
        entries.append(data)
    return entries, errors


def string_field(entry: dict[str, Any], key: str, errors: list[str]) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{entry.get('_path')}: `{key}` must be a non-empty string.")
        return ""
    return value.strip()


def entry_paths(entry: dict[str, Any]) -> set[str]:
    paths = set(normalize_list(entry.get("predicted_write_set")))
    paths.update(normalize_list(entry.get("actual_write_set")))
    paths.update(normalize_list(entry.get("hotspots")))
    return paths


def has_dependency(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_deps = set(normalize_list(left.get("dependencies")))
    right_deps = set(normalize_list(right.get("dependencies")))
    left_id = str(left.get("entry_id") or "")
    right_id = str(right.get("entry_id") or "")
    return right_id in left_deps or left_id in right_deps


def evaluate(root: Path, max_ready: int = 6) -> dict[str, Any]:
    root = root.resolve()
    entries, errors = load_entries(root)
    warnings: list[str] = []

    active_by_plan: dict[str, list[str]] = {}
    ready_entries: list[dict[str, Any]] = []

    for entry in entries:
        path = entry.get("_path")
        if entry.get("schema_version") != 1:
            errors.append(f"{path}: `schema_version` must be 1.")
        entry_id = string_field(entry, "entry_id", errors)
        state = entry.get("state")
        if not isinstance(state, str) or state not in ALLOWED_STATES:
            errors.append(f"{path}: `state` must be one of {sorted(ALLOWED_STATES)}.")
            continue

        if state in ACTIVE_STATES or state == "retired":
            string_field(entry, "session_id", errors)
            plan = string_field(entry, "implementation_plan", errors)
            string_field(entry, "branch", errors)
            string_field(entry, "worktree", errors)
            string_field(entry, "base_main", errors)
            if state in ACTIVE_STATES and plan:
                active_by_plan.setdefault(normalize_path(plan), []).append(entry_id)

        if state == "ready":
            ready_entries.append(entry)
            actual = normalize_list(entry.get("actual_write_set"))
            if not actual:
                errors.append(f"{path}: ready ROB entry must declare `actual_write_set`.")
            gates = entry.get("gate_status")
            if not isinstance(gates, dict):
                errors.append(f"{path}: ready ROB entry must declare object `gate_status`.")
                gates = {}
            for gate in READY_GATE_REQUIREMENTS:
                if gates.get(gate) != "passed":
                    errors.append(f"{path}: ready ROB entry gate `{gate}` must be `passed`.")

        if state in {"ready", "retiring", "retired"}:
            predicted = set(normalize_list(entry.get("predicted_write_set")))
            actual = set(normalize_list(entry.get("actual_write_set")))
            if actual and not actual.issubset(predicted):
                resolution = entry.get("prediction_resolution")
                if resolution not in PREDICTION_RESOLUTIONS:
                    missing = sorted(actual - predicted)
                    errors.append(
                        f"{path}: branch prediction mismatch for {missing}; set prediction_resolution or block/flush the entry."
                    )

        if state == "retired":
            string_field(entry, "rollback_ref", errors)
            string_field(entry, "local_main_commit", errors)
            evidence = normalize_list(entry.get("evidence"))
            if not evidence:
                errors.append(f"{path}: retired ROB entry must keep non-empty `evidence`.")

    for plan, ids in sorted(active_by_plan.items()):
        if len(ids) > 1:
            errors.append(f"implementation plan {plan} has multiple active ROB entries: {', '.join(ids)}")

    for index, left in enumerate(entries):
        if left.get("state") not in ACTIVE_STATES:
            continue
        left_paths = entry_paths(left)
        if not left_paths:
            continue
        for right in entries[index + 1 :]:
            if right.get("state") not in ACTIVE_STATES:
                continue
            if has_dependency(left, right):
                continue
            right_paths = entry_paths(right)
            conflicts = sorted(
                {l for l in left_paths for r in right_paths if overlaps(l, r)}
                | {r for l in left_paths for r in right_paths if overlaps(l, r)}
            )
            if conflicts and left.get("state") == "ready" and right.get("state") == "ready":
                errors.append(
                    f"ready ROB entries {left.get('entry_id')} and {right.get('entry_id')} share hotspot/write paths without dependency ordering: {conflicts}"
                )

    if len(ready_entries) > max_ready:
        warnings.append(f"ready ROB entry count {len(ready_entries)} exceeds backpressure threshold {max_ready}.")

    counts: dict[str, int] = {"entries": len(entries), "errors": len(errors), "warnings": len(warnings)}
    for entry in entries:
        state = str(entry.get("state", "unknown"))
        counts[state] = counts.get(state, 0) + 1

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": "commit_reorder_buffer",
        "ok": not errors,
        "root": str(root),
        "state_dir": str(root / STATE_SUBDIR),
        "max_ready": max_ready,
        "errors": errors,
        "warnings": warnings,
        "counts": counts,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local commit reorder-buffer state.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--max-ready", type=int, default=6, help="Backpressure warning threshold for ready entries.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = evaluate(Path(args.root), max_ready=max(1, args.max_ready))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("commit_reorder_buffer: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
