#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "fanout_write_ownership_evidence"
REGISTRY_RULE_ID = "fanout-write-ownership-evidence"
GUARD_STEP = "check_fanout_write_ownership_evidence"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "tools/check_fanout_write_ownership_evidence.py",
        "leader-side spawning",
        "leader-owned fan-in",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "Raw Codex",
        "does not auto-spawn specialist roles",
        "read-heavy, bounded, independent",
        "write-heavy parallel execution",
        "file/module ownership",
        "disjoint write sets",
        "hotspot serialization",
        "leader-owned final integration",
        "not alone in the codebase",
        "must not revert or overwrite",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Fan-out/write-ownership discipline",
        "tools/check_fanout_write_ownership_evidence.py",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "leader-side spawning",
        "write-heavy parallel execution",
        "leader-owned final integration",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Fan-out/write-ownership discipline",
        "tools/check_fanout_write_ownership_evidence.py",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "leader-side spawning",
        "write-heavy parallel execution",
        "leader-owned final integration",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Fan-out and write-heavy parallel execution are bounded and ownership-isolated",
        "tools/check_fanout_write_ownership_evidence.py",
        "leader-side spawning",
        "leader-owned fan-in",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "Raw Codex",
        "does not auto-spawn specialist roles",
        "read-heavy, bounded, independent",
        "write-heavy parallel execution",
        "file/module ownership",
        "disjoint write sets",
        "hotspot serialization",
        "leader-owned final integration",
        "not alone in the codebase",
        "must not revert or overwrite",
        "changed-path reporting",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "Fan-out and write-heavy parallel execution are bounded and ownership-isolated",
        "tools/check_fanout_write_ownership_evidence.py",
        "leader-side spawning",
        "leader-owned fan-in",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "Raw Codex",
        "does not auto-spawn specialist roles",
        "read-heavy, bounded, independent",
        "write-heavy parallel execution",
        "file/module ownership",
        "disjoint write sets",
        "hotspot serialization",
        "leader-owned final integration",
        "not alone in the codebase",
        "must not revert or overwrite",
        "changed-path reporting",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Fan-out and write-heavy parallel execution SHALL be bounded and ownership-isolated",
        "tools/check_fanout_write_ownership_evidence.py",
        "leader-side spawning",
        "leader-owned fan-in",
        "agents.max_threads=6",
        "agents.max_depth=1",
        "Raw Codex SHALL NOT be described as auto-spawning specialist roles",
        "read-heavy or otherwise tightly bounded independent work",
        "Write-heavy parallel execution SHALL declare file/module ownership",
        "disjoint write sets",
        "hotspot serialization",
        "leader-owned final integration",
        "not alone in the codebase",
        "not to revert or overwrite",
        "changed-path reporting",
    ],
}

FORBIDDEN_REPOSITORY_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "raw Codex auto-spawns specialist roles",
        "write-heavy parallel execution may overlap without serialization",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "raw Codex auto-spawns specialist roles",
        "write-heavy parallel execution may overlap without serialization",
    ],
}

