#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "session_replay_context_filtering"

START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
END_CANARY = chr(21941) + "~"
LEGACY_START_CANARY = "CODEX_CTX_" + "CANARY_START"
LEGACY_END_CANARY = "CODEX_CTX_" + "CANARY_END"
LEGACY_ENCODINGS_FOR_MOJIBAKE = ("gbk", "gb18030", "cp936", "latin-1")

POLICY_PATHS = (
    Path("docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"),
    Path("docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md"),
)
SCRIPT_PATH = Path("tools/session_replay_context_filtering.py")
CI_MANIFEST_PATH = Path("tools/ci/ci_test_manifest.json")
TEST_MANIFEST_ENTRY = "check_session_replay_context_filtering.test.py"

INPUT_CONTRACT = {
    "inputs": [
        "assistant-visible response text",
        "Codex session JSONL response_item/event_msg transcript entries",
        "tool/function-call output carried by replay transcripts",
        "raw startup-summary copies pasted into resumed legacy sessions",
        "legacy runtime or MCP workaround assumptions from old /resume threads",
    ],
    "authority_inputs": [
        "AGENTS.md",
        "docs_bilingual/project_startup_summary.md",
        "docs_bilingual/project_startup_summary.zh-CN.md",
        "current repository governance documents",
    ],
}

OUTPUT_CONTRACT = {
    "fields": [
        "accepted_context_items",
        "filtered_context_items",
        "blocked_authority_items",
        "replay_diagnostics",
    ],
    "blocked_reasons": [
        "canonical_canary",
        "legacy_canary",
        "mojibake_canary",
        "raw_startup_summary_copy",
        "stale_mcp_global_disable",
        "stale_runtime_authority",
    ],
    "filter_reasons": [
        "tool_or_function_output",
        "non_assistant_payload",
    ],
}

REQUIRED_POLICY_TERMS = {
    "english": (
        "Session replay context filtering",
        "Replay inputs",
        "Filtered outputs",
        "assistant-visible",
        "tool/function output",
        "stale canary text",
        "mojibake",
        "stale MCP assumptions",
        "AGENTS.md",
        "UTF-8 startup summary pair",
        "per-invocation override",
        'mcp_servers.omx_code_intel.enabled=false',
        "must not become current authority",
    ),
    "zh": (
        "Session replay context filtering",
        "Replay inputs",
        "Filtered outputs",
        "AGENTS.md",
        "UTF-8 startup summary pair",
        "mcp_servers.omx_code_intel.enabled=false",
    ),
}

RAW_STARTUP_PATTERNS = (
    re.compile(r"(?is)#\s*Project Startup Summary.*?Cold-Start Read Order"),
    re.compile(r"(?is)doc_id:\s*project_startup_summary.*?Cold-Start Read Order"),
)

STALE_MCP_GLOBAL_DISABLE_PATTERNS = (
    re.compile(
        r"(?is)(permanent(?:ly)?|global(?:ly)?|edit|mutate|write|modify|change).{0,120}"
        r"(?:config\.toml|user-level config|C:\\Users\\lenovo\\\.codex\\config\.toml).{0,160}"
        r"(?:disable|remove|turn off).{0,120}mcp_servers\.omx_"
    ),
    re.compile(
        r"(?is)(?:disable|remove|turn off).{0,120}mcp_servers\.omx_.{0,160}"
        r"(?:permanent(?:ly)?|global(?:ly)?|config\.toml|user-level config)"
    ),
)

STALE_RUNTIME_AUTHORITY_PATTERNS = (
    re.compile(r"(?is)(?:old|legacy|stale).{0,80}(?:thread|session|resume).{0,120}(?:current authority|authoritative)"),
    re.compile(r"(?is)(?:use|treat).{0,80}(?:pasted|raw|old).{0,80}(?:startup summary|transcript).{0,80}(?:authority|authoritative)"),
)


