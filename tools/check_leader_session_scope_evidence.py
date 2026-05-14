#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

CHECK_NAME = "leader_session_scope_evidence"
REGISTRY_RULE_ID = "leader-session-scope-evidence"
GUARD_STEP = "check_leader_session_scope_evidence"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "Preserve the current main Codex CLI session as leader",
        "separate persistent leader pane",
        "Treat resumed legacy Codex sessions as compatibility-scoped",
        "tools/check_leader_session_scope_evidence.py",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Current main-session scope evidence",
        "tools/check_leader_session_scope_evidence.py",
        "current main Codex CLI session remains the leader",
        "separate persistent leader pane",
        "startup or first activation",
        "task-flow scoped adoption",
        "legacy resumed sessions are compatibility-scoped",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Current main-session scope evidence",
        "tools/check_leader_session_scope_evidence.py",
        "current main Codex CLI session remains the leader",
        "separate persistent leader pane",
        "startup or first activation",
        "task-flow scoped adoption",
        "legacy resumed sessions are compatibility-scoped",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Leader session and task-flow scope evidence",
        "tools/check_leader_session_scope_evidence.py",
        "current main Codex CLI session remains the leader",
        "separate persistent leader pane",
        "startup non-autolaunch",
        "task-flow scoped adoption",
        "legacy resumed sessions are compatibility-scoped",
        "reload, restart, resume, continue",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "Leader session and task-flow scope evidence",
        "tools/check_leader_session_scope_evidence.py",
        "current main Codex CLI session remains the leader",
        "separate persistent leader pane",
        "startup non-autolaunch",
        "task-flow scoped adoption",
        "legacy resumed sessions are compatibility-scoped",
        "reload, restart, resume, continue",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Main-session leader and task-flow scope evidence SHALL be script-checkable",
        "tools/check_leader_session_scope_evidence.py",
        "leader-owned fan-in",
        "startup non-autolaunch",
        "task-flow scoped adoption",
        "legacy resumed sessions",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "separate persistent leader pane replaces the current main Codex CLI session",
        "Codex startup auto-launches durable teams",
        "new repositories use orchestration but existing projects do not",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "separate persistent leader pane replaces the current main Codex CLI session",
        "Codex startup auto-launches durable teams",
        "new repositories use orchestration but existing projects do not",
    ],
}

LEADER_MARKERS = (
    "current main codex cli session remains the leader",
    "main codex cli session remains the leader",
    "main session remains leader",
    "current main session remains the leader",
)
FANIN_MARKERS = ("leader-owned fan-in", "leader owned fan-in", "leader owns fan-in", "leader fan-in")
EVIDENCE_LABEL_MARKERS = ("evidence labeling", "labels evidence", "evidence sources", "evidence source")
INTEGRATION_MARKERS = ("final integration", "leader-owned final integration", "release recommendations", "release recommendation")

SEPARATE_LEADER_FORBIDDEN_PATTERNS = (
    re.compile(r"separate persistent leader pane\s+(replaces|replaced|replacing|instead of|takes over)", re.IGNORECASE),
    re.compile(r"main (codex cli )?session\s+(is|was)?\s*(replaced|owned) by (a )?separate persistent leader pane", re.IGNORECASE),
    re.compile(r"persistent leader pane\s+(replaces|owns|becomes the leader)", re.IGNORECASE),
)
NEGATION_MARKERS = ("not ", "no ", "never ", "shall not", "must not", "do not", "does not", "without ", "不得", "不能", "不会", "不是")

STARTUP_MARKERS = ("startup", "first activation", "codex startup", "session start", "首次 activation")
STARTUP_AUTOLAUNCH_PATTERNS = (
    re.compile(r"startup\s+auto[- ]?launch(?:es|ed)?\s+durable team", re.IGNORECASE),
    re.compile(r"codex startup\s+auto[- ]?launch(?:es|ed)?\s+durable", re.IGNORECASE),
    re.compile(r"auto[- ]?launch(?:es|ed)?\s+durable team\s+on startup", re.IGNORECASE),
)
THRESHOLD_MARKERS = (
    "threshold_not_met:",
    "triggered_threshold:",
    "threshold_met:",
    "unmet threshold",
    "concrete threshold",
    "no_frozen_plan",
    "single_execution_slice",
    "frozen plan",
    "2+ independent execution slices",
    "two or more independent execution slices",
    "stabilization phase with named blocking issues",
)

ADOPTION_SCOPE_MARKERS = ("task-flow scoped adoption", "current task flow", "current task-flow", "task flow scoped", "scoped to the current task")
REPO_STATUS_BASIS_PATTERNS = (
    re.compile(r"adoption\s+(is|was|based|decided)[^\n.]{0,80}(new repo|new repository|existing project|old project|repo age)", re.IGNORECASE),
    re.compile(r"because\s+(the\s+)?(repo|repository)\s+(is\s+)?(new|old|existing)", re.IGNORECASE),
    re.compile(r"new repositories\s+use orchestration\s+but\s+existing projects\s+do not", re.IGNORECASE),
)

