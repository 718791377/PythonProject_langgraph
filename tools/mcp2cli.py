#!/usr/bin/env python3
"""Compact, fail-closed MCP facade discovery helper.

This repository-local MVP does not invoke live MCP servers or mutate user-level
Codex configuration. It exposes a compact allowed-profile registry and a guarded
call facade that fails closed for sensitive calls.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SUMMARY_LIMIT = 180
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|?]+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"'<>|?]+(?:\\[^\s\"'<>|?]+)+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?<![\w.-])/(?:Users|home|private|var|tmp|mnt|Volumes|builds)/[^\s\"'<>|?]+")
TOKEN_RE = re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|cookie|password)\s*[:=]\s*([^\s,;\"']+)")
STANDALONE_SECRET_RE = re.compile(r"(?i)\b(?:sk-[a-z0-9_-]{6,}|xox[baprs]-[a-z0-9_-]{6,}|gh[pousr]_[a-z0-9_]{8,})\b")
SENSITIVE_RISK_LEVELS = {"medium", "high", "critical"}
REQUIRED_RECEIPT_FIELDS = ("action", "target", "scope", "expiry", "session", "operator_confirmation")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_registry_path() -> Path:
    return repo_root() / "tools" / "mcp2cli_allowed_profiles.json"


def sanitize_text(value: Any, *, limit: int | None = None) -> str:
    text = str(value)
    # Redact secret values before path redaction so query-string or suffix
    # secrets embedded in a path-like token still leave explicit secret evidence.
    text = TOKEN_RE.sub(lambda match: match.group(0).split(match.group(1))[0] + "[REDACTED_SECRET]", text)
    text = STANDALONE_SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit is not None and len(text) > limit:
        return text[: max(0, limit - len("...[truncated]"))].rstrip() + "...[truncated]"
    return text


def sanitize_json(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, dict):
        return {sanitize_text(key, limit=120): sanitize_json(child) for key, child in value.items()}
    return value


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("registry_schema_version_invalid")
    profiles = data.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("registry_profiles_missing")
    return data


def compact_tool(tool: dict[str, Any], *, full: bool = False) -> dict[str, Any]:
    call = tool.get("call") if isinstance(tool.get("call"), dict) else {}
    result = {
        "tool_id": sanitize_text(tool.get("tool_id", ""), limit=120),
        "name": sanitize_text(tool.get("name", ""), limit=120),
        "source": sanitize_text(tool.get("source", ""), limit=120),
        "category": sanitize_text(tool.get("category", ""), limit=120),
        "risk_level": sanitize_text(tool.get("risk_level", "unknown"), limit=40),
        "sensitive_categories": [sanitize_text(item, limit=80) for item in tool.get("sensitive_categories", []) if isinstance(item, str)],
        "summary": sanitize_text(tool.get("summary", ""), limit=SUMMARY_LIMIT),
        "available": bool(tool.get("available")),
        "call_enabled": bool(call.get("enabled")),
        "requires_authorization": bool(call.get("requires_authorization")),
        "full_metadata_included": False,
    }
    if full:
        result.update({
            "full_metadata_included": True,
            "schema_summary": sanitize_text(tool.get("schema_summary", ""), limit=400),
            "call": sanitize_json(call),
        })
    return result


def find_profile(registry: dict[str, Any], profile_id: str) -> dict[str, Any] | None:
    for profile in registry.get("profiles", []):
        if isinstance(profile, dict) and profile.get("profile_id") == profile_id:
            return profile
    return None


def find_tool(profile: dict[str, Any], tool_id: str) -> dict[str, Any] | None:
    for tool in profile.get("tools", []):
        if isinstance(tool, dict) and tool.get("tool_id") == tool_id:
            return tool
    return None


def envelope(command: str, payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "safety": {
            "compact_output": True,
            "raw_paths_retained": False,
            "full_schema_included_by_default": False,
            "invokes_live_mcp_servers": False,
            "mutates_config": False,
            "edits_user_codex_config": False,
        },
    }
    base.update(payload)
    return base


def profile_payload(profile: dict[str, Any], *, full: bool = False) -> dict[str, Any]:
    tools = [compact_tool(tool, full=full) for tool in profile.get("tools", []) if isinstance(tool, dict)]
    return {
        "profile_id": sanitize_text(profile.get("profile_id", ""), limit=120),
        "status": sanitize_text(profile.get("status", ""), limit=80),
        "summary": sanitize_text(profile.get("summary", ""), limit=SUMMARY_LIMIT),
        "tools": tools,
        "tool_count": len(tools),
    }


def command_list(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    profile = find_profile(registry, args.profile)
    if profile is None:
        emit(envelope("list", {"ok": False, "error": "profile_not_found", "profile": sanitize_text(args.profile, limit=120)}), args.json)
        return 2
    emit(envelope("list", {"ok": True, "profile": profile_payload(profile)}), args.json)
    return 0


def score_tool(tool: dict[str, Any], terms: list[str]) -> int:
    haystack = " ".join(str(tool.get(key, "")) for key in ("tool_id", "name", "source", "category", "summary")).lower()
    return sum(1 for term in terms if term in haystack)


def command_search(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    profile = find_profile(registry, args.profile)
    if profile is None:
        emit(envelope("search", {"ok": False, "error": "profile_not_found", "profile": sanitize_text(args.profile, limit=120)}), args.json)
        return 2
    terms = [term.lower() for term in re.split(r"\s+", args.query.strip()) if term]
    results = []
    for tool in profile.get("tools", []):
        if not isinstance(tool, dict):
            continue
        score = score_tool(tool, terms)
        if score:
            item = compact_tool(tool)
            item["score"] = score
            results.append(item)
    results.sort(key=lambda item: (-int(item["score"]), str(item["tool_id"])))
    emit(envelope("search", {"ok": True, "profile": sanitize_text(args.profile, limit=120), "query": sanitize_text(args.query, limit=120), "total_matches": len(results), "results": results[: args.limit]}), args.json)
    return 0


def command_show(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    profile = find_profile(registry, args.profile)
    if profile is None:
        emit(envelope("show", {"ok": False, "error": "profile_not_found", "profile": sanitize_text(args.profile, limit=120)}), args.json)
        return 2
    tool = find_tool(profile, args.tool)
    if tool is None:
        emit(envelope("show", {"ok": False, "error": "tool_not_found", "tool_id": sanitize_text(args.tool, limit=120)}), args.json)
        return 2
    emit(envelope("show", {"ok": True, "profile": sanitize_text(args.profile, limit=120), "tool": compact_tool(tool, full=args.full)}), args.json)
    return 0


def parse_args_json(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"args_json_invalid:{exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("args_json_must_be_object")
    return value


def validate_receipt(path: Path, *, tool_id: str) -> tuple[bool, list[str], dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return False, ["authorization_receipt_missing"], {}
    except json.JSONDecodeError:
        return False, ["authorization_receipt_invalid_json"], {}
    except OSError:
        return False, ["authorization_receipt_unreadable"], {}
    if not isinstance(data, dict):
        return False, ["authorization_receipt_not_object"], {}
    blockers: list[str] = []
    for field in REQUIRED_RECEIPT_FIELDS:
        if field not in data:
            blockers.append(f"authorization_receipt_missing_{field}")
    if data.get("operator_confirmation") is not True:
        blockers.append("authorization_receipt_operator_confirmation_not_true")
    target = data.get("target")
    if isinstance(target, str) and target not in {tool_id, "*"}:
        blockers.append("authorization_receipt_target_mismatch")
    if not isinstance(data.get("action"), str) or "call" not in data.get("action", "").lower():
        blockers.append("authorization_receipt_action_not_call")
    expiry = data.get("expiry")
    if isinstance(expiry, str):
        try:
            parsed = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            if parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc):
                blockers.append("authorization_receipt_expired")
        except ValueError:
            blockers.append("authorization_receipt_expiry_invalid")
    elif "expiry" in data:
        blockers.append("authorization_receipt_expiry_invalid")
    sanitized = {key: sanitize_json(value) for key, value in data.items() if key in REQUIRED_RECEIPT_FIELDS}
    return not blockers, blockers, sanitized


def call_requires_receipt(tool: dict[str, Any]) -> bool:
    call = tool.get("call") if isinstance(tool.get("call"), dict) else {}
    risk = str(tool.get("risk_level", "unknown")).lower()
    sensitive = tool.get("sensitive_categories") if isinstance(tool.get("sensitive_categories"), list) else []
    return bool(call.get("requires_authorization")) or risk in SENSITIVE_RISK_LEVELS or bool(sensitive)


def command_call(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    profile = find_profile(registry, args.profile)
    if profile is None:
        emit(envelope("call", {"ok": False, "blocked": True, "error": "profile_not_found", "call_performed": False}), args.json)
        return 2
    tool = find_tool(profile, args.tool)
    if tool is None:
        emit(envelope("call", {"ok": False, "blocked": True, "error": "tool_not_found", "call_performed": False}), args.json)
        return 2
    try:
        call_args = parse_args_json(args.args)
    except ValueError as exc:
        emit(envelope("call", {"ok": False, "blocked": True, "error": str(exc), "call_performed": False}), args.json)
        return 2
    requires_receipt = call_requires_receipt(tool)
    receipt_ok = False
    receipt_blockers: list[str] = []
    receipt_summary: dict[str, Any] = {}
    if requires_receipt:
        if not args.authorization_receipt:
            emit(envelope("call", {
                "ok": False,
                "blocked": True,
                "reason": "authorization_receipt_required",
                "tool": compact_tool(tool),
                "receipt_required": True,
                "receipt_valid": False,
                "receipt_blockers": ["authorization_receipt_missing"],
                "call_performed": False,
                "external_mcp_invoked": False,
            }), args.json)
            return 3
        receipt_ok, receipt_blockers, receipt_summary = validate_receipt(Path(args.authorization_receipt), tool_id=args.tool)
        if not receipt_ok:
            emit(envelope("call", {
                "ok": False,
                "blocked": True,
                "reason": "authorization_receipt_invalid",
                "tool": compact_tool(tool),
                "receipt_required": True,
                "receipt_valid": False,
                "receipt_blockers": receipt_blockers,
                "receipt_summary": receipt_summary,
                "call_performed": False,
                "external_mcp_invoked": False,
            }), args.json)
            return 3
    call = tool.get("call") if isinstance(tool.get("call"), dict) else {}
    call_enabled = bool(call.get("enabled"))
    result = {
        "ok": True,
        "blocked": False,
        "tool": compact_tool(tool),
        "receipt_required": requires_receipt,
        "receipt_valid": receipt_ok if requires_receipt else None,
        "receipt_summary": receipt_summary if receipt_ok else {},
        "call_performed": call_enabled,
        "external_mcp_invoked": False,
        "facade_mode": sanitize_text(call.get("mode", "local_facade"), limit=120),
        "args_summary": sanitize_json(call_args),
        "result": {
            "result_kind": sanitize_text(call.get("result_kind", "deterministic_summary"), limit=120),
            "message": "repo-local mcp2cli MVP returned a deterministic guarded facade result; no live MCP server was invoked.",
        },
    }
    if not call_enabled:
        result.update({"ok": False, "blocked": True, "reason": sanitize_text(call.get("mode", "call_disabled"), limit=120), "call_performed": False})
        return_code = 3
    else:
        return_code = 0
    emit(envelope("call", result), args.json)
    return return_code


def emit(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            sys.stdout.buffer.write(data.encode("utf-8"))
        except AttributeError:  # pragma: no cover
            sys.stdout.write(data)
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def add_common(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--profile", default="core-readonly", help="Allowed MCP facade profile id.")
    sub.add_argument("--registry", default=str(default_registry_path()), help="Allowed profile registry JSON path.")
    sub.add_argument("--json", action="store_true", help="Emit JSON output.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compact fail-closed MCP facade helper.")
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(dest="command")

    list_cmd = subparsers.add_parser("list", help="List tools in an allowed MCP profile.")
    add_common(list_cmd)
    list_cmd.set_defaults(func=command_list)

    search = subparsers.add_parser("search", help="Search tools in an allowed MCP profile.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    add_common(search)
    search.set_defaults(func=command_search)

    show = subparsers.add_parser("show", help="Show compact MCP tool metadata.")
    show.add_argument("tool")
    show.add_argument("--full", action="store_true", help="Explicitly include sanitized full registry metadata.")
    add_common(show)
    show.set_defaults(func=command_show)

    call = subparsers.add_parser("call", help="Run the guarded repo-local call facade.")
    call.add_argument("tool")
    call.add_argument("--args", default="{}", help="JSON object arguments for the facade call.")
    call.add_argument("--authorization-receipt", default=None, help="Path to a one-task authorization receipt JSON file.")
    add_common(call)
    call.set_defaults(func=command_call)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.func is None:
        parser.print_help()
        return 2
    try:
        return int(args.func(args))
    except ValueError as exc:
        emit(envelope("error", {"ok": False, "blocked": True, "error": sanitize_text(str(exc), limit=200)}), True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
