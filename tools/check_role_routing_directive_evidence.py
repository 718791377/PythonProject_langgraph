#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "role_routing_directive_evidence"
REGISTRY_RULE_ID = "role-routing-directive-evidence"
GUARD_STEP = "check_role_routing_directive_evidence"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "hard routing directives",
        "explanation-only mode",
        "optional preference",
        "smallest sufficient expert role set",
        "analyst-only fan-out",
        "tools/check_role_routing_directive_evidence.py",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Hard directive/role-routing discipline",
        "tools/check_role_routing_directive_evidence.py",
        "selected or running",
        "optional preference",
        "smallest-sufficient role",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Hard directive/role-routing discipline",
        "tools/check_role_routing_directive_evidence.py",
        "selected or running",
        "optional preference",
        "smallest-sufficient role",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Explicit `omx` and `LangGraph` requests are hard routing directives",
        "must not remain in explanation-only mode",
        "must not describe an explicit directive as an optional preference",
        "Smallest-sufficient role selection is mandatory",
        "Bounded multi-face research remains analyst-fanout-first",
        "tools/check_role_routing_directive_evidence.py",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "显式 `omx` 与 `LangGraph` 请求是当前 task flow 的 hard routing directives",
        "explanation-only mode",
        "optional preference",
        "Smallest-sufficient role selection",
        "analyst-fanout-first",
        "tools/check_role_routing_directive_evidence.py",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Hard routing directives SHALL require adoption or named blockers",
        "Smallest-sufficient role selection SHALL stay trigger-based",
        "tools/check_role_routing_directive_evidence.py",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "explicit directives are optional preferences",
        "add roles merely because available",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "explicit directives are optional preferences",
        "add roles merely because available",
    ],
}

DIRECTIVE_MARKERS = (
    "explicit directive",
    "hard routing directive",
    "user requested omx",
    "user explicitly requested omx",
    "explicit omx",
    "use omx",
    "user requested langgraph",
    "user explicitly requested langgraph",
    "explicit langgraph",
    "use langgraph",
    "显式 omx",
    "显式 langgraph",
)
ADOPTION_MARKERS = ("selected", "running", "lane adoption", "actual adoption", "已采用", "已选择")
BLOCKER_MARKERS = (
    "blocked:",
    "blocked by",
    "backend_not_ready",
    "preflight_failed",
    "helper_missing",
    "write_ownership_conflict",
    "threshold_not_met:",
    "unmet threshold",
    "未满足阈值",
    "具名 blocker",
)
OPTIONAL_PREFERENCE_MARKERS = ("optional preference", "soft preference", "软偏好", "可选偏好")
THRESHOLDS_SATISFIED_MARKERS = (
    "capability chain, preflight, and task thresholds are satisfied",
    "thresholds satisfied",
    "threshold_met",
    "no blocker exists",
    "no concrete blocker",
    "阈值已满足",
)
EXPLANATION_ONLY_MARKERS = ("explanation-only mode", "explanation only", "只解释不采用")

ROLE_NAMES = (
    "analyst",
    "researcher",
    "architect",
    "planner",
    "debugger",
    "verifier",
    "test-engineer",
    "security-reviewer",
    "writer",
    "bug-finder",
    "bug-rebutter",
    "bug-judge",
)

ROLE_TRIGGERS: dict[str, tuple[str, ...]] = {
    "analyst": ("unclear outcome", "non-goals", "acceptance target", "major ambiguities", "bounded multi-face research"),
    "researcher": ("external docs", "dependency behavior", "version-sensitive", "official-source", "official source"),
    "architect": ("2+ modules", "two or more modules", "shared interface", "trust boundary", "migration", "architecture"),
    "planner": ("execution slices", "rollout order", "dependency chain", "serial hotspot", "dependency chains"),
    "debugger": ("blocking failure", "regression", "reproducible defect", "stabilization", "stabilize"),
    "verifier": ("final acceptance", "behavior-changing", "multi-file", "multi-worker integration", "acceptance verification"),
    "test-engineer": ("critical-path behavior changed", "tests missing", "flaky", "broad regression", "test strategy"),
    "security-reviewer": ("auth", "secrets", "permissions", "untrusted input", "payments", "external trust boundary"),
    "writer": ("user-facing", "setup", "migration", "operator workflow", "document-finalization"),
    "bug-finder": ("contested", "noisy", "high-volume bug triage", "candidate bug"),
    "bug-rebutter": ("contested", "noisy", "high-volume bug triage", "candidate bug"),
    "bug-judge": ("contested", "noisy", "high-volume bug triage", "candidate bug"),
}

