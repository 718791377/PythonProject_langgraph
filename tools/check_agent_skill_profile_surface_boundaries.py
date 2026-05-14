#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "agent_skill_profile_surface_boundaries"
REGISTRY_RULE_ID = "orchestration-activation-policy"
GUARD_STEP = "check_agent_skill_profile_surface_boundaries"
SCRIPT_PATH = "tools/check_agent_skill_profile_surface_boundaries.py"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "Native reusable role definitions",
        "skills from installed SKILL.md files",
        "plugin modules and profile helpers",
        "skills or plugin profiles",
        "tools/check_agent_skill_profile_surface_boundaries.py",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Native agents, skills, and profiles remain distinct",
        "tools/check_agent_skill_profile_surface_boundaries.py",
        "skill or profile invocation is not expert evidence",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "Native agents, skills, and profiles remain distinct",
        "tools/check_agent_skill_profile_surface_boundaries.py",
        "skill or profile invocation is not expert evidence",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "Native agents, skills, and profile helpers are distinct orchestration surfaces",
        "Native reusable role definitions live in user-level or repo-local agents directories",
        "Skills are loaded from installed `SKILL.md` files",
        "Skill invocation, plugin profile loading, or profile helper hard-load/soft-load is not expert evidence",
        "tools/check_agent_skill_profile_surface_boundaries.py",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "Native agents, skills, and profile helpers are distinct orchestration surfaces",
        "Native reusable role definitions live in user-level or repo-local agents directories",
        "Skills are loaded from installed `SKILL.md` files",
        "Skill invocation, plugin profile loading, or profile helper hard-load/soft-load is not expert evidence",
        "tools/check_agent_skill_profile_surface_boundaries.py",
    ],
}

SPEC_SURFACE_SNIPPETS = [
    "Agent skill and profile surfaces SHALL remain distinct",
    "native Codex agents, workflow skills, plugin-provided skills, plugin modules, and profile helpers as distinct surfaces",
    "skill/profile invocation is not expert evidence",
]

SPEC_SURFACE_CANDIDATES = (
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md",
    "openspec/changes/enforce-agent-skill-profile-surface-boundaries/specs/codex-user-level-orchestration-activation-policy/spec.md",
)

FORBIDDEN_REPOSITORY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"skills?\s+(are|as)\s+native\s+(codex\s+)?subagents?", re.IGNORECASE),
    re.compile(r"plugin\s+profiles?\s+are\s+native\s+(codex\s+)?subagents?", re.IGNORECASE),
    re.compile(r"profile\s+helpers?\s+(are|as)\s+expert\s+evidence", re.IGNORECASE),
    re.compile(r"skill\s+invocation\s+(is|as)\s+expert\s+evidence", re.IGNORECASE),
)

SKILL_OR_PROFILE_MARKERS = (
    "skill invocation",
    "skill invoked",
    "invoked skill",
    "workflow skill",
    "plugin-provided skill",
    "plugin skill",
    "profile helper",
    "profile hard-load",
    "profile soft-load",
    "hard-load profile",
    "soft-load profile",
    "plugin profile",
    "skills loaded",
    "skill/profile",
    "skills/profiles",
    "技能调用",
    "调用技能",
    "配置文件加载",
    "硬加载配置文件",
    "软加载配置文件",
    "插件配置文件",
    "profile helper",
)

EXPERT_EVIDENCE_MARKERS = (
    "expert returned",
    "expert result",
    "expert evidence",
    "native subagent",
    "subagent result",
    "worker evidence",
    "durable team evidence",
    "durable-team evidence",
    "专家证据",
    "专家结果",
    "子代理结果",
    "持久化团队证据",
    "工作线程证据",
    "worker result",
)

VALID_EVIDENCE_MARKERS = (
    "actual expert result",
    "spawn_agent result",
    "wait_agent completed",
    "durable checkpoint",
    "local verification",
    "local test",
    "本地验证",
    "本地测试",
    "持久化检查点",
    "实际专家结果",
)

