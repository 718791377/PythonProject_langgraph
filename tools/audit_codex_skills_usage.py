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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


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


def build_audit_state(args: argparse.Namespace) -> dict[str, Any]:
    if args.baseline:
        return {
            "state": "running",
            "reason": "baseline_generated",
            "next_action": "continue_weekly_reports_warning_triage_and_manual_notes",
            "profile_apply_allowed": False,
        }
    if args.days >= 30:
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
    audit_state = build_audit_state(args)
    current_profile = build_current_profile_summary(profiles, enabled_plugins)
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
        "recommendations": [
            "Do not treat another 2% budget warning as soft-load failure; soft-load is outside the model-visible skills budget surface.",
            "Continue audit-only mode until the agreed window closes unless a concrete task requires a profile preview or explicitly approved hard-load apply.",
            "Use strong evidence, not weak mentions, to decide default profile changes.",
            "Keep disabled plugins restorable; do not delete plugin cache or vendor SKILL.md files.",
        ],
    }
    return report


def render_markdown_summary(report: dict[str, Any]) -> str:
    audit_window = report.get("audit_window", {})
    config = report.get("config_summary", {})
    warnings = report.get("log_evidence", {})
    warning_severity = report.get("warning_severity", {})
    noise_review = report.get("noise_review", {})
    audit_state = report.get("audit_state", {})
    lines = [
        "# Codex Skills Usage Audit Summary",
        "",
        "## Audit window",
        "",
        f"- Since: `{audit_window.get('since')}`",
        f"- Until: `{audit_window.get('until')}`",
        f"- Days: `{audit_window.get('days')}`",
        f"- Audit state: `{audit_state.get('state')}` ({audit_state.get('reason')})",
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
            "## Decision recommendation",
            "",
            "- This sanitized summary is review evidence only.",
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
    args = parser.parse_args()

    report = build_report(args)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.summary_output:
        summary_output = Path(args.summary_output)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(render_markdown_summary(report), encoding="utf-8")
    if args.json:
        emit_stdout(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
