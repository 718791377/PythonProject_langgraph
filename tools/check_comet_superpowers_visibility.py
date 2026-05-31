#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


CHECK_NAME = "comet_superpowers_visibility"

REQUIRED_TERMS: dict[str, list[str]] = {
    ".codex/skills/comet/SKILL.md": [
        "Superpowers HOW-layer visibility",
        "OpenSpec remains WHAT",
        "Superpowers remains HOW",
        "`superpowers:using-superpowers`",
        "`superpowers:writing-plans`",
        "`superpowers:executing-plans`",
        "`superpowers:test-driven-development`",
        "`superpowers:verification-before-completion`",
        "`superpowers:finishing-a-development-branch`",
        "Skill invocation is HOW-layer procedural evidence only, not native subagent evidence",
    ],
    ".codex/skills/comet-design/SKILL.md": [
        "Superpowers HOW-layer evidence",
        "`superpowers:using-superpowers`",
        "`superpowers:brainstorming`",
        "design document path",
        "not native subagent evidence",
    ],
    ".codex/skills/comet-build/SKILL.md": [
        "Superpowers HOW-layer evidence",
        "`superpowers:using-superpowers`",
        "`superpowers:writing-plans`",
        "`superpowers:executing-plans`",
        "`superpowers:test-driven-development`",
        "`superpowers:verification-before-completion`",
        "selected build_mode",
        "not native subagent evidence",
    ],
    ".codex/skills/comet-verify/SKILL.md": [
        "Superpowers HOW-layer evidence",
        "`superpowers:using-superpowers`",
        "`superpowers:verification-before-completion`",
        "`superpowers:finishing-a-development-branch`",
        "branch handling evidence",
        "not native subagent evidence",
    ],
    "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md": [
        "Comet MUST expose Superpowers HOW-layer evidence",
        "OpenSpec remains the WHAT layer",
        "Superpowers remains the HOW layer",
        "Skill invocation is HOW-layer procedural evidence, not native subagent evidence",
        "`superpowers:using-superpowers`",
        "`superpowers:writing-plans`",
        "`superpowers:executing-plans`",
        "`superpowers:test-driven-development`",
        "`superpowers:verification-before-completion`",
        "`superpowers:finishing-a-development-branch`",
    ],
    "docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md": [
        "Comet 必须显式记录 Superpowers HOW-layer evidence",
        "OpenSpec 仍然是 WHAT layer",
        "Superpowers 仍然是 HOW layer",
        "Skill invocation 是 HOW-layer procedural evidence，不是 native subagent evidence",
        "`superpowers:using-superpowers`",
        "`superpowers:writing-plans`",
        "`superpowers:executing-plans`",
        "`superpowers:test-driven-development`",
        "`superpowers:verification-before-completion`",
        "`superpowers:finishing-a-development-branch`",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def run_repository_check(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    checked_files: list[str] = []
    missing_terms: dict[str, list[str]] = {}

    for relative, terms in REQUIRED_TERMS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"Missing required Comet/Superpowers visibility surface: {relative}")
            missing_terms[relative] = terms
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError as exc:
            errors.append(f"{relative} is not valid UTF-8: {exc}")
            missing_terms[relative] = terms
            continue
        checked_files.append(relative)
        missing = [term for term in terms if term not in text]
        if missing:
            missing_terms[relative] = missing
            for term in missing:
                errors.append(f"{relative} is missing required HOW-layer visibility term: {term}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "checked_files": checked_files,
        "required_terms": REQUIRED_TERMS,
        "missing_terms": missing_terms,
        "counts": {
            "checked_files": len(checked_files),
            "required_surfaces": len(REQUIRED_TERMS),
            "missing_terms": sum(len(items) for items in missing_terms.values()),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Comet Superpowers HOW-layer visibility evidence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = run_repository_check(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print("Comet Superpowers visibility check passed.")
    else:
        print("Comet Superpowers visibility check failed:")
        for error in report["errors"]:
            print(f"  - {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