def derive_mojibake_variants(text: str) -> tuple[str, ...]:
    variants: set[str] = set()
    raw = text.encode("utf-8")
    for encoding in LEGACY_ENCODINGS_FOR_MOJIBAKE:
        for errors in ("ignore", "replace"):
            try:
                decoded = raw.decode(encoding, errors=errors)
            except LookupError:
                continue
            if decoded and decoded != text:
                variants.add(decoded)
    return tuple(sorted(variants, key=lambda value: (-len(value), value)))


MOJIBAKE_CANARY_MARKERS = tuple(
    sorted(
        {
            marker_or_variant
            for marker in (START_CANARY, END_CANARY)
            for marker_or_variant in derive_mojibake_variants(marker)
            if marker_or_variant != marker
        }
    )
)


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def resolve_input_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    return path


def flatten_text(value: object) -> str:
    parts: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            for child in item.values():
                if isinstance(child, (str, list, dict)):
                    visit(child)

    visit(value)
    return "\n".join(parts)


def event_turn_id(event: dict, payload: dict) -> str | None:
    for value in (payload.get("turn_id"), event.get("turn_id")):
        if isinstance(value, str) and value:
            return value
    return None


def extract_session_items(path: Path, turn_id: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    items: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        return [], [f"Session JSONL is not UTF-8 readable: {path}: {exc}"]
    except OSError as exc:
        return [], [f"Session JSONL cannot be read: {path}: {exc}"]

    in_selected_turn = turn_id is None
    for line_number, line in enumerate(lines, start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f"Skipped invalid JSONL line {line_number} in {path}")
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        payload_type = payload.get("type")
        payload_turn_id = event_turn_id(event, payload)
        if turn_id is not None:
            if event_type == "event_msg" and payload_type == "task_started":
                in_selected_turn = payload_turn_id == turn_id
            if not (in_selected_turn or payload_turn_id == turn_id):
                continue
        text = ""
        role = payload.get("role")
        item_kind = "non_assistant_payload"
        if payload_type == "message" and role == "assistant":
            text = flatten_text(payload.get("content", []))
            item_kind = "assistant_visible"
        elif payload_type == "agent_message":
            message = payload.get("message")
            text = message if isinstance(message, str) else ""
            item_kind = "assistant_visible"
        elif payload_type in {"function_call_output", "tool_call_output"}:
            text = flatten_text(payload.get("output", ""))
            item_kind = "tool_or_function_output"
        elif payload_type in {"function_call", "tool_call"}:
            text = flatten_text(payload)
            item_kind = "tool_or_function_call"
        if text:
            items.append(
                {
                    "source": "session_jsonl",
                    "path": str(path),
                    "line": line_number,
                    "event_type": event_type,
                    "payload_type": payload_type,
                    "kind": item_kind,
                    "text": text,
                }
            )
        if turn_id is not None and event_type == "event_msg" and payload_type == "task_complete" and payload_turn_id == turn_id:
            in_selected_turn = False
    return items, warnings


def contains_mojibake_canary(text: str) -> bool:
    return any(marker and marker in text for marker in MOJIBAKE_CANARY_MARKERS)


def detect_block_reasons(text: str) -> list[str]:
    reasons: list[str] = []
    if START_CANARY in text or END_CANARY in text:
        reasons.append("canonical_canary")
    if LEGACY_START_CANARY in text or LEGACY_END_CANARY in text:
        reasons.append("legacy_canary")
    if contains_mojibake_canary(text):
        reasons.append("mojibake_canary")
    if any(pattern.search(text) for pattern in RAW_STARTUP_PATTERNS):
        reasons.append("raw_startup_summary_copy")
    if any(pattern.search(text) for pattern in STALE_MCP_GLOBAL_DISABLE_PATTERNS):
        reasons.append("stale_mcp_global_disable")
    if any(pattern.search(text) for pattern in STALE_RUNTIME_AUTHORITY_PATTERNS):
        reasons.append("stale_runtime_authority")
    return reasons


def sanitize_reasons(reasons: list[str]) -> list[str]:
    return sorted(set(reasons))


def summarize_text(text: str) -> dict[str, Any]:
    return {
        "chars": len(text),
        "lines": len(text.splitlines()) or (1 if text else 0),
        "sha256_prefix": __import__("hashlib").sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16],
    }


