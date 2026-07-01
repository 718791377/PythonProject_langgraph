#!/usr/bin/env python3
"""Sync the project-local SQLite + JSONL mirror into project-local LanceDB.

This tool is intentionally repository-local. It writes only under the
``projectLocalMirror.vector.dbPath`` configured in ``config/local-vector-db.json``
and refuses to write into ``<configured-external-source-root>``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))


def as_text(value: Any) -> str:
    return str(value or "").strip()


def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def normalize_table_name(value: str) -> str:
    table = as_text(value) or "authority_chunks"
    if table.endswith(".lance"):
        table = table[: -len(".lance")]
    return table


def refuse_openclaw_write(path: Path, openclaw_root: Path) -> None:
    if is_relative_to(path, openclaw_root):
        raise ValueError(f"refusing to write LanceDB data under OpenClaw: {path}")


def optional_column(existing: set[str], name: str, table_alias: str = "c") -> str:
    return f"{table_alias}.{name}" if name in existing else f"NULL AS {name}"


def load_records(sqlite_db_path: Path) -> list[dict[str, Any]]:
    with sqlite3.connect(sqlite_db_path) as conn:
        conn.row_factory = sqlite3.Row
        indexed_columns = {row[1] for row in conn.execute("PRAGMA table_info(indexed_chunks)").fetchall()}
        rows = conn.execute(
            f"""
            SELECT c.chunk_id, c.source_path, c.section_id, c.canonical_pointer,
                   c.heading, c.role_tags_json, c.keywords_json, c.content_hash,
                   {optional_column(indexed_columns, "source_sha256")},
                   {optional_column(indexed_columns, "extraction_method")},
                   {optional_column(indexed_columns, "authority_status")},
                   {optional_column(indexed_columns, "usable_for_facts")},
                   {optional_column(indexed_columns, "manual_review_promoted")},
                   {optional_column(indexed_columns, "quality_evidence_path")},
                   {optional_column(indexed_columns, "quality_report_path")},
                   {optional_column(indexed_columns, "render_evidence_path")},
                   {optional_column(indexed_columns, "contact_sheet_path")},
                   {optional_column(indexed_columns, "font_report_path")},
                   {optional_column(indexed_columns, "conversion_chain_json")},
                   {optional_column(indexed_columns, "evidence_purpose")},
                   {optional_column(indexed_columns, "fact_boundary_note")},
                   {optional_column(indexed_columns, "source_inventory_path")},
                   {optional_column(indexed_columns, "inventory_record_type")},
                   {optional_column(indexed_columns, "inventory_status")},
                   {optional_column(indexed_columns, "extraction_status")},
                   {optional_column(indexed_columns, "format_family")},
                   {optional_column(indexed_columns, "modality")},
                   {optional_column(indexed_columns, "extractor_id")},
                   {optional_column(indexed_columns, "extractor_name")},
                   {optional_column(indexed_columns, "extractor_version")},
                   {optional_column(indexed_columns, "container_path")},
                   {optional_column(indexed_columns, "container_depth")},
                   {optional_column(indexed_columns, "archive_recursion_status")},
                   {optional_column(indexed_columns, "ocr_status_json")},
                   {optional_column(indexed_columns, "speech_to_text_status_json")},
                   {optional_column(indexed_columns, "transcript_segments_json")},
                   {optional_column(indexed_columns, "timestamp_start")},
                   {optional_column(indexed_columns, "timestamp_end")},
                   {optional_column(indexed_columns, "confidence")},
                   {optional_column(indexed_columns, "exact_search_terms_json")},
                   {optional_column(indexed_columns, "exact_search_hits_json")},
                   {optional_column(indexed_columns, "coverage_notice")},
                   {optional_column(indexed_columns, "source_inventory_record_json")},
                   {optional_column(indexed_columns, "page_number")},
                   {optional_column(indexed_columns, "slide_number")},
                   {optional_column(indexed_columns, "sheet_name")},
                   {optional_column(indexed_columns, "cell_range")},
                   c.char_count, v.embedding_model, v.embedding_dimensions,
                   v.vector_json, t.content, t.content_snippet
            FROM indexed_chunks c
            JOIN embedding_vectors v ON v.chunk_id = c.chunk_id
            LEFT JOIN chunk_texts t ON t.chunk_id = c.chunk_id
            ORDER BY c.source_path, c.section_id, c.chunk_id
            """
        ).fetchall()
    records: list[dict[str, Any]] = []
    for row in rows:
        vector = [float(value) for value in json.loads(row["vector_json"])]
        records.append(
            {
                "id": row["chunk_id"],
                "vector": vector,
                "content": row["content"] or "",
                "contentSnippet": row["content_snippet"] or "",
                "sourcePath": row["source_path"] or "",
                "sectionId": row["section_id"] or "",
                "canonicalPointer": row["canonical_pointer"] or "",
                "heading": row["heading"] or "",
                "roleTagsJson": row["role_tags_json"] or "[]",
                "keywordsJson": row["keywords_json"] or "[]",
                "sourceSha256": row["source_sha256"] or "",
                "extractionMethod": row["extraction_method"] or "",
                "authorityStatus": row["authority_status"] or "",
                "usableForFacts": bool(row["usable_for_facts"]),
                "manualReviewPromoted": bool(row["manual_review_promoted"]),
                "qualityEvidencePath": row["quality_evidence_path"] or "",
                "qualityReportPath": row["quality_report_path"] or "",
                "renderEvidencePath": row["render_evidence_path"] or "",
                "contactSheetPath": row["contact_sheet_path"] or "",
                "fontReportPath": row["font_report_path"] or "",
                "conversionChainJson": row["conversion_chain_json"] or "[]",
                "evidencePurpose": row["evidence_purpose"] or "",
                "factBoundaryNote": row["fact_boundary_note"] or "",
                "sourceInventoryPath": row["source_inventory_path"] or "",
                "inventoryRecordType": row["inventory_record_type"] or "",
                "inventoryStatus": row["inventory_status"] or "",
                "extractionStatus": row["extraction_status"] or "",
                "formatFamily": row["format_family"] or "",
                "modality": row["modality"] or "",
                "extractorId": row["extractor_id"] or "",
                "extractorName": row["extractor_name"] or "",
                "extractorVersion": row["extractor_version"] or "",
                "containerPath": row["container_path"] or "",
                "containerDepth": int(row["container_depth"]) if row["container_depth"] is not None else None,
                "archiveRecursionStatus": row["archive_recursion_status"] or "",
                "ocrStatusJson": row["ocr_status_json"] or "{}",
                "speechToTextStatusJson": row["speech_to_text_status_json"] or "{}",
                "transcriptSegmentsJson": row["transcript_segments_json"] or "[]",
                "timestampStart": float(row["timestamp_start"]) if row["timestamp_start"] is not None else None,
                "timestampEnd": float(row["timestamp_end"]) if row["timestamp_end"] is not None else None,
                "confidence": float(row["confidence"]) if row["confidence"] is not None else None,
                "exactSearchTermsJson": row["exact_search_terms_json"] or "[]",
                "exactSearchHitsJson": row["exact_search_hits_json"] or "[]",
                "coverageNotice": row["coverage_notice"] or "",
                "sourceInventoryRecordJson": row["source_inventory_record_json"] or "{}",
                "pageNumber": int(row["page_number"]) if row["page_number"] is not None else None,
                "slideNumber": int(row["slide_number"]) if row["slide_number"] is not None else None,
                "sheetName": row["sheet_name"] or "",
                "cellRange": row["cell_range"] or "",
                "contentHash": row["content_hash"] or "",
                "charCount": int(row["char_count"] or 0),
                "embeddingModel": row["embedding_model"] or "",
                "embeddingDimensions": int(row["embedding_dimensions"] or 0),
                "indexedAt": stamp(),
            }
        )
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--sqlite-db", help="SQLite mirror path. Defaults to projectLocalMirror.metadata.dbPath.")
    parser.add_argument("--lancedb-path", help="Project-local LanceDB directory.")
    parser.add_argument("--table", help="LanceDB table name. A trailing .lance suffix is ignored.")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")
    openclaw_root = Path(as_text(config.get("openclawRoot") or r"<configured-external-source-root>"))
    mirror = config.get("projectLocalMirror", {})
    if not isinstance(mirror, dict):
        raise ValueError("config.projectLocalMirror must be an object")
    metadata = mirror.get("metadata", {})
    vector = mirror.get("vector", {})
    if not isinstance(metadata, dict) or not isinstance(vector, dict):
        raise ValueError("config.projectLocalMirror.metadata/vector must be objects")

    sqlite_db_path = Path(args.sqlite_db or as_text(metadata.get("dbPath")))
    lancedb_path = Path(args.lancedb_path or as_text(vector.get("dbPath")))
    table_name = normalize_table_name(args.table or as_text(vector.get("targetTable")))
    table_path = lancedb_path / f"{table_name}.lance"
    report_path = Path(args.report) if args.report else None

    refuse_openclaw_write(lancedb_path, openclaw_root)
    refuse_openclaw_write(table_path, openclaw_root)
    records = load_records(sqlite_db_path)
    if not records:
        raise ValueError(f"no records found in SQLite mirror: {sqlite_db_path}")

    import lancedb  # imported lazily so --help works before dependency installation

    lancedb_path.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(lancedb_path))
    table = db.create_table(table_name, data=records, mode="overwrite")
    row_count = table.count_rows()

    report = {
        "ok": True,
        "mode": "project_local_lancedb_sync",
        "syncedAt": stamp(),
        "configPath": str(config_path),
        "sqliteDbPath": str(sqlite_db_path),
        "lancedbPath": str(lancedb_path),
        "tableName": table_name,
        "tablePath": str(table_path),
        "rowsRead": len(records),
        "rowsWritten": row_count,
        "embeddingDimensions": records[0].get("embeddingDimensions"),
        "writesOpenClaw": False,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    print(output)
    return 0 if row_count == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
