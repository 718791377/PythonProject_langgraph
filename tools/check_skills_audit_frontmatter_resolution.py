#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from skills2cli import build_frontmatter_compatibility_summary  # noqa: E402


CHECK_NAME = "skills_audit_frontmatter_resolution"
DEFAULT_EVIDENCE = Path("docs_bilingual/memory/skills_usage_audit_reference_warning_resolution_2026-06-21.md")
DEFAULT_EVIDENCE_ZH = Path("docs_bilingual/memory/skills_usage_audit_reference_warning_resolution_2026-06-21.zh-CN.md")
OPTIONAL_REFERENCE = Path("reference_files/10.md")
HISTORICAL_PATTERNS = {
    "skipped_loading_286": re.compile(r"Skipped loading\s+286\s+skill", re.IGNORECASE),
    "name_limit_64": re.compile(r"invalid name:\s*exceeds maximum length of\s*64\s+characters", re.IGNORECASE),
    "description_limit_1024": re.compile(
        r"invalid description:\s*exceeds maximum length of\s*1024\s+characters",
        re.IGNORECASE,
    ),
}


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def find_historical_sources(root: Path, explicit_reference: Path | None = None) -> list[Path]:
    sources: list[Path] = []
    for candidate in (DEFAULT_EVIDENCE, DEFAULT_EVIDENCE_ZH, OPTIONAL_REFERENCE):
        path = root / candidate
        if path.exists():
            sources.append(path)
    if explicit_reference is not None and explicit_reference.exists():
        resolved = explicit_reference.resolve()
        if all(path.resolve() != resolved for path in sources):
            sources.append(explicit_reference)
    return sources


def detect_historical_issue(paths: list[Path]) -> dict[str, Any]:
    combined = "\n".join(read_text(path) for path in paths)
    pattern_hits = {
        name: bool(pattern.search(combined))
        for name, pattern in HISTORICAL_PATTERNS.items()
    }
    return {
        "detected": all(pattern_hits.values()),
        "pattern_hits": pattern_hits,
        "source_paths": [norm(path) for path in paths],
        "raw_reference_files_retained": False,
    }


def build_report(root: Path, codex_home: Path, explicit_reference: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    codex_home = codex_home.resolve()
    sources = find_historical_sources(root, explicit_reference)
    historical = detect_historical_issue(sources)
    current = build_frontmatter_compatibility_summary(root, codex_home)
    by_layer = dict(current.get("by_layer") or {})
    plugin_cache_warning_total = int(by_layer.get("plugin") or 0)
    blocking_by_layer = {
        str(layer): int(count)
        for layer, count in by_layer.items()
        if str(layer) != "plugin" and int(count or 0) > 0
    }
    blocking_invalid_total = sum(blocking_by_layer.values())
    errors: list[str] = []
    warnings: list[str] = [] if sources else ["no_historical_source_file_found"]

    if not historical["detected"]:
        errors.append("historical_reference_warning_markers_missing")
    if blocking_invalid_total != 0:
        errors.append("current_frontmatter_blocking_invalid_total_not_zero")
        # Kept as a compatibility error token for existing dashboards that have
        # not yet migrated from total-invalid semantics to controlled-layer
        # blocking semantics. Plugin-cache-only invalid entries never emit it.
        errors.append("current_frontmatter_invalid_total_not_zero")
    if plugin_cache_warning_total:
        warnings.append("plugin_cache_frontmatter_invalid_report_only_without_vendor_cache_authorization")
    for flag in ("raw_paths_retained", "raw_skill_bodies_retained", "mutates_config", "edits_plugin_cache", "profile_apply_performed"):
        if current.get(flag) is not False:
            errors.append(f"current_frontmatter_{flag}_not_false")

    resolved = not errors
    if resolved and plugin_cache_warning_total:
        interpretation = "historical_warning_current_controlled_layers_clean_plugin_cache_report_only"
    elif resolved:
        interpretation = "historical_warning_current_inventory_clean"
    else:
        interpretation = "current_invalid_or_unproven_frontmatter_resolution"
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": resolved,
        "resolved": resolved,
        "root": str(root),
        "evidence_paths": {
            "primary": norm(DEFAULT_EVIDENCE),
            "primary_zh": norm(DEFAULT_EVIDENCE_ZH),
            "optional_local_reference": norm(OPTIONAL_REFERENCE),
        },
        "historical_issue": historical,
        "current_frontmatter_compatibility": {
            **current,
            "blocking_invalid_total": blocking_invalid_total,
            "blocking_by_layer": dict(sorted(blocking_by_layer.items())),
            "plugin_cache_warning_total": plugin_cache_warning_total,
            "plugin_cache_policy": "report_only_without_vendor_cache_authorization",
        },
        "interpretation": interpretation,
        "safety": {
            "audit_only": True,
            "mutates_config": False,
            "edits_plugin_cache": False,
            "plugin_cache_mutation_allowed": False,
            "plugin_cache_policy": "report_only_without_vendor_cache_authorization",
            "hard_load_apply_performed": False,
            "raw_paths_retained": False,
            "raw_skill_bodies_retained": False,
            "raw_reference_files_retained": False,
            "profile_apply_allowed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "historical_sources": len(sources),
            "current_frontmatter_invalid_total": int(current.get("invalid_total") or 0),
            "current_frontmatter_blocking_invalid_total": blocking_invalid_total,
            "plugin_cache_warning_total": plugin_cache_warning_total,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that historical invalid SKILL.md loading warnings are resolved by current frontmatter compatibility."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--codex-home", default=str(default_codex_home()), help="Codex home to inspect.")
    parser.add_argument(
        "--reference-file",
        default=None,
        help="Optional local historical warning file such as reference_files/10.md. It remains local-only.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    explicit_reference = Path(args.reference_file).resolve() if args.reference_file else None
    report = build_report(Path(args.root), Path(args.codex_home), explicit_reference)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    elif report["ok"]:
        print(f"{CHECK_NAME}: ok ({report['interpretation']})")
    else:
        print(f"{CHECK_NAME}: failed ({report['interpretation']})")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
