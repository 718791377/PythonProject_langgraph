#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "durable_artifact_state_surfaces"
REGISTRY_RULE_ID = "durable-artifact-state-surfaces"
GUARD_STEP = "check_durable_artifact_state_surfaces"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "Read-only exploration must stay specific, well-scoped, and read-only",
        "bounded code-changing worker task",
        "tools/check_durable_artifact_state_surfaces.py",
        ".omx/state/langgraph/",
        ".omx/state/selectors/active.json",
        "durable artifacts",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Durable artifact/state-surface discipline",
        "tools/check_durable_artifact_state_surfaces.py",
        ".omx/state/langgraph/",
        "frozen implementation brief",
        "survivor queue",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Durable artifact/state-surface discipline",
        "tools/check_durable_artifact_state_surfaces.py",
        ".omx/state/langgraph/",
        "frozen implementation brief",
        "survivor queue",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Read-only exploration is for specific codebase questions",
        "must not replace a bounded code-changing worker task",
        "LangGraph entrypoints and repo-local `.omx/state/langgraph/` state",
        "`.omx/state/selectors/active.json` remains the active selector authority",
        "Durable artifacts, frozen briefs, and survivor queues",
        "tools/check_durable_artifact_state_surfaces.py",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "read-only exploration 只用于 specific codebase questions",
        "不得替代 bounded code-changing worker task",
        "LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` state",
        "active selector authority",
        "durable artifacts、frozen briefs 与 survivor queues",
        "tools/check_durable_artifact_state_surfaces.py",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Exploration, code-change delegation, and durable artifact persistence SHALL stay script-checkable",
        "tools/check_durable_artifact_state_surfaces.py",
        "`.omx/state/langgraph/` state",
        "`.omx/state/selectors/active.json`",
        "documented artifact paths",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "read-only exploration may replace implementation workers",
        "durable artifacts may remain only in chat context",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "read-only exploration may replace implementation workers",
        "durable artifacts may remain only in chat context",
    ],
}

EXPLORATION_MARKERS = (
    "explorer",
    "read-only exploration",
    "codebase search",
    "file discovery",
    "symbol mapping",
    "只读探索",
)
SPECIFIC_MARKERS = ("specific", "well-scoped", "明确", "具体")
READ_ONLY_MARKERS = ("read-only", "read only", "只读")
CODE_CHANGE_MARKERS = (
    "bounded code-changing worker task",
    "implementation patch is clear",
    "clear implementation patch",
    "code-changing worker",
    "code change",
    "bounded patch",
    "实现补丁",
)
WORKER_MARKERS = ("code-changing worker", "implementation worker", "patch worker", "worker task", "执行 worker")

GRAPH_MARKERS = (
    "graph phases",
    "checkpoint gates",
    "tracked langgraph thread",
    "langgraph checkpoint",
    "checkpoint-driven",
    "graph-shaped",
)
LANGGRAPH_ENTRYPOINT_MARKERS = (
    "langgraph entrypoint",
    "langgraph entrypoints",
    "omx-langgraph-cli",
    "langgraph cli",
    "langgraph lane",
)
LANGGRAPH_STATE_MARKERS = (".omx/state/langgraph/", ".omx\\state\\langgraph\\")
SELECTOR_MARKERS = (".omx/state/selectors/active.json", ".omx\\state\\selectors\\active.json")
COMPATIBILITY_MARKERS = ("compatibility record", "compatibility records", ".omx/state/team/", ".omx\\state\\team\\")
DURABLE_ADOPTION_MARKERS = ("durable-team adoption", "automatic durable-team routing", "durable team adoption")

DURABLE_ARTIFACT_MARKERS = (
    "durable artifact",
    "durable artifacts",
    "frozen implementation brief",
    "frozen brief",
    "survivor queue",
    "survivor queues",
    "persisted survivor",
)
REPO_LOCAL_PATH_PATTERN = re.compile(
    r"(?:\.omx[\\/]state[\\/](?:langgraph|team|selectors)[\\/]|docs_bilingual[\\/]|openspec[\\/]|artifacts[\\/]|evidence[\\/])",
    re.IGNORECASE,
)
TRANSIENT_ONLY_PATTERNS = (
    re.compile(r"only\s+(?:in\s+)?(?:transient\s+)?chat context", re.IGNORECASE),
    re.compile(r"transient chat context only", re.IGNORECASE),
    re.compile(r"只存在于\s*transient chat context", re.IGNORECASE),
)

