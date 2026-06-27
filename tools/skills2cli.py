#!/usr/bin/env python3
"""Compact, sanitized Codex skill discovery helper.

This repository-local MVP intentionally does not mutate Codex configuration,
plugin cache files, or user-level wrappers. It provides low-token JSON summaries
for skill discovery, profile suggestions, and warning audits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from codex_skill_frontmatter import (  # noqa: E402
    CODEX_SKILL_DESCRIPTION_LIMIT,
    CODEX_SKILL_NAME_LIMIT,
    codex_frontmatter_report,
)
from skills2cli_profile_registry_contract import (  # noqa: E402
    as_string_list,
    explicit_full_selection_reason,
    is_explicit_full_request,
    load_profile_registry as load_profile_registry_contract,
    plugin_hints as contract_plugin_hints,
    scene_description as contract_scene_description,
    skill_doc_hints as contract_skill_doc_hints,
    task_module_identity,
)

SCHEMA_VERSION = 1
SUMMARY_LIMIT = 160
SHOW_BODY_LIMIT = 20000
WARNING_EXCERPT_LIMIT = 240
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|]+(?:\\[^\s\"'<>|]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|]+")
TOKEN_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")
STANDALONE_SECRET_RE = re.compile(r"(?i)\b(?:sk-[a-z0-9_-]{6,}|xox[baprs]-[a-z0-9_-]{6,}|gh[pousr]_[a-z0-9_]{8,})\b")
UUID_RE = re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
CALL_ID_RE = re.compile(r"\bcall_[A-Za-z0-9_-]{8,}\b")
RESPONSE_ID_RE = re.compile(r"\bresp_[A-Za-z0-9_-]{8,}\b")
RUNTIME_ID_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(thread_id|session_id|conversation_id|turn_id|submission\.id|rpc\.request_id|request_id|connection_id)"
    r"\s*=\s*(?:\\?\"[^\"\s,;)}]+\\?\"|[^\s,;)}]+)"
)
TOKEN_COUNTER_RE = re.compile(r"(?i)\b(?:input|output|total|cached)[_-]?tokens?\s*[:=]\s*\d+\b")
BUDGET_WARNING_RE = re.compile(r"Exceeded skills context budget of 2%", re.IGNORECASE)
SKIPPED_LOADING_RE = re.compile(r"Skipped loading\s+\d+\s+skill|Skipped loading|invalid SKILL\.md|missing YAML frontmatter", re.IGNORECASE)
OMITTED_ADDITIONAL_RE = re.compile(r"(\d+)\s+additional skills were not included", re.IGNORECASE)
ALL_DESCRIPTIONS_REMOVED_RE = re.compile(r"All skill descriptions were removed", re.IGNORECASE)
BUDGET_INTENT_TERMS = (
    "Exceeded skills context budget",
    "skills context budget",
    "All skill descriptions were removed",
    "additional skills were not included",
    "model-visible skills list",
    "skill descriptions removed",
    "context compacted",
    "compaction",
    "上下文压缩",
    "技能上下文预算",
    "skills预算",
)
BUDGET_TRIAGE_PROFILE = "core-dev"
BUDGET_TRIAGE_SCENARIO = "skills-budget-triage"
BUDGET_TRIAGE_TASK_MODULE = "skills-budget-triage"


@dataclass(frozen=True)
class SkillRecord:
    skill_id: str
    name: str
    source_layer: str
    path_hint: str
    description_summary: str
    description_hash: str
    available: bool
    frontmatter_valid: bool
    frontmatter_error: str | None
    codex_frontmatter_compatible: bool
    codex_frontmatter_errors: list[str]
    name_length: int
    description_length: int
    full_body_included: bool = False


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_text(value: str, *, limit: int | None = None) -> str:
    text = str(value)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = TOKEN_RE.sub(lambda match: match.group(0).split(match.group(1))[0] + "[REDACTED_SECRET]", text)
    text = STANDALONE_SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = RUNTIME_ID_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}=[REDACTED_ID]", text)
    text = CALL_ID_RE.sub("[REDACTED_ID]", text)
    text = RESPONSE_ID_RE.sub("[REDACTED_ID]", text)
    text = UUID_RE.sub("[REDACTED_ID]", text)
    text = TOKEN_COUNTER_RE.sub("[REDACTED_TOKEN_COUNT]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit is not None and len(text) > limit:
        return text[: max(0, limit - len("...[truncated]"))].rstrip() + "...[truncated]"
    return text


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._/-]+", "-", value.strip().replace("\\", "/"))
    slug = re.sub(r"-+", "-", slug).strip("-/.")
    return slug or "skill"


def read_text_lossy(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> tuple[dict[str, str], bool, str | None, str]:
    if text.startswith("\ufeff"):
        text = text[1:]
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return {}, False, "missing_yaml_frontmatter", normalized
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return {}, False, "unterminated_yaml_frontmatter", normalized
    raw = normalized[4:end]
    body = normalized[end + len("\n---\n") :]
    data: dict[str, str] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_key:
            data[current_key] = (data[current_key] + " " + line.strip()).strip()
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")
        if key:
            data[key] = value
            current_key = key
    missing = [key for key in ("name", "description") if not data.get(key)]
    if missing:
        return data, False, "missing_" + "_".join(missing), body
    return data, True, None, body


def skill_roots(repo_root: Path, codex_home: Path) -> list[tuple[str, Path, str]]:
    return [
        ("repo", repo_root / ".codex" / "skills", "[REPO_SKILLS]"),
        ("system", codex_home / "skills" / ".system", "[SYSTEM_SKILLS]"),
        ("user", codex_home / "skills", "[CODEX_SKILLS]"),
        ("plugin", codex_home / "plugins" / "cache", "[PLUGIN_CACHE]"),
    ]


def iter_skill_files(repo_root: Path, codex_home: Path) -> Iterable[tuple[str, Path, Path, str]]:
    seen: set[Path] = set()
    system_root = (codex_home / "skills" / ".system").resolve()
    for layer, base, placeholder in skill_roots(repo_root, codex_home):
        if not base.exists():
            continue
        try:
            candidates = sorted(base.rglob("SKILL.md"))
        except OSError:
            continue
        for path in candidates:
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            if layer == "user":
                try:
                    resolved.relative_to(system_root)
                    continue
                except ValueError:
                    pass
            seen.add(resolved)
            yield layer, base, path, placeholder


def build_path_hint(base: Path, path: Path, placeholder: str) -> str:
    try:
        rel = path.parent.relative_to(base).as_posix()
    except ValueError:
        rel = path.parent.name
    rel = slugify(rel)
    return f"{placeholder}/{rel}/SKILL.md" if rel else f"{placeholder}/SKILL.md"


def build_skill_id(layer: str, base: Path, path: Path, parsed_name: str | None) -> str:
    try:
        rel = path.parent.relative_to(base).as_posix()
    except ValueError:
        rel = path.parent.name
    if layer == "plugin" and parsed_name:
        rel = f"{rel}/{parsed_name}"
    return f"{layer}:{slugify(rel or parsed_name or path.parent.name)}"


def index_skills(repo_root: Path, codex_home: Path) -> list[dict[str, Any]]:
    records: list[SkillRecord] = []
    used_ids: dict[str, int] = {}
    for layer, base, path, placeholder in iter_skill_files(repo_root, codex_home):
        try:
            text = read_text_lossy(path)
        except OSError:
            continue
        had_bom = text.startswith("\ufeff")
        frontmatter, valid, error, _body = parse_frontmatter(text)
        name = sanitize_text(frontmatter.get("name") or path.parent.name, limit=80)
        description = sanitize_text(frontmatter.get("description") or "", limit=10000)
        summary = sanitize_text(description or "No valid skill description available.", limit=SUMMARY_LIMIT)
        skill_id = build_skill_id(layer, base, path, name)
        compatibility = codex_frontmatter_report(frontmatter, valid, error, had_bom=had_bom)
        if skill_id in used_ids:
            used_ids[skill_id] += 1
            skill_id = f"{skill_id}-{used_ids[skill_id]}"
        else:
            used_ids[skill_id] = 1
        records.append(
            SkillRecord(
                skill_id=skill_id,
                name=name,
                source_layer=layer,
                path_hint=build_path_hint(base, path, placeholder),
                description_summary=summary,
                description_hash=stable_hash(description),
                available=valid,
                frontmatter_valid=valid,
                frontmatter_error=error,
                codex_frontmatter_compatible=bool(compatibility["codex_frontmatter_compatible"]),
                codex_frontmatter_errors=list(compatibility["codex_frontmatter_errors"]),
                name_length=int(compatibility["name_length"]),
                description_length=int(compatibility["description_length"]),
            )
        )
    return [asdict(record) for record in sorted(records, key=lambda item: (item.source_layer, item.name.lower(), item.skill_id))]


def build_frontmatter_compatibility_summary(repo_root: Path, codex_home: Path) -> dict[str, Any]:
    """Return a compact current SKILL.md frontmatter compatibility summary."""
    skills = index_skills(repo_root, codex_home)
    invalid = [item for item in skills if not item.get("codex_frontmatter_compatible")]
    by_error: Counter[str] = Counter()
    by_layer: Counter[str] = Counter()
    for item in invalid:
        by_layer[str(item.get("source_layer") or "unknown")] += 1
        for error in item.get("codex_frontmatter_errors") or []:
            by_error[str(error)] += 1
    return {
        "checked_with": "tools/skills2cli.py index",
        "total": len(skills),
        "invalid_total": len(invalid),
        "by_error": dict(sorted(by_error.items())),
        "by_layer": dict(sorted(by_layer.items())),
        "codex_name_limit": CODEX_SKILL_NAME_LIMIT,
        "codex_description_limit": CODEX_SKILL_DESCRIPTION_LIMIT,
        "raw_paths_retained": False,
        "raw_skill_bodies_retained": False,
        "mutates_config": False,
        "edits_plugin_cache": False,
        "profile_apply_performed": False,
    }


def envelope(command: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "safety": {
            "compact_output": True,
            "raw_paths_retained": False,
            "full_skill_bodies_included_by_default": False,
            "mutates_config": False,
            "edits_plugin_cache": False,
            "codex_frontmatter_name_limit": CODEX_SKILL_NAME_LIMIT,
            "codex_frontmatter_description_limit": CODEX_SKILL_DESCRIPTION_LIMIT,
        },
    }
    result.update(payload)
    return result


def command_index(args: argparse.Namespace) -> int:
    repo_root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve()
    skills = index_skills(repo_root, codex_home)
    payload = envelope("index", {"total": len(skills), "skills": skills})
    emit(payload, args.json)
    return 0


def build_skill_layer_counts(skills: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in skills:
        counts[str(item.get("source_layer") or "unknown")] += 1
    for layer in ("repo", "system", "user", "plugin"):
        counts.setdefault(layer, 0)
    return dict(sorted(counts.items()))


def build_skill_layer_pressure(skills: list[dict[str, Any]]) -> dict[str, Any]:
    by_layer = build_skill_layer_counts(skills)
    total = sum(int(value) for value in by_layer.values())
    dominant_layer = max(by_layer, key=lambda layer: (int(by_layer[layer]), layer)) if by_layer else "unknown"
    user_count = int(by_layer.get("user") or 0)
    plugin_count = int(by_layer.get("plugin") or 0)
    repo_count = int(by_layer.get("repo") or 0)
    user_layer_pressure = bool(total and user_count >= max(plugin_count, repo_count) and user_count / max(total, 1) >= 0.35)
    if user_layer_pressure:
        pressure_reason = "standalone_user_skills_dominate_visible_skill_surface"
    elif plugin_count > user_count:
        pressure_reason = "plugin_skills_are_larger_than_standalone_user_skills"
    elif total:
        pressure_reason = "skill_surface_pressure_detected_without_user_layer_dominance"
    else:
        pressure_reason = "no_skills_indexed"
    return {
        "available": True,
        "total": total,
        "by_layer": by_layer,
        "dominant_layer": dominant_layer,
        "user_layer_pressure": user_layer_pressure,
        "standalone_user_skill_count": user_count,
        "plugin_skill_count": plugin_count,
        "repo_skill_count": repo_count,
        "pressure_reason": pressure_reason,
        "raw_skill_bodies_retained": False,
        "raw_paths_retained": False,
    }


def build_standalone_user_skill_pressure(skills: list[dict[str, Any]], *, limit: int = 8) -> dict[str, Any]:
    user_skills = [item for item in skills if str(item.get("source_layer") or "") == "user"]
    incompatible = [item for item in user_skills if not item.get("codex_frontmatter_compatible")]
    sampled = [
        {
            "skill_id": sanitize_text(str(item.get("skill_id") or ""), limit=120),
            "name": sanitize_text(str(item.get("name") or ""), limit=80),
            "description_hash": str(item.get("description_hash") or ""),
            "frontmatter_compatible": bool(item.get("codex_frontmatter_compatible")),
        }
        for item in user_skills[:limit]
    ]
    return {
        "available": True,
        "count": len(user_skills),
        "incompatible_count": len(incompatible),
        "sampled_skill_metadata": sampled,
        "sample_limit": limit,
        "candidate_actions": [
            "keep_core_dev_profile_loaded_for_developer_work",
            "use_task_module_soft_load_for_current_task_before_hard_load_apply",
            "audit_standalone_user_skills_before_any_visibility_apply",
            "do_not_repeat_plugin_profile_apply_as_the_primary_fix_when_user_layer_dominates",
        ],
        "apply_required_for_visibility_changes": True,
        "profile_apply_performed": False,
        "mutates_config": False,
        "edits_plugin_cache": False,
        "raw_skill_bodies_retained": False,
        "raw_paths_retained": False,
    }


def build_visibility_preview(skill_layer_pressure: dict[str, Any], standalone_pressure: dict[str, Any]) -> dict[str, Any]:
    user_count = int(standalone_pressure.get("count") or 0)
    return {
        "mode": "preview-only",
        "recommended_target_profile": BUDGET_TRIAGE_PROFILE,
        "recommended_task_module": f"{BUDGET_TRIAGE_PROFILE}.{BUDGET_TRIAGE_TASK_MODULE}",
        "dominant_layer": skill_layer_pressure.get("dominant_layer"),
        "standalone_user_skill_count": user_count,
        "candidate_actions": standalone_pressure.get("candidate_actions", []),
        "why_profile_apply_alone_is_insufficient": (
            "Plugin profile apply can reduce plugin visibility, but standalone user-level skills remain a separate pressure source."
            if skill_layer_pressure.get("user_layer_pressure")
            else "Profile apply remains preview-only and should be based on audited current skill layers."
        ),
        "requires_future_explicit_apply_receipt": True,
        "mutates_config": False,
        "edits_plugin_cache": False,
        "profile_apply_performed": False,
    }


def score_record(record: dict[str, Any], terms: list[str]) -> int:
    haystack = " ".join(
        str(record.get(key, "")) for key in ("skill_id", "name", "source_layer", "description_summary")
    ).lower()
    return sum(1 for term in terms if term in haystack)


def command_search(args: argparse.Namespace) -> int:
    repo_root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve()
    terms = [term.lower() for term in re.split(r"\s+", args.query.strip()) if term]
    results = []
    for record in index_skills(repo_root, codex_home):
        score = score_record(record, terms)
        if score:
            item = dict(record)
            item["score"] = score
            results.append(item)
    results.sort(key=lambda item: (-int(item["score"]), str(item["name"]).lower(), str(item["skill_id"])))
    payload = envelope("search", {"query": sanitize_text(args.query, limit=120), "total_matches": len(results), "results": results[: args.limit]})
    emit(payload, args.json)
    return 0


def find_skill(repo_root: Path, codex_home: Path, skill_id: str) -> tuple[dict[str, Any], Path] | None:
    for layer, base, path, placeholder in iter_skill_files(repo_root, codex_home):
        try:
            text = read_text_lossy(path)
        except OSError:
            continue
        had_bom = text.startswith("\ufeff")
        frontmatter, valid, error, _body = parse_frontmatter(text)
        name = sanitize_text(frontmatter.get("name") or path.parent.name, limit=80)
        record_id = build_skill_id(layer, base, path, name)
        aliases = {record_id, name, f"{layer}:{name}"}
        if skill_id in aliases:
            description = sanitize_text(frontmatter.get("description") or "", limit=10000)
            compatibility = codex_frontmatter_report(frontmatter, valid, error, had_bom=had_bom)
            record = asdict(
                SkillRecord(
                    skill_id=record_id,
                    name=name,
                    source_layer=layer,
                    path_hint=build_path_hint(base, path, placeholder),
                    description_summary=sanitize_text(description or "No valid skill description available.", limit=SUMMARY_LIMIT),
                    description_hash=stable_hash(description),
                    available=valid,
                    frontmatter_valid=valid,
                    frontmatter_error=error,
                    codex_frontmatter_compatible=bool(compatibility["codex_frontmatter_compatible"]),
                    codex_frontmatter_errors=list(compatibility["codex_frontmatter_errors"]),
                    name_length=int(compatibility["name_length"]),
                    description_length=int(compatibility["description_length"]),
                )
            )
            return record, path
    # Fall back to generated indexed ids, including duplicate suffixes.
    for record in index_skills(repo_root, codex_home):
        if skill_id in {record["skill_id"], record["name"]}:
            for layer, base, path, _placeholder in iter_skill_files(repo_root, codex_home):
                frontmatter, _valid, _error, _body = parse_frontmatter(read_text_lossy(path))
                if sanitize_text(frontmatter.get("name") or path.parent.name, limit=80) == record["name"]:
                    return record, path
    return None


def command_show(args: argparse.Namespace) -> int:
    repo_root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve()
    found = find_skill(repo_root, codex_home, args.skill_id)
    if found is None:
        emit(envelope("show", {"ok": False, "error": "skill_not_found", "skill_id": sanitize_text(args.skill_id, limit=120)}), args.json)
        return 2
    record, path = found
    record = dict(record)
    if args.full:
        body = sanitize_text(read_text_lossy(path), limit=SHOW_BODY_LIMIT)
        record.update({"full_body_included": True, "full_body_redacted": True, "body": body})
    else:
        record.update({"full_body_included": False})
    payload = envelope("show", {"ok": True, "skill": record})
    emit(payload, args.json)
    return 0


AUDIT_MEMORY_RELATIVE = Path("docs_bilingual/memory")
AUDIT_SUMMARY_PATTERNS = (
    "skills_usage_audit_30d_summary_*.md",
    "skills_usage_audit_weekly_summary_*.md",
)
QUERY_SYNONYMS = {
    "\u5b89\u5168": "security secure threat review",
    "\u5ba1\u67e5": "review audit",
    "\u590d\u6838": "review verify",
    "\u4fee\u590d": "fix repair",
    "\u6784\u5efa": "build",
    "\u79fb\u52a8\u7aef": "mobile expo react native",
    "\u5ba2\u6237": "customer",
    "\u901a\u77e5": "notification notice",
    "\u4f1a\u8bae": "meeting",
    "\u7eaa\u8981": "meeting notes transcript",
    "\u79d1\u7814": "science research",
    "\u6392\u969c": "troubleshoot troubleshooting",
    "\u5168\u90e8\u63d2\u4ef6": "all plugins full profile",
    "\u4e0a\u4e0b\u6587\u538b\u7f29": "context compacted compaction",
    "\u6280\u80fd\u4e0a\u4e0b\u6587\u9884\u7b97": "skills context budget",
    "\u6280\u80fd\u9884\u7b97": "skills context budget",
}

def load_profile_registry(repo_root: Path, codex_home: Path | None = None) -> dict[str, Any]:
    return load_profile_registry_contract(
        repo_root,
        codex_home,
        script_dir=SCRIPT_DIR,
        default_codex_home=default_codex_home(),
    )


def repo_relative_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return sanitize_text(str(path), limit=220)


def parse_backtick_field(text: str, label: str) -> str | None:
    pattern = re.compile(rf"(?im)^\s*-\s*{re.escape(label)}\s*:\s*`([^`]*)`")
    match = pattern.search(text)
    if match:
        return sanitize_text(match.group(1), limit=120)
    return None


def parse_int_field(text: str, label: str) -> int:
    raw = parse_backtick_field(text, label)
    if raw is None:
        return 0
    match = re.search(r"-?\d+", raw)
    return int(match.group(0)) if match else 0


def parse_bool_field(text: str, label: str) -> bool | None:
    raw = parse_backtick_field(text, label)
    if raw is None:
        return None
    if raw.strip().lower() in {"true", "yes", "1", "allowed"}:
        return True
    if raw.strip().lower() in {"false", "no", "0", "not_authorized", "not-allowed"}:
        return False
    return None


def newest_audit_summary_files(repo_root: Path, *, limit: int = 2) -> list[Path]:
    memory_dir = repo_root / AUDIT_MEMORY_RELATIVE
    if not memory_dir.exists():
        return []
    files: list[Path] = []
    for pattern in AUDIT_SUMMARY_PATTERNS:
        matches = sorted(
            (path for path in memory_dir.glob(pattern) if path.is_file() and ".zh-CN." not in path.name),
            key=lambda path: path.name,
            reverse=True,
        )
        files.extend(matches[:1])
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        if path in seen:
            continue
        deduped.append(path)
        seen.add(path)
    return deduped[:limit]


def parse_profile_audit_table(text: str, known_profiles: set[str]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        profile = cells[0]
        if profile not in known_profiles:
            continue
        score_match = re.search(r"-?\d+", cells[1]) if len(cells) > 1 else None
        usage_score = int(score_match.group(0)) if score_match else 0
        evidence_reason = sanitize_text(cells[2] if len(cells) > 2 else "", limit=160)
        review_state = sanitize_text(cells[4] if len(cells) > 4 else "", limit=120)
        decision_bucket = sanitize_text(cells[5] if len(cells) > 5 else "", limit=160)
        reason_lower = evidence_reason.lower()
        if "mapped_tool_calls_present" in reason_lower or "strong" in reason_lower:
            level = "strong"
        elif usage_score > 0 or "medium" in reason_lower:
            level = "medium"
        else:
            level = "weak"
        entries[profile] = {
            "usage_score": usage_score,
            "evidence_reason": evidence_reason,
            "evidence_level": level,
            "review_state": review_state,
            "decision_bucket": decision_bucket,
        }
    return entries


def load_audit_ranking_context(repo_root: Path, profiles: Iterable[str]) -> dict[str, Any]:
    """Load committed, sanitized skills-audit summaries as advisory rerank input.

    This intentionally reads only repository-retained Markdown summaries.  Raw
    transcripts, local JSON, runtime logs, user config, and plugin cache files
    are not touched by profile suggestion.
    """
    known_profiles = {str(profile) for profile in profiles if str(profile).strip()}
    source_files = newest_audit_summary_files(repo_root)
    profile_entries: dict[str, dict[str, Any]] = {}
    warning_pressure: dict[str, Any] = {
        "available": False,
        "severity": "unknown",
        "budget_warning_count": 0,
        "all_descriptions_removed_count": 0,
        "max_omitted_additional_skills": 0,
        "recommended_action": "",
        "penalty_profiles": [],
        "penalty_value": 0,
    }
    summary_review_state = "unknown"
    profile_apply_allowed = False
    for path in source_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for profile, entry in parse_profile_audit_table(text, known_profiles).items():
            existing = profile_entries.get(profile)
            if existing is None or int(entry["usage_score"]) > int(existing.get("usage_score") or 0):
                entry["source_file"] = repo_relative_path(repo_root, path)
                profile_entries[profile] = entry
        severity = parse_backtick_field(text, "Highest severity")
        if severity:
            warning_pressure["available"] = True
            warning_pressure["severity"] = severity
            warning_pressure["budget_warning_count"] = max(
                int(warning_pressure["budget_warning_count"]),
                parse_int_field(text, "Budget warning count"),
                parse_int_field(text, "Last seven-day budget warning count"),
                parse_int_field(text, "30-day budget warning count"),
                parse_int_field(text, "Seven-day budget warning count inside the 30-day report"),
            )
            warning_pressure["all_descriptions_removed_count"] = max(
                int(warning_pressure["all_descriptions_removed_count"]),
                parse_int_field(text, "All-descriptions-removed count"),
            )
            warning_pressure["max_omitted_additional_skills"] = max(
                int(warning_pressure["max_omitted_additional_skills"]),
                parse_int_field(text, "Maximum omitted additional skills"),
            )
            warning_pressure["recommended_action"] = parse_backtick_field(text, "Severity recommended action") or ""
        summary_review_state = parse_backtick_field(text, "Summary review state") or summary_review_state
        allowed = parse_bool_field(text, "Profile apply allowed")
        if allowed is not None:
            profile_apply_allowed = bool(allowed)
    pressure_high = str(warning_pressure.get("severity", "")).lower() in {"medium", "high", "critical"} or int(
        warning_pressure.get("budget_warning_count") or 0
    ) >= 3
    if pressure_high:
        warning_pressure["penalty_profiles"] = ["full"]
        warning_pressure["penalty_value"] = -40
    return {
        "available": bool(source_files),
        "source_files": [repo_relative_path(repo_root, path) for path in source_files],
        "profile_entries": profile_entries,
        "strong_evidence_available": any(entry.get("evidence_level") == "strong" for entry in profile_entries.values()),
        "summary_review_state": summary_review_state,
        "profile_apply_allowed": profile_apply_allowed,
        "warning_pressure": warning_pressure,
        "raw_log_paths_retained": False,
        "raw_skill_bodies_retained": False,
        "mutates_config": False,
        "edits_plugin_cache": False,
        "profile_apply_performed": False,
    }


def normalize_query(value: str) -> str:
    base = sanitize_text(value, limit=500).lower()
    additions = [alias for marker, alias in QUERY_SYNONYMS.items() if marker.lower() in base]
    return " ".join([base, *additions]).strip()


def detect_budget_warning_intent(raw_query: str, normalized_query: str | None = None) -> dict[str, Any]:
    raw = str(raw_query or "")
    normalized = normalized_query or normalize_query(raw)
    haystack = f"{raw}\n{normalized}".lower()
    matched_terms: list[str] = []
    for term in BUDGET_INTENT_TERMS:
        candidate = term.lower()
        if candidate and candidate in haystack and term not in matched_terms:
            matched_terms.append(term)
    regex_matches = {
        "budget_warning": bool(BUDGET_WARNING_RE.search(raw) or BUDGET_WARNING_RE.search(normalized)),
        "all_descriptions_removed": bool(ALL_DESCRIPTIONS_REMOVED_RE.search(raw) or ALL_DESCRIPTIONS_REMOVED_RE.search(normalized)),
        "omitted_additional_skills": bool(OMITTED_ADDITIONAL_RE.search(raw) or OMITTED_ADDITIONAL_RE.search(normalized)),
    }
    compacted = "compaction" in haystack or "context compacted" in haystack or "上下文压缩" in haystack
    budget_terms = "skills context budget" in haystack or "skill descriptions removed" in haystack or "additional skills" in haystack
    detected = bool(matched_terms or any(regex_matches.values()) or (compacted and budget_terms))
    blocked = ["web-saas", "company-ops", "market-research", "customer-comms", "creative-content", "pyside6-gui", "full"] if detected else []
    return {
        "detected": detected,
        "matched_terms": matched_terms,
        "regex_matches": regex_matches,
        "target_profile": BUDGET_TRIAGE_PROFILE if detected else None,
        "scenario_profile": BUDGET_TRIAGE_SCENARIO if detected else None,
        "task_module": BUDGET_TRIAGE_TASK_MODULE if detected else None,
        "audit_override_blocked": detected,
        "blocked_unrelated_profiles": blocked,
        "policy": "budget_warning_intent_routes_before_audit_boost_and_blocks_unrelated_profile_override",
    }


def match_terms(haystack: str, terms: Iterable[Any]) -> list[str]:
    haystack_lower = haystack.lower()
    hits: list[str] = []
    seen: set[str] = set()
    for term in terms:
        candidate = str(term).strip().lower()
        if not candidate or candidate in seen:
            continue
        if candidate in haystack_lower:
            hits.append(candidate)
            seen.add(candidate)
    return hits


def scene_description(entry: dict[str, Any]) -> str:
    """Return the new scene_description field while preserving legacy compatibility."""

    return contract_scene_description(entry)


def profile_plugin_hints(entry: dict[str, Any]) -> list[str]:
    return contract_plugin_hints(entry)


def profile_skill_doc_hints(entry: dict[str, Any]) -> list[str]:
    return contract_skill_doc_hints(entry)


def profile_candidate_terms(profile_id: str, entry: dict[str, Any]) -> list[str]:
    terms: list[str] = [profile_id]
    terms.extend(as_string_list(entry.get("route_when")))
    terms.extend(as_string_list(entry.get("plugin_hints")))
    terms.extend(as_string_list(entry.get("plugins")))
    terms.append(scene_description(entry))
    terms.append(str(entry.get("description") or ""))
    for module_id, module in (entry.get("task_modules") or {}).items():
        terms.append(str(module_id))
        terms.extend(as_string_list(module.get("route_when")))
        terms.extend(as_string_list(module.get("plugin_hints")))
    return terms


def scenario_candidate_terms(scenario_id: str, scenario: dict[str, Any]) -> list[str]:
    terms: list[str] = [scenario_id]
    terms.extend(as_string_list(scenario.get("route_when")))
    terms.extend(as_string_list(scenario.get("positive_examples")))
    terms.extend(as_string_list(scenario.get("plugin_hints")))
    terms.append(scene_description(scenario))
    terms.append(str(scenario.get("description") or ""))
    return terms


def build_task_module_recommendations(query_text: str, profile_id: str, entry: dict[str, Any], default_modules: list[str] | None = None) -> list[dict[str, Any]]:
    modules = entry.get("task_modules") or {}
    results: list[dict[str, Any]] = []
    default_set = set(default_modules or [])
    for module_id, module in modules.items():
        terms = [module_id, module.get("description", ""), scene_description(module)]
        terms.extend(as_string_list(module.get("route_when")))
        terms.extend(as_string_list(module.get("positive_examples")))
        terms.extend(as_string_list(module.get("plugin_hints")))
        negative = match_terms(query_text, as_string_list(module.get("negative_examples")))
        hits = match_terms(query_text, terms)
        score = len(hits) * 10 + (2 if hits and module_id in default_set else 0) - len(negative) * 8
        if score > 0:
            identity = task_module_identity(profile_id, module_id, module)
            results.append(
                {
                    "task_module": module_id,
                    "qualified_name": str(identity["qualified_name"]),
                    "identity": identity,
                    "score": score,
                    "matched_terms": hits[:10],
                    "negative_matches": negative[:5],
                    "load_policy": str(module.get("load_policy") or "soft-load"),
                    "plugin_hints": as_string_list(module.get("plugin_hints"))[:8],
                    "skill_doc_hints": as_string_list(module.get("skill_doc_hints"))[:8],
                    "routing_explanation": sanitize_text(str(module.get("routing_explanation") or module.get("description") or ""), limit=220),
                }
            )
    results.sort(key=lambda item: (-int(item["score"]), str(item["task_module"])))
    return results[:5]


def audit_profile_boost(profile_id: str, audit_context: dict[str, Any] | None) -> dict[str, Any]:
    if not audit_context:
        return {"available": False, "boost": 0}
    entry = (audit_context.get("profile_entries") or {}).get(profile_id)
    if not isinstance(entry, dict):
        return {"available": False, "boost": 0}
    usage_score = int(entry.get("usage_score") or 0)
    level = str(entry.get("evidence_level") or "weak")
    if level == "strong":
        boost = 8 + min(12, int(math.log10(max(usage_score, 1)) * 4))
    elif level == "medium":
        boost = 3 + min(5, int(math.log10(max(usage_score, 1)) * 2))
    else:
        boost = 1 if usage_score > 0 else 0
    return {
        "available": True,
        "profile": profile_id,
        "boost": boost,
        "evidence_level": level,
        "usage_score": usage_score,
        "evidence_reason": sanitize_text(str(entry.get("evidence_reason") or ""), limit=160),
        "review_state": sanitize_text(str(entry.get("review_state") or ""), limit=120),
        "source_file": sanitize_text(str(entry.get("source_file") or ""), limit=220),
        "policy": "advisory_boost_only_profile_apply_not_authorized",
    }


def warning_pressure_penalty(profile_id: str, explicit_full: bool, audit_context: dict[str, Any] | None) -> dict[str, Any]:
    pressure = (audit_context or {}).get("warning_pressure") if audit_context else None
    if not isinstance(pressure, dict) or not pressure.get("available"):
        return {"available": False, "penalty": 0}
    penalty_profiles = [str(item) for item in as_string_list(pressure.get("penalty_profiles"))]
    applies = profile_id in penalty_profiles and not explicit_full
    penalty = int(pressure.get("penalty_value") or 0) if applies else 0
    return {
        "available": True,
        "profile": profile_id,
        "applied": applies,
        "penalty": penalty,
        "severity": sanitize_text(str(pressure.get("severity") or "unknown"), limit=80),
        "budget_warning_count": int(pressure.get("budget_warning_count") or 0),
        "all_descriptions_removed_count": int(pressure.get("all_descriptions_removed_count") or 0),
        "max_omitted_additional_skills": int(pressure.get("max_omitted_additional_skills") or 0),
        "recommended_action": sanitize_text(str(pressure.get("recommended_action") or ""), limit=160),
        "policy": "warning_pressure_penalizes_broad_profiles_without_authorizing_profile_apply",
    }


def score_profile_candidate(
    query_text: str,
    profile_id: str,
    entry: dict[str, Any],
    scenario_id: str | None,
    scenario: dict[str, Any] | None,
    audit_context: dict[str, Any] | None = None,
    explicit_full: bool | None = None,
    budget_intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile_hits = match_terms(query_text, profile_candidate_terms(profile_id, entry))
    scenario_hits = match_terms(query_text, scenario_candidate_terms(str(scenario_id), scenario)) if scenario_id and scenario else []
    negative_terms = as_string_list(entry.get("negative_examples")) + as_string_list((scenario or {}).get("negative_examples"))
    negative = match_terms(query_text, negative_terms)
    explicit_full = is_explicit_full_request(query_text) if explicit_full is None else explicit_full
    full_explicit_required = profile_id == "full" or str(entry.get("load_policy") or "") == "troubleshooting-only"
    full_selection_reason = explicit_full_selection_reason(query_text) if full_explicit_required and explicit_full else None
    load_policy = str((scenario or {}).get("load_policy") or entry.get("load_policy") or "default-candidate")
    default_modules = as_string_list((scenario or {}).get("default_task_modules"))
    default_module_set = set(default_modules)
    task_modules = build_task_module_recommendations(query_text, profile_id, entry, default_modules)
    default_module_hits = [item for item in task_modules if item.get("task_module") in default_module_set]

    if scenario_id:
        # Scenario candidates are entry points, not aliases for every parent-profile hit.
        # They must match their own scene text or one of their default task modules;
        # otherwise ordinary repo/CI/security work must stay with the repo-dev scene.
        score = len(scenario_hits) * 14 + sum(min(8, int(item["score"])) for item in default_module_hits)
        score += min(6, len(profile_hits) * 2)
        if scenario_hits or default_module_hits:
            score += 5
        else:
            score = -100
    else:
        score = len(profile_hits) * 10
        if task_modules:
            score += min(15, sum(min(5, int(item["score"])) for item in task_modules))

    score -= len(negative) * 8
    if profile_id == "core-dev":
        score += 2
    if full_explicit_required:
        score += 20 if explicit_full else -60
    budget_detected = bool((budget_intent or {}).get("detected"))
    budget_target_match = bool(
        budget_detected
        and profile_id == BUDGET_TRIAGE_PROFILE
        and (scenario_id in {None, BUDGET_TRIAGE_SCENARIO})
    )
    budget_unrelated = bool(budget_detected and not budget_target_match)
    if budget_target_match:
        score += 85 if scenario_id == BUDGET_TRIAGE_SCENARIO else 55
    elif budget_unrelated:
        score -= 45
    audit_boost = audit_profile_boost(profile_id, audit_context)
    if budget_unrelated:
        audit_boost = dict(audit_boost)
        audit_boost["suppressed_by_budget_warning_intent"] = True
        audit_boost["original_boost"] = int(audit_boost.get("boost") or 0)
        audit_boost["boost"] = 0
    score += int(audit_boost.get("boost") or 0)
    pressure_penalty = warning_pressure_penalty(profile_id, explicit_full, audit_context)
    score += int(pressure_penalty.get("penalty") or 0)
    confidence = max(0.1, min(0.98, 0.28 + score / 100.0))
    hits = [*scenario_hits, *profile_hits]
    return {
        "scenario_profile": scenario_id,
        "profile": profile_id,
        "target_profile": profile_id,
        "score": score,
        "confidence": round(confidence, 2),
        "matched_terms": hits[:12],
        "scenario_matched_terms": scenario_hits[:12],
        "profile_matched_terms": profile_hits[:12],
        "negative_matches": negative[:8],
        "eligibility": {
            "eligible": not (full_explicit_required and not explicit_full),
            "reason": "eligible" if not (full_explicit_required and not explicit_full) else "explicit_full_request_required",
            "explicit_full_request_required": full_explicit_required,
            "explicit_full_request": explicit_full,
        },
        "rank_factors": {
            "scenario_match_count": len(scenario_hits),
            "profile_match_count": len(profile_hits),
            "task_module_match_count": len(task_modules),
            "negative_match_count": len(negative),
            "audit_boost": int(audit_boost.get("boost") or 0),
            "warning_pressure_penalty": int(pressure_penalty.get("penalty") or 0),
            "full_selection_reason": full_selection_reason,
            "budget_warning_intent": budget_detected,
            "budget_warning_target_match": budget_target_match,
            "budget_warning_unrelated_profile_blocked": budget_unrelated,
        },
        "why_full_selected": full_selection_reason if profile_id == "full" and explicit_full else None,
        "load_policy": load_policy,
        "task_modules": task_modules,
        "ranking_signals": as_string_list((scenario or {}).get("ranking_signals")) or as_string_list(entry.get("ranking_signals")),
        "plugin_hints": profile_plugin_hints(entry),
        "skill_doc_hints": profile_skill_doc_hints(entry),
        "audit_evidence": audit_boost,
        "warning_pressure_penalty": pressure_penalty,
    }


def build_profile_recommendations(
    registry: dict[str, Any],
    raw_query: str,
    audit_context: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool, dict[str, Any]]:
    query_text = normalize_query(raw_query)
    budget_intent = detect_budget_warning_intent(raw_query, query_text)
    modules = registry.get("modules") or {}
    scenarios = registry.get("scenario_profiles") or {}
    explicit_full = is_explicit_full_request(query_text, registry)
    candidates: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str | None]] = set()
    for scenario_id, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            continue
        target = str(scenario.get("target_profile") or "")
        entry = modules.get(target)
        if not isinstance(entry, dict):
            continue
        key = (target, scenario_id)
        seen_keys.add(key)
        candidates.append(score_profile_candidate(query_text, target, entry, str(scenario_id), scenario, audit_context, explicit_full, budget_intent))
    for profile_id, entry in modules.items():
        if not isinstance(entry, dict):
            continue
        key = (str(profile_id), None)
        if key in seen_keys:
            continue
        candidates.append(score_profile_candidate(query_text, str(profile_id), entry, None, None, audit_context, explicit_full, budget_intent))
    excluded: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []
    for item in candidates:
        eligibility = item.get("eligibility") if isinstance(item.get("eligibility"), dict) else {}
        if item["profile"] == "full" and not eligibility.get("eligible", True):
            excluded.append(
                {
                    "profile": item["profile"],
                    "target_profile": item["target_profile"],
                    "scenario_profile": item.get("scenario_profile"),
                    "reason": "explicit_full_request_required",
                    "eligibility": eligibility,
                    "rank_factors": item.get("rank_factors", {}),
                }
            )
        elif item["negative_matches"] and item["score"] <= 0:
            excluded.append(
                {
                    "profile": item["profile"],
                    "target_profile": item["target_profile"],
                    "scenario_profile": item.get("scenario_profile"),
                    "reason": "negative_examples_matched",
                    "negative_matches": item["negative_matches"],
                    "rank_factors": item.get("rank_factors", {}),
                }
            )
        elif item["score"] > 0:
            retained.append(item)
    if not retained:
        fallback_entry = modules.get("core-dev") if isinstance(modules.get("core-dev"), dict) else {}
        retained.append(
            score_profile_candidate(
                query_text,
                "core-dev",
                fallback_entry,
                "repo-dev",
                (registry.get("scenario_profiles") or {}).get("repo-dev") if isinstance(registry.get("scenario_profiles"), dict) else None,
                audit_context,
                explicit_full,
                budget_intent,
            )
        )
        retained[-1]["score"] = max(1, int(retained[-1]["score"]))
        retained[-1]["confidence"] = max(0.35, float(retained[-1]["confidence"]))
        retained[-1]["matched_terms"] = retained[-1].get("matched_terms") or []
        retained[-1]["fallback_reason"] = "no_positive_profile_match_default_to_core_dev_preview"
    retained.sort(key=lambda item: (-int(item["score"]), 1 if item["profile"] == "full" else 0, str(item.get("scenario_profile") or item["profile"])))
    return retained[:5], excluded[:10], explicit_full, budget_intent


def command_profile_suggest(args: argparse.Namespace) -> int:
    raw_query = getattr(args, "query", None) or getattr(args, "task", "")
    query = sanitize_text(raw_query, limit=500)
    repo_root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve()
    registry = load_profile_registry(repo_root, codex_home)
    modules = registry.get("modules") if isinstance(registry.get("modules"), dict) else {}
    audit_context = load_audit_ranking_context(repo_root, modules.keys())
    recommendations, excluded, explicit_full, budget_intent = build_profile_recommendations(registry, query, audit_context)
    selected = recommendations[0]
    selected_modules = selected.get("task_modules") or []
    target_profile = str(selected.get("target_profile") or selected.get("profile"))
    skills = index_skills(repo_root, codex_home) if budget_intent.get("detected") else []
    skill_layer_pressure = (
        build_skill_layer_pressure(skills)
        if budget_intent.get("detected")
        else {"available": False, "reason": "budget_warning_intent_not_detected"}
    )
    standalone_user_skill_pressure = (
        build_standalone_user_skill_pressure(skills)
        if budget_intent.get("detected")
        else {"available": False, "reason": "budget_warning_intent_not_detected"}
    )
    visibility_preview = (
        build_visibility_preview(skill_layer_pressure, standalone_user_skill_pressure)
        if budget_intent.get("detected")
        else {"available": False, "mode": "not_applicable_without_budget_warning_intent"}
    )
    soft_load_commands = [
        f".\\tools\\skill_sources\\plugin-modules\\scripts\\load_module.ps1 {item['qualified_name']} -Json"
        for item in selected_modules[:3]
    ]
    if not soft_load_commands:
        soft_load_commands = [f".\\tools\\skill_sources\\plugin-modules\\scripts\\load_module.ps1 {target_profile} -Json"]
    hard_load_preview_command = None if target_profile == "full" and not explicit_full else f".\\tools\\skill_sources\\plugin-modules\\scripts\\set_plugin_profile.ps1 {target_profile} -Json"
    suggestions = [
        {
            "profile": item["profile"],
            "target_profile": item["target_profile"],
            "scenario_profile": item.get("scenario_profile"),
            "matched_terms": item.get("matched_terms", []),
            "confidence": item.get("confidence", 0),
            "task_modules": [module["task_module"] for module in item.get("task_modules", [])],
        }
        for item in recommendations
    ]
    payload = envelope(
        "profile suggest",
        {
            "query": query,
            "task_summary": query,
            "explicit_full_request": explicit_full,
            "budget_warning_intent": budget_intent,
            "skill_layer_counts": skill_layer_pressure.get("by_layer", {}),
            "skill_layer_pressure": skill_layer_pressure,
            "standalone_user_skill_pressure": standalone_user_skill_pressure,
            "visibility_preview": visibility_preview,
            "budget_warning_resolution_note": (
                "Route to core-dev.skills-budget-triage; inspect standalone user-skill pressure before repeating plugin profile apply."
                if budget_intent.get("detected")
                else None
            ),
            "eligibility_policy": "full profile is explicit-only; ordinary tasks receive focused non-full profiles and full is reported only in excluded_candidates.",
            "selected_profile": {
                "profile": selected["profile"],
                "target_profile": target_profile,
                "scenario_profile": selected.get("scenario_profile"),
                "confidence": selected.get("confidence"),
                "load_policy": selected.get("load_policy"),
                "matched_terms": selected.get("matched_terms", []),
                "ranking_signals": selected.get("ranking_signals", []),
                "plugin_hints": selected.get("plugin_hints", []),
                "skill_doc_hints": selected.get("skill_doc_hints", []),
                "audit_evidence": selected.get("audit_evidence"),
                "warning_pressure_penalty": selected.get("warning_pressure_penalty"),
                "eligibility": selected.get("eligibility"),
                "rank_factors": selected.get("rank_factors"),
                "negative_matches": selected.get("negative_matches", []),
                "why_full_selected": selected.get("why_full_selected"),
            },
            "task_modules": selected_modules,
            "recommendations": recommendations,
            "suggestions": suggestions,
            "excluded_candidates": excluded,
            "soft_load_commands": soft_load_commands,
            "hard_load_preview_command": hard_load_preview_command,
            "soft_hard_boundary": "profile_suggest and load_module are advisory soft-load/preview surfaces; set_plugin_profile without -Apply is preview only; hard-load apply requires separate explicit authorization and restart.",
            "registry_source": sanitize_text(str(registry.get("_registry_source") or "missing"), limit=220),
            "ranking_inputs": {
                "scenario_routing": True,
                "negative_examples": True,
                "task_module_rerank": True,
                "audit_strong_evidence_available": bool(audit_context.get("strong_evidence_available")),
                "audit_evidence_policy": "strong evidence may boost ranking when present but never authorizes profile apply",
                "audit_evidence_sources": audit_context.get("source_files", []),
                "audit_summary_review_state": audit_context.get("summary_review_state"),
                "audit_profile_apply_allowed": bool(audit_context.get("profile_apply_allowed")),
                "warning_pressure_available": bool((audit_context.get("warning_pressure") or {}).get("available")),
                "warning_pressure": audit_context.get("warning_pressure"),
                "budget_warning_intent": budget_intent,
                "skill_layer_pressure_available": bool(skill_layer_pressure.get("available")),
                "standalone_user_skill_pressure_available": bool(standalone_user_skill_pressure.get("available")),
                "warning_pressure_penalty_applied_to_full": bool(
                    not explicit_full
                    and (audit_context.get("warning_pressure") or {}).get("available")
                    and "full" in as_string_list((audit_context.get("warning_pressure") or {}).get("penalty_profiles"))
                ),
            },
            "mutates_config": False,
            "edits_plugin_cache": False,
            "profile_apply_performed": False,
            "approval_required_for_apply": True,
            "apply_policy": "preview_only_do_not_apply_without_explicit_profile_apply_authorization",
            "routing_evidence": {
                "surface_type": "skill_profile_suggestion",
                "native_subagent_evidence": False,
                "expert_evidence": False,
                "separate_native_agent_required_for_expert_claims": True,
                "reason": "Skills and profile suggestions are workflow/context surfaces, not native Codex subagent results.",
            },
        },
    )
    emit(payload, args.json)
    return 0


def parse_duration_or_since(value: str, now: datetime | None = None) -> datetime:
    now = now or utc_now()
    raw = value.strip()
    match = re.fullmatch(r"(\d+)([dhm])", raw, flags=re.IGNORECASE)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        if unit == "d":
            return now - timedelta(days=amount)
        if unit == "h":
            return now - timedelta(hours=amount)
        return now - timedelta(minutes=amount)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return now - timedelta(days=7)


def iter_text_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_text_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_text_values(child)


def parse_event_timestamp(payload: Any) -> datetime | None:
    if not isinstance(payload, dict):
        return None
    for key in ("timestamp", "time", "created_at"):
        raw = payload.get(key)
        if isinstance(raw, str):
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except ValueError:
                continue
    return None


def iter_session_texts(codex_home: Path, since: datetime) -> Iterable[str]:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return
    candidates: list[tuple[float, Path]] = []
    since_epoch = since.timestamp()
    for path in sessions_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".jsonl", ".log", ".txt", ".md"}:
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        # Most real sessions/log snippets are append-only.  Filtering old files
        # keeps live warning triage from walking the full historical archive.
        if mtime < since_epoch:
            continue
        candidates.append((mtime, path))
    for _mtime, path in sorted(candidates, key=lambda item: item[0], reverse=True):
        try:
            raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in raw_lines:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                payload = None
            if payload is not None:
                ts = parse_event_timestamp(payload)
                if ts is not None and ts < since:
                    continue
                text = " ".join(iter_text_values(payload))
            else:
                text = line
            if text:
                yield text


def blank_warning_source(source: str, *, available: bool = True, error: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source": source,
        "available": available,
        "budget_warning_count": 0,
        "skipped_loading_count": 0,
        "all_descriptions_removed_count": 0,
        "max_omitted_additional_skills": 0,
        "recent_sanitized_excerpts": [],
    }
    if error:
        payload["error"] = sanitize_text(error, limit=120)
    return payload


def add_warning_text(stats: dict[str, Any], text: str, *, limit: int) -> None:
    has_budget = bool(BUDGET_WARNING_RE.search(text))
    has_skipped = bool(SKIPPED_LOADING_RE.search(text))
    if has_budget:
        stats["budget_warning_count"] += len(BUDGET_WARNING_RE.findall(text)) or 1
    if has_skipped:
        stats["skipped_loading_count"] += len(SKIPPED_LOADING_RE.findall(text)) or 1
    if ALL_DESCRIPTIONS_REMOVED_RE.search(text):
        stats["all_descriptions_removed_count"] += 1
    for match in OMITTED_ADDITIONAL_RE.finditer(text):
        try:
            stats["max_omitted_additional_skills"] = max(
                int(stats["max_omitted_additional_skills"]),
                int(match.group(1)),
            )
        except (TypeError, ValueError):
            continue
    if (has_budget or has_skipped) and len(stats["recent_sanitized_excerpts"]) < limit:
        stats["recent_sanitized_excerpts"].append(sanitize_text(text, limit=WARNING_EXCERPT_LIMIT))


def scan_session_warning_source(codex_home: Path, since: datetime, *, limit: int) -> dict[str, Any]:
    stats = blank_warning_source("sessions_jsonl", available=(codex_home / "sessions").exists())
    for text in iter_session_texts(codex_home, since) or []:
        add_warning_text(stats, text, limit=limit)
    return stats


def logs_table_columns(con: sqlite3.Connection) -> set[str]:
    try:
        rows = con.execute("pragma table_info(logs)").fetchall()
    except sqlite3.Error:
        return set()
    return {str(row[1]) for row in rows if len(row) > 1}


def scan_sqlite_warning_source(codex_home: Path, since: datetime, *, limit: int) -> dict[str, Any]:
    db = codex_home / "logs_2.sqlite"
    if not db.exists():
        return blank_warning_source("logs_2.sqlite", available=False)
    stats = blank_warning_source("logs_2.sqlite", available=True)
    try:
        con = sqlite3.connect(str(db))
    except sqlite3.Error as exc:
        return blank_warning_source("logs_2.sqlite", available=False, error=f"sqlite_open_failed:{exc.__class__.__name__}")
    try:
        columns = logs_table_columns(con)
        if "feedback_log_body" not in columns:
            return blank_warning_source("logs_2.sqlite", available=False, error="missing_feedback_log_body_column")
        where = "feedback_log_body is not null and (feedback_log_body like ? or feedback_log_body like ?)"
        params: list[Any] = ["%Exceeded skills context budget%", "%Skipped loading%"]
        if "ts" in columns:
            where = "ts >= ? and " + where
            params.insert(0, int(since.timestamp()))
        query = f"select feedback_log_body from logs where {where} order by {'ts desc' if 'ts' in columns else 'rowid desc'}"
        for (body,) in con.execute(query, params):
            add_warning_text(stats, str(body or ""), limit=limit)
    except sqlite3.Error as exc:
        return blank_warning_source("logs_2.sqlite", available=False, error=f"sqlite_query_failed:{exc.__class__.__name__}")
    finally:
        con.close()
    return stats


def command_audit_warnings(args: argparse.Namespace) -> int:
    codex_home = Path(args.codex_home).resolve()
    repo_root = Path(args.root).resolve()
    since = parse_duration_or_since(args.since)
    session_source = scan_session_warning_source(codex_home, since, limit=args.limit)
    sqlite_source = scan_sqlite_warning_source(codex_home, since, limit=args.limit)
    sources = [session_source, sqlite_source]
    budget_count = sum(int(item.get("budget_warning_count") or 0) for item in sources)
    skipped_count = sum(int(item.get("skipped_loading_count") or 0) for item in sources)
    all_descriptions_removed_count = sum(int(item.get("all_descriptions_removed_count") or 0) for item in sources)
    max_omitted_additional_skills = max(int(item.get("max_omitted_additional_skills") or 0) for item in sources)
    excerpts: list[str] = []
    for source in sources:
        for excerpt in source.get("recent_sanitized_excerpts") or []:
            if len(excerpts) < args.limit:
                excerpts.append(str(excerpt))
    payload = envelope(
        "audit warnings",
        {
            "since": since.isoformat(),
            "budget_warning_count": budget_count,
            "skipped_loading_count": skipped_count,
            "all_descriptions_removed_count": all_descriptions_removed_count,
            "max_omitted_additional_skills": max_omitted_additional_skills,
            "recent_sanitized_excerpts": excerpts,
            "sources": sources,
            "current_frontmatter_compatibility": build_frontmatter_compatibility_summary(repo_root, codex_home),
            "log_source_review": "sessions_jsonl_and_logs_2_sqlite_are_read_only_sanitized_sources",
            "raw_log_paths_retained": False,
            "raw_skill_bodies_retained": False,
            "recommended_action": "use_summary_for_triage_and_do_not_edit_plugin_cache_without_authorization",
        },
    )
    emit(payload, args.json)
    return 0


def emit(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        # Machine-readable output must stay UTF-8 even on Windows pipes whose
        # default text encoding may be a legacy code page.
        data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            sys.stdout.buffer.write(data.encode("utf-8"))
        except AttributeError:  # pragma: no cover - nonstandard stdout shim.
            sys.stdout.write(data)
        return
    command = payload.get("command")
    if command == "index":
        print(f"skills2cli index: {payload.get('total', 0)} skills")
        for skill in payload.get("skills", [])[:20]:
            print(f"- {skill['skill_id']} [{skill['source_layer']}] {skill['description_summary']}")
    elif command == "search":
        print(f"skills2cli search: {payload.get('total_matches', 0)} matches")
        for skill in payload.get("results", []):
            print(f"- {skill['skill_id']} score={skill['score']} {skill['description_summary']}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compact sanitized Codex skill discovery helper.")
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(dest="command")

    def add_common(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--root", default=str(default_repo_root()), help="Repository root containing .codex/skills.")
        sub.add_argument("--codex-home", default=str(default_codex_home()), help="Codex home to inspect.")
        sub.add_argument("--json", action="store_true", help="Emit JSON.")

    index = subparsers.add_parser("index", help="Index available skills.")
    add_common(index)
    index.set_defaults(func=command_index)

    search = subparsers.add_parser("search", help="Search available skills.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    add_common(search)
    search.set_defaults(func=command_search)

    show = subparsers.add_parser("show", help="Show compact skill metadata.")
    show.add_argument("skill_id")
    show.add_argument("--full", action="store_true", help="Explicitly include a sanitized SKILL.md body.")
    add_common(show)
    show.set_defaults(func=command_show)

    profile = subparsers.add_parser("profile", help="Profile suggestion commands.")
    profile_sub = profile.add_subparsers(dest="profile_command")
    suggest = profile_sub.add_parser("suggest", help="Suggest a profile for a task without applying it.")
    group = suggest.add_mutually_exclusive_group(required=True)
    group.add_argument("--query")
    group.add_argument("--task")
    suggest.add_argument("--root", default=str(default_repo_root()))
    suggest.add_argument("--codex-home", default=str(default_codex_home()))
    suggest.add_argument("--json", action="store_true")
    suggest.set_defaults(func=command_profile_suggest)

    audit = subparsers.add_parser("audit", help="Audit commands.")
    audit_sub = audit.add_subparsers(dest="audit_command")
    warnings = audit_sub.add_parser("warnings", help="Summarize skills budget/skipped-loading warnings.")
    warnings.add_argument("--since", required=True, help="Duration such as 7d/24h/30m or an ISO timestamp.")
    warnings.add_argument("--root", default=str(default_repo_root()), help="Repository root containing .codex/skills.")
    warnings.add_argument("--codex-home", default=str(default_codex_home()))
    warnings.add_argument("--limit", type=int, default=5)
    warnings.add_argument("--json", action="store_true")
    warnings.set_defaults(func=command_audit_warnings)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.func is None:
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
