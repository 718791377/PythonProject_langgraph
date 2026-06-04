#!/usr/bin/env python3
"""Validate the split Browser/CLI adapter governance boundary.

This checker replaces the old mixed MCP/skills/browser/CLI baseline for the
Browser/CLI adapter lane.  The canonical adapter set is intentionally narrow:
``chrome-devtools-mcp``, ``cdp-bridge-mcp`` / ``CDP Bridge``, and ``OpenCLI``.
CLI-Anything, WXWork_CLI, WXWork.exe, and Codex harnesses are sibling lanes and
must not appear as adapter-lane entries.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "user_level_browser_cli_adapter_boundary"
PLAN_EN = Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md")
PARENT_EN = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md")
PARENT_ZH = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md")
SPEC_EN = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md")
SPEC_ZH = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")

CANONICAL_ADAPTERS = {
    "chrome-devtools-mcp": "https://github.com/ChromeDevTools/chrome-devtools-mcp",
    "cdp-bridge-mcp": "https://github.com/Unagi-cq/cdp-bridge-mcp",
    "CDP Bridge": "https://github.com/Unagi-cq/cdp-bridge-mcp",
    "OpenCLI": "https://github.com/jackwener/OpenCLI",
}
FORBIDDEN_LANE_TERMS = ("CLI-Anything", "WXWork_CLI", "WXWork.exe", "wecom-cli", "harness")
REQUIRED_PLAN_MARKERS = (
    "Status: implemented-local",
    "chrome-devtools-mcp",
    "cdp-bridge-mcp",
    "CDP Bridge",
    "OpenCLI",
    "https://github.com/ChromeDevTools/chrome-devtools-mcp",
    "https://github.com/Unagi-cq/cdp-bridge-mcp",
    "https://github.com/jackwener/OpenCLI",
    "authorization receipt",
    "owner lease",
    "codex-port",
    "--port auto",
    "not adapters",
)
REQUIRED_SPEC_MARKERS = (
    "Browser/CLI adapter",
    "chrome-devtools-mcp",
    "CDP Bridge",
    "OpenCLI",
    "adapter lane",
    "CLI-Anything/WXWork_CLI",
    "not Browser/CLI adapters",
)
REQUIRED_TESTS = {
    "check_user_level_browser_cli_adapter_boundary.test.py",
    "cdp_bridge_governance.test.py",
    "chrome_devtools_mcp_managed.test.py",
    "codex_port.test.py",
    "browser_owner_registry.test.py",
}


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


def table_rows(section: str) -> list[str]:
    return [line.strip() for line in section.splitlines() if line.strip().startswith("|")]


def check_plan_pair(root: Path, errors: list[str], info: list[str]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_PLAN_MARKERS, errors)
        status = extract_anchor_block(text, "CURRENT_STATUS") or extract_section(text, "Current Status")
        if "implemented-local" not in status:
            errors.append(f"{rel.as_posix()}:current_status_not_implemented_local")
        if "remote publication" not in status.lower() and "remote-publication" not in status.lower():
            errors.append(f"{rel.as_posix()}:remote_publication_boundary_missing")

        section = extract_section(text, "Adapter lane status")
        rows = table_rows(section)
        canonical_hits = {
            name: any(name.lower() in row.lower() for row in rows)
            for name in ("chrome-devtools-mcp", "CDP Bridge", "OpenCLI")
        }
        missing = [name for name, present in canonical_hits.items() if not present]
        if missing:
            errors.append(f"{rel.as_posix()}:adapter_lane_table_missing:{','.join(missing)}")
        for forbidden in FORBIDDEN_LANE_TERMS:
            if any(forbidden.lower() in row.lower() for row in rows):
                errors.append(f"{rel.as_posix()}:forbidden_adapter_lane_term:{forbidden}")
        payload[rel.as_posix()] = {
            "rows": len(rows),
            "canonical_hits": canonical_hits,
            "forbidden_terms": [
                term for term in FORBIDDEN_LANE_TERMS if any(term.lower() in row.lower() for row in rows)
            ],
        }
        info.append(f"{rel.as_posix()}: canonical adapter rows {canonical_hits}")
    return payload


def check_parent_plan(root: Path, errors: list[str]) -> None:
    for rel in (PARENT_EN, PARENT_ZH):
        text = read_text(root / rel, errors)
        require_markers(
            rel.as_posix(),
            text,
            (
                "user_level_browser_cli_adapter_boundary_plan",
                "user_level_cli_anything_wxwork_cli_governance_plan",
                "codex_harnesses_governance_plan",
                "Stage B",
                "delete",
            ),
            errors,
        )


def check_spec(root: Path, errors: list[str]) -> dict[str, Any]:
    accepted: list[str] = []
    for rel in (SPEC_EN, SPEC_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_SPEC_MARKERS, errors)
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
        errors.append("ci_manifest_still_registers_deleted_wecom_cli_test")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    if "check_user_level_browser_cli_adapter_boundary" not in guard_text:
        errors.append("openspec_guard_missing:check_user_level_browser_cli_adapter_boundary")
    if "check_user_level_mcp_skills_browser_cli_baseline" in guard_text:
        errors.append("openspec_guard_still_runs_old_mixed_browser_cli_baseline")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "user-level-browser-cli-adapter-boundary":
                rule_found = True
                prompts = set(rule.get("prompt_reminders", [])) if isinstance(rule.get("prompt_reminders"), list) else set()
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if PLAN_EN.as_posix() not in prompts or PLAN_ZH.as_posix() not in prompts:
                    errors.append("safety_registry_adapter_rule_missing_plan_reminders")
                if "tools/check_user_level_browser_cli_adapter_boundary.py" not in scripts:
                    errors.append("safety_registry_adapter_rule_missing_script")
                if "check_user_level_browser_cli_adapter_boundary" not in steps:
                    errors.append("safety_registry_adapter_rule_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:user-level-browser-cli-adapter-boundary")
    return {"missing_tests": missing_tests, "rule_found": rule_found}


def check_deleted_old_plans(root: Path, errors: list[str]) -> dict[str, bool]:
    old_paths = {
        "old_mixed_en": Path("docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md"),
        "old_mixed_zh": Path("docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md"),
        "old_discovery_en": Path("docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.md"),
        "old_discovery_zh": Path("docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.zh-CN.md"),
    }
    presence = {key: (root / rel).exists() for key, rel in old_paths.items()}
    for key, present in presence.items():
        if present:
            errors.append(f"old_plan_still_present:{key}:{old_paths[key].as_posix()}")
    registry_text = read_text(root / Path("docs_bilingual/docs_registry.yaml"), errors)
    for rel in old_paths.values():
        if rel.as_posix() in registry_text:
            errors.append(f"docs_registry_still_references_old_plan:{rel.as_posix()}")
    return presence


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    plans = check_plan_pair(root, errors, info)
    check_parent_plan(root, errors)
    spec = check_spec(root, errors)
    registry = check_registry_guard_ci(root, errors)
    old_plan_presence = check_deleted_old_plans(root, errors)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "canonical_adapters": CANONICAL_ADAPTERS,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "plans": plans,
        "spec": spec,
        "registry_guard_ci": registry,
        "old_plan_presence": old_plan_presence,
        "counts": {"errors": len(errors), "warnings": len(warnings), "info": len(info)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate split Browser/CLI adapter governance.")
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
