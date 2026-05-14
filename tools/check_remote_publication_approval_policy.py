#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "remote_publication_approval_policy"
REGISTRY_RULE_ID = "remote-publication-approval-gate"
GUARD_STEP = "check_remote_publication_approval_policy"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "Local `main` integration approval is not remote publication approval",
        "Generic continuation such as `continue`, `go on`, `proceed`, or a localized equivalent is not remote publication approval",
        "push to GitLab",
        "sync GitHub",
        "delete a remote publication branch",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "Local integration approval does not authorize remote publication",
        "remote-publication approval gate",
        "Generic `continue` / `go on` / `proceed` wording, including localized equivalents, is not enough",
        "push GitLab",
        "sync GitHub",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "本地集成批准不等于远端发布批准",
        "remote-publication approval gate",
        "泛化的 `continue` / `继续` 不足以授权远端发布",
        "推送 GitLab",
        "同步 GitHub",
    ],
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md": [
        "local integration approval and remote publication approval as separate release decisions",
        "remote-publication approval gate",
        "Generic continuation such as `continue`, `go on`, `proceed`, or a localized equivalent is not remote publication approval",
        "approved release record explicitly authorizes",
        "do not treat generic continuation as approval",
    ],
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md": [
        "本地集成批准和远端发布批准是两个独立 release decisions",
        "remote-publication approval gate",
        "泛化的 `continue`、`继续`、`go on` 或 `proceed` 不是远端发布批准",
        "approved release record 明确授权",
        "不得把泛化的继续指令当作批准",
    ],
    "openspec/specs/codex-repository-multi-session-worktree-isolation/spec.md": [
        "Remote publication SHALL require fresh explicit user approval",
        "local `main` integration approval and remote publication approval as separate release decisions",
        "SHALL NOT push to GitLab",
        "Generic continuation language such as `continue`, `go on`, `proceed`, or a localized equivalent SHALL NOT be treated as remote publication approval",
        "Generic continuation after local integration",
        "Remote publication is explicitly approved",
    ],
}

FORBIDDEN_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "generic continuation is remote publication approval",
        "continue implies remote publication",
    ],
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md": [
        "generic continuation is remote publication approval",
        "continue implies remote publication",
    ],
}


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return None


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required remote publication approval surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        for snippet in missing:
            errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_SNIPPETS.items():
        text = read_text(root / rel) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden remote-publication approval wording: {snippet}")

    guard_text = read_text(root / "tools/run_openspec_guard.py") or ""
    if GUARD_STEP not in guard_text:
        errors.append(f"tools/run_openspec_guard.py must run {GUARD_STEP}")

    registry_text = read_text(root / "tools/safety_rule_script_backing_registry.json")
    if registry_text is None:
        errors.append("Missing safety rule registry")
    else:
        try:
            registry = json.loads(registry_text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid safety rule registry JSON: {exc}")
        else:
            rules = registry.get("rules", []) if isinstance(registry, dict) else []
            matching = [rule for rule in rules if isinstance(rule, dict) and rule.get("id") == REGISTRY_RULE_ID]
            if not matching:
                errors.append(f"Safety rule registry missing rule id: {REGISTRY_RULE_ID}")
            else:
                rule = matching[0]
                for field, expected in {
                    "prompt_reminders": "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md",
                    "script_controls": "tools/check_remote_publication_approval_policy.py",
                    "guard_steps": GUARD_STEP,
                }.items():
                    values = rule.get(field, [])
                    if expected not in values:
                        errors.append(f"Safety rule {REGISTRY_RULE_ID} missing {field} entry: {expected}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "checked": checked,
        "errors": errors,
        "warnings": warnings,
        "counts": {"checked_files": len(checked), "errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify fail-closed remote publication approval policy surfaces.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("remote_publication_approval_policy: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
