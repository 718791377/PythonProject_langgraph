#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


CHECK_NAME = "context_retention_canary_surface"


def from_codepoints(*codepoints: int) -> str:
    return "".join(chr(codepoint) for codepoint in codepoints)


START_CANARY = from_codepoints(25351, 25381, 23448)
END_CANARY = from_codepoints(21941) + "~"
LEGACY_START_CANARY = "CODEX_CTX_" + "CANARY_START"
LEGACY_END_CANARY = "CODEX_CTX_" + "CANARY_END"
LEGACY_ENCODINGS_FOR_MOJIBAKE = ("gbk", "gb18030", "cp936", "latin-1")

ENGLISH_STARTUP_SUMMARY_PATH = Path("docs_bilingual/project_startup_summary.md")
CHINESE_STARTUP_SUMMARY_PATH = Path("docs_bilingual/project_startup_summary.zh-CN.md")
START_CANARY_CODEPOINT_DESCRIPTION = "U+6307 U+6325 U+5B98"
END_CANARY_CODEPOINT_DESCRIPTION = "U+55B5"
END_CANARY_TILDE_DESCRIPTION = "U+007E"

ALLOWED_CANARY_PROMPT_PATHS = {
    ENGLISH_STARTUP_SUMMARY_PATH,
    CHINESE_STARTUP_SUMMARY_PATH,
}

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".worktrees",
    ".omx",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".ps1",
    ".psm1",
    ".cmd",
    ".bat",
    ".sh",
}

SKIP_FILE_NAMES = {
    "local-gate-report.json",
    "openspec-guard-report.json",
}

AGENTS_PATH = Path("AGENTS.md")

RECOVERY_ANCHORS = (
    "Recovery action:",
    "恢复动作：",
)

CONFIG_OR_LAUNCHER_PATTERNS = (
    ".codex/*.toml",
    ".codex/**/*.toml",
    "config.toml",
    "*launcher*",
    "*payload*",
    "*.ps1",
    "*.psm1",
    "*.cmd",
    "*.bat",
    "*.sh",
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


def normalize_relative_path(path: Path) -> Path:
    return Path(*path.parts)


def is_archived_openspec_path(relative_path: Path) -> bool:
    parts = relative_path.parts
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ("openspec", "changes", "archive"):
            return True
    return False


def load_root_gitignore_patterns(root: Path) -> list[str]:
    gitignore_path = root / ".gitignore"
    text = read_text(gitignore_path)
    if text is None:
        return []
    patterns: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        patterns.append(line.replace("\\", "/"))
    return patterns


def matches_root_gitignore(relative_path: Path, patterns: list[str]) -> bool:
    path_text = relative_path.as_posix()
    path_parts = relative_path.parts
    for pattern in patterns:
        directory_only = pattern.endswith("/")
        normalized = pattern.strip("/") if pattern.startswith("/") else pattern.rstrip("/")
        if not normalized:
            continue
        if directory_only:
            if path_text == normalized or path_text.startswith(normalized + "/"):
                return True
            if not pattern.startswith("/") and normalized in path_parts:
                return True
            continue
        if pattern.startswith("/"):
            if fnmatch.fnmatchcase(path_text, normalized):
                return True
            continue
        if fnmatch.fnmatchcase(path_text, normalized) or fnmatch.fnmatchcase(relative_path.name, normalized):
            return True
    return False


def iter_candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    root_gitignore_patterns = load_root_gitignore_patterns(root)
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIR_NAMES
        ]
        current_path = Path(current_root)
        for filename in filenames:
            if filename in SKIP_FILE_NAMES:
                continue
            path = current_path / filename
            try:
                relative_path = normalize_relative_path(path.relative_to(root))
            except ValueError:
                continue
            if is_archived_openspec_path(relative_path):
                continue
            if matches_root_gitignore(relative_path, root_gitignore_patterns):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            files.append(path)
    return files


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def find_line_numbers(text: str, needle: str) -> list[int]:
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), start=1)
        if needle in line
    ]


