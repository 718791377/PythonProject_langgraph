#!/usr/bin/env python3
"""Normalize QMD JSON shards for a future local vector ingestion pipeline.

The script is intentionally dry-run only. It reads QMD JSON files, computes
deterministic chunk IDs and content hashes, and optionally writes a JSONL
manifest outside protected source-material directories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Iterable


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


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def as_string(value: Any) -> str:
    return str(value or "").strip()


def as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [as_string(item) for item in value if as_string(item)]


def iter_qmd_files(root: Path) -> Iterable[Path]:
    yield from sorted(path for path in root.glob("*.json") if path.is_file())


def iter_shards(path: Path) -> Iterable[dict[str, Any]]:
    data = load_json(path)
    if isinstance(data, dict) and isinstance(data.get("shards"), list):
        for shard in data["shards"]:
            if isinstance(shard, dict):
                yield shard
    elif isinstance(data, list):
        for shard in data:
            if isinstance(shard, dict):
                yield shard
    elif isinstance(data, dict):
        yield data


def normalize_chunk(shard: dict[str, Any], source_file: Path, min_chars: int) -> dict[str, Any]:
    content = as_string(shard.get("content"))
    source_path = as_string(shard.get("sourcePath"))
    section_id = as_string(shard.get("sectionId"))
    canonical_pointer = as_string(shard.get("canonicalPointer"))
    identity_basis = "\n".join([source_path, section_id, canonical_pointer, content])
    content_hash = stable_hash(content)
    chunk_id = stable_hash(identity_basis)
    status = "accepted"
    skip_reason = ""
    if not content:
        status = "skipped"
        skip_reason = "empty_content"
    elif len(content) < min_chars:
        status = "skipped"
        skip_reason = "content_too_short"
    return {
        "id": chunk_id,
        "status": status,
        "skipReason": skip_reason,
        "sourceQmdFile": str(source_file),
        "sourcePath": source_path,
        "sourceAbsolutePath": as_string(shard.get("sourceAbsolutePath")),
        "sectionId": section_id,
        "heading": as_string(shard.get("heading")),
        "headingLevel": shard.get("headingLevel") if isinstance(shard.get("headingLevel"), int) else None,
        "canonicalPointer": canonical_pointer,
        "roleTags": as_string_list(shard.get("roleTags")),
        "keywords": as_string_list(shard.get("keywords")),
        "contentHash": content_hash,
        "charCount": len(content),
        "content": content,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--qmd-root", help="Override QMD root.")
    parser.add_argument("--out", help="Optional JSONL output path.")
    parser.add_argument("--include-skipped", action="store_true", help="Include skipped chunks in JSONL.")
    parser.add_argument("--min-chars", type=int, help="Minimum accepted content length.")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    qmd_cfg = config.get("qmd", {}) if isinstance(config, dict) else {}
    qmd_root = Path(args.qmd_root or qmd_cfg.get("defaultRoot", ""))
    min_chars = int(args.min_chars if args.min_chars is not None else qmd_cfg.get("minContentChars", 20))

    if not qmd_root.is_dir():
        raise SystemExit(f"QMD root not found: {qmd_root}")

    chunks: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    duplicate_count = 0
    for qmd_file in iter_qmd_files(qmd_root):
        for shard in iter_shards(qmd_file):
            chunk = normalize_chunk(shard, qmd_file, min_chars)
            dedupe_key = "::".join([chunk["sourcePath"], chunk["sectionId"], chunk["contentHash"]])
            if dedupe_key in seen_keys:
                duplicate_count += 1
                chunk["status"] = "skipped"
                chunk["skipReason"] = "duplicate"
            else:
                seen_keys.add(dedupe_key)
            chunks.append(chunk)

    accepted = [chunk for chunk in chunks if chunk["status"] == "accepted"]
    skipped = [chunk for chunk in chunks if chunk["status"] != "accepted"]
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        selected = chunks if args.include_skipped else accepted
        with out_path.open("w", encoding="utf-8") as handle:
            for chunk in selected:
                handle.write(json.dumps(chunk, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary = {
        "ok": True,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "qmdRoot": str(qmd_root),
        "qmdFileCount": len(list(iter_qmd_files(qmd_root))),
        "totalChunks": len(chunks),
        "acceptedChunks": len(accepted),
        "skippedChunks": len(skipped),
        "duplicateChunks": duplicate_count,
        "minContentChars": min_chars,
        "outputPath": str(Path(args.out)) if args.out else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
