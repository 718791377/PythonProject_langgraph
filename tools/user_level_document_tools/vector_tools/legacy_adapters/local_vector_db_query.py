#!/usr/bin/env python3
"""Query the project-local SQLite + JSONL vector mirror.

The query path embeds the input text through the configured local sidecar and
computes cosine similarity over vectors stored in the project-local SQLite
mirror. It does not read or write <configured-external-source-root>.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import time
from pathlib import Path
from typing import Any
from urllib import error, request


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"
WORD_RE = re.compile(r"[A-Za-z0-9_.:/#-]+")


def as_text(value: Any) -> str:
    return str(value or "").strip()


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))


def http_json(url: str, *, headers: dict[str, str], body: dict[str, Any], timeout: float) -> dict[str, Any]:
    req = request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json", **headers},
        data=json.dumps(body).encode("utf-8"),
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except (error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"HTTP request failed for {url}: {exc}") from exc
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("HTTP JSON response was not an object")
    return data


def embed_query(config: dict[str, Any], query: str, timeout: float) -> list[float]:
    embedding = config.get("embedding", {})
    if not isinstance(embedding, dict):
        raise ValueError("config.embedding must be an object")
    base_url = as_text(embedding.get("baseURL")).rstrip("/")
    model = as_text(embedding.get("model"))
    api_key = as_text(embedding.get("apiKey"))
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    data = http_json(
        f"{base_url}/embeddings",
        headers=headers,
        body={"model": model, "input": query},
        timeout=timeout,
    )
    rows = data.get("data")
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        raise RuntimeError("embedding response missing data[0]")
    vector = rows[0].get("embedding")
    if not isinstance(vector, list):
        raise RuntimeError("embedding response missing vector")
    return [float(value) for value in vector]


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cosine(query_vector: list[float], query_norm: float, doc_vector: list[float], doc_norm: float) -> float:
    if not query_norm or not doc_norm:
        return 0.0
    return sum(a * b for a, b in zip(query_vector, doc_vector)) / (query_norm * doc_norm)


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def now_stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def query_terms(query: str) -> list[str]:
    seen: set[str] = set()
    terms: list[str] = []
    for match in WORD_RE.finditer(query.lower()):
        term = match.group(0).strip("-_.:/#")
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        terms.append(term)
    return terms


def keyword_score(query: str, terms: list[str], row: sqlite3.Row) -> tuple[float, list[str]]:
    haystack = " ".join(
        [
            str(row["source_path"] or ""),
            str(row["section_id"] or ""),
            str(row["canonical_pointer"] or ""),
            str(row["heading"] or ""),
            str(row["exact_search_hits_json"] or "") if "exact_search_hits_json" in row.keys() else "",
            str(row["content_snippet"] or ""),
            str(row["content"] or ""),
        ]
    ).lower()
    if not terms:
        return 0.0, []
    matched = [term for term in terms if term in haystack]
    score = len(matched) / len(terms)
    if query.lower() in haystack:
        score = min(1.0, score + 0.25)
    return score, matched


def optional_column(existing: set[str], name: str, table_alias: str = "c") -> str:
    return f"{table_alias}.{name}" if name in existing else f"NULL AS {name}"


def parse_json_array(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def parse_json_object(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def coverage_summary(conn: sqlite3.Connection) -> dict[str, Any]:
    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='source_inventory_records'"
    ).fetchone()
    if not table_exists:
        return {"available": False, "recordCount": 0, "countsByExtractionStatus": {}, "incompleteCoverageCounts": {}}
    rows = conn.execute(
        "SELECT extraction_status, COUNT(*) AS count FROM source_inventory_records GROUP BY extraction_status"
    ).fetchall()
    counts = {str(row["extraction_status"] or ""): int(row["count"]) for row in rows}
    incomplete = {key: value for key, value in counts.items() if key not in {"indexed_full", "indexed_partial"} and value}
    return {"available": True, "recordCount": sum(counts.values()), "countsByExtractionStatus": counts, "incompleteCoverageCounts": incomplete}


def bounded_negative_wording(query: str, coverage: dict[str, Any]) -> str:
    incomplete = coverage.get("incompleteCoverageCounts") or {}
    if incomplete:
        detail = ", ".join(f"{key}={value}" for key, value in sorted(incomplete.items()))
        return f"`{query}` was not found in successfully indexed text chunks, but source coverage is incomplete ({detail}); this is not a complete negative conclusion."
    if coverage.get("available"):
        return f"`{query}` was not found in indexed text chunks, and no incomplete source-inventory statuses were recorded."
    return f"`{query}` was not found in indexed text chunks; no source-inventory coverage table was available."


def audit_query(
    conn: sqlite3.Connection,
    *,
    query: str,
    mode: str,
    limit: int,
    result_count: int,
    notes: dict[str, Any],
) -> str:
    created_at = now_stamp()
    query_id = stable_hash(f"{created_at}|{mode}|{query}")[:32]
    conn.execute(
        """
        INSERT OR REPLACE INTO query_audit (
          query_id, query_text_hash, retrieval_mode, vector_table,
          limit_requested, result_count, created_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            query_id,
            stable_hash(query),
            mode,
            "embedding_vectors",
            limit,
            result_count,
            created_at,
            json.dumps(notes, ensure_ascii=False, sort_keys=True),
        ),
    )
    conn.commit()
    return query_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Query text.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--db", help="SQLite mirror path. Defaults to projectLocalMirror.metadata.dbPath.")
    parser.add_argument("--limit", type=int, default=5, help="Number of results.")
    parser.add_argument("--mode", choices=("vector", "qmd", "hybrid"), default="vector", help="Retrieval mode.")
    parser.add_argument("--no-audit", action="store_true", help="Do not write query_audit row.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Embedding HTTP timeout.")
    parser.add_argument("--out", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    config = load_json(Path(args.config))
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")
    mirror = config.get("projectLocalMirror", {})
    metadata = mirror.get("metadata", {}) if isinstance(mirror, dict) else {}
    db_path = Path(args.db or as_text(metadata.get("dbPath")))

    query_vector: list[float] = []
    query_norm = 0.0
    if args.mode in {"vector", "hybrid"}:
        query_vector = embed_query(config, args.query, args.timeout)
        query_norm = norm(query_vector)
    terms = query_terms(args.query)
    results: list[dict[str, Any]] = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        indexed_columns = {row[1] for row in conn.execute("PRAGMA table_info(indexed_chunks)").fetchall()}
        rows = conn.execute(
            f"""
            SELECT c.chunk_id, c.source_path, c.section_id, c.canonical_pointer, c.heading,
                   c.content_hash, c.char_count, v.vector_json, v.vector_norm,
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
                   t.content_snippet, t.content
            FROM indexed_chunks c
            JOIN embedding_vectors v ON v.chunk_id = c.chunk_id
            LEFT JOIN chunk_texts t ON t.chunk_id = c.chunk_id
            """
        ).fetchall()
        for row in rows:
            vector_score = 0.0
            if args.mode in {"vector", "hybrid"}:
                vector = [float(value) for value in json.loads(row["vector_json"])]
                vector_score = cosine(query_vector, query_norm, vector, float(row["vector_norm"]))
            text_score, matched_terms = keyword_score(args.query, terms, row)
            if args.mode == "vector":
                score = vector_score
                retrieval_mode = "project_local_sqlite_vector"
            elif args.mode == "qmd":
                score = text_score
                retrieval_mode = "project_local_qmd_keyword"
            else:
                score = (0.75 * vector_score) + (0.25 * text_score)
                retrieval_mode = "project_local_hybrid"
            if score <= 0 and args.mode != "vector":
                continue
            results.append(
                {
                    "score": score,
                    "vectorScore": vector_score,
                    "keywordScore": text_score,
                    "matchedTerms": matched_terms,
                    "id": row["chunk_id"],
                    "sourcePath": row["source_path"],
                    "sectionId": row["section_id"],
                    "canonicalPointer": row["canonical_pointer"],
                    "heading": row["heading"],
                    "contentHash": row["content_hash"],
                    "charCount": row["char_count"],
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
                    "conversionChain": parse_json_array(row["conversion_chain_json"]),
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
                    "containerDepth": row["container_depth"],
                    "archiveRecursionStatus": row["archive_recursion_status"] or "",
                    "ocrStatus": parse_json_object(row["ocr_status_json"]),
                    "speechToTextStatus": parse_json_object(row["speech_to_text_status_json"]),
                    "transcriptSegments": parse_json_array(row["transcript_segments_json"]),
                    "timestampStart": row["timestamp_start"],
                    "timestampEnd": row["timestamp_end"],
                    "confidence": row["confidence"],
                    "exactSearchTerms": parse_json_array(row["exact_search_terms_json"]),
                    "exactSearchHits": parse_json_array(row["exact_search_hits_json"]),
                    "coverageNotice": row["coverage_notice"] or "",
                    "sourceInventoryRecord": parse_json_object(row["source_inventory_record_json"]),
                    "pageNumber": row["page_number"],
                    "slideNumber": row["slide_number"],
                    "sheetName": row["sheet_name"] or "",
                    "cellRange": row["cell_range"] or "",
                    "contentSnippet": row["content_snippet"] or "",
                    "retrievalMode": retrieval_mode,
                }
            )
        results.sort(key=lambda item: item["score"], reverse=True)
        selected = results[: max(args.limit, 0)]
        coverage = coverage_summary(conn)
        negative_notice = "" if selected else bounded_negative_wording(args.query, coverage)
        query_audit_id = None
        if not args.no_audit:
            query_audit_id = audit_query(
                conn,
                query=args.query,
                mode=args.mode,
                limit=max(args.limit, 0),
                result_count=len(selected),
                notes={"terms": terms, "dbPath": str(db_path), "coverage": coverage, "boundedNegativeResultWording": negative_notice},
            )
    payload = {
        "ok": True,
        "query": args.query,
        "mode": args.mode,
        "dbPath": str(db_path),
        "queryAuditId": query_audit_id,
        "resultCount": len(selected),
        "coverage": coverage,
        "boundedNegativeResultWording": negative_notice,
        "results": selected,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