NO_FANOUT_MARKERS = (
    "no fan-out occurred",
    "no native subagent fan-out occurred",
    "single local execution slice",
)
FANOUT_MARKERS = (
    "fan-out",
    "fanout",
    "parallel subagents",
    "spawned agents",
    "spawn_agent",
    "subagent fan-out",
    "expert fan-out",
    "native subagent",
    "native codex subagents",
    "experts_now=",
)
READ_HEAVY_MARKERS = (
    "read-heavy",
    "read only",
    "read-only",
    "analysis-only",
    "mapping question",
    "codebase search",
    "research fan-out",
)
WRITE_HEAVY_MARKERS = (
    "write-heavy",
    "write heavy",
    "code-changing worker",
    "code change worker",
    "patch worker",
    "worker patch",
    "parallel write",
    "write set",
    "write sets",
    "file edits",
    "edit files",
    "changed files",
)
LEADER_SIDE_MARKERS = (
    "leader-side spawning",
    "leader side spawning",
    "leader spawned",
    "leader-owned spawning",
    "leader-owned fan-in",
    "leader owned fan-in",
    "leader fan-in",
    "main session owns fan-in",
    "current main codex cli session remains the leader",
)
RAW_CODEX_MARKERS = (
    "raw codex",
    "bare codex",
    "native codex startup",
)
RAW_CODEX_AUTO_SPAWN_PATTERNS = (
    re.compile(r"\braw\s+codex\b[^\n.]{0,120}\bauto[- ]?spawn(?:s|ed|ing)?\b[^\n.]{0,80}\b(?:specialist|subagent|expert|agent|role)s?", re.IGNORECASE),
    re.compile(r"\b(?:specialist|subagent|expert|agent|role)s?\b[^\n.]{0,80}\bauto[- ]?spawn(?:s|ed|ing)?\b[^\n.]{0,120}\braw\s+codex\b", re.IGNORECASE),
)
NO_AUTO_SPAWN_MARKERS = (
    "does not auto-spawn specialist roles",
    "do not imply raw codex auto-spawns",
    "raw codex does not auto-spawn",
    "not auto-spawn specialist roles",
    "leader-side spawning rather than raw codex auto-spawning",
)
MAX_THREADS_PATTERNS = (
    re.compile(r"agents\.max_threads\s*=\s*(\d+)", re.IGNORECASE),
    re.compile(r"max_threads\s*[:=]\s*(\d+)", re.IGNORECASE),
    re.compile(r"threads\s*[:=]\s*(\d+)", re.IGNORECASE),
    re.compile(r"(\d+)\s+(?:parallel\s+)?(?:agents|subagents|experts|workers|threads)", re.IGNORECASE),
)
MAX_DEPTH_PATTERNS = (
    re.compile(r"agents\.max_depth\s*=\s*(\d+)", re.IGNORECASE),
    re.compile(r"max_depth\s*[:=]\s*(\d+)", re.IGNORECASE),
    re.compile(r"depth\s*[:=]\s*(\d+)", re.IGNORECASE),
)
OVERRIDE_MARKERS = (
    "explicit override",
    "override approved",
    "approved override",
    "operator approved override",
    "user approved override",
    "override reason",
    "override_reason",
)
BOUNDED_MARKERS = (
    "bounded",
    "tightly bounded",
    "bounded scope",
    "scope boundary",
    "managed bounds",
)
INDEPENDENT_MARKERS = (
    "independent",
    "mostly independent",
    "non-overlapping",
    "disjoint",
    "self-contained",
)
MATERIAL_ADVANCE_MARKERS = (
    "materially advance",
    "materially advances",
    "materially useful",
    "advances the main task",
)
OWNERSHIP_MARKERS = (
    "file/module ownership",
    "file ownership",
    "module ownership",
    "ownership boundary",
    "owned paths",
    "owner paths",
)
DISJOINT_MARKERS = (
    "disjoint write sets",
    "disjoint write set",
    "non-overlapping write sets",
    "isolated write sets",
    "separate write sets",
)
HOTSPOT_MARKERS = (
    "hotspot serialization",
    "hotspot serialized",
    "serialize hotspot",
    "serialized hotspot",
    "shared hotspot serialized",
    "no shared hotspot",
    "no hotspot",
    "sequential ownership transfer",
    "leader-owned merge plan",
)
LEADER_INTEGRATION_MARKERS = (
    "leader-owned final integration",
    "leader owned final integration",
    "leader final integration",
    "leader-owned integration",
    "leader owns final integration",
    "leader-owned merge",
)
NOT_ALONE_MARKERS = (
    "not alone in the codebase",
    "not the only worker",
    "not alone",
)
DO_NOT_REVERT_MARKERS = (
    "must not revert or overwrite",
    "must not revert",
    "do not revert",
    "do not overwrite",
    "must not overwrite",
    "avoid overwriting",
)
CHANGED_PATHS_MARKERS = (
    "changed paths",
    "changed-path reporting",
    "list changed paths",
    "list changed files",
    "list the file paths",
    "changed file paths",
)
OVERLAP_MARKERS = (
    "overlapping write sets",
    "overlap write sets",
    "shared hotspot",
    "same files",
    "same path",
    "same module",
)
BAD_OVERLAP_PATTERNS = (
    re.compile(r"overlap(?:ping)?\s+write\s+sets?[^\n.]{0,120}\b(?:without|no)\b[^\n.]{0,80}\b(serial|hotspot|merge|handoff)", re.IGNORECASE),
    re.compile(r"same\s+(?:files?|paths?|modules?)[^\n.]{0,120}\bparallel\b[^\n.]{0,80}\b(?:without|no)\b[^\n.]{0,80}\b(serial|hotspot|merge|handoff)", re.IGNORECASE),
)
BLOCKING_DELEGATION_PATTERNS = (
    re.compile(r"delegat(?:e|ed|ing)[^\n.]{0,100}(?:urgent|immediate)[^\n.]{0,80}blocking[^\n.]{0,80}critical[- ]path", re.IGNORECASE),
    re.compile(r"delegat(?:e|ed|ing)[^\n.]{0,100}critical[- ]path[^\n.]{0,80}blocking", re.IGNORECASE),
)
HANDOFF_MARKERS = (
    "explicit handoff",
    "handoff reason",
    "main-session takeover",
    "leader takeover",
    "explicit takeover",
    "critical-path handoff",
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


def max_int_for_patterns(text: str, patterns: tuple[re.Pattern[str], ...]) -> int | None:
    values: list[int] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            try:
                values.append(int(match.group(1)))
            except (IndexError, ValueError):
                continue
    return max(values) if values else None


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required fan-out/write-ownership policy surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_REPOSITORY_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden fan-out/write-ownership wording: {snippet}")

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
                    "script_controls": "tools/check_fanout_write_ownership_evidence.py",
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
        errors.append(f"Missing or unreadable fan-out/write-ownership evidence file: {evidence_path}")
        text = ""

    no_fanout = contains_any(text, NO_FANOUT_MARKERS)
    has_fanout = contains_any(text, FANOUT_MARKERS) and not no_fanout
    has_read = contains_any(text, READ_HEAVY_MARKERS)
    has_write = contains_any(text, WRITE_HEAVY_MARKERS)
    has_raw_codex = contains_any(text, RAW_CODEX_MARKERS)
    has_leader_side = contains_any(text, LEADER_SIDE_MARKERS)
    has_override = contains_any(text, OVERRIDE_MARKERS)
    max_threads = max_int_for_patterns(text, MAX_THREADS_PATTERNS)
    max_depth = max_int_for_patterns(text, MAX_DEPTH_PATTERNS)

    if matches_any(text, RAW_CODEX_AUTO_SPAWN_PATTERNS) and not contains_any(text, NO_AUTO_SPAWN_MARKERS):
        detected.append("raw_codex_auto_spawn_claim")
        errors.append("Evidence must not imply raw Codex auto-spawns specialist roles; use leader-side spawning language.")

    if has_fanout:
        detected.append("fanout")
        if not has_leader_side:
            errors.append("Fan-out evidence must show leader-side spawning and leader-owned fan-in.")
        if has_raw_codex and not contains_any(text, NO_AUTO_SPAWN_MARKERS):
            errors.append("Raw Codex fan-out evidence must state that raw Codex does not auto-spawn specialist roles.")
        if max_threads is None:
            warnings.append("Fan-out evidence did not state agents.max_threads; default bound is assumed only if no count is claimed.")
        elif max_threads > 6 and not has_override:
            errors.append("Fan-out evidence exceeds agents.max_threads=6 without an explicit override, reason, and approval.")
        if max_depth is None:
            warnings.append("Fan-out evidence did not state agents.max_depth; default depth is assumed only if no depth is claimed.")
        elif max_depth > 1 and not has_override:
            errors.append("Fan-out evidence exceeds agents.max_depth=1 without an explicit override, reason, and approval.")
        if has_read:
            detected.append("read_heavy_fanout")
            for label, markers in {
                "bounded read-heavy fan-out": BOUNDED_MARKERS,
                "independent read-heavy work": INDEPENDENT_MARKERS,
                "materially advancing read-heavy work": MATERIAL_ADVANCE_MARKERS,
            }.items():
                if not contains_any(text, markers):
                    errors.append(f"Read-heavy fan-out evidence must include {label}.")

    if has_write:
        detected.append("write_heavy_parallel")
        for label, markers in {
            "file/module ownership": OWNERSHIP_MARKERS,
            "disjoint write sets": DISJOINT_MARKERS,
            "hotspot serialization or no shared hotspot": HOTSPOT_MARKERS,
            "leader-owned final integration": LEADER_INTEGRATION_MARKERS,
            "not-alone worker instruction": NOT_ALONE_MARKERS,
            "do-not-revert-or-overwrite instruction": DO_NOT_REVERT_MARKERS,
            "changed-path reporting": CHANGED_PATHS_MARKERS,
        }.items():
            if not contains_any(text, markers):
                errors.append(f"Write-heavy parallel evidence must include {label}.")

    has_overlap = contains_any(text, OVERLAP_MARKERS) or matches_any(text, BAD_OVERLAP_PATTERNS)
    if has_overlap:
        detected.append("overlapping_write_sets")
        if matches_any(text, BAD_OVERLAP_PATTERNS) or not contains_any(text, HOTSPOT_MARKERS):
            errors.append("Overlapping write sets or shared hotspots must be serialized or have a leader-owned merge plan.")

    if matches_any(text, BLOCKING_DELEGATION_PATTERNS) and not contains_any(text, HANDOFF_MARKERS):
        detected.append("blocking_critical_path_delegation")
        errors.append("Immediate blocking critical-path work must stay local unless explicit handoff/takeover is recorded.")

    if no_fanout and not has_write:
        detected.append("no_fanout")

    if not errors:
        if detected:
            info.append("Fan-out and write-ownership evidence is acceptable.")
        else:
            warnings.append("No fan-out, raw-Codex, or write-heavy ownership markers were detected in the evidence file.")

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
        description="Validate native subagent fan-out bounds and write-heavy worker ownership evidence."
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
            print("Fan-out/write-ownership repository policy is backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
