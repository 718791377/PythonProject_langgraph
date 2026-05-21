#!/usr/bin/env python3
"""Audit Codex skills/plugin usage without mutating user configuration.

The report is evidence-oriented: it separates strong evidence (explicit skill
announcements, SKILL.md reads, profile helper calls, and budget warnings) from
weak text mentions. It never edits config.toml or plugin cache files.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SKILL_ANNOUNCE_PATTERNS = [
    re.compile(r"使用技能[:：]\s*([^\n\r]+)"),
    re.compile(r"Using skill[s]?[:：]\s*([^\n\r]+)", re.IGNORECASE),
    # Compatibility for older session logs whose Chinese prompt was mojibake in
    # the terminal/log transport. Keep this broad and secondary; extraction still
    # only counts explicit backticked skill names.
    re.compile(r"浣跨敤[^\n\r]{0,40}\s*([^\n\r]+)"),
]
BACKTICK_PATTERN = re.compile(r"`([^`]+)`")
SKILL_PATH_PATTERN = re.compile(r"([A-Z]:\\[^\s\"']*?SKILL\.md)", re.IGNORECASE)
BUDGET_WARNING_PATTERN = re.compile(r"Exceeded skills context budget of 2%", re.IGNORECASE)
OMITTED_PATTERN = re.compile(r"(\d+)\s+additional skills", re.IGNORECASE)
WINDOWS_PATH_PATTERN = re.compile(r"[A-Za-z]:\\[^\s\"'<>|]+")
WINDOWS_FORWARD_PATH_PATTERN = re.compile(r"[A-Za-z]:/[^\s\"'<>|]+")
UNC_PATH_PATTERN = re.compile(r"\\\\[^\s\"'<>|]+(?:\\[^\s\"'<>|]+)+")
POSIX_PRIVATE_PATH_PATTERN = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|]+")
POSIX_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![\w.:/-])/(?!/)[^\s\"'<>|]+")
PRIVATE_PATH_PATTERNS = (
    UNC_PATH_PATTERN,
    WINDOWS_PATH_PATTERN,
    WINDOWS_FORWARD_PATH_PATTERN,
    POSIX_PRIVATE_PATH_PATTERN,
)
ACCESS_TOKEN_PATTERN = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie)\s*[:=]\s*([^\s,;\"']+)")
STANDALONE_TOKEN_PATTERN = re.compile(r"(?i)\b(?:sk-[a-z0-9_-]{6,}|xox[baprs]-[a-z0-9_-]{6,})\b")
REDACTION_MARKERS = ("[REDACTED_PATH]", "[REDACTED_SECRET]")
GENERIC_EXPLICIT_SKILL_NOISE = {
    "a",
    "an",
    "and",
    "as",
    "by",
    "draft",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
EXPLICIT_SKILL_NOISE_TOKEN_LIMIT = 120
EXPLICIT_SKILL_NOISE_SUMMARY_SAMPLE_LIMIT = 10
MANUAL_NOTE_PATH_LIMIT = 300
MANUAL_NOTE_FIELDS = {
    "time",
    "project",
    "task_type",
    "requested_capability",
    "evidence_level",
    "reason",
    "action_taken",
    "restore_or_followup",
}
REQUIRED_MANUAL_NOTE_FIELDS = {
    "time",
    "project",
    "task_type",
    "requested_capability",
    "evidence_level",
    "reason",
    "action_taken",
}
VALID_MANUAL_EVIDENCE_LEVELS = {"medium", "exception", "noise_removed"}
VALID_MANUAL_ACTIONS = {"none", "soft-load", "preview", "approved hard-load exception"}
REQUIRED_REPORT_FIELDS = {
    "schema_version",
    "generated_at",
    "audit_state",
    "audit_window",
    "safety",
    "config_summary",
    "inventory_summary",
    "log_evidence",
    "warning_triage",
    "session_evidence",
    "manual_evidence",
    "noise_review",
    "script_capability_boundaries",
    "module_evidence",
    "decision_recommendation",
    "cadence_review",
    "output_retention",
    "precommit_update_archive",
    "runtime_paths",
    "recommendations",
}
REQUIRED_REPORT_FIELD_TYPES = {
    "audit_state": dict,
    "audit_window": dict,
    "safety": dict,
    "config_summary": dict,
    "inventory_summary": dict,
    "log_evidence": dict,
    "warning_triage": dict,
    "session_evidence": dict,
    "manual_evidence": dict,
    "noise_review": dict,
    "script_capability_boundaries": dict,
    "module_evidence": list,
    "decision_recommendation": dict,
    "cadence_review": dict,
    "output_retention": dict,
    "precommit_update_archive": dict,
    "runtime_paths": dict,
    "recommendations": list,
}
REQUIRED_DECISION_RECOMMENDATION_FIELDS = {
    "status",
    "policy",
    "profile_apply_allowed",
    "buckets",
    "bucket_counts",
}
REQUIRED_DECISION_RECOMMENDATION_FIELD_TYPES = {
    "status": str,
    "policy": str,
    "profile_apply_allowed": bool,
    "buckets": dict,
    "bucket_counts": dict,
}
REQUIRED_DECISION_BUCKET_NAMES = (
    "profile_review_candidates",
    "on_demand_soft_load",
    "manual_review_medium_or_weak",
    "dormant_restorable",
)
REQUIRED_MODULE_EVIDENCE_FIELDS = {
    "module",
    "plugins",
    "strong_helper_calls",
    "strong_skill_path_reads",
    "strong_total",
    "default_candidate_threshold",
    "mapped_tool_call_mentions",
    "mapped_tool_call_policy",
    "medium_evidence_rationale",
    "weak_plugin_mentions",
    "cross_project_utility",
    "recommendation",
}
REQUIRED_MODULE_EVIDENCE_FIELD_TYPES = {
    "module": str,
    "plugins": list,
    "strong_helper_calls": int,
    "strong_skill_path_reads": int,
    "strong_total": int,
    "default_candidate_threshold": int,
    "mapped_tool_call_mentions": int,
    "mapped_tool_call_policy": str,
    "medium_evidence_rationale": str,
    "weak_plugin_mentions": int,
    "cross_project_utility": str,
    "recommendation": str,
}
MODULE_EVIDENCE_NONNEGATIVE_INT_FIELDS = (
    "strong_helper_calls",
    "strong_skill_path_reads",
    "strong_total",
    "mapped_tool_call_mentions",
    "weak_plugin_mentions",
)
VALID_MODULE_EVIDENCE_RECOMMENDATIONS = {
    "candidate_for_project_or_default_profile_review",
    "keep_module_on_demand_and_continue_audit",
    "mentioned_only_do_not_apply_without_strong_evidence",
    "no_recent_evidence_keep_dormant_not_deleted",
}
VALID_MEDIUM_EVIDENCE_RATIONALES = {
    "mapped_tool_calls_present_manual_review_required",
    "no_mapped_tool_call_medium_evidence",
}
MODULE_EVIDENCE_MAPPED_TOOL_POLICY = "medium_evidence_only_not_counted_as_strong_evidence"
TOOL_CALL_PLUGIN_ALIASES = {
    # These are stable local tool surfaces whose invocation name does not
    # always include the plugin display name. They remain medium evidence only:
    # a tool call can prove task affinity, not default-profile eligibility.
    "Browser": (
        "mcp__chrome_devtools__",
        "mcp__cdp_bridge__",
    ),
    "Cloudflare": (
        "mcp__cloudflare_api__",
    ),
}
TOOL_CALL_MODULE_ALIASES = {
    # Pencil is a design/canvas surface rather than a native plugin skill, so
    # map it to the creative module for human review instead of claiming Canva
    # or Figma plugin usage.
    "creative-content": (
        "mcp__pencil__",
    ),
}


def stable_tool_call_alias_registry() -> dict[str, Any]:
    """Return the stable alias registry exposed in reports for human review."""
    return {
        "policy": "stable_aliases_are_medium_evidence_only_and_never_profile_apply_evidence",
        "evidence_level": "medium",
        "counts_as_strong_evidence": False,
        "plugin_aliases": {plugin: list(aliases) for plugin, aliases in sorted(TOOL_CALL_PLUGIN_ALIASES.items())},
        "module_aliases": {module: list(aliases) for module, aliases in sorted(TOOL_CALL_MODULE_ALIASES.items())},
    }
REQUIRED_NOISE_REVIEW_FIELDS = {
    "status",
    "explicit_skill_noise_removed",
    "strong_evidence_policy",
    "raw_noise_tokens_retained",
    "max_noise_token_length",
    "token_privacy_policy",
}
REQUIRED_NOISE_REVIEW_FIELD_TYPES = {
    "status": str,
    "explicit_skill_noise_removed": dict,
    "strong_evidence_policy": str,
    "raw_noise_tokens_retained": bool,
    "max_noise_token_length": int,
    "token_privacy_policy": str,
}
REQUIRED_AUDIT_STATE_FIELDS = {
    "state",
    "reason",
    "next_action",
    "profile_apply_allowed",
}
REQUIRED_AUDIT_STATE_FIELD_TYPES = {
    "state": str,
    "reason": str,
    "next_action": str,
    "profile_apply_allowed": bool,
}
VALID_AUDIT_STATES = {
    "planned",
    "running",
    "paused",
    "ready-for-summary",
    "summary-reviewed",
    "apply-candidate",
    "closed-no-change",
    "closed-with-candidate",
}
CANDIDATE_READY_AUDIT_STATES = {
    "summary-reviewed",
    "apply-candidate",
    "closed-with-candidate",
}
REQUIRED_PROFILE_APPLY_CANDIDATE_FIELDS = {
    "schema_version",
    "record_type",
    "candidate_id",
    "generated_at",
    "source_reports",
    "source_reports_privacy",
    "candidate_generation_gate",
    "current_profile",
    "target_profile",
    "plugin_diff",
    "evidence_basis",
    "risk_review",
    "rollback_path",
    "validation_plan",
    "approval_state",
    "mutates_config",
    "edits_plugin_cache",
    "hard_load_apply_performed",
    "explicit_authorization_required_for_apply",
    "ordinary_continue_or_generic_confirmation_is_not_apply_authorization",
}
REQUIRED_PROFILE_APPLY_CANDIDATE_FIELD_TYPES = {
    "schema_version": int,
    "record_type": str,
    "candidate_id": str,
    "generated_at": str,
    "source_reports": dict,
    "source_reports_privacy": dict,
    "candidate_generation_gate": dict,
    "current_profile": dict,
    "target_profile": dict,
    "plugin_diff": dict,
    "evidence_basis": dict,
    "risk_review": dict,
    "rollback_path": dict,
    "validation_plan": list,
    "approval_state": str,
    "mutates_config": bool,
    "edits_plugin_cache": bool,
    "hard_load_apply_performed": bool,
    "explicit_authorization_required_for_apply": bool,
    "ordinary_continue_or_generic_confirmation_is_not_apply_authorization": bool,
}
PROFILE_APPLY_CANDIDATE_PREVIEW_APPROVAL_STATE = "preview-only"
AUDIT_STATE_BLOCKER_FIELDS = (
    "close_blockers",
    "candidate_blockers",
    "summary_review_blockers",
    "pause_blockers",
    "warning_triage_blockers",
)
REQUIRED_WARNING_TRIAGE_FIELDS = {
    "requested",
    "status",
    "blockers",
    "window_policy",
    "window_ok",
    "budget_warning_count",
    "skipped_loading_count",
    "recent_skipped_loading_samples",
    "recent_skipped_loading_sample_excerpts",
    "skipped_loading_review",
    "recommended_action",
}
REQUIRED_WARNING_TRIAGE_FIELD_TYPES = {
    "requested": bool,
    "status": str,
    "blockers": list,
    "window_policy": str,
    "window_ok": bool,
    "budget_warning_count": int,
    "skipped_loading_count": int,
    "recent_skipped_loading_samples": int,
    "recent_skipped_loading_sample_excerpts": list,
    "skipped_loading_review": str,
    "recommended_action": str,
}
VALID_WARNING_TRIAGE_STATUSES = {
    "not_requested",
    "blocked",
    "log_source_unavailable",
    "warning_found",
    "no_warning_found_in_triage_window",
}
WARNING_TRIAGE_WINDOW_POLICY = "use_days_1_or_since_for_warning_triage"
VALID_WARNING_TRIAGE_SKIPPED_LOADING_REVIEWS = {
    "record_source_and_do_not_edit_vendor_cache_without_authorization",
    "none",
}
VALID_WARNING_TRIAGE_BLOCKERS = {
    "warning_triage_window_not_narrow",
}
WARNING_TRIAGE_NON_NEGATIVE_INTEGER_FIELDS = (
    "budget_warning_count",
    "skipped_loading_count",
    "recent_skipped_loading_samples",
)
REQUIRED_CADENCE_REVIEW_FIELDS = {
    "late_run",
    "missed_weekly_runs",
    "weekly_report_review",
}
REQUIRED_CADENCE_REVIEW_FIELD_TYPES = {
    "late_run": bool,
    "weekly_report_review": str,
}
REQUIRED_MANUAL_EVIDENCE_FIELDS = {
    "valid_note_count",
    "raw_notes_retained",
    "source_paths_retained",
    "max_path_length",
    "path_privacy_policy",
    "conflict_review",
}
REQUIRED_MANUAL_EVIDENCE_FIELD_TYPES = {
    "valid_note_count": int,
    "raw_notes_retained": bool,
    "source_paths_retained": bool,
    "max_path_length": int,
    "path_privacy_policy": str,
    "conflict_review": dict,
}
REQUIRED_MANUAL_CONFLICT_REVIEW_FIELDS = {
    "status",
    "policy",
    "conflict_or_exception_count",
    "disposition_required",
    "disposition",
}
REQUIRED_MANUAL_CONFLICT_REVIEW_FIELD_TYPES = {
    "status": str,
    "policy": str,
    "conflict_or_exception_count": int,
    "disposition_required": bool,
    "disposition": str,
}
REQUIRED_SCRIPT_CAPABILITY_FIELDS = {
    "policy",
    "reliable_coverage",
    "human_review_required_for",
    "enhancement_triggers",
    "stable_tool_call_alias_registry",
}
REQUIRED_SCRIPT_CAPABILITY_FIELD_TYPES = {
    "policy": str,
    "reliable_coverage": list,
    "human_review_required_for": list,
    "enhancement_triggers": list,
    "stable_tool_call_alias_registry": dict,
}
REQUIRED_STABLE_TOOL_CALL_ALIAS_REGISTRY_FIELDS = {
    "policy",
    "evidence_level",
    "counts_as_strong_evidence",
    "plugin_aliases",
    "module_aliases",
}
REQUIRED_STABLE_TOOL_CALL_ALIAS_REGISTRY_FIELD_TYPES = {
    "policy": str,
    "evidence_level": str,
    "counts_as_strong_evidence": bool,
    "plugin_aliases": dict,
    "module_aliases": dict,
}
REQUIRED_OUTPUT_RETENTION_FIELDS = {
    "status",
    "ok",
    "checker",
    "tmp_outputs_local_only",
    "raw_audit_json_local_only",
    "long_term_evidence_format",
    "violation_count",
}
REQUIRED_OUTPUT_RETENTION_FIELD_TYPES = {
    "status": str,
    "ok": bool,
    "checker": str,
    "tmp_outputs_local_only": bool,
    "raw_audit_json_local_only": bool,
    "long_term_evidence_format": str,
    "violation_count": int,
}
REQUIRED_PRECOMMIT_UPDATE_ARCHIVE_FIELDS = {
    "status",
    "ok",
    "checker",
    "before_local_git_commit",
    "review_existing_files_for_required_updates",
    "archive_completed_openspec_changes_before_commit",
    "error_count",
    "warning_count",
    "changed_path_count",
    "active_change_review_count",
}
REQUIRED_PRECOMMIT_UPDATE_ARCHIVE_FIELD_TYPES = {
    "status": str,
    "ok": bool,
    "checker": str,
    "before_local_git_commit": bool,
    "review_existing_files_for_required_updates": bool,
    "archive_completed_openspec_changes_before_commit": bool,
    "error_count": int,
    "warning_count": int,
    "changed_path_count": int,
    "active_change_review_count": int,
}
REQUIRED_RUNTIME_PATH_FIELDS = {
    "root",
    "codex_home",
    "config_path",
    "root_kind",
    "codex_home_kind",
    "config_path_kind",
    "raw_paths_retained",
    "privacy_policy",
}
REQUIRED_RUNTIME_PATH_FIELD_TYPES = {
    "root": str,
    "codex_home": str,
    "config_path": str,
    "root_kind": str,
    "codex_home_kind": str,
    "config_path_kind": str,
    "raw_paths_retained": bool,
    "privacy_policy": str,
}


def emit_stdout(text: str) -> None:
    """Write text to stdout safely on non-UTF-8 Windows consoles."""
    try:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe = text.encode(encoding, errors="backslashreplace").decode(encoding, errors="replace")
        sys.stdout.write(safe)
        if not safe.endswith("\n"):
            sys.stdout.write("\n")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def parse_since(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def build_output_retention_status(root: Path) -> dict[str, Any]:
    """Expose the repository audit-output retention gate in each audit report."""
    checker = root / "tools" / "check_skills_audit_output_retention.py"
    relative_checker = "tools/check_skills_audit_output_retention.py"
    if not checker.exists():
        return {
            "status": "unavailable",
            "ok": False,
            "checker": relative_checker,
            "tmp_outputs_local_only": False,
            "raw_audit_json_local_only": False,
            "long_term_evidence_format": "unknown",
            "violation_count": 0,
            "blockers": ["checker_missing"],
        }
    try:
        spec = importlib.util.spec_from_file_location("check_skills_audit_output_retention", checker)
        if spec is None or spec.loader is None:
            raise RuntimeError("checker_import_spec_unavailable")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        raw_report = module.build_report(root)
    except Exception as exc:  # pragma: no cover - defensive guard for checker import/runtime drift.
        return {
            "status": "unavailable",
            "ok": False,
            "checker": relative_checker,
            "tmp_outputs_local_only": False,
            "raw_audit_json_local_only": False,
            "long_term_evidence_format": "unknown",
            "violation_count": 0,
            "blockers": [f"checker_unavailable:{type(exc).__name__}"],
        }
    policy = raw_report.get("policy", {}) if isinstance(raw_report, dict) else {}
    violations = raw_report.get("violations", []) if isinstance(raw_report, dict) else []
    ok = bool(raw_report.get("ok")) if isinstance(raw_report, dict) else False
    return {
        "status": "passed" if ok else "failed",
        "ok": ok,
        "checker": relative_checker,
        "tmp_outputs_local_only": policy.get("tmp_outputs_local_only") is True,
        "raw_audit_json_local_only": policy.get("raw_audit_json_local_only") is True,
        "long_term_evidence_format": str(policy.get("long_term_evidence_format") or "unknown"),
        "violation_count": len(violations) if isinstance(violations, list) else 0,
        "violation_reasons": sorted(
            {
                str(item.get("reason"))
                for item in violations
                if isinstance(item, dict) and item.get("reason")
            }
        ),
    }


def build_precommit_update_archive_status(root: Path) -> dict[str, Any]:
    """Expose the pre-commit existing-file update/archive gate in each audit report."""
    checker = root / "tools" / "check_precommit_update_archive.py"
    relative_checker = "tools/check_precommit_update_archive.py"
    if not checker.exists():
        return {
            "status": "unavailable",
            "ok": False,
            "checker": relative_checker,
            "before_local_git_commit": False,
            "review_existing_files_for_required_updates": False,
            "archive_completed_openspec_changes_before_commit": False,
            "error_count": 0,
            "warning_count": 0,
            "changed_path_count": 0,
            "active_change_review_count": 0,
            "blockers": ["checker_missing"],
        }
    try:
        spec = importlib.util.spec_from_file_location("check_precommit_update_archive", checker)
        if spec is None or spec.loader is None:
            raise RuntimeError("checker_import_spec_unavailable")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        raw_report = module.check(root)
    except Exception as exc:  # pragma: no cover - defensive guard for checker import/runtime drift.
        return {
            "status": "unavailable",
            "ok": False,
            "checker": relative_checker,
            "before_local_git_commit": False,
            "review_existing_files_for_required_updates": False,
            "archive_completed_openspec_changes_before_commit": False,
            "error_count": 0,
            "warning_count": 0,
            "changed_path_count": 0,
            "active_change_review_count": 0,
            "blockers": [f"checker_unavailable:{type(exc).__name__}"],
        }
    policy = raw_report.get("policy", {}) if isinstance(raw_report, dict) else {}
    counts = raw_report.get("counts", {}) if isinstance(raw_report, dict) else {}
    errors = raw_report.get("errors", []) if isinstance(raw_report, dict) else []
    warnings = raw_report.get("warnings", []) if isinstance(raw_report, dict) else []
    ok = bool(raw_report.get("ok")) if isinstance(raw_report, dict) else False
    return {
        "status": "passed" if ok else "failed",
        "ok": ok,
        "checker": relative_checker,
        "before_local_git_commit": policy.get("before_local_git_commit") is True,
        "review_existing_files_for_required_updates": policy.get("review_existing_files_for_required_updates") is True,
        "archive_completed_openspec_changes_before_commit": (
            policy.get("archive_completed_openspec_changes_before_commit") is True
        ),
        "error_count": len(errors) if isinstance(errors, list) else int(counts.get("errors") or 0),
        "warning_count": len(warnings) if isinstance(warnings, list) else int(counts.get("warnings") or 0),
        "changed_path_count": int(counts.get("changed_paths") or 0),
        "active_change_review_count": int(counts.get("active_change_reviews") or 0),
        "error_reasons": [str(error)[:240] for error in errors[:10]] if isinstance(errors, list) else [],
    }


def truncate_preserving_redaction_markers(text: str, limit: int) -> str:
    """Truncate text without leaving an incomplete redaction marker fragment."""
    if len(text) <= limit:
        return text
    truncated = text[:limit]
    for marker in REDACTION_MARKERS:
        for prefix_length in range(1, len(marker)):
            prefix = marker[:prefix_length]
            suffix = marker[prefix_length:]
            if truncated.endswith(prefix) and text[limit : limit + len(suffix)] == suffix:
                truncated = truncated[: -prefix_length] + marker
                break
    return truncated.rstrip() + "[truncated]"


def sanitize_log_excerpt(text: str, limit: int = 500) -> str:
    sanitized = str(text)
    for pattern in PRIVATE_PATH_PATTERNS:
        sanitized = pattern.sub("[REDACTED_PATH]", sanitized)
    sanitized = ACCESS_TOKEN_PATTERN.sub(lambda m: m.group(0).replace(m.group(1), "[REDACTED_SECRET]"), sanitized)
    sanitized = STANDALONE_TOKEN_PATTERN.sub("[REDACTED_SECRET]", sanitized)
    return truncate_preserving_redaction_markers(sanitized, limit)


def sanitize_manual_value(value: str, limit: int = 300) -> str:
    return sanitize_log_excerpt(value.strip(), limit=limit)


def sanitize_retained_path(value: str | None, limit: int = MANUAL_NOTE_PATH_LIMIT) -> str | None:
    if not value:
        return None
    raw_value = str(value)
    sanitized = sanitize_log_excerpt(raw_value, limit=limit)
    if "[REDACTED_PATH]" in sanitized:
        return sanitized
    if POSIX_ABSOLUTE_PATH_PATTERN.search(raw_value):
        return "[REDACTED_PATH]"
    return sanitized


def sanitize_runtime_path(path: Path, *, repo_root: Path, codex_home: Path) -> str:
    """Return a stable placeholder for runtime paths retained in audit reports."""
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        relative = resolved.relative_to(codex_home.resolve())
        tail = relative.as_posix()
        return "[CODEX_HOME]" if not tail or tail == "." else f"[CODEX_HOME]/{tail}"
    except Exception:
        pass
    try:
        relative = resolved.relative_to(repo_root.resolve())
        tail = relative.as_posix()
        return "[REPO_ROOT]" if not tail or tail == "." else f"[REPO_ROOT]/{tail}"
    except Exception:
        pass
    return sanitize_retained_path(str(path)) or "[REDACTED_PATH]"


def build_runtime_paths(root: Path, codex_home: Path) -> dict[str, Any]:
    """Expose runtime path categories without retaining private absolute paths."""
    config_path = codex_home / "config.toml"
    return {
        "root": sanitize_runtime_path(root, repo_root=root, codex_home=codex_home),
        "codex_home": sanitize_runtime_path(codex_home, repo_root=root, codex_home=codex_home),
        "config_path": sanitize_runtime_path(config_path, repo_root=root, codex_home=codex_home),
        "root_kind": "repo_root",
        "codex_home_kind": "user_codex_home",
        "config_path_kind": "user_codex_config",
        "raw_paths_retained": False,
        "privacy_policy": "runtime_paths_are_kind_labels_and_placeholders_no_raw_user_paths",
    }


def sanitize_explicit_skill_noise_token(value: str) -> str:
    """Sanitize and bound rejected explicit-skill tokens before report retention."""
    sanitized = sanitize_log_excerpt(str(value), limit=EXPLICIT_SKILL_NOISE_TOKEN_LIMIT * 4)
    sanitized = (
        sanitized.replace("\\r", " ")
        .replace("\\n", " ")
        .replace("\r", " ")
        .replace("\n", " ")
    )
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    if len(sanitized) > EXPLICIT_SKILL_NOISE_TOKEN_LIMIT:
        sanitized = sanitized[:EXPLICIT_SKILL_NOISE_TOKEN_LIMIT].rstrip() + "[truncated]"
    return sanitized or "[EMPTY_NOISE_TOKEN]"


def inline_code(value: str) -> str:
    """Render short sanitized values as Markdown inline code without leaking raw backticks."""
    return "`" + str(value).replace("`", "'") + "`"


def format_noise_token_samples(removed_noise: Any) -> str:
    """Return a bounded sanitized sample list for removed explicit-skill noise tokens."""
    if not isinstance(removed_noise, dict) or not removed_noise:
        return inline_code("none")

    def sortable_count(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    sorted_items = sorted(
        removed_noise.items(),
        key=lambda item: (-sortable_count(item[1]), sanitize_explicit_skill_noise_token(str(item[0])).lower()),
    )
    samples = [
        inline_code(sanitize_explicit_skill_noise_token(str(token)))
        for token, _count in sorted_items[:EXPLICIT_SKILL_NOISE_SUMMARY_SAMPLE_LIMIT]
    ]
    if len(sorted_items) > EXPLICIT_SKILL_NOISE_SUMMARY_SAMPLE_LIMIT:
        remaining = len(sorted_items) - EXPLICIT_SKILL_NOISE_SUMMARY_SAMPLE_LIMIT
        samples.append(inline_code(f"+{remaining} more"))
    return ", ".join(samples)


def bounded_inline_list(values: list[str], *, limit: int = 12) -> str:
    """Render bounded Markdown inline-code lists for human review summaries."""
    cleaned = [str(value) for value in values if value]
    if not cleaned:
        return inline_code("none")
    samples = [inline_code(value) for value in cleaned[:limit]]
    if len(cleaned) > limit:
        samples.append(inline_code(f"+{len(cleaned) - limit} more"))
    return ", ".join(samples)


def format_alias_targets_for_human(targets: dict[str, Any], *, limit: int = 4) -> str:
    """Render stable tool-call alias targets for bounded human stdout."""
    if not isinstance(targets, dict) or not targets:
        return "none"
    parts: list[str] = []
    for target, aliases in sorted(targets.items()):
        alias_values = [str(alias) for alias in (aliases if isinstance(aliases, list) else []) if alias]
        if alias_values:
            parts.append(f"{target}={', '.join(alias_values[:limit])}")
    if not parts:
        return "none"
    shown = parts[:limit]
    if len(parts) > limit:
        shown.append(f"+{len(parts) - limit} more")
    return "; ".join(shown)


def build_decision_recommendation(
    module_evidence: list[dict[str, Any]],
    warning_severity: dict[str, Any],
    audit_state: dict[str, Any],
) -> dict[str, Any]:
    """Build advisory, non-mutating decision buckets from module evidence."""
    buckets: dict[str, list[str]] = {
        "profile_review_candidates": [],
        "on_demand_soft_load": [],
        "manual_review_medium_or_weak": [],
        "dormant_restorable": [],
    }
    for row in module_evidence:
        module = str(row.get("module") or "").strip()
        if not module:
            continue
        recommendation = str(row.get("recommendation") or "")
        if recommendation == "candidate_for_project_or_default_profile_review":
            buckets["profile_review_candidates"].append(module)
        elif recommendation == "keep_module_on_demand_and_continue_audit":
            buckets["on_demand_soft_load"].append(module)
        elif (
            recommendation == "mentioned_only_do_not_apply_without_strong_evidence"
            or int(row.get("mapped_tool_call_mentions") or 0) > 0
        ):
            buckets["manual_review_medium_or_weak"].append(module)
        else:
            buckets["dormant_restorable"].append(module)
    for modules in buckets.values():
        modules.sort()
    return {
        "status": "advisory_only_no_profile_apply",
        "policy": "decision_buckets_are_review_inputs_and_never_apply_profiles",
        "warning_pressure": warning_severity.get("level"),
        "audit_state": audit_state.get("state"),
        "next_action": audit_state.get("next_action"),
        "profile_apply_allowed": False,
        "buckets": buckets,
        "bucket_counts": {name: len(modules) for name, modules in buckets.items()},
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def parse_manual_note_blocks(text: str) -> list[dict[str, str]]:
    """Parse sanitized Markdown manual-note blocks made of `field: value` lines."""
    notes: list[dict[str, str]] = []
    current: dict[str, str] = {}
    field_re = re.compile(r"^\s*[-*]?\s*`?([A-Za-z_]+)`?\s*:\s*(.*?)\s*$")
    for raw in text.splitlines() + [""]:
        match = field_re.match(raw)
        if not match:
            if current:
                notes.append(current)
                current = {}
            continue
        key = match.group(1)
        if key not in MANUAL_NOTE_FIELDS:
            continue
        current[key] = sanitize_manual_value(match.group(2))
    return notes


def build_manual_conflict_review(notes: list[dict[str, str]]) -> dict[str, Any]:
    conflict_or_exception_notes = [
        note
        for note in notes
        if note.get("evidence_level") == "exception" or note.get("action_taken") == "approved hard-load exception"
    ]
    conflict_or_exception_count = len(conflict_or_exception_notes)
    return {
        "status": (
            "manual_conflict_or_exception_review_required"
            if conflict_or_exception_count
            else "no_manual_conflict_or_exception_notes"
        ),
        "policy": "manual_notes_do_not_override_script_evidence",
        "conflict_or_exception_count": conflict_or_exception_count,
        "disposition_required": bool(conflict_or_exception_count),
        "disposition": (
            "list_conflict_and_disposition_in_30_day_summary_before_profile_decision"
            if conflict_or_exception_count
            else "none"
        ),
    }


def collect_manual_notes(paths: list[str]) -> dict[str, Any]:
    notes: list[dict[str, str]] = []
    invalid: list[dict[str, Any]] = []
    files_read = 0
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            invalid.append({"path": sanitize_retained_path(raw_path), "reason": "missing_file"})
            continue
        files_read += 1
        parsed = parse_manual_note_blocks(path.read_text(encoding="utf-8", errors="replace"))
        for index, note in enumerate(parsed, start=1):
            missing = sorted(REQUIRED_MANUAL_NOTE_FIELDS - set(note))
            invalid_values: list[str] = []
            if note.get("evidence_level") and note["evidence_level"] not in VALID_MANUAL_EVIDENCE_LEVELS:
                invalid_values.append("evidence_level")
            if note.get("action_taken") and note["action_taken"] not in VALID_MANUAL_ACTIONS:
                invalid_values.append("action_taken")
            if missing or invalid_values:
                invalid.append(
                    {
                        "path": sanitize_retained_path(str(path)),
                        "note_index": index,
                        "missing_fields": missing,
                        "invalid_fields": invalid_values,
                    }
                )
                continue
            notes.append(note)
    counts_by_level = Counter(note["evidence_level"] for note in notes)
    counts_by_action = Counter(note["action_taken"] for note in notes)
    conflict_review = build_manual_conflict_review(notes)
    return {
        "files_requested": len(paths),
        "files_read": files_read,
        "notes": notes,
        "valid_note_count": len(notes),
        "invalid_notes": invalid,
        "counts_by_evidence_level": dict(counts_by_level),
        "counts_by_action": dict(counts_by_action),
        "raw_notes_retained": False,
        "source_paths_retained": False,
        "max_path_length": MANUAL_NOTE_PATH_LIMIT,
        "privacy_policy": "manual_notes_are_sanitized_markdown_fields_only_no_raw_transcripts",
        "path_privacy_policy": "manual_note_source_paths_are_redacted_and_bounded_before_report_retention",
        "conflict_review": conflict_review,
    }


def parse_plugin_config(config_path: Path) -> dict[str, bool | None]:
    """Parse [plugins."Name"] enabled values using a small TOML subset."""
    if not config_path.exists():
        return {}
    current: str | None = None
    plugins: dict[str, bool | None] = {}
    section_re = re.compile(r'^\s*\[plugins\."(.+)"\]\s*$')
    enabled_re = re.compile(r"^\s*enabled\s*=\s*(true|false)\s*(?:#.*)?$", re.IGNORECASE)
    for raw in config_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        section_match = section_re.match(raw)
        if section_match:
            current = section_match.group(1)
            plugins.setdefault(current, None)
            continue
        if raw.lstrip().startswith("["):
            current = None
            continue
        if current:
            enabled_match = enabled_re.match(raw)
            if enabled_match:
                plugins[current] = enabled_match.group(1).lower() == "true"
    return plugins


def collect_inventory_counts(codex_home: Path, repo_root: Path) -> dict[str, int]:
    user_skills = list((codex_home / "skills").rglob("SKILL.md")) if (codex_home / "skills").exists() else []
    repo_skills = list((repo_root / ".codex" / "skills").rglob("SKILL.md")) if (repo_root / ".codex" / "skills").exists() else []
    plugin_skills = list((codex_home / "plugins" / "cache").rglob("SKILL.md")) if (codex_home / "plugins" / "cache").exists() else []
    return {
        "user_skills": len(user_skills),
        "repo_skills": len(repo_skills),
        "plugin_skills": len(plugin_skills),
        "total_skills": len(user_skills) + len(repo_skills) + len(plugin_skills),
    }


def normalize_skill_path(path_text: str, codex_home: Path, repo_root: Path) -> str:
    normalized = path_text.replace("\\\\", "\\")
    parts = Path(normalized).parts
    lower_parts = [part.lower() for part in parts]
    try:
        plugins_idx = lower_parts.index("plugins")
        cache_idx = plugins_idx + 1
        if cache_idx < len(parts) and lower_parts[cache_idx] == "cache":
            tail = list(parts[cache_idx + 1 :])
            # openai-curated/<plugin>/<version>/skills/<...>/SKILL.md
            if len(tail) >= 5 and tail[0].lower() in {"openai-curated", "openai-bundled", "openai-primary-runtime"}:
                family = tail[0]
                plugin = tail[1]
                skill_dir = "unknown"
                if "skills" in [p.lower() for p in tail]:
                    si = [p.lower() for p in tail].index("skills")
                    if si + 1 < len(tail):
                        skill_dir = tail[si + 1]
                return f"plugin:{family}/{plugin}/{skill_dir}"
    except ValueError:
        pass
    try:
        skills_idx = lower_parts.index("skills")
        if skills_idx + 1 < len(parts):
            owner = "user"
            try:
                p = Path(normalized).resolve()
                p.relative_to(repo_root.resolve())
                owner = "repo"
            except Exception:
                owner = "user"
            return f"{owner}:{parts[skills_idx + 1]}"
    except ValueError:
        pass
    return normalized


def texts_from_jsonl_payload(obj: dict[str, Any]) -> list[str]:
    payload = obj.get("payload") or {}
    typ = obj.get("type")
    texts: list[str] = []
    if typ == "response_item":
        content = payload.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    value = item.get("text") or item.get("input_text")
                    if value:
                        texts.append(str(value))
        elif isinstance(content, str):
            texts.append(content)
        for key in ("arguments", "output", "name"):
            if payload.get(key):
                texts.append(str(payload[key]))
    elif typ == "event_msg":
        as_text = json.dumps(payload, ensure_ascii=False)
        if any(
            token in as_text
            for token in (
                "SKILL.md",
                "Using skill",
                "使用技能",
                "浣跨敤",
                "load_module.ps1",
                "set_plugin_profile.ps1",
            )
        ):
            texts.append(as_text[:60000])
    return texts


def extract_skill_names(segment: str, allowed_names: set[str] | None = None) -> list[str]:
    # Count only explicit backticked skill names. This avoids treating policy
    # prose such as "使用技能：xxx" or bullet text as actual usage evidence.
    names = [name.strip() for name in BACKTICK_PATTERN.findall(segment) if name.strip()]
    filtered: list[str] = []
    for name in names:
        lowered = name.lower()
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{1,79}$", name):
            continue
        if lowered in GENERIC_EXPLICIT_SKILL_NOISE:
            continue
        if allowed_names is not None and lowered not in allowed_names:
            continue
        filtered.append(name)
    return filtered


def classify_explicit_skill_names(
    segment: str, allowed_names: set[str] | None = None
) -> tuple[list[str], list[str], list[str]]:
    names = [name.strip() for name in BACKTICK_PATTERN.findall(segment) if name.strip()]
    accepted: list[str] = []
    generic_noise: list[str] = []
    unknown_noise: list[str] = []
    for name in names:
        lowered = name.lower()
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{1,79}$", name):
            unknown_noise.append(name)
            continue
        if lowered in GENERIC_EXPLICIT_SKILL_NOISE:
            generic_noise.append(name)
            continue
        if allowed_names is not None and lowered not in allowed_names:
            unknown_noise.append(name)
            continue
        accepted.append(name)
    return accepted, generic_noise, unknown_noise


def known_skill_names(codex_home: Path, repo_root: Path, modules: set[str], known_plugins: list[str]) -> set[str]:
    names = {module.lower() for module in modules}
    names.update(plugin.lower() for plugin in known_plugins)
    for skills_root in (codex_home / "skills", repo_root / ".codex" / "skills"):
        if skills_root.exists():
            for skill_md in skills_root.rglob("SKILL.md"):
                try:
                    names.add(skill_md.parent.name.lower())
                except OSError:
                    continue
    plugin_cache = codex_home / "plugins" / "cache"
    if plugin_cache.exists():
        for skill_md in plugin_cache.rglob("SKILL.md"):
            try:
                names.add(skill_md.parent.name.lower())
            except OSError:
                continue
    return names


def scan_sessions(codex_home: Path, repo_root: Path, cutoff: datetime, modules: set[str]) -> dict[str, Any]:
    sessions_root = codex_home / "sessions"
    explicit_skills: Counter[str] = Counter()
    explicit_skill_noise: Counter[str] = Counter()
    skill_paths: Counter[str] = Counter()
    profile_helper_calls: Counter[str] = Counter()
    weak_plugin_mentions: Counter[str] = Counter()
    tool_call_names: Counter[str] = Counter()
    files_scanned = 0
    lines_scanned = 0
    known_plugins = load_known_plugins(codex_home, repo_root)
    allowed_explicit_skill_names = known_skill_names(codex_home, repo_root, modules, known_plugins)

    if not sessions_root.exists():
        return {
            "files_scanned": 0,
            "lines_scanned": 0,
            "explicit_skills": {},
            "explicit_skill_noise_removed": {},
            "skill_paths": {},
            "profile_helper_calls": {},
            "tool_call_names": {},
            "weak_plugin_mentions": {},
        }

    module_command_re = re.compile(r"(load_module|set_plugin_profile)\.ps1([^\n\r]*)", re.IGNORECASE)
    for path in sessions_root.rglob("*.jsonl"):
        try:
            raw_text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if cutoff.year >= 2026 and f"{cutoff.year}-" not in raw_text and "SKILL.md" not in raw_text:
            # Fast skip for old files that have neither recent timestamps nor skill reads.
            continue
        file_used = False
        for line in raw_text.splitlines():
            lines_scanned += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_ts(obj.get("timestamp"))
            if ts is not None and ts < cutoff:
                continue
            texts = texts_from_jsonl_payload(obj)
            if not texts:
                continue
            file_used = True
            payload = obj.get("payload") or {}
            if obj.get("type") == "response_item" and payload.get("type") == "function_call" and payload.get("name"):
                tool_call_names[str(payload.get("name"))] += 1
            for text in texts:
                for pattern in SKILL_ANNOUNCE_PATTERNS:
                    for match in pattern.finditer(text):
                        accepted, generic_noise, unknown_noise = classify_explicit_skill_names(
                            match.group(1)[:300], allowed_explicit_skill_names
                        )
                        for name in accepted:
                            explicit_skills[name] += 1
                        for name in generic_noise + unknown_noise:
                            explicit_skill_noise[sanitize_explicit_skill_noise_token(name)] += 1
                for match in SKILL_PATH_PATTERN.finditer(text):
                    skill_paths[normalize_skill_path(match.group(1), codex_home, repo_root)] += 1
                for match in module_command_re.finditer(text):
                    tail = match.group(2)
                    found_module = None
                    for module in sorted(modules, key=len, reverse=True):
                        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(module)}(?![A-Za-z0-9_-])", tail):
                            found_module = module
                            break
                    profile_helper_calls[found_module or match.group(1).lower()] += 1
                lower_text = text.lower()
                for plugin in known_plugins:
                    if plugin.lower() in lower_text:
                        weak_plugin_mentions[plugin] += 1
        if file_used:
            files_scanned += 1

    return {
        "files_scanned": files_scanned,
        "lines_scanned": lines_scanned,
        "explicit_skills": dict(explicit_skills.most_common()),
        "explicit_skill_noise_removed": dict(explicit_skill_noise.most_common()),
        "skill_paths": dict(skill_paths.most_common()),
        "profile_helper_calls": dict(profile_helper_calls.most_common()),
        "tool_call_names": dict(tool_call_names.most_common()),
        "weak_plugin_mentions": dict(weak_plugin_mentions.most_common()),
    }


def load_profiles(codex_home: Path, repo_root: Path | None = None) -> dict[str, Any]:
    user_path = codex_home / "skills" / "plugin-modules" / "references" / "profiles.json"
    if user_path.exists():
        return read_json(user_path)
    if repo_root is not None:
        repo_path = repo_root / "tools" / "skill_sources" / "plugin-modules" / "references" / "profiles.json"
        if repo_path.exists():
            return read_json(repo_path)
    return {}


def load_known_plugins(codex_home: Path, repo_root: Path | None = None) -> list[str]:
    profiles = load_profiles(codex_home, repo_root)
    known = profiles.get("known_plugins")
    if isinstance(known, list):
        return [str(item) for item in known]
    return []


def scan_logs(codex_home: Path, cutoff: datetime, until: datetime | None = None) -> dict[str, Any]:
    db = codex_home / "logs_2.sqlite"
    warnings: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    until = until or now_utc()
    seven_day_cutoff_epoch = int((until - timedelta(days=7)).timestamp())
    last_7d_budget_warning_count = 0
    all_descriptions_removed_count = 0
    last_7d_all_descriptions_removed_count = 0
    max_omitted_additional_skills = 0
    if not db.exists():
        return {
            "available": False,
            "budget_warning_count": 0,
            "last_7d_budget_warning_count": 0,
            "all_descriptions_removed_count": 0,
            "last_7d_all_descriptions_removed_count": 0,
            "max_omitted_additional_skills": 0,
            "recent_budget_warnings": [],
            "skipped_loading_count": 0,
            "recent_skipped_loading": [],
        }
    cutoff_epoch = int(cutoff.timestamp())
    con = sqlite3.connect(str(db))
    try:
        cur = con.cursor()
        cur.execute(
            "select ts, level, target, feedback_log_body from logs where ts >= ? and feedback_log_body is not null and (feedback_log_body like ? or feedback_log_body like ?) order by ts desc",
            (cutoff_epoch, "%Exceeded skills context budget%", "%Skipped loading%"),
        )
        for ts, level, target, body in cur.fetchall():
            ts_int = int(ts)
            dt = datetime.fromtimestamp(ts_int, timezone.utc).astimezone().isoformat()
            body_text = str(body or "")
            omitted_match = OMITTED_PATTERN.search(body_text)
            omitted_count = int(omitted_match.group(1)) if omitted_match else None
            all_removed = "All skill descriptions were removed" in body_text
            row = {
                "time": dt,
                "level": level,
                "target": target,
                "omitted_additional_skills": omitted_count,
                "all_descriptions_removed": all_removed,
                "message_excerpt": sanitize_log_excerpt(body_text),
            }
            if BUDGET_WARNING_PATTERN.search(body_text):
                warnings.append(row)
                if ts_int >= seven_day_cutoff_epoch:
                    last_7d_budget_warning_count += 1
                if all_removed:
                    all_descriptions_removed_count += 1
                    if ts_int >= seven_day_cutoff_epoch:
                        last_7d_all_descriptions_removed_count += 1
                if omitted_count is not None:
                    max_omitted_additional_skills = max(max_omitted_additional_skills, omitted_count)
            if "Skipped loading" in body_text:
                skipped.append(row)
    finally:
        con.close()
    return {
        "available": True,
        "budget_warning_count": len(warnings),
        "last_7d_budget_warning_count": last_7d_budget_warning_count,
        "all_descriptions_removed_count": all_descriptions_removed_count,
        "last_7d_all_descriptions_removed_count": last_7d_all_descriptions_removed_count,
        "max_omitted_additional_skills": max_omitted_additional_skills,
        "recent_budget_warnings": warnings[:20],
        "skipped_loading_count": len(skipped),
        "recent_skipped_loading": skipped[:20],
    }


def build_warning_severity(logs_data: dict[str, Any]) -> dict[str, Any]:
    if not logs_data.get("available"):
        return {
            "level": "unknown",
            "reason": "logs_unavailable",
            "recommended_action": "keep_log_evidence_available_false_and_do_not_treat_zero_as_no_warning",
        }
    warning_count = int(logs_data.get("budget_warning_count") or 0)
    last_7d_warning_count = int(logs_data.get("last_7d_budget_warning_count") or 0)
    recent_warnings = logs_data.get("recent_budget_warnings") or []
    all_descriptions_removed = bool(logs_data.get("all_descriptions_removed_count")) or any(
        row.get("all_descriptions_removed") for row in recent_warnings if isinstance(row, dict)
    )
    if all_descriptions_removed or last_7d_warning_count >= 3:
        return {
            "level": "high",
            "reason": "all_descriptions_removed_or_last_7d_budget_warning_count_at_least_3",
            "recommended_action": "avoid_full_profile_and_prefer_smaller_default_or_task_profile_during_audit",
        }
    if warning_count > 0:
        return {
            "level": "medium",
            "reason": "budget_warnings_present_below_high_threshold",
            "recommended_action": "continue_audit_and_triage_with_task_context",
        }
    return {
        "level": "none",
        "reason": "no_budget_warnings_in_window",
        "recommended_action": "continue_scheduled_audit_without_profile_apply",
    }


def audit_window_elapsed_days(cutoff: datetime, generated_at: datetime) -> float:
    return max((generated_at - cutoff).total_seconds() / 86400, 0.0)


def candidate_output_requested(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "candidate_output", None) or getattr(args, "candidate_summary_output", None))


def target_profile_ready(args: argparse.Namespace) -> bool:
    return bool(str(getattr(args, "target_profile", "") or "").strip())


def source_report_paths_ready(args: argparse.Namespace) -> bool:
    return bool(str(getattr(args, "output", "") or "").strip()) and bool(
        str(getattr(args, "summary_output", "") or "").strip()
    )


def warning_triage_requested(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "warning_triage", False))


def warning_triage_window_ok(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "since", None)) or int(getattr(args, "days", 30) or 0) == 1


def planned_audit_requested(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "planned_audit", False))


def pause_audit_reason(args: argparse.Namespace) -> str | None:
    raw_reason = getattr(args, "pause_audit", None)
    if raw_reason is None:
        return None
    reason = str(raw_reason).strip()
    return reason or None


def build_audit_state(
    args: argparse.Namespace,
    cutoff: datetime | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    elapsed_days = audit_window_elapsed_days(cutoff, generated_at) if cutoff and generated_at else float(args.days)
    window_at_least_30_days = args.days >= 30 or elapsed_days >= 30
    summary_reviewed = bool(getattr(args, "summary_reviewed", False))
    source_paths_ready = source_report_paths_ready(args)
    candidate_requested = candidate_output_requested(args)
    target_profile_available = target_profile_ready(args)
    close_audit = getattr(args, "close_audit", None)
    pause_reason = pause_audit_reason(args)
    if pause_reason:
        return {
            "state": "paused",
            "reason": f"audit_paused_{pause_reason}",
            "next_action": "resolve_pause_reason_fix_data_source_or_privacy_or_script_defect_then_rerun_report",
            "profile_apply_allowed": False,
            "pause_reason": pause_reason,
            "pause_blockers": [pause_reason],
        }
    if planned_audit_requested(args):
        return {
            "state": "planned",
            "reason": "audit_plan_recorded_baseline_not_generated",
            "next_action": "run_day_0_baseline_preview_without_profile_apply",
            "profile_apply_allowed": False,
            "planned_audit": True,
        }
    if warning_triage_requested(args) and not warning_triage_window_ok(args):
        return {
            "state": "running",
            "reason": "warning_triage_window_too_broad",
            "next_action": "rerun_warning_triage_with_days_1_or_since",
            "profile_apply_allowed": False,
            "warning_triage_blockers": ["warning_triage_window_not_narrow"],
        }
    if close_audit:
        close_blockers: list[str] = []
        if not window_at_least_30_days:
            close_blockers.append("audit_window_shorter_than_30_days")
        if not summary_reviewed:
            close_blockers.append("summary_not_marked_reviewed")
        if not source_paths_ready:
            close_blockers.append("source_report_paths_missing")
        if close_audit == "with-candidate" and not candidate_requested:
            close_blockers.append("candidate_output_missing")
        if close_audit == "with-candidate" and not target_profile_available:
            close_blockers.append("target_profile_missing")
        if not close_blockers:
            if close_audit == "no-change":
                return {
                    "state": "closed-no-change",
                    "reason": "summary_reviewed_and_no_profile_change_candidate_requested",
                    "next_action": "close_this_audit_round_and_keep_dormant_or_soft_load_paths",
                    "profile_apply_allowed": False,
                    "close_audit_requested": close_audit,
                    "close_blockers": [],
                }
            return {
                "state": "closed-with-candidate",
                "reason": "summary_reviewed_and_profile_apply_candidate_record_requested",
                "next_action": "move_follow_up_to_the_separate_profile_apply_candidate_change",
                "profile_apply_allowed": False,
                "close_audit_requested": close_audit,
                "close_blockers": [],
            }
        return {
            "state": "ready-for-summary" if window_at_least_30_days else "running",
            "reason": f"audit_closure_{close_audit}_blocked",
            "next_action": "resolve_closure_blockers_without_profile_apply",
            "profile_apply_allowed": False,
            "close_audit_requested": close_audit,
            "close_blockers": close_blockers,
        }
    if candidate_requested and summary_reviewed and window_at_least_30_days and source_paths_ready and target_profile_available:
        return {
            "state": "apply-candidate",
            "reason": "profile_apply_candidate_preview_requested_after_summary_review",
            "next_action": "review_preview_candidate_and_request_explicit_apply_authorization_if_accepted",
            "profile_apply_allowed": False,
        }
    if candidate_requested and summary_reviewed and window_at_least_30_days and (not source_paths_ready or not target_profile_available):
        candidate_blockers = []
        if not source_paths_ready:
            candidate_blockers.append("source_report_paths_missing")
        if not target_profile_available:
            candidate_blockers.append("target_profile_missing")
        return {
            "state": "ready-for-summary",
            "reason": "profile_apply_candidate_gate_blocked",
            "next_action": "resolve_candidate_blockers_before_candidate_review",
            "profile_apply_allowed": False,
            "candidate_blockers": candidate_blockers,
        }
    if summary_reviewed and window_at_least_30_days and source_paths_ready:
        return {
            "state": "summary-reviewed",
            "reason": "summary_reviewed_and_source_reports_ready",
            "next_action": "create_profile_apply_candidate_or_close_audit_round_without_profile_apply",
            "profile_apply_allowed": False,
            "summary_reviewed": True,
        }
    if summary_reviewed and window_at_least_30_days and not source_paths_ready:
        return {
            "state": "ready-for-summary",
            "reason": "summary_reviewed_source_report_paths_missing",
            "next_action": "regenerate_with_output_and_summary_output_before_candidate_or_closure",
            "profile_apply_allowed": False,
            "summary_reviewed": True,
            "summary_review_blockers": ["source_report_paths_missing"],
        }
    if args.baseline:
        return {
            "state": "running",
            "reason": "baseline_generated",
            "next_action": "continue_weekly_reports_warning_triage_and_manual_notes",
            "profile_apply_allowed": False,
        }
    if window_at_least_30_days:
        return {
            "state": "ready-for-summary",
            "reason": "audit_window_at_least_30_days",
            "next_action": "generate_sanitized_30_day_markdown_summary_before_profile_apply_candidate",
            "profile_apply_allowed": False,
        }
    return {
        "state": "running",
        "reason": "audit_window_shorter_than_30_days",
        "next_action": "continue_audit_collection_without_profile_apply",
        "profile_apply_allowed": False,
    }


def build_warning_triage(
    args: argparse.Namespace,
    logs_data: dict[str, Any],
    cutoff: datetime,
    generated_at: datetime,
) -> dict[str, Any]:
    requested = warning_triage_requested(args)
    window_ok = warning_triage_window_ok(args)
    blockers = ["warning_triage_window_not_narrow"] if requested and not window_ok else []
    warning_count = int(logs_data.get("budget_warning_count") or 0)
    skipped_loading_count = int(logs_data.get("skipped_loading_count") or 0)
    recent_skipped_loading = logs_data.get("recent_skipped_loading") or []
    recent_skipped_loading_samples = len(recent_skipped_loading)
    recent_skipped_loading_sample_excerpts = [
        str(row.get("message_excerpt") or "")
        for row in recent_skipped_loading[:3]
        if isinstance(row, dict) and str(row.get("message_excerpt") or "").strip()
    ]
    skipped_loading_review = (
        "record_source_and_do_not_edit_vendor_cache_without_authorization"
        if skipped_loading_count
        else "none"
    )
    available = bool(logs_data.get("available"))
    if not requested:
        status = "not_requested"
        recommended_action = "run_with_warning_triage_after_a_live_session_budget_warning"
    elif blockers:
        status = "blocked"
        recommended_action = "rerun_with_days_1_or_since_covering_the_warning_time"
    elif not available:
        status = "log_source_unavailable"
        recommended_action = "use_session_transcripts_only_as_supporting_evidence_do_not_treat_zero_logs_as_no_warning"
    else:
        status = "warning_found" if warning_count else "no_warning_found_in_triage_window"
        recommended_action = (
            "review_recent_budget_warning_samples_and_record_turn_context"
            if warning_count
            else "record_no_matching_warning_in_this_window_without_ending_the_audit"
        )
    return {
        "requested": requested,
        "status": status,
        "blockers": blockers,
        "window_policy": WARNING_TRIAGE_WINDOW_POLICY,
        "window_ok": window_ok,
        "since": cutoff.isoformat(),
        "until": generated_at.isoformat(),
        "days": int(getattr(args, "days", 30) or 0),
        "uses_since_override": bool(getattr(args, "since", None)),
        "log_evidence_available": available,
        "budget_warning_count": warning_count,
        "skipped_loading_count": skipped_loading_count,
        "recent_skipped_loading_samples": recent_skipped_loading_samples,
        "recent_skipped_loading_sample_excerpts": recent_skipped_loading_sample_excerpts,
        "skipped_loading_review": skipped_loading_review,
        "all_descriptions_removed_count": logs_data.get("all_descriptions_removed_count", 0),
        "max_omitted_additional_skills": logs_data.get("max_omitted_additional_skills", 0),
        "recent_budget_warning_samples": len(logs_data.get("recent_budget_warnings") or []),
        "recommended_action": recommended_action,
    }


def validate_report_field_contract(report: dict[str, Any], *, require_embedded: bool = False) -> dict[str, Any]:
    required_fields = set(REQUIRED_REPORT_FIELDS)
    type_expectations = dict(REQUIRED_REPORT_FIELD_TYPES)
    if require_embedded:
        required_fields.add("field_contract")
        type_expectations["field_contract"] = dict
    missing_fields = sorted(required_fields - set(report))
    invalid_type_fields = sorted(
        field
        for field, expected_type in type_expectations.items()
        if field in report and not isinstance(report.get(field), expected_type)
    )
    safety = report.get("safety") if isinstance(report.get("safety"), dict) else {}
    safety_violations = sorted(
        field
        for field in ("mutates_config", "edits_plugin_cache", "hard_load_apply_performed", "audit_only")
        if field not in safety
    )
    if safety.get("mutates_config") is not False:
        safety_violations.append("mutates_config_not_false")
    if safety.get("edits_plugin_cache") is not False:
        safety_violations.append("edits_plugin_cache_not_false")
    if safety.get("hard_load_apply_performed") is not False:
        safety_violations.append("hard_load_apply_performed_not_false")
    if safety.get("audit_only") is not True:
        safety_violations.append("audit_only_not_true")
    audit_state = report.get("audit_state") if isinstance(report.get("audit_state"), dict) else {}
    audit_state_violations = []
    for field in sorted(REQUIRED_AUDIT_STATE_FIELDS):
        if field not in audit_state:
            audit_state_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_AUDIT_STATE_FIELD_TYPES.items()):
        if field in audit_state and not isinstance(audit_state.get(field), expected_type):
            audit_state_violations.append(f"{field}_invalid_type")
    if isinstance(audit_state.get("state"), str) and audit_state.get("state") not in VALID_AUDIT_STATES:
        audit_state_violations.append("state_invalid_value")
    if audit_state.get("profile_apply_allowed") is not False:
        audit_state_violations.append("profile_apply_allowed_not_false")
    for field in AUDIT_STATE_BLOCKER_FIELDS:
        if field not in audit_state:
            continue
        blockers = audit_state.get(field)
        if not isinstance(blockers, list):
            audit_state_violations.append(f"{field}_invalid_type")
            continue
        if any(not isinstance(blocker, str) for blocker in blockers):
            audit_state_violations.append(f"{field}_contains_non_string")
    config = report.get("config_summary") if isinstance(report.get("config_summary"), dict) else {}
    config_violations = []
    if "current_profile" not in config:
        config_violations.append("current_profile_missing")
    log_evidence = report.get("log_evidence") if isinstance(report.get("log_evidence"), dict) else {}
    log_violations = []
    for field in ("budget_warning_count", "last_7d_budget_warning_count"):
        if field not in log_evidence:
            log_violations.append(f"{field}_missing")
    warning_triage = report.get("warning_triage") if isinstance(report.get("warning_triage"), dict) else {}
    warning_triage_violations = []
    for field in sorted(REQUIRED_WARNING_TRIAGE_FIELDS):
        if field not in warning_triage:
            warning_triage_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_WARNING_TRIAGE_FIELD_TYPES.items()):
        if field in warning_triage and not isinstance(warning_triage.get(field), expected_type):
            warning_triage_violations.append(f"{field}_invalid_type")
    if warning_triage.get("status") not in (None, *VALID_WARNING_TRIAGE_STATUSES):
        warning_triage_violations.append("status_invalid_value")
    if warning_triage.get("window_policy") not in (None, WARNING_TRIAGE_WINDOW_POLICY):
        warning_triage_violations.append("window_policy_invalid_value")
    if warning_triage.get("skipped_loading_review") not in (None, *VALID_WARNING_TRIAGE_SKIPPED_LOADING_REVIEWS):
        warning_triage_violations.append("skipped_loading_review_invalid_value")
    triage_blockers = warning_triage.get("blockers")
    if isinstance(triage_blockers, list):
        for blocker in triage_blockers:
            if not isinstance(blocker, str):
                warning_triage_violations.append("blockers_item_invalid_type")
            elif blocker not in VALID_WARNING_TRIAGE_BLOCKERS:
                warning_triage_violations.append(f"blockers_invalid_value:{blocker}")
        if warning_triage.get("status") == "blocked" and not triage_blockers:
            warning_triage_violations.append("blocked_status_missing_blockers")
        if triage_blockers and warning_triage.get("status") != "blocked":
            warning_triage_violations.append("blockers_require_blocked_status")
    for field in WARNING_TRIAGE_NON_NEGATIVE_INTEGER_FIELDS:
        if field in warning_triage:
            value = warning_triage.get(field)
            if isinstance(value, bool) or not isinstance(value, int):
                if f"{field}_invalid_type" not in warning_triage_violations:
                    warning_triage_violations.append(f"{field}_invalid_type")
            elif value < 0:
                warning_triage_violations.append(f"{field}_negative")
    sample_excerpts = warning_triage.get("recent_skipped_loading_sample_excerpts")
    if isinstance(sample_excerpts, list):
        for excerpt in sample_excerpts:
            if not isinstance(excerpt, str):
                warning_triage_violations.append("recent_skipped_loading_sample_excerpts_item_invalid_type")
                break
            if any(pattern.search(excerpt) for pattern in PRIVATE_PATH_PATTERNS):
                warning_triage_violations.append("recent_skipped_loading_sample_excerpts_contains_private_path")
                break
            raw_secret_found = False
            for match in ACCESS_TOKEN_PATTERN.finditer(excerpt):
                if match.group(1) != "[REDACTED_SECRET]":
                    warning_triage_violations.append("recent_skipped_loading_sample_excerpts_contains_raw_secret")
                    raw_secret_found = True
                    break
            if raw_secret_found:
                break
            if STANDALONE_TOKEN_PATTERN.search(excerpt):
                warning_triage_violations.append("recent_skipped_loading_sample_excerpts_contains_standalone_token")
                break
    cadence_review = report.get("cadence_review") if isinstance(report.get("cadence_review"), dict) else {}
    cadence_review_violations = []
    for field in sorted(REQUIRED_CADENCE_REVIEW_FIELDS):
        if field not in cadence_review:
            cadence_review_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_CADENCE_REVIEW_FIELD_TYPES.items()):
        if field in cadence_review and not isinstance(cadence_review.get(field), expected_type):
            cadence_review_violations.append(f"{field}_invalid_type")
    if "missed_weekly_runs" in cadence_review:
        missed_runs = cadence_review.get("missed_weekly_runs")
        if missed_runs is not None and (
            not isinstance(missed_runs, int) or isinstance(missed_runs, bool) or missed_runs < 0
        ):
            cadence_review_violations.append("missed_weekly_runs_invalid_type")
    if cadence_review.get("late_run") is True and cadence_review.get("missed_weekly_runs") is None:
        cadence_review_violations.append("late_run_missing_missed_weekly_runs")
    manual_evidence = report.get("manual_evidence") if isinstance(report.get("manual_evidence"), dict) else {}
    manual_violations = []
    for field in sorted(REQUIRED_MANUAL_EVIDENCE_FIELDS):
        if field not in manual_evidence:
            manual_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_MANUAL_EVIDENCE_FIELD_TYPES.items()):
        if field in manual_evidence and not isinstance(manual_evidence.get(field), expected_type):
            manual_violations.append(f"{field}_invalid_type")
    if manual_evidence.get("raw_notes_retained") is not False:
        manual_violations.append("raw_notes_retained_not_false")
    if manual_evidence.get("source_paths_retained") is not False:
        manual_violations.append("source_paths_retained_not_false")
    conflict_review = manual_evidence.get("conflict_review") if isinstance(manual_evidence.get("conflict_review"), dict) else {}
    for field in sorted(REQUIRED_MANUAL_CONFLICT_REVIEW_FIELDS):
        if field not in conflict_review:
            manual_violations.append(f"conflict_review:{field}_missing")
    for field, expected_type in sorted(REQUIRED_MANUAL_CONFLICT_REVIEW_FIELD_TYPES.items()):
        if field in conflict_review and not isinstance(conflict_review.get(field), expected_type):
            manual_violations.append(f"conflict_review:{field}_invalid_type")
    if conflict_review.get("policy") not in (None, "manual_notes_do_not_override_script_evidence"):
        manual_violations.append("conflict_review:policy_invalid_value")
    if isinstance(conflict_review.get("conflict_or_exception_count"), int) and conflict_review["conflict_or_exception_count"] < 0:
        manual_violations.append("conflict_review:conflict_or_exception_count_invalid_type")
    if isinstance(manual_evidence.get("max_path_length"), int) and manual_evidence["max_path_length"] > MANUAL_NOTE_PATH_LIMIT:
        manual_violations.append("max_path_length_exceeds_limit")
    serialized_manual = json.dumps(manual_evidence, ensure_ascii=False)
    if any(pattern.search(serialized_manual) for pattern in PRIVATE_PATH_PATTERNS):
        manual_violations.append("manual_evidence_contains_private_path")
    for match in ACCESS_TOKEN_PATTERN.finditer(serialized_manual):
        if match.group(1) != "[REDACTED_SECRET]":
            manual_violations.append("manual_evidence_contains_raw_secret_assignment")
            break
    if STANDALONE_TOKEN_PATTERN.search(serialized_manual):
        manual_violations.append("manual_evidence_contains_standalone_token")
    noise_review = report.get("noise_review") if isinstance(report.get("noise_review"), dict) else {}
    noise_violations = []
    for field in sorted(REQUIRED_NOISE_REVIEW_FIELDS):
        if field not in noise_review:
            noise_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_NOISE_REVIEW_FIELD_TYPES.items()):
        if field in noise_review and not isinstance(noise_review.get(field), expected_type):
            noise_violations.append(f"{field}_invalid_type")
    if noise_review.get("raw_noise_tokens_retained") is not False:
        noise_violations.append("raw_noise_tokens_retained_not_false")
    if isinstance(noise_review.get("max_noise_token_length"), int) and noise_review["max_noise_token_length"] > 120:
        noise_violations.append("max_noise_token_length_exceeds_120")
    removed_noise = noise_review.get("explicit_skill_noise_removed")
    if isinstance(removed_noise, dict):
        for token in removed_noise:
            if len(str(token)) > int(noise_review.get("max_noise_token_length") or EXPLICIT_SKILL_NOISE_TOKEN_LIMIT) + len(
                "[truncated]"
            ):
                noise_violations.append("explicit_skill_noise_token_too_long")
                break
            serialized_token = json.dumps(token, ensure_ascii=False)
            raw_token = str(token)
            if any(pattern.search(raw_token) for pattern in PRIVATE_PATH_PATTERNS):
                noise_violations.append("explicit_skill_noise_token_contains_private_path")
                break
            if ACCESS_TOKEN_PATTERN.search(raw_token) or STANDALONE_TOKEN_PATTERN.search(raw_token):
                noise_violations.append("explicit_skill_noise_token_contains_secret")
                break
    script_capabilities = (
        report.get("script_capability_boundaries")
        if isinstance(report.get("script_capability_boundaries"), dict)
        else {}
    )
    script_capability_violations = []
    for field in sorted(REQUIRED_SCRIPT_CAPABILITY_FIELDS):
        if field not in script_capabilities:
            script_capability_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_SCRIPT_CAPABILITY_FIELD_TYPES.items()):
        if field in script_capabilities and not isinstance(script_capabilities.get(field), expected_type):
            script_capability_violations.append(f"{field}_invalid_type")
    if not script_capabilities.get("reliable_coverage"):
        script_capability_violations.append("reliable_coverage_empty")
    if not script_capabilities.get("human_review_required_for"):
        script_capability_violations.append("human_review_required_for_empty")
    if not script_capabilities.get("enhancement_triggers"):
        script_capability_violations.append("enhancement_triggers_empty")
    alias_registry = (
        script_capabilities.get("stable_tool_call_alias_registry")
        if isinstance(script_capabilities.get("stable_tool_call_alias_registry"), dict)
        else {}
    )
    for field in sorted(REQUIRED_STABLE_TOOL_CALL_ALIAS_REGISTRY_FIELDS):
        if field not in alias_registry:
            script_capability_violations.append(f"stable_tool_call_alias_registry:{field}_missing")
    for field, expected_type in sorted(REQUIRED_STABLE_TOOL_CALL_ALIAS_REGISTRY_FIELD_TYPES.items()):
        if field in alias_registry and not isinstance(alias_registry.get(field), expected_type):
            script_capability_violations.append(f"stable_tool_call_alias_registry:{field}_invalid_type")
    if alias_registry.get("policy") != "stable_aliases_are_medium_evidence_only_and_never_profile_apply_evidence":
        script_capability_violations.append("stable_tool_call_alias_registry:policy_invalid_value")
    if alias_registry.get("evidence_level") != "medium":
        script_capability_violations.append("stable_tool_call_alias_registry:evidence_level_not_medium")
    if alias_registry.get("counts_as_strong_evidence") is not False:
        script_capability_violations.append("stable_tool_call_alias_registry:counts_as_strong_evidence_not_false")
    for field in ("plugin_aliases", "module_aliases"):
        aliases_by_target = alias_registry.get(field)
        if isinstance(aliases_by_target, dict):
            if not aliases_by_target:
                script_capability_violations.append(f"stable_tool_call_alias_registry:{field}_empty")
            for target, aliases in aliases_by_target.items():
                if not isinstance(target, str) or not target.strip():
                    script_capability_violations.append(f"stable_tool_call_alias_registry:{field}_target_invalid")
                    continue
                if not isinstance(aliases, list) or not aliases or any(
                    not isinstance(alias, str) or not alias.strip() for alias in aliases
                ):
                    script_capability_violations.append(
                        f"stable_tool_call_alias_registry:{field}:{target}_aliases_invalid"
                    )
    output_retention = report.get("output_retention") if isinstance(report.get("output_retention"), dict) else {}
    output_retention_violations = []
    for field in sorted(REQUIRED_OUTPUT_RETENTION_FIELDS):
        if field not in output_retention:
            output_retention_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_OUTPUT_RETENTION_FIELD_TYPES.items()):
        if field in output_retention and not isinstance(output_retention.get(field), expected_type):
            output_retention_violations.append(f"{field}_invalid_type")
    if output_retention.get("status") not in {"passed", "failed", "unavailable"}:
        output_retention_violations.append("status_invalid_value")
    if output_retention.get("status") == "passed" and output_retention.get("ok") is not True:
        output_retention_violations.append("passed_status_without_ok_true")
    if output_retention.get("status") in {"failed", "unavailable"} and output_retention.get("ok") is not False:
        output_retention_violations.append("nonpassing_status_without_ok_false")
    if output_retention.get("tmp_outputs_local_only") is not True:
        output_retention_violations.append("tmp_outputs_local_only_not_true")
    if output_retention.get("raw_audit_json_local_only") is not True:
        output_retention_violations.append("raw_audit_json_local_only_not_true")
    if output_retention.get("long_term_evidence_format") != "sanitized_markdown_summary":
        output_retention_violations.append("long_term_evidence_format_not_sanitized_markdown_summary")
    violation_count = output_retention.get("violation_count")
    if isinstance(violation_count, int) and not isinstance(violation_count, bool) and violation_count < 0:
        output_retention_violations.append("violation_count_negative")
    if output_retention.get("status") != "passed":
        output_retention_violations.append("status_not_passed")
    precommit_update_archive = (
        report.get("precommit_update_archive")
        if isinstance(report.get("precommit_update_archive"), dict)
        else {}
    )
    precommit_update_archive_violations = []
    for field in sorted(REQUIRED_PRECOMMIT_UPDATE_ARCHIVE_FIELDS):
        if field not in precommit_update_archive:
            precommit_update_archive_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_PRECOMMIT_UPDATE_ARCHIVE_FIELD_TYPES.items()):
        if field in precommit_update_archive and not isinstance(precommit_update_archive.get(field), expected_type):
            precommit_update_archive_violations.append(f"{field}_invalid_type")
    if precommit_update_archive.get("status") not in {"passed", "failed", "unavailable"}:
        precommit_update_archive_violations.append("status_invalid_value")
    if precommit_update_archive.get("status") == "passed" and precommit_update_archive.get("ok") is not True:
        precommit_update_archive_violations.append("passed_status_without_ok_true")
    if precommit_update_archive.get("status") in {"failed", "unavailable"} and precommit_update_archive.get("ok") is not False:
        precommit_update_archive_violations.append("nonpassing_status_without_ok_false")
    if precommit_update_archive.get("before_local_git_commit") is not True:
        precommit_update_archive_violations.append("before_local_git_commit_not_true")
    if precommit_update_archive.get("review_existing_files_for_required_updates") is not True:
        precommit_update_archive_violations.append("review_existing_files_for_required_updates_not_true")
    if precommit_update_archive.get("archive_completed_openspec_changes_before_commit") is not True:
        precommit_update_archive_violations.append("archive_completed_openspec_changes_before_commit_not_true")
    for field in ("error_count", "warning_count", "changed_path_count", "active_change_review_count"):
        value = precommit_update_archive.get(field)
        if isinstance(value, int) and not isinstance(value, bool) and value < 0:
            precommit_update_archive_violations.append(f"{field}_negative")
    if precommit_update_archive.get("status") != "passed":
        precommit_update_archive_violations.append("status_not_passed")
    runtime_paths = report.get("runtime_paths") if isinstance(report.get("runtime_paths"), dict) else {}
    runtime_path_violations: list[str] = []
    for field in sorted(REQUIRED_RUNTIME_PATH_FIELDS):
        if field not in runtime_paths:
            runtime_path_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_RUNTIME_PATH_FIELD_TYPES.items()):
        if field in runtime_paths and not isinstance(runtime_paths.get(field), expected_type):
            runtime_path_violations.append(f"{field}_invalid_type")
    if runtime_paths.get("raw_paths_retained") is not False:
        runtime_path_violations.append("raw_paths_retained_not_false")
    if runtime_paths.get("privacy_policy") != "runtime_paths_are_kind_labels_and_placeholders_no_raw_user_paths":
        runtime_path_violations.append("privacy_policy_invalid")
    for field in ("root", "codex_home", "config_path"):
        value = runtime_paths.get(field)
        if isinstance(value, str) and any(pattern.search(value) for pattern in PRIVATE_PATH_PATTERNS):
            runtime_path_violations.append(f"{field}_raw_private_path")
    report_root = report.get("root")
    if isinstance(report_root, str) and any(pattern.search(report_root) for pattern in PRIVATE_PATH_PATTERNS):
        runtime_path_violations.append("top_level_root_raw_private_path")
    report_codex_home = report.get("codex_home")
    if isinstance(report_codex_home, str) and any(pattern.search(report_codex_home) for pattern in PRIVATE_PATH_PATTERNS):
        runtime_path_violations.append("top_level_codex_home_raw_private_path")
    config_summary = report.get("config_summary") if isinstance(report.get("config_summary"), dict) else {}
    config_path = config_summary.get("config_path")
    if isinstance(config_path, str) and any(pattern.search(config_path) for pattern in PRIVATE_PATH_PATTERNS):
        runtime_path_violations.append("config_summary_config_path_raw_private_path")
    module_evidence = report.get("module_evidence") if isinstance(report.get("module_evidence"), list) else []
    module_evidence_violations = []
    for index, row in enumerate(module_evidence):
        row_prefix = f"row_{index}"
        if not isinstance(row, dict):
            module_evidence_violations.append(f"{row_prefix}:invalid_type")
            continue
        for field in sorted(REQUIRED_MODULE_EVIDENCE_FIELDS):
            if field not in row:
                module_evidence_violations.append(f"{row_prefix}:{field}_missing")
        for field, expected_type in sorted(REQUIRED_MODULE_EVIDENCE_FIELD_TYPES.items()):
            if field not in row:
                continue
            value = row.get(field)
            if expected_type is int:
                if not isinstance(value, int) or isinstance(value, bool):
                    module_evidence_violations.append(f"{row_prefix}:{field}_invalid_type")
            elif not isinstance(value, expected_type):
                module_evidence_violations.append(f"{row_prefix}:{field}_invalid_type")
        plugins = row.get("plugins")
        if isinstance(plugins, list) and any(not isinstance(plugin, str) for plugin in plugins):
            module_evidence_violations.append(f"{row_prefix}:plugins_contains_non_string")
        for field in MODULE_EVIDENCE_NONNEGATIVE_INT_FIELDS:
            value = row.get(field)
            if isinstance(value, int) and not isinstance(value, bool) and value < 0:
                module_evidence_violations.append(f"{row_prefix}:{field}_negative")
        threshold = row.get("default_candidate_threshold")
        if isinstance(threshold, int) and not isinstance(threshold, bool) and threshold <= 0:
            module_evidence_violations.append(f"{row_prefix}:default_candidate_threshold_not_positive")
        helper_calls = row.get("strong_helper_calls")
        path_reads = row.get("strong_skill_path_reads")
        strong_total = row.get("strong_total")
        if (
            isinstance(helper_calls, int)
            and not isinstance(helper_calls, bool)
            and isinstance(path_reads, int)
            and not isinstance(path_reads, bool)
            and isinstance(strong_total, int)
            and not isinstance(strong_total, bool)
            and strong_total != helper_calls + path_reads
        ):
            module_evidence_violations.append(f"{row_prefix}:strong_total_mismatch")
        if row.get("mapped_tool_call_policy") != MODULE_EVIDENCE_MAPPED_TOOL_POLICY:
            module_evidence_violations.append(f"{row_prefix}:mapped_tool_call_policy_invalid_value")
        if row.get("medium_evidence_rationale") not in VALID_MEDIUM_EVIDENCE_RATIONALES:
            module_evidence_violations.append(f"{row_prefix}:medium_evidence_rationale_invalid_value")
        if row.get("cross_project_utility") != "manual_review_required":
            module_evidence_violations.append(f"{row_prefix}:cross_project_utility_not_manual_review_required")
        if row.get("recommendation") not in VALID_MODULE_EVIDENCE_RECOMMENDATIONS:
            module_evidence_violations.append(f"{row_prefix}:recommendation_invalid_value")
        weak_mentions = row.get("weak_plugin_mentions")
        recommendation = row.get("recommendation")
        if (
            isinstance(strong_total, int)
            and not isinstance(strong_total, bool)
            and isinstance(weak_mentions, int)
            and not isinstance(weak_mentions, bool)
            and isinstance(threshold, int)
            and not isinstance(threshold, bool)
            and threshold > 0
            and weak_mentions >= 0
            and strong_total >= 0
            and recommendation in VALID_MODULE_EVIDENCE_RECOMMENDATIONS
            and recommendation != expected_module_evidence_recommendation(strong_total, weak_mentions, threshold)
        ):
            module_evidence_violations.append(f"{row_prefix}:recommendation_threshold_mismatch")
    decision_recommendation = (
        report.get("decision_recommendation")
        if isinstance(report.get("decision_recommendation"), dict)
        else {}
    )
    decision_violations = []
    for field in sorted(REQUIRED_DECISION_RECOMMENDATION_FIELDS):
        if field not in decision_recommendation:
            decision_violations.append(f"{field}_missing")
    for field, expected_type in sorted(REQUIRED_DECISION_RECOMMENDATION_FIELD_TYPES.items()):
        if field in decision_recommendation and not isinstance(decision_recommendation.get(field), expected_type):
            decision_violations.append(f"{field}_invalid_type")
    if decision_recommendation.get("status") != "advisory_only_no_profile_apply":
        decision_violations.append("status_not_advisory_only_no_profile_apply")
    if decision_recommendation.get("profile_apply_allowed") is not False:
        decision_violations.append("profile_apply_allowed_not_false")
    decision_buckets = decision_recommendation.get("buckets") if isinstance(decision_recommendation.get("buckets"), dict) else {}
    decision_bucket_counts = (
        decision_recommendation.get("bucket_counts")
        if isinstance(decision_recommendation.get("bucket_counts"), dict)
        else {}
    )
    for bucket_name in REQUIRED_DECISION_BUCKET_NAMES:
        bucket_values = decision_buckets.get(bucket_name)
        if bucket_name not in decision_buckets:
            decision_violations.append(f"buckets:{bucket_name}_missing")
            continue
        if not isinstance(bucket_values, list):
            decision_violations.append(f"buckets:{bucket_name}_invalid_type")
            continue
        if any(not isinstance(value, str) for value in bucket_values):
            decision_violations.append(f"buckets:{bucket_name}_contains_non_string")
        bucket_count = decision_bucket_counts.get(bucket_name)
        if bucket_name not in decision_bucket_counts:
            decision_violations.append(f"bucket_counts:{bucket_name}_missing")
            continue
        if not isinstance(bucket_count, int) or isinstance(bucket_count, bool):
            decision_violations.append(f"bucket_counts:{bucket_name}_invalid_type")
            continue
        if bucket_count != len(bucket_values):
            decision_violations.append(f"bucket_counts:{bucket_name}_stale")
    blockers = (
        [f"missing_field:{field}" for field in missing_fields]
        + [f"invalid_type:{field}" for field in invalid_type_fields]
        + [f"safety:{field}" for field in safety_violations]
        + [f"audit_state:{field}" for field in audit_state_violations]
        + [f"config_summary:{field}" for field in config_violations]
        + [f"log_evidence:{field}" for field in log_violations]
        + [f"warning_triage:{field}" for field in warning_triage_violations]
        + [f"cadence_review:{field}" for field in cadence_review_violations]
        + [f"manual_evidence:{field}" for field in manual_violations]
        + [f"noise_review:{field}" for field in noise_violations]
        + [f"script_capability_boundaries:{field}" for field in script_capability_violations]
        + [f"output_retention:{field}" for field in output_retention_violations]
        + [f"precommit_update_archive:{field}" for field in precommit_update_archive_violations]
        + [f"runtime_paths:{field}" for field in runtime_path_violations]
        + [f"module_evidence:{field}" for field in module_evidence_violations]
        + [f"decision_recommendation:{field}" for field in decision_violations]
    )
    embedded_violations: list[str] = []
    if require_embedded and "field_contract" in report:
        embedded = report.get("field_contract")
        if not isinstance(embedded, dict):
            embedded_violations.append("not_dict")
        else:
            expected_status = "passed" if not blockers else "failed"
            expected_passed = not blockers
            embedded_blockers = embedded.get("blockers")
            if embedded.get("status") != expected_status:
                embedded_violations.append("status_stale")
            if embedded.get("passed") is not expected_passed:
                embedded_violations.append("passed_stale")
            if not isinstance(embedded_blockers, list):
                embedded_violations.append("blockers_not_list")
            else:
                normalized_embedded = sorted(str(item) for item in embedded_blockers)
                normalized_expected = sorted(blockers)
                if normalized_embedded != normalized_expected:
                    embedded_violations.append("blockers_stale")
    blockers = blockers + [f"embedded_field_contract:{field}" for field in embedded_violations]
    return {
        "status": "passed" if not blockers else "failed",
        "passed": not blockers,
        "blockers": blockers,
        "required_fields": sorted(required_fields),
        "requires_embedded_field_contract": require_embedded,
        "missing_fields": missing_fields,
        "invalid_type_fields": invalid_type_fields,
        "safety_violations": safety_violations,
        "audit_state_violations": audit_state_violations,
        "config_summary_violations": config_violations,
        "log_evidence_violations": log_violations,
        "warning_triage_violations": warning_triage_violations,
        "cadence_review_violations": cadence_review_violations,
        "manual_evidence_violations": manual_violations,
        "noise_review_violations": noise_violations,
        "script_capability_boundary_violations": script_capability_violations,
        "output_retention_violations": output_retention_violations,
        "precommit_update_archive_violations": precommit_update_archive_violations,
        "runtime_path_violations": runtime_path_violations,
        "module_evidence_violations": module_evidence_violations,
        "decision_recommendation_violations": decision_violations,
        "embedded_field_contract_violations": embedded_violations,
    }


def build_candidate_generation_gate(
    report: dict[str, Any],
    summary_reviewed: bool,
    *,
    json_report_path: str | None = None,
    markdown_summary_path: str | None = None,
    require_source_reports: bool = False,
    target_profile: str | None = None,
    require_target_profile: bool = False,
) -> dict[str, Any]:
    audit_window = report.get("audit_window", {})
    try:
        configured_days = int(audit_window.get("days") or 0)
    except (TypeError, ValueError):
        configured_days = 0
    since = parse_ts(audit_window.get("since"))
    until = parse_ts(audit_window.get("until"))
    elapsed_days = audit_window_elapsed_days(since, until) if since and until else float(configured_days)
    audit_window_at_least_30_days = configured_days >= 30 or elapsed_days >= 30
    blockers: list[str] = []
    if not audit_window_at_least_30_days:
        blockers.append("audit_window_shorter_than_30_days")
    if not summary_reviewed:
        blockers.append("summary_not_marked_reviewed")
    audit_state = report.get("audit_state") if isinstance(report.get("audit_state"), dict) else {}
    audit_state_value = audit_state.get("state")
    if audit_state_value == "planned":
        blockers.append("audit_state_planned")
    elif audit_state_value == "paused":
        blockers.append("audit_state_paused")
    elif audit_state_value not in CANDIDATE_READY_AUDIT_STATES:
        blockers.append(f"audit_state_not_candidate_ready:{audit_state_value or 'missing'}")
    json_report_present = bool(str(json_report_path or "").strip())
    markdown_summary_present = bool(str(markdown_summary_path or "").strip())
    if require_source_reports and not json_report_present:
        blockers.append("source_report_json_missing")
    if require_source_reports and not markdown_summary_present:
        blockers.append("source_report_markdown_summary_missing")
    target_profile_present = bool(str(target_profile or "").strip())
    if require_target_profile and not target_profile_present:
        blockers.append("target_profile_missing")
    source_reports_privacy = source_report_privacy_contract(
        build_source_reports(json_report_path, markdown_summary_path)
    )
    if require_source_reports and not source_reports_privacy["passed"]:
        blockers.extend(f"source_report_privacy:{violation}" for violation in source_reports_privacy["violations"])
    field_contract = validate_report_field_contract(report, require_embedded=True)
    blockers.extend(f"field_contract:{blocker}" for blocker in field_contract["blockers"])
    allowed = not blockers
    return {
        "status": "allowed" if allowed else "blocked",
        "allowed": allowed,
        "blockers": blockers,
        "summary_reviewed": bool(summary_reviewed),
        "requires_30_day_summary": True,
        "audit_window_days": configured_days,
        "audit_window_elapsed_days": round(elapsed_days, 4),
        "audit_window_at_least_30_days": audit_window_at_least_30_days,
        "source_reports_required": bool(require_source_reports),
        "json_report_present": json_report_present,
        "markdown_summary_present": markdown_summary_present,
        "target_profile_required": bool(require_target_profile),
        "target_profile_present": target_profile_present,
        "candidate_ready_audit_states": sorted(CANDIDATE_READY_AUDIT_STATES),
        "source_reports_privacy": source_reports_privacy,
        "field_contract": field_contract,
        "ordinary_continue_or_generic_confirmation_is_not_apply_authorization": True,
    }


def module_plugins(profiles: dict[str, Any], module: dict[str, Any]) -> list[str]:
    raw_plugins = module.get("plugins", [])
    if raw_plugins == "all_known_plugins":
        known = profiles.get("known_plugins", [])
        return [str(item) for item in known] if isinstance(known, list) else []
    if isinstance(raw_plugins, list):
        return [str(item) for item in raw_plugins]
    return []


def normalize_name_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def tool_call_matches_stable_alias(tool_name: str, aliases: tuple[str, ...]) -> bool:
    """Match known tool-call prefixes without turning them into strong evidence."""
    tool_lower = tool_name.lower()
    tool_key = normalize_name_for_match(tool_name)
    for alias in aliases:
        alias_lower = alias.lower()
        alias_key = normalize_name_for_match(alias)
        if alias_lower.endswith("__") and tool_lower.startswith(alias_lower):
            return True
        if alias_key and alias_key in tool_key:
            return True
    return False


def match_enabled_known_plugins(enabled_plugins: list[str], known_plugins: list[str]) -> tuple[list[str], list[str]]:
    """Map config plugin entries to registry plugin names without exposing config contents."""
    matched: set[str] = set()
    unmatched: list[str] = []
    known_pairs = [(plugin, normalize_name_for_match(plugin)) for plugin in known_plugins]
    for entry in enabled_plugins:
        entry_base = entry.split("@", 1)[0]
        entry_keys = {
            normalize_name_for_match(entry),
            normalize_name_for_match(entry_base),
        }
        entry_matches = [
            plugin
            for plugin, plugin_key in known_pairs
            if plugin_key and any(plugin_key in entry_key or entry_key in plugin_key for entry_key in entry_keys if entry_key)
        ]
        if entry_matches:
            matched.update(entry_matches)
        else:
            unmatched.append(entry)
    return sorted(matched), sorted(unmatched)


def build_current_profile_summary(profiles: dict[str, Any], enabled_plugins: list[str]) -> dict[str, Any]:
    known_plugins = [str(item) for item in profiles.get("known_plugins", []) if isinstance(item, str)]
    matched_enabled, unmatched_enabled = match_enabled_known_plugins(enabled_plugins, known_plugins)
    enabled_known = set(matched_enabled)
    modules = profiles.get("modules") if isinstance(profiles.get("modules"), dict) else {}
    matches: list[dict[str, Any]] = []
    for module_name, module in modules.items():
        if not isinstance(module, dict):
            continue
        expected = set(module_plugins(profiles, module))
        if not expected:
            continue
        overlap = expected & enabled_known
        missing = expected - enabled_known
        extra = enabled_known - expected
        matches.append(
            {
                "module": module_name,
                "expected_plugins": len(expected),
                "enabled_overlap": len(overlap),
                "missing_expected_plugins": len(missing),
                "extra_enabled_known_plugins": len(extra),
                "coverage_ratio": round(len(overlap) / len(expected), 4) if expected else 0.0,
            }
        )
    matches.sort(
        key=lambda row: (
            row["missing_expected_plugins"] == 0 and row["extra_enabled_known_plugins"] == 0,
            row["coverage_ratio"],
            -row["extra_enabled_known_plugins"],
        ),
        reverse=True,
    )
    exact_matches = [
        row["module"]
        for row in matches
        if row["missing_expected_plugins"] == 0 and row["extra_enabled_known_plugins"] == 0
    ]
    inferred = exact_matches[0] if exact_matches else "custom_or_unmatched"
    return {
        "source": "inferred_from_enabled_plugin_entries",
        "inferred_profile": inferred,
        "exact_profile_matches": exact_matches,
        "closest_profile_matches": matches[:3],
        "matched_enabled_known_plugins": matched_enabled,
        "unmatched_enabled_plugin_entries": unmatched_enabled,
        "manual_review_required": inferred == "custom_or_unmatched" or bool(unmatched_enabled),
    }


def mapped_tool_call_count(tool_call_counts: Counter[str], module_name: str, plugins: list[str]) -> int:
    module_key = normalize_name_for_match(module_name)
    plugin_keys = [normalize_name_for_match(plugin) for plugin in plugins]
    module_aliases = TOOL_CALL_MODULE_ALIASES.get(module_name, ())
    plugin_aliases = tuple(
        alias
        for plugin in plugins
        for alias in TOOL_CALL_PLUGIN_ALIASES.get(plugin, ())
    )
    total = 0
    for tool_name, count in tool_call_counts.items():
        tool_key = normalize_name_for_match(tool_name)
        if module_key and module_key in tool_key:
            total += count
            continue
        if any(plugin_key and plugin_key in tool_key for plugin_key in plugin_keys):
            total += count
            continue
        if tool_call_matches_stable_alias(tool_name, module_aliases) or tool_call_matches_stable_alias(
            tool_name, plugin_aliases
        ):
            total += count
    return total


def expected_module_evidence_recommendation(strong_total: int, weak_mentions: int, threshold: int) -> str:
    if strong_total >= threshold:
        return "candidate_for_project_or_default_profile_review"
    if strong_total > 0:
        return "keep_module_on_demand_and_continue_audit"
    if weak_mentions > 0:
        return "mentioned_only_do_not_apply_without_strong_evidence"
    return "no_recent_evidence_keep_dormant_not_deleted"


def build_module_evidence(profiles: dict[str, Any], session_data: dict[str, Any]) -> list[dict[str, Any]]:
    modules = profiles.get("modules") if isinstance(profiles.get("modules"), dict) else {}
    helper_counts = Counter(session_data.get("profile_helper_calls", {}))
    skill_path_counts = Counter(session_data.get("skill_paths", {}))
    weak_mentions = Counter(session_data.get("weak_plugin_mentions", {}))
    tool_call_counts = Counter(session_data.get("tool_call_names", {}))
    rows: list[dict[str, Any]] = []
    for module_name, module in modules.items():
        plugins = module_plugins(profiles, module) if isinstance(module, dict) else []
        weak = sum(weak_mentions.get(plugin, 0) for plugin in plugins)
        # Strong plugin evidence is approximated by plugin skill path reads containing a normalized plugin slug.
        strong_path = 0
        for path_label, count in skill_path_counts.items():
            lowered = path_label.lower().replace(" ", "-")
            for plugin in plugins:
                slug = plugin.lower().replace(" ", "-")
                if slug in lowered:
                    strong_path += count
                    break
        helper = helper_counts.get(module_name, 0)
        mapped_tools = mapped_tool_call_count(tool_call_counts, module_name, plugins)
        strong_total = helper + strong_path
        medium_rationale = (
            "mapped_tool_calls_present_manual_review_required" if mapped_tools else "no_mapped_tool_call_medium_evidence"
        )
        default_candidate_threshold = 10
        recommendation = expected_module_evidence_recommendation(strong_total, weak, default_candidate_threshold)
        rows.append(
            {
                "module": module_name,
                "plugins": plugins,
                "strong_helper_calls": helper,
                "strong_skill_path_reads": strong_path,
                "strong_total": strong_total,
                "default_candidate_threshold": default_candidate_threshold,
                "mapped_tool_call_mentions": mapped_tools,
                "mapped_tool_call_policy": MODULE_EVIDENCE_MAPPED_TOOL_POLICY,
                "medium_evidence_rationale": medium_rationale,
                "weak_plugin_mentions": weak,
                "cross_project_utility": "manual_review_required",
                "recommendation": recommendation,
            }
        )
    return rows


def build_noise_review(session_data: dict[str, Any]) -> dict[str, Any]:
    removed = dict(session_data.get("explicit_skill_noise_removed", {}))
    return {
        "status": "review_required" if removed else "no_obvious_false_positives_found",
        "explicit_skill_noise_removed": removed,
        "strong_evidence_policy": "removed_noise_tokens_are_not_counted_as_strong_evidence",
        "raw_noise_tokens_retained": False,
        "max_noise_token_length": EXPLICIT_SKILL_NOISE_TOKEN_LIMIT,
        "token_privacy_policy": "explicit_skill_noise_tokens_are_sanitized_path_secret_redacted_and_truncated",
    }


def build_script_capability_boundaries() -> dict[str, Any]:
    """Describe what the audit helper can prove and what still needs review."""
    return {
        "policy": "audit_helper_reports_evidence_boundaries_and_is_not_an_omniscient_source_of_truth",
        "reliable_coverage": [
            "plugin_enabled_disabled_unknown_state_from_config_toml",
            "user_repo_plugin_skill_inventory_counts",
            "session_explicit_skill_announcements_skill_path_reads_helper_calls_and_tool_call_names",
            "logs_2_sqlite_budget_warnings_all_descriptions_removed_omitted_skills_and_skipped_loading_samples",
            "profile_module_aggregation_from_helper_calls_and_plugin_skill_path_reads",
            "stable_tool_call_aliases_for_medium_evidence_only_module_review",
            "precommit_existing_file_update_and_openspec_archive_gate_status",
        ],
        "human_review_required_for": [
            "weak_plugin_mentions_are_text_trends_not_real_invocation_evidence",
            "explicit_skills_can_contain_natural_language_or_example_token_false_positives",
            "tool_call_names_and_stable_aliases_are_medium_evidence_not_plugin_or_profile_apply_evidence",
            "unreadable_rotated_or_missing_logs_can_underreport_warning_counts",
            "missing_or_stale_profile_registry_data_can_make_module_evidence_incomplete",
        ],
        "enhancement_triggers": [
            "same_false_positive_pattern_repeats_in_two_weekly_reports",
            "thirty_day_summary_needs_evidence_that_is_only_reported_as_weak_mentions",
            "stable_tool_call_pattern_maps_to_a_plugin_or_module_but_is_not_in_the_alias_registry",
            "live_session_warning_cannot_be_localized_from_logs_2_sqlite",
            "profile_registry_and_enabled_plugin_surface_diverge_enough_to_mislead_module_evidence",
        ],
        "stable_tool_call_alias_registry": stable_tool_call_alias_registry(),
    }


def slugify_candidate_part(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "profile"


def sanitize_source_report_path(value: str | None) -> str | None:
    return sanitize_retained_path(value)


def sanitize_source_reports(source_reports: dict[str, Any] | None) -> dict[str, Any]:
    if not source_reports:
        return build_source_reports()
    return {
        "json_report": sanitize_source_report_path(source_reports.get("json_report")),
        "markdown_summary": sanitize_source_report_path(source_reports.get("markdown_summary")),
        "manual_notes": [
            sanitize_source_report_path(str(path)) for path in (source_reports.get("manual_notes") or [])
        ],
    }


def source_report_privacy_contract(source_reports: dict[str, Any] | None) -> dict[str, Any]:
    serialized = json.dumps(source_reports or {}, ensure_ascii=False)
    violations: list[str] = []
    if any(pattern.search(serialized) for pattern in PRIVATE_PATH_PATTERNS):
        violations.append("raw_private_path")
    for match in ACCESS_TOKEN_PATTERN.finditer(serialized):
        if match.group(1) != "[REDACTED_SECRET]":
            violations.append("raw_secret_assignment")
            break
    if STANDALONE_TOKEN_PATTERN.search(serialized):
        violations.append("raw_standalone_token")
    return {
        "status": "passed" if not violations else "failed",
        "passed": not violations,
        "violations": violations,
        "policy": "candidate_source_reports_must_be_sanitized_before_recording_or_rendering",
        "redacted_path_count": serialized.count("[REDACTED_PATH]"),
        "redacted_secret_count": serialized.count("[REDACTED_SECRET]"),
    }


def iter_string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for nested in value.values():
            strings.extend(iter_string_values(nested))
        return strings
    if isinstance(value, list):
        strings = []
        for nested in value:
            strings.extend(iter_string_values(nested))
        return strings
    return []


def validate_profile_apply_candidate_contract(candidate: dict[str, Any]) -> dict[str, Any]:
    """Validate the self-contained, preview-only candidate record shape.

    This contract is separate from the upstream report field contract. It
    protects the retained candidate JSON/Markdown artifact from being mistaken
    for approval or an already-applied profile change.
    """

    missing_fields = sorted(REQUIRED_PROFILE_APPLY_CANDIDATE_FIELDS - set(candidate))
    invalid_type_fields = sorted(
        field
        for field, expected_type in REQUIRED_PROFILE_APPLY_CANDIDATE_FIELD_TYPES.items()
        if field in candidate and not isinstance(candidate.get(field), expected_type)
    )

    blockers: list[str] = []
    blockers.extend(f"missing:{field}" for field in missing_fields)
    blockers.extend(f"invalid_type:{field}" for field in invalid_type_fields)

    if candidate.get("schema_version") != 1:
        blockers.append("schema_version_not_1")
    if candidate.get("record_type") != "codex_skills_profile_apply_candidate":
        blockers.append("record_type_invalid")
    if not str(candidate.get("candidate_id") or "").strip():
        blockers.append("candidate_id_missing")
    if not str(candidate.get("generated_at") or "").strip():
        blockers.append("generated_at_missing")

    if candidate.get("approval_state") != PROFILE_APPLY_CANDIDATE_PREVIEW_APPROVAL_STATE:
        blockers.append("approval_state_not_preview_only")
    if candidate.get("mutates_config") is not False:
        blockers.append("mutates_config_not_false")
    if candidate.get("edits_plugin_cache") is not False:
        blockers.append("edits_plugin_cache_not_false")
    if candidate.get("hard_load_apply_performed") is not False:
        blockers.append("hard_load_apply_performed_not_false")
    if candidate.get("explicit_authorization_required_for_apply") is not True:
        blockers.append("explicit_authorization_required_for_apply_not_true")
    if candidate.get("ordinary_continue_or_generic_confirmation_is_not_apply_authorization") is not True:
        blockers.append("ordinary_continue_or_generic_confirmation_is_not_apply_authorization_not_true")

    source_reports_privacy = (
        candidate.get("source_reports_privacy") if isinstance(candidate.get("source_reports_privacy"), dict) else {}
    )
    if source_reports_privacy.get("status") != "passed" or source_reports_privacy.get("passed") is not True:
        blockers.append("source_reports_privacy_not_passed")
    privacy_violations = source_reports_privacy.get("violations")
    if privacy_violations not in (None, []):
        blockers.append("source_reports_privacy_has_violations")

    gate = candidate.get("candidate_generation_gate") if isinstance(candidate.get("candidate_generation_gate"), dict) else {}
    if "allowed" not in gate:
        blockers.append("candidate_generation_gate:allowed_missing")
    elif not isinstance(gate.get("allowed"), bool):
        blockers.append("candidate_generation_gate:allowed_invalid_type")
    if "blockers" not in gate:
        blockers.append("candidate_generation_gate:blockers_missing")
    elif not isinstance(gate.get("blockers"), list):
        blockers.append("candidate_generation_gate:blockers_invalid_type")
    elif any(not isinstance(blocker, str) for blocker in gate.get("blockers") or []):
        blockers.append("candidate_generation_gate:blockers_contains_non_string")
    if gate.get("status") not in (None, "allowed", "blocked"):
        blockers.append("candidate_generation_gate:status_invalid_value")
    if gate.get("status") == "allowed" and gate.get("allowed") is not True:
        blockers.append("candidate_generation_gate:allowed_status_without_allowed_true")
    if gate.get("status") == "blocked" and gate.get("allowed") is not False:
        blockers.append("candidate_generation_gate:blocked_status_without_allowed_false")

    rollback = candidate.get("rollback_path") if isinstance(candidate.get("rollback_path"), dict) else {}
    if not str(rollback.get("restore_command") or "").strip():
        blockers.append("rollback_path:restore_command_missing")
    if "restart_required" not in rollback:
        blockers.append("rollback_path:restart_required_missing")
    elif not isinstance(rollback.get("restart_required"), bool):
        blockers.append("rollback_path:restart_required_invalid_type")

    validation_plan = candidate.get("validation_plan")
    if isinstance(validation_plan, list):
        if not validation_plan:
            blockers.append("validation_plan_empty")
        for index, step in enumerate(validation_plan):
            if not isinstance(step, dict):
                blockers.append(f"validation_plan:{index}:invalid_type")
                continue
            if not str(step.get("step") or "").strip():
                blockers.append(f"validation_plan:{index}:step_missing")
            if not (str(step.get("command") or "").strip() or str(step.get("required_evidence") or "").strip()):
                blockers.append(f"validation_plan:{index}:evidence_or_command_missing")

    candidate_without_contract = {
        key: value for key, value in candidate.items() if key != "candidate_record_contract"
    }
    for value in iter_string_values(candidate_without_contract):
        if any(pattern.search(value) for pattern in PRIVATE_PATH_PATTERNS):
            blockers.append("candidate_contains_raw_private_path")
            break
    for value in iter_string_values(candidate_without_contract):
        raw_secret = False
        for match in ACCESS_TOKEN_PATTERN.finditer(value):
            if match.group(1) != "[REDACTED_SECRET]":
                blockers.append("candidate_contains_raw_secret_assignment")
                raw_secret = True
                break
        if raw_secret:
            break
    if any(STANDALONE_TOKEN_PATTERN.search(value) for value in iter_string_values(candidate_without_contract)):
        blockers.append("candidate_contains_standalone_token")

    return {
        "status": "passed" if not blockers else "failed",
        "passed": not blockers,
        "blockers": blockers,
        "required_fields": sorted(REQUIRED_PROFILE_APPLY_CANDIDATE_FIELDS),
        "missing_fields": missing_fields,
        "invalid_type_fields": invalid_type_fields,
        "preview_safety_violations": sorted(
            blocker
            for blocker in blockers
            if blocker
            in {
                "approval_state_not_preview_only",
                "mutates_config_not_false",
                "edits_plugin_cache_not_false",
                "hard_load_apply_performed_not_false",
                "explicit_authorization_required_for_apply_not_true",
                "ordinary_continue_or_generic_confirmation_is_not_apply_authorization_not_true",
            }
        ),
        "source_reports_privacy_violations": sorted(
            blocker for blocker in blockers if blocker.startswith("source_reports_privacy")
        ),
        "candidate_gate_violations": sorted(
            blocker for blocker in blockers if blocker.startswith("candidate_generation_gate:")
        ),
        "rollback_path_violations": sorted(
            blocker for blocker in blockers if blocker.startswith("rollback_path:")
        ),
        "validation_plan_violations": sorted(
            blocker for blocker in blockers if blocker.startswith("validation_plan")
        ),
        "sanitization_violations": sorted(
            blocker for blocker in blockers if blocker.startswith("candidate_contains_")
        ),
        "approval_state_policy": "candidate_outputs_from_this_script_must_remain_preview_only_until_a_separate_explicit_apply_change",
    }


def build_source_reports(
    json_report: str | None = None,
    markdown_summary: str | None = None,
    manual_notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "json_report": sanitize_source_report_path(json_report),
        "markdown_summary": sanitize_source_report_path(markdown_summary),
        "manual_notes": [sanitize_source_report_path(path) for path in (manual_notes or [])],
    }


def find_module_evidence_row(report: dict[str, Any], module_name: str) -> dict[str, Any] | None:
    for row in report.get("module_evidence", []):
        if isinstance(row, dict) and row.get("module") == module_name:
            return row
    return None


def build_profile_apply_candidate(
    report: dict[str, Any],
    candidate_id: str | None = None,
    target_profile: str | None = None,
    source_reports: dict[str, Any] | None = None,
    candidate_gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a preview-only profile apply candidate record.

    The candidate translates audit evidence into a reversible review record. It
    deliberately does not mutate config.toml, plugin cache, or hard-load state.
    """
    target_profile_value = str(target_profile or "").strip()
    target_profile_name = target_profile_value or "missing-target-profile"
    candidate_gate = candidate_gate or build_candidate_generation_gate(
        report,
        summary_reviewed=False,
        target_profile=target_profile_value,
        require_target_profile=True,
    )
    sanitized_source_reports = sanitize_source_reports(source_reports)
    source_reports_privacy = source_report_privacy_contract(sanitized_source_reports)

    generated_at = str(report.get("generated_at") or now_utc().isoformat())
    generated_day = generated_at[:10] if len(generated_at) >= 10 else now_utc().date().isoformat()
    candidate_id = candidate_id or f"skills-profile-{generated_day}-{slugify_candidate_part(target_profile_name)}"

    config = report.get("config_summary", {})
    current_profile = config.get("current_profile", {}) if isinstance(config, dict) else {}
    enabled_known = sorted(current_profile.get("matched_enabled_known_plugins") or [])
    enabled_known_set = set(enabled_known)
    target_row = find_module_evidence_row(report, target_profile_value) if target_profile_value else None
    target_plugins = sorted(target_row.get("plugins", [])) if target_row else []
    target_plugin_set = set(target_plugins)

    add_to_default = sorted(target_plugin_set - enabled_known_set)
    remove_from_default = sorted(enabled_known_set - target_plugin_set)
    keep_enabled = sorted(target_plugin_set & enabled_known_set)
    unknown_enabled = list(current_profile.get("unmatched_enabled_plugin_entries") or [])

    evidence_basis = {
        "target_profile": target_profile_value or None,
        "target_profile_present": bool(target_profile_value),
        "target_profile_found_in_registry": target_row is not None,
        "target_module_evidence": {
            "strong_total": target_row.get("strong_total") if target_row else 0,
            "strong_helper_calls": target_row.get("strong_helper_calls") if target_row else 0,
            "strong_skill_path_reads": target_row.get("strong_skill_path_reads") if target_row else 0,
            "medium_evidence_rationale": target_row.get("medium_evidence_rationale") if target_row else "target_profile_not_found_manual_review_required",
            "weak_plugin_mentions": target_row.get("weak_plugin_mentions") if target_row else 0,
            "cross_project_utility": target_row.get("cross_project_utility") if target_row else "manual_review_required",
            "recommendation": target_row.get("recommendation") if target_row else "target_profile_not_found_do_not_apply",
        },
        "warning_pressure": report.get("warning_severity", {}),
        "manual_evidence_counts": {
            "valid_note_count": report.get("manual_evidence", {}).get("valid_note_count", 0),
            "counts_by_evidence_level": report.get("manual_evidence", {}).get("counts_by_evidence_level", {}),
            "counts_by_action": report.get("manual_evidence", {}).get("counts_by_action", {}),
        },
        "policy": "strong_evidence_prefers_profile_candidates_medium_evidence_requires_human_review",
    }

    candidate = {
        "schema_version": 1,
        "record_type": "codex_skills_profile_apply_candidate",
        "candidate_id": candidate_id,
        "generated_at": generated_at,
        "source_reports": sanitized_source_reports,
        "source_reports_privacy": source_reports_privacy,
        "candidate_generation_gate": candidate_gate,
        "current_profile": {
            "inferred_profile": current_profile.get("inferred_profile"),
            "source": current_profile.get("source"),
            "manual_review_required": current_profile.get("manual_review_required"),
            "enabled_plugins_count": len(config.get("enabled_plugins", [])),
            "disabled_plugins_count": len(config.get("disabled_plugins", [])),
            "unknown_enabled_state_plugins": config.get("unknown_enabled_state_plugins", []),
            "matched_enabled_known_plugins": enabled_known,
            "unmatched_enabled_plugin_entries": unknown_enabled,
        },
        "target_profile": {
            "name": target_profile_value or None,
            "target_profile_present": bool(target_profile_value),
            "known_profile": target_row is not None,
            "target_plugins": target_plugins,
        },
        "plugin_diff": {
            "add_to_default": add_to_default,
            "remove_from_default": remove_from_default,
            "keep_enabled": keep_enabled,
            "unknown_current_enabled_entries_requiring_manual_review": unknown_enabled,
            "keep_dormant_or_on_demand_policy": "non_target_modules_remain_dormant_or_soft_load_until_a_separate_candidate_is_approved",
        },
        "evidence_basis": evidence_basis,
        "risk_review": {
            "risk_level": "manual_review_required" if remove_from_default or unknown_enabled or target_row is None else "low",
            "possibly_disabled_capabilities": remove_from_default,
            "affected_projects": "manual_review_required_before_apply",
            "restore_cost": "restart_or_resume_after_set_plugin_profile_restore_latest_apply",
            "generic_continue_is_not_authorization": True,
        },
        "rollback_path": {
            "restore_command": "set_plugin_profile.ps1 -RestoreLatest -Apply",
            "restart_required": True,
            "restart_entrypoint": "codex-ohmy",
            "rollback_first_policy": "if_budget_warnings_continue_or_capabilities_are_missing_restore_before_stacking_more_profile_changes",
        },
        "validation_plan": [
            {
                "step": "preview_candidate_record",
                "required_evidence": "review_candidate_json_and_sanitized_30_day_summary",
            },
            {
                "step": "local_checks",
                "command": "python .\\test\\audit_codex_skills_usage.test.py && powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\ci\\local_gate.ps1",
            },
            {
                "step": "startup_validation",
                "command": "restart_with_codex-ohmy_after_explicit_apply_authorization_only",
            },
            {
                "step": "warning_retest",
                "command": "python .\\tools\\audit_codex_skills_usage.py --root . --days 1 --json --output .\\.tmp\\skills-usage-warning-retest.json",
            },
        ],
        "approval_state": "preview-only",
        "mutates_config": False,
        "edits_plugin_cache": False,
        "hard_load_apply_performed": False,
        "explicit_authorization_required_for_apply": True,
        "ordinary_continue_or_generic_confirmation_is_not_apply_authorization": True,
    }
    candidate["candidate_record_contract"] = validate_profile_apply_candidate_contract(candidate)
    return candidate


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve() if args.codex_home else default_codex_home().resolve()
    generated_at = now_utc()
    if args.since:
        cutoff = parse_since(args.since)
    else:
        cutoff = generated_at - timedelta(days=max(args.days, 0))
    profiles = load_profiles(codex_home, root)
    modules = set((profiles.get("modules") or {}).keys()) if isinstance(profiles.get("modules"), dict) else set()
    plugins_config = parse_plugin_config(codex_home / "config.toml")
    enabled_plugins = sorted([name for name, enabled in plugins_config.items() if enabled is True])
    disabled_plugins = sorted([name for name, enabled in plugins_config.items() if enabled is False])
    session_data = scan_sessions(codex_home, root, cutoff, modules)
    logs_data = scan_logs(codex_home, cutoff, generated_at)
    inventory_counts = collect_inventory_counts(codex_home, root)
    module_evidence = build_module_evidence(profiles, session_data)
    noise_review = build_noise_review(session_data)
    warning_severity = build_warning_severity(logs_data)
    warning_triage = build_warning_triage(args, logs_data, cutoff, generated_at)
    audit_state = build_audit_state(args, cutoff, generated_at)
    current_profile = build_current_profile_summary(profiles, enabled_plugins)
    manual_notes = collect_manual_notes(getattr(args, "manual_notes", []) or [])
    decision_recommendation = build_decision_recommendation(module_evidence, warning_severity, audit_state)
    output_retention = build_output_retention_status(root)
    precommit_update_archive = build_precommit_update_archive_status(root)
    runtime_paths = build_runtime_paths(root, codex_home)
    report = {
        "schema_version": 1,
        "generated_at": generated_at.isoformat(),
        "check_name": "codex_skills_usage_audit",
        "mode": "baseline" if args.baseline else "usage_audit",
        "audit_state": audit_state,
        "audit_window": {
            "since": cutoff.isoformat(),
            "until": generated_at.isoformat(),
            "days": args.days,
        },
        "root": runtime_paths["root"],
        "codex_home": runtime_paths["codex_home"],
        "runtime_paths": runtime_paths,
        "safety": {
            "mutates_config": False,
            "edits_plugin_cache": False,
            "hard_load_apply_performed": False,
            "audit_only": True,
        },
        "config_summary": {
            "config_path": runtime_paths["config_path"],
            "plugins_total_in_config": len(plugins_config),
            "enabled_plugins": enabled_plugins,
            "disabled_plugins": disabled_plugins,
            "unknown_enabled_state_plugins": sorted([name for name, enabled in plugins_config.items() if enabled is None]),
            "current_profile": current_profile,
        },
        "cadence_review": {
            "late_run": bool(getattr(args, "late_run", False)),
            "missed_weekly_runs": getattr(args, "missed_weekly_runs", None),
            "weekly_report_review": "manual_review_required",
        },
        "inventory_summary": inventory_counts,
        "log_evidence": logs_data,
        "warning_severity": warning_severity,
        "warning_triage": warning_triage,
        "session_evidence": session_data,
        "module_evidence": module_evidence,
        "decision_recommendation": decision_recommendation,
        "noise_review": noise_review,
        "manual_evidence": manual_notes,
        "script_capability_boundaries": build_script_capability_boundaries(),
        "output_retention": output_retention,
        "precommit_update_archive": precommit_update_archive,
        "recommendations": [
            "Do not treat another 2% budget warning as soft-load failure; soft-load is outside the model-visible skills budget surface.",
            "Continue audit-only mode until the agreed window closes unless a concrete task requires a profile preview or explicitly approved hard-load apply.",
            "Use strong evidence, not weak mentions, to decide default profile changes.",
            "Keep disabled plugins restorable; do not delete plugin cache or vendor SKILL.md files.",
            "Before local commit, run the pre-commit update/archive gate and resolve required existing-file updates or OpenSpec archive work.",
        ],
    }
    report["field_contract"] = validate_report_field_contract(report)
    return report


