#!/usr/bin/env python3
"""Dry-run-only Spec Kit subordinate adapter runtime.

This helper never installs Spec Kit, never invokes ``specify``, never creates
``.specify/`` or root ``specs/``, and never writes generated ``/speckit.*`` or
``$speckit-*`` command surfaces.  It emits machine-readable receipts that the
Spec Kit authority guard can validate before any future live adapter work is
considered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "spec_kit_subordinate_runtime"
SOURCE_URL = "https://github.com/github/spec-kit"
SOURCE_PIN = "7106858c4e636098815fffa23f6c6b99eb0e156b"
REQUIRED_PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
MODES = ("source-refresh", "probe", "plan-dry-run", "init-dry-run", "self-check-dry-run")
SURFACE_KEYS = (
    "specify_init",
    "specify_init_force",
    "specify_self_check",
    ".specify/",
    "specs/",
    "/speckit.*",
    "$speckit-*",
    "extensions",
    "presets",
    "workflow_outputs",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def has_speckit_path(root: Path, prefix: str) -> bool:
    target = root / prefix
    if not target.exists():
        return False
    for path in target.rglob("*") if target.is_dir() else [target]:
        rel = path.relative_to(root).as_posix().lower()
        if "speckit" in rel:
            return True
    return False


def surface_status(root: Path) -> dict[str, str]:
    return {
        "specify_init": "blocked",
        "specify_init_force": "blocked",
        "specify_self_check": "blocked",
        ".specify/": "present-blocked" if (root / ".specify").exists() else "absent",
        "specs/": "present-blocked" if (root / "specs").exists() else "absent",
        "/speckit.*": "blocked",
        "$speckit-*": "blocked",
        "extensions": "present-blocked" if has_speckit_path(root, "extensions") else "absent",
        "presets": "present-blocked" if has_speckit_path(root, "presets") else "absent",
        "workflow_outputs": "present-blocked" if has_speckit_path(root, "workflow_outputs") else "absent",
    }


def discover_blockers(root: Path, mode: str, surfaces: dict[str, str]) -> list[str]:
    blockers: list[str] = []
    if surfaces[".specify/"] != "absent":
        blockers.append(".specify_present")
    if surfaces["specs/"] != "absent":
        blockers.append("root_specs_present")
    if surfaces["extensions"] != "absent":
        blockers.append("speckit_extensions_present")
    if surfaces["presets"] != "absent":
        blockers.append("speckit_presets_present")
    if surfaces["workflow_outputs"] != "absent":
        blockers.append("speckit_workflow_outputs_present")
    generated_roots = (
        root / ".codex" / "commands",
        root / ".codex" / "skills",
        root / ".github" / "prompts",
    )
    for generated_root in generated_roots:
        if not generated_root.exists():
            continue
        for path in generated_root.rglob("*"):
            if "speckit" in path.relative_to(root).as_posix().lower():
                blockers.append("generated_speckit_command_surface_present")
                break
    for path in root.glob("speckit.*"):
        if path.exists():
            blockers.append("root_speckit_file_present")
            break
    for path in root.glob("speckit-*"):
        if path.exists():
            blockers.append("root_speckit_file_present")
            break
    return sorted(set(blockers))


def build_receipt(root: Path, mode: str, timeout_seconds: int) -> dict[str, Any]:
    surfaces = surface_status(root)
    blockers = discover_blockers(root, mode, surfaces)
    decision = "blocked" if blockers else "subordinate"
    ok = not blockers
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "runtime": CHECK_NAME,
        "mode": mode,
        "ok": ok,
        "blockers": blockers,
        "dry_run_only": True,
        "would_run_specify": False,
        "runs_specify": False,
        "installs_spec_kit": False,
        "creates_specify_directory": False,
        "creates_root_specs": False,
        "writes_speckit_commands": False,
        "mutates_repo_state": False,
        "mutates_user_level_state": False,
        "source_url": SOURCE_URL,
        "source_pin": SOURCE_PIN,
        "source_reference_kind": "pinned-official-reference-only",
        "authority_decision": {
            "decision": decision,
            "winning_authority": "Comet/OpenSpec/Superpowers/local-main-first gates",
            "priority_order": REQUIRED_PRIORITY_ORDER,
            "reason": "Spec Kit remains a subordinate dry-run/probe source; live initialization and generated surfaces are blocked.",
            "blockers": blockers,
        },
        "surface_status": surfaces,
        "redaction": {
            "status": "pass",
            "raw_private_paths_in_output": False,
            "redacted_root_hash": stable_hash(str(root.resolve())),
        },
        "timeout": {
            "seconds": timeout_seconds,
            "released": True,
            "mode": "bounded-dry-run",
        },
        "rollback_pointer": "not-needed-dry-run-no-spec-kit-surfaces-written",
        "local_main_first_validation": {
            "status": "not_required_for_dry_run",
            "mutates_git": False,
            "requires_local_gate_before_live_use": True,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Spec Kit subordinate adapter dry-run runtime.")
    parser.add_argument("mode", choices=MODES, help="Dry-run-only runtime mode.")
    parser.add_argument("--root", default=".", help="Repository root to inspect without mutation.")
    parser.add_argument("--receipt-out", default=None, help="Optional path to write the JSON receipt.")
    parser.add_argument("--timeout-seconds", type=int, default=10, help="Recorded timeout budget for the dry-run receipt.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    receipt = build_receipt(root, args.mode, max(1, int(args.timeout_seconds)))
    if args.receipt_out:
        out = Path(args.receipt_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{args.mode}: {'ok' if receipt['ok'] else 'blocked'}")
        for blocker in receipt["blockers"]:
            print(f"BLOCKER: {blocker}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
