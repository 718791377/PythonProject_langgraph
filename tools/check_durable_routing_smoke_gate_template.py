#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "durable_routing_smoke_gate_template"
TEMPLATE_PATH = Path("tools/durable_routing_smoke_gate_template.json")
FIXTURE_DIR = Path("tools/fixtures/durable_routing_smoke_gate_template")
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


def display_path(path: Path) -> str:
    return path.as_posix()


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing durable routing smoke gate template: {display_path(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {display_path(path)}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{display_path(path)} must contain a JSON object.")
        return {}
    return data


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_template(template: dict[str, Any], errors: list[str]) -> None:
    """Validate the repository-local durable routing smoke/adoption gate template.

    This checker intentionally validates static JSON only. It must remain read-only:
    no durable runtime launch, no `omx-team-auto.ps1 -Apply`, and no `.omx/state`
    writes are needed to prove the gate-template contract.
    """
    if template.get("schema_version") != 1:
        errors.append("Template must declare schema_version 1.")
    if template.get("template_id") != "durable-routing-smoke-gate-template":
        errors.append("Template must declare template_id durable-routing-smoke-gate-template.")
    if template.get("release_floor") != "R0.6.0":
        errors.append("Template must declare release_floor R0.6.0.")
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
    if defaults.get("routing_mode") == "apply" and defaults.get("mutation_allowed") is not True:
        errors.append(
            "Apply routing_mode requires mutation_allowed true and explicit operator consent; "
            "the canonical R0.6.0 template must remain read_only."
        )

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


def resolve_path(root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return root / path


def validate_template_path(root: Path, template_path: Path) -> list[str]:
    errors: list[str] = []
    template = read_json(resolve_path(root, template_path), errors)
    if template:
        validate_template(template, errors)
    return errors


def run_self_test(root: Path, fixture_dir: Path) -> dict[str, Any]:
    fixture_root = resolve_path(root, fixture_dir)
    fixture_specs = [
        {
            "path": fixture_root / "valid_template.json",
            "expected_ok": True,
            "expected_error_terms": [],
        },
        {
            "path": fixture_root / "missing_required_fields.json",
            "expected_ok": False,
            "expected_error_terms": ["required_fields"],
        },
        {
            "path": fixture_root / "apply_without_mutation_consent.json",
            "expected_ok": False,
            "expected_error_terms": ["default routing_mode must be read_only", "Apply routing_mode requires"],
        },
        {
            "path": fixture_root / "missing_read_only_guards.json",
            "expected_ok": False,
            "expected_error_terms": ["read_only_guards must mention"],
        },
    ]

    results: list[dict[str, Any]] = []
    harness_errors: list[str] = []
    for spec in fixture_specs:
        errors = validate_template_path(root, spec["path"])
        ok = not errors
        error_text = "\n".join(errors)
        missing_terms = [term for term in spec["expected_error_terms"] if term not in error_text]
        if ok != spec["expected_ok"]:
            harness_errors.append(
                f"Fixture {display_path(spec['path'])} expected ok={spec['expected_ok']} but got ok={ok}."
            )
        if missing_terms:
            harness_errors.append(
                f"Fixture {display_path(spec['path'])} did not emit expected error terms: "
                + ", ".join(missing_terms)
            )
        results.append(
            {
                "path": display_path(spec["path"]),
                "expected_ok": spec["expected_ok"],
                "ok": ok,
                "errors": errors,
                "expected_error_terms": spec["expected_error_terms"],
                "missing_expected_error_terms": missing_terms,
            }
        )

    return {
        "ok": not harness_errors,
        "fixture_dir": display_path(fixture_root),
        "fixtures": results,
        "errors": harness_errors,
        "counts": {
            "fixtures": len(results),
            "negative_fixtures": sum(1 for item in fixture_specs if not item["expected_ok"]),
            "fixture_failures": len(harness_errors),
        },
    }


def run_check(root: Path, template_path: Path = TEMPLATE_PATH, self_test: bool = True, fixture_dir: Path = FIXTURE_DIR) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    resolved_template_path = resolve_path(root, template_path)
    template = read_json(resolved_template_path, errors)

    if template:
        validate_template(template, errors)

    self_test_result: dict[str, Any] | None = None
    if self_test:
        self_test_result = run_self_test(root, fixture_dir)
        errors.extend(f"Self-test failure: {message}" for message in self_test_result["errors"])

    if not errors:
        info.append("Durable routing smoke gate template is present, read-only by default, and has required field descriptions.")
        if self_test_result is not None:
            info.append("Durable routing smoke gate template self-test fixtures passed, including negative adoption-gate fixtures.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "template": display_path(template_path),
        "self_test": self_test_result,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "required_fields": len(REQUIRED_FIELDS),
            "self_test_fixtures": 0 if self_test_result is None else self_test_result["counts"]["fixtures"],
            "negative_self_test_fixtures": 0 if self_test_result is None else self_test_result["counts"]["negative_fixtures"],
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the durable routing smoke gate template.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--template", default=str(TEMPLATE_PATH), help="Template JSON path relative to --root, or an absolute path.")
    parser.add_argument("--skip-self-test", action="store_true", help="Skip read-only fixture checks. Intended only for narrow fixture debugging.")
    parser.add_argument("--fixture-dir", default=str(FIXTURE_DIR), help="Fixture directory relative to --root, or an absolute path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root), template_path=Path(args.template), self_test=not args.skip_self_test, fixture_dir=Path(args.fixture_dir))
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
