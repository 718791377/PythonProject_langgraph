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


PROFILE_REGISTRY_RELATIVE = Path("tools/skill_sources/plugin-modules/references/profiles.json")
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
}
EXPLICIT_FULL_TERMS = (
    "full profile",
    "all plugins",
    "all-plugin",
    "troubleshoot all plugins",
    "diagnose missing plugin capability",
    "????",
    "????",
    "????",
)


def load_profile_registry(repo_root: Path, codex_home: Path | None = None) -> dict[str, Any]:
    candidates = [
        repo_root / PROFILE_REGISTRY_RELATIVE,
        SCRIPT_DIR / "references" / "profiles.json",
    ]
    if codex_home is not None:
        candidates.append(codex_home / "skills" / "plugin-modules" / "references" / "profiles.json")
    candidates.append(default_codex_home() / "skills" / "plugin-modules" / "references" / "profiles.json")
    for path in candidates:
        try:
            if path.exists():
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    payload["_registry_source"] = str(path)
                    return payload
        except (OSError, json.JSONDecodeError):
            continue
    return {"modules": {}, "scenario_profiles": {}, "known_plugins": [], "_registry_source": None}


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def normalize_query(value: str) -> str:
    base = sanitize_text(value, limit=500).lower()
    additions = [alias for marker, alias in QUERY_SYNONYMS.items() if marker.lower() in base]
    return " ".join([base, *additions]).strip()


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


def profile_candidate_terms(profile_id: str, entry: dict[str, Any]) -> list[str]:
    terms: list[str] = [profile_id]
    terms.extend(as_string_list(entry.get("route_when")))
    terms.extend(as_string_list(entry.get("plugin_hints")))
    terms.extend(as_string_list(entry.get("plugins")))
    terms.append(str(entry.get("scenario_description") or ""))
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
    terms.append(str(scenario.get("scenario_description") or ""))
    terms.append(str(scenario.get("description") or ""))
    return terms


def build_task_module_recommendations(query_text: str, profile_id: str, entry: dict[str, Any], default_modules: list[str] | None = None) -> list[dict[str, Any]]:
    modules = entry.get("task_modules") or {}
    results: list[dict[str, Any]] = []
    default_set = set(default_modules or [])
    for module_id, module in modules.items():
        terms = [module_id, module.get("description", ""), module.get("scenario_description", "")]
        terms.extend(as_string_list(module.get("route_when")))
        terms.extend(as_string_list(module.get("positive_examples")))
        terms.extend(as_string_list(module.get("plugin_hints")))
        negative = match_terms(query_text, as_string_list(module.get("negative_examples")))
        hits = match_terms(query_text, terms)
        score = len(hits) * 10 + (2 if hits and module_id in default_set else 0) - len(negative) * 8
        if score > 0:
            results.append(
                {
                    "task_module": module_id,
                    "qualified_name": f"{profile_id}.{module_id}",
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


def score_profile_candidate(query_text: str, profile_id: str, entry: dict[str, Any], scenario_id: str | None, scenario: dict[str, Any] | None) -> dict[str, Any]:
    profile_hits = match_terms(query_text, profile_candidate_terms(profile_id, entry))
    scenario_hits = match_terms(query_text, scenario_candidate_terms(str(scenario_id), scenario)) if scenario_id and scenario else []
    negative_terms = as_string_list(entry.get("negative_examples")) + as_string_list((scenario or {}).get("negative_examples"))
    negative = match_terms(query_text, negative_terms)
    explicit_full = any(term in query_text for term in EXPLICIT_FULL_TERMS)
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
    if profile_id == "full" or load_policy == "troubleshooting-only":
        score += 20 if explicit_full else -60
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
        "load_policy": load_policy,
        "task_modules": task_modules,
        "ranking_signals": as_string_list((scenario or {}).get("ranking_signals")) or as_string_list(entry.get("ranking_signals")),
    }


def build_profile_recommendations(registry: dict[str, Any], raw_query: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    query_text = normalize_query(raw_query)
    modules = registry.get("modules") or {}
    scenarios = registry.get("scenario_profiles") or {}
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
        candidates.append(score_profile_candidate(query_text, target, entry, str(scenario_id), scenario))
    for profile_id, entry in modules.items():
        if not isinstance(entry, dict):
            continue
        key = (str(profile_id), None)
        if key in seen_keys:
            continue
        candidates.append(score_profile_candidate(query_text, str(profile_id), entry, None, None))
    excluded: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []
    for item in candidates:
        if item["negative_matches"] and item["score"] <= 0:
            excluded.append(
                {
                    "profile": item["profile"],
                    "target_profile": item["target_profile"],
                    "scenario_profile": item.get("scenario_profile"),
                    "reason": "negative_examples_matched",
                    "negative_matches": item["negative_matches"],
                }
            )
        elif item["score"] > 0:
            retained.append(item)
    if not retained:
        fallback_entry = modules.get("core-dev") if isinstance(modules.get("core-dev"), dict) else {}
        retained.append(score_profile_candidate(query_text, "core-dev", fallback_entry, "repo-dev", (registry.get("scenario_profiles") or {}).get("repo-dev") if isinstance(registry.get("scenario_profiles"), dict) else None))
        retained[-1]["score"] = max(1, int(retained[-1]["score"]))
        retained[-1]["confidence"] = max(0.35, float(retained[-1]["confidence"]))
        retained[-1]["matched_terms"] = retained[-1].get("matched_terms") or []
        retained[-1]["fallback_reason"] = "no_positive_profile_match_default_to_core_dev_preview"
    retained.sort(key=lambda item: (-int(item["score"]), 1 if item["profile"] == "full" else 0, str(item.get("scenario_profile") or item["profile"])))
    explicit_full = any(term in query_text for term in EXPLICIT_FULL_TERMS)
    if retained and retained[0]["profile"] == "full" and not explicit_full:
        non_full = [item for item in retained if item["profile"] != "full"]
        if non_full:
            retained.remove(non_full[0])
            retained.insert(0, non_full[0])
    return retained[:5], excluded[:10], explicit_full


def command_profile_suggest(args: argparse.Namespace) -> int:
    raw_query = getattr(args, "query", None) or getattr(args, "task", "")
    query = sanitize_text(raw_query, limit=500)
    repo_root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve()
    registry = load_profile_registry(repo_root, codex_home)
    recommendations, excluded, explicit_full = build_profile_recommendations(registry, query)
    selected = recommendations[0]
    selected_modules = selected.get("task_modules") or []
    target_profile = str(selected.get("target_profile") or selected.get("profile"))
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
            "selected_profile": {
                "profile": selected["profile"],
                "target_profile": target_profile,
                "scenario_profile": selected.get("scenario_profile"),
                "confidence": selected.get("confidence"),
                "load_policy": selected.get("load_policy"),
                "matched_terms": selected.get("matched_terms", []),
                "ranking_signals": selected.get("ranking_signals", []),
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
                "audit_strong_evidence_available": False,
                "audit_evidence_policy": "strong evidence may boost ranking when present but never authorizes profile apply",
                "warning_pressure_penalty_applied_to_full": not explicit_full,
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