FALSE_BOUNDARY_MARKERS = (
    "skill invocation is expert evidence",
    "skill invocation as expert evidence",
    "skill invocation counts as expert",
    "plugin profile is expert evidence",
    "profile helper is expert evidence",
    "skills are native subagents",
    "plugin profiles are native subagents",
    "skills as native subagents",
    "profiles as native subagents",
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


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required agent/skill/profile boundary surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        for pattern in FORBIDDEN_REPOSITORY_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel} contains forbidden agent/skill/profile boundary wording: {pattern.pattern}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    spec_candidates_checked: list[dict[str, Any]] = []
    spec_surface_ok = False
    for rel in SPEC_SURFACE_CANDIDATES:
        spec_text = read_text(root / rel)
        if spec_text is None:
            spec_candidates_checked.append({"path": rel, "present": False, "missing": SPEC_SURFACE_SNIPPETS})
            continue
        missing = [snippet for snippet in SPEC_SURFACE_SNIPPETS if snippet not in spec_text]
        spec_candidates_checked.append({"path": rel, "present": True, "missing": missing})
        if not missing:
            spec_surface_ok = True
            break
    if not spec_surface_ok:
        errors.append(
            "No current orchestration activation spec surface contains all agent/skill/profile boundary snippets; "
            "expected either stable spec or active change delta to cover them."
        )
    checked.extend(spec_candidates_checked)

    guard_text = read_text(root / "tools/run_openspec_guard.py") or ""
    if GUARD_STEP not in guard_text:
        errors.append(f"tools/run_openspec_guard.py must run {GUARD_STEP}")

    manifest_text = read_text(root / "tools/ci/ci_test_manifest.json")
    if manifest_text is None:
        errors.append("Missing local CI manifest")
    else:
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid local CI manifest JSON: {exc}")
        else:
            tests = manifest.get("python_unittest", []) if isinstance(manifest, dict) else []
            if "check_agent_skill_profile_surface_boundaries.test.py" not in tests:
                errors.append("CI manifest missing check_agent_skill_profile_surface_boundaries.test.py")

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
                script_controls = rule.get("script_controls", [])
                guard_steps = rule.get("guard_steps", [])
                if SCRIPT_PATH not in script_controls:
                    errors.append(f"Safety rule {REGISTRY_RULE_ID} missing script_controls entry: {SCRIPT_PATH}")
                if GUARD_STEP not in guard_steps:
                    errors.append(f"Safety rule {REGISTRY_RULE_ID} missing guard_steps entry: {GUARD_STEP}")

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
        errors.append(f"Missing or unreadable agent/skill/profile evidence file: {evidence_path}")
        text = ""

    has_skill_or_profile = contains_any(text, SKILL_OR_PROFILE_MARKERS)
    has_expert_claim = contains_any(text, EXPERT_EVIDENCE_MARKERS)
    has_valid_evidence = contains_any(text, VALID_EVIDENCE_MARKERS)
    has_false_boundary = contains_any(text, FALSE_BOUNDARY_MARKERS)

    if has_skill_or_profile:
        detected.append("skill_or_profile_surface")
    if has_expert_claim:
        detected.append("expert_evidence_claim")
    if has_valid_evidence:
        detected.append("valid_evidence_source")

    if has_false_boundary:
        errors.append("Skill/profile surfaces must not be described as native subagents or expert evidence.")

    if has_skill_or_profile and has_expert_claim and not has_valid_evidence:
        errors.append(
            "Skill invocation, plugin profile loading, or profile helper use cannot support expert-result, "
            "native-subagent, worker, or durable-team evidence without a separate actual expert result, "
            "durable checkpoint, or local verification source."
        )

    if not detected and not errors:
        warnings.append("No skill/profile surface or expert-evidence markers were detected.")
    elif not errors:
        info.append("Agent, skill, and profile surface evidence is acceptable.")

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
    parser = argparse.ArgumentParser(description="Validate native agent, skill, plugin profile, and expert-evidence boundaries.")
    parser.add_argument("--root", default=".", help="Repository root for repository-surface checks.")
    parser.add_argument("--evidence", help="Saved trace, report, or routing evidence file to validate.")
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
            print("Agent/skill/profile surface boundaries are backed by script controls.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
