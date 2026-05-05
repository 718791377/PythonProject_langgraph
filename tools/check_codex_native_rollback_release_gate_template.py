#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "codex_native_rollback_release_gate_template"
TEMPLATE_PATH = Path("tools/codex_native_rollback_release_gate_template.json")
INSTALLER_PATH = Path("tools/install-codex-user-level-team-mode.ps1")
INSTALLER_TEST_PATH = Path("test/install-codex-user-level-team-mode.test.ps1")
RUN_GUARD_PATH = Path("tools/run_openspec_guard.py")

REQUIRED_FIELDS = [
    "gate_id",
    "target_repository",
    "release_version",
    "operator_consent_boundary",
    "native_codex_entrypoint",
    "raw_bypass_entrypoint",
    "wrapped_entrypoint",
    "installer_rollback_test",
    "openspec_guard",
    "config_toml_sentinel",
    "manual_rollback_path",
    "publication_rollback_path",
]

REQUIRED_CHECK_IDS = [
    "native_codex_entrypoint",
    "raw_bypass_entrypoint",
    "wrapped_entrypoint",
    "installer_rollback_test",
    "openspec_guard",
    "config_toml_sentinel",
    "manual_rollback_path",
    "publication_rollback_path",
]

ALLOWED_CHECK_TYPES = {
    "local_smoke",
    "repository_test",
    "repository_guard",
    "sentinel",
    "manual_rollback",
    "publication_rollback",
}

PROTECTED_NATIVE_ENTRYPOINTS = ["codex", "codex.cmd", "codex.ps1"]