def render_markdown_summary(report: dict[str, Any]) -> str:
    audit_window = report.get("audit_window", {})
    config = report.get("config_summary", {})
    warnings = report.get("log_evidence", {})
    warning_severity = report.get("warning_severity", {})
    warning_triage = report.get("warning_triage", {})
    noise_review = report.get("noise_review", {})
    manual_evidence = report.get("manual_evidence", {})
    script_capabilities = report.get("script_capability_boundaries", {})
    stable_alias_registry = (
        script_capabilities.get("stable_tool_call_alias_registry", {})
        if isinstance(script_capabilities, dict)
        else {}
    )
    output_retention = report.get("output_retention", {})
    precommit_update_archive = report.get("precommit_update_archive", {})
    runtime_paths = report.get("runtime_paths", {})
    audit_state = report.get("audit_state", {})
    field_contract = report.get("field_contract", {})
    cadence_review = report.get("cadence_review", {})
    decision_recommendation = report.get("decision_recommendation", {})
    decision_buckets = decision_recommendation.get("buckets", {}) if isinstance(decision_recommendation, dict) else {}
    audit_state_blocker_fields = [
        "close_blockers",
        "candidate_blockers",
        "summary_review_blockers",
        "pause_blockers",
        "warning_triage_blockers",
    ]
    audit_state_blockers = [
        str(blocker)
        for field in audit_state_blocker_fields
        for blocker in (audit_state.get(field) or [])
        if blocker is not None
    ]
    field_contract_blockers = field_contract.get("blockers") if isinstance(field_contract.get("blockers"), list) else []
    lines = [
        "# Codex Skills Usage Audit Summary",
        "",
        "## Audit window",
        "",
        f"- Since: `{audit_window.get('since')}`",
        f"- Until: `{audit_window.get('until')}`",
        f"- Days: `{audit_window.get('days')}`",
        f"- Audit state: `{audit_state.get('state')}` ({audit_state.get('reason')})",
        f"- Audit next action: `{audit_state.get('next_action')}`",
        f"- Profile apply allowed: `{audit_state.get('profile_apply_allowed')}`",
        f"- Audit state blockers: `{', '.join(audit_state_blockers) if audit_state_blockers else 'none'}`",
        f"- Field contract: `{field_contract.get('status')}`",
        f"- Field contract passed: `{field_contract.get('passed')}`",
        f"- Field contract blockers: `{len(field_contract_blockers)}`",
        f"- Field contract required fields: `{len(field_contract.get('required_fields') or [])}`",
        f"- Field contract missing fields: `{len(field_contract.get('missing_fields') or [])}`",
        f"- Field contract invalid-type fields: `{len(field_contract.get('invalid_type_fields') or [])}`",
        f"- Field contract requires embedded contract: `{field_contract.get('requires_embedded_field_contract')}`",
        f"- Field contract safety violations: `{len(field_contract.get('safety_violations') or [])}`",
        f"- Field contract audit-state violations: `{len(field_contract.get('audit_state_violations') or [])}`",
        f"- Field contract log-evidence violations: `{len(field_contract.get('log_evidence_violations') or [])}`",
        f"- Field contract warning-triage violations: `{len(field_contract.get('warning_triage_violations') or [])}`",
        f"- Field contract cadence-review violations: `{len(field_contract.get('cadence_review_violations') or [])}`",
        f"- Field contract manual-evidence violations: `{len(field_contract.get('manual_evidence_violations') or [])}`",
        f"- Field contract noise-review violations: `{len(field_contract.get('noise_review_violations') or [])}`",
        f"- Field contract script-capability violations: `{len(field_contract.get('script_capability_boundary_violations') or [])}`",
        f"- Field contract output-retention violations: `{len(field_contract.get('output_retention_violations') or [])}`",
        f"- Field contract precommit-update-archive violations: `{len(field_contract.get('precommit_update_archive_violations') or [])}`",
        f"- Field contract runtime-path violations: `{len(field_contract.get('runtime_path_violations') or [])}`",
        f"- Field contract module-evidence violations: `{len(field_contract.get('module_evidence_violations') or [])}`",
        f"- Field contract decision-recommendation violations: `{len(field_contract.get('decision_recommendation_violations') or [])}`",
        f"- Field contract embedded-contract violations: `{len(field_contract.get('embedded_field_contract_violations') or [])}`",
            f"- Output retention gate: `{output_retention.get('status')}` via `{output_retention.get('checker')}`",
            f"- Output retention violations: `{output_retention.get('violation_count')}`",
            f"- Pre-commit update/archive gate: `{precommit_update_archive.get('status')}` via `{precommit_update_archive.get('checker')}`",
            f"- Pre-commit update/archive errors: `{precommit_update_archive.get('error_count')}`",
            f"- Late run: `{cadence_review.get('late_run')}`",
        f"- Missed weekly runs: `{cadence_review.get('missed_weekly_runs')}`",
        f"- Weekly report review: `{cadence_review.get('weekly_report_review')}`",
        "",
        "## Current configuration surface",
        "",
        f"- Enabled plugins: `{len(config.get('enabled_plugins', []))}`",
        f"- Disabled plugins: `{len(config.get('disabled_plugins', []))}`",
        f"- Unknown plugin states: `{len(config.get('unknown_enabled_state_plugins', []))}`",
        f"- Inferred current profile: `{config.get('current_profile', {}).get('inferred_profile')}`",
        f"- Current profile source: `{config.get('current_profile', {}).get('source')}`",
        f"- Current profile manual review required: `{config.get('current_profile', {}).get('manual_review_required')}`",
        "",
        "## Warning conclusion",
        "",
        f"- Budget warning count: `{warnings.get('budget_warning_count')}`",
        f"- Last 7d budget warning count: `{warnings.get('last_7d_budget_warning_count')}`",
        f"- All descriptions removed count: `{warnings.get('all_descriptions_removed_count')}`",
        f"- Max omitted additional skills: `{warnings.get('max_omitted_additional_skills')}`",
        f"- Skipped loading count: `{warnings.get('skipped_loading_count')}`",
        f"- Highest severity: `{warning_severity.get('level')}`",
        f"- Severity reason: `{warning_severity.get('reason')}`",
        "",
        "## Warning triage",
        "",
        f"- Requested: `{warning_triage.get('requested')}`",
        f"- Status: `{warning_triage.get('status')}`",
        f"- Window policy: `{warning_triage.get('window_policy')}`",
        f"- Window OK: `{warning_triage.get('window_ok')}`",
        f"- Budget warnings in triage window: `{warning_triage.get('budget_warning_count')}`",
        f"- Skipped loading in triage window: `{warning_triage.get('skipped_loading_count')}`",
        f"- Recent skipped-loading samples: `{warning_triage.get('recent_skipped_loading_samples')}`",
        f"- Recent skipped-loading sample excerpts: {bounded_inline_list(warning_triage.get('recent_skipped_loading_sample_excerpts') or [], limit=3)}",
        f"- Skipped-loading review: `{warning_triage.get('skipped_loading_review')}`",
        f"- Recommended action: `{warning_triage.get('recommended_action')}`",
        "",
        "## Module evidence",
        "",
        "| Module | Strong total | Medium rationale | Weak mentions | Cross-project utility | Recommendation |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in report.get("module_evidence", [])[:20]:
        lines.append(
            "| {module} | {strong} | {medium} | {weak} | {cross_project} | {recommendation} |".format(
                module=row.get("module"),
                strong=row.get("strong_total"),
                medium=row.get("medium_evidence_rationale"),
                weak=row.get("weak_plugin_mentions"),
                cross_project=row.get("cross_project_utility"),
                recommendation=row.get("recommendation"),
            )
        )
    lines.extend(
        [
            "",
            "## Noise review",
            "",
            f"- Status: `{noise_review.get('status')}`",
            f"- Removed explicit-skill noise tokens: `{len(noise_review.get('explicit_skill_noise_removed', {}))}`",
            f"- Removed explicit-skill noise token samples: {format_noise_token_samples(noise_review.get('explicit_skill_noise_removed'))}",
            f"- Strong evidence policy: `{noise_review.get('strong_evidence_policy')}`",
            f"- Raw noise tokens retained: `{noise_review.get('raw_noise_tokens_retained')}`",
            f"- Max noise token length: `{noise_review.get('max_noise_token_length')}`",
            f"- Token privacy policy: `{noise_review.get('token_privacy_policy')}`",
            "",
            "## Manual evidence",
            "",
            f"- Files requested: `{manual_evidence.get('files_requested', 0)}`",
            f"- Files read: `{manual_evidence.get('files_read', 0)}`",
            f"- Valid notes: `{manual_evidence.get('valid_note_count', 0)}`",
            f"- Invalid notes: `{len(manual_evidence.get('invalid_notes', []))}`",
            f"- Raw notes retained: `{manual_evidence.get('raw_notes_retained', False)}`",
            f"- Source paths retained: `{manual_evidence.get('source_paths_retained', False)}`",
            f"- Max source path length: `{manual_evidence.get('max_path_length')}`",
            f"- Privacy policy: `{manual_evidence.get('privacy_policy')}`",
            f"- Source path privacy policy: `{manual_evidence.get('path_privacy_policy')}`",
            f"- Conflict review status: `{manual_evidence.get('conflict_review', {}).get('status')}`",
            f"- Conflict/exception count: `{manual_evidence.get('conflict_review', {}).get('conflict_or_exception_count')}`",
            f"- Conflict disposition required: `{manual_evidence.get('conflict_review', {}).get('disposition_required')}`",
            f"- Conflict policy: `{manual_evidence.get('conflict_review', {}).get('policy')}`",
            f"- Conflict disposition: `{manual_evidence.get('conflict_review', {}).get('disposition')}`",
            "",
            "## Script coverage and human review boundaries",
            "",
            f"- Policy: `{script_capabilities.get('policy')}`",
            f"- Reliable coverage items: `{len(script_capabilities.get('reliable_coverage') or [])}`",
            f"- Human-review items: `{len(script_capabilities.get('human_review_required_for') or [])}`",
            f"- Enhancement triggers: `{len(script_capabilities.get('enhancement_triggers') or [])}`",
            f"- Stable tool-call alias registry policy: `{stable_alias_registry.get('policy')}`",
            f"- Stable tool-call alias evidence level: `{stable_alias_registry.get('evidence_level')}`",
            f"- Stable tool-call aliases count as strong evidence: `{stable_alias_registry.get('counts_as_strong_evidence')}`",
            f"- Stable tool-call plugin alias targets: `{len(stable_alias_registry.get('plugin_aliases') or {})}`",
            f"- Stable tool-call module alias targets: `{len(stable_alias_registry.get('module_aliases') or {})}`",
            f"- Audit output long-term evidence format: `{output_retention.get('long_term_evidence_format')}`",
            f"- `.tmp/` outputs local only: `{output_retention.get('tmp_outputs_local_only')}`",
            f"- Raw audit JSON local only: `{output_retention.get('raw_audit_json_local_only')}`",
            f"- Pre-commit existing-file update review: `{precommit_update_archive.get('review_existing_files_for_required_updates')}`",
            f"- Pre-commit OpenSpec archive gate: `{precommit_update_archive.get('archive_completed_openspec_changes_before_commit')}`",
            f"- Pre-commit changed path count: `{precommit_update_archive.get('changed_path_count')}`",
            f"- Pre-commit active change reviews: `{precommit_update_archive.get('active_change_review_count')}`",
            f"- Runtime path raw values retained: `{runtime_paths.get('raw_paths_retained')}`",
            f"- Runtime path privacy policy: `{runtime_paths.get('privacy_policy')}`",
            "",
            "### Reliable coverage",
            "",
        ]
    )
    for item in (script_capabilities.get("reliable_coverage") or [])[:8]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "### Human review required for",
            "",
        ]
    )
    for item in (script_capabilities.get("human_review_required_for") or [])[:8]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "### Enhancement triggers",
            "",
        ]
    )
    for item in (script_capabilities.get("enhancement_triggers") or [])[:8]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "### Stable tool-call alias registry",
            "",
        ]
    )
    for target, aliases in (stable_alias_registry.get("plugin_aliases") or {}).items():
        lines.append(f"- Plugin `{target}` aliases: `{', '.join(str(alias) for alias in aliases)}`")
    for target, aliases in (stable_alias_registry.get("module_aliases") or {}).items():
        lines.append(f"- Module `{target}` aliases: `{', '.join(str(alias) for alias in aliases)}`")
    lines.extend(
        [
            "",
            "## Decision recommendation",
            "",
            f"- Decision status: `{decision_recommendation.get('status')}`",
            f"- Decision policy: `{decision_recommendation.get('policy')}`",
            f"- Warning pressure: `{decision_recommendation.get('warning_pressure')}`",
            f"- Profile apply allowed by summary: `{decision_recommendation.get('profile_apply_allowed')}`",
            f"- Profile review candidates: {bounded_inline_list(decision_buckets.get('profile_review_candidates') or [])}",
            f"- On-demand soft-load modules: {bounded_inline_list(decision_buckets.get('on_demand_soft_load') or [])}",
            f"- Manual-review medium/weak modules: {bounded_inline_list(decision_buckets.get('manual_review_medium_or_weak') or [])}",
            f"- Dormant/restorable modules: {bounded_inline_list(decision_buckets.get('dormant_restorable') or [])}",
            "- This sanitized summary is review evidence only.",
            "- Reports with failed field contracts must be rerun or fixed before profile decisions.",
            "- It does not modify `config.toml`, plugin cache, or hard-load profiles.",
            "- Create a separate profile apply candidate record before any apply action.",
            "- Review `medium_evidence_rationale` and `cross_project_utility` manually before any default-profile decision.",
            "",
            "## Risks and restore path",
            "",
            "- If a plugin is removed from the default profile later, restore through `set_plugin_profile.ps1 -RestoreLatest -Apply` or apply the prior approved profile.",
            "- Restart Codex through `codex-ohmy` after any future hard-load/profile apply.",
            "- Keep this audit summary separate from any future apply-candidate record.",
            "",
            "## Non-action list",
            "",
            "- Did not modify user-level `config.toml`.",
            "- Did not edit plugin/vendor cache.",
            "- Did not perform hard-load/profile apply.",
            "- Did not include raw session transcripts or raw log databases.",
            "",
        ]
    )
    return "\n".join(lines)


