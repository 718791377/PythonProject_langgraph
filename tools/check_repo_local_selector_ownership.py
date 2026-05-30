#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "repo_local_selector_ownership"
ACTIVE_SELECTOR_RELATIVE = Path(".omx/state/selectors/active.json")
SELECTOR_LEASES_RELATIVE = Path(".omx/state/selectors/leases")
DEFAULT_MAX_HEARTBEAT_AGE_SECONDS = 8 * 60 * 60
REQUIRED_ACTIVE_FIELDS = (
    "backend_family",
    "selector_id",
    "repo_root",
    "worktree_id",
    "thread_id",
    "session_scope_id",
    "last_heartbeat_at",
    "routing_eligible",
)


def read_json(path: Path, errors: list[str], label: str) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        errors.append(f"Missing {label}: {path}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {label} {path}: {exc}")
        return None
    except OSError as exc:
        errors.append(f"Cannot read {label} {path}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label} {path} must contain a JSON object")
        return None
    return data


def normalize_path(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path.absolute()
    return resolved.as_posix().rstrip("/").casefold()


def path_from_value(value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return Path(value)


def path_matches(value: Any, expected: Path) -> bool:
    candidate = path_from_value(value)
    if candidate is None:
        return False
    return normalize_path(candidate) == normalize_path(expected)


def path_is_under(value: Any, parent: Path) -> bool:
    candidate = path_from_value(value)
    if candidate is None:
        return False
    candidate_norm = normalize_path(candidate)
    parent_norm = normalize_path(parent)
    return candidate_norm == parent_norm or candidate_norm.startswith(parent_norm + "/")


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    parsed = parse_time(value)
    if parsed is None:
        raise SystemExit(f"Invalid --now timestamp: {value}")
    return parsed


def is_released(selector: dict[str, Any]) -> bool:
    released_at = selector.get("released_at")
    return isinstance(released_at, str) and bool(released_at.strip())


def selector_staleness(selector: dict[str, Any], *, now: datetime, max_age_seconds: int) -> tuple[bool, str | None, float | None]:
    heartbeat = parse_time(selector.get("last_heartbeat_at")) or parse_time(selector.get("acquired_at"))
    if heartbeat is None:
        return True, "selector_heartbeat_missing_or_invalid", None
    age = max(0.0, (now - heartbeat).total_seconds())
    if age > max_age_seconds:
        return True, "selector_heartbeat_stale", age
    return False, None, age


def validate_selector(
    *,
    root: Path,
    selector_path: Path,
    selector: dict[str, Any],
    now: datetime,
    max_age_seconds: int,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    root = root.resolve()
    expected_selector_root = root / ".omx" / "state" / "selectors"
    expected_active_selector = root / ACTIVE_SELECTOR_RELATIVE
    expected_leases_dir = root / SELECTOR_LEASES_RELATIVE

    released = is_released(selector)
    routing_eligible = selector.get("routing_eligible")
    stale, stale_reason, heartbeat_age_seconds = selector_staleness(selector, now=now, max_age_seconds=max_age_seconds)

    for field in REQUIRED_ACTIVE_FIELDS:
        if field not in selector:
            errors.append(f"Active selector missing required field: {field}")

    if routing_eligible is not True and routing_eligible is not False:
        errors.append("Active selector field `routing_eligible` must be an explicit boolean.")

    repo_root = selector.get("repo_root")
    if not path_matches(repo_root, root):
        errors.append("Active selector `repo_root` must match the current repository/worktree root; cross-repository selector adoption is blocked.")

    layout = selector.get("layout")
    if not isinstance(layout, dict):
        errors.append("Active selector `layout` must be a JSON object with repo-local selector paths.")
        layout = {}

    layout_root = layout.get("root")
    layout_active = layout.get("active_selector")
    layout_leases = layout.get("selector_leases")

    if layout_root is not None and not path_matches(layout_root, expected_selector_root):
        errors.append("Active selector `layout.root` must point to the current repo-local .omx/state/selectors directory.")
    if layout_active is not None and not path_matches(layout_active, expected_active_selector):
        errors.append("Active selector `layout.active_selector` must point to the current repo-local active selector file.")
    if layout_leases is not None and not path_matches(layout_leases, expected_leases_dir):
        errors.append("Active selector `layout.selector_leases` must point to the current repo-local selector leases directory.")

    for field, value in (("layout.root", layout_root), ("layout.active_selector", layout_active), ("layout.selector_leases", layout_leases)):
        if value is not None and not path_is_under(value, root):
            errors.append(f"Active selector `{field}` must not point outside the current repository/worktree root.")

    if stale:
        if routing_eligible is True and not released:
            warnings.append(
                "Active selector is stale but `routing_eligible` is true; automatic adoption is not allowed until the selector is refreshed."
            )
        else:
            warnings.append("Active selector is stale or missing heartbeat; automatic adoption is not allowed from stale selector state.")

    if released and routing_eligible is True:
        errors.append("Released selector must not remain `routing_eligible=true`; automatic adoption is blocked.")

    return {
        "selector_path": str(selector_path),
        "selector_id": selector.get("selector_id"),
        "backend_family": selector.get("backend_family"),
        "repo_root": selector.get("repo_root"),
        "worktree_id": selector.get("worktree_id"),
        "routing_eligible": routing_eligible,
        "released": released,
        "stale": stale,
        "stale_reason": stale_reason,
        "heartbeat_age_seconds": heartbeat_age_seconds,
    }


def validate_lease(root: Path, lease_path: Path, lease: dict[str, Any], selector_id: str | None, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    root = root.resolve()
    repo_root = lease.get("repo_root")
    if repo_root is not None and not path_matches(repo_root, root):
        errors.append(f"Selector lease {lease_path} has non-local `repo_root`; cross-repository selector lease adoption is blocked.")
    layout_root = lease.get("selector_root") or lease.get("layout", {}).get("root") if isinstance(lease.get("layout"), dict) else lease.get("selector_root")
    if layout_root is not None and not path_is_under(layout_root, root):
        errors.append(f"Selector lease {lease_path} points outside the current repository/worktree root.")
    lease_selector_id = lease.get("selector_id")
    if selector_id and lease_selector_id and lease_selector_id != selector_id:
        warnings.append(f"Selector lease {lease_path} references selector_id `{lease_selector_id}` instead of active `{selector_id}`.")
    return {
        "path": str(lease_path),
        "selector_id": lease_selector_id,
        "repo_root": repo_root,
        "status": lease.get("status"),
    }


def run_check(root: Path, *, selector_path: Path | None = None, now: datetime | None = None, max_age_seconds: int = DEFAULT_MAX_HEARTBEAT_AGE_SECONDS) -> dict[str, Any]:
    root = root.resolve()
    now = now or datetime.now(timezone.utc)
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    active_selector_path = selector_path.resolve(strict=False) if selector_path else root / ACTIVE_SELECTOR_RELATIVE
    leases_dir = active_selector_path.parent / "leases" if selector_path else root / SELECTOR_LEASES_RELATIVE

    selector_summary: dict[str, Any] | None = None
    selector_id: str | None = None
    if active_selector_path.exists():
        selector = read_json(active_selector_path, errors, "active selector")
        if selector is not None:
            selector_id = selector.get("selector_id") if isinstance(selector.get("selector_id"), str) else None
            selector_summary = validate_selector(
                root=root,
                selector_path=active_selector_path,
                selector=selector,
                now=now,
                max_age_seconds=max_age_seconds,
                errors=errors,
                warnings=warnings,
            )
    else:
        info.append("No repo-local active selector found; automatic durable adoption must report a selector refresh gap instead of using compatibility records.")

    lease_summaries: list[dict[str, Any]] = []
    if leases_dir.exists():
        for lease_path in sorted(leases_dir.glob("*.json")):
            lease = read_json(lease_path, errors, "selector lease")
            if lease is not None:
                lease_summaries.append(validate_lease(root, lease_path, lease, selector_id, errors, warnings))

    adoption_blockers: list[str] = []
    if errors:
        adoption_blockers.append("selector_ownership_invalid")
    if selector_summary is None:
        adoption_blockers.append("selector_refresh_gap")
    elif selector_summary.get("released"):
        adoption_blockers.append("selector_released")
    elif selector_summary.get("stale"):
        adoption_blockers.append("selector_stale")
    elif selector_summary.get("routing_eligible") is not True:
        adoption_blockers.append("selector_not_routing_eligible")

    adoption_allowed = bool(selector_summary) and not adoption_blockers
    if adoption_allowed:
        info.append("Repo-local active selector ownership is valid for automatic adoption.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "active_selector_path": str(active_selector_path),
        "selector_found": selector_summary is not None,
        "selector": selector_summary,
        "leases_dir": str(leases_dir),
        "leases": lease_summaries,
        "adoption_allowed": adoption_allowed,
        "adoption_blockers": adoption_blockers,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {"errors": len(errors), "warnings": len(warnings), "leases": len(lease_summaries)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local active durable selector ownership.")
    parser.add_argument("--root", default=".", help="Repository or worktree root to validate.")
    parser.add_argument("--selector", help="Optional active selector path, primarily for fixtures.")
    parser.add_argument("--max-heartbeat-age-seconds", type=int, default=DEFAULT_MAX_HEARTBEAT_AGE_SECONDS)
    parser.add_argument("--now", help="Optional ISO timestamp for deterministic stale-selector checks.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(
        Path(args.root),
        selector_path=Path(args.selector) if args.selector else None,
        now=parse_now(args.now),
        max_age_seconds=max(0, int(args.max_heartbeat_age_seconds)),
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
        if payload["ok"]:
            print("Repo-local selector ownership check passed.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
