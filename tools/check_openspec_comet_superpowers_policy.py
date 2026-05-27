#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DOC_ID = "openspec_comet_superpowers_workflow_policy"
EN_POLICY = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md")
ZH_POLICY = Path("docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
ACTIVE_SPEC = Path(
    "openspec/changes/upgrade-openspec-comet-superpowers/"
    "specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md"
)
STABLE_SPEC = Path("openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md")
IMPLEMENTATION_PLAN = Path("docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md")
IMPLEMENTATION_PLAN_ZH = Path("docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md")
COMET_STATE_SCRIPT = Path(".codex/skills/comet/scripts/comet-state.sh")
COMET_GUARD_SCRIPT = Path(".codex/skills/comet/scripts/comet-guard.sh")
COMET_VALIDATE_SCRIPT = Path(".codex/skills/comet/scripts/comet-yaml-validate.sh")
COMET_ARCHIVE_SCRIPT = Path(".codex/skills/comet/scripts/comet-archive.sh")
COMET_SKILL_FILES = [
    Path(".codex/skills/comet/SKILL.md"),
    Path(".codex/skills/comet-open/SKILL.md"),
    Path(".codex/skills/comet-design/SKILL.md"),
    Path(".codex/skills/comet-build/SKILL.md"),
    Path(".codex/skills/comet-verify/SKILL.md"),
    Path(".codex/skills/comet-archive/SKILL.md"),
    Path(".codex/skills/comet-hotfix/SKILL.md"),
    Path(".codex/skills/comet-tweak/SKILL.md"),
]

EN_REQUIRED_TERMS = [
    "Comet-controlled OpenSpec + Superpowers",
    "OpenSpec is the WHAT layer",
    "Superpowers is the HOW layer",
    "Comet is the control layer",
    "Open -> Design -> Build -> Verify -> Archive",
    ".openspec.yaml",
    ".comet.yaml",
    "comet init",
    "explicit operator approval",
    "Skills remain workflow instruction surfaces",
    "not native subagent evidence",
    "PMBOK8 Project Management Focus Areas",
    "Open | Initiating",
    "Design | Planning",
    "Build | Executing",
    "Verify | Controlling",
    "Archive | Closing",
    "Monitoring is a cross-cutting focus area",
    "non-prescriptive",
    "Runtime Monitoring is more than a passive check",
    "return the active change to `open`, `design`, `build`, or `verify`",
    "adaptive or hybrid control loop",
]

ZH_REQUIRED_TERMS = [
    "Comet 控制",
    "OpenSpec",
    "Superpowers",
    "WHAT",
    "HOW",
    "Comet 管 WHEN & NEXT",
    "Open -> Design -> Build -> Verify -> Archive",
    ".openspec.yaml",
    ".comet.yaml",
    "显式操作员批准",
    "不是 native subagent 证据",
    "PMBOK8 Project Management Focus Areas",
    "Open | Initiating",
    "Design | Planning",
    "Build | Executing",
    "Verify | Controlling",
    "Archive | Closing",
    "Monitoring 是横切 focus area",
    "non-prescriptive",
    "Runtime Monitoring 不只是被动检查或阻拦",
    "回退到 `open`、`design`、`build` 或 `verify`",
    "适应型/混合型控制循环",
]

SPEC_REQUIRED_TERMS = [
    "Comet-controlled workflow SHALL preserve layer boundaries",
    "five-phase pipeline",
    "decoupled state",
    "guard phase transitions",
    "archive evidence",
    "explicit and repository-local",
    "checker-backed",
    "PMBOK8 Project Management Focus Areas",
    "Open = Initiating",
    "Design = Planning",
    "Build = Executing",
    "Verify = Controlling",
    "Archive = Closing",
    "Monitoring SHALL be documented as a cross-cutting focus area",
    "Comet runtime SHALL support iterative management returns",
    "management record with checklist evidence",
    "return work from the current phase to `open`, `design`, `build`, or `verify`",
    "Return transitions SHALL preserve the rework reason and increment an iteration counter",
    "runtime field names SHALL NOT depend on the literal `PMBOK8` term",
]

IMPLEMENTATION_PLAN_REQUIRED_TERMS = [
    "Comet Runtime Agile Focus-Area Implementation Plan",
    "Monitoring can return work from any current phase",
    "return transitions",
    "iteration_count",
]

IMPLEMENTATION_PLAN_ZH_REQUIRED_TERMS = [
    "Comet Runtime 敏捷/混合式管理关注领域落地方案",
    "可以回退到 `open/design/build/verify`",
    "不做一次性大瀑布方案",
    "monitor-return-design",
]

STATE_SCRIPT_REQUIRED_TERMS = [
    "management_record:",
    "monitoring_status: clear",
    "control_decision: continue",
    "target_phase: null",
    "rework_reason: null",
    "iteration_count: 0",
    "apply_monitor_return",
    "increment_iteration",
    "require_forward_monitoring_clear",
    "monitoring_status must be 'clear'",
    "control_decision must be 'continue'",
    "monitor-return-open",
    "monitor-return-design",
    "monitor-return-build",
    "monitor-return-verify",
]

GUARD_SCRIPT_REQUIRED_TERMS = [
    "management_phase_complete",
    "monitoring_allows_forward",
    "Open management checklist complete",
    "Design management checklist complete",
    "Build management checklist complete",
    "Verify management checklist complete",
    "Archive management checklist complete",
    "checklist_done_named",
    "Missing management checklist section:",
    "Missing management checklist item:",
    "control_decision=adjust-current",
    "monitor-return-* transition",
]

VALIDATE_SCRIPT_REQUIRED_TERMS = [
    "management_record monitoring_status control_decision target_phase rework_reason iteration_count",
    "clear needs_decision blocked",
    "return-open return-design return-build return-verify stop",
    "iteration_count='$iteration_count' is not a non-negative integer",
]

ARCHIVE_SCRIPT_REQUIRED_TERMS = [
    "Management closing evidence verified",
    "checklist_done_any",
    "价值结果已总结",
    "经验沉淀已记录",
    "delta spec sync / verification evidence / archive path 已确认",
    "Value outcome is summarized.",
    "Lessons learned or reusable guidance are recorded.",
    "Delta spec sync, verification evidence, and archive path are confirmed.",
    "monitoring_status is",
    "control_decision is",
]

SKILL_REQUIRED_TERMS = [
    "management_record",
    "monitor-return-open",
    "monitor-return-design",
    "monitor-return-build",
    "monitor-return-verify",
    "Management Checklist",
    "adaptive/hybrid rework loop",
    "Archive management checklist",
]

ROOT_SKILL_REQUIRED_TERMS = [
    "Adaptive Monitoring Return Dispatch",
    "`control_decision=return-open|return-design|return-build|return-verify`",
    "`monitoring_status=blocked`",
    "do not force waterfall progression",
    "`return-open` -> `/comet-open`",
    "`return-design` -> `/comet-design`",
    "`return-build` -> `/comet-build`",
    "`return-verify` -> `/comet-verify`",
    "reread `.comet.yaml`",
    "refresh the target phase management checklist",
]

PHASE_SKILL_REQUIRED_TERMS = {
    ".codex/skills/comet-open/SKILL.md": [
        "Open management checklist",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-design/SKILL.md": [
        "Design management checklist",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-build/SKILL.md": [
        "Build management checklist",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-verify/SKILL.md": [
        "Verify management checklist",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-archive/SKILL.md": [
        "Archive management checklist",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-hotfix/SKILL.md": [
        "Management checklist evidence",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
    ".codex/skills/comet-tweak/SKILL.md": [
        "Management checklist evidence",
        "Monitoring is a cross-cutting focus area, not a sixth Comet phase",
        "`monitoring_status=clear`",
        "`control_decision=continue`",
        "do not force waterfall progression",
        "monitor-return-open",
        "monitor-return-design",
        "monitor-return-build",
        "monitor-return-verify",
        "refresh its matching management checklist",
    ],
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def parse_registry_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            stripped = stripped[2:]
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def require_file(root: Path, relative: Path, errors: list[str]) -> Path | None:
    path = root / relative
    if not path.exists():
        errors.append(f"Missing required file: {relative.as_posix()}")
        return None
    if not path.is_file():
        errors.append(f"Required path is not a file: {relative.as_posix()}")
        return None
    return path


def check_terms(label: str, text: str, terms: list[str], errors: list[str]) -> list[str]:
    missing = [term for term in terms if term not in text]
    for term in missing:
        errors.append(f"{label} is missing required term: {term}")
    return missing


def build_report(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    checked_files: list[str] = []

    en_path = require_file(root, EN_POLICY, errors)
    zh_path = require_file(root, ZH_POLICY, errors)
    registry_path = require_file(root, REGISTRY, errors)

    en_missing: list[str] = []
    zh_missing: list[str] = []
    spec_missing: list[str] = []
    implementation_plan_missing: list[str] = []
    implementation_plan_zh_missing: list[str] = []
    state_script_missing: list[str] = []
    guard_script_missing: list[str] = []
    validate_script_missing: list[str] = []
    archive_script_missing: list[str] = []
    skill_missing: list[str] = []
    root_skill_missing: list[str] = []
    phase_skill_missing: dict[str, list[str]] = {}

    if en_path:
        try:
            en_text = read_text(en_path)
            checked_files.append(EN_POLICY.as_posix())
            try:
                en_text.encode("ascii")
            except UnicodeEncodeError as exc:
                errors.append(f"{EN_POLICY.as_posix()} contains non-ASCII text at character index {exc.start}.")
            en_missing = check_terms("English policy", en_text, EN_REQUIRED_TERMS, errors)
        except UnicodeDecodeError as exc:
            errors.append(f"{EN_POLICY.as_posix()} is not valid UTF-8: {exc}")

    if zh_path:
        try:
            zh_text = read_text(zh_path)
            checked_files.append(ZH_POLICY.as_posix())
            if "\ufffd" in zh_text or "??" in zh_text:
                errors.append(
                    f"{ZH_POLICY.as_posix()} appears to contain mojibake or placeholder question marks; "
                    "read and maintain it as UTF-8 Chinese text."
                )
            zh_missing = check_terms("Chinese policy", zh_text, ZH_REQUIRED_TERMS, errors)
        except UnicodeDecodeError as exc:
            errors.append(f"{ZH_POLICY.as_posix()} is not valid UTF-8: {exc}")

    if registry_path:
        try:
            registry_text = read_text(registry_path)
            checked_files.append(REGISTRY.as_posix())
            entries = parse_registry_entries(registry_text)
            matching = [entry for entry in entries if entry.get("doc_id") == DOC_ID]
            if not matching:
                errors.append(f"docs registry is missing governance doc_id `{DOC_ID}`.")
            else:
                entry = matching[0]
                expected = {
                    "doc_class": "governance",
                    "status": "active",
                    "canonical_path": EN_POLICY.as_posix(),
                    "zh_cn_path": ZH_POLICY.as_posix(),
                }
                for key, value in expected.items():
                    if entry.get(key) != value:
                        errors.append(
                            f"docs registry entry `{DOC_ID}` has wrong {key}: expected `{value}`, got `{entry.get(key)}`."
                        )
        except UnicodeDecodeError as exc:
            errors.append(f"{REGISTRY.as_posix()} is not valid UTF-8: {exc}")

    spec_path = root / ACTIVE_SPEC
    spec_kind = "active_delta"
    if not spec_path.exists():
        spec_path = root / STABLE_SPEC
        spec_kind = "stable"
    if not spec_path.exists():
        errors.append(
            "Missing Comet/OpenSpec/Superpowers spec; expected active delta or stable spec at "
            f"{ACTIVE_SPEC.as_posix()} or {STABLE_SPEC.as_posix()}."
        )
    else:
        try:
            spec_text = read_text(spec_path)
            checked_files.append(str(spec_path.relative_to(root).as_posix()))
            spec_missing = check_terms("OpenSpec capability", spec_text, SPEC_REQUIRED_TERMS, errors)
            info.append(f"Spec source: {spec_kind}")
        except UnicodeDecodeError as exc:
            errors.append(f"{spec_path.relative_to(root).as_posix()} is not valid UTF-8: {exc}")

    implementation_plan_path = require_file(root, IMPLEMENTATION_PLAN, errors)
    if implementation_plan_path:
        try:
            implementation_plan_text = read_text(implementation_plan_path)
            checked_files.append(IMPLEMENTATION_PLAN.as_posix())
            implementation_plan_missing = check_terms(
                "Implementation plan",
                implementation_plan_text,
                IMPLEMENTATION_PLAN_REQUIRED_TERMS,
                errors,
            )
        except UnicodeDecodeError as exc:
            errors.append(f"{IMPLEMENTATION_PLAN.as_posix()} is not valid UTF-8: {exc}")

    implementation_plan_zh_path = require_file(root, IMPLEMENTATION_PLAN_ZH, errors)
    if implementation_plan_zh_path:
        try:
            implementation_plan_zh_text = read_text(implementation_plan_zh_path)
            checked_files.append(IMPLEMENTATION_PLAN_ZH.as_posix())
            if "\ufffd" in implementation_plan_zh_text or "??" in implementation_plan_zh_text:
                errors.append(
                    f"{IMPLEMENTATION_PLAN_ZH.as_posix()} appears to contain mojibake or placeholder question marks; "
                    "read and maintain it as UTF-8 Chinese text."
                )
            implementation_plan_zh_missing = check_terms(
                "Chinese implementation plan",
                implementation_plan_zh_text,
                IMPLEMENTATION_PLAN_ZH_REQUIRED_TERMS,
                errors,
            )
        except UnicodeDecodeError as exc:
            errors.append(f"{IMPLEMENTATION_PLAN_ZH.as_posix()} is not valid UTF-8: {exc}")

    state_script_path = require_file(root, COMET_STATE_SCRIPT, errors)
    if state_script_path:
        state_script_text = read_text(state_script_path)
        checked_files.append(COMET_STATE_SCRIPT.as_posix())
        state_script_missing = check_terms("Comet state script", state_script_text, STATE_SCRIPT_REQUIRED_TERMS, errors)

    guard_script_path = require_file(root, COMET_GUARD_SCRIPT, errors)
    if guard_script_path:
        guard_script_text = read_text(guard_script_path)
        checked_files.append(COMET_GUARD_SCRIPT.as_posix())
        guard_script_missing = check_terms("Comet guard script", guard_script_text, GUARD_SCRIPT_REQUIRED_TERMS, errors)

    validate_script_path = require_file(root, COMET_VALIDATE_SCRIPT, errors)
    if validate_script_path:
        validate_script_text = read_text(validate_script_path)
        checked_files.append(COMET_VALIDATE_SCRIPT.as_posix())
        validate_script_missing = check_terms(
            "Comet YAML validator",
            validate_script_text,
            VALIDATE_SCRIPT_REQUIRED_TERMS,
            errors,
        )

    archive_script_path = require_file(root, COMET_ARCHIVE_SCRIPT, errors)
    if archive_script_path:
        archive_script_text = read_text(archive_script_path)
        checked_files.append(COMET_ARCHIVE_SCRIPT.as_posix())
        archive_script_missing = check_terms("Comet archive script", archive_script_text, ARCHIVE_SCRIPT_REQUIRED_TERMS, errors)

    skill_texts: list[str] = []
    for relative in COMET_SKILL_FILES:
        skill_path = require_file(root, relative, errors)
        if skill_path:
            skill_text = read_text(skill_path)
            skill_texts.append(skill_text)
            checked_files.append(relative.as_posix())
            if relative.as_posix() == ".codex/skills/comet/SKILL.md":
                root_skill_missing = check_terms("Root Comet skill", skill_text, ROOT_SKILL_REQUIRED_TERMS, errors)
            per_file_terms = PHASE_SKILL_REQUIRED_TERMS.get(relative.as_posix())
            if per_file_terms:
                missing = check_terms(f"Comet phase skill {relative.as_posix()}", skill_text, per_file_terms, errors)
                phase_skill_missing[relative.as_posix()] = missing
    if skill_texts:
        skill_missing = check_terms("Comet skills", "\n".join(skill_texts), SKILL_REQUIRED_TERMS, errors)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "openspec_comet_superpowers_policy",
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "checked_files": checked_files,
        "required_terms": {
            "english_policy": EN_REQUIRED_TERMS,
            "chinese_policy": ZH_REQUIRED_TERMS,
            "spec": SPEC_REQUIRED_TERMS,
            "implementation_plan": IMPLEMENTATION_PLAN_REQUIRED_TERMS,
            "implementation_plan_zh": IMPLEMENTATION_PLAN_ZH_REQUIRED_TERMS,
            "state_script": STATE_SCRIPT_REQUIRED_TERMS,
            "guard_script": GUARD_SCRIPT_REQUIRED_TERMS,
            "validate_script": VALIDATE_SCRIPT_REQUIRED_TERMS,
            "archive_script": ARCHIVE_SCRIPT_REQUIRED_TERMS,
            "skills": SKILL_REQUIRED_TERMS,
            "root_skill": ROOT_SKILL_REQUIRED_TERMS,
            "phase_skills": PHASE_SKILL_REQUIRED_TERMS,
        },
        "missing_terms": {
            "english_policy": en_missing,
            "chinese_policy": zh_missing,
            "spec": spec_missing,
            "implementation_plan": implementation_plan_missing,
            "implementation_plan_zh": implementation_plan_zh_missing,
            "state_script": state_script_missing,
            "guard_script": guard_script_missing,
            "validate_script": validate_script_missing,
            "archive_script": archive_script_missing,
            "skills": skill_missing,
            "root_skill": root_skill_missing,
            "phase_skills": phase_skill_missing,
        },
        "counts": {
            "checked_files": len(checked_files),
            "english_terms": len(EN_REQUIRED_TERMS),
            "chinese_terms": len(ZH_REQUIRED_TERMS),
            "spec_terms": len(SPEC_REQUIRED_TERMS),
            "runtime_terms": (
                len(STATE_SCRIPT_REQUIRED_TERMS)
                + len(GUARD_SCRIPT_REQUIRED_TERMS)
                + len(VALIDATE_SCRIPT_REQUIRED_TERMS)
                + len(ARCHIVE_SCRIPT_REQUIRED_TERMS)
                + len(SKILL_REQUIRED_TERMS)
                + len(ROOT_SKILL_REQUIRED_TERMS)
                + sum(len(terms) for terms in PHASE_SKILL_REQUIRED_TERMS.values())
            ),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Comet-controlled OpenSpec + Superpowers governance policy.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if report["ok"]:
            print("OpenSpec Comet/Superpowers policy check passed.")
        else:
            print("OpenSpec Comet/Superpowers policy check failed:")
            for error in report["errors"]:
                print(f"  - {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
