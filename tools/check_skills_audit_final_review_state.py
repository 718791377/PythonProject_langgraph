#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_final_review_state"
FINAL_SUMMARY = Path("docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md")
FINAL_SUMMARY_ZH = Path("docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.zh-CN.md")
DECISION_TEMPLATE = Path("docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.md")
DECISION_TEMPLATE_ZH = Path("docs_bilingual/memory/skills_usage_audit_human_review_decision_template_2026-06-15.zh-CN.md")
MEMORY_DIR = Path("docs_bilingual/memory")

PENDING_SUMMARY_STATES = {"human_review_pending", "review-pending"}
REVIEWED_SUMMARY_STATES = {"summary-reviewed", "summary_reviewed"}
ALLOWED_PENDING_CANDIDATE_STATES = {"not_requested"}
ALLOWED_PENDING_APPLY_STATES = {"not_authorized"}
ALLOWED_REVIEWED_OUTCOMES = {
    "summary-reviewed + closed-no-change",
    "summary-reviewed + preview-only candidate",
    "review-pending + continue monitoring",
}


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def latest_path(root: Path, pattern: str) -> Path | None:
    candidates = [
        path
        for path in (root / MEMORY_DIR).glob(pattern)
        if not path.name.endswith(".zh-CN.md")
    ]
    return sorted(candidates, key=lambda item: item.name)[-1] if candidates else None


def extract_backtick_value(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        pattern = re.compile(
            rf"^\s*[-*]\s*{re.escape(label)}\s*:\s*`([^`]+)`\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_decision_outcomes(text: str) -> list[str]:
    outcomes: list[str] = []
    for outcome in sorted(ALLOWED_REVIEWED_OUTCOMES):
        if outcome in text:
            outcomes.append(outcome)
    return outcomes


def existing_candidate_artifacts(root: Path) -> list[str]:
    patterns = (
        "skills_usage_audit_profile_apply_candidate*.md",
        "skills_usage_audit_profile_apply_candidate*.json",
        "skills_profile_candidate*.md",
        "skills_profile_candidate*.json",
    )
    artifacts: list[Path] = []
    for pattern in patterns:
        artifacts.extend((root / MEMORY_DIR).glob(pattern))
    return sorted({norm(path.relative_to(root)) for path in artifacts})


def parse_summary_state(text: str) -> dict[str, Any]:
    return {
        "summary_review_state": extract_backtick_value(
            text,
            (
                "Summary review state",
                "Final 30-day summary state",
                "Final 30-day summary",
            ),
        ),
        "candidate_generation_state": extract_backtick_value(
            text,
            (
                "Candidate generation state",
                "Candidate generation",
            ),
        ),
        "profile_apply_state": extract_backtick_value(
            text,
            (
                "Profile apply state",
                "Profile apply",
            ),
        ),
        "manual_review_required": extract_backtick_value(text, ("Manual review required",)),
        "decision_outcomes": extract_decision_outcomes(text),
    }


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    open_items: list[str] = []

    required_paths = [FINAL_SUMMARY, FINAL_SUMMARY_ZH, DECISION_TEMPLATE, DECISION_TEMPLATE_ZH]
    missing_required = [norm(path) for path in required_paths if not (root / path).exists()]
    for path in missing_required:
        errors.append(f"{path}: required final review evidence file is missing.")

    final_text = read_text(root / FINAL_SUMMARY)
    final_state = parse_summary_state(final_text)

    latest_continuation = latest_path(root, "skills_usage_audit_review_pending_continuation_*.md")
    latest_index = latest_path(root, "skills_usage_audit_evidence_index_*.md")
    continuation_text = read_text(latest_continuation) if latest_continuation else ""
    latest_index_text = read_text(latest_index) if latest_index else ""
    continuation_state = parse_summary_state(continuation_text)
    latest_index_state = parse_summary_state(latest_index_text)

    candidate_artifacts = existing_candidate_artifacts(root)
    summary_state = final_state.get("summary_review_state")
    candidate_state = continuation_state.get("candidate_generation_state") or final_state.get("candidate_generation_state")
    apply_state = continuation_state.get("profile_apply_state") or final_state.get("profile_apply_state")

    decision_state = "unknown"
    if not summary_state:
        errors.append(f"{norm(FINAL_SUMMARY)}: missing Summary review state field.")
    elif summary_state in PENDING_SUMMARY_STATES:
        decision_state = "review_pending_continue_monitoring"
        open_items.extend(
            [
                "final_human_review_pending",
                "closure_decision_pending",
                "profile_apply_not_authorized",
            ]
        )
        if latest_continuation is None:
            errors.append("review-pending continuation record is missing.")
        if candidate_state not in ALLOWED_PENDING_CANDIDATE_STATES:
            errors.append(
                "review-pending state must keep candidate generation at not_requested; "
                f"observed {candidate_state!r}."
            )
        if apply_state not in ALLOWED_PENDING_APPLY_STATES:
            errors.append(
                "review-pending state must keep profile apply at not_authorized; "
                f"observed {apply_state!r}."
            )
        if candidate_artifacts:
            errors.append(
                "profile candidate artifacts exist before summary-reviewed decision: "
                + ", ".join(candidate_artifacts)
            )
    elif summary_state in REVIEWED_SUMMARY_STATES:
        outcomes = final_state.get("decision_outcomes") or []
        decision_state = "summary_reviewed"
        if not outcomes:
            errors.append(
                "summary-reviewed state requires an explicit outcome: "
                + ", ".join(sorted(ALLOWED_REVIEWED_OUTCOMES))
            )
        if apply_state not in ALLOWED_PENDING_APPLY_STATES:
            errors.append(
                "summary-reviewed state still must not authorize profile apply without a later "
                f"approved-to-apply receipt; observed {apply_state!r}."
            )
    else:
        errors.append(
            f"{norm(FINAL_SUMMARY)}: unsupported Summary review state {summary_state!r}; "
            "expected human_review_pending or summary-reviewed."
        )

    if not latest_index:
        warnings.append("No skills usage audit evidence index was found.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "decision_state": decision_state,
        "does_not_mutate_config": True,
        "does_not_edit_plugin_cache": True,
        "does_not_apply_profile": True,
        "evidence_paths": {
            "final_summary": norm(FINAL_SUMMARY),
            "final_summary_zh": norm(FINAL_SUMMARY_ZH),
            "human_review_decision_template": norm(DECISION_TEMPLATE),
            "human_review_decision_template_zh": norm(DECISION_TEMPLATE_ZH),
            "latest_review_pending_continuation": norm(latest_continuation.relative_to(root)) if latest_continuation else None,
            "latest_evidence_index": norm(latest_index.relative_to(root)) if latest_index else None,
        },
        "states": {
            "final_summary": final_state,
            "latest_continuation": continuation_state,
            "latest_evidence_index": latest_index_state,
        },
        "candidate_artifacts": candidate_artifacts,
        "open_items": open_items,
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "final_summary_must_exist": True,
            "human_review_decision_template_must_exist": True,
            "review_pending_requires_continuation_record": True,
            "candidate_generation_before_summary_reviewed": "blocked",
            "profile_apply_requires_later_approved_to_apply": True,
        },
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "open_items": len(open_items),
            "candidate_artifacts": len(candidate_artifacts),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Codex Skills usage audit final-review, closure, candidate, and apply-gate state."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = build_report(Path(args.root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"{CHECK_NAME}: ok ({report['decision_state']})")
        for item in report["open_items"]:
            print(f"OPEN: {item}")
    else:
        print(f"{CHECK_NAME}: failed ({report['decision_state']})")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
