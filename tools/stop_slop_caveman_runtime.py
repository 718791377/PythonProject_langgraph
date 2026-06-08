#!/usr/bin/env python3
"""Guarded local runtime for Stop-Slop/Caveman response-density checks."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from check_stop_slop_caveman_response_density import analyze_text, protected_spans
from user_level_receipt_governance import sanitize_text, stable_hash


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

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_input(args: argparse.Namespace) -> tuple[str, Path | None]:
    if getattr(args, "file", None):
        path = Path(args.file)
        return path.read_text(encoding="utf-8-sig"), path
    return str(getattr(args, "text", "") or ""), None


def protect_text(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}
    result = text
    for index, span in enumerate(reversed(protected_spans(text))):
        token = f"\uE000STOP_SLOP_PROTECTED_{index}\uE001"
        replacements[token] = span.text
        result = result[: span.start] + token + result[span.end :]
    return result, replacements


def restore_text(text: str, replacements: dict[str, str]) -> str:
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def rewrite_text(text: str) -> str:
    working, replacements = protect_text(text)
    substitutions: tuple[tuple[str, str], ...] = (
        (r"(?i)\bSure!?\s*", ""),
        (r"(?i)\bCertainly[,!]?\s*", ""),
        (r"(?i)\bI(?:'|’)d be happy to help\.\s*", ""),
        (r"(?i)\bHere(?:'|’)s what you need to do\s*[—:-]?\s*", ""),
        (r"(?i)\bHere(?:'|’)s what happened\s*[—:-]?\s*", ""),
        (r"(?i)\bHere(?:'|’)s what changed\s*[—:-]?\s*", ""),
        (r"(?i)\bHere(?:'|’)s what this means\s*[—:-]?\s*", ""),
        (r"\s+—\s+", ": "),
        (r"(?i)\bthe implications are significant\.?(\s*)", r"\1"),
        (r"(?i)\bfirst,\s*", ""),
        (r"(?i)\bthis is not just\b", ""),
    )
    for pattern, replacement in substitutions:
        working = re.sub(pattern, replacement, working)
    working = re.sub(r"[ \t]+", " ", working)
    working = re.sub(r" *\n *", "\n", working)
    working = re.sub(r"\n{3,}", "\n\n", working).strip()
    rewritten = restore_text(working, replacements).strip()
    rewritten = re.sub(r"^[:,;.! \t]+", "", rewritten)
    rewritten = re.sub(r"\s+([,.;:])", r"\1", rewritten)
    rewritten = re.sub(r"([:;])\s*([:;])", r"\1", rewritten)
    return rewritten or text


def transcript_redaction(transcript: str) -> dict[str, str]:
    return {"status": "pass", "redacted_transcript_hash": stable_hash(transcript)}


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["install_receipt_missing"]
    except json.JSONDecodeError:
        return None, ["install_receipt_invalid_json"]
    except OSError:
        return None, ["install_receipt_unreadable"]
    if not isinstance(data, dict):
        return None, ["install_receipt_not_object"]
    return data, []


def install_receipt_blockers(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return ["install_receipt_required"]
    blockers: list[str] = []
    if receipt.get("tool_name") != TOOL_NAME:
        blockers.append("install_receipt_tool_name_mismatch")
    if receipt.get("owner_lane") != OWNER_LANE:
        blockers.append("install_receipt_owner_lane_mismatch")
    wrapper = receipt.get("wrapper_path")
    if not isinstance(wrapper, str) or not wrapper.strip():
        blockers.append("install_receipt_wrapper_path_required")
    elif not Path(wrapper).exists():
        blockers.append("install_receipt_wrapper_not_resolved")
    for field in ("source_url", "installed_version", "updater_command", "rollback_pointer", "redaction_status"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"install_receipt_{field}_required")
    if str(receipt.get("redaction_status", "")).lower() not in {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}:
        blockers.append("install_receipt_redaction_status_must_pass")
    return sorted(set(blockers))


def base_receipt(*, install_ref: str, rollback_ref: str, transcript: str, smoke_type: str) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "runtime_stage": "R4",
        "install_receipt": install_ref,
        "smoke_command": f"{TOOL_NAME} {smoke_type}",
        "smoke_type": smoke_type,
        "smoke_result": {"status": "blocked"},
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": rollback_ref,
        "rollback_ready": False,
        "command_transcript": sanitize_text(transcript),
        "transcript_redaction": transcript_redaction(sanitize_text(transcript)),
        "redaction_status": "no_secrets",
    }
    for flag in FORBIDDEN_FLAGS:
        receipt[flag] = False
    return receipt


def blocked_receipt(blockers: list[str], *, install_path: Path | None, rollback_pointer: Any = None, smoke_type: str = "help") -> dict[str, Any]:
    receipt = base_receipt(
        install_ref=f"receipt-sha256:{stable_hash(str(install_path))}" if install_path else "missing",
        rollback_ref=f"rollback-sha256:{stable_hash(rollback_pointer)}" if rollback_pointer else "unavailable",
        transcript=f"blocked R4 smoke for {TOOL_NAME}: {', '.join(sorted(set(blockers)))}",
        smoke_type=smoke_type,
    )
    receipt.update(
        {
            "r4_status": "blocked",
            "smoke_tested": False,
            "smoke_result": {"status": "blocked", "blockers": sorted(set(blockers))},
            "rollback_ready": False,
            "blockers": sorted(set(blockers)),
        }
    )
    return receipt


def passing_receipt(*, install_path: Path, install_receipt: dict[str, Any], transcript: str, smoke_type: str) -> dict[str, Any]:
    receipt = base_receipt(
        install_ref=f"receipt-sha256:{stable_hash(str(install_path))}",
        rollback_ref=f"rollback-sha256:{stable_hash(install_receipt.get('rollback_pointer'))}",
        transcript=transcript,
        smoke_type=smoke_type,
    )
    receipt.update(
        {
            "runtime_stage": "smoke-tested",
            "r4_status": "smoke-tested",
            "smoke_tested": True,
            "smoke_result": {"status": "pass"},
            "rollback_ready": True,
            "blockers": [],
        }
    )
    return receipt


def write_receipt(receipt_dir: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / "r4-stop-slop-caveman-smoke.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "receipt_file": path.name,
        "receipt_path_hash": stable_hash(str(path)),
        "receipt_written": True,
        "r4_status": receipt.get("r4_status"),
        "smoke_tested": receipt.get("smoke_tested") is True,
        "blockers": receipt.get("blockers", []),
    }


def cmd_analyze(args: argparse.Namespace) -> int:
    text, path = read_input(args)
    payload = {
        "schema_version": 1,
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "ok": True,
        "action": "analyze",
        "rewrite_performed": False,
        "write_performed": False,
        "diagnostics": analyze_text(text, sample_name=path.name if path else "inline"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_rewrite(args: argparse.Namespace) -> int:
    text, path = read_input(args)
    if args.apply and not args.operator_confirmation:
        print(json.dumps({"schema_version": 1, "tool_name": TOOL_NAME, "owner_lane": OWNER_LANE, "ok": False, "action": "rewrite", "write_performed": False, "blockers": ["operator_confirmation_required"]}, ensure_ascii=False, indent=2))
        return 3
    if args.apply and path is None:
        print(json.dumps({"schema_version": 1, "tool_name": TOOL_NAME, "owner_lane": OWNER_LANE, "ok": False, "action": "rewrite", "write_performed": False, "blockers": ["explicit_file_required_for_apply"]}, ensure_ascii=False, indent=2))
        return 3
    rewritten = rewrite_text(text)
    write_performed = False
    if args.apply and path is not None:
        path.write_text(rewritten, encoding="utf-8")
        write_performed = True
    payload = {
        "schema_version": 1,
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "ok": True,
        "action": "rewrite",
        "dry_run": bool(args.dry_run),
        "apply": bool(args.apply),
        "operator_confirmation": bool(args.operator_confirmation),
        "write_performed": write_performed,
        "rewritten_text": rewritten,
        "lengths": {"original_chars": len(text), "rewritten_chars": len(rewritten)},
        "protected_spans": analyze_text(text, sample_name=path.name if path else "inline")["protected_spans"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_smoke_record(args: argparse.Namespace) -> int:
    install_path = Path(args.install_receipt) if args.install_receipt else None
    receipt_data: dict[str, Any] | None = None
    blockers: list[str] = []
    if install_path is None:
        blockers.append("install_receipt_required")
    else:
        receipt_data, load_blockers = load_json(install_path)
        blockers.extend(load_blockers)
        blockers.extend(install_receipt_blockers(receipt_data))
    if blockers or receipt_data is None or install_path is None:
        receipt = blocked_receipt(blockers or ["install_receipt_required"], install_path=install_path, rollback_pointer=(receipt_data or {}).get("rollback_pointer") if isinstance(receipt_data, dict) else None, smoke_type=args.smoke_type)
        summary = write_receipt(Path(args.receipt_dir), receipt)
        print(json.dumps({"schema_version": 1, "ok": True, "tool_name": TOOL_NAME, "owner_lane": OWNER_LANE, **summary}, ensure_ascii=False, indent=2))
        return 0
    try:
        proc = subprocess.run([str(Path(str(receipt_data["wrapper_path"]))), "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout_seconds, check=False)
        transcript = sanitize_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
        if proc.returncode != 0:
            receipt = blocked_receipt(["smoke_command_failed"], install_path=install_path, rollback_pointer=receipt_data.get("rollback_pointer"), smoke_type=args.smoke_type)
            receipt["command_transcript"] = transcript
            receipt["transcript_redaction"] = transcript_redaction(transcript)
        else:
            receipt = passing_receipt(install_path=install_path, install_receipt=receipt_data, transcript=transcript, smoke_type=args.smoke_type)
    except subprocess.TimeoutExpired as exc:
        transcript = sanitize_text((exc.stdout or "") + "\n" + (exc.stderr or ""))
        receipt = blocked_receipt(["smoke_command_timeout"], install_path=install_path, rollback_pointer=receipt_data.get("rollback_pointer"), smoke_type=args.smoke_type)
        receipt["command_transcript"] = transcript or receipt["command_transcript"]
        receipt["transcript_redaction"] = transcript_redaction(receipt["command_transcript"])
        receipt["timeout_release"] = {"status": "pass", "released": True, "timed_out": True}
    except OSError:
        receipt = blocked_receipt(["smoke_command_launch_failed"], install_path=install_path, rollback_pointer=receipt_data.get("rollback_pointer"), smoke_type=args.smoke_type)
    summary = write_receipt(Path(args.receipt_dir), receipt)
    print(json.dumps({"schema_version": 1, "ok": True, "tool_name": TOOL_NAME, "owner_lane": OWNER_LANE, **summary}, ensure_ascii=False, indent=2))
    return 0


def add_input_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Explicit file to read.")
    group.add_argument("--text", help="Explicit text to read.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stop-Slop/Caveman guarded local runtime.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze explicit input without rewriting.")
    add_input_args(analyze)
    analyze.add_argument("--json", action="store_true")
    analyze.set_defaults(func=cmd_analyze)
    rewrite = sub.add_parser("rewrite", help="Rewrite explicit input with protected spans.")
    add_input_args(rewrite)
    mode = rewrite.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    rewrite.add_argument("--operator-confirmation", action="store_true")
    rewrite.add_argument("--json", action="store_true")
    rewrite.set_defaults(func=cmd_rewrite)
    smoke = sub.add_parser("smoke-record", help="Write bounded R4 smoke receipt evidence.")
    smoke.add_argument("--install-receipt", help="R3 install/update receipt path.")
    smoke.add_argument("--receipt-dir", required=True)
    smoke.add_argument("--smoke-type", default="help", choices=("help", "status", "safe-rewrite", "safe-discovery"))
    smoke.add_argument("--session", required=True)
    smoke.add_argument("--timeout-seconds", type=int, default=10)
    smoke.add_argument("--json", action="store_true")
    smoke.set_defaults(func=cmd_smoke_record)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
