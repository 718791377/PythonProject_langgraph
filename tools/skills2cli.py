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
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
SUMMARY_LIMIT = 160
SHOW_BODY_LIMIT = 20000
WARNING_EXCERPT_LIMIT = 240
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|]+(?:\\[^\s\"'<>|]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|]+")
TOKEN_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")
STANDALONE_SECRET_RE = re.compile(r"(?i)\b(?:sk-[a-z0-9_-]{6,}|xox[baprs]-[a-z0-9_-]{6,}|gh[pousr]_[a-z0-9_]{8,})\b")
BUDGET_WARNING_RE = re.compile(r"Exceeded skills context budget of 2%", re.IGNORECASE)
SKIPPED_LOADING_RE = re.compile(r"Skipped loading\s+\d+\s+skill|Skipped loading|invalid SKILL\.md|missing YAML frontmatter", re.IGNORECASE)


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
        frontmatter, valid, error, _body = parse_frontmatter(text)
        name = sanitize_text(frontmatter.get("name") or path.parent.name, limit=80)
        description = sanitize_text(frontmatter.get("description") or "", limit=10000)
        summary = sanitize_text(description or "No valid skill description available.", limit=SUMMARY_LIMIT)
        skill_id = build_skill_id(layer, base, path, name)
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
            )
        )
    return [asdict(record) for record in sorted(records, key=lambda item: (item.source_layer, item.name.lower(), item.skill_id))]


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
        frontmatter, valid, error, _body = parse_frontmatter(text)
        name = sanitize_text(frontmatter.get("name") or path.parent.name, limit=80)
        record_id = build_skill_id(layer, base, path, name)
        aliases = {record_id, name, f"{layer}:{name}"}
        if skill_id in aliases:
            description = sanitize_text(frontmatter.get("description") or "", limit=10000)
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


PROFILE_RULES = [
    ("browser-automation", ("browser", "chrome", "cdp", "opencli", "devtools", "tab", "screenshot")),
    ("mcp", ("mcp", "tool", "server", "facade")),
    ("communications", ("twilio", "wecom", "wxwork", "enterprise wechat", "slack", "gmail")),
    ("creative-content", ("image", "figma", "presentation", "ppt", "canvas", "design")),
    ("document-data", ("pdf", "docx", "spreadsheet", "xlsx", "document")),
    ("core-dev", ("code", "test", "git", "openspec", "docs", "governance", "python")),
]


def command_profile_suggest(args: argparse.Namespace) -> int:
    task = sanitize_text(args.task, limit=500)
    lowered = task.lower()
    suggestions = []
    for profile, keywords in PROFILE_RULES:
        hits = [keyword for keyword in keywords if keyword in lowered]
        if hits:
            suggestions.append({"profile": profile, "matched_terms": hits, "confidence": min(0.95, 0.45 + 0.1 * len(hits))})
    if not suggestions:
        suggestions.append({"profile": "core-dev", "matched_terms": [], "confidence": 0.35})
    payload = envelope(
        "profile suggest",
        {
            "task_summary": task,
            "suggestions": suggestions,
            "mutates_config": False,
            "edits_plugin_cache": False,
            "profile_apply_performed": False,
            "approval_required_for_apply": True,
            "apply_policy": "preview_only_do_not_apply_without_explicit_profile_apply_authorization",
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
    for path in sorted(sessions_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".jsonl", ".log", ".txt", ".md"}:
            continue
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


def command_audit_warnings(args: argparse.Namespace) -> int:
    codex_home = Path(args.codex_home).resolve()
    since = parse_duration_or_since(args.since)
    budget_count = 0
    skipped_count = 0
    excerpts: list[str] = []
    for text in iter_session_texts(codex_home, since) or []:
        has_budget = bool(BUDGET_WARNING_RE.search(text))
        has_skipped = bool(SKIPPED_LOADING_RE.search(text))
        if has_budget:
            budget_count += len(BUDGET_WARNING_RE.findall(text)) or 1
        if has_skipped:
            skipped_count += len(SKIPPED_LOADING_RE.findall(text)) or 1
        if (has_budget or has_skipped) and len(excerpts) < args.limit:
            excerpts.append(sanitize_text(text, limit=WARNING_EXCERPT_LIMIT))
    payload = envelope(
        "audit warnings",
        {
            "since": since.isoformat(),
            "budget_warning_count": budget_count,
            "skipped_loading_count": skipped_count,
            "recent_sanitized_excerpts": excerpts,
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
    suggest.add_argument("--task", required=True)
    suggest.add_argument("--root", default=str(default_repo_root()))
    suggest.add_argument("--codex-home", default=str(default_codex_home()))
    suggest.add_argument("--json", action="store_true")
    suggest.set_defaults(func=command_profile_suggest)

    audit = subparsers.add_parser("audit", help="Audit commands.")
    audit_sub = audit.add_subparsers(dest="audit_command")
    warnings = audit_sub.add_parser("warnings", help="Summarize skills budget/skipped-loading warnings.")
    warnings.add_argument("--since", required=True, help="Duration such as 7d/24h/30m or an ISO timestamp.")
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