def render_candidate_markdown(candidate: dict[str, Any]) -> str:
    current = candidate.get("current_profile", {})
    target = candidate.get("target_profile", {})
    diff = candidate.get("plugin_diff", {})
    risk = candidate.get("risk_review", {})
    rollback = candidate.get("rollback_path", {})
    evidence = candidate.get("evidence_basis", {})
    target_evidence = evidence.get("target_module_evidence", {}) if isinstance(evidence, dict) else {}
    source_reports = candidate.get("source_reports", {})
    source_reports_privacy = candidate.get("source_reports_privacy", {})
    gate = candidate.get("candidate_generation_gate", {})
    candidate_contract = (
        candidate.get("candidate_record_contract")
        if isinstance(candidate.get("candidate_record_contract"), dict)
        else validate_profile_apply_candidate_contract(candidate)
    )
    candidate_contract_blockers = (
        candidate_contract.get("blockers") if isinstance(candidate_contract.get("blockers"), list) else []
    )
    lines = [
        "# Codex Skills Profile Apply Candidate",
        "",
        "## Candidate identity",
        "",
        f"- Candidate ID: `{candidate.get('candidate_id')}`",
        f"- Approval state: `{candidate.get('approval_state')}`",
        f"- Generated at: `{candidate.get('generated_at')}`",
        f"- Record type: `{candidate.get('record_type')}`",
        "",
        "## Safety",
        "",
        f"- Mutates config: `{candidate.get('mutates_config')}`",
        f"- Edits plugin cache: `{candidate.get('edits_plugin_cache')}`",
        f"- Hard-load apply performed: `{candidate.get('hard_load_apply_performed')}`",
        f"- Explicit authorization required for apply: `{candidate.get('explicit_authorization_required_for_apply')}`",
        f"- Generic continue is not apply authorization: `{candidate.get('ordinary_continue_or_generic_confirmation_is_not_apply_authorization')}`",
        f"- Candidate record contract: `{candidate_contract.get('status')}`",
        f"- Candidate record passed: `{candidate_contract.get('passed')}`",
        f"- Candidate record blockers: `{len(candidate_contract_blockers)}`",
        f"- Candidate record required fields: `{len(candidate_contract.get('required_fields') or [])}`",
        f"- Candidate record missing fields: `{len(candidate_contract.get('missing_fields') or [])}`",
        f"- Candidate record invalid-type fields: `{len(candidate_contract.get('invalid_type_fields') or [])}`",
        f"- Candidate record preview-safety violations: `{len(candidate_contract.get('preview_safety_violations') or [])}`",
        f"- Candidate record source-report-privacy violations: `{len(candidate_contract.get('source_reports_privacy_violations') or [])}`",
        f"- Candidate record gate-shape violations: `{len(candidate_contract.get('candidate_gate_violations') or [])}`",
        f"- Candidate record rollback-path violations: `{len(candidate_contract.get('rollback_path_violations') or [])}`",
        f"- Candidate record validation-plan violations: `{len(candidate_contract.get('validation_plan_violations') or [])}`",
        f"- Candidate record sanitization violations: `{len(candidate_contract.get('sanitization_violations') or [])}`",
        f"- Candidate record approval policy: `{candidate_contract.get('approval_state_policy')}`",
        f"- Candidate record blocker details: `{', '.join(candidate_contract_blockers) if candidate_contract_blockers else 'none'}`",
        "",
        "## Source reports",
        "",
        f"- JSON report: `{source_reports.get('json_report')}`",
        f"- Markdown summary: `{source_reports.get('markdown_summary')}`",
        f"- Manual notes: `{len(source_reports.get('manual_notes') or [])}`",
        f"- Privacy contract: `{source_reports_privacy.get('status')}`",
        f"- Privacy violations: `{', '.join(source_reports_privacy.get('violations') or []) or 'none'}`",
        "",
        "## Candidate generation gate",
        "",
        f"- Gate status: `{gate.get('status')}`",
        f"- Gate allowed: `{gate.get('allowed')}`",
        f"- Blockers: `{', '.join(gate.get('blockers') or []) or 'none'}`",
        f"- Summary reviewed: `{gate.get('summary_reviewed')}`",
        f"- Audit window at least 30 days: `{gate.get('audit_window_at_least_30_days')}`",
        f"- Field contract: `{(gate.get('field_contract') or {}).get('status')}`",
        "",
        "## Current and target profile",
        "",
        f"- Current inferred profile: `{current.get('inferred_profile')}`",
        f"- Current enabled plugins: `{current.get('enabled_plugins_count')}`",
        f"- Current manual review required: `{current.get('manual_review_required')}`",
        f"- Target profile: `{target.get('name')}`",
        f"- Target profile provided: `{target.get('target_profile_present')}`",
        f"- Target profile found in registry: `{target.get('known_profile')}`",
        f"- Target plugins: `{len(target.get('target_plugins') or [])}`",
        "",
        "## Plugin diff",
        "",
        f"- Add to default: `{', '.join(diff.get('add_to_default') or []) or 'none'}`",
        f"- Remove from default: `{', '.join(diff.get('remove_from_default') or []) or 'none'}`",
        f"- Keep enabled: `{', '.join(diff.get('keep_enabled') or []) or 'none'}`",
        f"- Unknown current enabled entries requiring review: `{len(diff.get('unknown_current_enabled_entries_requiring_manual_review') or [])}`",
        "",
        "## Evidence basis",
        "",
        f"- Strong total: `{target_evidence.get('strong_total')}`",
        f"- Strong helper calls: `{target_evidence.get('strong_helper_calls')}`",
        f"- Strong skill path reads: `{target_evidence.get('strong_skill_path_reads')}`",
        f"- Medium evidence rationale: `{target_evidence.get('medium_evidence_rationale')}`",
        f"- Weak plugin mentions: `{target_evidence.get('weak_plugin_mentions')}`",
        f"- Recommendation: `{target_evidence.get('recommendation')}`",
        f"- Warning severity: `{(evidence.get('warning_pressure') or {}).get('level') if isinstance(evidence, dict) else None}`",
        "",
        "## Risk review and rollback",
        "",
        f"- Risk level: `{risk.get('risk_level')}`",
        f"- Possibly disabled capabilities: `{', '.join(risk.get('possibly_disabled_capabilities') or []) or 'none'}`",
        f"- Restore command: `{rollback.get('restore_command')}`",
        f"- Restart required: `{rollback.get('restart_required')}`",
        "",
        "## Validation plan",
        "",
    ]
    for item in candidate.get("validation_plan", []):
        lines.append(f"- `{item.get('step')}`: {item.get('command') or item.get('required_evidence')}")
    lines.extend(
        [
            "",
            "## Non-action list",
            "",
            "- Did not modify user-level `config.toml`.",
            "- Did not edit plugin/vendor cache.",
            "- Did not perform hard-load/profile apply.",
            "- Did not infer approval from generic continue/confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def print_human(report: dict[str, Any]) -> None:
    audit_state = report.get("audit_state", {}) if isinstance(report.get("audit_state"), dict) else {}
    safety = report.get("safety", {}) if isinstance(report.get("safety"), dict) else {}
    runtime_paths = report.get("runtime_paths", {}) if isinstance(report.get("runtime_paths"), dict) else {}
    config_summary = report.get("config_summary", {}) if isinstance(report.get("config_summary"), dict) else {}
    inventory_summary = (
        report.get("inventory_summary") if isinstance(report.get("inventory_summary"), dict) else {}
    )
    log_evidence = report.get("log_evidence", {}) if isinstance(report.get("log_evidence"), dict) else {}
    warning_severity = (
        report.get("warning_severity") if isinstance(report.get("warning_severity"), dict) else {}
    )
    warning_triage = report.get("warning_triage", {}) if isinstance(report.get("warning_triage"), dict) else {}
    cadence_review = report.get("cadence_review", {}) if isinstance(report.get("cadence_review"), dict) else {}
    noise_review = report.get("noise_review", {}) if isinstance(report.get("noise_review"), dict) else {}
    manual_evidence = report.get("manual_evidence", {}) if isinstance(report.get("manual_evidence"), dict) else {}
    manual_conflict_review = (
        manual_evidence.get("conflict_review")
        if isinstance(manual_evidence.get("conflict_review"), dict)
        else {}
    )
    session_evidence = report.get("session_evidence", {}) if isinstance(report.get("session_evidence"), dict) else {}
    script_capabilities = (
        report.get("script_capability_boundaries")
        if isinstance(report.get("script_capability_boundaries"), dict)
        else {}
    )
    stable_alias_registry = (
        script_capabilities.get("stable_tool_call_alias_registry")
        if isinstance(script_capabilities.get("stable_tool_call_alias_registry"), dict)
        else {}
    )
    decision_recommendation = (
        report.get("decision_recommendation")
        if isinstance(report.get("decision_recommendation"), dict)
        else {}
    )
    decision_buckets = (
        decision_recommendation.get("buckets")
        if isinstance(decision_recommendation.get("buckets"), dict)
        else {}
    )
    decision_bucket_counts = (
        decision_recommendation.get("bucket_counts")
        if isinstance(decision_recommendation.get("bucket_counts"), dict)
        else {}
    )
    field_contract = report.get("field_contract", {}) if isinstance(report.get("field_contract"), dict) else {}
    field_contract_blockers = field_contract.get("blockers") if isinstance(field_contract.get("blockers"), list) else []
    output_retention = report.get("output_retention", {}) if isinstance(report.get("output_retention"), dict) else {}
    precommit_update_archive = (
        report.get("precommit_update_archive")
        if isinstance(report.get("precommit_update_archive"), dict)
        else {}
    )
    current_profile = (
        config_summary.get("current_profile") if isinstance(config_summary.get("current_profile"), dict) else {}
    )
    enabled_plugins = config_summary.get("enabled_plugins") if isinstance(config_summary.get("enabled_plugins"), list) else []
    explicit_skills = (
        session_evidence.get("explicit_skills") if isinstance(session_evidence.get("explicit_skills"), dict) else {}
    )
    audit_state_blockers = [
        str(blocker)
        for field in AUDIT_STATE_BLOCKER_FIELDS
        for blocker in (audit_state.get(field) if isinstance(audit_state.get(field), list) else [])
        if blocker is not None
    ]
    recommendations = report.get("recommendations") if isinstance(report.get("recommendations"), list) else []
    print(f"Codex skills usage audit ({report['mode']})")
    print(f"Window: {report['audit_window']['since']} -> {report['audit_window']['until']}")
    print(
        "Enabled plugins: "
        f"{len(enabled_plugins)} "
        f"matched_known={len(current_profile.get('matched_enabled_known_plugins') or [])} "
        f"unmatched={len(current_profile.get('unmatched_enabled_plugin_entries') or [])}"
    )
    print(
        "Current profile: "
        f"inferred={current_profile.get('inferred_profile')} "
        f"exact_matches={len(current_profile.get('exact_profile_matches') or [])} "
        f"closest_matches={len(current_profile.get('closest_profile_matches') or [])} "
        f"manual_review_required={current_profile.get('manual_review_required')}"
    )
    print(
        "Inventory summary: "
        f"total={inventory_summary.get('total_skills')} "
        f"user={inventory_summary.get('user_skills')} "
        f"repo={inventory_summary.get('repo_skills')} "
        f"plugin={inventory_summary.get('plugin_skills')}"
    )
    print(f"Log evidence available: {log_evidence.get('available')}")
    print(f"Budget warnings: {log_evidence.get('budget_warning_count')}")
    print(
        "Budget warning samples: "
        f"recent={len(log_evidence.get('recent_budget_warnings') or [])} "
        f"last_7d={log_evidence.get('last_7d_budget_warning_count')}"
    )
    print(
        "Warning severity: "
        f"{warning_severity.get('level')} "
        f"reason={warning_severity.get('reason')} "
        f"action={warning_severity.get('recommended_action')}"
    )
    print(
        "Budget warning pressure: "
        f"all_descriptions_removed={log_evidence.get('all_descriptions_removed_count')} "
        f"last_7d_all_descriptions_removed={log_evidence.get('last_7d_all_descriptions_removed_count')} "
        f"max_omitted_additional_skills={log_evidence.get('max_omitted_additional_skills')}"
    )
    print(f"Audit state: {audit_state.get('state')} ({audit_state.get('reason')})")
    print(f"Audit next action: {audit_state.get('next_action')}")
    print(f"Profile apply allowed: {audit_state.get('profile_apply_allowed')}")
    print(
        "Audit state blockers: "
        f"{', '.join(audit_state_blockers) if audit_state_blockers else 'none'}"
    )
    print(
        "Audit-only safety: "
        f"audit_only={safety.get('audit_only')} "
        f"mutates_config={safety.get('mutates_config')} "
        f"edits_plugin_cache={safety.get('edits_plugin_cache')} "
        f"hard_load_apply_performed={safety.get('hard_load_apply_performed')}"
    )
    print(
        "Runtime path privacy: "
        f"raw_paths_retained={runtime_paths.get('raw_paths_retained')} "
        f"policy={runtime_paths.get('privacy_policy')}"
    )
    print(
        "Runtime path placeholders: "
        f"root={runtime_paths.get('root')} "
        f"codex_home={runtime_paths.get('codex_home')} "
        f"config_path={runtime_paths.get('config_path')}"
    )
    print(
        "Cadence review: "
        f"late_run={cadence_review.get('late_run')} "
        f"missed_weekly_runs={cadence_review.get('missed_weekly_runs')} "
        f"weekly_report_review={cadence_review.get('weekly_report_review')}"
    )
    print(
        "Warning triage: "
        f"{warning_triage.get('status')} "
        f"requested={warning_triage.get('requested')} "
        f"window_ok={warning_triage.get('window_ok')}"
    )
    print(f"Warning triage policy: {warning_triage.get('window_policy')}")
    print(
        "Warning triage warnings: "
        f"budget={warning_triage.get('budget_warning_count')} "
        f"skipped_loading={warning_triage.get('skipped_loading_count')} "
        f"recent_skipped_samples={warning_triage.get('recent_skipped_loading_samples')}"
    )
    print(
        "Warning triage skipped-loading sample excerpts: "
        f"{bounded_inline_list(warning_triage.get('recent_skipped_loading_sample_excerpts') or [], limit=3)}"
    )
    print(f"Warning triage skipped-loading review: {warning_triage.get('skipped_loading_review')}")
    print(f"Warning triage recommended action: {warning_triage.get('recommended_action')}")
    warning_triage_blockers = warning_triage.get("blockers") if isinstance(warning_triage.get("blockers"), list) else []
    print(
        "Warning triage blockers: "
        f"{', '.join(str(blocker) for blocker in warning_triage_blockers) if warning_triage_blockers else 'none'}"
    )
    print(
        "Explicit skill usages: "
        f"total={sum(explicit_skills.values())} "
        f"unique={len(explicit_skills)}"
    )
    print(f"Skill path reads: {sum((session_evidence.get('skill_paths') or {}).values())}")
    print(f"Profile helper calls: {sum((session_evidence.get('profile_helper_calls') or {}).values())}")
    print(
        "Noise review: "
        f"status={noise_review.get('status')} "
        f"removed={len(noise_review.get('explicit_skill_noise_removed') or {})} "
        f"raw_retained={noise_review.get('raw_noise_tokens_retained')} "
        f"max_token_length={noise_review.get('max_noise_token_length')}"
    )
    print(f"Noise privacy policy: {noise_review.get('token_privacy_policy')}")
    print(
        "Manual evidence: "
        f"files_requested={manual_evidence.get('files_requested')} "
        f"files_read={manual_evidence.get('files_read')} "
        f"valid={manual_evidence.get('valid_note_count')} "
        f"invalid={len(manual_evidence.get('invalid_notes') or [])} "
        f"raw_retained={manual_evidence.get('raw_notes_retained')} "
        f"source_paths_retained={manual_evidence.get('source_paths_retained')} "
        f"max_path_length={manual_evidence.get('max_path_length')}"
    )
    print(f"Manual evidence privacy policy: {manual_evidence.get('privacy_policy')}")
    print(f"Manual evidence path privacy policy: {manual_evidence.get('path_privacy_policy')}")
    print(
        "Manual conflict review: "
        f"status={manual_conflict_review.get('status')} "
        f"conflicts={manual_conflict_review.get('conflict_or_exception_count')} "
        f"disposition_required={manual_conflict_review.get('disposition_required')} "
        f"disposition={manual_conflict_review.get('disposition')}"
    )
    print(
        "Script capability boundaries: "
        f"reliable={len(script_capabilities.get('reliable_coverage') or [])} "
        f"human_review={len(script_capabilities.get('human_review_required_for') or [])} "
        f"enhancement_triggers={len(script_capabilities.get('enhancement_triggers') or [])}"
    )
    print(
        "Stable tool-call alias registry: "
        f"policy={stable_alias_registry.get('policy')} "
        f"evidence_level={stable_alias_registry.get('evidence_level')} "
        f"counts_as_strong_evidence={stable_alias_registry.get('counts_as_strong_evidence')}"
    )
    print(
        "Stable tool-call alias targets: "
        f"plugin={len(stable_alias_registry.get('plugin_aliases') or {})} "
        f"module={len(stable_alias_registry.get('module_aliases') or {})}"
    )
    print(
        "Stable tool-call plugin alias targets: "
        f"{format_alias_targets_for_human(stable_alias_registry.get('plugin_aliases') or {})}"
    )
    print(
        "Stable tool-call module alias targets: "
        f"{format_alias_targets_for_human(stable_alias_registry.get('module_aliases') or {})}"
    )
    print(
        "Decision recommendation: "
        f"{decision_recommendation.get('status')} "
        f"profile_apply_allowed={decision_recommendation.get('profile_apply_allowed')}"
    )
    print(
        "Decision recommendation buckets: "
        f"profile_review_candidates={decision_bucket_counts.get('profile_review_candidates')} "
        f"on_demand_soft_load={decision_bucket_counts.get('on_demand_soft_load')} "
        f"manual_review_medium_or_weak={decision_bucket_counts.get('manual_review_medium_or_weak')} "
        f"dormant_restorable={decision_bucket_counts.get('dormant_restorable')}"
    )
    print(
        "Decision profile review candidates: "
        f"{bounded_inline_list(decision_buckets.get('profile_review_candidates') or [])}"
    )
    print(
        "Decision on-demand soft-load modules: "
        f"{bounded_inline_list(decision_buckets.get('on_demand_soft_load') or [])}"
    )
    print(
        "Decision manual-review medium/weak modules: "
        f"{bounded_inline_list(decision_buckets.get('manual_review_medium_or_weak') or [])}"
    )
    print(
        "Decision dormant/restorable modules: "
        f"{bounded_inline_list(decision_buckets.get('dormant_restorable') or [])}"
    )
    print(f"Recommendations: {len(recommendations)}")
    for recommendation in recommendations[:2]:
        print(f"  - {recommendation}")
    print(f"Field contract: {field_contract.get('status')}")
    print(
        "Field contract details: "
        f"passed={field_contract.get('passed')} "
        f"blockers={len(field_contract_blockers)} "
        f"required_fields={len(field_contract.get('required_fields') or [])} "
        f"missing_fields={len(field_contract.get('missing_fields') or [])} "
        f"invalid_type_fields={len(field_contract.get('invalid_type_fields') or [])} "
        f"requires_embedded={field_contract.get('requires_embedded_field_contract')}"
    )
    print(
        "Field contract violation groups: "
        f"safety={len(field_contract.get('safety_violations') or [])} "
        f"audit_state={len(field_contract.get('audit_state_violations') or [])} "
        f"log_evidence={len(field_contract.get('log_evidence_violations') or [])} "
        f"warning_triage={len(field_contract.get('warning_triage_violations') or [])} "
        f"cadence_review={len(field_contract.get('cadence_review_violations') or [])} "
        f"manual_evidence={len(field_contract.get('manual_evidence_violations') or [])} "
        f"noise_review={len(field_contract.get('noise_review_violations') or [])} "
        f"script_capability={len(field_contract.get('script_capability_boundary_violations') or [])} "
        f"output_retention={len(field_contract.get('output_retention_violations') or [])} "
        f"precommit_update_archive={len(field_contract.get('precommit_update_archive_violations') or [])} "
        f"runtime_paths={len(field_contract.get('runtime_path_violations') or [])} "
        f"module_evidence={len(field_contract.get('module_evidence_violations') or [])} "
        f"decision_recommendation={len(field_contract.get('decision_recommendation_violations') or [])} "
        f"embedded={len(field_contract.get('embedded_field_contract_violations') or [])}"
    )
    print(f"Output retention gate: {output_retention.get('status')}")
    print(
        "Output retention details: "
        f"checker={output_retention.get('checker')} "
        f"violations={output_retention.get('violation_count')} "
        f"tmp_outputs_local_only={output_retention.get('tmp_outputs_local_only')} "
        f"raw_audit_json_local_only={output_retention.get('raw_audit_json_local_only')} "
        f"long_term_evidence_format={output_retention.get('long_term_evidence_format')}"
    )
    print(
        "Pre-commit update/archive gate: "
        f"{precommit_update_archive.get('status')} "
        f"errors={precommit_update_archive.get('error_count')} "
        f"warnings={precommit_update_archive.get('warning_count')}"
    )
    print(
        "Pre-commit update/archive details: "
        f"checker={precommit_update_archive.get('checker')} "
        f"before_local_git_commit={precommit_update_archive.get('before_local_git_commit')} "
        f"review_existing_files={precommit_update_archive.get('review_existing_files_for_required_updates')} "
        f"archive_completed_openspec={precommit_update_archive.get('archive_completed_openspec_changes_before_commit')} "
        f"changed_paths={precommit_update_archive.get('changed_path_count')} "
        f"active_change_reviews={precommit_update_archive.get('active_change_review_count')}"
    )
    if field_contract.get("blockers"):
        print("Field contract blockers:")
        for blocker in field_contract.get("blockers", [])[:10]:
            print(f"  - {blocker}")
    if output_retention.get("violation_reasons"):
        print("Output retention violations:")
        for reason in output_retention.get("violation_reasons", [])[:10]:
            print(f"  - {reason}")
    if precommit_update_archive.get("error_reasons"):
        print("Pre-commit update/archive errors:")
        for reason in precommit_update_archive.get("error_reasons", [])[:10]:
            print(f"  - {reason}")
    print("Top explicit skills:")
    for name, count in list(explicit_skills.items())[:10]:
        print(f"  {name}: {count}")
    print("Top module evidence:")
    for row in report.get("module_evidence", [])[:20]:
        print(
            f"  {row['module']}: strong={row['strong_helper_calls'] + row['strong_skill_path_reads']} "
            f"weak={row['weak_plugin_mentions']} recommendation={row['recommendation']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Codex skills/plugin usage evidence without mutating config.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--codex-home", default=None, help="Codex home directory. Defaults to %%CODEX_HOME%% or ~/.codex.")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days.")
    parser.add_argument("--since", default=None, help="UTC date override, e.g. 2026-05-01.")
    parser.add_argument("--baseline", action="store_true", help="Label the report as a baseline snapshot.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", default=None, help="Optional path to write JSON report.")
    parser.add_argument("--summary-output", default=None, help="Optional path to write sanitized Markdown summary.")
    parser.add_argument("--late-run", action="store_true", help="Mark this run as a late cadence recovery run.")
    parser.add_argument(
        "--warning-triage",
        action="store_true",
        help="Mark this run as a post-warning triage run. Use with --days 1 or --since covering the warning time.",
    )
    parser.add_argument(
        "--planned-audit",
        action="store_true",
        help="Record an audit-only planned state before the Day 0 baseline is generated.",
    )
    parser.add_argument(
        "--pause-audit",
        choices=("data-source-missing", "privacy-review", "script-defect"),
        default=None,
        help="Record an audit-only paused state for missing data, privacy review, or script defects without profile apply.",
    )
    parser.add_argument(
        "--missed-weekly-runs",
        type=int,
        default=None,
        help="Optional manual count of missed weekly audit runs for the summary.",
    )
    parser.add_argument(
        "--manual-notes",
        action="append",
        default=[],
        help="Optional sanitized Markdown manual-evidence note file. May be passed multiple times.",
    )
    parser.add_argument(
        "--candidate-output",
        default=None,
        help="Optional path to write a preview-only profile apply candidate JSON record.",
    )
    parser.add_argument(
        "--candidate-summary-output",
        default=None,
        help="Optional path to write a sanitized Markdown summary for the preview-only candidate record.",
    )
    parser.add_argument(
        "--candidate-id",
        default=None,
        help="Optional candidate change ID. Defaults to skills-profile-YYYY-MM-DD-<target-profile>.",
    )
    parser.add_argument(
        "--target-profile",
        default=None,
        help="Target profile/module name for --candidate-output, for example core-dev or web-saas.",
    )
    parser.add_argument(
        "--summary-reviewed",
        action="store_true",
        help="Mark the sanitized 30-day Markdown summary as human-reviewed before generating a candidate.",
    )
    parser.add_argument(
        "--close-audit",
        choices=("no-change", "with-candidate"),
        default=None,
        help="Record a preview-only audit closure state after the 30-day summary is reviewed.",
    )
    args = parser.parse_args()

    report = build_report(args)
    candidate = None
    if args.candidate_output or args.candidate_summary_output:
        candidate_gate = build_candidate_generation_gate(
            report,
            summary_reviewed=args.summary_reviewed,
            json_report_path=args.output,
            markdown_summary_path=args.summary_output,
            require_source_reports=True,
            target_profile=args.target_profile,
            require_target_profile=True,
        )
        candidate = build_profile_apply_candidate(
            report,
            candidate_id=args.candidate_id,
            target_profile=args.target_profile,
            source_reports=build_source_reports(args.output, args.summary_output, args.manual_notes),
            candidate_gate=candidate_gate,
        )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.summary_output:
        summary_output = Path(args.summary_output)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(render_markdown_summary(report), encoding="utf-8")
    if args.candidate_output and candidate is not None:
        candidate_output = Path(args.candidate_output)
        candidate_output.parent.mkdir(parents=True, exist_ok=True)
        candidate_output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.candidate_summary_output and candidate is not None:
        candidate_summary_output = Path(args.candidate_summary_output)
        candidate_summary_output.parent.mkdir(parents=True, exist_ok=True)
        candidate_summary_output.write_text(render_candidate_markdown(candidate), encoding="utf-8")
    if args.json:
        emit_stdout(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
