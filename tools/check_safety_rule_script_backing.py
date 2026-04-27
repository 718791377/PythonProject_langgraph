#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "safety_rule_script_backing"
REGISTRY_PATH = Path("tools/safety_rule_script_backing_registry.json")
GUARD_PATH = Path("tools/run_openspec_guard.py")

RULE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_OWNER_LEVELS = {"system", "user", "project"}
VALID_STATUSES = {"implemented", "planned", "tracked_gap"}


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def load_registry(root: Path, errors: list[str]) -> dict[str, Any]:
    path = root / REGISTRY_PATH
    text = read_text(path)
    if text is None:
        errors.append(f"Missing or unreadable safety rule registry: {REGISTRY_PATH.as_posix()}")
        return {}
    try:
        registry = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {REGISTRY_PATH.as_posix()}: {exc}")
        return {}
    if not isinstance(registry, dict):
        errors.append(f"{REGISTRY_PATH.as_posix()} must contain a JSON object.")
        return {}
    return registry


def require_existing_paths(root: Path, rule_id: str, field: str, paths: Any, errors: list[str]) -> list[str]:
    if not isinstance(paths, list) or not paths:
        errors.append(f"Rule {rule_id} must declare a non-empty {field} list.")
        return []
    normalized: list[str] = []
    for value in paths:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Rule {rule_id} has an invalid {field} entry: {value!r}")
            continue
        relative = Path(value)
        normalized.append(relative.as_posix())
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Rule {rule_id} {field} path must be repository-relative: {value}")
            continue
        if not (root / relative).exists():
            errors.append(f"Rule {rule_id} references missing {field} path: {value}")
    return normalized


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked_rules: list[dict[str, Any]] = []

    registry = load_registry(root, errors)
    rules = registry.get("rules", []) if isinstance(registry, dict) else []
    if registry.get("schema_version") != 1:
        errors.append(f"{REGISTRY_PATH.as_posix()} must declare schema_version 1.")
    if not isinstance(rules, list) or not rules:
        errors.append(f"{REGISTRY_PATH.as_posix()} must declare a non-empty rules list.")
        rules = []

    guard_text = read_text(root / GUARD_PATH)
    if guard_text is None:
        errors.append(f"Missing or unreadable guard script: {GUARD_PATH.as_posix()}")
        guard_text = ""

    seen_rule_ids: set[str] = set()
    for index, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict):
            errors.append(f"Rule entry {index} must be a JSON object.")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not RULE_ID_PATTERN.match(rule_id):
            errors.append(f"Rule entry {index} has invalid id: {rule_id!r}")
            rule_id = f"<invalid-{index}>"
        if rule_id in seen_rule_ids:
            errors.append(f"Duplicate safety rule id: {rule_id}")
        seen_rule_ids.add(rule_id)

        owner_level = rule.get("owner_level")
        if owner_level not in VALID_OWNER_LEVELS:
            errors.append(f"Rule {rule_id} has invalid owner_level: {owner_level!r}")

        status = rule.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"Rule {rule_id} has invalid status: {status!r}")

        prompt_paths = require_existing_paths(root, rule_id, "prompt_reminders", rule.get("prompt_reminders"), errors)
        script_paths = require_existing_paths(root, rule_id, "script_controls", rule.get("script_controls"), errors)

        guard_steps = rule.get("guard_steps", [])
        if not isinstance(guard_steps, list):
            errors.append(f"Rule {rule_id} guard_steps must be a list when present.")
            guard_steps = []
        for step in guard_steps:
            if not isinstance(step, str) or not step.strip():
                errors.append(f"Rule {rule_id} has invalid guard step: {step!r}")
                continue
            if step not in guard_text:
                errors.append(f"Rule {rule_id} guard step is not referenced by {GUARD_PATH.as_posix()}: {step}")

        if status == "implemented":
            if not script_paths:
                errors.append(f"Rule {rule_id} is implemented but has no executable script control.")
            if not prompt_paths:
                errors.append(f"Rule {rule_id} is implemented but has no prompt reminder location.")
        else:
            gap = rule.get("gap")
            if not isinstance(gap, str) or not gap.strip():
                errors.append(f"Rule {rule_id} is not implemented and must declare a tracked gap.")

        checked_rules.append(
            {
                "id": rule_id,
                "owner_level": owner_level,
                "status": status,
                "prompt_reminders": prompt_paths,
                "script_controls": script_paths,
                "guard_steps": guard_steps,
            }
        )

    if not errors:
        info.append("Every registered safety rule has script backing, prompt reminders, and guard linkage or tracked gap metadata.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "registry": REGISTRY_PATH.as_posix(),
        "rules": checked_rules,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "rules": len(checked_rules),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that registered safety rules have executable script controls and prompt reminders."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
