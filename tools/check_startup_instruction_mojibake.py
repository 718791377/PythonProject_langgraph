#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


CHECK_NAME = "startup_instruction_mojibake"

LEGACY_ENCODINGS_FOR_MOJIBAKE = ("gbk", "gb18030", "cp936", "latin-1")

START_CANARY = "CODEX_CTX_" + "CANARY_START"
END_CANARY = "CODEX_CTX_" + "CANARY_END"
LEGACY_START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
LEGACY_END_CANARY = chr(21941) + "~"

AUTHORITY_SURFACES = (
    Path("AGENTS.md"),
    Path("docs_bilingual/project_startup_summary.md"),
    Path("docs_bilingual/project_startup_summary.zh-CN.md"),
    Path("docs_bilingual/governance/openspec_official_workflow_policy.md"),
    Path("docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md"),
    Path("docs_bilingual/governance/langgraph_user_level_runtime_policy.md"),
    Path("docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md"),
    Path("docs_bilingual/governance/user_level_launcher_payload_policy.md"),
    Path("docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md"),
    Path("docs_bilingual/governance/codex_user_level_mcp_scope_policy.md"),
    Path("docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md"),
    Path("docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md"),
    Path("docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md"),
    Path("docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md"),
    Path("docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md"),
)

RECOVERY_SOURCES = (
    {
        "path": "docs_bilingual/project_startup_summary.md",
        "encoding": "utf-8-sig",
        "role": "canonical_startup_summary_primary",
    },
    {
        "path": "docs_bilingual/project_startup_summary.zh-CN.md",
        "encoding": "utf-8-sig",
        "role": "canonical_startup_summary_companion",
    },
)

QUESTION_REPLACEMENT_RUN_RE = re.compile(r"\?{3,}")


def from_codepoints(*codepoints: int) -> str:
    return "".join(chr(codepoint) for codepoint in codepoints)


CANONICAL_CHINESE_TOKENS = {
    "canary_start_marker": LEGACY_START_CANARY,
    "canary_end_marker": LEGACY_END_CANARY,
    "mojibake": from_codepoints(20081, 30721),
    "prompt_sentinel": from_codepoints(25552, 31034, 35789, 21736, 20853),
    "startup_instructions": from_codepoints(21551, 21160, 35828, 26126),
    "recovery_action": from_codepoints(24674, 22797, 21160, 20316),
    "automatic_collaboration": from_codepoints(33258, 21160, 21327, 20316),
    "persistent_team": from_codepoints(25345, 20037, 22242, 38431),
    "durable_team": from_codepoints(25345, 20037, 21270, 22242, 38431),
    "read_agents": from_codepoints(35835, 21462, 32, 65, 71, 69, 78, 84, 83),
}


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


def configured_mojibake_variants(token_name: str, token_text: str) -> tuple[str, ...]:
    variants = set(derive_mojibake_variants(token_text))
    if token_name in {"canary_start_marker", "canary_end_marker"}:
        variants.add(token_text)
    return tuple(sorted(variants, key=lambda value: (-len(value), value)))


MOJIBAKE_VARIANTS_BY_TOKEN = {
    token_name: configured_mojibake_variants(token_name, token_text)
    for token_name, token_text in CANONICAL_CHINESE_TOKENS.items()
}


def read_utf8_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8-sig"), None
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decode failed: {exc}"
    except OSError as exc:
        return None, f"read failed: {exc}"


def find_mojibake_lines(text: str) -> list[dict]:
    findings: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        line_findings: list[dict] = []
        if "\ufffd" in line:
            line_findings.append({"kind": "replacement_character", "marker": "\\ufffd"})
        if QUESTION_REPLACEMENT_RUN_RE.search(line):
            line_findings.append({"kind": "question_mark_replacement_run", "marker": "???"})
        for token_name, variants in MOJIBAKE_VARIANTS_BY_TOKEN.items():
            matched_variants = sorted({variant for variant in variants if variant and variant in line})
            if matched_variants:
                line_findings.append(
                    {
                        "kind": "legacy_encoding_mojibake_variant",
                        "token": token_name,
                        "markers": matched_variants,
                    }
                )
        if line_findings:
            findings.append({"line": line_number, "findings": line_findings})
    return findings


