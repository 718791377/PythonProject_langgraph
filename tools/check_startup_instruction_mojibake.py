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

START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
END_CANARY = chr(21941) + "~"

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

QUESTION_REPLACEMENT_RUN_RE = re.compile(r"\?{3,}")


def from_codepoints(*codepoints: int) -> str:
    return "".join(chr(codepoint) for codepoint in codepoints)


CANONICAL_CHINESE_TOKENS = {
    "canary_start_marker": START_CANARY,
    "canary_end_marker": END_CANARY,
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


MOJIBAKE_VARIANTS_BY_TOKEN = {
    token_name: derive_mojibake_variants(token_text)
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


def run_check(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    findings: list[dict] = []

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
                "read the source as UTF-8 and repair the launcher/payload boundary before preserving it."
            )
            findings.append({"path": relative_path.as_posix(), "mojibake_lines": mojibake_lines})

    if not errors:
        info.append("Startup and instruction authority surfaces are UTF-8-clean.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "authority_surfaces": [path.as_posix() for path in AUTHORITY_SURFACES],
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "surfaces_checked": len(AUTHORITY_SURFACES),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": len(findings),
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
    args = parser.parse_args()

    payload = run_check(Path(args.root))
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
