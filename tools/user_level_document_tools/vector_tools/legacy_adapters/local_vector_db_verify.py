#!/usr/bin/env python3
"""Offline verifier for the project-local vector mirror.

The verifier checks files, SQLite tables, row counts, vector dimensions,
query audit coverage, and smoke-test reports. It does not call the embedding
sidecar and does not read or write <configured-external-source-root>.
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


def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig") as handle:
        return sum(1 for line in handle if line.strip())


def add_check(checks: list[dict[str, Any]], name: str, ok: bool, **details: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), **details})


def report_query_file(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"query report is not an object: {path}")
    results = data.get("results")
    if not isinstance(results, list):
        results = []
    return {
        "path": str(path),
        "ok": bool(data.get("ok")),
        "mode": data.get("mode"),
        "resultCount": data.get("resultCount"),
        "hasAuditId": bool(data.get("queryAuditId")),
        "allHaveSourcePointers": all(
            bool(item.get("sourcePath") and item.get("sectionId") and item.get("canonicalPointer"))
            for item in results
            if isinstance(item, dict)
        ),
        "allHaveSnippets": all(bool(item.get("contentSnippet")) for item in results if isinstance(item, dict)),
    }


def report_lancedb_file(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"LanceDB report is not an object: {path}")
    return {
        "path": str(path),
        "ok": bool(data.get("ok")),
        "rowsRead": data.get("rowsRead"),
        "rowsWritten": data.get("rowsWritten"),
        "tableName": data.get("tableName"),
        "tablePath": data.get("tablePath"),
        "writesOpenClaw": bool(data.get("writesOpenClaw")),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--out", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    config = load_json(Path(args.config))
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")
    mirror = config.get("projectLocalMirror", {})
    if not isinstance(mirror, dict):
        raise ValueError("config.projectLocalMirror must be an object")
    metadata = mirror.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("config.projectLocalMirror.metadata must be an object")
    expected_dimensions = int(config.get("embedding", {}).get("dimensions"))

    data_root = Path(as_text(mirror.get("dataRoot")))
    runtime_root = Path(as_text(mirror.get("runtimeRoot")))
    manifest_path = Path(as_text(mirror.get("chunksManifestPath")))
    db_path = Path(as_text(metadata.get("dbPath")))
    embeddings_path = data_root / "embeddings.jsonl"
    reports_root = runtime_root / "reports"
    checks: list[dict[str, Any]] = []

    for label, path in (
        ("dataRoot", data_root),
        ("runtimeRoot", runtime_root),
        ("chunksManifest", manifest_path),
        ("sqliteDb", db_path),
        ("embeddingsJsonl", embeddings_path),
        ("reportsRoot", reports_root),
    ):
        add_check(checks, f"path.{label}", path.exists(), path=str(path), isFile=path.is_file(), isDir=path.is_dir())

    chunks = load_jsonl(manifest_path)
    embeddings_line_count = count_lines(embeddings_path)
    accepted_chunks = [chunk for chunk in chunks if as_text(chunk.get("status")) in {"", "accepted"}]
    add_check(
        checks,
        "manifest.accepted_count",
        len(accepted_chunks) > 0,
        acceptedChunks=len(accepted_chunks),
        totalManifestRows=len(chunks),
    )
    add_check(
        checks,
        "embeddings.line_count_matches_manifest",
        embeddings_line_count == len(accepted_chunks),
        embeddingsLines=embeddings_line_count,
        acceptedChunks=len(accepted_chunks),
    )

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        required_tables = {
            "ingestion_jobs",
            "indexed_chunks",
            "embedding_vectors",
            "chunk_texts",
            "query_audit",
            "schema_migrations",
        }
        missing_tables = sorted(required_tables - table_names)
        add_check(checks, "sqlite.required_tables", not missing_tables, missingTables=missing_tables)
        row_counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in sorted(required_tables & table_names)
        }
        sample_vector = conn.execute(
            "SELECT embedding_dimensions, vector_json FROM embedding_vectors LIMIT 1"
        ).fetchone()
        actual_dimension = None
        declared_dimension = None
        if sample_vector is not None:
            declared_dimension = sample_vector["embedding_dimensions"]
            actual_dimension = len(json.loads(sample_vector["vector_json"]))
        audit_modes = {
            row["retrieval_mode"]: row["count"]
            for row in conn.execute(
                "SELECT retrieval_mode, COUNT(*) AS count FROM query_audit GROUP BY retrieval_mode"
            ).fetchall()
        }

    for table in ("indexed_chunks", "embedding_vectors", "chunk_texts"):
        add_check(
            checks,
            f"sqlite.{table}_count_matches_manifest",
            row_counts.get(table) == len(accepted_chunks),
            rows=row_counts.get(table),
            acceptedChunks=len(accepted_chunks),
        )
    add_check(
        checks,
        "sqlite.vector_dimension",
        declared_dimension == expected_dimensions and actual_dimension == expected_dimensions,
        expectedDimensions=expected_dimensions,
        declaredDimensions=declared_dimension,
        actualDimensions=actual_dimension,
    )
    add_check(
        checks,
        "sqlite.query_audit_modes",
        all(mode in audit_modes for mode in ("vector", "qmd", "hybrid")),
        auditModes=audit_modes,
    )

    query_reports = [
        report_query_file(reports_root / "query_smoke.json"),
        report_query_file(reports_root / "qmd_query_smoke.json"),
        report_query_file(reports_root / "hybrid_query_smoke.json"),
        report_query_file(reports_root / "lancedb_query_smoke.json"),
    ]
    for report in query_reports:
        report_details = dict(report)
        report_ok = bool(report_details.pop("ok"))
        requires_audit = Path(report["path"]).name != "lancedb_query_smoke.json"
        add_check(
            checks,
            f"query_report.{Path(report['path']).name}",
            bool(
                report_ok
                and (report["hasAuditId"] or not requires_audit)
                and report["allHaveSourcePointers"]
                and report["allHaveSnippets"]
            ),
            reportOk=report_ok,
            requiresAudit=requires_audit,
            **report_details,
        )

    lancedb_report = report_lancedb_file(reports_root / "lancedb_sync.json")
    lancedb_report_details = dict(lancedb_report)
    lancedb_report_ok = bool(lancedb_report_details.pop("ok"))
    add_check(
        checks,
        "lancedb.sync_report",
        bool(
            lancedb_report_ok
            and lancedb_report["writesOpenClaw"] is False
            and lancedb_report["rowsRead"] == len(accepted_chunks)
            and lancedb_report["rowsWritten"] == len(accepted_chunks)
        ),
        reportOk=lancedb_report_ok,
        **lancedb_report_details,
    )

    ok = all(check["ok"] for check in checks)
    payload = {
        "ok": ok,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "configPath": str(Path(args.config)),
        "dataRoot": str(data_root),
        "runtimeRoot": str(runtime_root),
        "rowCounts": row_counts,
        "auditModes": audit_modes,
        "queryReports": query_reports,
        "lancedbReport": lancedb_report,
        "checks": checks,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