def recovery_sources() -> list[dict]:
    return [dict(source) for source in RECOVERY_SOURCES]


def sanitize_mojibake_lines(mojibake_lines: list[dict]) -> list[dict]:
    sanitized_lines: list[dict] = []
    for line in mojibake_lines:
        sanitized_findings: list[dict] = []
        for finding in line.get("findings", []):
            sanitized: dict = {"kind": finding.get("kind")}
            if "token" in finding:
                sanitized["token"] = finding.get("token")
            markers = finding.get("markers")
            if isinstance(markers, list):
                sanitized["marker_count"] = len(markers)
                sanitized["max_marker_length"] = max((len(marker) for marker in markers if isinstance(marker, str)), default=0)
            elif "marker" in finding:
                sanitized["marker_kind"] = finding.get("kind")
            sanitized_findings.append(sanitized)
        sanitized_lines.append({"line": line.get("line"), "findings": sanitized_findings})
    return sanitized_lines


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


def extract_payload_message_text(payload: dict) -> str:
    payload_type = payload.get("type")
    if payload_type == "message" and payload.get("role") == "assistant":
        return flatten_text(payload.get("content", []))
    if payload_type == "agent_message":
        message = payload.get("message")
        return message if isinstance(message, str) else ""
    return ""


def event_turn_id(event: dict, payload: dict) -> str | None:
    for value in (payload.get("turn_id"), event.get("turn_id")):
        if isinstance(value, str) and value:
            return value
    return None


def iter_session_assistant_responses(path: Path, turn_id: str | None = None) -> tuple[list[dict], list[str]]:
    responses: list[dict] = []
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
        if event_type not in {"response_item", "event_msg"} or not isinstance(payload, dict):
            continue
        payload_type = payload.get("type")
        payload_turn_id = event_turn_id(event, payload)
        if turn_id is not None:
            if event_type == "event_msg" and payload_type == "task_started":
                in_selected_turn = payload_turn_id == turn_id
            if not (in_selected_turn or payload_turn_id == turn_id):
                continue
        text = extract_payload_message_text(payload)
        if not text:
            if turn_id is not None and event_type == "event_msg" and payload_type == "task_complete" and payload_turn_id == turn_id:
                in_selected_turn = False
            continue
        responses.append(
            {
                "path": str(path),
                "line": line_number,
                "event_type": event_type,
                "payload_type": payload_type,
                "text": text,
            }
        )
        if turn_id is not None and event_type == "event_msg" and payload_type == "task_complete" and payload_turn_id == turn_id:
            in_selected_turn = False
    return responses, warnings


def filter_canary_mojibake_lines(mojibake_lines: list[dict]) -> list[dict]:
    filtered: list[dict] = []
    for line in mojibake_lines:
        findings = []
        for finding in line.get("findings", []):
            if finding.get("token") in {"canary_start_marker", "canary_end_marker"}:
                markers = finding.get("markers", [])
                findings.append(
                    {
                        "kind": finding.get("kind"),
                        "token": finding.get("token"),
                        "marker_count": len(markers) if isinstance(markers, list) else 0,
                    }
                )
        if findings:
            filtered.append({"line": line.get("line"), "findings": findings})
    return filtered


def diagnose_response_text(source: str, text: str, *, path: str | None = None, line: int | None = None) -> dict:
    mojibake_lines = filter_canary_mojibake_lines(find_mojibake_lines(text))
    if mojibake_lines:
        status = "mojibake_canary"
    elif START_CANARY in text and END_CANARY in text:
        status = "canonical_present"
    else:
        status = "no_mojibake_detected"
    diagnostic = {
        "source": source,
        "status": status,
        "mojibake_canary_lines": mojibake_lines,
        "recovery_action": (
            "reread docs_bilingual/project_startup_summary.md and "
            "docs_bilingual/project_startup_summary.zh-CN.md through an explicit UTF-8 path; "
            "do not preserve terminal mojibake as canonical startup instructions"
        ),
        "recovery_sources": recovery_sources(),
    }
    if path is not None:
        diagnostic["path"] = path
    if line is not None:
        diagnostic["line"] = line
    return diagnostic