REQUIRED_COMMAND_TERMS = {
    "native_codex_entrypoint": "codex --version",
    "raw_bypass_entrypoint": "codex-raw --version",
    "wrapped_entrypoint": "codex-ohmy",
    "installer_rollback_test": "test\\install-codex-user-level-team-mode.test.ps1",
    "openspec_guard": "tools\\run_openspec_guard.py",
    "config_toml_sentinel": "config.toml",
    "manual_rollback_path": "backups",
    "publication_rollback_path": "GitLab",
}


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing Codex native rollback release-gate template: {TEMPLATE_PATH.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {TEMPLATE_PATH.as_posix()}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{TEMPLATE_PATH.as_posix()} must contain a JSON object.")
        return {}
    return data


def read_text(path: Path, errors: list[str], label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"Missing {label}: {path.as_posix()}")
        return ""


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_path_text(value: str) -> str:
    return value.replace("/", "\\")


def validate_template(template: dict[str, Any], errors: list[str]) -> None:
    if template.get("schema_version") != 1:
        errors.append("Template must declare schema_version 1.")
    if template.get("template_id") != "codex-native-rollback-release-gate-template":
        errors.append("Template must declare template_id codex-native-rollback-release-gate-template.")
    if not non_empty_string(template.get("purpose")):
        errors.append("Template must declare a non-empty purpose.")

    defaults = template.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("Template defaults must be an object.")
        defaults = {}
    if defaults.get("mutation_allowed") is not False:
        errors.append("Template default mutation_allowed must be false.")
    if defaults.get("release_marking_allowed") is not False:
        errors.append("Template default release_marking_allowed must be false.")

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

    protected = template.get("protected_native_entrypoints")
    if protected != PROTECTED_NATIVE_ENTRYPOINTS:
        errors.append(
            "Template protected_native_entrypoints must be exactly: "
            + ", ".join(PROTECTED_NATIVE_ENTRYPOINTS)
        )

    allowed = template.get("allowed_check_types")
    if not isinstance(allowed, list) or set(allowed) != ALLOWED_CHECK_TYPES:
        errors.append("Template allowed_check_types must list the canonical release-gate check types.")

    checks = template.get("required_release_checks")
    if not isinstance(checks, list):
        errors.append("Template required_release_checks must be a list.")
        checks = []

    ids = [item.get("id") for item in checks if isinstance(item, dict)]
    if ids != REQUIRED_CHECK_IDS:
        errors.append(
            "Template required_release_checks ids must match the canonical ordered list: "
            + ", ".join(REQUIRED_CHECK_IDS)
        )

    for item in checks:
        if not isinstance(item, dict):
            errors.append("Every required_release_checks item must be an object.")
            continue
        check_id = item.get("id")
        if check_id not in REQUIRED_CHECK_IDS:
            errors.append(f"Unexpected release check id: {check_id!r}")
            continue
        if item.get("check_type") not in ALLOWED_CHECK_TYPES:
            errors.append(f"Release check {check_id} has invalid check_type: {item.get('check_type')!r}")
        if item.get("evidence_required") is not True:
            errors.append(f"Release check {check_id} must require evidence.")
        if not isinstance(item.get("ci_required"), bool):
            errors.append(f"Release check {check_id} must declare a boolean ci_required field.")
        if not non_empty_string(item.get("description")):
            errors.append(f"Release check {check_id} must have a non-empty description.")
        command_or_path = item.get("command_or_path")
        if not non_empty_string(command_or_path):
            errors.append(f"Release check {check_id} must have a non-empty command_or_path.")
        else:
            normalized = normalize_path_text(command_or_path)
            expected = normalize_path_text(REQUIRED_COMMAND_TERMS[check_id])
            if expected not in normalized:
                errors.append(f"Release check {check_id} command_or_path must mention {REQUIRED_COMMAND_TERMS[check_id]}.")

    guards = template.get("non_mutation_guards")
    if not isinstance(guards, list) or not guards:
        errors.append("Template non_mutation_guards must be a non-empty list.")
        guards = []
    guard_text = "\n".join(str(item) for item in guards)
    for term in ["codex.cmd", "config.toml", "real user Codex home", "native_omx", "LangGraph"]:
        if term not in guard_text:
            errors.append(f"Template non_mutation_guards must mention {term}.")

    blockers = template.get("release_blockers")
    if not isinstance(blockers, list) or len(blockers) < 5:
        errors.append("Template release_blockers must list the main release-blocking evidence gaps.")
        blockers = []
    blocker_text = "\n".join(str(item) for item in blockers)
    for term in ["native Codex", "raw bypass", "wrapped launcher", "rollback", "config.toml"]:
        if term not in blocker_text:
            errors.append(f"Template release_blockers must mention {term}.")


def validate_source_evidence(root: Path, errors: list[str]) -> None:
    installer = read_text(root / INSTALLER_PATH, errors, "user-level team-mode installer")
    installer_test = read_text(root / INSTALLER_TEST_PATH, errors, "installer rollback test")
    run_guard = read_text(root / RUN_GUARD_PATH, errors, "aggregate OpenSpec guard")

    if installer:
        for term in [
            "$Script:NativeCodexNames",
            "codex.cmd",
            "codex.ps1",
            "New-InstallBackupSnapshot",
            "Restore-InstallBackupSnapshot",
            "rollback_on_error",
        ]:
            if term not in installer:
                errors.append(f"{INSTALLER_PATH.as_posix()} must contain source evidence term: {term}")

    if installer_test:
        for term in [
            "preserves_native_codex",
            "backup",
            "rollback",
            "codex-raw.cmd",
            "codex-native.cmd",
            "TestFailPoint",
        ]:
            if term not in installer_test:
                errors.append(f"{INSTALLER_TEST_PATH.as_posix()} must contain test evidence term: {term}")

    if run_guard:
        for term in [
            "check_codex_native_rollback_release_gate_template",
            "codex_native_rollback_release_gate_template",
        ]:
            if term not in run_guard:
                errors.append(f"{RUN_GUARD_PATH.as_posix()} must run or reference the release-gate checker term: {term}")


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    template = read_json(root / TEMPLATE_PATH, errors)
    if template:
        validate_template(template, errors)
    validate_source_evidence(root, errors)

    if not errors:
        info.append(
            "Codex native rollback release-gate template is present, read-only by default, "
            "and backed by static native-preservation and rollback source evidence."
        )

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
            "required_release_checks": len(REQUIRED_CHECK_IDS),
            "protected_native_entrypoints": len(PROTECTED_NATIVE_ENTRYPOINTS),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the Codex native preservation and rollback release-gate template.")
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
