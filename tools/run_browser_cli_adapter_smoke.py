#!/usr/bin/env python3
"""Run bounded R4 Browser/CLI adapter smoke probes.

This repo-local helper is intentionally conservative.  It only runs help /
version style commands against adapters that already have an R3 install/update
receipt.  It does not install adapters, start browsers, connect to CDP, click,
type, navigate, execute JavaScript, read cookies, read raw browser data, mutate
GUI state, or edit user-level Codex configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "browser_cli_adapter_smoke_runner"
CANONICAL_ADAPTERS: dict[str, dict[str, Any]] = {
    "chrome-devtools-mcp": {
        "aliases": {"chrome-devtools-mcp", "chrome-devtools", "Chrome DevTools MCP"},
        "owner_lane": "browser-cli-adapter:chrome-devtools-mcp",
        "display": "chrome-devtools-mcp",
        "source_url": "https://github.com/ChromeDevTools/chrome-devtools-mcp",
        "smoke_args": ["--help"],
        "smoke_type": "help",
    },
    "cdp-bridge-mcp": {
        "aliases": {"cdp-bridge-mcp", "CDP Bridge", "cdp-bridge"},
        "owner_lane": "browser-cli-adapter:cdp-bridge-mcp",
        "display": "cdp-bridge-mcp",
        "source_url": "https://github.com/Unagi-cq/cdp-bridge-mcp",
        "smoke_args": ["--help"],
        "smoke_type": "help",
    },
    "OpenCLI": {
        "aliases": {"OpenCLI", "opencli", "open-cli"},
        "owner_lane": "browser-cli-adapter:opencli",
        "display": "OpenCLI",
        "source_url": "https://github.com/jackwener/OpenCLI",
        "smoke_args": ["--help"],
        "smoke_type": "help",
    },
}
ALIAS_TO_CANONICAL = {
    alias.lower(): canonical
    for canonical, meta in CANONICAL_ADAPTERS.items()
    for alias in set(meta["aliases"]) | {canonical}
}
ALLOWED_REDACTION_STATUS = {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
FORBIDDEN_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")


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


def redaction_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ALLOWED_REDACTION_STATUS
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in ALLOWED_REDACTION_STATUS
    return False


def normalize_adapter(value: str) -> str | None:
    return ALIAS_TO_CANONICAL.get(str(value).strip().lower())


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


def install_receipt_blockers(adapter: str, receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return ["install_receipt_required"]
    blockers: list[str] = []
    receipt_adapter = normalize_adapter(str(receipt.get("tool_name", "")))
    if receipt_adapter != adapter:
        blockers.append("install_receipt_tool_name_mismatch")
    if not isinstance(receipt.get("wrapper_path"), str) or not receipt.get("wrapper_path", "").strip():
        blockers.append("install_receipt_wrapper_path_required")
    elif not Path(str(receipt["wrapper_path"])).exists():
        blockers.append("install_receipt_wrapper_not_resolved")
    for field in ("source_url", "installed_version", "updater_command", "rollback_pointer", "owner_lane"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            blockers.append(f"install_receipt_{field}_required")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("install_receipt_redaction_status_must_pass")
    return sorted(set(blockers))


def transcript_redaction(transcript: str) -> dict[str, str]:
    return {
        "status": "pass",
        "redacted_transcript_hash": stable_hash(transcript),
    }


def base_receipt(adapter: str, *, install_receipt_ref: str, rollback_ref: str, transcript: str) -> dict[str, Any]:
    meta = CANONICAL_ADAPTERS[adapter]
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "tool_name": adapter,
        "owner_lane": meta["owner_lane"],
        "runtime_stage": "R4",
        "install_receipt": install_receipt_ref,
        "smoke_command": f"{meta['display']} {' '.join(meta['smoke_args'])}".strip(),
        "smoke_type": meta["smoke_type"],
        "timeout_release": {"status": "pass", "released": True},
        "rollback_pointer": rollback_ref,
        "command_transcript": transcript,
        "transcript_redaction": transcript_redaction(transcript),
        "redaction_status": "no_secrets",
    }
    for flag in FORBIDDEN_FLAGS:
        receipt[flag] = False
    return receipt


def blocked_receipt(
    adapter: str,
    *,
    blockers: list[str],
    install_receipt_path: Path | None = None,
    rollback_pointer: Any = None,
) -> dict[str, Any]:
    transcript = sanitize_text(f"blocked R4 smoke for {adapter}: {', '.join(sorted(set(blockers)))}")
    receipt = base_receipt(
        adapter,
        install_receipt_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}" if install_receipt_path else "missing",
        rollback_ref=f"rollback-sha256:{stable_hash(rollback_pointer)}" if rollback_pointer else "unavailable",
        transcript=transcript,
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


def passing_receipt(
    adapter: str,
    *,
    install_receipt_path: Path,
    install_receipt: dict[str, Any],
    transcript: str,
) -> dict[str, Any]:
    receipt = base_receipt(
        adapter,
        install_receipt_ref=f"receipt-sha256:{stable_hash(str(install_receipt_path))}",
        rollback_ref=f"rollback-sha256:{stable_hash(install_receipt.get('rollback_pointer'))}",
        transcript=sanitize_text(transcript),
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


def run_single_smoke(adapter: str, install_receipt_path: Path | None, *, timeout_seconds: int) -> dict[str, Any]:
    receipt_data: dict[str, Any] | None = None
    load_blockers: list[str] = []
    if install_receipt_path is None:
        return blocked_receipt(adapter, blockers=["install_receipt_required"])
    receipt_data, load_blockers = load_json(install_receipt_path)
    blockers = list(load_blockers)
    blockers.extend(install_receipt_blockers(adapter, receipt_data))
    if blockers or receipt_data is None:
        return blocked_receipt(
            adapter,
            blockers=blockers,
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer") if isinstance(receipt_data, dict) else None,
        )

    wrapper = Path(str(receipt_data["wrapper_path"]))
    command = [str(wrapper), *CANONICAL_ADAPTERS[adapter]["smoke_args"]]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        transcript = sanitize_text((exc.stdout or "") + "\n" + (exc.stderr or ""))
        blocked = blocked_receipt(
            adapter,
            blockers=["smoke_command_timeout"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )
        blocked["command_transcript"] = transcript or blocked["command_transcript"]
        blocked["transcript_redaction"] = transcript_redaction(blocked["command_transcript"])
        blocked["timeout_release"] = {"status": "pass", "released": True, "timed_out": True}
        return blocked
    except OSError:
        return blocked_receipt(
            adapter,
            blockers=["smoke_command_launch_failed"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )

    transcript = sanitize_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
    if proc.returncode != 0:
        blocked = blocked_receipt(
            adapter,
            blockers=["smoke_command_failed"],
            install_receipt_path=install_receipt_path,
            rollback_pointer=receipt_data.get("rollback_pointer"),
        )
        blocked["command_transcript"] = transcript or blocked["command_transcript"]
        blocked["transcript_redaction"] = transcript_redaction(blocked["command_transcript"])
        blocked["smoke_result"] = {"status": "blocked", "returncode": proc.returncode, "blockers": ["smoke_command_failed"]}
        return blocked
    return passing_receipt(adapter, install_receipt_path=install_receipt_path, install_receipt=receipt_data, transcript=transcript)


def write_receipt(receipt_dir: Path, adapter: str, receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    filename = f"r4-browser-cli-adapter-smoke-{adapter.lower().replace(' ', '-')}.json"
    path = receipt_dir / filename
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = str(receipt.get("r4_status", "blocked"))
    return {
        "adapter": adapter,
        "receipt_file": filename,
        "receipt_path_hash": stable_hash(str(path)),
        "r4_status": status,
        "smoke_tested": receipt.get("smoke_tested") is True,
        "blockers": receipt.get("blockers", []),
    }


def parse_install_receipt_mappings(values: list[str]) -> tuple[dict[str, Path], list[str]]:
    mapping: dict[str, Path] = {}
    errors: list[str] = []
    for item in values:
        if "=" not in item:
            errors.append("install_receipt_mapping_must_be_adapter_equals_path")
            continue
        key, value = item.split("=", 1)
        adapter = normalize_adapter(key)
        if adapter is None:
            errors.append(f"unknown_adapter:{sanitize_text(key, limit=80)}")
            continue
        mapping[adapter] = Path(value)
    return mapping, errors


def selected_adapters(values: list[str]) -> tuple[list[str], list[str]]:
    if not values or any(value.lower() == "all" for value in values):
        return list(CANONICAL_ADAPTERS), []
    adapters: list[str] = []
    errors: list[str] = []
    for value in values:
        adapter = normalize_adapter(value)
        if adapter is None:
            errors.append(f"unknown_adapter:{sanitize_text(value, limit=80)}")
        elif adapter not in adapters:
            adapters.append(adapter)
    return adapters, errors


def response(ok: bool, action: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": ok,
        "action": action,
        "mutates_user_level_state": False,
        "installs_adapter": False,
        "starts_browser": False,
        "connects_to_cdp": False,
        "performs_sensitive_browser_action": False,
        "reads_browser_data": False,
        "raw_private_paths_in_output": False,
    }
    payload.update(extra)
    return payload


def command_plan(_args: argparse.Namespace) -> dict[str, Any]:
    adapters = {
        name: {
            "display": meta["display"],
            "source_url": meta["source_url"],
            "smoke_type": meta["smoke_type"],
            "safe_command": f"{meta['display']} {' '.join(meta['smoke_args'])}".strip(),
            "owner_lane": meta["owner_lane"],
        }
        for name, meta in CANONICAL_ADAPTERS.items()
    }
    return response(
        True,
        "plan",
        adapters=adapters,
        safety_boundary="R4 help/version/status/read-only smoke only; no browser/GUI/user-level-state mutation.",
    )


def command_run(args: argparse.Namespace) -> dict[str, Any]:
    adapters, adapter_errors = selected_adapters(args.adapter)
    receipt_mapping, mapping_errors = parse_install_receipt_mappings(args.install_receipt)
    receipt_index: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    if adapter_errors or mapping_errors:
        return response(False, "run", errors=adapter_errors + mapping_errors, receipt_index=[])

    receipt_dir = Path(args.receipt_dir)
    for adapter in adapters:
        receipt = run_single_smoke(adapter, receipt_mapping.get(adapter), timeout_seconds=max(1, int(args.timeout_seconds)))
        receipts.append(receipt)
        receipt_index.append(write_receipt(receipt_dir, adapter, receipt))

    return response(
        True,
        "run",
        receipt_index=receipt_index,
        counts={
            "adapters": len(adapters),
            "smoke_tested": sum(1 for receipt in receipts if receipt.get("smoke_tested") is True),
            "blocked": sum(1 for receipt in receipts if receipt.get("smoke_tested") is not True),
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded R4 Browser/CLI adapter smoke probes.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Describe canonical R4 smoke behavior.")
    plan.add_argument("--json", action="store_true", help="Emit JSON output.")

    run = sub.add_parser("run", help="Write R4 smoke-tested or honest blocked receipts.")
    run.add_argument("--receipt-dir", required=True, help="Directory for repo-local smoke receipts.")
    run.add_argument(
        "--adapter",
        action="append",
        default=[],
        help="Adapter to smoke. Repeat or use all. Defaults to all canonical adapters.",
    )
    run.add_argument(
        "--install-receipt",
        action="append",
        default=[],
        metavar="ADAPTER=PATH",
        help="R3 install/update receipt for a canonical adapter.",
    )
    run.add_argument("--timeout-seconds", type=int, default=10, help="Per-command timeout for safe help/version smoke.")
    run.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        payload = command_plan(args)
    else:
        payload = command_run(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for entry in payload.get("receipt_index", []):
            print(f"{entry['adapter']}: {entry['r4_status']}")
        for error in payload.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