def sanitize_item(item: dict[str, Any], *, reasons: list[str] | None = None) -> dict[str, Any]:
    sanitized = {
        "source": item.get("source"),
        "kind": item.get("kind"),
        "path": item.get("path"),
        "line": item.get("line"),
        "payload_type": item.get("payload_type"),
        "text_summary": summarize_text(str(item.get("text", ""))),
    }
    if reasons is not None:
        sanitized["reasons"] = sanitize_reasons(reasons)
    return {key: value for key, value in sanitized.items() if value is not None}


def collect_input_items(
    root: Path,
    *,
    response_texts: list[str],
    response_files: list[str],
    session_jsonl_paths: list[str],
    latest_assistant: bool,
    turn_id: str | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    items: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    for index, text in enumerate(response_texts, start=1):
        items.append({"source": f"response_text:{index}", "kind": "assistant_visible", "text": text})

    for raw_path in response_files:
        path = resolve_input_path(root, raw_path)
        text = read_text(path)
        if text is None:
            errors.append(f"Missing or unreadable response file: {path}")
            continue
        items.append({"source": "response_file", "kind": "assistant_visible", "path": str(path), "text": text})

    for raw_path in session_jsonl_paths:
        path = resolve_input_path(root, raw_path)
        session_items, session_warnings = extract_session_items(path, turn_id=turn_id)
        warnings.extend(session_warnings)
        if latest_assistant:
            assistants = [item for item in session_items if item.get("kind") == "assistant_visible"]
            tool_items = [item for item in session_items if item.get("kind") != "assistant_visible"]
            selected_items = tool_items + (assistants[-1:] if assistants else [])
        else:
            selected_items = session_items
        if not selected_items:
            warnings.append(f"No replay context items found in session JSONL: {path}")
        items.extend(selected_items)

    return items, errors, warnings


def load_json(path: Path) -> Any:
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def check_default_surfaces(root: Path) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    warnings: list[str] = []
    diagnostics: list[dict[str, Any]] = []

    for index, relative_path in enumerate(POLICY_PATHS):
        path = root / relative_path
        text = read_text(path)
        if text is None:
            errors.append(f"Missing or unreadable session replay filtering policy surface: {relative_path.as_posix()}")
            continue
        key = "english" if index == 0 else "zh"
        missing = [term for term in REQUIRED_POLICY_TERMS[key] if term not in text]
        diagnostics.append({"path": relative_path.as_posix(), "missing_terms": missing})
        if missing:
            errors.append(
                f"{relative_path.as_posix()} is missing session replay filtering contract terms: "
                + ", ".join(missing)
            )

    script_path = root / SCRIPT_PATH
    diagnostics.append(
        {
            "path": SCRIPT_PATH.as_posix(),
            "exists": script_path.exists(),
            "surface_role": "runtime helper and standalone replay-filtering checker",
        }
    )
    if not script_path.exists():
        errors.append(f"Missing session replay filtering helper: {SCRIPT_PATH.as_posix()}")

    manifest = load_json(root / CI_MANIFEST_PATH)
    if not isinstance(manifest, dict):
        errors.append(f"Missing or invalid CI test manifest: {CI_MANIFEST_PATH.as_posix()}")
    else:
        python_unittest = manifest.get("python_unittest", [])
        diagnostics.append(
            {
                "path": CI_MANIFEST_PATH.as_posix(),
                "required_entry": TEST_MANIFEST_ENTRY,
                "registered": TEST_MANIFEST_ENTRY in python_unittest if isinstance(python_unittest, list) else False,
            }
        )
        if not isinstance(python_unittest, list):
            errors.append(f"{CI_MANIFEST_PATH.as_posix()} must contain a python_unittest list.")
        elif TEST_MANIFEST_ENTRY not in python_unittest:
            errors.append(
                f"{CI_MANIFEST_PATH.as_posix()} must register {TEST_MANIFEST_ENTRY} in python_unittest."
            )

    return errors, warnings, diagnostics


def run_check(
    root: Path,
    *,
    response_texts: list[str] | None = None,
    response_files: list[str] | None = None,
    session_jsonl_paths: list[str] | None = None,
    latest_assistant: bool = False,
    turn_id: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    errors, warnings, surface_diagnostics = check_default_surfaces(root)

    items, item_errors, item_warnings = collect_input_items(
        root,
        response_texts=response_texts or [],
        response_files=response_files or [],
        session_jsonl_paths=session_jsonl_paths or [],
        latest_assistant=latest_assistant,
        turn_id=turn_id,
    )
    errors.extend(item_errors)
    warnings.extend(item_warnings)

    accepted_context_items: list[dict[str, Any]] = []
    filtered_context_items: list[dict[str, Any]] = []
    blocked_authority_items: list[dict[str, Any]] = []
    replay_diagnostics: list[dict[str, Any]] = []

    for item in items:
        text = str(item.get("text", ""))
        kind = item.get("kind")
        if kind != "assistant_visible":
            filtered_context_items.append(sanitize_item(item, reasons=[str(kind or "non_assistant_payload")]))
            replay_diagnostics.append(
                {
                    "source": item.get("source"),
                    "kind": kind,
                    "status": "filtered_non_authority_context",
                    "text_summary": summarize_text(text),
                }
            )
            continue

        reasons = detect_block_reasons(text)
        if reasons:
            blocked_authority_items.append(sanitize_item(item, reasons=reasons))
            replay_diagnostics.append(
                {
                    "source": item.get("source"),
                    "kind": kind,
                    "status": "blocked_authority_candidate",
                    "reasons": sanitize_reasons(reasons),
                    "text_summary": summarize_text(text),
                }
            )
            continue

        accepted_context_items.append(sanitize_item(item))
        replay_diagnostics.append(
            {
                "source": item.get("source"),
                "kind": kind,
                "status": "accepted_assistant_visible_context",
                "text_summary": summarize_text(text),
            }
        )

    if blocked_authority_items:
        reason_set = sorted({reason for item in blocked_authority_items for reason in item.get("reasons", [])})
        errors.append(
            "Session replay context contains stale or unsafe authority candidates: " + ", ".join(reason_set)
        )

    info: list[str] = []
    if not errors:
        info.append("Session replay context filtering contract and replay diagnostics are clean.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "input_contract": INPUT_CONTRACT,
        "output_contract": OUTPUT_CONTRACT,
        "surface_diagnostics": surface_diagnostics,
        "accepted_context_items": accepted_context_items,
        "filtered_context_items": filtered_context_items,
        "blocked_authority_items": blocked_authority_items,
        "replay_diagnostics": replay_diagnostics,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "accepted_context_items": len(accepted_context_items),
            "filtered_context_items": len(filtered_context_items),
            "blocked_authority_items": len(blocked_authority_items),
            "replay_diagnostics": len(replay_diagnostics),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Filter resumed session replay context before treating it as current prompt authority."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--response-text", action="append", default=[], help="Assistant-visible response text to diagnose.")
    parser.add_argument("--response-file", action="append", default=[], help="UTF-8 file containing assistant-visible response text.")
    parser.add_argument("--session-jsonl", action="append", default=[], help="Codex session JSONL transcript to diagnose.")
    parser.add_argument("--turn-id", help="Optional turn id used to filter session JSONL lines.")
    parser.add_argument("--latest-assistant", action="store_true", help="Only keep the latest assistant-visible item from each session JSONL.")
    args = parser.parse_args()

    payload = run_check(
        Path(args.root),
        response_texts=args.response_text,
        response_files=args.response_file,
        session_jsonl_paths=args.session_jsonl,
        latest_assistant=args.latest_assistant,
        turn_id=args.turn_id,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
