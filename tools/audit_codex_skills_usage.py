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
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SKILL_ANNOUNCE_PATTERNS = [
    re.compile(r"使用技能[:：]\s*([^\n\r]+)"),
    re.compile(r"Using skill[s]?[:：]\s*([^\n\r]+)", re.IGNORECASE),
]
BACKTICK_PATTERN = re.compile(r"`([^`]+)`")
SKILL_PATH_PATTERN = re.compile(r"([A-Z]:\\[^\s\"']*?SKILL\.md)", re.IGNORECASE)
BUDGET_WARNING_PATTERN = re.compile(r"Exceeded skills context budget of 2%", re.IGNORECASE)
OMITTED_PATTERN = re.compile(r"(\d+)\s+additional skills", re.IGNORECASE)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


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
        if any(token in as_text for token in ("SKILL.md", "Using skill", "使用技能", "load_module.ps1", "set_plugin_profile.ps1")):
            texts.append(as_text[:60000])
    return texts


def extract_skill_names(segment: str) -> list[str]:
    # Count only explicit backticked skill names. This avoids treating policy
    # prose such as "使用技能：xxx" or bullet text as actual usage evidence.
    names = [name.strip() for name in BACKTICK_PATTERN.findall(segment) if name.strip()]
    return [name for name in names if re.match(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{1,79}$", name)]


def scan_sessions(codex_home: Path, repo_root: Path, cutoff: datetime, modules: set[str]) -> dict[str, Any]:
    sessions_root = codex_home / "sessions"
    explicit_skills: Counter[str] = Counter()
    skill_paths: Counter[str] = Counter()
    profile_helper_calls: Counter[str] = Counter()
    weak_plugin_mentions: Counter[str] = Counter()
    tool_call_names: Counter[str] = Counter()
    files_scanned = 0
    lines_scanned = 0
    known_plugins = load_known_plugins(codex_home)

    if not sessions_root.exists():
        return {
            "files_scanned": 0,
            "lines_scanned": 0,
            "explicit_skills": {},
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
                        for name in extract_skill_names(match.group(1)[:300]):
                            explicit_skills[name] += 1
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
        "skill_paths": dict(skill_paths.most_common()),
        "profile_helper_calls": dict(profile_helper_calls.most_common()),
        "tool_call_names": dict(tool_call_names.most_common()),
        "weak_plugin_mentions": dict(weak_plugin_mentions.most_common()),
    }


def load_profiles(codex_home: Path) -> dict[str, Any]:
    path = codex_home / "skills" / "plugin-modules" / "references" / "profiles.json"
    return read_json(path)


def load_known_plugins(codex_home: Path) -> list[str]:
    profiles = load_profiles(codex_home)
    known = profiles.get("known_plugins")
    if isinstance(known, list):
        return [str(item) for item in known]
    return []


def scan_logs(codex_home: Path, cutoff: datetime) -> dict[str, Any]:
    db = codex_home / "logs_2.sqlite"
    warnings: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    if not db.exists():
        return {"available": False, "budget_warning_count": 0, "recent_budget_warnings": [], "skipped_loading_count": 0}
    cutoff_epoch = int(cutoff.timestamp())
    con = sqlite3.connect(str(db))
    try:
        cur = con.cursor()
        cur.execute(
            "select ts, level, target, feedback_log_body from logs where ts >= ? and feedback_log_body is not null and (feedback_log_body like ? or feedback_log_body like ?) order by ts desc",
            (cutoff_epoch, "%Exceeded skills context budget%", "%Skipped loading%"),
        )
        for ts, level, target, body in cur.fetchall():
            dt = datetime.fromtimestamp(int(ts), timezone.utc).astimezone().isoformat()
            body_text = str(body or "")
            omitted_match = OMITTED_PATTERN.search(body_text)
            row = {
                "time": dt,
                "level": level,
                "target": target,
                "omitted_additional_skills": int(omitted_match.group(1)) if omitted_match else None,
                "all_descriptions_removed": "All skill descriptions were removed" in body_text,
                "message_excerpt": body_text[:500],
            }
            if BUDGET_WARNING_PATTERN.search(body_text):
                warnings.append(row)
            if "Skipped loading" in body_text:
                skipped.append(row)
    finally:
        con.close()
    return {
        "available": True,
        "budget_warning_count": len(warnings),
        "recent_budget_warnings": warnings[:20],
        "skipped_loading_count": len(skipped),
        "recent_skipped_loading": skipped[:20],
    }


def build_module_evidence(profiles: dict[str, Any], session_data: dict[str, Any]) -> list[dict[str, Any]]:
    modules = profiles.get("modules") if isinstance(profiles.get("modules"), dict) else {}
    helper_counts = Counter(session_data.get("profile_helper_calls", {}))
    skill_path_counts = Counter(session_data.get("skill_paths", {}))
    weak_mentions = Counter(session_data.get("weak_plugin_mentions", {}))
    rows: list[dict[str, Any]] = []
    for module_name, module in modules.items():
        plugins = [str(item) for item in module.get("plugins", [])] if isinstance(module, dict) else []
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
        strong_total = helper + strong_path
        if strong_total >= 5:
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
                "weak_plugin_mentions": weak,
                "recommendation": recommendation,
            }
        )
    return rows


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    codex_home = Path(args.codex_home).resolve() if args.codex_home else default_codex_home().resolve()
    generated_at = now_utc()
    if args.since:
        cutoff = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    else:
        cutoff = generated_at - timedelta(days=max(args.days, 0))
    profiles = load_profiles(codex_home)
    modules = set((profiles.get("modules") or {}).keys()) if isinstance(profiles.get("modules"), dict) else set()
    plugins_config = parse_plugin_config(codex_home / "config.toml")
    enabled_plugins = sorted([name for name, enabled in plugins_config.items() if enabled is True])
    disabled_plugins = sorted([name for name, enabled in plugins_config.items() if enabled is False])
    session_data = scan_sessions(codex_home, root, cutoff, modules)
    logs_data = scan_logs(codex_home, cutoff)
    inventory_counts = collect_inventory_counts(codex_home, root)
    module_evidence = build_module_evidence(profiles, session_data)
    report = {
        "schema_version": 1,
        "generated_at": generated_at.isoformat(),
        "check_name": "codex_skills_usage_audit",
        "mode": "baseline" if args.baseline else "usage_audit",
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
        },
        "inventory_summary": inventory_counts,
        "log_evidence": logs_data,
        "session_evidence": session_data,
        "module_evidence": module_evidence,
        "recommendations": [
            "Do not treat another 2% budget warning as soft-load failure; soft-load is outside the model-visible skills budget surface.",
            "Continue audit-only mode until the agreed window closes unless a concrete task requires a profile preview or explicitly approved hard-load apply.",
            "Use strong evidence, not weak mentions, to decide default profile changes.",
            "Keep disabled plugins restorable; do not delete plugin cache or vendor SKILL.md files.",
        ],
    }
    return report


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
    args = parser.parse_args()

    report = build_report(args)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