ROLE_HEADER_MARKERS = ("experts=", "selected experts", "role selection", "expert roles", "roles:")
MULTIFACE_RESEARCH_MARKERS = ("bounded multi-face research", "multi-face research", "多面研究")
FIRST_ROUND_MARKERS = ("first round", "first fan-out", "first-round", "首轮")
ANALYST_FANOUT_MARKERS = ("analystxn", "analyst x n", "analyst-only", "analyst fan-out", "analyst fanout")
FORBIDDEN_FIRST_ROUND_ROLES = ("architect", "planner", "writer")
AFTER_FANIN_MARKERS = ("after analyst fan-in", "analyst fan-in shows", "after fan-in", "fan-in 后")
EXTRA_ROLE_PATTERNS = (
    re.compile(r"roles?[^\n.]{0,80}(because|since)[^\n.]{0,40}available", re.IGNORECASE),
    re.compile(r"add(?:ed)?[^\n.]{0,60}roles?[^\n.]{0,60}available", re.IGNORECASE),
    re.compile(r"因为[^\n。]{0,40}可用[^\n。]{0,40}添加[^\n。]{0,20}角色", re.IGNORECASE),
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


def find_roles(text: str) -> list[str]:
    lowered = text.lower()
    roles: list[str] = []
    for role in ROLE_NAMES:
        pattern = rf"(?<![a-z0-9_-]){re.escape(role)}(?![a-z0-9_-])"
        if re.search(pattern, lowered):
            roles.append(role)
    if "analystxn" in lowered or "analyst x n" in lowered:
        roles.append("analyst")
    return sorted(set(roles))


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required role/directive policy surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden role/directive wording: {snippet}")

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
                    "script_controls": "tools/check_role_routing_directive_evidence.py",
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
        errors.append(f"Missing or unreadable role/directive evidence file: {evidence_path}")
        text = ""
    lowered = text.lower()

    has_directive = contains_any(text, DIRECTIVE_MARKERS)
    has_adoption = contains_any(text, ADOPTION_MARKERS)
    has_blocker = contains_any(text, BLOCKER_MARKERS)
    has_thresholds_satisfied = contains_any(text, THRESHOLDS_SATISFIED_MARKERS)
    has_explanation_only = contains_any(text, EXPLANATION_ONLY_MARKERS)
    roles = find_roles(text)
    has_role_context = bool(roles) and contains_any(text, ROLE_HEADER_MARKERS)
    has_multiface = contains_any(text, MULTIFACE_RESEARCH_MARKERS)

    if has_directive:
        detected.append("hard_directive")
        if contains_any(text, OPTIONAL_PREFERENCE_MARKERS):
            errors.append("Explicit `omx` or `LangGraph` directives must not be described as optional preferences.")
        if not (has_adoption or has_blocker):
            errors.append(
                "Explicit `omx` or `LangGraph` directives must lead to selected/running lane adoption "
                "or a named blocker/unmet threshold."
            )

    if has_thresholds_satisfied:
        detected.append("threshold_adoption")
        if has_explanation_only or not has_adoption:
            errors.append(
                "When capability chain, preflight, and task thresholds are satisfied, evidence must show actual "
                "selected/running adoption rather than explanation-only mode."
            )

    if matches_any(text, EXTRA_ROLE_PATTERNS):
        errors.append("Role evidence must not add expert roles merely because they are available.")

    if has_role_context:
        detected.append("role_minimality")
        for role in roles:
            triggers = ROLE_TRIGGERS[role]
            if not contains_any(text, triggers):
                errors.append(f"Role `{role}` must map to a smallest-sufficient trigger in the evidence.")

    if has_multiface:
        detected.append("analyst_first")
        if not contains_any(text, ANALYST_FANOUT_MARKERS):
            errors.append("Bounded multi-face research must start with analyst-only `analystxN` fan-out.")
        if contains_any(text, FIRST_ROUND_MARKERS):
            for role in FORBIDDEN_FIRST_ROUND_ROLES:
                if re.search(rf"(?<![a-z0-9_-]){role}(?![a-z0-9_-])", lowered) and not contains_any(
                    text, AFTER_FANIN_MARKERS
                ):
                    errors.append(
                        "Bounded multi-face research first round must not include architect, planner, or writer "
                        "before analyst fan-in."
                    )
                    break

    if not detected and not errors:
        warnings.append("No hard directive, threshold-adoption, role-selection, or bounded multi-face markers were detected.")
    elif not errors:
        info.append("Role routing and hard directive evidence is acceptable.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "mode": "evidence",
        "ok": not errors,
        "evidence_path": str(evidence_path),
        "detected": detected,
        "roles": roles,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {"detected": len(detected), "roles": len(roles), "errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate hard routing directive adoption and role-routing evidence.")
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved trace, run summary, or role-routing evidence file to validate.")
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
            print("Role routing/directive repository policy is backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
