#!/usr/bin/env python3
"""Query the project-local LanceDB authority chunk table.

The query embeds input through the configured local embedding sidecar, searches
the project-local LanceDB table, and writes only optional report output under
``<consumer-project-root>``. It does not mutate ``<configured-external-source-root>``.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib import error, request


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


def normalize_table_name(value: str) -> str:
    table = as_text(value) or "authority_chunks"
    if table.endswith(".lance"):
        table = table[: -len(".lance")]
    return table


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


def score_from_row(row: dict[str, Any]) -> float:
    for key in ("_distance", "_score", "score"):
        if key in row and row[key] is not None:
            value = float(row[key])
            return 1.0 / (1.0 + value) if key == "_distance" else value
    return 0.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Query text.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--lancedb-path", help="Project-local LanceDB directory.")
    parser.add_argument("--table", help="LanceDB table name. A trailing .lance suffix is ignored.")
    parser.add_argument("--limit", type=int, default=5, help="Number of results.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Embedding HTTP timeout.")
    parser.add_argument("--out", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")
    mirror = config.get("projectLocalMirror", {})
    vector_cfg = mirror.get("vector", {}) if isinstance(mirror, dict) else {}
    if not isinstance(vector_cfg, dict):
        raise ValueError("config.projectLocalMirror.vector must be an object")

    lancedb_path = Path(args.lancedb_path or as_text(vector_cfg.get("dbPath")))
    table_name = normalize_table_name(args.table or as_text(vector_cfg.get("targetTable")))
    query_vector = embed_query(config, args.query, args.timeout)

    import lancedb  # imported lazily so --help works before dependency installation

    db = lancedb.connect(str(lancedb_path))
    table = db.open_table(table_name)
    raw_results = table.search(query_vector).limit(max(args.limit, 0)).to_list()
    results: list[dict[str, Any]] = []
    for row in raw_results:
        if not isinstance(row, dict):
            continue
        results.append(
            {
                "score": score_from_row(row),
                "distance": row.get("_distance"),
                "id": row.get("id"),
                "sourcePath": row.get("sourcePath"),
                "sectionId": row.get("sectionId"),
                "canonicalPointer": row.get("canonicalPointer"),
                "heading": row.get("heading"),
                "contentHash": row.get("contentHash"),
                "charCount": row.get("charCount"),
                "sourceSha256": row.get("sourceSha256") or "",
                "extractionMethod": row.get("extractionMethod") or "",
                "authorityStatus": row.get("authorityStatus") or "",
                "usableForFacts": bool(row.get("usableForFacts")),
                "manualReviewPromoted": bool(row.get("manualReviewPromoted")),
                "qualityEvidencePath": row.get("qualityEvidencePath") or "",
                "qualityReportPath": row.get("qualityReportPath") or "",
                "renderEvidencePath": row.get("renderEvidencePath") or "",
                "contactSheetPath": row.get("contactSheetPath") or "",
                "fontReportPath": row.get("fontReportPath") or "",
                "conversionChainJson": row.get("conversionChainJson") or "[]",
                "evidencePurpose": row.get("evidencePurpose") or "",
                "factBoundaryNote": row.get("factBoundaryNote") or "",
                "pageNumber": row.get("pageNumber"),
                "slideNumber": row.get("slideNumber"),
                "sheetName": row.get("sheetName") or "",
                "cellRange": row.get("cellRange") or "",
                "contentSnippet": row.get("contentSnippet") or "",
                "retrievalMode": "project_local_lancedb_vector",
            }
        )

    payload = {
        "ok": True,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "query": args.query,
        "mode": "lancedb",
        "lancedbPath": str(lancedb_path),
        "tableName": table_name,
        "resultCount": len(results),
        "results": results,
        "writesOpenClaw": False,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
