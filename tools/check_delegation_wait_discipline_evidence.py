#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "delegation_wait_discipline_evidence"
REGISTRY_RULE_ID = "delegation-wait-discipline-evidence"
GUARD_STEP = "check_delegation_wait_discipline_evidence"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "Delegation must be concrete, bounded, self-contained",
        "immediate critical-path local work",
        "meaningful non-overlapping leader work",
        "wait_agent",
        "not alone in the codebase",
        "changed paths",
        "tools/check_delegation_wait_discipline_evidence.py",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Delegation/wait discipline",
        "tools/check_delegation_wait_discipline_evidence.py",
        "immediate critical-path local work",
        "non-overlapping leader work",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Delegation/wait discipline",
        "tools/check_delegation_wait_discipline_evidence.py",
        "immediate critical-path local work",
        "non-overlapping leader work",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Delegation must be concrete, bounded, self-contained sidecar work",
        "immediate critical-path local work",
        "meaningful non-overlapping leader work",
        "tools/check_delegation_wait_discipline_evidence.py",
        "not alone in the codebase",
        "changed paths",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "Delegation 必须是 concrete、bounded、self-contained sidecar work",
        "immediate critical-path local work",
        "meaningful non-overlapping leader work",
        "tools/check_delegation_wait_discipline_evidence.py",
        "不是代码库中唯一执行者",
        "changed paths",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Delegation and leader wait discipline SHALL be script-checkable",
        "tools/check_delegation_wait_discipline_evidence.py",
        "immediate critical-path local work",
        "meaningful non-overlapping leader work",
        "not alone in the codebase",
        "changed-path reporting",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "delegate blocking critical-path work by default",
        "wait_agent by reflex",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "delegate blocking critical-path work by default",
        "wait_agent by reflex",
    ],
}

NO_DELEGATION_MARKERS = (
    "no delegated expert work occurred",
    "no delegation occurred",
    "no expert delegation occurred",
    "未发生委派",
    "没有委派",
)

DELEGATION_MARKERS = (
    "delegated",
    "delegate",
    "delegation",
    "spawn_agent",
    "subagent",
    "expert",
    "worker brief",
    "worker task",
    "委派",
    "专家",
    "子代理",
)

LEADER_PLANNING_MARKERS = (
    "immediate critical-path local work",
    "immediate critical-path task",
    "leader local task",
    "leader-owned critical path",
    "critical-path local work",
    "本地关键路径",
    "主会话当前任务",
)

CONCRETE_MARKERS = ("concrete", "specific", "well-scoped", "明确", "具体")
BOUNDED_MARKERS = ("bounded", "bounded scope", "scope boundary", "范围", "有界")
SELF_CONTAINED_MARKERS = ("self-contained", "independent", "自包含", "独立")
MATERIAL_ADVANCE_MARKERS = ("materially advance", "materially advances", "实质推进")
SIDECAR_MARKERS = ("sidecar", "non-blocking", "旁路", "并行侧车")

NON_DUPLICATION_MARKERS = (
    "non-duplicative",
    "duplicate-work prevention",
    "no duplicate work",
    "avoid duplicate work",
    "non-overlapping",
    "disjoint",
    "不重复",
    "避免 duplicate",
)

CODE_WORK_MARKERS = (
    "code-changing worker",
    "code change worker",
    "bounded patch",
    "patch worker",
    "write set",
    "code worker",
    "代码修改",
    "补丁",
)

OWNERSHIP_MARKERS = (
    "file ownership",
    "module ownership",
    "ownership boundary",
    "disjoint write set",
    "disjoint write sets",
    "owned paths",
    "文件所有权",
    "模块所有权",
    "写入范围",
)

NOT_ALONE_MARKERS = (
    "not alone in the codebase",
    "not the only worker",
    "do not revert",
    "do not overwrite others",
    "不得 revert",
    "不得覆盖其他",
    "不是代码库中唯一执行者",
)

CHANGED_PATHS_MARKERS = (
    "changed paths",
    "list changed files",
    "list the file paths",
    "changed file paths",
    "列出修改文件",
    "列出 changed paths",
)

WAIT_MARKERS = (
    "wait_agent",
    "wait for expert",
    "wait for agent",
    "waited for expert",
    "等待 expert",
    "等待 agent",
)

NON_OVERLAPPING_LEADER_WORK_MARKERS = (
    "meaningful non-overlapping leader work",
    "leader continued non-overlapping work",
    "non-overlapping local work",
    "continued meaningful work",
    "主会话继续",
    "非重叠工作",
)

