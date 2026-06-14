#!/usr/bin/env python3
"""Build a project-local SQLite + JSONL vector mirror from QMD chunks.

This script writes only inside <consumer-project-root> development-asset paths by default:

- <consumer-project-root>\\data\\local_vector_db\\vector-meta.sqlite
- <consumer-project-root>\\data\\local_vector_db\\embeddings.jsonl
- <consumer-project-root>\\.project-runtime\\local-vector-db\\reports\\mirror_ingest.json

It does not write to <configured-external-source-root>.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any
from urllib import error, request


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"
INDEXED_CHUNK_EVIDENCE_COLUMNS: dict[str, str] = {
    "source_sha256": "TEXT",
    "extraction_method": "TEXT",
    "authority_status": "TEXT",
    "usable_for_facts": "INTEGER NOT NULL DEFAULT 0",
    "manual_review_promoted": "INTEGER NOT NULL DEFAULT 0",
    "quality_evidence_path": "TEXT",
    "quality_report_path": "TEXT",
    "render_evidence_path": "TEXT",
    "contact_sheet_path": "TEXT",
    "font_report_path": "TEXT",
    "conversion_chain_json": "TEXT NOT NULL DEFAULT '[]'",
    "evidence_purpose": "TEXT",
    "fact_boundary_note": "TEXT",
    "source_inventory_path": "TEXT",
    "inventory_record_type": "TEXT",
    "inventory_status": "TEXT",
    "extraction_status": "TEXT",
    "format_family": "TEXT",
    "modality": "TEXT",
    "extractor_id": "TEXT",
    "extractor_name": "TEXT",
    "extractor_version": "TEXT",
    "container_path": "TEXT",
    "container_depth": "INTEGER",
    "archive_recursion_status": "TEXT",
    "ocr_status_json": "TEXT NOT NULL DEFAULT '{}'",
    "speech_to_text_status_json": "TEXT NOT NULL DEFAULT '{}'",
    "transcript_segments_json": "TEXT NOT NULL DEFAULT '[]'",
    "timestamp_start": "REAL",
    "timestamp_end": "REAL",
    "confidence": "REAL",
    "exact_search_terms_json": "TEXT NOT NULL DEFAULT '[]'",
    "exact_search_hits_json": "TEXT NOT NULL DEFAULT '[]'",
    "coverage_notice": "TEXT",
    "source_inventory_record_json": "TEXT NOT NULL DEFAULT '{}'",
    "page_number": "INTEGER",
    "slide_number": "INTEGER",
    "sheet_name": "TEXT",
    "cell_range": "TEXT",
}


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            item = json.loads(stripped)
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number}: JSONL record is not an object")
            rows.append(item)
    return rows


def as_text(value: Any) -> str:
    return str(value or "").strip()


def utcish_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    payload = None
    request_headers = dict(headers or {})
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    req = request.Request(url, method=method, headers=request_headers, data=payload)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except (error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"HTTP request failed for {url}: {exc}") from exc
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"HTTP JSON response was not an object for {url}")
    return data


def embed_text(base_url: str, api_key: str, model: str, text: str, timeout: float) -> list[float]:
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    data = http_json(
        f"{base_url.rstrip('/')}/embeddings",
        method="POST",
        headers=headers,
        body={"model": model, "input": text},
        timeout=timeout,
    )
    rows = data.get("data")
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        raise RuntimeError("embedding response missing data[0]")
    embedding = rows[0].get("embedding")
    if not isinstance(embedding, list):
        raise RuntimeError("embedding response missing vector")
    return [float(value) for value in embedding]


def apply_schema(db_path: Path, schema_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = schema_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
        conn.commit()


def init_extra_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS embedding_vectors (
          chunk_id TEXT PRIMARY KEY,
          embedding_model TEXT NOT NULL,
          embedding_dimensions INTEGER NOT NULL,
          vector_json TEXT NOT NULL,
          vector_norm REAL NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY (chunk_id) REFERENCES indexed_chunks(chunk_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS source_inventory_records (
          inventory_row_id TEXT PRIMARY KEY,
          job_id TEXT NOT NULL,
          source_path TEXT NOT NULL,
          source_absolute_path TEXT,
          source_sha256 TEXT,
          source_root TEXT,
          relative_path TEXT,
          extension TEXT,
          mime_type TEXT,
          format_family TEXT,
          modality TEXT,
          extractor_id TEXT,
          extraction_status TEXT NOT NULL,
          container_path TEXT,
          archive_recursion_status TEXT,
          ocr_status_json TEXT NOT NULL DEFAULT '{}',
          speech_to_text_status_json TEXT NOT NULL DEFAULT '{}',
          transcript_segments_json TEXT NOT NULL DEFAULT '[]',
          exact_search_terms_json TEXT NOT NULL DEFAULT '[]',
          exact_search_hits_json TEXT NOT NULL DEFAULT '[]',
          inventory_record_json TEXT NOT NULL,
          indexed_at TEXT NOT NULL,
          FOREIGN KEY (job_id) REFERENCES ingestion_jobs(job_id)
        )
        """
    )


