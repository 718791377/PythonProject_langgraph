#!/usr/bin/env python3
"""Validate QMD dry-run manifests before any real vector ingestion.

This validator is intentionally read-only. It checks the JSONL manifest
created by tools/qmd_vector_ingest_dry_run.py and writes an optional summary
to a project-development runtime path, not to tender deliverable folders.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"
DEFAULT_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "local_vector_db"
    / "qmd_chunks.jsonl"
)

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_FIELDS = (
    "id",
    "status",
    "sourceQmdFile",
    "sourcePath",
    "sectionId",
    "canonicalPointer",
    "contentHash",
    "charCount",
    "content",
)


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(item, dict):
                errors.append(f"line {line_number}: record is not an object")
                continue
            item["_lineNumber"] = line_number
            rows.append(item)
    return rows, errors


def as_text(value: Any) -> str:
    return str(value or "")


def expected_chunk_id(row: dict[str, Any]) -> str:
    identity_basis = "\n".join(
        [
            as_text(row.get("sourcePath")).strip(),
            as_text(row.get("sectionId")).strip(),
            as_text(row.get("canonicalPointer")).strip(),
            as_text(row.get("content")).strip(),
        ]
    )
    return stable_hash(identity_basis)


def validate_row(row: dict[str, Any], min_chars: int) -> list[str]:
    line = row.get("_lineNumber", "?")
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in row:
            errors.append(f"line {line}: missing required field {field}")

    status = as_text(row.get("status")).strip() or "accepted"
    content = as_text(row.get("content")).strip()
    char_count = row.get("charCount")
    content_hash = as_text(row.get("contentHash")).strip()
    chunk_id = as_text(row.get("id")).strip()

    if status not in {"accepted", "skipped"}:
        errors.append(f"line {line}: unsupported status {status!r}")

    if not isinstance(char_count, int):
        errors.append(f"line {line}: charCount must be an integer")
    elif char_count != len(content):
        errors.append(f"line {line}: charCount {char_count} does not match content length {len(content)}")

    if not HEX64_RE.match(content_hash):
        errors.append(f"line {line}: contentHash is not a lowercase sha256 hex digest")
    elif content_hash != stable_hash(content):
        errors.append(f"line {line}: contentHash does not match content")

    if not HEX64_RE.match(chunk_id):
        errors.append(f"line {line}: id is not a lowercase sha256 hex digest")
    elif chunk_id != expected_chunk_id(row):
        errors.append(f"line {line}: id does not match deterministic identity basis")

    if status == "accepted":
        if not content:
            errors.append(f"line {line}: accepted chunk has empty content")
        if isinstance(char_count, int) and char_count < min_chars:
            errors.append(f"line {line}: accepted chunk is shorter than min_chars={min_chars}")
    else:
        if not as_text(row.get("skipReason")).strip():
            errors.append(f"line {line}: skipped chunk must include skipReason")

    for list_field in ("roleTags", "keywords"):
        value = row.get(list_field)
        if value is not None and not isinstance(value, list):
            errors.append(f"line {line}: {list_field} must be a list when present")

    if row.get("conversionChain") is not None and not isinstance(row.get("conversionChain"), list):
        errors.append(f"line {line}: conversionChain must be a list when present")
    for list_field in ("exactSearchTerms", "exactSearchHits", "transcriptSegments"):
        if row.get(list_field) is not None and not isinstance(row.get(list_field), list):
            errors.append(f"line {line}: {list_field} must be a list when present")
    for object_field in ("ocrStatus", "speechToTextStatus", "sourceInventoryRecord"):
        if row.get(object_field) is not None and not isinstance(row.get(object_field), dict):
            errors.append(f"line {line}: {object_field} must be an object when present")

    if row.get("usableForFacts") is not None and not isinstance(row.get("usableForFacts"), bool):
        errors.append(f"line {line}: usableForFacts must be a boolean when present")

    for bool_field in ("manualReviewPromoted",):
        value = row.get(bool_field)
        if value is not None and not isinstance(value, bool):
            errors.append(f"line {line}: {bool_field} must be a boolean when present")

    for int_field in ("pageNumber", "slideNumber"):
        value = row.get(int_field)
        if value is not None and not isinstance(value, int):
            errors.append(f"line {line}: {int_field} must be an integer when present")
    for number_field in ("timestampStart", "timestampEnd", "confidence"):
        value = row.get(number_field)
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"line {line}: {number_field} must be a number when present")

    if isinstance(row.get("pageImages"), list):
        errors.append(f"line {line}: pageImages must stay in evidence records, not text vector manifest content")

    for path_field in (
        "qualityEvidencePath",
        "qualityReportPath",
        "renderEvidencePath",
        "contactSheetPath",
        "fontReportPath",
    ):
        value = row.get(path_field)
        if value is not None and not isinstance(value, str):
            errors.append(f"line {line}: {path_field} must be a string when present")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH), help="QMD dry-run JSONL manifest.")
    parser.add_argument("--out", help="Optional JSON output path.")
    parser.add_argument("--min-chars", type=int, help="Override minimum accepted content length.")
    args = parser.parse_args(argv)

    config = load_json(Path(args.config))
    qmd_cfg = config.get("qmd", {}) if isinstance(config, dict) else {}
    min_chars = int(args.min_chars if args.min_chars is not None else qmd_cfg.get("minContentChars", 20))

    project_mirror = config.get("projectLocalMirror", {}) if isinstance(config, dict) else {}
    configured_manifest = str(project_mirror.get("chunksManifestPath", "")).strip()
    manifest_arg = str(args.manifest)
    if configured_manifest and manifest_arg == str(DEFAULT_MANIFEST_PATH):
        manifest_arg = configured_manifest
    manifest_path = Path(manifest_arg)
    rows, errors = load_jsonl(manifest_path)

    accepted_dedupe_keys: set[str] = set()
    duplicate_accepted_keys: list[str] = []
    accepted_rows = 0
    skipped_rows = 0
    for row in rows:
        errors.extend(validate_row(row, min_chars))
        status = as_text(row.get("status")).strip() or "accepted"
        if status == "accepted":
            accepted_rows += 1
            dedupe_key = "::".join(
                [
                    as_text(row.get("sourcePath")).strip(),
                    as_text(row.get("sectionId")).strip(),
                    as_text(row.get("contentHash")).strip(),
                ]
            )
            if dedupe_key in accepted_dedupe_keys:
                duplicate_accepted_keys.append(dedupe_key)
            else:
                accepted_dedupe_keys.add(dedupe_key)
        elif status == "skipped":
            skipped_rows += 1

    if duplicate_accepted_keys:
        errors.append(f"duplicate accepted dedupe keys: {len(duplicate_accepted_keys)}")

    report = {
        "ok": not errors,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "manifestPath": str(manifest_path),
        "minContentChars": min_chars,
        "rowCount": len(rows),
        "acceptedRows": accepted_rows,
        "skippedRows": skipped_rows,
        "duplicateAcceptedKeys": len(duplicate_accepted_keys),
        "errorCount": len(errors),
        "errors": errors[:200],
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
