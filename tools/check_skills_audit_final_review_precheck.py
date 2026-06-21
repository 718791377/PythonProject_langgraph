#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_final_review_precheck"

MEMORY_DIR = Path("docs_bilingual/memory")
FINAL_SUMMARY = MEMORY_DIR / "skills_usage_audit_30d_summary_2026-06-15-1059.md"

PENDING_SUMMARY_STATES = {"human_review_pending", "review-pending"}
ALLOWED_PENDING_CANDIDATE_STATES = {"not_requested"}
ALLOWED_PENDING_APPLY_STATES = {"not_authorized"}
ALLOWED_NOISE_REVIEW_STATES = {"review_required"}
ALLOWED_MANUAL_CONFLICT_STATES = {"no_manual_conflict_or_exception_notes"}

PRECHECK_PATTERNS = (
    "skills_usage_audit_final_review_precheck_*.md",
    "skills_usage_audit_review_pending_continuation_*.md",
)

CANDIDATE_PATTERNS = (
    "skills_usage_audit_profile_apply_candidate*.md",
    "skills_usage_audit_profile_apply_candidate*.json",
    "skills_profile_candidate*.md",
    "skills_profile_candidate*.json",
)


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def extract_backtick_value(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        pattern = re.compile(
            rf"^\s*[-*]\s*{re.escape(label)}\s*:\s*`([^`]+)`\s*[。.．.]?\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    return None


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def extract_violation_count(text: str, group: str) -> int | None:
    patterns = (
        rf"field contract reports zero `{re.escape(group)}` violations",
        rf"`{re.escape(group)}` violations? (?:is|are|=|:)\s*`?0`?",
        rf"field contract .*?`{re.escape(group)}`.*?violations? (?:is|are|=|:)\s*`?0`?",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            return 0
    return None


def sortable_name_key(path: Path) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2}-\d{4})", path.name)
    return match.group(1) if match else path.name


def precheck_candidate_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in PRECHECK_PATTERNS:
        candidates = [
            path
            for path in (root / MEMORY_DIR).glob(pattern)
            if not path.name.endswith(".zh-CN.md")
        ]
        paths.extend(sorted(candidates, key=sortable_name_key, reverse=True))
    return paths


def existing_candidate_artifacts(root: Path) -> list[str]:
    artifacts: list[Path] = []
    for pattern in CANDIDATE_PATTERNS:
        artifacts.extend((root / MEMORY_DIR).glob(pattern))
    return sorted({norm(path.relative_to(root)) for path in artifacts})


def parse_final_summary(text: str) -> dict[str, Any]:
    return {
        "summary_review_state": extract_backtick_value(
            text,
            ("Summary review state", "Final 30-day summary state", "Final 30-day summary"),
        ),
        "candidate_generation_state": extract_backtick_value(
            text,
            ("Candidate generation state", "Candidate generation"),
        ),
        "profile_apply_state": extract_backtick_value(
            text,
            ("Profile apply state", "Profile apply"),
        ),
        "noise_review_status": extract_backtick_value(text, ("Noise review status",)),
        "raw_noise_tokens_retained": parse_bool(
            extract_backtick_value(text, ("Raw noise tokens retained",))
        ),
        "manual_conflict_review_status": extract_backtick_value(
            text,
            ("Manual conflict review status", "Manual evidence conflict review status"),
        ),
        "conflict_or_exception_count": parse_int(
            extract_backtick_value(text, ("Conflict or exception count",))
        ),
        "conflict_disposition_required": parse_bool(
            extract_backtick_value(text, ("Conflict disposition required",))
        ),
        "manual_evidence_files_requested": parse_int(
            extract_backtick_value(text, ("Manual evidence files requested",))
        ),
    }


def precheck_evidence_result(root: Path) -> dict[str, Any]:
    candidates = precheck_candidate_paths(root)
    for path in candidates:
        text = read_text(path)
        if not text:
            continue
        noise_count = extract_violation_count(text, "noise_review")
        manual_count = extract_violation_count(text, "manual_evidence")
        has_noise_precheck = bool(
            re.search(r"noise .*?(machine|pre-review|prechecked|pre-review)", text, flags=re.IGNORECASE | re.DOTALL)
            or "Noise false-positive pre-review" in text
        )
        has_manual_precheck = bool(
            re.search(r"manual.*?(machine|pre-review|prechecked|pre-review)", text, flags=re.IGNORECASE | re.DOTALL)
            or "Manual conflict and exception pre-review" in text
        )
        if (
            has_noise_precheck
            and has_manual_precheck
            and noise_count == 0
            and manual_count == 0
            and "Raw noise tokens are not retained" in text
            and "Conflict or exception count: `0`" in text
        ):
            return {
                "path": norm(path.relative_to(root)),
                "found": True,
                "noise_review_machine_prechecked": True,
                "manual_conflict_machine_prechecked": True,
                "noise_review_violation_count": noise_count,
                "manual_evidence_violation_count": manual_count,
            }
    return {
        "path": None,
        "found": False,
        "noise_review_machine_prechecked": False,
        "manual_conflict_machine_prechecked": False,
        "noise_review_violation_count": None,
        "manual_evidence_violation_count": None,
    }


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    open_items: list[str] = [
        "final_human_review_pending",
        "closure_decision_pending",
        "profile_apply_not_authorized",
    ]

    summary_path = root / FINAL_SUMMARY
    final_text = read_text(summary_path)
    if not summary_path.exists():
        errors.append(f"{norm(FINAL_SUMMARY)}: required final summary is missing.")

    final_state = parse_final_summary(final_text)
    candidate_artifacts = existing_candidate_artifacts(root)
    precheck = precheck_evidence_result(root)

    summary_state = final_state.get("summary_review_state")
    if summary_state not in PENDING_SUMMARY_STATES:
        errors.append(
            f"{norm(FINAL_SUMMARY)}: final precheck only supports review-pending summaries; "
            f"observed {summary_state!r}."
        )

    candidate_state = final_state.get("candidate_generation_state")
    if candidate_state not in ALLOWED_PENDING_CANDIDATE_STATES:
        errors.append(
            "final precheck requires candidate generation to remain not_requested; "
            f"observed {candidate_state!r}."
        )

    apply_state = final_state.get("profile_apply_state")
    if apply_state not in ALLOWED_PENDING_APPLY_STATES:
        errors.append(
            "final precheck requires profile apply to remain not_authorized; "
            f"observed {apply_state!r}."
        )

    noise_status = final_state.get("noise_review_status")
    if noise_status not in ALLOWED_NOISE_REVIEW_STATES:
        errors.append(
            "final summary must keep the human-facing noise review item open as review_required; "
            f"observed {noise_status!r}."
        )

    if final_state.get("raw_noise_tokens_retained") is not False:
        errors.append("final summary must state Raw noise tokens retained: `False`.")

    manual_status = final_state.get("manual_conflict_review_status")
    if manual_status not in ALLOWED_MANUAL_CONFLICT_STATES:
        errors.append(
            "manual conflict review status must be no_manual_conflict_or_exception_notes; "
            f"observed {manual_status!r}."
        )

    if final_state.get("conflict_or_exception_count") != 0:
        errors.append(
            "manual conflict precheck requires Conflict or exception count: `0`; "
            f"observed {final_state.get('conflict_or_exception_count')!r}."
        )

    if final_state.get("conflict_disposition_required") is not False:
        errors.append("manual conflict precheck requires Conflict disposition required: `False`.")

    if not precheck["found"]:
        errors.append(
            "no retained sanitized precheck evidence proves zero noise_review and manual_evidence "
            "field-contract violations while keeping the summary human-review pending."
        )

    if candidate_artifacts:
        errors.append(
            "profile candidate artifacts exist before an explicit summary-reviewed decision: "
            + ", ".join(candidate_artifacts)
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "decision_state": "review_pending_continue_monitoring" if not errors else "precheck_failed",
        "does_not_mutate_config": True,
        "does_not_edit_plugin_cache": True,
        "does_not_apply_profile": True,
        "evidence_paths": {
            "final_summary": norm(FINAL_SUMMARY),
            "precheck_evidence": precheck["path"],
        },
        "final_summary": final_state,
        "precheck": precheck,
        "candidate_artifacts": candidate_artifacts,
        "open_items": open_items,
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "precheck_is_machine_evidence_only": True,
            "summary_reviewed_must_remain_human_decision": True,
            "candidate_generation_before_summary_reviewed": "blocked",
            "profile_apply_requires_later_approved_to_apply": True,
            "raw_noise_tokens_retained": False,
            "manual_conflict_or_exception_count": 0,
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
        description=(
            "Verify machine precheck evidence for the Codex Skills usage audit final "
            "noise/manual-conflict review while preserving human-review and apply gates."
        )
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
        print(f"{CHECK_NAME}: failed")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
