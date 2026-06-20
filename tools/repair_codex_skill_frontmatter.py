#!/usr/bin/env python3
"""Audit and repair installed Codex SKILL.md frontmatter compatibility.

Default mode is read-only.  Apply mode requires `apply --operator-confirmation`
and writes backups plus rollback manifests before mutating any SKILL.md file.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from codex_skill_frontmatter import (  # noqa: E402
    CODEX_SKILL_DESCRIPTION_LIMIT,
    CODEX_SKILL_NAME_LIMIT,
    codex_frontmatter_report,
    parse_frontmatter_file,
    read_text_lossy,
    repaired_frontmatter_text,
)

SCHEMA_VERSION = 1
DEFAULT_STATE_DIR = Path("state") / "skills2cli" / "frontmatter-repair"


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return now().strftime("%Y%m%dT%H%M%SZ")


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def safe_rel(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return f"[OUTSIDE:{path.name}]"


def skill_roots(home: Path, include_plugins: bool) -> list[tuple[str, Path]]:
    roots = [("user", home / "skills")]
    if include_plugins:
        roots.append(("plugin", home / "plugins" / "cache"))
    return roots


def iter_skill_files(home: Path, include_plugins: bool) -> list[tuple[str, Path]]:
    system_root = (home / "skills" / ".system").resolve()
    rows: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for layer, root in skill_roots(home, include_plugins):
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
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
            rows.append((layer, path))
    return rows


def collect_existing_names(home: Path, include_plugins: bool) -> set[str]:
    names: set[str] = set()
    for _layer, path in iter_skill_files(home, include_plugins):
        parsed = parse_frontmatter_file(path)
        name = parsed.data.get("name")
        if name:
            names.add(name)
    return names


def audit_rows(home: Path, include_plugins: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for layer, path in iter_skill_files(home, include_plugins):
        parsed = parse_frontmatter_file(path)
        report = codex_frontmatter_report(
            parsed.data,
            parsed.frontmatter_valid,
            parsed.frontmatter_error,
            had_bom=parsed.had_bom,
        )
        name = parsed.data.get("name") or path.parent.name
        description = parsed.data.get("description") or ""
        rows.append(
            {
                "layer": layer,
                "path_hint": safe_rel(path, home),
                "name": name,
                "name_length": report["name_length"],
                "description_length": report["description_length"],
                "frontmatter_valid": parsed.frontmatter_valid,
                "frontmatter_error": parsed.frontmatter_error,
                "codex_frontmatter_compatible": report["codex_frontmatter_compatible"],
                "codex_frontmatter_errors": report["codex_frontmatter_errors"],
                "repairable": parsed.frontmatter_valid
                and bool(set(report["codex_frontmatter_errors"]) & {"name_too_long", "description_too_long", "bom_present"}),
                "description_hash": __import__("hashlib").sha256(description.encode("utf-8", errors="replace")).hexdigest()[:16],
                "absolute_path": str(path.resolve()),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid = [row for row in rows if not row["codex_frontmatter_compatible"]]
    by_error: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    for row in invalid:
        by_layer[row["layer"]] = by_layer.get(row["layer"], 0) + 1
        for error in row["codex_frontmatter_errors"]:
            by_error[error] = by_error.get(error, 0) + 1
    return {
        "total": len(rows),
        "invalid_total": len(invalid),
        "repairable_total": sum(1 for row in invalid if row.get("repairable")),
        "by_error": dict(sorted(by_error.items())),
        "by_layer": dict(sorted(by_layer.items())),
        "codex_name_limit": CODEX_SKILL_NAME_LIMIT,
        "codex_description_limit": CODEX_SKILL_DESCRIPTION_LIMIT,
    }


def filtered_rows(rows: list[dict[str, Any]], scope: str) -> list[dict[str, Any]]:
    if scope == "all":
        return rows
    return [row for row in rows if row["layer"] == scope]


def sanitized_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean = []
    for row in rows:
        item = dict(row)
        item.pop("absolute_path", None)
        clean.append(item)
    return clean


def make_plan(home: Path, rows: list[dict[str, Any]], *, scope: str, include_plugins: bool) -> dict[str, Any]:
    existing = collect_existing_names(home, include_plugins)
    actions: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for row in filtered_rows(rows, scope):
        if row["codex_frontmatter_compatible"]:
            continue
        if not row.get("repairable"):
            blockers.append({k: row[k] for k in ("layer", "path_hint", "name", "codex_frontmatter_errors")})
            continue
        path = Path(row["absolute_path"])
        original = read_text_lossy(path)
        repaired, meta = repaired_frontmatter_text(original, existing_names=existing)
        if meta.get("new_name"):
            existing.add(str(meta["new_name"]))
        actions.append(
            {
                "layer": row["layer"],
                "path_hint": row["path_hint"],
                "name": row["name"],
                "codex_frontmatter_errors": row["codex_frontmatter_errors"],
                "changes": meta.get("changes", []),
                "changed": bool(meta.get("changed")) and repaired != original,
                "plugin_cache_edit": row["layer"] == "plugin",
                "absolute_path": str(path.resolve()),
            }
        )
    return {"actions": actions, "blockers": blockers}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def apply_plan(home: Path, plan: dict[str, Any], *, state_dir: Path, include_plugins: bool) -> dict[str, Any]:
    batch = stamp()
    backup_dir = state_dir / "backups" / batch
    manifest_path = state_dir / "rollback-manifests" / f"skill-frontmatter-repair-{batch}.json"
    touched: list[dict[str, Any]] = []
    existing = collect_existing_names(home, include_plugins)
    for action in plan["actions"]:
        if not action.get("changed"):
            continue
        src = Path(action["absolute_path"])
        backup = backup_dir / safe_rel(src, home)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, backup)
        original = read_text_lossy(src)
        repaired, meta = repaired_frontmatter_text(original, existing_names=existing)
        if meta.get("new_name"):
            existing.add(str(meta["new_name"]))
        if repaired != original:
            src.write_text(repaired, encoding="utf-8", newline="\n")
        touched.append(
            {
                "layer": action["layer"],
                "path_hint": action["path_hint"],
                "backup_path": safe_rel(backup, state_dir),
                "changes": meta.get("changes", action.get("changes", [])),
                "plugin_cache_edit": action.get("plugin_cache_edit", False),
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "kind": "codex_skill_frontmatter_repair_rollback_manifest",
        "generated_at": now().isoformat(),
        "codex_home": str(home),
        "state_dir": str(state_dir),
        "backup_dir": str(backup_dir),
        "touched_count": len(touched),
        "touched": touched,
        "rollback_instructions": "Copy each backup_path from state_dir back to codex_home/path_hint to revert metadata-only frontmatter repair.",
        "mutated_config_toml": False,
        "profile_apply_performed": False,
        "hard_load_or_disable_plugin_performed": False,
        "skill_body_edits_intended": False,
    }
    write_json(manifest_path, manifest)
    return {"manifest_path": str(manifest_path), "backup_dir": str(backup_dir), "touched": touched}


def base(command: str, ok: bool, **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "ok": ok,
        "generated_at": now().isoformat(),
        "safety": {
            "dry_run_default": True,
            "mutates_config_toml": False,
            "profile_apply_performed": False,
            "hard_load_or_disable_plugin_performed": False,
            "skill_body_edits_intended": False,
            "plugin_cache_edits_separated": True,
        },
    }
    payload.update(extra)
    return payload


def command_audit(args: argparse.Namespace) -> int:
    home = Path(args.codex_home).resolve()
    rows = audit_rows(home, args.include_plugins)
    invalid = [row for row in rows if not row["codex_frontmatter_compatible"]]
    payload = base(
        "audit",
        True,
        codex_home=str(home),
        summary=summarize(rows),
        invalid=sanitized_rows(invalid[: args.limit]),
        invalid_truncated=max(0, len(invalid) - args.limit),
        mutates_user_level_state=False,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_plan(args: argparse.Namespace) -> int:
    home = Path(args.codex_home).resolve()
    rows = audit_rows(home, args.include_plugins)
    plan = make_plan(home, rows, scope=args.scope, include_plugins=args.include_plugins)
    actions = plan["actions"]
    blockers = plan["blockers"]
    payload = base(
        "plan",
        True,
        codex_home=str(home),
        scope=args.scope,
        summary=summarize(rows),
        planned_action_count=len(actions),
        blockers=blockers[: args.limit],
        actions=sanitized_rows(actions[: args.limit]),
        actions_truncated=max(0, len(actions) - args.limit),
        apply_performed=False,
        mutates_user_level_state=False,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_apply(args: argparse.Namespace) -> int:
    home = Path(args.codex_home).resolve()
    if not args.operator_confirmation:
        payload = base(
            "apply",
            False,
            codex_home=str(home),
            blockers=["operator_confirmation_required"],
            apply_performed=False,
            mutates_user_level_state=False,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 3
    rows = audit_rows(home, args.include_plugins)
    plan = make_plan(home, rows, scope=args.scope, include_plugins=args.include_plugins)
    state_dir = (Path(args.state_dir).resolve() if args.state_dir else home / DEFAULT_STATE_DIR)
    apply_result = apply_plan(home, plan, state_dir=state_dir, include_plugins=args.include_plugins)
    post_rows = audit_rows(home, args.include_plugins)
    post_summary = summarize(post_rows)
    remaining = [row for row in filtered_rows(post_rows, args.scope) if not row["codex_frontmatter_compatible"]]
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "kind": "codex_skill_frontmatter_repair_receipt",
        "generated_at": now().isoformat(),
        "codex_home": str(home),
        "scope": args.scope,
        "apply_performed": True,
        "touched_count": len(apply_result["touched"]),
        "rollback_manifest_path": apply_result["manifest_path"],
        "post_summary": post_summary,
        "remaining_invalid_for_scope": sanitized_rows(remaining[: args.limit]),
    }
    receipt_path = state_dir / "receipts" / f"skill-frontmatter-repair-{stamp()}.json"
    write_json(receipt_path, receipt)
    payload = base(
        "apply",
        len(remaining) == 0,
        codex_home=str(home),
        scope=args.scope,
        apply_performed=True,
        mutates_user_level_state=True,
        touched_count=len(apply_result["touched"]),
        rollback_manifest_path=apply_result["manifest_path"],
        receipt_path=str(receipt_path),
        post_summary=post_summary,
        remaining_invalid_for_scope=sanitized_rows(remaining[: args.limit]),
        remaining_invalid_truncated=max(0, len(remaining) - args.limit),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit or repair Codex SKILL.md frontmatter compatibility.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--codex-home", default=str(codex_home()), help="Codex home to audit or repair.")
        p.set_defaults(include_plugins=True)
        p.add_argument("--include-plugins", dest="include_plugins", action="store_true", help="Include plugin cache skills. This is the default.")
        p.add_argument("--no-plugins", dest="include_plugins", action="store_false", help="Skip plugin cache skills.")
        p.add_argument("--limit", type=int, default=25, help="Maximum detailed rows to include in JSON output.")
        p.add_argument("--json", action="store_true", help="Accepted for command symmetry; JSON is always emitted.")

    audit = sub.add_parser("audit", help="Read-only compatibility audit.")
    common(audit)
    audit.set_defaults(func=command_audit)

    plan = sub.add_parser("plan", help="Read-only repair plan / dry-run.")
    common(plan)
    plan.add_argument("--scope", choices=["user", "plugin", "all"], default="all")
    plan.set_defaults(func=command_plan)

    dry_run = sub.add_parser("dry-run", help="Alias for plan.")
    common(dry_run)
    dry_run.add_argument("--scope", choices=["user", "plugin", "all"], default="all")
    dry_run.set_defaults(func=command_plan)

    apply = sub.add_parser("apply", help="Apply metadata-only repair with backups and rollback manifest.")
    common(apply)
    apply.add_argument("--scope", choices=["user", "plugin", "all"], default="all")
    apply.add_argument("--state-dir", help="Override state directory for backups, manifests, and receipts.")
    apply.add_argument("--operator-confirmation", action="store_true", help="Required before any live mutation.")
    apply.set_defaults(func=command_apply)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
