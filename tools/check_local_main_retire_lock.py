#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "local_main_retire_lock"
LOCK_RELATIVE = Path(".omx/locks/local-main-retire.lock")
REQUIRED_STRINGS = ("lock_name", "status", "owner_session_id", "branch", "worktree", "entry_id", "created_at", "expires_at", "nonce")
STALE_RECLAIM_FLAG = "reclaim-stale"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = root / LOCK_RELATIVE
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    lock: dict[str, Any] | None = None
    expired = False

    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            data = None
        except OSError as exc:
            errors.append(f"{path}: cannot read lock: {exc}")
            data = None
        if data is not None:
            if not isinstance(data, dict):
                errors.append(f"{path}: lock must be a JSON object")
            else:
                lock = data
                if data.get("schema_version") != 1:
                    errors.append(f"{path}: `schema_version` must be 1")
                for field in REQUIRED_STRINGS:
                    value = data.get(field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(f"{path}: `{field}` must be a non-empty string")
                if data.get("lock_name") != "local-main-retire":
                    errors.append(f"{path}: `lock_name` must be local-main-retire")
                if data.get("status") != "active":
                    errors.append(f"{path}: active lock file must have status `active`")
                created = parse_timestamp(data.get("created_at"))
                expires = parse_timestamp(data.get("expires_at"))
                if created is None:
                    errors.append(f"{path}: `created_at` must be an ISO timestamp")
                if expires is None:
                    errors.append(f"{path}: `expires_at` must be an ISO timestamp")
                elif expires <= utc_now():
                    expired = True
                    warnings.append(f"{path}: active local-main retire lock is stale")
                    info.append(
                        f"Stale lock recovery requires an explicit operator-controlled `{STALE_RECLAIM_FLAG}` action."
                    )
                if created and expires and expires <= created:
                    errors.append(f"{path}: `expires_at` must be after `created_at`")
    else:
        info.append("No active local-main retire lock is present.")

    return {
        "schema_version": 1,
        "generated_at": utc_now().isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "lock_path": str(path),
        "locked": lock is not None,
        "expired": expired,
        "lock": lock,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "active_locks": 1 if lock is not None else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local local-main retire lock state.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("local_main_retire_lock: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
