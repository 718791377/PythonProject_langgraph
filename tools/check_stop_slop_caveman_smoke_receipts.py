#!/usr/bin/env python3
"""Validate Stop-Slop/Caveman R4 smoke receipts."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from user_level_receipt_governance import collect_redaction_findings, smoke_summary, stable_hash, validate_smoke_receipt


CHECK_NAME = "stop_slop_caveman_smoke_receipts"
TOOL_NAME = "Stop-Slop-Caveman"
OWNER_LANE = "stop-slop-caveman-response-density"
FORBIDDEN_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
RAW_PRIVATE_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+"),
    re.compile(r"\\\\[^\s\"']+"),
    re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+"),
)
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
SENSITIVE_COMMAND_RE = re.compile(r"(?i)\b(?:rewrite\s+--apply|--apply|write|mutate|hook|install|push|send|delete)\b")


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def hash_text(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return stable_hash(text)


def load_receipt(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, [f"receipt_missing:{hash_text(str(path))}"]
    except json.JSONDecodeError:
        return None, [f"receipt_invalid_json:{path.name}"]
    except OSError:
        return None, [f"receipt_unreadable:{hash_text(str(path))}"]
    if not isinstance(data, dict):
        return None, [f"receipt_not_object:{path.name}"]
    return data, []


def receipt_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.receipt_dir:
        directory = Path(args.receipt_dir)
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    paths.extend(Path(value) for value in args.receipt)
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


def contains_raw_path_or_secret(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    findings = [f"raw_private_path:{pattern.pattern}" for pattern in RAW_PRIVATE_PATH_PATTERNS if pattern.search(text)]
    if SECRET_RE.search(text):
        findings.append("raw_secret")
    return sorted(set(findings))


def receipt_is_blocked(receipt: dict[str, Any]) -> bool:
    result = receipt.get("smoke_result")
    result_status = str(result.get("status", "") if isinstance(result, dict) else result).strip().lower()
    r4_status = str(receipt.get("r4_status", "")).strip().lower()
    return receipt.get("smoke_tested") is not True and (
        result_status in {"blocked", "not-installed", "not_installed"}
        or r4_status in {"blocked", "not-installed", "not_installed"}
    )


def validate_blocked(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    blockers = receipt.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append("blocked_receipt_requires_blockers")
    if receipt.get("smoke_tested") is True:
        errors.append("blocked_receipt_must_not_be_smoke_tested")
    if receipt.get("rollback_ready") is True:
        errors.append("blocked_receipt_must_not_claim_rollback_ready")
    for flag in FORBIDDEN_FLAGS:
        if receipt.get(flag) is True:
            errors.append(f"blocked_receipt_forbidden_{flag}")
    return errors


def validate_positive(receipt: dict[str, Any], path: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    errors.extend(validate_smoke_receipt(receipt, tool_name=TOOL_NAME, owner_lane=OWNER_LANE))
    if receipt.get("owner_lane") != OWNER_LANE:
        errors.append("owner_lane_mismatch")
    if receipt.get("tool_name") != TOOL_NAME:
        errors.append("tool_name_mismatch")
    if receipt.get("smoke_tested") is not True:
        errors.append("positive_receipt_must_set_smoke_tested_true")
    for flag in FORBIDDEN_FLAGS:
        if receipt.get(flag) is True:
            errors.append(f"forbidden_{flag}")
    if SENSITIVE_COMMAND_RE.search(str(receipt.get("smoke_command", ""))):
        errors.append("sensitive_smoke_command")
    for field in ("install_receipt", "rollback_pointer", "command_transcript"):
        for finding in contains_raw_path_or_secret(receipt.get(field)):
            errors.append(f"{field}:{finding}")
    for finding in collect_redaction_findings(receipt):
        errors.append(f"redaction:{finding}")
    return sorted(set(errors)), smoke_summary(receipt, receipt_path=path)


def validate_receipts(paths: list[Path], *, require_smoke_tested: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    summaries: list[dict[str, Any]] = []
    positive_count = 0
    blocked_count = 0
    for path in paths:
        receipt, load_errors = load_receipt(path)
        errors.extend(load_errors)
        if receipt is None:
            continue
        if receipt.get("tool_name") != TOOL_NAME:
            errors.append(f"{path.name}:tool_name_mismatch")
            continue
        if receipt_is_blocked(receipt):
            blocked_count += 1
            errors.extend(f"{path.name}:{item}" for item in validate_blocked(receipt))
            summaries.append(
                {
                    "receipt_file": path.name,
                    "receipt_path_hash": stable_hash(str(path)),
                    "r4_status": receipt.get("r4_status"),
                    "smoke_tested": False,
                    "blockers": receipt.get("blockers", []),
                }
            )
            continue
        receipt_errors, summary = validate_positive(receipt, path)
        if receipt_errors:
            errors.extend(f"{path.name}:{item}" for item in receipt_errors)
        else:
            positive_count += 1
        summaries.append(summary)
    if require_smoke_tested and positive_count < 1:
        errors.append("positive_smoke_tested_receipt_required")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summaries": summaries,
        "counts": {
            "receipts": len(paths),
            "positive_smoke_tested": positive_count,
            "blocked_or_not_installed": blocked_count,
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stop-Slop/Caveman R4 smoke receipts.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--receipt-dir", help="Directory containing receipt JSON files.")
    parser.add_argument("--receipt", action="append", default=[], help="Single receipt path.")
    parser.add_argument("--require-smoke-tested", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = receipt_paths(args)
    if paths:
        result = validate_receipts(paths, require_smoke_tested=args.require_smoke_tested)
    else:
        result = {
            "ok": True,
            "errors": [],
            "warnings": ["no_receipts_supplied; repo-surface guard only"],
            "summaries": [],
            "counts": {"receipts": 0, "positive_smoke_tested": 0, "blocked_or_not_installed": 0, "errors": 0, "warnings": 1},
        }
    payload = {"schema_version": 1, "check_name": CHECK_NAME, **result}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
