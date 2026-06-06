#!/usr/bin/env python3
"""Validate the split CLI-Anything / WXWork_CLI governance lane."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_cli_anything_wxwork_cli_governance"
PLAN_EN = Path("docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.zh-CN.md")
SPEC_EN = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md")
SPEC_ZH = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
CLI_HELPER = Path("tools/cli_anything_governance.py")
WXWORK_HELPER = Path("tools/wxwork_cli_governance.py")
OLD_WECOM_HELPER = Path("tools/wecom_cli_governance.py")

REQUIRED_PLAN_MARKERS = (
    "Status: implemented-local",
    "https://github.com/HKUDS/CLI-Anything",
    "WXWork_CLI",
    "WXWork.exe",
    "not Codex harnesses",
    "adapter-plan",
    "adapter-generation",
    "global lease",
    "operator authorization",
    "timeout release",
    "rollback pointer",
    "no message-content",
    "Runtime Promotion Ladder",
    "R0 project-level preflight",
    "R1 project-level fake/dry-run runtime",
    "R2 reusable project-level helper/guard",
    "R3 user-level install/update receipt",
    "R4 user-level smoke runtime",
    "R5 active-candidate / bounded live handoff",
    "not installed/started/enabled in this package",
    "installed-user-level",
    "smoke-tested",
    "active-candidate",
    "send action allowed only at R5",
    "target/action allowlist",
    "message redaction",
    "ephemeral message handling",
)
REQUIRED_HELPER_MARKERS = (
    "adapter-plan",
    "adapter_generation_only",
    "adapter_generation_boundary_only",
    "WXWork_CLI",
    "https://github.com/HKUDS/CLI-Anything",
)
REQUIRED_WXWORK_MARKERS = (
    "TOOL_NAME = \"WXWork_CLI\"",
    "OWNER_LANE = \"wxwork_cli\"",
    "TARGET_PROCESS = \"WXWork.exe\"",
    "global-wxwork-gui",
    "operator_authorization_receipt_required",
    "global_wxwork_lease_required",
    "smoke-record",
    "smoke-check",
    "SMOKE_FORBIDDEN_MARKERS",
)
REQUIRED_SPEC_MARKERS = (
    "CLI-Anything/WXWork_CLI",
    "adapter-generation",
    "adapter-plan",
    "WXWork_CLI governance guard",
    "tools/wxwork_cli_governance.py",
    "Runtime promotion ladder",
    "R0 project-level preflight",
    "R1 project-level fake/dry-run runtime",
    "R2 reusable project-level helper/guard",
    "R3 user-level install/update receipt",
    "R4 user-level smoke runtime",
    "R5 active-candidate / bounded live handoff",
    "installed-user-level",
    "smoke-tested",
    "active-candidate",
    "not installed/started/enabled in this package",
    "send action allowed only at R5",
)
REQUIRED_TESTS = {
    "cli_anything_governance.test.py",
    "wxwork_cli_governance.test.py",
    "check_user_level_cli_anything_wxwork_cli_governance.test.py",
}
RUNTIME_STAGE_MARKERS = (
    "R0 project-level preflight",
    "R1 project-level fake/dry-run runtime",
    "R2 reusable project-level helper/guard",
    "R3 user-level install/update receipt",
    "R4 user-level smoke runtime",
    "R5 active-candidate / bounded live handoff",
)
RUNTIME_STATUS_MARKERS = ("installed-user-level", "smoke-tested", "active-candidate")


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


def extract_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    section = text.split(marker, 1)[1]
    if "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def extract_anchor_block(text: str, anchor: str) -> str:
    start = f"<!-- {anchor}_START -->"
    end = f"<!-- {anchor}_END -->"
    if start not in text or end not in text:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0]


def check_plan_pair(root: Path, errors: list[str], info: list[str]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_PLAN_MARKERS, errors)
        status = extract_anchor_block(text, "CURRENT_STATUS") or extract_section(text, "Current Status")
        backlog = extract_anchor_block(text, "TASK_BACKLOG") or extract_section(text, "Task Backlog")
        evidence = extract_anchor_block(text, "EVIDENCE_INDEX") or extract_section(text, "Evidence Index")
        if "implemented-local" not in status:
            errors.append(f"{rel.as_posix()}:current_status_not_implemented_local")
        if "- [ ]" in backlog:
            errors.append(f"{rel.as_posix()}:unchecked_task_backlog_items")
        if "2026-06-04 Stage B" not in evidence:
            errors.append(f"{rel.as_posix()}:missing_stage_b_evidence_index")
        if "2026-06-06 Stage D R4 local smoke tooling evidence" not in evidence:
            errors.append(f"{rel.as_posix()}:missing_stage_d_r4_smoke_evidence_index")
        if "wecom-cli" in status.lower() or "wecom-cli" in backlog.lower():
            errors.append(f"{rel.as_posix()}:active_status_or_backlog_uses_legacy_wecom_cli")
        details[rel.as_posix()] = {
            "implemented_local": "implemented-local" in status,
            "has_stage_b_evidence": "2026-06-04 Stage B" in evidence,
            "has_stage_d_r4_smoke_evidence": "2026-06-06 Stage D R4 local smoke tooling evidence" in evidence,
            "runtime_stage_markers": {
                marker: marker.lower() in text.lower()
                for marker in RUNTIME_STAGE_MARKERS
            },
            "runtime_status_markers": {
                marker: marker.lower() in text.lower()
                for marker in RUNTIME_STATUS_MARKERS
            },
            "send_allowed_only_r5": "send action allowed only at r5" in text.lower(),
            "not_installed_started_enabled": "not installed/started/enabled in this package" in text.lower(),
        }
        info.append(f"{rel.as_posix()}: CLI-Anything/WXWork_CLI plan checked")
    return details


def check_helpers(root: Path, errors: list[str]) -> dict[str, bool]:
    cli_text = read_text(root / CLI_HELPER, errors)
    wx_text = read_text(root / WXWORK_HELPER, errors)
    require_markers(CLI_HELPER.as_posix(), cli_text, REQUIRED_HELPER_MARKERS, errors)
    require_markers(WXWORK_HELPER.as_posix(), wx_text, REQUIRED_WXWORK_MARKERS, errors)
    if "harness-plan" in cli_text or "harness_generation" in cli_text:
        errors.append("cli_anything_helper_still_uses_harness_generation_wording")
    if (root / OLD_WECOM_HELPER).exists():
        errors.append("legacy_wecom_cli_helper_still_present")
    r4_smoke_record_present = "smoke-record" in wx_text and "command_smoke_record" in wx_text
    r4_smoke_check_present = "smoke-check" in wx_text and "command_smoke_check" in wx_text
    r4_smoke_forbidden_markers_present = all(
        marker in wx_text
        for marker in (
            "SMOKE_FORBIDDEN_MARKERS",
            "gui_control_performed",
            "sends_messages",
            "message_body_included",
            "external_message_sent",
        )
    )
    if not r4_smoke_record_present:
        errors.append("wxwork_helper_missing_r4_smoke_record")
    if not r4_smoke_check_present:
        errors.append("wxwork_helper_missing_r4_smoke_check")
    if not r4_smoke_forbidden_markers_present:
        errors.append("wxwork_helper_missing_r4_smoke_forbidden_markers")
    return {
        "cli_anything_helper_present": (root / CLI_HELPER).exists(),
        "wxwork_helper_present": (root / WXWORK_HELPER).exists(),
        "legacy_wecom_helper_present": (root / OLD_WECOM_HELPER).exists(),
        "r4_smoke_record_present": r4_smoke_record_present,
        "r4_smoke_check_present": r4_smoke_check_present,
        "r4_smoke_forbidden_markers_present": r4_smoke_forbidden_markers_present,
    }


def check_spec(root: Path, errors: list[str]) -> dict[str, Any]:
    accepted: list[str] = []
    for rel in (SPEC_EN, SPEC_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_SPEC_MARKERS, errors)
        if "tools/wecom_cli_governance.py" in text:
            errors.append(f"{rel.as_posix()}:stable_spec_still_points_to_legacy_wecom_helper")
        if "harness-plan" in text or "harness_generation_allowed" in text:
            errors.append(f"{rel.as_posix()}:stable_spec_still_uses_cli_anything_harness_plan")
        if all(marker.lower() in text.lower() for marker in REQUIRED_SPEC_MARKERS):
            accepted.append(rel.as_posix())
    return {"accepted": accepted}


def check_registry_guard_ci(root: Path, errors: list[str]) -> dict[str, Any]:
    manifest = read_json(root / CI_MANIFEST, errors)
    tests: set[str] = set()
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        tests = {str(item) for item in manifest["python_unittest"]}
    missing_tests = sorted(REQUIRED_TESTS - tests)
    if missing_tests:
        errors.append(f"ci_manifest_missing:{','.join(missing_tests)}")
    if "wecom_cli_governance.test.py" in tests:
        errors.append("ci_manifest_still_registers_legacy_wecom_cli_test")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    if "check_user_level_cli_anything_wxwork_cli_governance" not in guard_text:
        errors.append("openspec_guard_missing:check_user_level_cli_anything_wxwork_cli_governance")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "user-level-cli-anything-wxwork-cli-governance":
                rule_found = True
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if "tools/check_user_level_cli_anything_wxwork_cli_governance.py" not in scripts:
                    errors.append("safety_registry_cli_anything_wxwork_rule_missing_script")
                if "check_user_level_cli_anything_wxwork_cli_governance" not in steps:
                    errors.append("safety_registry_cli_anything_wxwork_rule_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:user-level-cli-anything-wxwork-cli-governance")
    return {"missing_tests": missing_tests, "rule_found": rule_found}


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    plans = check_plan_pair(root, errors, info)
    helpers = check_helpers(root, errors)
    spec = check_spec(root, errors)
    registry = check_registry_guard_ci(root, errors)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "plans": plans,
        "helpers": helpers,
        "spec": spec,
        "registry_guard_ci": registry,
        "counts": {"errors": len(errors), "warnings": len(warnings), "info": len(info)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CLI-Anything/WXWork_CLI split governance.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
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
