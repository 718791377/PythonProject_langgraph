#!/usr/bin/env python3
"""Guarded gstack-style Codex delivery-loop runtime helper.

This helper is repo-local and conservative. Dry-run commands are read-only.
The R4 smoke command writes only bounded receipt files into an explicitly
supplied receipt directory. It does not install or clone upstream gstack,
mutate user-level Codex state, launch browsers, enable telemetry, push remotes,
open merge requests, or promote itself to an active candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "gstack_codex_delivery_loop_runtime"
TOOL_NAME = "gstack"
OWNER_LANE = "gstack-codex-delivery-loop"
SOURCE_URL = "https://github.com/garrytan/gstack"
LANDING_URL = "https://gstack.lol/"
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
DELIVERY_LOOP = ("Think", "Plan", "Build", "Review", "Test", "Ship", "Reflect")
DRY_RUN_STAGES = {
    "analyze": "Think",
    "plan-dry-run": "Plan",
    "review-dry-run": "Review",
    "qa-dry-run": "Test",
    "ship-dry-run": "Ship",
}
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")
FORBIDDEN_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "remote_state_mutated",
    "browser_launch_performed",
    "telemetry_enabled",
    "codex_launcher_mutated",
    "local_main_gate_bypassed",
    "active_candidate",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def sanitize_text(value: Any, *, limit: int = 1200) -> str:
    text = "" if value is None else str(value)
    text = SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > limit:
        text = text[: max(0, limit - 14)].rstrip() + "...[truncated]"
    return text


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def run_git(root: Path, args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return proc.returncode, (proc.stdout or proc.stderr or "").strip()


def authority_decision(decision: str, scope: str, reason: str) -> list[dict[str, Any]]:
    return [
        {
            "decision": decision,
            "scope": scope,
            "priority_order": PRIORITY_ORDER,
            "reason": reason,
            "does_not_override": [
                "Comet control",
                "OpenSpec WHAT authority",
                "Superpowers HOW discipline",
                "implementation-plan claim locks",
                "local-main-first gates",
                "remote-publication approval gate",
                "browser/GUI authorization",
                "telemetry opt-in",
            ],
        }
    ]


def mutation_summary() -> dict[str, bool]:
    return {
        "file_write_performed": False,
        "user_level_state_mutated": False,
        "remote_state_mutated": False,
        "wrapper_payload_mutated": False,
    }


def safety_summary() -> dict[str, bool]:
    return {
        "gstack_installed_or_cloned": False,
        "hook_enabled": False,
        "browser_launch_performed": False,
        "telemetry_enabled": False,
        "active_candidate": False,
        "remote_publication_allowed": False,
        "local_main_gate_bypassed": False,
    }


def loop_evidence(root: Path) -> dict[str, Any]:
    text = read_text(root / "docs_bilingual" / "implementation_plans" / "gstack_codex_delivery_loop_runtime_governance_plan.md")
    changes_root = root / "openspec" / "changes"
    active_change_count = len([p for p in changes_root.iterdir() if p.is_dir() and p.name != "archive"]) if changes_root.exists() else 0
    branch_code, branch = run_git(root, ["branch", "--show-current"])
    status_code, status = run_git(root, ["status", "--short"])
    return {
        "plan_present": bool(text),
        "plan_mentions_authority_decision": "authority_decision" in text,
        "active_change_count": active_change_count,
        "branch_hash": stable_hash(branch) if branch_code == 0 else "unavailable",
        "git_status_clean": status_code == 0 and not status,
    }


def dry_run_payload(action: str, root: Path) -> dict[str, Any]:
    stage = DRY_RUN_STAGES[action]
    blockers: list[str] = []
    if action == "qa-dry-run":
        blockers.append("browser_qa_requires_explicit_browser_authorization")
    if action == "ship-dry-run":
        blockers.append("remote_publication_requires_current_explicit_remote_action")
    recommendations = {
        "analyze": [
            "Classify current Codex work into the delivery-loop stage without mutating files.",
            "Read startup, governance, plan, and local evidence before selecting next action.",
        ],
        "plan-dry-run": [
            "Keep Comet/OpenSpec/Superpowers authoritative and use gstack only for sequencing advice.",
            "Confirm claim lock, write set, local gates, and R4 receipt expectations before implementation.",
        ],
        "review-dry-run": [
            "Report reviewer, QA, security, documentation, and release-readiness gaps.",
            "Do not apply fixes or spawn live side effects from this helper.",
        ],
        "qa-dry-run": [
            "Report browser QA eligibility and blockers only.",
            "Do not open Browser, Chrome, GUI apps, or read browser data.",
        ],
        "ship-dry-run": [
            "Check local-main-first readiness and remote-publication gate state.",
            "Do not push, open/update merge requests, merge remote MRs, or sync GitHub.",
        ],
    }[action]
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": True,
        "action": action,
        "root_hash": stable_hash(str(root.resolve())),
        "delivery_loop_stage": stage,
        "delivery_loop": list(DELIVERY_LOOP),
        "source_refs": [SOURCE_URL, LANDING_URL],
        "authority_decision": authority_decision("advisory", action, "gstack is delivery-loop advice below Comet/OpenSpec/Superpowers"),
        "recommendations": recommendations,
        "blockers": blockers,
        "evidence": loop_evidence(root),
        "mutation": mutation_summary(),
        "safety": safety_summary(),
    }


def redaction_pass(value: Any) -> bool:
    allowed = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
    if isinstance(value, str):
        return value.strip().lower() in allowed
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in allowed
    return False


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
    if str(receipt.get("tool_name", "")).strip().lower() != TOOL_NAME:
        blockers.append("install_receipt_tool_name_mismatch")
    wrapper_path = receipt.get("wrapper_path")
    if not isinstance(wrapper_path, str) or not wrapper_path.strip():
        blockers.append("install_receipt_wrapper_path_required")
    elif not Path(wrapper_path).exists():
        blockers.append("install_receipt_wrapper_not_resolved")
    for field in ("source_url", "installed_version", "updater_command", "rollback_pointer", "owner_lane"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"install_receipt_{field}_required")
    if str(receipt.get("owner_lane", "")) != OWNER_LANE:
        blockers.append("install_receipt_owner_lane_must_be_gstack_delivery_loop")
    if SOURCE_URL not in str(receipt.get("source_url", "")):
        blockers.append("install_receipt_source_url_must_be_garrytan_gstack")
    if not (
        isinstance(receipt.get("source_pin"), str)
        and str(receipt.get("source_pin")).strip()
        or isinstance(receipt.get("package_pin"), str)
        and str(receipt.get("package_pin")).strip()
        or isinstance(receipt.get("installed_version"), str)
        and str(receipt.get("installed_version")).strip()
    ):
        blockers.append("install_receipt_pin_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("install_receipt_redaction_status_must_pass")
    return sorted(set(blockers))


def transcript_redaction(transcript: str) -> dict[str, str]:
    return {"status": "pass", "redacted_transcript_hash": stable_hash(transcript)}


def guard_fields(status: str) -> dict[str, Any]:
    return {
        "read_guard": {"status": "pass", "scope": "help/status/dry-run", "read_only": True},
        "write_guard": {"status": "pass", "write_allowed": False, "write_performed": False},
        "remote_publication_gate": {"status": "blocked", "remote_mutation_allowed": False},
        "browser_guard": {"status": "blocked", "browser_launch_performed": False},
        "telemetry_guard": {"status": "blocked", "telemetry_enabled": False},
        "job_state": {"status": status, "job_kind": "r4-read-only-smoke", "write_capable": False},
    }


def base_receipt(*, install_ref: str, rollback_ref: str, transcript: str, status: str, decision: str, reason: str) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "owner_lane": OWNER_LANE,
        "runtime_stage": "R4",
        "install_receipt": install_ref,
        "smoke_command": "gstack --help",
        "smoke_type": "help",
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": rollback_ref,
        "command_transcript": transcript,
        "transcript_redaction": transcript_redaction(transcript),
        "redaction_status": "no_secrets",
        "authority_decision": authority_decision(decision, "r4-smoke", reason),
    }
    receipt.update(guard_fields(status))
    for flag in FORBIDDEN_FLAGS:
        receipt[flag] = False
    return receipt


def blocked_receipt(blockers: list[str], *, install_receipt_path: Path | None = None, rollback_pointer: Any = None) -> dict[str, Any]:
    transcript = sanitize_text(f"blocked R4 smoke for gstack: {', '.join(sorted(set(blockers)))}")
    receipt = base_receipt(
        install_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}" if install_receipt_path else "missing",
        rollback_ref=f"rollback-sha256:{stable_hash(rollback_pointer)}" if rollback_pointer else "unavailable",
        transcript=transcript,
        status="blocked",
        decision="blocked",
        reason="R4 smoke requires an existing install receipt and bounded read-only command evidence",
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


def passing_receipt(*, install_receipt_path: Path, install_receipt: dict[str, Any], transcript: str) -> dict[str, Any]:
    receipt = base_receipt(
        install_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}",
        rollback_ref=f"rollback-sha256:{stable_hash(install_receipt.get('rollback_pointer'))}",
        transcript=sanitize_text(transcript),
        status="smoke-tested",
        decision="allow",
        reason="bounded read-only help smoke with receipt evidence",
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


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    receipt_dir = Path(args.receipt_dir)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    install_path = Path(args.install_receipt) if args.install_receipt else None
    if install_path is None:
        receipt = blocked_receipt(["install_receipt_required"])
    else:
        install, load_blockers = load_json(install_path)
        blockers = list(load_blockers)
        blockers.extend(install_receipt_blockers(install))
        if blockers or install is None:
            receipt = blocked_receipt(
                blockers,
                install_receipt_path=install_path,
                rollback_pointer=install.get("rollback_pointer") if isinstance(install, dict) else None,
            )
        else:
            wrapper = Path(str(install["wrapper_path"]))
            try:
                proc = subprocess.run(
                    [str(wrapper), "--help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=int(args.timeout_seconds),
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                transcript = sanitize_text((exc.stdout or "") + "\n" + (exc.stderr or ""))
                receipt = blocked_receipt(["smoke_command_timeout"], install_receipt_path=install_path, rollback_pointer=install.get("rollback_pointer"))
                receipt["command_transcript"] = transcript or receipt["command_transcript"]
                receipt["timeout_release"] = {"status": "pass", "released": True, "timed_out": True}
            except OSError:
                receipt = blocked_receipt(["smoke_command_launch_failed"], install_receipt_path=install_path, rollback_pointer=install.get("rollback_pointer"))
            else:
                transcript = sanitize_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
                if proc.returncode != 0:
                    receipt = blocked_receipt(["smoke_command_failed"], install_receipt_path=install_path, rollback_pointer=install.get("rollback_pointer"))
                    receipt["command_transcript"] = transcript or receipt["command_transcript"]
                    receipt["smoke_result"] = {"status": "blocked", "returncode": proc.returncode, "blockers": ["smoke_command_failed"]}
                else:
                    receipt = passing_receipt(install_receipt_path=install_path, install_receipt=install, transcript=transcript or "gstack help smoke completed")
    out = receipt_dir / "smoke-gstack.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    smoke_tested = receipt.get("smoke_tested") is True
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": True,
        "action": "smoke",
        "root_hash": stable_hash(str(Path(args.root).resolve())),
        "receipt_path_hashes": [stable_hash(str(out))],
        "receipt_summaries": [
            {
                "tool_name": TOOL_NAME,
                "runtime_stage": receipt.get("runtime_stage"),
                "r4_status": receipt.get("r4_status"),
                "smoke_tested": smoke_tested,
                "blocker_count": len(receipt.get("blockers", [])) if isinstance(receipt.get("blockers"), list) else 0,
            }
        ],
        "counts": {"receipts": 1, "smoke_tested": 1 if smoke_tested else 0, "blocked": 0 if smoke_tested else 1},
        "authority_decision": receipt.get("authority_decision", []),
        "mutation": {**mutation_summary(), "file_write_performed": True},
        "safety": safety_summary(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded gstack-style Codex delivery-loop helper.")
    sub = parser.add_subparsers(dest="command", required=True)
    for action in DRY_RUN_STAGES:
        cmd = sub.add_parser(action)
        cmd.add_argument("--root", default=".")
        cmd.add_argument("--json", action="store_true")
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--root", default=".")
    smoke.add_argument("--receipt-dir", required=True)
    smoke.add_argument("--install-receipt", default=None)
    smoke.add_argument("--timeout-seconds", type=int, default=10)
    smoke.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = dry_run_payload(args.command, Path(args.root)) if args.command in DRY_RUN_STAGES else run_smoke(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{payload['check_name']}:{payload['action']}:ok={payload['ok']}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
