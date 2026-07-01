#!/usr/bin/env python3
"""Validate Reference 6/7/8 recursive installable-unit surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "reference_recursive_capability_install"
RUNTIME = Path("tools/reference_recursive_capability_install.py")
MANIFEST = Path("tools/reference_recursive_capability_install/manifest.json")
PLAN_EN = Path("docs_bilingual/implementation_plans/reference6_7_8_recursive_install_live_runtime_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/reference6_7_8_recursive_install_live_runtime_plan.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
TEST_NAME = "reference_recursive_capability_install.test.py"
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
PLAN_MARKERS = [
    "reference_files/6.md",
    "reference_files/7.md",
    "reference_files/8.md",
    "recursive installable-unit",
    "Browserbase",
    "Matt Pocock",
    "D:/PythonProject_General",
    "D:/PythonProject_General_2",
    "hash-redacted",
]


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


def run_json(command: list[str], cwd: Path) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = None
    return proc.returncode, data, proc.stderr


def require_markers(label: str, text: str, markers: list[str], errors: list[str]) -> None:
    lowered = text.lower()
    for marker in markers:
        if marker.lower() not in lowered:
            errors.append(f"{label}:missing_marker:{marker}")


def check_manifest(root: Path, errors: list[str]) -> dict[str, Any]:
    data = read_json(root / MANIFEST, errors)
    if not isinstance(data, dict):
        return {}
    if data.get("priority_order") != PRIORITY_ORDER:
        errors.append("manifest_priority_order_mismatch")
    if data.get("browserbase_policy") != "disabled_by_user":
        errors.append("manifest_browserbase_policy_must_be_disabled_by_user")
    policy = data.get("generated_policy")
    if not isinstance(policy, dict):
        errors.append("manifest_missing_generated_policy")
    else:
        if policy.get("raw_upstream_install_counts_as_codex_live_executed") is not False:
            errors.append("manifest_raw_upstream_install_must_not_count")
        if policy.get("mutates_native_codex_files") is not False:
            errors.append("manifest_must_not_mutate_native_codex")
        if policy.get("mutates_codex_config_toml") is not False:
            errors.append("manifest_must_not_mutate_codex_config")
    unit_items = data.get("units")
    if not isinstance(unit_items, list) or not unit_items:
        errors.append("manifest_missing_recursive_units")
        return data
    by_parent: dict[str, int] = {}
    by_state: dict[str, int] = {}
    for unit in unit_items:
        if not isinstance(unit, dict):
            errors.append("manifest_unit_not_object")
            continue
        for field in (
            "reference_id",
            "parent_capability_id",
            "child_unit_id",
            "source_url",
            "capability_unit_path",
            "installable_marker_kind",
            "child_state",
        ):
            if not unit.get(field):
                errors.append(f"manifest_unit_missing_{field}")
        by_parent[str(unit.get("parent_capability_id"))] = by_parent.get(str(unit.get("parent_capability_id")), 0) + 1
        by_state[str(unit.get("child_state"))] = by_state.get(str(unit.get("child_state")), 0) + 1
        if unit.get("parent_capability_id") == "browserbase-skills" and unit.get("child_state") != "disabled":
            errors.append("browserbase_child_not_disabled")
        if unit.get("child_state") == "provision-recorded" and not unit.get("provision_required"):
            errors.append("provision_child_missing_provision_required")
    if by_parent.get("mattpocock-skills", 0) < 30:
        errors.append("mattpocock_child_units_not_recursively_expanded")
    if by_parent.get("browserbase-skills", 0) < 10:
        errors.append("browserbase_child_units_not_recursively_expanded")
    if by_state.get("disabled", 0) < by_parent.get("browserbase-skills", 0):
        errors.append("disabled_count_must_cover_browserbase_children")
    if by_state.get("live-executed", 0) <= 0:
        errors.append("manifest_missing_live_executed_children")
    return data


def check_registry_guard_ci(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    tests: set[str] = set()
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        tests = {str(item) for item in manifest["python_unittest"]}
    if TEST_NAME not in tests:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")
    guard_text = read_text(root / GUARD, errors)
    if "check_reference_recursive_capability_install" not in guard_text:
        errors.append("openspec_guard_missing:check_reference_recursive_capability_install")
    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "reference-recursive-capability-install":
                rule_found = True
                prompts = set(rule.get("prompt_reminders", [])) if isinstance(rule.get("prompt_reminders"), list) else set()
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if PLAN_EN.as_posix() not in prompts or PLAN_ZH.as_posix() not in prompts:
                    errors.append("safety_registry_missing_recursive_plan_reminders")
                if "tools/check_reference_recursive_capability_install.py" not in scripts:
                    errors.append("safety_registry_missing_recursive_checker")
                if "tools/reference_recursive_capability_install.py" not in scripts:
                    errors.append("safety_registry_missing_recursive_runtime")
                if "check_reference_recursive_capability_install" not in steps:
                    errors.append("safety_registry_missing_recursive_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:reference-recursive-capability-install")
    return {
        "test_registered": TEST_NAME in tests,
        "guard_registered": "check_reference_recursive_capability_install" in guard_text,
        "safety_rule_found": rule_found,
    }


def check_runtime_plan(root: Path, errors: list[str]) -> dict[str, Any]:
    if not (root / RUNTIME).is_file():
        errors.append(f"missing_runtime:{RUNTIME.as_posix()}")
        return {}
    code, payload, stderr = run_json([sys.executable, str(root / RUNTIME), "plan", "--json"], root)
    if code != 0 or not isinstance(payload, dict):
        errors.append("runtime_plan_failed:" + stderr.strip())
        return {}
    if not payload.get("ok"):
        errors.append("runtime_plan_not_ok")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(summary.get("unit_count") or 0) < 900:
        errors.append("runtime_plan_unit_count_too_low")
    if payload.get("browserbase_policy") != "disabled_by_user":
        errors.append("runtime_plan_browserbase_policy_mismatch")
    if payload.get("codex_config_toml_mutated") is not False:
        errors.append("runtime_plan_must_not_mutate_codex_config")
    if payload.get("native_codex_files_mutated") is not False:
        errors.append("runtime_plan_must_not_mutate_native_codex")
    return payload


def evaluate(
    root: Path,
    *,
    codex_home: Path | None,
    general_root: Path | None,
    general2_root: Path | None,
    require_user_level_installed: bool,
    require_smoke_tested: bool,
    require_live_executed: bool,
    require_template_sync: bool,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    for rel in (PLAN_EN, PLAN_ZH):
        require_markers(rel.as_posix(), read_text(root / rel, errors), PLAN_MARKERS, errors)
    manifest = check_manifest(root, errors)
    registry = check_registry_guard_ci(root, errors)
    runtime_plan = check_runtime_plan(root, errors)
    recursive_check: dict[str, Any] | None = None
    if require_user_level_installed or require_smoke_tested or require_live_executed or require_template_sync:
        cmd = [sys.executable, str(root / RUNTIME), "check", "--json"]
        if codex_home:
            cmd.extend(["--codex-home", str(codex_home)])
        if general_root:
            cmd.extend(["--general-root", str(general_root)])
        if general2_root:
            cmd.extend(["--general2-root", str(general2_root)])
        if require_user_level_installed:
            cmd.append("--require-installed")
        if require_smoke_tested:
            cmd.append("--require-smoke-tested")
        if require_live_executed:
            cmd.append("--require-live-executed")
        if require_template_sync:
            cmd.append("--require-template-sync")
        code, recursive_check, stderr = run_json(cmd, root)
        if code != 0 or not isinstance(recursive_check, dict) or not recursive_check.get("ok"):
            errors.append("user_level_reference_recursive_check_failed:" + stderr.strip())
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "manifest": {
            "unit_count": len(manifest.get("units", [])) if isinstance(manifest, dict) else 0,
            "expected_counts": manifest.get("expected_counts") if isinstance(manifest, dict) else None,
        },
        "registry_guard_ci": registry,
        "runtime_plan": runtime_plan,
        "recursive_check": recursive_check,
        "policy": {
            "priority_order": PRIORITY_ORDER,
            "browserbase_policy": "disabled_by_user",
            "raw_upstream_install_counts_as_live_executed": False,
            "source_reference_only_counts_as_live_executed": False,
            "remote_publication_allowed": False,
        },
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "counts": {"errors": len(set(errors)), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Reference recursive capability install surfaces.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codex-home", default=None)
    parser.add_argument("--general-root", default=None)
    parser.add_argument("--general2-root", default=None)
    parser.add_argument("--require-user-level-installed", action="store_true")
    parser.add_argument("--require-smoke-tested", action="store_true")
    parser.add_argument("--require-live-executed", action="store_true")
    parser.add_argument("--require-template-sync", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(
        Path(args.root),
        codex_home=Path(args.codex_home).resolve() if args.codex_home else None,
        general_root=Path(args.general_root).resolve() if args.general_root else None,
        general2_root=Path(args.general2_root).resolve() if args.general2_root else None,
        require_user_level_installed=bool(args.require_user_level_installed),
        require_smoke_tested=bool(args.require_smoke_tested),
        require_live_executed=bool(args.require_live_executed),
        require_template_sync=bool(args.require_template_sync),
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
