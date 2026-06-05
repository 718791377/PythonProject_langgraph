#!/usr/bin/env python3
"""Validate Codex harnesses governance split from adapter lanes."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "codex_harnesses_governance"
PLAN_EN = Path("docs_bilingual/implementation_plans/codex_harnesses_governance_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/codex_harnesses_governance_plan.zh-CN.md")
PARENT_EN = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md")
PARENT_ZH = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md")
SPEC_EN = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md")
SPEC_ZH = Path("openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.zh-CN.md")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")

SOURCE_URLS = (
    "https://blog.can.ac/2026/02/12/the-harness-problem",
    "https://github.com/can1357/oh-my-pi",
    "https://pi.dev/",
    "https://pi.dev/packages",
)
REQUIRED_PLAN_MARKERS = (
    "Status: implemented-local",
    "source ledger",
    "source pin",
    "retrieved_at",
    "license note",
    "rollback pointer",
    "no Codex takeover",
    "unpinned Pi packages",
    "read guard",
    "write guard",
    "job state",
    "isolated worktree",
    "changed-path report",
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
    "fake Pi job",
    "active sidecar",
)
REQUIRED_SPEC_MARKERS = (
    "Codex harnesses governance",
    "The Harness Problem",
    "oh-my-pi",
    "pi.dev/packages",
    "no Codex takeover",
    "unpinned Pi packages",
    "read guard",
    "write guard",
    "job state",
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
)
FORBIDDEN_PLAN_LANE_TERMS = ("chrome-devtools-mcp", "cdp-bridge-mcp", "OpenCLI", "CLI-Anything", "WXWork_CLI")
REQUIRED_TESTS = {"check_codex_harnesses_governance.test.py"}
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


def table_rows(section: str) -> list[str]:
    return [line.strip() for line in section.splitlines() if line.strip().startswith("|")]


def check_plan_pair(root: Path, errors: list[str], info: list[str]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_PLAN_MARKERS, errors)
        for url in SOURCE_URLS:
            if url not in text:
                errors.append(f"{rel.as_posix()}:missing_source_url:{url}")
        status = extract_anchor_block(text, "CURRENT_STATUS") or extract_section(text, "Current Status")
        backlog = extract_anchor_block(text, "TASK_BACKLOG") or extract_section(text, "Task Backlog")
        evidence = extract_anchor_block(text, "EVIDENCE_INDEX") or extract_section(text, "Evidence Index")
        if "implemented-local" not in status:
            errors.append(f"{rel.as_posix()}:current_status_not_implemented_local")
        if "- [ ]" in backlog:
            errors.append(f"{rel.as_posix()}:unchecked_task_backlog_items")
        if "2026-06-04 Stage B" not in evidence:
            errors.append(f"{rel.as_posix()}:missing_stage_b_evidence_index")
        ledger = extract_section(text, "Source Ledger")
        rows = table_rows(ledger)
        for url in SOURCE_URLS:
            matching = [row for row in rows if url in row]
            if not matching:
                errors.append(f"{rel.as_posix()}:source_ledger_missing:{url}")
                continue
            row = matching[0].lower()
            for marker in ("source pin", "retrieved_at", "license note", "rollback pointer"):
                if marker not in row:
                    errors.append(f"{rel.as_posix()}:source_ledger_row_missing:{url}:{marker}")
        details[rel.as_posix()] = {
            "source_rows": len(rows),
            "runtime_stage_markers": {
                marker: marker.lower() in text.lower()
                for marker in RUNTIME_STAGE_MARKERS
            },
            "runtime_status_markers": {
                marker: marker.lower() in text.lower()
                for marker in RUNTIME_STATUS_MARKERS
            },
            "not_installed_started_enabled": "not installed/started/enabled in this package" in text.lower(),
            "active_sidecar_guard": "active sidecar" in text.lower()
            and "no codex takeover" in text.lower(),
        }
        info.append(f"{rel.as_posix()}: Codex harness source ledger rows={len(rows)}")
    return details


def check_no_harness_takeover_in_sibling_plans(root: Path, errors: list[str]) -> dict[str, list[str]]:
    sibling_paths = [
        Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md"),
        Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md"),
        Path("docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.md"),
        Path("docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.zh-CN.md"),
    ]
    hits: dict[str, list[str]] = {}
    for rel in sibling_paths:
        text = read_text(root / rel, errors)
        lowered = text.lower()
        terms = [term for term in ("codex harnesses", "harnesses") if term in lowered]
        # Sibling plans may say they are not harnesses, but must not own the
        # harness source ledger or job/read/write guard contract.
        forbidden_contract = [
            marker
            for marker in ("source ledger", "unpinned pi packages", "harness job state", "harness write guard")
            if marker in lowered
        ]
        if forbidden_contract:
            errors.append(f"{rel.as_posix()}:sibling_plan_owns_harness_contract:{','.join(forbidden_contract)}")
        hits[rel.as_posix()] = terms
    return hits


def check_spec(root: Path, errors: list[str]) -> dict[str, Any]:
    accepted: list[str] = []
    for rel in (SPEC_EN, SPEC_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_SPEC_MARKERS, errors)
        for url in SOURCE_URLS:
            if url not in text:
                errors.append(f"{rel.as_posix()}:missing_harness_source_url:{url}")
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

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    if "check_codex_harnesses_governance" not in guard_text:
        errors.append("openspec_guard_missing:check_codex_harnesses_governance")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    rule_found = False
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "codex-harnesses-governance":
                rule_found = True
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                if "tools/check_codex_harnesses_governance.py" not in scripts:
                    errors.append("safety_registry_harness_rule_missing_script")
                if "check_codex_harnesses_governance" not in steps:
                    errors.append("safety_registry_harness_rule_missing_guard_step")
    if not rule_found:
        errors.append("safety_registry_missing:codex-harnesses-governance")
    return {"missing_tests": missing_tests, "rule_found": rule_found}


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    plans = check_plan_pair(root, errors, info)
    siblings = check_no_harness_takeover_in_sibling_plans(root, errors)
    spec = check_spec(root, errors)
    registry = check_registry_guard_ci(root, errors)
    for rel in (PARENT_EN, PARENT_ZH):
        text = read_text(root / rel, errors)
        require_markers(
            rel.as_posix(),
            text,
            ("codex_harnesses_governance_plan", "The Harness Problem", "oh-my-pi", "pi.dev/packages"),
            errors,
        )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "source_urls": list(SOURCE_URLS),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "plans": plans,
        "sibling_mentions": siblings,
        "spec": spec,
        "registry_guard_ci": registry,
        "counts": {"errors": len(errors), "warnings": len(warnings), "info": len(info)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Codex harnesses governance split.")
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
