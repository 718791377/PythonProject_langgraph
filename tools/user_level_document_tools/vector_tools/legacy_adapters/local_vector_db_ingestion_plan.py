#!/usr/bin/env python3
"""Create a non-mutating ingestion plan from a validated QMD dry-run manifest.

This tool does not call the embedding endpoint and does not write to
<configured-external-source-root>. It only converts an already validated dry-run
manifest into an auditable plan for a later project-local ingestion task.
"""

from __future__ import annotations

import argparse
import json
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
DEFAULT_VALIDATION_PATH = (
    PROJECT_ROOT
    / ".project-runtime"
    / "local-vector-db"
    / "reports"
    / "manifest_validation.json"
)


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


def metadata_row(chunk: dict[str, Any]) -> dict[str, Any]:
    """Return the metadata-only row planned for future vector ingestion."""

    return {
        "id": as_text(chunk.get("id")),
        "sourcePath": as_text(chunk.get("sourcePath")),
        "sectionId": as_text(chunk.get("sectionId")),
        "canonicalPointer": as_text(chunk.get("canonicalPointer")),
        "heading": as_text(chunk.get("heading")),
        "headingLevel": chunk.get("headingLevel") if isinstance(chunk.get("headingLevel"), int) else None,
        "roleTags": chunk.get("roleTags") if isinstance(chunk.get("roleTags"), list) else [],
        "keywords": chunk.get("keywords") if isinstance(chunk.get("keywords"), list) else [],
        "contentHash": as_text(chunk.get("contentHash")),
        "charCount": chunk.get("charCount") if isinstance(chunk.get("charCount"), int) else None,
    }


def require_validation_ok(path: Path) -> dict[str, Any]:
    validation = load_json(path)
    if not isinstance(validation, dict):
        raise ValueError(f"validation report is not an object: {path}")
    if validation.get("ok") is not True:
        raise ValueError(f"manifest validation is not OK: {path}")
    return validation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH), help="Validated QMD dry-run JSONL manifest.")
    parser.add_argument(
        "--manifest-validation",
        default=str(DEFAULT_VALIDATION_PATH),
        help="JSON report produced by local_vector_db_manifest_validate.py.",
    )
    parser.add_argument("--target-table", help="Planned future LanceDB table name.")
    parser.add_argument("--out", help="Optional JSON output path.")
    parser.add_argument("--max-preview-rows", type=int, default=10, help="Metadata-only preview row count.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    manifest_path = Path(args.manifest)
    validation_path = Path(args.manifest_validation)

    config = load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError(f"config root is not an object: {config_path}")
    project_mirror = config.get("projectLocalMirror", {}) if isinstance(config, dict) else {}
    if as_text(args.manifest) == str(DEFAULT_MANIFEST_PATH) and as_text(project_mirror.get("chunksManifestPath")):
        manifest_path = Path(as_text(project_mirror.get("chunksManifestPath")))
    if as_text(args.manifest_validation) == str(DEFAULT_VALIDATION_PATH) and as_text(
        project_mirror.get("validationReportPath")
    ):
        validation_path = Path(as_text(project_mirror.get("validationReportPath")))

    validation = require_validation_ok(validation_path)
    chunks = [row for row in load_jsonl(manifest_path) if as_text(row.get("status")) in {"", "accepted"}]

    embedding = config.get("embedding", {})
    stores = config.get("stores", {})
    mirror_vector = project_mirror.get("vector", {}) if isinstance(project_mirror, dict) else {}
    mirror_metadata = project_mirror.get("metadata", {}) if isinstance(project_mirror, dict) else {}
    vector_store = mirror_vector or (stores.get("vector", {}) if isinstance(stores, dict) else {})
    metadata_store = mirror_metadata or (stores.get("metadata", {}) if isinstance(stores, dict) else {})
    db_path = Path(as_text(vector_store.get("dbPath")))
    metadata_db_path = as_text(metadata_store.get("dbPath"))
    target_table = as_text(args.target_table or mirror_vector.get("targetTable"))
    target_lance_path = str(db_path / target_table) if target_table else str(db_path)

    plan = {
        "ok": True,
        "mode": "non_mutating_ingestion_plan",
        "plannedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "configPath": str(config_path),
        "manifestPath": str(manifest_path),
        "manifestValidationPath": str(validation_path),
        "validationSummary": {
            "rowCount": validation.get("rowCount"),
            "acceptedRows": validation.get("acceptedRows"),
            "errorCount": validation.get("errorCount"),
        },
        "gate": {
            "writesOpenClaw": False,
            "writesProjectLocalMirror": True,
            "requiresExplicitInstructionBeforeProjectLocalMirrorWrite": True,
            "requiresOpenClawRepositoryWorkflow": False,
            "requiresEmbeddingEndpointAvailable": True,
            "requiresGuardCheckForFutureWritePaths": True,
        },
        "embedding": {
            "provider": embedding.get("provider"),
            "baseURL": embedding.get("baseURL"),
            "model": embedding.get("model"),
            "dimensions": embedding.get("dimensions"),
        },
        "plannedTargets": {
            "vectorProvider": vector_store.get("provider"),
            "vectorDbPath": vector_store.get("dbPath"),
            "targetTable": target_table,
            "targetLancePath": target_lance_path,
            "metadataProvider": metadata_store.get("provider"),
            "metadataDbPath": metadata_db_path,
        },
        "futureWritePaths": [
            target_lance_path,
            metadata_db_path,
        ],
        "rowContract": [
            "id",
            "vector",
            "content",
            "sourcePath",
            "sectionId",
            "canonicalPointer",
            "heading",
            "roleTagsJson",
            "keywordsJson",
            "contentHash",
            "indexedAt",
        ],
        "auditContract": [
            "ingestion_jobs",
            "indexed_chunks",
            "query_audit",
            "schema_migrations",
        ],
        "chunkCount": len(chunks),
        "previewRows": [metadata_row(chunk) for chunk in chunks[: max(args.max_preview_rows, 0)]],
    }

    output = json.dumps(plan, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