WAIT_BLOCKER_MARKERS = (
    "critical-path step was blocked",
    "blocked until result",
    "leader next step blocked",
    "next critical-path step depends on the result",
    "等待结果前被阻塞",
    "下一步依赖结果",
)

SPARSE_WAIT_MARKERS = (
    "sparingly",
    "only when blocked",
    "critical-path blocker",
    "仅在阻塞时",
    "谨慎使用",
)

BAD_WAIT_PATTERNS = (
    re.compile(r"\bwait(?:ed|ing)?\s+(indefinitely|forever|silently|by reflex)\b", re.IGNORECASE),
    re.compile(r"\b(unbounded|silent|reflexive)\s+wait\b", re.IGNORECASE),
    re.compile(r"(无限|静默|反射式|无界)\s*等待", re.IGNORECASE),
)

BAD_DELEGATION_PATTERNS = (
    re.compile(r"\bdelegat(?:e|ed|ing)\b[^\n.]{0,80}\b(urgent|immediate)\b[^\n.]{0,80}\bblocking\b", re.IGNORECASE),
    re.compile(r"\bdelegat(?:e|ed|ing)\b[^\n.]{0,80}\bcritical-path\b[^\n.]{0,80}\bblocking\b", re.IGNORECASE),
    re.compile(r"委派[^\n。]{0,80}(紧急|立即|关键路径)[^\n。]{0,80}(阻塞|依赖)", re.IGNORECASE),
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
            errors.append(f"Missing required delegation/wait discipline surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden delegation/wait wording: {snippet}")

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
                    "script_controls": "tools/check_delegation_wait_discipline_evidence.py",
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
        errors.append(f"Missing or unreadable delegation/wait discipline evidence file: {evidence_path}")
        text = ""

    no_delegation = contains_any(text, NO_DELEGATION_MARKERS)
    has_delegation = contains_any(text, DELEGATION_MARKERS) and not no_delegation
    has_code_work = contains_any(text, CODE_WORK_MARKERS)
    has_wait = contains_any(text, WAIT_MARKERS)

    if has_delegation:
        detected.append("delegation")
        if matches_any(text, BAD_DELEGATION_PATTERNS):
            errors.append(
                "Delegation evidence must not delegate urgent or immediate blocking critical-path work "
                "without an explicit handoff/takeover record."
            )
        for label, markers in {
            "immediate critical-path local work": LEADER_PLANNING_MARKERS,
            "concrete delegated task": CONCRETE_MARKERS,
            "bounded delegated task": BOUNDED_MARKERS,
            "self-contained delegated task": SELF_CONTAINED_MARKERS,
            "materially advancing sidecar work": MATERIAL_ADVANCE_MARKERS + SIDECAR_MARKERS,
            "duplicate-work prevention or non-overlap": NON_DUPLICATION_MARKERS,
        }.items():
            if not contains_any(text, markers):
                errors.append(f"Delegation evidence must include {label}.")

    if has_code_work:
        detected.append("code_worker")
        for label, markers in {
            "file/module ownership or disjoint write sets": OWNERSHIP_MARKERS,
            "not-alone/do-not-revert worker instruction": NOT_ALONE_MARKERS,
            "changed-path reporting expectation": CHANGED_PATHS_MARKERS,
        }.items():
            if not contains_any(text, markers):
                errors.append(f"Code-changing worker evidence must include {label}.")

    if has_wait:
        detected.append("wait")
        if matches_any(text, BAD_WAIT_PATTERNS):
            errors.append("Leader wait evidence must not describe indefinite, silent, unbounded, or reflexive waiting.")
        if not contains_any(text, SPARSE_WAIT_MARKERS):
            errors.append("Leader wait evidence must state that wait_agent is used sparingly or only when blocked.")
        if not (contains_any(text, NON_OVERLAPPING_LEADER_WORK_MARKERS) or contains_any(text, WAIT_BLOCKER_MARKERS)):
            errors.append(
                "Leader wait evidence must show meaningful non-overlapping leader work while waiting "
                "or name the critical-path blocker that prevents local progress."
            )

    if no_delegation and not has_wait:
        detected.append("no_delegation")

    if not errors:
        if detected:
            info.append("Delegation and leader wait discipline evidence is acceptable.")
        else:
            warnings.append("No delegation or wait markers were detected in the evidence file.")

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
        description="Validate delegation design quality and leader wait discipline evidence."
    )
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved run-summary or worker-brief evidence file to validate.")
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
            print("Delegation/wait discipline repository surfaces are backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