RESEARCH_MARKERS = ("open-ended research", "research fan-in", "开放式 research", "研究 fan-in")
IMPLEMENTATION_MARKERS = ("implementation starts", "implementation phase", "开始 implementation", "执行阶段")
BRIEF_FIELDS = ("scope", "non-goals", "acceptance evidence", "ownership boundaries", "unresolved risks")
BUG_TRIAD_MARKERS = ("bug-finder", "bug-rebutter", "bug-judge")
BUG_TRIAD_REQUIRED = ("burst", "read-only", "leader-side", "survivor queue", "debugger-lane")


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


def has_repo_local_path(text: str) -> bool:
    return bool(REPO_LOCAL_PATH_PATTERN.search(text))


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required durable artifact/state-surface policy surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden durable artifact/state-surface wording: {snippet}")

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
                    "script_controls": "tools/check_durable_artifact_state_surfaces.py",
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
        errors.append(f"Missing or unreadable durable artifact/state-surface evidence file: {evidence_path}")
        text = ""

    has_exploration = contains_any(text, EXPLORATION_MARKERS)
    has_code_change = contains_any(text, CODE_CHANGE_MARKERS)
    has_worker = contains_any(text, WORKER_MARKERS)
    has_graph = contains_any(text, GRAPH_MARKERS)
    has_durable_artifact = contains_any(text, DURABLE_ARTIFACT_MARKERS)
    has_research_to_implementation = contains_any(text, RESEARCH_MARKERS) and contains_any(
        text, IMPLEMENTATION_MARKERS
    )
    has_bug_triad = contains_any(text, BUG_TRIAD_MARKERS)
    has_durable_adoption = contains_any(text, DURABLE_ADOPTION_MARKERS)
    has_compatibility = contains_any(text, COMPATIBILITY_MARKERS)

    if has_exploration:
        detected.append("exploration")
        if not contains_any(text, SPECIFIC_MARKERS):
            errors.append("Exploration evidence must describe a specific or well-scoped codebase question.")
        if not contains_any(text, READ_ONLY_MARKERS):
            errors.append("Exploration evidence must state that exploration is read-only.")
        if has_code_change and not has_worker:
            errors.append(
                "Read-only exploration must not replace a bounded code-changing worker task when the implementation patch is clear."
            )

    if has_graph:
        detected.append("langgraph_state")
        if not contains_any(text, LANGGRAPH_ENTRYPOINT_MARKERS):
            errors.append("Graph/checkpoint evidence must name LangGraph entrypoints or an equivalent LangGraph CLI/lane.")
        if not contains_any(text, LANGGRAPH_STATE_MARKERS):
            errors.append("Graph/checkpoint evidence must include repo-local .omx/state/langgraph/ state.")

    if has_durable_adoption or has_compatibility:
        detected.append("selector_source")
        if has_durable_adoption and not contains_any(text, SELECTOR_MARKERS):
            errors.append(
                "Automatic durable-team adoption evidence must cite .omx/state/selectors/active.json as the active selector source."
            )
        if has_compatibility and has_durable_adoption and not contains_any(text, SELECTOR_MARKERS):
            errors.append(
                "Compatibility records may be context only and must not be the sole durable-team adoption authority."
            )

    if has_durable_artifact:
        detected.append("durable_artifact")
        if matches_any(text, TRANSIENT_ONLY_PATTERNS) or not has_repo_local_path(text):
            errors.append(
                "Durable artifacts, frozen briefs, and survivor queues must be persisted to repo-local state "
                "or documented artifact paths, not only transient chat context."
            )

    if has_research_to_implementation:
        detected.append("frozen_research_handoff")
        for field in BRIEF_FIELDS:
            if field not in text.lower():
                errors.append(f"Frozen implementation brief evidence must include {field}.")
        if not has_repo_local_path(text):
            errors.append("Frozen implementation brief evidence must include a repo-local state or documented artifact path.")

    if has_bug_triad:
        detected.append("adversarial_survivor_queue")
        lowered = text.lower()
        for marker in BUG_TRIAD_REQUIRED:
            if marker not in lowered:
                errors.append(f"Bug triad evidence must include {marker}.")
        if not has_repo_local_path(text):
            errors.append("Adversarial-review survivor queue evidence must include a repo-local state or documented artifact path.")

    if not detected and not errors:
        warnings.append(
            "No explorer, LangGraph state, durable artifact, research handoff, selector-source, or bug-triad markers were detected in the evidence file."
        )
    elif not errors:
        info.append("Durable artifact/state-surface evidence is acceptable.")

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
        description="Validate explorer/worker boundaries and durable artifact state-surface evidence."
    )
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved run-summary, worker brief, or durable artifact evidence file to validate.")
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
            print("Durable artifact/state-surface repository policy is backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
