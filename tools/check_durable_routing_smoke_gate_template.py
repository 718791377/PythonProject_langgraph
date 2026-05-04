#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "durable_routing_smoke_gate_template"
TEMPLATE_PATH = Path("tools/durable_routing_smoke_gate_template.json")
REQUIRED_FIELDS = [
    "target_repository",
    "phase",
    "task",
    "operator_consent_boundary",
    "routing_mode",
    "mutation_allowed",
    "validation_path",
    "rollback_path",
]
ALLOWED_ROUTING_MODES = {"read_only", "dry_run", "apply"}
READ_ONLY_GUARD_TERMS = ["omx-team-auto.ps1 -Apply", "native_omx", "LangGraph", ".omx/state"]


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing durable routing smoke gate template: {TEMPLATE_PATH.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {TEMPLATE_PATH.as_posix()}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{TEMPLATE_PATH.as_posix()} must contain a JSON object.")
        return {}
    return data


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    template_path = root / TEMPLATE_PATH
    template = read_json(template_path, errors)

    if template:
        if template.get("schema_version") != 1:
            errors.append("Template must declare schema_version 1.")
        if template.get("template_id") != "durable-routing-smoke-gate-template":
            errors.append("Template must declare template_id durable-routing-smoke-gate-template.")
        if not non_empty_string(template.get("purpose")):
            errors.append("Template must declare a non-empty purpose.")

        required_fields = template.get("required_fields")
        if required_fields != REQUIRED_FIELDS:
            errors.append(
                "Template required_fields must match the canonical ordered field list: "
                + ", ".join(REQUIRED_FIELDS)
            )

        descriptions = template.get("field_descriptions")
        if not isinstance(descriptions, dict):
            errors.append("Template field_descriptions must be an object.")
            descriptions = {}
        for field in REQUIRED_FIELDS:
            if not non_empty_string(descriptions.get(field)):
                errors.append(f"Template field {field} must have a non-empty description.")

        defaults = template.get("defaults")
        if not isinstance(defaults, dict):
            errors.append("Template defaults must be an object.")
            defaults = {}
        if defaults.get("routing_mode") != "read_only":
            errors.append("Template default routing_mode must be read_only.")
        if defaults.get("mutation_allowed") is not False:
            errors.append("Template default mutation_allowed must be false.")

        allowed_modes = template.get("allowed_routing_modes")
        if not isinstance(allowed_modes, list) or set(allowed_modes) != ALLOWED_ROUTING_MODES:
            errors.append("Template allowed_routing_modes must be read_only, dry_run, and apply.")

        read_only_guards = template.get("read_only_guards")
        if not isinstance(read_only_guards, list) or not read_only_guards:
            errors.append("Template read_only_guards must be a non-empty list.")
            read_only_guards = []
        guard_text = "\n".join(str(item) for item in read_only_guards)
        for term in READ_ONLY_GUARD_TERMS:
            if term not in guard_text:
                errors.append(f"Template read_only_guards must mention {term}.")

    if not errors:
        info.append("Durable routing smoke gate template is present, read-only by default, and has required field descriptions.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "template": TEMPLATE_PATH.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_fields": len(REQUIRED_FIELDS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the durable routing smoke gate template.")
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
