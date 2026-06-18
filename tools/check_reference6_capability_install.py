#!/usr/bin/env python3
"""Validate Reference 6 user-level and project-template install surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "reference6_capability_install"
RUNTIME = Path("tools/reference6_capability_install.py")
MANIFEST = Path("tools/reference6_capability_install/manifest.json")
PLAN_EN = Path("docs_bilingual/implementation_plans/reference6_user_project_capability_install_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/reference6_user_project_capability_install_plan.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
TEST_NAME = "reference6_capability_install.test.py"
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
CAPABILITY_IDS = {
    "open-design",
    "html-anything",
    "browserbase-skills",
    "pymupdf",
    "mineru",
    "mineru-api-limit",
    "mineru-site",
    "book-to-skill",
    "mattpocock-skills",
}
PLAN_MARKERS = [
    "reference_files/6.md",
    "open-design",
    "html-anything",
    "browserbase/skills",
    "pymupdf",
    "MinerU",
    "mineru.net/apiManage/limit",
    "mineru.net/",
    "book-to-skill",
    "mattpocock/skills",
    "env_key",
    "redacted receipts",
    "D:\\PythonProject_General",
    "D:\\PythonProject_General_2",
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
    policy = data.get("codex_config_policy")
    if not isinstance(policy, dict):
        errors.append("manifest_missing_codex_config_policy")
    else:
        if policy.get("reuse_mode") != "env_key_name_only":
            errors.append("manifest_codex_config_reuse_mode_must_be_env_key_name_only")
        if policy.get("copy_secret_values") is not False:
            errors.append("manifest_must_not_copy_secret_values")
        if policy.get("encoding") != "utf-8-sig":
            errors.append("manifest_must_read_config_utf8_sig")
    caps = data.get("capabilities")
    observed = {str(item.get("id")) for item in caps if isinstance(item, dict)} if isinstance(caps, list) else set()
    missing = sorted(CAPABILITY_IDS - observed)
    extra = sorted(observed - CAPABILITY_IDS)
    if missing:
        errors.append("manifest_missing_capabilities:" + ",".join(missing))
    if extra:
        errors.append("manifest_unexpected_capabilities:" + ",".join(extra))
    for item in caps if isinstance(caps, list) else []:
        if not isinstance(item, dict):
            continue
        if not item.get("source_url") or not item.get("install_mode") or not item.get("smoke_kind"):
            errors.append(f"manifest_capability_incomplete:{item.get('id')}")
        live = item.get("live_runtime")
        if not isinstance(live, dict):
            errors.append(f"manifest_capability_missing_live_runtime:{item.get('id')}")
            continue
        if not live.get("live_runtime_target") or not live.get("live_smoke_kind"):
            errors.append(f"manifest_live_runtime_missing_target_or_kind:{item.get('id')}")
        if live.get("codex_adapter_required") is not True:
            errors.append(f"manifest_live_runtime_must_require_codex_adapter:{item.get('id')}")
        if live.get("raw_upstream_install_only_counts") is not False:
            errors.append(f"manifest_raw_upstream_install_must_not_count:{item.get('id')}")
        if live.get("source_reference_only_counts") is not False:
            errors.append(f"manifest_source_reference_must_not_count:{item.get('id')}")
    return data


def check_registry_guard_ci(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    tests: set[str] = set()
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        tests = {str(item) for item in manifest["python_unittest"]}
    if TEST_NAME not in tests:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")

    guard_text = read_text(root / GUARD, errors)
    if "check_reference6_capability_install" not in guard_text:
        errors.append("openspec_guard_missing:check_reference6_capability_install")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "reference6-capability-install":
                rule_found = True
                prompts = set(rule.get("prompt_reminders", [])) if isinstance(rule.get("prompt_reminders"), list) else set()
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if PLAN_EN.as_posix() not in prompts or PLAN_ZH.as_posix() not in prompts:
                    errors.append("safety_registry_missing_plan_reminders")
                if "tools/check_reference6_capability_install.py" not in scripts:
                    errors.append("safety_registry_missing_checker")
                if "tools/reference6_capability_install.py" not in scripts:
                    errors.append("safety_registry_missing_runtime")
                if "check_reference6_capability_install" not in steps:
                    errors.append("safety_registry_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:reference6-capability-install")
    return {
        "test_registered": TEST_NAME in tests,
        "guard_registered": "check_reference6_capability_install" in guard_text,
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
    if payload.get("codex_config_toml_mutated") is not False:
        errors.append("runtime_plan_must_not_mutate_codex_config")
    caps = payload.get("capabilities")
    observed = {str(item.get("id")) for item in caps if isinstance(item, dict)} if isinstance(caps, list) else set()
    if observed != CAPABILITY_IDS:
        errors.append("runtime_plan_capability_set_mismatch")
    env_policy = payload.get("codex_provider_env")
    if not isinstance(env_policy, dict) or env_policy.get("copy_secret_values") is not False:
        errors.append("runtime_plan_missing_env_key_only_policy")
    return payload


def evaluate(
    root: Path,
    *,
    codex_home: Path | None,
    require_user_level_installed: bool,
    require_smoke_tested: bool,
    require_live_executed: bool,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    for rel in (PLAN_EN, PLAN_ZH):
        require_markers(rel.as_posix(), read_text(root / rel, errors), PLAN_MARKERS, errors)
    manifest = check_manifest(root, errors)
    registry = check_registry_guard_ci(root, errors)
    runtime_plan = check_runtime_plan(root, errors)

    user_level_check: dict[str, Any] | None = None
    if require_user_level_installed or require_smoke_tested or require_live_executed:
        cmd = [sys.executable, str(root / RUNTIME), "check", "--json"]
        if codex_home:
            cmd.extend(["--codex-home", str(codex_home)])
        if require_user_level_installed:
            cmd.append("--require-installed")
        if require_smoke_tested:
            cmd.append("--require-smoke-tested")
        if require_live_executed:
            cmd.append("--require-live-executed")
        code, user_level_check, stderr = run_json(cmd, root)
        if code != 0 or not isinstance(user_level_check, dict) or not user_level_check.get("ok"):
            errors.append("user_level_reference6_check_failed:" + stderr.strip())

    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "manifest": {"capability_count": len(manifest.get("capabilities", [])) if isinstance(manifest, dict) else 0},
        "registry_guard_ci": registry,
        "runtime_plan": runtime_plan,
        "user_level_check": user_level_check,
        "policy": {
            "priority_order": PRIORITY_ORDER,
            "codex_config_env_key_name_only": True,
            "copies_secret_values": False,
            "source_reference_counts_as_live_executed": False,
            "raw_upstream_install_counts_as_live_executed": False,
            "remote_publication_allowed": False,
        },
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "counts": {"errors": len(set(errors)), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Reference 6 capability install surfaces.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codex-home", default=None)
    parser.add_argument("--require-user-level-installed", action="store_true")
    parser.add_argument("--require-smoke-tested", action="store_true")
    parser.add_argument("--require-live-executed", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(
        Path(args.root),
        codex_home=Path(args.codex_home).resolve() if args.codex_home else None,
        require_user_level_installed=args.require_user_level_installed,
        require_smoke_tested=args.require_smoke_tested,
        require_live_executed=args.require_live_executed,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