def collect_response_diagnostics(
    root: Path,
    *,
    response_texts: list[str],
    response_files: list[str],
    session_jsonl_paths: list[str],
    latest_assistant: bool,
    turn_id: str | None,
) -> tuple[list[dict], list[str], list[str]]:
    diagnostics: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []

    for index, text in enumerate(response_texts, start=1):
        diagnostics.append(diagnose_response_text(f"response_text:{index}", text))

    for raw_path in response_files:
        path = resolve_input_path(root, raw_path)
        text, read_error = read_utf8_text(path)
        if read_error is not None:
            errors.append(f"{path} is missing or not UTF-8 readable: {read_error}")
            continue
        assert text is not None
        diagnostics.append(diagnose_response_text("response_file", text, path=str(path)))

    for raw_path in session_jsonl_paths:
        path = resolve_input_path(root, raw_path)
        responses, session_warnings = iter_session_assistant_responses(path, turn_id=turn_id)
        warnings.extend(session_warnings)
        if not responses:
            diagnostics.append(
                {
                    "source": "session_latest_assistant" if latest_assistant else "session_assistant",
                    "status": "not_applicable_no_assistant_response",
                    "path": str(path),
                    "mojibake_canary_lines": [],
                }
            )
            continue
        selected = [responses[-1]] if latest_assistant else responses
        for response in selected:
            source = "session_latest_assistant" if latest_assistant else "session_assistant"
            diagnostics.append(
                diagnose_response_text(
                    source,
                    response["text"],
                    path=response["path"],
                    line=response["line"],
                )
            )

    return diagnostics, errors, warnings


def run_check(
    root: Path,
    *,
    response_texts: list[str] | None = None,
    response_files: list[str] | None = None,
    session_jsonl_paths: list[str] | None = None,
    latest_assistant: bool = False,
    turn_id: str | None = None,
) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    findings: list[dict] = []
    response_diagnostics: list[dict] = []

    for relative_path in AUTHORITY_SURFACES:
        path = root / relative_path
        text, read_error = read_utf8_text(path)
        if read_error is not None:
            errors.append(f"{relative_path.as_posix()} is missing or not UTF-8 readable: {read_error}")
            findings.append({"path": relative_path.as_posix(), "read_error": read_error})
            continue
        assert text is not None
        mojibake_lines = find_mojibake_lines(text)
        if mojibake_lines:
            errors.append(
                f"{relative_path.as_posix()} contains mojibake or lossy replacement text; "
                "read the configured recovery sources as UTF-8 and repair the launcher/payload boundary before preserving it."
            )
            findings.append(
                {
                    "path": relative_path.as_posix(),
                    "mojibake_lines": sanitize_mojibake_lines(mojibake_lines),
                    "recovery_sources": recovery_sources(),
                }
            )

    response_diagnostics, response_errors, response_warnings = collect_response_diagnostics(
        root,
        response_texts=response_texts or [],
        response_files=response_files or [],
        session_jsonl_paths=session_jsonl_paths or [],
        latest_assistant=latest_assistant,
        turn_id=turn_id,
    )
    errors.extend(response_errors)
    warnings.extend(response_warnings)
    for diagnostic in response_diagnostics:
        if diagnostic.get("status") == "mojibake_canary":
            errors.append(
                "Response/session startup diagnostic reported mojibake_canary; "
                "reread the startup summary pair through an explicit UTF-8 path before continuing."
            )

    if not errors:
        info.append("Startup and instruction authority surfaces are UTF-8-clean.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "authority_surfaces": [path.as_posix() for path in AUTHORITY_SURFACES],
        "recovery_sources": recovery_sources(),
        "findings": findings,
        "response_diagnostics": response_diagnostics,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "surfaces_checked": len(AUTHORITY_SURFACES),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": len(findings),
            "response_diagnostics": len(response_diagnostics),
        },
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Verify startup and instruction authority surfaces do not contain mojibake."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--response-text", action="append", default=[], help="Assistant response text to diagnose.")
    parser.add_argument("--response-file", action="append", default=[], help="UTF-8 file containing assistant response text.")
    parser.add_argument("--session-jsonl", action="append", default=[], help="Codex session JSONL transcript to diagnose.")
    parser.add_argument("--turn-id", help="Optional turn id substring used to filter session JSONL lines.")
    parser.add_argument("--latest-assistant", action="store_true", help="Only diagnose the latest eligible assistant response in each session JSONL.")
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
