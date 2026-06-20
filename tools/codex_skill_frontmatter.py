#!/usr/bin/env python3
"""Codex SKILL.md frontmatter compatibility helpers.

These helpers intentionally parse and rewrite only the YAML-like frontmatter
block.  They do not interpret, remove, or rewrite the skill body.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CODEX_SKILL_NAME_LIMIT = 64
CODEX_SKILL_DESCRIPTION_LIMIT = 1024
SHORT_NAME_HASH_LENGTH = 8

_NAME_TOKEN_RE = re.compile(r"[^A-Za-z0-9-]+")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class FrontmatterParseResult:
    data: dict[str, str]
    body: str
    raw_frontmatter: str
    frontmatter_valid: bool
    frontmatter_error: str | None
    had_bom: bool = False


def read_text_lossy(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter_text(text: str) -> FrontmatterParseResult:
    had_bom = text.startswith("\ufeff")
    if had_bom:
        text = text[1:]
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return FrontmatterParseResult({}, normalized, "", False, "missing_yaml_frontmatter", had_bom)
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return FrontmatterParseResult({}, normalized, normalized[4:], False, "unterminated_yaml_frontmatter", had_bom)
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
    error = "missing_" + "_".join(missing) if missing else None
    return FrontmatterParseResult(data, body, raw, error is None, error, had_bom)


def parse_frontmatter_file(path: Path) -> FrontmatterParseResult:
    return parse_frontmatter_text(read_text_lossy(path))


def codex_frontmatter_errors(
    data: dict[str, str],
    frontmatter_valid: bool,
    frontmatter_error: str | None,
    *,
    had_bom: bool = False,
) -> list[str]:
    errors: list[str] = []
    if had_bom:
        errors.append("bom_present")
    if not frontmatter_valid and frontmatter_error:
        errors.append(frontmatter_error)
    name = str(data.get("name", "") or "")
    description = str(data.get("description", "") or "")
    if name and len(name) > CODEX_SKILL_NAME_LIMIT:
        errors.append("name_too_long")
    if description and len(description) > CODEX_SKILL_DESCRIPTION_LIMIT:
        errors.append("description_too_long")
    return errors


def codex_frontmatter_report(
    data: dict[str, str],
    frontmatter_valid: bool,
    frontmatter_error: str | None,
    *,
    had_bom: bool = False,
) -> dict[str, Any]:
    errors = codex_frontmatter_errors(data, frontmatter_valid, frontmatter_error, had_bom=had_bom)
    name = str(data.get("name", "") or "")
    description = str(data.get("description", "") or "")
    return {
        "codex_frontmatter_compatible": not errors,
        "codex_frontmatter_errors": errors,
        "name_length": len(name),
        "description_length": len(description),
        "codex_name_limit": CODEX_SKILL_NAME_LIMIT,
        "codex_description_limit": CODEX_SKILL_DESCRIPTION_LIMIT,
        "had_bom": had_bom,
    }


def slugify_skill_name(value: str) -> str:
    text = value.strip().lower().replace("_", "-")
    text = _NAME_TOKEN_RE.sub("-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "skill"


def stable_short_name(name: str, *, existing: set[str] | None = None, limit: int = CODEX_SKILL_NAME_LIMIT) -> str:
    existing = set(existing or set())
    slug = slugify_skill_name(name)
    if len(slug) <= limit and slug not in existing:
        return slug
    digest = hashlib.sha256(name.encode("utf-8", errors="replace")).hexdigest()[:SHORT_NAME_HASH_LENGTH]
    suffix = "-" + digest
    prefix_limit = max(1, limit - len(suffix))
    prefix = slug[:prefix_limit].rstrip("-") or "skill"
    candidate = (prefix + suffix)[:limit]
    if candidate not in existing:
        return candidate
    for index in range(2, 1000):
        indexed_suffix = f"-{digest}-{index}"
        prefix_limit = max(1, limit - len(indexed_suffix))
        candidate = ((slug[:prefix_limit].rstrip("-") or "skill") + indexed_suffix)[:limit]
        if candidate not in existing:
            return candidate
    raise RuntimeError("unable_to_generate_unique_short_skill_name")


def compact_description(description: str, *, limit: int = CODEX_SKILL_DESCRIPTION_LIMIT) -> str:
    text = _WHITESPACE_RE.sub(" ", description).strip()
    if len(text) <= limit:
        return text
    marker = "...[truncated]"
    return text[: max(0, limit - len(marker))].rstrip() + marker


def render_frontmatter(data: dict[str, str], body: str) -> str:
    ordered_keys = ["name", "description"]
    lines = ["---"]
    emitted: set[str] = set()
    for key in ordered_keys:
        if key in data:
            lines.append(f"{key}: {data[key]}")
            emitted.add(key)
    for key in sorted(k for k in data if k not in emitted):
        lines.append(f"{key}: {data[key]}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def repaired_frontmatter_text(text: str, *, existing_names: set[str] | None = None) -> tuple[str, dict[str, Any]]:
    parsed = parse_frontmatter_text(text)
    data = dict(parsed.data)
    changes: list[str] = []
    if not parsed.frontmatter_valid:
        return text, {"changed": False, "changes": changes, "blocked": parsed.frontmatter_error or "invalid_frontmatter"}
    original_name = data.get("name", "")
    if len(original_name) > CODEX_SKILL_NAME_LIMIT:
        new_name = stable_short_name(original_name, existing=existing_names)
        data["name"] = new_name
        changes.append("name_shortened")
    original_description = data.get("description", "")
    if len(original_description) > CODEX_SKILL_DESCRIPTION_LIMIT:
        data["description"] = compact_description(original_description)
        changes.append("description_shortened")
    if not changes and not parsed.had_bom:
        return text, {"changed": False, "changes": changes}
    if parsed.had_bom:
        changes.append("bom_removed")
    return render_frontmatter(data, parsed.body), {"changed": True, "changes": changes, "new_name": data.get("name", "")}
