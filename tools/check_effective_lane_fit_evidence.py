#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "effective_lane_fit_evidence"
REGISTRY_RULE_ID = "effective-lane-fit-evidence"
GUARD_STEP = "check_effective_lane_fit_evidence"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "tools/check_effective_lane_fit_evidence.py",
        "effective lane choice is task-fit based",
        "worker-centric durable execution",
        "graph-shaped multi-phase execution",
        "one backend family at a time",
        "explicit close or handoff",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Effective lane-fit discipline",
        "tools/check_effective_lane_fit_evidence.py",
        "worker-centric `native_omx`",
        "graph-shaped LangGraph",
        "one backend family",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Effective lane-fit discipline",
        "tools/check_effective_lane_fit_evidence.py",
        "worker-centric `native_omx`",
        "graph-shaped LangGraph",
        "one backend family",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Effective lane choice is task-fit based",
        "worker-centric durable execution",
        "graph-shaped multi-phase execution",
        "one backend family at a time",
        "explicit close or handoff",
        "tools/check_effective_lane_fit_evidence.py",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "Effective lane choice 基于 task fit",
        "worker-centric durable execution",
        "graph-shaped multi-phase execution",
        "one backend family",
        "explicit close or handoff",
        "tools/check_effective_lane_fit_evidence.py",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Native Codex SHALL remain the base layer and durable lanes SHALL be task-fit choices",
        "tools/check_effective_lane_fit_evidence.py",
        "native_omx worker-centric fit",
        "LangGraph graph-shaped fit",
        "default-backend-not-enough",
        "explicit close/handoff",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "backend_default=langgraph is enough to select LangGraph for every task",
        "silently switch backend family",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "backend_default=langgraph is enough to select LangGraph for every task",
        "silently switch backend family",
    ],
}

