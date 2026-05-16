#!/usr/bin/env python3
"""Audit Codex skills/plugin usage without mutating user configuration.

The report is evidence-oriented: it separates strong evidence (explicit skill
announcements, SKILL.md reads, profile helper calls, and budget warnings) from
weak text mentions. It never edits config.toml or plugin cache files.
"""
from __future__ import annotations

import argparse
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
ACCESS_TOKEN_PATTERN = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie)\s*[:=]\s*([^\s,;]+)")
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
    "audit_window",
    "safety",
    "config_summary",
    "inventory_summary",
    "log_evidence",
    "session_evidence",
    "manual_evidence",
    "module_evidence",
    "cadence_review",
    "recommendations",
}
REQUIRED_REPORT_FIELD_TYPES = {
    "audit_window": dict,
    "safety": dict,
    "config_summary": dict,
    "inventory_summary": dict,
    "log_evidence": dict,
    "session_evidence": dict,
    "manual_evidence": dict,
    "module_evidence": list,
    "cadence_review": dict,
    "recommendations": list,
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


def sanitize_log_excerpt(text: str, limit: int = 500) -> str:
    sanitized = WINDOWS_PATH_PATTERN.sub("[REDACTED_PATH]", text)
    sanitized = ACCESS_TOKEN_PATTERN.sub(lambda m: m.group(0).replace(m.group(1), "[REDACTED_SECRET]"), sanitized)
    return sanitized[:limit]


def sanitize_manual_value(value: str, limit: int = 300) -> str:
    return sanitize_log_excerpt(value.strip(), limit=limit)


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


def collect_manual_notes(paths: list[str]) -> dict[str, Any]:
    notes: list[dict[str, str]] = []
    invalid: list[dict[str, Any]] = []
    files_read = 0
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            invalid.append({"path": raw_path, "reason": "missing_file"})
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
                        "path": str(path),
                        "note_index": index,
                        "missing_fields": missing,
                        "invalid_fields": invalid_values,
                    }
                )
                continue
            notes.append(note)
    counts_by_level = Counter(note["evidence_level"] for note in notes)
    counts_by_action = Counter(note["action_taken"] for note in notes)
    return {
        "files_requested": len(paths),
        "files_read": files_read,
        "notes": notes,
        "valid_note_count": len(notes),
        "invalid_notes": invalid,
        "counts_by_evidence_level": dict(counts_by_level),
        "counts_by_action": dict(counts_by_action),
        "raw_notes_retained": False,
        "privacy_policy": "manual_notes_are_sanitized_markdown_fields_only_no_raw_transcripts",
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
                            explicit_skill_noise[name] += 1
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


def source_report_paths_ready(args: argparse.Namespace) -> bool:
    return bool(str(getattr(args, "output", "") or "").strip()) and bool(
        str(getattr(args, "summary_output", "") or "").strip()
    )


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
    close_audit = getattr(args, "close_audit", None)
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
    if candidate_requested and summary_reviewed and window_at_least_30_days and source_paths_ready:
        return {
            "state": "apply-candidate",
            "reason": "profile_apply_candidate_preview_requested_after_summary_review",
            "next_action": "review_preview_candidate_and_request_explicit_apply_authorization_if_accepted",
            "profile_apply_allowed": False,
        }
    if candidate_requested and summary_reviewed and window_at_least_30_days and not source_paths_ready:
        return {
            "state": "ready-for-summary",
            "reason": "profile_apply_candidate_source_report_paths_missing",
            "next_action": "regenerate_with_output_and_summary_output_before_candidate_review",
            "profile_apply_allowed": False,
            "candidate_blockers": ["source_report_paths_missing"],
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
    config = report.get("config_summary") if isinstance(report.get("config_summary"), dict) else {}
    config_violations = []
    if "current_profile" not in config:
        config_violations.append("current_profile_missing")
    log_evidence = report.get("log_evidence") if isinstance(report.get("log_evidence"), dict) else {}
    log_violations = []
    for field in ("budget_warning_count", "last_7d_budget_warning_count"):
        if field not in log_evidence:
            log_violations.append(f"{field}_missing")
    manual_evidence = report.get("manual_evidence") if isinstance(report.get("manual_evidence"), dict) else {}
    manual_violations = []
    if "valid_note_count" not in manual_evidence:
        manual_violations.append("valid_note_count_missing")
    blockers = (
        [f"missing_field:{field}" for field in missing_fields]
        + [f"invalid_type:{field}" for field in invalid_type_fields]
        + [f"safety:{field}" for field in safety_violations]
        + [f"config_summary:{field}" for field in config_violations]
        + [f"log_evidence:{field}" for field in log_violations]
        + [f"manual_evidence:{field}" for field in manual_violations]
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
        "config_summary_violations": config_violations,
        "log_evidence_violations": log_violations,
        "manual_evidence_violations": manual_violations,
        "embedded_field_contract_violations": embedded_violations,
    }


def build_candidate_generation_gate(
    report: dict[str, Any],
    summary_reviewed: bool,
    *,
    json_report_path: str | None = None,
    markdown_summary_path: str | None = None,
    require_source_reports: bool = False,
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
    json_report_present = bool(str(json_report_path or "").strip())
    markdown_summary_present = bool(str(markdown_summary_path or "").strip())
    if require_source_reports and not json_report_present:
        blockers.append("source_report_json_missing")
    if require_source_reports and not markdown_summary_present:
        blockers.append("source_report_markdown_summary_missing")
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
    total = 0
    for tool_name, count in tool_call_counts.items():
        tool_key = normalize_name_for_match(tool_name)
        if module_key and module_key in tool_key:
            total += count
            continue
        if any(plugin_key and plugin_key in tool_key for plugin_key in plugin_keys):
            total += count
    return total


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
        if strong_total >= 10:
            recommendation = "candidate_for_project_or_default_profile_review"
        elif strong_total > 0:
            recommendation = "keep_module_on_demand_and_continue_audit"
        elif weak > 0:
            recommendation = "mentioned_only_do_not_apply_without_strong_evidence"
        else:
            recommendation = "no_recent_evidence_keep_dormant_not_deleted"
        rows.append(
            {
                "module": module_name,
                "plugins": plugins,
                "strong_helper_calls": helper,
                "strong_skill_path_reads": strong_path,
                "strong_total": strong_total,
                "default_candidate_threshold": 10,
                "mapped_tool_call_mentions": mapped_tools,
                "mapped_tool_call_policy": "medium_evidence_only_not_counted_as_strong_evidence",
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
    }


def slugify_candidate_part(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "profile"


def sanitize_source_report_path(value: str | None) -> str | None:
    if not value:
        return None
    return sanitize_log_excerpt(str(value), limit=300)


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
    if not target_profile:
        raise ValueError("target_profile is required for a profile apply candidate")
    candidate_gate = candidate_gate or build_candidate_generation_gate(report, summary_reviewed=False)

    generated_at = str(report.get("generated_at") or now_utc().isoformat())
    generated_day = generated_at[:10] if len(generated_at) >= 10 else now_utc().date().isoformat()
    candidate_id = candidate_id or f"skills-profile-{generated_day}-{slugify_candidate_part(target_profile)}"

    config = report.get("config_summary", {})
    current_profile = config.get("current_profile", {}) if isinstance(config, dict) else {}
    enabled_known = sorted(current_profile.get("matched_enabled_known_plugins") or [])
    enabled_known_set = set(enabled_known)
    target_row = find_module_evidence_row(report, target_profile)
    target_plugins = sorted(target_row.get("plugins", [])) if target_row else []
    target_plugin_set = set(target_plugins)

    add_to_default = sorted(target_plugin_set - enabled_known_set)
    remove_from_default = sorted(enabled_known_set - target_plugin_set)
    keep_enabled = sorted(target_plugin_set & enabled_known_set)
    unknown_enabled = list(current_profile.get("unmatched_enabled_plugin_entries") or [])

    evidence_basis = {
        "target_profile": target_profile,
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
        "source_reports": source_reports or build_source_reports(),
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
            "name": target_profile,
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
    audit_state = build_audit_state(args, cutoff, generated_at)
    current_profile = build_current_profile_summary(profiles, enabled_plugins)
    manual_notes = collect_manual_notes(getattr(args, "manual_notes", []) or [])
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
        "root": str(root),
        "codex_home": str(codex_home),
        "safety": {
            "mutates_config": False,
            "edits_plugin_cache": False,
            "hard_load_apply_performed": False,
            "audit_only": True,
        },
        "config_summary": {
            "config_path": str(codex_home / "config.toml"),
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
        "session_evidence": session_data,
        "module_evidence": module_evidence,
        "noise_review": noise_review,
        "manual_evidence": manual_notes,
        "recommendations": [
            "Do not treat another 2% budget warning as soft-load failure; soft-load is outside the model-visible skills budget surface.",
            "Continue audit-only mode until the agreed window closes unless a concrete task requires a profile preview or explicitly approved hard-load apply.",
            "Use strong evidence, not weak mentions, to decide default profile changes.",
            "Keep disabled plugins restorable; do not delete plugin cache or vendor SKILL.md files.",
        ],
    }
    report["field_contract"] = validate_report_field_contract(report)
    return report


def render_markdown_summary(report: dict[str, Any]) -> str:
    audit_window = report.get("audit_window", {})
    config = report.get("config_summary", {})
    warnings = report.get("log_evidence", {})
    warning_severity = report.get("warning_severity", {})
    noise_review = report.get("noise_review", {})
    manual_evidence = report.get("manual_evidence", {})
    audit_state = report.get("audit_state", {})
    field_contract = report.get("field_contract", {})
    lines = [
        "# Codex Skills Usage Audit Summary",
        "",
        "## Audit window",
        "",
        f"- Since: `{audit_window.get('since')}`",
        f"- Until: `{audit_window.get('until')}`",
        f"- Days: `{audit_window.get('days')}`",
        f"- Audit state: `{audit_state.get('state')}` ({audit_state.get('reason')})",
        f"- Field contract: `{field_contract.get('status')}`",
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
            f"- Strong evidence policy: `{noise_review.get('strong_evidence_policy')}`",
            "",
            "## Manual evidence",
            "",
            f"- Files requested: `{manual_evidence.get('files_requested', 0)}`",
            f"- Files read: `{manual_evidence.get('files_read', 0)}`",
            f"- Valid notes: `{manual_evidence.get('valid_note_count', 0)}`",
            f"- Invalid notes: `{len(manual_evidence.get('invalid_notes', []))}`",
            f"- Raw notes retained: `{manual_evidence.get('raw_notes_retained', False)}`",
            f"- Privacy policy: `{manual_evidence.get('privacy_policy')}`",
            "",
            "## Decision recommendation",
            "",
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
    gate = candidate.get("candidate_generation_gate", {})
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
        "",
        "## Source reports",
        "",
        f"- JSON report: `{source_reports.get('json_report')}`",
        f"- Markdown summary: `{source_reports.get('markdown_summary')}`",
        f"- Manual notes: `{len(source_reports.get('manual_notes') or [])}`",
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
    print(f"Codex skills usage audit ({report['mode']})")
    print(f"Window: {report['audit_window']['since']} -> {report['audit_window']['until']}")
    print(f"Enabled plugins: {len(report['config_summary']['enabled_plugins'])}")
    print(f"Budget warnings: {report['log_evidence'].get('budget_warning_count')}")
    print("Top explicit skills:")
    for name, count in list(report["session_evidence"].get("explicit_skills", {}).items())[:10]:
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