def find_non_ascii_line_numbers(text: str) -> list[int]:
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), start=1)
        if any(ord(character) > 127 for character in line)
    ]


def english_canary_codepoint_description_complete(text: str) -> bool:
    return (
        START_CANARY_CODEPOINT_DESCRIPTION in text
        and END_CANARY_CODEPOINT_DESCRIPTION in text
        and END_CANARY_TILDE_DESCRIPTION in text
    )


def find_mojibake_canary_lines(text: str) -> list[dict]:
    findings: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        matched_markers = [
            marker
            for marker in MOJIBAKE_CANARY_MARKERS
            if marker and marker in line
        ]
        if matched_markers:
            findings.append(
                {
                    "line": line_number,
                    "markers": sorted(set(matched_markers)),
                }
            )
    return findings


def classify_surface(relative_path: Path) -> str:
    path_text = relative_path.as_posix()
    if relative_path == AGENTS_PATH:
        return "agents_instruction_surface"
    if any(fnmatch.fnmatchcase(path_text, pattern) for pattern in CONFIG_OR_LAUNCHER_PATTERNS):
        return "config_or_launcher_surface"
    if relative_path.parts and relative_path.parts[0] == "docs_bilingual":
        return "documentation_surface"
    return "active_text_surface"


def sanitize_mojibake_canary_lines(mojibake_lines: list[dict]) -> list[dict]:
    sanitized: list[dict] = []
    for line in mojibake_lines:
        markers = line.get("markers", [])
        sanitized.append(
            {
                "line": line.get("line"),
                "marker_count": len(markers) if isinstance(markers, list) else 0,
            }
        )
    return sanitized


