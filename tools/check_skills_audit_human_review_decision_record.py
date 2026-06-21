#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_human_review_decision_record"

MEMORY_DIR = Path("docs_bilingual/memory")
FINAL_SUMMARY = MEMORY_DIR / "skills_usage_audit_30d_summary_2026-06-15-1059.md"

DECISION_RECORD_PATTERNS = (
    "skills_usage_audit_human_review_decision_*.md",
    "skills_usage_audit_review_decision_*.md",
)
CANDIDATE_PATTERNS = (
    "skills_usage_audit_profile_apply_candidate*.md",
    "skills_usage_audit_profile_apply_candidate*.json",
    "skills_profile_candidate*.md",
    "skills_profile_candidate*.json",
)
APPROVED_TO_APPLY_RECEIPT_PATTERNS = (
    "skills_usage_audit_approved_to_apply_*.md",
    "skills_usage_audit_profile_apply_approval_*.md",
)

ALLOWED_OUTCOMES = {
    "summary-reviewed + closed-no-change",
    "summary-reviewed + preview-only candidate",
    "review-pending + continue monitoring",
}
PREVIEW_ONLY_OUTCOME = "summary-reviewed + preview-only candidate"
REVIEW_PENDING_OUTCOME = "review-pending + continue monitoring"
CLOSED_NO_CHANGE_OUTCOME = "summary-reviewed + closed-no-change"

PENDING_SUMMARY_STATES = {"human_review_pending", "review-pending"}
REVIEWED_SUMMARY_STATES = {"summary-reviewed", "summary_reviewed"}
ALLOWED_PENDING_CANDIDATE_STATES = {"not_requested"}
ALLOWED_PREVIEW_CANDIDATE_STATES = {"preview-only", "preview_only", "requested", "candidate_preview_requested"}
ALLOWED_APPLY_STATES_WITHOUT_RECEIPT = {"not_authorized"}
ALLOWED_APPLY_STATES_WITH_RECEIPT = {"not_authorized", "approved-to-apply", "approved_to_apply"}

PLACEHOLDER_VALUES = {"", "none", "null", "todo", "tbd", "n/a", "not_applicable", "未定", "待定"}

WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|private|Temp|tmp|AppData|PythonProject|[^ \t\r\n`'\"]+)")
UNC_PATH_RE = re.compile(r"\\\\[^\\\s]+\\[^ \t\r\n`'\"]+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?i)(?:/home/|/users/|/var/folders/|/tmp/)[^\s`'\"]+")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*(?!\[REDACTED_SECRET\])([^\s,;\"']+)"
)
STANDALONE_TOKEN_RE = re.compile(r"(?i)\b(?:sk-[a-z0-9_-]{8,}|xox[baprs]-[a-z0-9_-]{8,})\b")
RAW_EVIDENCE_LABEL_RE = re.compile(
    r"(?i)\b(raw\s+transcript|transcript\s+excerpt|runtime\s+log\s+row|raw\s+log\s+row|"
    r"warning\s+excerpt|raw\s+warning|thread\s+id|token\s+counter)\b"
)
SAFE_RAW_EVIDENCE_WORDS = ("not retained", "not committed", "none", "redacted", "sanitized", "local-only", "local only")


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
            rf"^\s*[-*]\s*{re.escape(label)}\s*:\s*`([^`]+)`\s*[。；;]?\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_plain_value(text: str, labels: tuple[str, ...]) -> str | None:
    backtick = extract_backtick_value(text, labels)
    if backtick is not None:
        return backtick
    for label in labels:
        pattern = re.compile(
            rf"^\s*[-*]\s*{re.escape(label)}\s*:\s*(.+?)\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip().strip("`").strip()
    return None


def is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().strip("`").lower()
    return normalized in PLACEHOLDER_VALUES


def is_present_note(value: str | None) -> bool:
    return not is_placeholder(value) and len((value or "").strip()) >= 8


def decision_records(root: Path) -> list[Path]:
    records: list[Path] = []
    for pattern in DECISION_RECORD_PATTERNS:
        for path in (root / MEMORY_DIR).glob(pattern):
            if path.name.endswith(".zh-CN.md"):
                continue
            if "template" in path.name.lower():
                continue
            records.append(path)
    return sorted({path for path in records}, key=lambda item: item.name)


def zh_companion(path: Path) -> Path:
    if path.name.endswith(".md"):
        return path.with_name(path.name[:-3] + ".zh-CN.md")
    return path.with_suffix(path.suffix + ".zh-CN.md")


def existing_artifacts(root: Path, patterns: tuple[str, ...]) -> list[str]:
    artifacts: list[Path] = []
    for pattern in patterns:
        artifacts.extend((root / MEMORY_DIR).glob(pattern))
    return sorted({norm(path.relative_to(root)) for path in artifacts})


def extract_outcomes(text: str) -> list[str]:
    explicit = extract_plain_value(
        text,
        (
            "Outcome",
            "Decision outcome",
            "Human review outcome",
            "Final review outcome",
            "Review outcome",
        ),
    )
    mentioned_allowed = [outcome for outcome in sorted(ALLOWED_OUTCOMES) if outcome in text]
    if explicit:
        if explicit in ALLOWED_OUTCOMES:
            return sorted(set([explicit, *mentioned_allowed]))
        # Keep unsupported explicit values visible to the caller by returning a sentinel.
        return [explicit, *mentioned_allowed]
    return mentioned_allowed


def parse_decision_record(text: str) -> dict[str, Any]:
    return {
        "outcomes": extract_outcomes(text),
        "summary_review_state": extract_plain_value(
            text,
            ("Summary review state", "Final 30-day summary state", "Final summary state"),
        ),
        "candidate_generation_state": extract_plain_value(
            text,
            ("Candidate generation state", "Candidate generation"),
        ),
        "profile_apply_state": extract_plain_value(
            text,
            ("Profile apply state", "Profile apply"),
        ),
        "target_profile": extract_plain_value(
            text,
            ("target_profile", "Target profile", "Target profile/module", "Profile target"),
        ),
        "candidate_review_notes": extract_plain_value(
            text,
            ("Candidate review notes", "Candidate review note", "Candidate notes"),
        ),
        "rollback_path_review_notes": extract_plain_value(
            text,
            ("Rollback path review notes", "Rollback path review", "Rollback review notes"),
        ),
        "validation_plan_review_notes": extract_plain_value(
            text,
            ("Validation plan review notes", "Validation plan review", "Validation review notes"),
        ),
        "approved_to_apply_receipt": extract_plain_value(
            text,
            ("approved-to-apply receipt", "Approved-to-apply receipt", "Profile apply approval receipt"),
        ),
    }


def raw_retention_findings(text: str) -> list[str]:
    findings: list[str] = []
    if WINDOWS_PATH_RE.search(text) or UNC_PATH_RE.search(text) or POSIX_PRIVATE_PATH_RE.search(text):
        findings.append("raw_private_path_retained")
    if SECRET_ASSIGNMENT_RE.search(text):
        findings.append("raw_secret_assignment_retained")
    if STANDALONE_TOKEN_RE.search(text):
        findings.append("standalone_secret_token_retained")

    for line_no, line in enumerate(text.splitlines(), start=1):
        if not RAW_EVIDENCE_LABEL_RE.search(line):
            continue
        lowered = line.lower()
        if not any(word in lowered for word in SAFE_RAW_EVIDENCE_WORDS):
            findings.append(f"raw_transcript_or_log_excerpt_retained:line_{line_no}")
    return findings


def validate_record(
    *,
    root: Path,
    record_path: Path | None,
    parsed: dict[str, Any] | None,
    candidate_artifacts: list[str],
    approval_receipts: list[str],
) -> tuple[list[str], list[str], list[str], str]:
    errors: list[str] = []
    warnings: list[str] = []
    open_items: list[str] = []

    if record_path is None or parsed is None:
        open_items.extend(
            [
                "final_human_review_pending",
                "closure_decision_pending",
                "profile_apply_not_authorized",
            ]
        )
        if candidate_artifacts:
            errors.append(
                "profile candidate artifacts exist before any human-review decision record: "
                + ", ".join(candidate_artifacts)
            )
        return errors, warnings, open_items, "no_decision_record"

    if not zh_companion(record_path).exists():
        errors.append(f"{norm(zh_companion(record_path).relative_to(root))}: required Chinese companion is missing.")

    outcomes = parsed.get("outcomes") or []
    if len(outcomes) != 1:
        errors.append(
            "human-review decision record must contain exactly one explicit allowed outcome; "
            f"observed {len(outcomes)} outcomes: {outcomes!r}."
        )
        outcome = "invalid"
    else:
        outcome = outcomes[0]
        if outcome not in ALLOWED_OUTCOMES:
            errors.append(
                f"unsupported human-review decision outcome {outcome!r}; expected one of "
                + ", ".join(sorted(ALLOWED_OUTCOMES))
            )

    summary_state = parsed.get("summary_review_state")
    candidate_state = parsed.get("candidate_generation_state")
    apply_state = parsed.get("profile_apply_state")
    apply_allowed = set(ALLOWED_APPLY_STATES_WITH_RECEIPT if approval_receipts else ALLOWED_APPLY_STATES_WITHOUT_RECEIPT)

    if outcome == REVIEW_PENDING_OUTCOME:
        if summary_state not in PENDING_SUMMARY_STATES:
            errors.append(
                "review-pending decision requires Summary review state to remain human_review_pending/review-pending; "
                f"observed {summary_state!r}."
            )
        if candidate_state not in ALLOWED_PENDING_CANDIDATE_STATES:
            errors.append(
                "review-pending decision requires Candidate generation state to remain not_requested; "
                f"observed {candidate_state!r}."
            )
        if apply_state not in apply_allowed:
            errors.append(
                "review-pending decision requires Profile apply state to remain not_authorized unless a later "
                f"approved-to-apply receipt exists; observed {apply_state!r}."
            )
        if candidate_artifacts:
            errors.append(
                "profile candidate artifacts exist while decision is review-pending: "
                + ", ".join(candidate_artifacts)
            )
        open_items.extend(
            [
                "final_human_review_pending",
                "closure_decision_pending",
                "profile_apply_not_authorized",
            ]
        )
        decision_state = "review_pending_continue_monitoring_recorded"
    elif outcome == CLOSED_NO_CHANGE_OUTCOME:
        if summary_state not in REVIEWED_SUMMARY_STATES:
            errors.append(
                "closed-no-change decision requires Summary review state summary-reviewed in the decision record; "
                f"observed {summary_state!r}."
            )
        if candidate_state not in ALLOWED_PENDING_CANDIDATE_STATES:
            errors.append(
                "closed-no-change decision requires Candidate generation state not_requested; "
                f"observed {candidate_state!r}."
            )
        if apply_state not in apply_allowed:
            errors.append(
                "closed-no-change decision requires Profile apply state to remain not_authorized unless a later "
                f"approved-to-apply receipt exists; observed {apply_state!r}."
            )
        if candidate_artifacts:
            errors.append(
                "profile candidate artifacts exist while decision is closed-no-change: "
                + ", ".join(candidate_artifacts)
            )
        open_items.append("profile_apply_not_authorized")
        decision_state = "summary_reviewed_closed_no_change"
    elif outcome == PREVIEW_ONLY_OUTCOME:
        if summary_state not in REVIEWED_SUMMARY_STATES:
            errors.append(
                "preview-only candidate decision requires Summary review state summary-reviewed in the decision record; "
                f"observed {summary_state!r}."
            )
        if candidate_state not in ALLOWED_PREVIEW_CANDIDATE_STATES:
            errors.append(
                "preview-only candidate decision requires Candidate generation state preview-only/requested; "
                f"observed {candidate_state!r}."
            )
        if is_placeholder(parsed.get("target_profile")):
            errors.append("preview-only candidate decision requires an explicit target_profile.")
        if not is_present_note(parsed.get("candidate_review_notes")):
            errors.append("preview-only candidate decision requires candidate review notes.")
        if not is_present_note(parsed.get("rollback_path_review_notes")):
            errors.append("preview-only candidate decision requires rollback path review notes.")
        if not is_present_note(parsed.get("validation_plan_review_notes")):
            errors.append("preview-only candidate decision requires validation plan review notes.")
        if apply_state not in apply_allowed:
            errors.append(
                "preview-only candidate decision must keep Profile apply state not_authorized unless a later "
                f"approved-to-apply receipt exists; observed {apply_state!r}."
            )
        if not approval_receipts:
            open_items.append("profile_apply_not_authorized")
        decision_state = "summary_reviewed_preview_only_candidate"
    else:
        decision_state = "invalid_decision_record"

    return errors, warnings, open_items, decision_state


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    records = decision_records(root)
    candidate_artifacts = existing_artifacts(root, CANDIDATE_PATTERNS)
    approval_receipts = existing_artifacts(root, APPROVED_TO_APPLY_RECEIPT_PATTERNS)

    if not (root / FINAL_SUMMARY).exists():
        errors.append(f"{norm(FINAL_SUMMARY)}: required final 30-day summary is missing.")

    selected_record: Path | None = None
    parsed: dict[str, Any] | None = None
    raw_findings: list[str] = []

    if len(records) > 1:
        errors.append(
            "multiple canonical human-review decision records found; keep exactly one active decision record: "
            + ", ".join(norm(path.relative_to(root)) for path in records)
        )
    elif len(records) == 1:
        selected_record = records[0]
        text = read_text(selected_record)
        parsed = parse_decision_record(text)
        raw_findings = raw_retention_findings(text)
        for finding in raw_findings:
            errors.append(f"{norm(selected_record.relative_to(root))}: {finding}.")

    validation_errors, validation_warnings, open_items, decision_state = validate_record(
        root=root,
        record_path=selected_record,
        parsed=parsed,
        candidate_artifacts=candidate_artifacts,
        approval_receipts=approval_receipts,
    )
    errors.extend(validation_errors)
    warnings.extend(validation_warnings)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "decision_record_state": decision_state,
        "does_not_mutate_config": True,
        "does_not_edit_plugin_cache": True,
        "does_not_apply_profile": True,
        "evidence_paths": {
            "final_summary": norm(FINAL_SUMMARY),
            "decision_record": norm(selected_record.relative_to(root)) if selected_record else None,
            "decision_record_zh": norm(zh_companion(selected_record).relative_to(root)) if selected_record else None,
            "approval_receipts": approval_receipts,
        },
        "decision_record": parsed or {},
        "candidate_artifacts": candidate_artifacts,
        "raw_retention_findings": raw_findings,
        "open_items": open_items,
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "no_decision_record_is_valid_pending_state": True,
            "allowed_outcomes": sorted(ALLOWED_OUTCOMES),
            "exactly_one_outcome_required_when_record_exists": True,
            "candidate_artifacts_before_summary_reviewed": "blocked",
            "preview_only_candidate_requires_target_profile_and_review_notes": True,
            "profile_apply_requires_later_approved_to_apply_receipt": True,
            "raw_paths_secrets_transcripts_and_log_excerpts_retained": "blocked",
        },
        "counts": {
            "decision_records": len(records),
            "candidate_artifacts": len(candidate_artifacts),
            "approval_receipts": len(approval_receipts),
            "open_items": len(open_items),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify optional Codex Skills usage audit human-review decision records "
            "without generating candidates, applying profiles, or editing user-level config."
        )
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = build_report(Path(args.root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"{CHECK_NAME}: ok ({report['decision_record_state']})")
        for item in report["open_items"]:
            print(f"OPEN: {item}")
    else:
        print(f"{CHECK_NAME}: failed ({report['decision_record_state']})")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