def ensure_indexed_chunk_evidence_columns(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(indexed_chunks)").fetchall()}
    for name, definition in INDEXED_CHUNK_EVIDENCE_COLUMNS.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE indexed_chunks ADD COLUMN {name} {definition}")


def snippet(text: str, limit: int = 360) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(limit - 1, 0)].rstrip() + "…"


def vector_norm(vector: list[float]) -> float:
    return sum(value * value for value in vector) ** 0.5


def as_bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


def optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def json_array_text(value: Any) -> str:
    return json.dumps(value if isinstance(value, list) else [], ensure_ascii=False, sort_keys=True)


def json_object_text(value: Any) -> str:
    return json.dumps(value if isinstance(value, dict) else {}, ensure_ascii=False, sort_keys=True)


def optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def inventory_row_id(row: dict[str, Any]) -> str:
    return stable_hash(
        "|".join(
            [
                as_text(row.get("sourcePath")),
                as_text(row.get("containerPath")),
                as_text(row.get("sourceSha256")),
                as_text(row.get("extractionStatus")),
            ]
        )
    )


def load_source_inventory_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not str(path).strip() or not path.exists():
        return []
    return load_jsonl(path)


def insert_source_inventory(conn: sqlite3.Connection, job_id: str, rows: list[dict[str, Any]]) -> int:
    conn.execute("DELETE FROM source_inventory_records WHERE job_id = ?", (job_id,))
    inserted = 0
    for row in rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO source_inventory_records (
              inventory_row_id, job_id, source_path, source_absolute_path, source_sha256,
              source_root, relative_path, extension, mime_type, format_family, modality,
              extractor_id, extraction_status, container_path, archive_recursion_status,
              ocr_status_json, speech_to_text_status_json, transcript_segments_json,
              exact_search_terms_json, exact_search_hits_json, inventory_record_json, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inventory_row_id(row),
                job_id,
                as_text(row.get("sourcePath")),
                as_text(row.get("sourceAbsolutePath")),
                as_text(row.get("sourceSha256")),
                as_text(row.get("sourceRoot")),
                as_text(row.get("relativePath")),
                as_text(row.get("extension")),
                as_text(row.get("mimeType")),
                as_text(row.get("formatFamily")),
                as_text(row.get("modality")),
                as_text(row.get("extractorId")),
                as_text(row.get("extractionStatus")),
                as_text(row.get("containerPath")),
                as_text(row.get("archiveRecursionStatus")),
                json_object_text(row.get("ocrStatus")),
                json_object_text(row.get("speechToTextStatus")),
                json_array_text(row.get("transcriptSegments")),
                json_array_text(row.get("exactSearchTerms")),
                json_array_text(row.get("exactSearchHits")),
                json.dumps(row, ensure_ascii=False, sort_keys=True),
                utcish_now(),
            ),
        )
        inserted += 1
    return inserted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--manifest", help="QMD chunks JSONL. Defaults to projectLocalMirror.chunksManifestPath.")
    parser.add_argument("--source-inventory", help="Optional source inventory JSONL to mirror into SQLite coverage metadata.")
    parser.add_argument("--db", help="SQLite output path. Defaults to projectLocalMirror.metadata.dbPath.")
    parser.add_argument("--embeddings", help="Embeddings JSONL output path.")
    parser.add_argument("--report", help="Optional JSON report output path.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Embedding HTTP timeout in seconds.")
    parser.add_argument("--limit", type=int, help="Optional chunk limit for testing.")
    args = parser.parse_args(argv)

    config = load_json(Path(args.config))
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")
    mirror = config.get("projectLocalMirror", {})
    if not isinstance(mirror, dict):
        raise ValueError("config.projectLocalMirror must be an object")
    mirror_meta = mirror.get("metadata", {})
    if not isinstance(mirror_meta, dict):
        raise ValueError("config.projectLocalMirror.metadata must be an object")

    embedding_cfg = config.get("embedding", {})
    if not isinstance(embedding_cfg, dict):
        raise ValueError("config.embedding must be an object")
    base_url = as_text(embedding_cfg.get("baseURL"))
    api_key = as_text(embedding_cfg.get("apiKey"))
    model = as_text(embedding_cfg.get("model"))
    expected_dimensions = int(embedding_cfg.get("dimensions"))

    manifest_path = Path(args.manifest or as_text(mirror.get("chunksManifestPath")))
    source_inventory_path_text = args.source_inventory or as_text(mirror.get("sourceInventoryPath"))
    source_inventory_path = Path(source_inventory_path_text) if source_inventory_path_text else None
    db_path = Path(args.db or as_text(mirror_meta.get("dbPath")))
    schema_path = Path(as_text(mirror_meta.get("schemaPath")))
    embeddings_path = Path(
        args.embeddings
        or str(Path(as_text(mirror.get("dataRoot"))) / "embeddings.jsonl")
    )
    report_path = Path(args.report) if args.report else None

    chunks = [chunk for chunk in load_jsonl(manifest_path) if as_text(chunk.get("status")) in {"", "accepted"}]
    source_inventory_rows = load_source_inventory_rows(source_inventory_path)
    if args.limit is not None:
        chunks = chunks[: max(args.limit, 0)]

    apply_schema(db_path, schema_path)
    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    job_id = stable_hash(f"{manifest_path}|{len(chunks)}|{model}|{expected_dimensions}")[:32]
    now = utcish_now()

    with sqlite3.connect(db_path) as conn, embeddings_path.open("w", encoding="utf-8") as out:
        init_extra_tables(conn)
        ensure_indexed_chunk_evidence_columns(conn)
        conn.execute("DELETE FROM embedding_vectors")
        conn.execute("DELETE FROM chunk_texts")
        conn.execute("DELETE FROM indexed_chunks")
        conn.execute("DELETE FROM ingestion_jobs WHERE job_id = ?", (job_id,))
        conn.execute(
            """
            INSERT INTO ingestion_jobs (
              job_id, source_root, qmd_manifest_path, vector_store_path, vector_table,
              embedding_model, embedding_dimensions, status, started_at, accepted_chunks,
              skipped_chunks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                as_text(mirror.get("sourcePolicy")),
                str(manifest_path),
                as_text(mirror.get("dataRoot")),
                "sqlite_jsonl_embedding_vectors",
                model,
                expected_dimensions,
                "running",
                now,
                0,
                0,
            ),
        )

        inventory_written = insert_source_inventory(conn, job_id, source_inventory_rows)
        written = 0
        for chunk in chunks:
            content = as_text(chunk.get("content"))
            vector = embed_text(base_url, api_key, model, content, args.timeout)
            if len(vector) != expected_dimensions:
                raise RuntimeError(
                    f"embedding dimension mismatch for {chunk.get('id')}: "
                    f"expected {expected_dimensions}, got {len(vector)}"
                )
            chunk_id = as_text(chunk.get("id"))
            indexed_at = utcish_now()
            conn.execute(
                """
                INSERT OR REPLACE INTO indexed_chunks (
                  chunk_id, job_id, source_path, section_id, canonical_pointer, heading,
                  role_tags_json, keywords_json, source_sha256, extraction_method, authority_status,
                  usable_for_facts, manual_review_promoted, quality_evidence_path, quality_report_path,
                  render_evidence_path, contact_sheet_path, font_report_path, conversion_chain_json,
                  evidence_purpose, fact_boundary_note, source_inventory_path, inventory_record_type,
                  inventory_status, extraction_status, format_family, modality, extractor_id, extractor_name,
                  extractor_version, container_path, container_depth, archive_recursion_status, ocr_status_json,
                  speech_to_text_status_json, transcript_segments_json, timestamp_start, timestamp_end, confidence,
                  exact_search_terms_json, exact_search_hits_json, coverage_notice, source_inventory_record_json,
                  page_number, slide_number, sheet_name, cell_range,
                  content_hash, char_count, vector_table, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    job_id,
                    as_text(chunk.get("sourcePath")),
                    as_text(chunk.get("sectionId")),
                    as_text(chunk.get("canonicalPointer")),
                    as_text(chunk.get("heading")),
                    json.dumps(chunk.get("roleTags") if isinstance(chunk.get("roleTags"), list) else [], ensure_ascii=False),
                    json.dumps(chunk.get("keywords") if isinstance(chunk.get("keywords"), list) else [], ensure_ascii=False),
                    as_text(chunk.get("sourceSha256")),
                    as_text(chunk.get("extractionMethod")),
                    as_text(chunk.get("authorityStatus")),
                    as_bool_int(chunk.get("usableForFacts")),
                    as_bool_int(chunk.get("manualReviewPromoted")),
                    as_text(chunk.get("qualityEvidencePath")),
                    as_text(chunk.get("qualityReportPath")),
                    as_text(chunk.get("renderEvidencePath")),
                    as_text(chunk.get("contactSheetPath")),
                    as_text(chunk.get("fontReportPath")),
                    json_array_text(chunk.get("conversionChain")),
                    as_text(chunk.get("evidencePurpose")),
                    as_text(chunk.get("factBoundaryNote")),
                    as_text(chunk.get("sourceInventoryPath")),
                    as_text(chunk.get("inventoryRecordType")),
                    as_text(chunk.get("inventoryStatus")),
                    as_text(chunk.get("extractionStatus")),
                    as_text(chunk.get("formatFamily")),
                    as_text(chunk.get("modality")),
                    as_text(chunk.get("extractorId")),
                    as_text(chunk.get("extractorName")),
                    as_text(chunk.get("extractorVersion")),
                    as_text(chunk.get("containerPath")),
                    optional_int(chunk.get("containerDepth")),
                    as_text(chunk.get("archiveRecursionStatus")),
                    json_object_text(chunk.get("ocrStatus")),
                    json_object_text(chunk.get("speechToTextStatus")),
                    json_array_text(chunk.get("transcriptSegments")),
                    optional_float(chunk.get("timestampStart")),
                    optional_float(chunk.get("timestampEnd")),
                    optional_float(chunk.get("confidence")),
                    json_array_text(chunk.get("exactSearchTerms")),
                    json_array_text(chunk.get("exactSearchHits")),
                    as_text(chunk.get("coverageNotice")),
                    json_object_text(chunk.get("sourceInventoryRecord")),
                    optional_int(chunk.get("pageNumber")),
                    optional_int(chunk.get("slideNumber")),
                    as_text(chunk.get("sheetName")),
                    as_text(chunk.get("cellRange")),
                    as_text(chunk.get("contentHash")),
                    int(chunk.get("charCount")),
                    "embedding_vectors",
                    indexed_at,
                ),
            )
            vector_json = json.dumps(vector, separators=(",", ":"))
            conn.execute(
                """
                INSERT OR REPLACE INTO embedding_vectors (
                  chunk_id, embedding_model, embedding_dimensions, vector_json, vector_norm, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (chunk_id, model, expected_dimensions, vector_json, vector_norm(vector), indexed_at),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO chunk_texts (
                  chunk_id, content, content_snippet, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (chunk_id, content, snippet(content), indexed_at),
            )
            out.write(
                json.dumps(
                    {
                        "id": chunk_id,
                        "model": model,
                        "dimensions": expected_dimensions,
                        "vector": vector,
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
            written += 1

        completed_at = utcish_now()
        conn.execute(
            """
            UPDATE ingestion_jobs
            SET status = 'completed', completed_at = ?, accepted_chunks = ?
            WHERE job_id = ?
            """,
            (completed_at, written, job_id),
        )
        conn.commit()

    report = {
        "ok": True,
        "mode": "project_local_sqlite_jsonl_vector_mirror",
        "jobId": job_id,
        "completedAt": utcish_now(),
        "manifestPath": str(manifest_path),
        "sqliteDbPath": str(db_path),
        "embeddingsPath": str(embeddings_path),
        "embeddingModel": model,
        "embeddingDimensions": expected_dimensions,
        "chunksRead": len(chunks),
        "chunksWritten": written,
        "sourceInventoryPath": str(source_inventory_path) if source_inventory_path else "",
        "sourceInventoryRowsWritten": inventory_written,
        "writesOpenClaw": False,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