def read_response_file(path: Path) -> tuple[str | None, str | None]:
    text = read_text(path)
    if text is None:
        return None, f"Missing or unreadable response file: {path}"
    return text, None


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
            for key in ("text", "content", "message"):
                child = item.get(key)
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
        if not isinstance(payload, dict):
            continue
        payload_type = payload.get("type")
        payload_turn_id = event_turn_id(event, payload)
        if turn_id is not None:
            if event_type == "event_msg" and payload_type == "task_started":
                in_selected_turn = payload_turn_id == turn_id
            if not (in_selected_turn or payload_turn_id == turn_id):
                continue
        if event_type not in {"response_item", "event_msg"}:
            continue
        text = extract_payload_message_text(payload)
        if not text:
            if turn_id is not None and event_type == "event_msg" and payload_type == "task_complete" and payload_turn_id == turn_id:
                in_selected_turn = False
            continue
        responses.append(
            {
                "source": "session_assistant",
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


def diagnose_response_text(source: str, text: str, *, path: str | None = None, line: int | None = None) -> dict:
    raw_mojibake_lines = find_mojibake_canary_lines(text)
    mojibake_lines = sanitize_mojibake_canary_lines(raw_mojibake_lines)
    start_present = START_CANARY in text
    end_present = END_CANARY in text
    stripped_text = text.strip()
    start_at_response_start = stripped_text.startswith(START_CANARY)
    end_at_response_end = stripped_text.endswith(END_CANARY)
    legacy_start_present = LEGACY_START_CANARY in text
    legacy_end_present = LEGACY_END_CANARY in text
    if raw_mojibake_lines:
        status = "mojibake_canary"
    elif start_present and end_present and start_at_response_start and end_at_response_end:
        status = "canonical_present"
    elif start_present and end_present:
        status = "mispositioned_canary"
    elif legacy_start_present or legacy_end_present:
        status = "legacy_canary"
    else:
        status = "missing_canary"

    missing_parts = []
    if not start_present:
        missing_parts.append("start_marker")
    if not end_present:
        missing_parts.append("end_marker")
    mispositioned_parts = []
    if start_present and not start_at_response_start:
        mispositioned_parts.append("start_marker_position")
    if end_present and not end_at_response_end:
        mispositioned_parts.append("end_marker_position")

    diagnostic = {
        "source": source,
        "status": status,
        "start_marker_present": start_present,
        "end_marker_present": end_present,
        "start_marker_at_response_start": start_at_response_start,
        "end_marker_at_response_end": end_at_response_end,
        "legacy_start_marker_present": legacy_start_present,
        "legacy_end_marker_present": legacy_end_present,
        "missing_parts": missing_parts,
        "mispositioned_parts": mispositioned_parts,
        "mojibake_canary_lines": mojibake_lines,
        "recovery": (
            "reread AGENTS.md, reread docs_bilingual/project_startup_summary.md and "
            "docs_bilingual/project_startup_summary.zh-CN.md through an explicit UTF-8 path, "
            "follow the cold-start read order, then reread only task-specific files needed to continue"
        ),
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
        text, read_error = read_response_file(path)
        if read_error is not None:
            errors.append(read_error)
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
                    "start_marker_present": False,
                    "end_marker_present": False,
                    "missing_parts": [],
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


def recovery_mentions_agents(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if any(anchor in line for anchor in RECOVERY_ANCHORS):
            window = "\n".join(lines[index : index + 3])
            return "AGENTS.md" in window
    return False


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

    for relative_path in sorted(ALLOWED_CANARY_PROMPT_PATHS):
        path = root / relative_path
        text = read_text(path)
        if text is None:
            errors.append(f"Missing or unreadable startup summary canary source: {relative_path.as_posix()}")
            continue

        if relative_path == ENGLISH_STARTUP_SUMMARY_PATH:
            non_ascii_lines = find_non_ascii_line_numbers(text)
            if non_ascii_lines:
                errors.append(
                    f"{relative_path.as_posix()} must remain ASCII-only and describe the "
                    "startup-summary canary through codepoint indirection."
                )
                findings.append(
                    {
                        "path": relative_path.as_posix(),
                        "non_ascii_lines": non_ascii_lines,
                    }
                )
            literal_start_lines = find_line_numbers(text, START_CANARY)
            literal_end_lines = find_line_numbers(text, END_CANARY)
            if literal_start_lines or literal_end_lines:
                errors.append(
                    f"{relative_path.as_posix()} must not contain literal visible canary marker text; "
                    "the literal marker source is the Chinese startup summary."
                )
                findings.append(
                    {
                        "path": relative_path.as_posix(),
                        "start_marker_lines": literal_start_lines,
                        "end_marker_lines": literal_end_lines,
                    }
                )
            if LEGACY_START_CANARY in text or LEGACY_END_CANARY in text:
                errors.append(
                    f"{relative_path.as_posix()} must not preserve legacy ASCII canary marker tokens; "
                    "describe historical markers indirectly instead."
                )
            if not english_canary_codepoint_description_complete(text):
                errors.append(
                    f"{relative_path.as_posix()} must describe the startup-summary canary markers with "
                    "ASCII Unicode codepoints."
                )
        else:
            missing_parts = []
            if START_CANARY not in text:
                missing_parts.append("start marker")
            if END_CANARY not in text:
                missing_parts.append("end marker")
            if missing_parts:
                errors.append(
                    f"{relative_path.as_posix()} is missing the startup-summary canary "
                    f"{', '.join(missing_parts)}."
                )
        mojibake_lines = find_mojibake_canary_lines(text)
        if mojibake_lines:
            errors.append(
                f"{relative_path.as_posix()} contains mojibake canary marker text; "
                "read and write the startup summary as UTF-8 and do not preserve the corrupted runtime copy."
            )
            findings.append(
                {
                    "path": relative_path.as_posix(),
                    "mojibake_canary_lines": sanitize_mojibake_canary_lines(mojibake_lines),
                }
            )
        if not recovery_mentions_agents(text):
            errors.append(
                f"{relative_path.as_posix()} must state that canary recovery rereads AGENTS.md "
                "as part of cold-start recovery."
            )

    agents_text = read_text(root / AGENTS_PATH)
    if agents_text is None:
        errors.append("Missing or unreadable AGENTS.md recovery authority surface.")
    elif START_CANARY in agents_text or END_CANARY in agents_text:
        errors.append(
            "AGENTS.md must remain a recovery reread target but must not duplicate the literal canary prompt."
        )
    elif LEGACY_START_CANARY in agents_text or LEGACY_END_CANARY in agents_text:
        errors.append(
            "AGENTS.md must point to the startup summary pair instead of preserving legacy canary marker text."
        )
    elif (agents_mojibake_lines := find_mojibake_canary_lines(agents_text)):
        errors.append(
            "AGENTS.md contains mojibake canary marker text; keep AGENTS.md UTF-8-clean and "
            "point to the startup summary pair instead of copying corrupted runtime instructions."
        )
        findings.append(
            {
                "path": AGENTS_PATH.as_posix(),
                "mojibake_canary_lines": sanitize_mojibake_canary_lines(agents_mojibake_lines),
            }
        )

    for path in iter_candidate_files(root):
        relative_path = normalize_relative_path(path.relative_to(root))
        if relative_path in ALLOWED_CANARY_PROMPT_PATHS:
            continue
        text = read_text(path)
        if text is None:
            warnings.append(f"Skipped unreadable text candidate: {relative_path.as_posix()}")
            continue
        start_lines = find_line_numbers(text, START_CANARY)
        end_lines = find_line_numbers(text, END_CANARY)
        legacy_start_lines = find_line_numbers(text, LEGACY_START_CANARY)
        legacy_end_lines = find_line_numbers(text, LEGACY_END_CANARY)
        if start_lines or end_lines:
            finding = {
                "path": relative_path.as_posix(),
                "surface": classify_surface(relative_path),
                "start_marker_lines": start_lines,
                "end_marker_lines": end_lines,
            }
            findings.append(finding)
            errors.append(
                "Context-retention canary prompt text must live only in "
                f"project_startup_summary.*; duplicate marker found in {relative_path.as_posix()}."
            )
        if legacy_start_lines or legacy_end_lines:
            findings.append(
                {
                    "path": relative_path.as_posix(),
                    "surface": classify_surface(relative_path),
                    "legacy_start_marker_lines": legacy_start_lines,
                    "legacy_end_marker_lines": legacy_end_lines,
                }
            )
            errors.append(
                "Legacy context-retention canary marker text must not be preserved in active "
                f"non-startup surfaces; legacy marker found in {relative_path.as_posix()}."
            )
        mojibake_lines = find_mojibake_canary_lines(text)
        if mojibake_lines:
            findings.append(
                {
                    "path": relative_path.as_posix(),
                    "mojibake_canary_lines": sanitize_mojibake_canary_lines(mojibake_lines),
                }
            )
            errors.append(
                "Context-retention canary prompt text must stay UTF-8-clean; "
                f"mojibake marker found in {relative_path.as_posix()}."
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
        status = diagnostic.get("status")
        if status == "missing_canary":
            errors.append(
                "Response/session canary diagnostic reported missing_canary; "
                "treat this as possible context loss and rerun cold-start recovery."
            )
        elif status == "mojibake_canary":
            errors.append(
                "Response/session canary diagnostic reported mojibake_canary; "
                "use the UTF-8 startup summary pair as canonical and rerun cold-start recovery."
            )
        elif status == "legacy_canary":
            errors.append(
                "Response/session canary diagnostic reported legacy_canary; "
                "legacy marker text is stale compatibility input and does not satisfy the startup-summary canary."
            )
        elif status == "mispositioned_canary":
            errors.append(
                "Response/session canary diagnostic reported mispositioned_canary; "
                "the startup-summary-defined start marker must be first visible response text and "
                "the end marker must be last visible response text."
            )

    if not findings and not errors:
        info.append("Context-retention canary prompt is confined to the startup summary pair.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "allowed_paths": sorted(path.as_posix() for path in ALLOWED_CANARY_PROMPT_PATHS),
        "findings": findings,
        "response_diagnostics": response_diagnostics,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
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
        description="Verify that the context-retention canary prompt lives only in startup summaries."
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