NATIVE_OMX_MARKERS = (
    "native_omx",
    "native omx",
    "omx durable lane",
    "omx worker",
    "omx team",
)
LANGGRAPH_MARKERS = (
    "langgraph",
    "langgraph lane",
    "langgraph durable",
    "backend_default=langgraph",
)
LANE_DECISION_MARKERS = (
    "effective lane",
    "selected lane",
    "lane selected",
    "durable lane",
    "durable workflow selected",
    "durable_workflow=selected",
    "persistent_team=selected",
    "selected",
    "running",
    "采用",
    "选择",
)
WORKER_CENTRIC_MARKERS = (
    "worker-centric",
    "worker centric",
    "worker-centric durable execution",
    "worktree isolation",
    "mailbox flow",
    "direct worker lifecycle control",
    "worker lifecycle",
    "team-executor",
    "debugger workers",
    "2:team-executor",
    "3:team-executor",
    "2:debugger",
)
GRAPH_SHAPED_MARKERS = (
    "graph-shaped",
    "graph shaped",
    "graph-shaped multi-phase",
    "multi-phase execution",
    "checkpoint-driven",
    "checkpoint recovery",
    "checkpoint gates",
    "interrupt/resume approval gates",
    "approval gates",
    "frozen brief",
    "frozen briefs",
    "persisted survivor queue",
    "persisted survivor queues",
    "tracked langgraph thread",
    "stategraph",
)
DEFAULT_BACKEND_ONLY_MARKERS = (
    "backend_default=langgraph",
    "default backend is langgraph",
    "langgraph is the default backend",
    "backend_ready=true",
)
DEFAULT_BACKEND_NOT_ENOUGH_MARKERS = (
    "default backend is not enough",
    "backend readiness is not enough",
    "default-backend-not-enough",
    "backend_default is not enough",
)
HANDOFF_MARKERS = (
    "explicit close",
    "explicit handoff",
    "close/handoff",
    "handoff before switching",
    "closed native_omx",
    "closed langgraph",
    "backend-family handoff",
    "recorded handoff",
    "显式 close",
    "显式 handoff",
)
SILENT_SWITCH_PATTERNS = (
    re.compile(r"silent(?:ly)?\s+(?:switch|switching|changed?)\s+backend", re.IGNORECASE),
    re.compile(r"implicit(?:ly)?\s+(?:switch|switching|changed?)\s+backend", re.IGNORECASE),
    re.compile(r"switch(?:ed|ing)?\s+backend[^\n.]{0,80}(?:without|no)\s+(?:handoff|close)", re.IGNORECASE),
    re.compile(r"静默[^\n。]{0,40}(?:切换|更换)[^\n。]{0,20}backend", re.IGNORECASE),
)


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def matches_any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required effective lane-fit policy surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden lane-fit wording: {snippet}")

    guard_text = read_text(root / "tools/run_openspec_guard.py") or ""
    if GUARD_STEP not in guard_text:
        errors.append(f"tools/run_openspec_guard.py must run {GUARD_STEP}")

    registry_text = read_text(root / "tools/safety_rule_script_backing_registry.json")
    if registry_text is None:
        errors.append("Missing safety rule registry")
    else:
        try:
            registry = json.loads(registry_text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid safety rule registry JSON: {exc}")
        else:
            rules = registry.get("rules", []) if isinstance(registry, dict) else []
            matching = [rule for rule in rules if isinstance(rule, dict) and rule.get("id") == REGISTRY_RULE_ID]
            if not matching:
                errors.append(f"Safety rule registry missing rule id: {REGISTRY_RULE_ID}")
            else:
                rule = matching[0]
                for field, expected in {
                    "prompt_reminders": "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md",
                    "script_controls": "tools/check_effective_lane_fit_evidence.py",
                    "guard_steps": GUARD_STEP,
                }.items():
                    values = rule.get(field, [])
                    if expected not in values:
                        errors.append(f"Safety rule {REGISTRY_RULE_ID} missing {field} entry: {expected}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "repository",
        "ok": not errors,
        "root": str(root),
        "checked": checked,
        "errors": errors,
        "warnings": warnings,
        "counts": {"checked_files": len(checked), "errors": len(errors), "warnings": len(warnings)},
    }


def run_evidence_check(evidence_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    detected: list[str] = []

    text = read_text(evidence_path)
    if text is None:
        errors.append(f"Missing or unreadable effective lane-fit evidence file: {evidence_path}")
        text = ""

    has_native = contains_any(text, NATIVE_OMX_MARKERS)
    has_langgraph = contains_any(text, LANGGRAPH_MARKERS)
    has_lane_decision = contains_any(text, LANE_DECISION_MARKERS)
    has_worker_fit = contains_any(text, WORKER_CENTRIC_MARKERS)
    has_graph_fit = contains_any(text, GRAPH_SHAPED_MARKERS)
    has_default_only = contains_any(text, DEFAULT_BACKEND_ONLY_MARKERS)
    has_default_not_enough = contains_any(text, DEFAULT_BACKEND_NOT_ENOUGH_MARKERS)
    has_handoff = contains_any(text, HANDOFF_MARKERS)

    if has_native and has_lane_decision:
        detected.append("native_omx_lane")
        if not has_worker_fit:
            errors.append(
                "`native_omx` effective lane evidence must cite worker-centric durable execution, "
                "worktree isolation, mailbox flow, or direct worker lifecycle control."
            )

    if has_langgraph and has_lane_decision:
        detected.append("langgraph_lane")
        if not has_graph_fit:
            errors.append(
                "LangGraph effective lane evidence must cite graph-shaped multi-phase execution, checkpoint-driven "
                "recovery, interrupt/resume approval gates, frozen briefs, or persisted survivor queues."
            )

    if has_langgraph and has_lane_decision and has_default_only:
        detected.append("default_backend_not_enough")
        if not (has_graph_fit or has_default_not_enough):
            errors.append(
                "`backend_default=langgraph` or `backend_ready=true` is readiness evidence only; "
                "it is not enough to justify task-level LangGraph lane adoption without graph-shaped task fit."
            )

    if has_native and has_langgraph:
        detected.append("backend_family_consistency")
        if not has_handoff:
            errors.append(
                "Evidence that mentions both `native_omx` and LangGraph in one durable task must record one active "
                "backend family or an explicit close/handoff before switching."
            )

    if matches_any(text, SILENT_SWITCH_PATTERNS):
        detected.append("silent_switch")
        errors.append("Backend-family switching must be explicit and recorded as close/handoff, not silent or implicit.")

    if not detected and not errors:
        warnings.append("No native_omx, LangGraph, lane-decision, or backend-family switching markers were detected.")
    elif not errors:
        info.append("Effective lane-fit evidence is acceptable.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "evidence",
        "ok": not errors,
        "evidence_path": str(evidence_path),
        "detected": detected,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {"detected": len(detected), "errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate effective durable lane-fit and backend-family switching evidence."
    )
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved trace, run summary, or lane-fit evidence file to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_evidence_check(Path(args.evidence)) if args.evidence else run_repository_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload.get("info", []):
            print(message)
        for message in payload.get("warnings", []):
            print(f"WARNING: {message}")
        for message in payload.get("errors", []):
            print(f"ERROR: {message}")
        if payload["ok"] and payload["mode"] == "repository":
            print("Effective lane-fit repository policy is backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