LEGACY_MARKERS = ("legacy resumed session", "legacy session", "resumed legacy", "旧会话", "legacy resume")
LEGACY_BOUNDARY_MARKERS = (
    "compatibility-scoped",
    "current repository governance",
    "capability-chain policy",
)
LEGACY_FORBIDDEN_PATTERNS = (
    re.compile(r"legacy (resumed )?session\s+(overrides|replaces)\s+current (repository )?governance", re.IGNORECASE),
    re.compile(r"legacy (resumed )?session\s+(overrides|replaces)\s+.*capability[- ]chain", re.IGNORECASE),
)

RETROFIT_TRIGGER_MARKERS = ("resume", "continue", "reload", "restart", "durable-state detection", ".omx durable-state", ".omx state detection")
ACTIVATION_RERUN_MARKERS = ("activation check", "re-run activation", "rerun activation", "triggered activation", "重新 activation", "重新做 activation")


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


def contains_all_categories(text: str, categories: list[tuple[str, ...]]) -> list[str]:
    missing: list[str] = []
    names = ["main-session leader marker", "leader-owned fan-in", "evidence labeling", "final integration or release recommendation"]
    for name, markers in zip(names, categories):
        if not contains_any(text, markers):
            missing.append(name)
    return missing


def line_is_negated(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in NEGATION_MARKERS)


def has_forbidden_unnegated_line(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    for line in text.splitlines():
        if any(pattern.search(line) for pattern in patterns) and not line_is_negated(line):
            return True
    return False


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required leader/session scope policy surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden leader/session scope wording: {snippet}")

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
                    "script_controls": "tools/check_leader_session_scope_evidence.py",
                    "guard_steps": GUARD_STEP,
                }.items():
                    values = rule.get(field, [])
                    if expected not in values:
                        errors.append(f"Safety rule {REGISTRY_RULE_ID} missing {field} entry: {expected}")

    manifest_text = read_text(root / "tools/ci/ci_test_manifest.json")
    if manifest_text is None:
        errors.append("Missing CI test manifest")
    else:
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid CI test manifest JSON: {exc}")
        else:
            tests = manifest.get("python_unittest", []) if isinstance(manifest, dict) else []
            if "check_leader_session_scope_evidence.test.py" not in tests:
                errors.append("CI test manifest missing check_leader_session_scope_evidence.test.py")

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
        errors.append(f"Missing or unreadable leader/session scope evidence file: {evidence_path}")
        text = ""
    lowered = text.lower()

    missing_leader = contains_all_categories(
        text,
        [LEADER_MARKERS, FANIN_MARKERS, EVIDENCE_LABEL_MARKERS, INTEGRATION_MARKERS],
    )
    if missing_leader:
        errors.append(
            "Leader evidence must show the current main Codex CLI session remains the leader, "
            "leader-owned fan-in, evidence labeling, and final integration/release recommendation evidence; "
            f"missing: {', '.join(missing_leader)}."
        )
    else:
        detected.append("leader_ownership")

    if has_forbidden_unnegated_line(text, SEPARATE_LEADER_FORBIDDEN_PATTERNS):
        errors.append("A separate persistent leader pane must not replace or own the current main Codex CLI session.")
    elif "separate persistent leader pane" in lowered:
        detected.append("no_separate_persistent_leader_pane")

    if contains_any(text, STARTUP_MARKERS):
        detected.append("startup_threshold")
        if any(pattern.search(text) for pattern in STARTUP_AUTOLAUNCH_PATTERNS) and not contains_any(text, THRESHOLD_MARKERS):
            errors.append("Startup or first activation must not auto-launch a durable team without threshold evidence.")
        if "persistent_team=not_needed" in lowered and not contains_any(text, THRESHOLD_MARKERS):
            errors.append("Startup or first activation with persistent_team=not_needed must cite an unmet threshold.")
        if "persistent_team=selected" in lowered and not contains_any(text, THRESHOLD_MARKERS):
            errors.append("Startup or first activation with persistent_team=selected must cite the triggered threshold.")

    if any(pattern.search(text) for pattern in REPO_STATUS_BASIS_PATTERNS):
        errors.append("Orchestration adoption must be scoped to the current task flow, not repository age or new/existing status.")
    if contains_any(text, ADOPTION_SCOPE_MARKERS):
        detected.append("task_flow_scope")
    elif "adoption" in lowered or "routing decision" in lowered:
        errors.append("Adoption or routing-decision evidence must explicitly state task-flow scoped adoption/current task flow scope.")

    if contains_any(text, LEGACY_MARKERS):
        detected.append("legacy_boundary")
        if has_forbidden_unnegated_line(text, LEGACY_FORBIDDEN_PATTERNS):
            errors.append("Legacy resumed sessions must not override current repository governance or capability-chain policy.")
        for marker in LEGACY_BOUNDARY_MARKERS:
            if marker.lower() not in lowered:
                errors.append(f"Legacy session evidence missing boundary marker: {marker}")

    if contains_any(text, RETROFIT_TRIGGER_MARKERS):
        detected.append("retrofit_activation")
        if not contains_any(text, ACTIVATION_RERUN_MARKERS):
            errors.append("reload/restart/resume/continue/durable-state detection evidence must show an activation check rerun.")

    if not errors:
        info.append("Leader/session scope evidence is acceptable.")

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
        description="Validate main-session leader ownership, startup threshold, task-flow scope, and legacy-resume evidence."
    )
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved trace, run summary, or leader/scope evidence file to validate.")
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
            print("Leader/session scope repository policy is backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
