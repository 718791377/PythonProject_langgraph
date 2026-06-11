#!/usr/bin/env python3
"""Validate user-level CloakBrowser and Academic Research runtime governance.

This checker is intentionally repo-local and read-only. It validates that the
implementation plan, safety wiring, CI registration, and optional live receipts
preserve the user-level/install-artifact boundary for:

* CloakBrowser wrapper runtime (Python and optional npm smoke)
* CloakBrowser-Manager source/receipt install with Docker explicitly not
  installed by this repository package
* academic-research-suite Codex skill installation
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_cloakbrowser_academic_runtime"
PLAN_EN = Path("docs_bilingual/implementation_plans/user_level_cloakbrowser_academic_research_runtime_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/user_level_cloakbrowser_academic_research_runtime_plan.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
DOCS_REGISTRY = Path("docs_bilingual/docs_registry.yaml")
TEST_NAME = "check_user_level_cloakbrowser_academic_runtime.test.py"
RUNTIME_SCRIPT = "tools/run_cloakbrowser_manager_source_runtime.py"

PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
EXPECTED_TOOLS: dict[str, dict[str, str]] = {
    "cloakbrowser-python": {
        "source_url": "https://github.com/CloakHQ/CloakBrowser",
        "version": "0.3.31",
    },
    "cloakbrowser-npm": {
        "source_url": "https://github.com/CloakHQ/CloakBrowser",
        "version": "0.3.31",
    },
    "cloakbrowser-manager-source": {
        "source_url": "https://github.com/CloakHQ/CloakBrowser-Manager",
        "version": "source-main",
    },
    "cloakbrowser-manager-source-runtime": {
        "source_url": "https://github.com/CloakHQ/CloakBrowser-Manager",
        "version": "source-main",
    },
    "academic-research-suite": {
        "source_url": "https://github.com/Imbad0202/academic-research-skills-codex",
        "version": "0.1.11",
    },
}

PLAN_MARKERS = (
    PRIORITY_ORDER,
    "CloakBrowser",
    "CloakBrowser-Manager",
    "academic-research-suite",
    "https://github.com/CloakHQ/CloakBrowser",
    "https://github.com/CloakHQ/CloakBrowser-Manager",
    "https://github.com/Imbad0202/academic-research-skills-codex",
    "cloakbrowser==0.3.31",
    "cloakbrowser@0.3.31",
    "Docker is not installed by this plan",
    "hash-only",
    "R6 live-ready",
    "R6 live-executed",
    "source-backend-frontend-loopback",
    "native Codex files are not modified",
    "remote publication remains unauthorized",
)
ALLOWED_PLAN_STATUSES = {"planned-local", "R6 live-executed"}
STATUS_RE = re.compile(r"^Status:\s*(.+?)\s*$", re.MULTILINE)

FORBIDDEN_RAW_KEYS = {
    "install_root",
    "wrapper_path",
    "state_path",
    "rollback_pointer",
    "raw_output",
    "stdout",
    "stderr",
    "token",
    "secret",
    "api_key",
    "cookie",
}
HASH_RE = re.compile(r"^[0-9a-fA-F]{12,64}$")
ALLOWED_REDACTION = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
ALLOWED_STAGES = {"R6 live-ready", "R6 live-executed", "R6 blocked"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        errors.append(f"missing_or_unreadable:{path.as_posix()}:{exc}")
        return ""


def read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        errors.append(f"missing_or_unreadable_json:{path.as_posix()}:{exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.as_posix()}:{exc}")
    return None


def require_markers(label: str, text: str, markers: tuple[str, ...], errors: list[str]) -> None:
    lowered = text.lower()
    for marker in markers:
        if marker.lower() not in lowered:
            errors.append(f"{label}:missing_marker:{marker}")


def check_plan(root: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, PLAN_MARKERS, errors)
        status_match = STATUS_RE.search(text)
        status = status_match.group(1).strip() if status_match else "unknown"
        if status not in ALLOWED_PLAN_STATUSES:
            errors.append(f"{rel.as_posix()}:status_must_be_one_of:{','.join(sorted(ALLOWED_PLAN_STATUSES))}")
        if "Docker is not installed by this plan" not in text:
            errors.append(f"{rel.as_posix()}:docker_non_install_boundary_missing")
        if "native Codex files are not modified" not in text:
            errors.append(f"{rel.as_posix()}:native_codex_boundary_missing")
        if "remote publication remains unauthorized" not in text:
            errors.append(f"{rel.as_posix()}:remote_publication_boundary_missing")
        result[rel.as_posix()] = {
            "status": status,
            "contains_priority_order": PRIORITY_ORDER in text,
            "contains_hash_only_policy": "hash-only" in text.lower(),
        }
    return result


def check_registry_guard_ci(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    tests: set[str] = set()
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        tests = {str(item) for item in manifest["python_unittest"]}
    if TEST_NAME not in tests:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    if "check_user_level_cloakbrowser_academic_runtime" not in guard_text:
        errors.append("openspec_guard_missing:check_user_level_cloakbrowser_academic_runtime")

    docs_text = read_text(root / DOCS_REGISTRY, errors)
    if "user_level_cloakbrowser_academic_research_runtime_plan" not in docs_text:
        errors.append("docs_registry_missing:user_level_cloakbrowser_academic_research_runtime_plan")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "user-level-cloakbrowser-academic-runtime":
                rule_found = True
                prompts = set(rule.get("prompt_reminders", [])) if isinstance(rule.get("prompt_reminders"), list) else set()
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if PLAN_EN.as_posix() not in prompts or PLAN_ZH.as_posix() not in prompts:
                    errors.append("safety_registry_rule_missing_plan_reminders")
                if "tools/check_user_level_cloakbrowser_academic_runtime.py" not in scripts:
                    errors.append("safety_registry_rule_missing_checker")
                if RUNTIME_SCRIPT not in scripts:
                    errors.append("safety_registry_rule_missing_runtime_script")
                if "check_user_level_cloakbrowser_academic_runtime" not in steps:
                    errors.append("safety_registry_rule_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:user-level-cloakbrowser-academic-runtime")

    return {
        "test_registered": TEST_NAME in tests,
        "guard_registered": "check_user_level_cloakbrowser_academic_runtime" in guard_text,
        "safety_rule_found": rule_found,
        "runtime_script_registered": RUNTIME_SCRIPT in json.dumps(registry, ensure_ascii=False) if isinstance(registry, dict) else False,
    }


def forbidden_raw_key_errors(value: Any, prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            current = f"{prefix}.{key}" if prefix else str(key)
            if lowered in FORBIDDEN_RAW_KEYS and item not in (None, "", [], {}, False):
                errors.append(f"forbidden_raw_key:{current}")
            errors.extend(forbidden_raw_key_errors(item, current))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            errors.extend(forbidden_raw_key_errors(item, f"{prefix}[{idx}]"))
    return errors


def hash_field_ok(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.match(value))


def validate_receipt(path: Path, data: Any) -> list[str]:
    errors: list[str] = []
    label = f"receipt:{path.name}"
    if not isinstance(data, dict):
        return [f"{label}:not_object"]
    tool = str(data.get("tool_name", ""))
    if tool not in EXPECTED_TOOLS:
        errors.append(f"{label}:tool_name_unknown:{tool}")
    expected = EXPECTED_TOOLS.get(tool, {})
    if data.get("schema_version") != 1:
        errors.append(f"{label}:schema_version_must_be_1")
    if data.get("runtime_stage") not in ALLOWED_STAGES:
        errors.append(f"{label}:runtime_stage_invalid")
    if expected and data.get("source_url") != expected["source_url"]:
        errors.append(f"{label}:source_url_mismatch")
    if tool in {"cloakbrowser-python", "cloakbrowser-npm"} and data.get("installed_version") != "0.3.31":
        errors.append(f"{label}:installed_version_must_be_0.3.31")
    if tool == "academic-research-suite" and data.get("installed_version") != "0.1.11":
        errors.append(f"{label}:installed_version_must_be_0.1.11")
    if tool in {"cloakbrowser-manager-source", "cloakbrowser-manager-source-runtime"} and data.get("installed_version") != "source-main":
        errors.append(f"{label}:installed_version_must_be_source-main")
    if tool in {"cloakbrowser-manager-source", "cloakbrowser-manager-source-runtime"} and data.get("docker_install_allowed") is not False:
        errors.append(f"{label}:docker_install_allowed_must_be_false")
    if tool == "cloakbrowser-manager-source-runtime":
        if data.get("runtime_stage") != "R6 live-executed":
            errors.append(f"{label}:runtime_stage_must_be_R6_live-executed")
        if data.get("runtime_stage_detail") != "source-backend-frontend-loopback":
            errors.append(f"{label}:runtime_stage_detail_must_be_source-backend-frontend-loopback")
        if data.get("container_runtime_used") is not False:
            errors.append(f"{label}:container_runtime_used_must_be_false")
        if data.get("smoke_kind") != "source-backend-frontend-loopback":
            errors.append(f"{label}:smoke_kind_must_be_source-backend-frontend-loopback")
        if data.get("api_status_http_status") != 200:
            errors.append(f"{label}:api_status_http_status_must_be_200")
        if data.get("api_status_json") is not True:
            errors.append(f"{label}:api_status_json_must_be_true")
        if data.get("gui_shell_http_status") != 200:
            errors.append(f"{label}:gui_shell_http_status_must_be_200")
        if data.get("gui_shell_html") is not True:
            errors.append(f"{label}:gui_shell_html_must_be_true")
        if data.get("profile_launch_smoke") != "not_run:no_xvnc_on_windows":
            errors.append(f"{label}:profile_launch_smoke_must_be_not_run_no_xvnc_on_windows")
    for field in ("install_root_hash", "wrapper_path_hash", "state_path_hash", "rollback_pointer_hash"):
        if not hash_field_ok(data.get(field)):
            errors.append(f"{label}:{field}_missing_or_invalid")
    smoke = data.get("smoke_result")
    if not isinstance(smoke, dict) or smoke.get("status") not in {"pass", "blocked"}:
        errors.append(f"{label}:smoke_result_status_invalid")
    elif not hash_field_ok(smoke.get("command_hash")):
        errors.append(f"{label}:smoke_result_command_hash_missing_or_invalid")
    if data.get("redaction_status") not in ALLOWED_REDACTION:
        errors.append(f"{label}:redaction_status_invalid")
    if data.get("raw_paths_included") is not False:
        errors.append(f"{label}:raw_paths_included_must_be_false")
    if data.get("remote_publication_mutated") is not False:
        errors.append(f"{label}:remote_publication_mutated_must_be_false")
    for error in forbidden_raw_key_errors(data):
        errors.append(f"{label}:{error}")
    return sorted(set(errors))


def check_receipts(receipt_dir: Path | None, *, require_live: bool, errors: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {"accepted": [], "receipt_count": 0, "missing": [], "receipt_dir": "", "sidecars_skipped": []}
    if receipt_dir is None:
        if require_live:
            errors.append("receipt_dir_required_when_require_live")
        return summary
    resolved = receipt_dir.resolve()
    summary["receipt_dir"] = str(resolved)
    files = sorted(resolved.glob("*.json")) if resolved.exists() else []
    summary["receipt_count"] = len(files)
    accepted: list[str] = []
    for path in files:
        if path.name == "summary.json":
            summary["sidecars_skipped"].append(path.name)
            continue
        load_errors: list[str] = []
        data = read_json(path, load_errors)
        if load_errors:
            errors.extend(f"receipt:{path.name}:{err}" for err in load_errors)
            continue
        blockers = validate_receipt(path, data)
        errors.extend(blockers)
        if not blockers and isinstance(data, dict):
            accepted.append(str(data.get("tool_name")))
    summary["accepted"] = sorted(accepted)
    if require_live:
        missing = sorted(set(EXPECTED_TOOLS) - set(accepted))
        summary["missing"] = missing
        errors.extend(f"receipt_missing:{tool}" for tool in missing)
    return summary


def evaluate(root: Path, receipt_dir: Path | None = None, *, require_live: bool = False) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    plans = check_plan(root, errors)
    registry = check_registry_guard_ci(root, errors)
    receipt_summary = check_receipts(receipt_dir, require_live=require_live, errors=errors)
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "plans": plans,
        "registry_guard_ci": registry,
        "receipt_summary": receipt_summary,
        "sources": {
            "cloakbrowser": {
                "source_url": "https://github.com/CloakHQ/CloakBrowser",
                "pypi_version": "0.3.31",
                "npm_version": "0.3.31",
            },
            "cloakbrowser_manager": {
                "source_url": "https://github.com/CloakHQ/CloakBrowser-Manager",
                "docker_required_for_gui_runtime": True,
                "docker_install_allowed": False,
            },
            "academic_research_suite": {
                "source_url": "https://github.com/Imbad0202/academic-research-skills-codex",
                "skill_path": "skills/academic-research-suite",
                "version": "0.1.11",
            },
        },
        "policy": {
            "priority_order": PRIORITY_ORDER,
            "docker_install_allowed": False,
            "native_codex_files_mutated": False,
            "remote_publication_allowed": False,
            "hash_only_receipts_required": True,
            "user_level_install_artifacts_only": True,
        },
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "counts": {"errors": len(set(errors)), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate user-level CloakBrowser/ARS runtime governance.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--receipt-dir", default=None)
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(Path(args.root), Path(args.receipt_dir) if args.receipt_dir else None, require_live=args.require_live)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
