#!/usr/bin/env python3
"""Validate Reference 8 Codex adapter/fork install surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "reference8_capability_install"
RUNTIME = Path("tools/reference8_capability_install.py")
RUNTIME_PACKAGE = Path("tools/reference8_capability_install/runtime.py")
MANIFEST = Path("docs_bilingual/reference_manifests/reference8_capability_sources.json")
PLAN_EN = Path("docs_bilingual/implementation_plans/reference6_reference7_reference8_user_project_live_runtime_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/reference6_reference7_reference8_user_project_live_runtime_plan.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
GUARD = Path("tools/run_openspec_guard.py")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
TEST_NAME = "reference8_capability_install.test.py"
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
EXPECTED_LAYER_COUNTS = {"user_level": 8, "project_template_general": 5, "project_template_general_2": 3}
EXPECTED_CAPABILITY_COUNT = 16
EXPECTED_GENERAL = {"fireworks-tech-graph", "open-design-ref8", "remotion", "compound-engineering-plugin", "zvec"}
EXPECTED_GENERAL_DERIVED = {"understand-anything", "markitdown", "headroom"}
EXPECTED_GENERAL2 = {"cae-agent-hub", "ansys-mcp-server", "system-prompts-and-models-of-ai-tools"}
EXPECTED_GENERAL2_DERIVED = {"codex-visio-paper-figure-skill"}
DEDUPE = {"open-design-ref8": "reference6:open-design"}
PLAN_MARKERS = [
    "reference_files/8.md",
    "D:/PythonProject_General",
    "D:/PythonProject_General_2",
    "Browserbase",
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


def stable_hash(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def layer_counts(caps: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cap in caps:
        layer = str(cap.get("target_layer") or "unknown")
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def check_manifest(root: Path, errors: list[str]) -> dict[str, Any]:
    data = read_json(root / MANIFEST, errors)
    if not isinstance(data, dict):
        return {}
    policy = data.get("generated_policy")
    if not isinstance(policy, dict):
        errors.append("manifest_missing_generated_policy")
    else:
        if policy.get("priority_order") != PRIORITY_ORDER:
            errors.append("manifest_priority_order_mismatch")
        if policy.get("raw_upstream_install_counts_as_codex_live_executed") is not False:
            errors.append("manifest_raw_upstream_install_must_not_count")
        if policy.get("all_non_codex_upstreams_require_codex_fork_or_adapter") is not True:
            errors.append("manifest_must_require_codex_adapter_for_all_non_codex")
        if policy.get("expected_layer_counts") != EXPECTED_LAYER_COUNTS:
            errors.append("manifest_expected_layer_counts_mismatch")
        config = policy.get("codex_config_policy")
        if not isinstance(config, dict) or config.get("reuse_mode") != "env_key_name_only" or config.get("copy_secret_values") is not False:
            errors.append("manifest_codex_config_policy_invalid")
    caps = data.get("capabilities")
    if not isinstance(caps, list):
        errors.append("manifest_capabilities_not_list")
        return data
    if len(caps) != EXPECTED_CAPABILITY_COUNT:
        errors.append(f"manifest_capability_count_mismatch:{len(caps)}")
    observed_counts = layer_counts([item for item in caps if isinstance(item, dict)])
    if observed_counts != EXPECTED_LAYER_COUNTS:
        errors.append("manifest_layer_counts_mismatch:" + json.dumps(observed_counts, sort_keys=True))
    observed_ids: set[str] = set()
    for item in caps:
        if not isinstance(item, dict):
            errors.append("manifest_capability_not_object")
            continue
        cap_id = str(item.get("id"))
        observed_ids.add(cap_id)
        for field in ("id", "source_url", "target_layer", "codex_adapter_strategy"):
            if not item.get(field):
                errors.append(f"manifest_capability_missing_{field}:{cap_id}")
        live = item.get("live_runtime")
        if not isinstance(live, dict):
            errors.append(f"manifest_capability_missing_live_runtime:{cap_id}")
        else:
            if not live.get("live_runtime_target") or not live.get("live_smoke_kind"):
                errors.append(f"manifest_live_runtime_missing_target_or_kind:{cap_id}")
            if live.get("codex_adapter_required") is not True:
                errors.append(f"manifest_live_runtime_must_require_codex_adapter:{cap_id}")
            if live.get("raw_upstream_install_only_counts") is not False:
                errors.append(f"manifest_raw_upstream_install_must_not_count:{cap_id}")
            if live.get("source_reference_only_counts") is not False:
                errors.append(f"manifest_source_reference_must_not_count:{cap_id}")
            if cap_id in DEDUPE and live.get("dedupe_live_receipt_required") is not True:
                errors.append(f"manifest_dedupe_must_require_strict_receipt:{cap_id}")
        if item.get("requires_codex_adapter_before_live_executed") is not True:
            errors.append(f"manifest_capability_must_require_codex_adapter:{cap_id}")
        if item.get("raw_upstream_live_executed_allowed") is not False:
            errors.append(f"manifest_capability_raw_upstream_allowed:{cap_id}")
        if item.get("upstream_is_codex_native") is False and not item.get("codex_adapter_strategy"):
            errors.append(f"manifest_non_codex_missing_adapter_strategy:{cap_id}")
    if data.get("dedupe") != DEDUPE:
        errors.append("manifest_dedupe_mismatch")
    if set(DEDUPE) - observed_ids:
        errors.append("manifest_dedupe_capabilities_missing")
    if not EXPECTED_GENERAL.issubset(observed_ids) or not EXPECTED_GENERAL2.issubset(observed_ids):
        errors.append("manifest_missing_expected_template_capabilities")
    return data


def check_registry_guard_ci(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    tests: set[str] = set()
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        tests = {str(item) for item in manifest["python_unittest"]}
    if TEST_NAME not in tests:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")
    guard_text = read_text(root / GUARD, errors)
    if "check_reference8_capability_install" not in guard_text:
        errors.append("openspec_guard_missing:check_reference8_capability_install")
    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "reference8-capability-install":
                rule_found = True
                prompts = set(rule.get("prompt_reminders", [])) if isinstance(rule.get("prompt_reminders"), list) else set()
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if PLAN_EN.as_posix() not in prompts or PLAN_ZH.as_posix() not in prompts:
                    errors.append("safety_registry_missing_plan_reminders")
                for script in ("tools/check_reference8_capability_install.py", "tools/reference8_capability_install.py"):
                    if script not in scripts:
                        errors.append(f"safety_registry_missing_script:{script}")
                if "check_reference8_capability_install" not in steps:
                    errors.append("safety_registry_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:reference8-capability-install")
    return {"test_registered": TEST_NAME in tests, "guard_registered": "check_reference8_capability_install" in guard_text, "safety_rule_found": rule_found}


def check_runtime_plan(root: Path, errors: list[str]) -> dict[str, Any]:
    if not (root / RUNTIME).is_file():
        errors.append(f"missing_runtime:{RUNTIME.as_posix()}")
        return {}
    if not (root / RUNTIME_PACKAGE).is_file():
        errors.append(f"missing_runtime_package:{RUNTIME_PACKAGE.as_posix()}")
    code, payload, stderr = run_json([sys.executable, str(root / RUNTIME), "plan", "--json"], root)
    if code != 0 or not isinstance(payload, dict):
        errors.append("runtime_plan_failed:" + stderr.strip())
        return {}
    if not payload.get("ok"):
        errors.append("runtime_plan_not_ok")
    if payload.get("codex_config_toml_mutated") is not False:
        errors.append("runtime_plan_must_not_mutate_codex_config")
    if payload.get("capability_count") != EXPECTED_CAPABILITY_COUNT:
        errors.append("runtime_plan_capability_count_mismatch")
    if payload.get("layer_counts") != EXPECTED_LAYER_COUNTS:
        errors.append("runtime_plan_layer_counts_mismatch")
    env_policy = payload.get("codex_provider_env")
    if not isinstance(env_policy, dict) or env_policy.get("copy_secret_values") is not False or env_policy.get("reuse_mode") != "env_key_name_only":
        errors.append("runtime_plan_missing_env_key_only_policy")
    return payload


def check_user_level(
    root: Path,
    codex_home: Path | None,
    general_root: Path | None,
    general2_root: Path | None,
    require_installed: bool,
    require_smoke_tested: bool,
    require_live_executed: bool,
    errors: list[str],
) -> dict[str, Any] | None:
    if not (require_installed or require_smoke_tested or require_live_executed):
        return None
    cmd = [sys.executable, str(root / RUNTIME), "check", "--json"]
    if codex_home:
        cmd.extend(["--codex-home", str(codex_home)])
    if general_root:
        cmd.extend(["--general-root", str(general_root)])
    if general2_root:
        cmd.extend(["--general2-root", str(general2_root)])
    if require_installed:
        cmd.append("--require-installed")
    if require_smoke_tested:
        cmd.append("--require-smoke-tested")
    if require_live_executed:
        cmd.append("--require-live-executed")
    code, payload, stderr = run_json(cmd, root)
    if code != 0 or not isinstance(payload, dict) or not payload.get("ok"):
        summary = payload.get("errors") if isinstance(payload, dict) else stderr.strip()
        errors.append("user_level_reference8_check_failed:" + str(summary))
    return payload


def check_template_roots(general_root: Path | None, general2_root: Path | None, errors: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {"general": None, "general2": None}
    if general_root:
        required = [
            Path("tools/reference8_capability_install.py"),
            Path("tools/reference8_capability_install/runtime.py"),
            Path("tools/reference8_capability_install/manifest.json"),
            Path("tools/check_reference8_capability_install.py"),
            Path("docs_bilingual/implementation_plans/reference8_capability_template_sync_plan.md"),
            Path("docs_bilingual/implementation_plans/reference8_capability_template_sync_plan.zh-CN.md"),
            Path("template_assets/reference8-active/README.md"),
            Path("template_assets/reference8-derived/README.md"),
        ]
        for cap_id in EXPECTED_GENERAL:
            required.append(Path("template_assets/reference8-active/adapters") / f"{cap_id}.md")
        for cap_id in EXPECTED_GENERAL_DERIVED:
            required.append(Path("template_assets/reference8-derived/adapters") / f"{cap_id}.md")
        missing = [rel.as_posix() for rel in required if not (general_root / rel).exists()]
        gate = general_root / "tools/ci/local_gate.ps1"
        if gate.exists() and "check_reference8_capability_install.py" not in gate.read_text(encoding="utf-8-sig", errors="replace"):
            missing.append("local_gate_missing_reference8_checker")
        if missing:
            errors.extend(f"general_template_missing:{item}" for item in missing)
        summary["general"] = {"root_hash": stable_hash(str(general_root)), "missing": missing}
    if general2_root:
        required = [
            Path("tools/check_reference8_inert_sample.py"),
            Path("docs_bilingual/implementation_plans/reference8_capability_inert_template_plan.md"),
            Path("docs_bilingual/implementation_plans/reference8_capability_inert_template_plan.zh-CN.md"),
            Path("template_assets/inert-samples/reference8/README.md"),
            Path("template_assets/inert-samples/reference8/manifest.json"),
            Path("template_assets/inert-samples/reference8-derived/README.md"),
        ]
        for cap_id in EXPECTED_GENERAL2:
            required.append(Path("template_assets/inert-samples/reference8/adapters") / f"{cap_id}.md")
        for cap_id in EXPECTED_GENERAL2_DERIVED:
            required.append(Path("template_assets/inert-samples/reference8-derived/adapters") / f"{cap_id}.md")
        missing = [rel.as_posix() for rel in required if not (general2_root / rel).exists()]
        for rel in (Path("tools/reference8_capability_install.py"), Path("tools/reference8_capability_install")):
            if (general2_root / rel).exists():
                errors.append(f"general2_forbidden_active_reference8_surface:{rel.as_posix()}")
        gate = general2_root / "tools/ci/local_gate.ps1"
        if gate.exists() and "check_reference8_inert_sample.py" not in gate.read_text(encoding="utf-8-sig", errors="replace"):
            missing.append("local_gate_missing_reference8_inert_checker")
        if missing:
            errors.extend(f"general2_template_missing:{item}" for item in missing)
        summary["general2"] = {"root_hash": stable_hash(str(general2_root)), "missing": missing}
    return summary


def evaluate(
    root: Path,
    *,
    codex_home: Path | None,
    require_user_level_installed: bool,
    require_smoke_tested: bool,
    require_live_executed: bool,
    general_root: Path | None,
    general2_root: Path | None,
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
    user_level = check_user_level(root, codex_home, general_root, general2_root, require_user_level_installed, require_smoke_tested, require_live_executed, errors)
    templates = None
    if require_template_sync or general_root or general2_root:
        templates = check_template_roots(general_root, general2_root, errors)
        if require_template_sync and (not general_root or not general2_root):
            errors.append("template_sync_requires_general_and_general2_roots")
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "manifest": {"capability_count": len(manifest.get("capabilities", [])) if isinstance(manifest, dict) else 0},
        "registry_guard_ci": registry,
        "runtime_plan": runtime_plan,
        "user_level_check": user_level,
        "template_check": templates,
        "policy": {
            "priority_order": PRIORITY_ORDER,
            "codex_config_env_key_name_only": True,
            "copies_secret_values": False,
            "all_non_codex_upstreams_require_codex_fork_or_adapter": True,
            "raw_upstream_install_counts_as_codex_live_executed": False,
            "browserbase_disabled": True,
            "remote_publication_allowed": False,
        },
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "counts": {"errors": len(set(errors)), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Reference 8 Codex adapter/fork capability install surfaces.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--codex-home", default=None)
    parser.add_argument("--require-user-level-installed", action="store_true")
    parser.add_argument("--require-smoke-tested", action="store_true")
    parser.add_argument("--require-live-executed", action="store_true")
    parser.add_argument("--general-root", default=None)
    parser.add_argument("--general2-root", default=None)
    parser.add_argument("--require-template-sync", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(
        Path(args.root),
        codex_home=Path(args.codex_home).resolve() if args.codex_home else None,
        require_user_level_installed=args.require_user_level_installed,
        require_smoke_tested=args.require_smoke_tested,
        require_live_executed=args.require_live_executed,
        general_root=Path(args.general_root).resolve() if args.general_root else None,
        general2_root=Path(args.general2_root).resolve() if args.general2_root else None,
        require_template_sync=args.require_template_sync,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
