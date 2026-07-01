#!/usr/bin/env python3
"""Document knowledge handoff utility for tender/material generation tasks.

This tool is intentionally project-local. It bridges document-pipeline text
artifacts under intermediate/document_knowledge_handoff to the local vector
control plane without writing protected source folders or OpenClaw.
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, textwrap, time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path.cwd()
HANDOFF_ROOT = PROJECT_ROOT / "intermediate" / "document_knowledge_handoff"
SCHEMA_DIR = PROJECT_ROOT / "config" / "document_knowledge_handoff"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
DIRS = ["extraction_runs", "extracted_text", "ocr_text", "converted_text", "normalized_chunks", "manifests", "rejected", "logs"]
CHUNK_REQUIRED = ["schemaVersion", "chunkId", "documentId", "sourcePath", "sourceAbsolutePath", "sourceSha256", "content", "contentHash", "contentSnippet", "charCount", "extractionMethod", "authorityStatus", "usableForFacts"]
MANIFEST_REQUIRED = ["schemaVersion", "runId", "taskScope", "artifactType", "documentId", "sourcePath", "sourceAbsolutePath", "sourceSha256", "producedPath", "extractionMethod", "authorityStatus", "usableForFacts", "createdAt"]
INVENTORY_EXTRA_FIELDS = [
    "sourceInventoryPath",
    "inventoryRecordType",
    "inventoryStatus",
    "extractionStatus",
    "formatFamily",
    "modality",
    "extractorId",
    "extractorName",
    "extractorVersion",
    "containerPath",
    "containerDepth",
    "archiveRecursionStatus",
    "ocrStatus",
    "speechToTextStatus",
    "transcriptSegments",
    "timestampStart",
    "timestampEnd",
    "confidence",
    "exactSearchTerms",
    "exactSearchHits",
    "coverageNotice",
    "sourceInventoryRecord",
]
INVENTORY_STATUS_VALUES = {"indexed_full", "indexed_partial", "ocr_required", "speech_to_text_required", "encrypted", "unsupported", "failed", "skipped_by_policy", "metadata_only"}
PROTECTED_NAMES = ("current_progress", "regulations", "requirement")
RECONSTRUCTED_METHODS = {"acrobat_ocr", "pdf_to_docx", "pdf_to_xlsx", "pdf_to_pptx"}
RECONSTRUCTED_STATUSES = {"ocr_reconstructed", "pdf_reconstructed"}
FACT_BOUNDARY_NOTE = (
    "Visual, font, render, contact-sheet, OCR, and PDF-to-Office reconstruction "
    "evidence supports layout/rendering review only. It is not proof of tender "
    "facts such as contract amounts, durations, owners, equipment quantities, "
    "model numbers, or source page references."
)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_no}: JSONL row is not an object")
            value["_lineNumber"] = line_no
            rows.append(value)
    return rows


def stable_doc_id(path_value: Any, fallback: str = "document") -> str:
    text = str(path_value or "").strip()
    if not text:
        return fallback
    return sha_text(text)[:24]


def inventory_metadata(row: dict[str, Any], inventory_path: Path) -> dict[str, Any]:
    status = str(row.get("extractionStatus") or "")
    coverage_notice = ""
    if status and status not in {"indexed_full", "indexed_partial"}:
        coverage_notice = (
            f"Source inventory status is {status}; this file was not fully indexed, "
            "so absence from extracted text is not a complete negative result."
        )
    return {
        "sourceInventoryPath": rel_or_abs(inventory_path),
        "inventoryRecordType": row.get("recordType"),
        "inventoryStatus": status,
        "extractionStatus": status,
        "formatFamily": row.get("formatFamily"),
        "modality": row.get("modality"),
        "extractorId": row.get("extractorId"),
        "extractorName": row.get("extractorName"),
        "extractorVersion": row.get("extractorVersion"),
        "containerPath": row.get("containerPath"),
        "containerDepth": row.get("containerDepth"),
        "archiveRecursionStatus": row.get("archiveRecursionStatus"),
        "ocrStatus": row.get("ocrStatus"),
        "speechToTextStatus": row.get("speechToTextStatus"),
        "transcriptSegments": row.get("transcriptSegments"),
        "timestampStart": row.get("timestampStart"),
        "timestampEnd": row.get("timestampEnd"),
        "confidence": row.get("confidence"),
        "exactSearchTerms": row.get("exactSearchTerms"),
        "exactSearchHits": row.get("exactSearchHits"),
        "coverageNotice": coverage_notice,
        "sourceInventoryRecord": {key: row.get(key) for key in (
            "recordType",
            "relativePath",
            "extension",
            "mimeType",
            "formatFamily",
            "modality",
            "extractorId",
            "extractionStatus",
            "containerPath",
            "archiveRecursionStatus",
        )},
    }


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    value = json.loads(read_text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root is not an object")
    return value


def rel_or_abs(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def protected_dirs() -> list[Path]:
    roots = [PROJECT_ROOT]
    canonical = Path(r"$(Get-Location)")
    if canonical not in roots:
        roots.append(canonical)
    return [(root / name).resolve(strict=False) for root in roots for name in PROTECTED_NAMES]


def is_under(path: Path, parent: Path) -> bool:
    child_key = os.path.normcase(str(path.resolve(strict=False)))
    parent_key = os.path.normcase(str(parent.resolve(strict=False)))
    return child_key == parent_key or child_key.startswith(parent_key + os.sep)


def validate_generated_path(path_value: Any, label: str, errors: list[str], line: Any) -> None:
    if path_value in (None, ""):
        return
    candidate = Path(str(path_value))
    for protected in protected_dirs():
        if is_under(candidate, protected):
            errors.append(f"line {line}: {label} targets protected source directory: {candidate}")


def evidence_metadata(args: argparse.Namespace) -> dict[str, Any]:
    evidence_path = Path(args.quality_evidence_path) if args.quality_evidence_path else None
    evidence = load_json(evidence_path)
    conversion_chain = evidence.get("conversionChain") if isinstance(evidence.get("conversionChain"), list) else []
    if args.conversion_chain_json:
        value = json.loads(args.conversion_chain_json)
        if not isinstance(value, list):
            raise ValueError("--conversion-chain-json must be a JSON array")
        conversion_chain = value
    quality_report_path = args.quality_report_path or evidence.get("qualityReportPath")
    render_evidence_path = args.render_evidence_path or evidence.get("renderRoot") or evidence.get("contactSheetPath")
    evidence_purpose = args.evidence_purpose
    if evidence.get("evidencePurpose") == "layout_rendering_only" and not evidence_purpose:
        evidence_purpose = "layout_rendering_only"
    if not evidence_purpose:
        if args.authority_status == "source":
            evidence_purpose = "factual_source_text"
        elif args.authority_status in RECONSTRUCTED_STATUSES:
            evidence_purpose = "reconstructed_text"
        elif args.authority_status == "draft":
            evidence_purpose = "generated_draft"
        else:
            evidence_purpose = "converted_text"
    return {
        "qualityEvidencePath": rel_or_abs(evidence_path) if evidence_path else None,
        "qualityReportPath": quality_report_path,
        "renderEvidencePath": render_evidence_path,
        "contactSheetPath": args.contact_sheet_path or evidence.get("contactSheetPath"),
        "fontReportPath": args.font_report_path or evidence.get("fontReportPath"),
        "conversionChain": conversion_chain,
        "evidencePurpose": evidence_purpose,
        "factBoundaryNote": FACT_BOUNDARY_NOTE if evidence_purpose in {"layout_rendering_only", "reconstructed_text"} else args.fact_boundary_note,
    }


def compute_usable_for_facts(args: argparse.Namespace) -> bool:
    if args.authority_status in RECONSTRUCTED_STATUSES or args.extraction_method in RECONSTRUCTED_METHODS:
        return bool(args.usable_for_facts and args.manual_review_promoted)
    if args.authority_status == "quality_evidence":
        return False
    return bool(args.usable_for_facts)


def split_chunks(text: str, size: int, overlap: int) -> list[str]:
    clean = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()
    if not clean:
        return []
    parts: list[str] = []
    start = 0
    size = max(size, 200)
    overlap = max(0, min(overlap, size // 2))
    while start < len(clean):
        end = min(len(clean), start + size)
        cut = clean.rfind("\n\n", start, end)
        if cut <= start + 200 or end == len(clean):
            cut = end
        chunk = clean[start:cut].strip()
        if chunk:
            parts.append(chunk)
        if cut >= len(clean):
            break
        start = max(cut - overlap, start + 1)
    return parts


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.output_root or HANDOFF_ROOT)
    for name in DIRS:
        (root / name).mkdir(parents=True, exist_ok=True)
    print(json.dumps({"ok": True, "handoffRoot": str(root), "directories": DIRS}, ensure_ascii=False, indent=2))
    return 0


def cmd_chunk_text(args: argparse.Namespace) -> int:
    out_root = Path(args.output_root or HANDOFF_ROOT)
    source = Path(args.source)
    text_path = Path(args.text)
    text = read_text(text_path)
    chunks = split_chunks(text, args.chunk_chars, args.overlap)
    source_abs = str(source.resolve())
    source_hash = sha_file(source) if source.exists() and source.is_file() else "0" * 64
    produced_hash = sha_file(text_path)
    usable = compute_usable_for_facts(args)
    metadata = evidence_metadata(args)
    manifest_path = out_root / "manifests" / f"{args.run_id}.jsonl"
    chunks_path = out_root / "normalized_chunks" / f"{args.run_id}.chunks.jsonl"
    manifest = [{
        "schemaVersion": "1", "runId": args.run_id, "taskScope": args.task_scope,
        "artifactType": "normalized_chunks", "documentId": args.document_id,
        "sourcePath": args.source_path or rel_or_abs(source), "sourceAbsolutePath": source_abs,
        "sourceSha256": source_hash, "producedPath": rel_or_abs(text_path),
        "producedSha256": produced_hash, "extractionMethod": args.extraction_method,
        "authorityStatus": args.authority_status, "usableForFacts": usable,
        "manualReviewPromoted": bool(args.manual_review_promoted),
        "qualityEvidencePath": metadata["qualityEvidencePath"],
        "qualityReportPath": metadata["qualityReportPath"],
        "renderEvidencePath": metadata["renderEvidencePath"],
        "contactSheetPath": metadata["contactSheetPath"],
        "fontReportPath": metadata["fontReportPath"],
        "conversionChain": metadata["conversionChain"],
        "evidencePurpose": metadata["evidencePurpose"],
        "factBoundaryNote": metadata["factBoundaryNote"],
        "contentPath": rel_or_abs(text_path),
        "chunkManifestPath": rel_or_abs(chunks_path), "createdAt": now(), "notes": args.notes,
        "pageNumber": args.page_number, "slideNumber": args.slide_number,
        "sheetName": args.sheet_name, "cellRange": args.cell_range,
    }]
    rows = []
    for idx, content in enumerate(chunks, 1):
        content_hash = sha_text(content)
        section = args.section_id or f"chunk-{idx:04d}"
        pointer = args.canonical_pointer or f"{args.document_id}#{section}"
        rows.append({
            "schemaVersion": "1", "chunkId": sha_text("|".join([args.document_id, section, content_hash])),
            "documentId": args.document_id, "sourcePath": args.source_path or rel_or_abs(source),
            "sourceAbsolutePath": source_abs, "sourceSha256": source_hash,
            "sectionId": section, "canonicalPointer": pointer, "heading": args.heading,
            "pageNumber": args.page_number, "content": content, "contentHash": content_hash,
            "contentSnippet": content[:300], "charCount": len(content),
            "extractionMethod": args.extraction_method, "authorityStatus": args.authority_status,
            "usableForFacts": usable, "manualReviewPromoted": bool(args.manual_review_promoted),
            "qualityEvidencePath": metadata["qualityEvidencePath"],
            "qualityReportPath": metadata["qualityReportPath"],
            "renderEvidencePath": metadata["renderEvidencePath"],
            "contactSheetPath": metadata["contactSheetPath"],
            "fontReportPath": metadata["fontReportPath"],
            "conversionChain": metadata["conversionChain"],
            "evidencePurpose": metadata["evidencePurpose"],
            "factBoundaryNote": metadata["factBoundaryNote"],
            "slideNumber": args.slide_number, "sheetName": args.sheet_name,
            "cellRange": args.cell_range,
            "handoffManifestPath": rel_or_abs(manifest_path),
        })
    write_jsonl(manifest_path, manifest)
    write_jsonl(chunks_path, rows)
    print(json.dumps({"ok": True, "manifestPath": str(manifest_path), "chunksPath": str(chunks_path), "chunkCount": len(rows), "usableForFacts": usable}, ensure_ascii=False, indent=2))
    return 0


def validate_rows(rows: list[dict[str, Any]], required: list[str], kind: str) -> list[str]:
    errors: list[str] = []
    for row in rows:
        line = row.get("_lineNumber", "?")
        for key in required:
            if key not in row or row.get(key) in (None, ""):
                if key == "pageNumber":
                    continue
                errors.append(f"{kind} line {line}: missing {key}")
        for key in ("sourceSha256", "contentHash", "producedSha256"):
            if key in row and row.get(key) not in (None, "") and not HEX64.match(str(row[key])):
                errors.append(f"{kind} line {line}: {key} is not sha256 hex")
        if row.get("conversionChain") not in (None, "") and not isinstance(row.get("conversionChain"), list):
            errors.append(f"{kind} line {line}: conversionChain must be an array")
        status = str(row.get("authorityStatus") or "")
        method = str(row.get("extractionMethod") or "")
        if (status in RECONSTRUCTED_STATUSES or method in RECONSTRUCTED_METHODS) and row.get("usableForFacts") is True and row.get("manualReviewPromoted") is not True:
            errors.append(f"{kind} line {line}: reconstructed/OCR text cannot be usableForFacts=true without manualReviewPromoted=true")
        if status == "quality_evidence" and row.get("usableForFacts") is True:
            errors.append(f"{kind} line {line}: quality evidence cannot be usableForFacts=true")
        for label in ("qualityEvidencePath", "qualityReportPath", "renderEvidencePath", "contactSheetPath", "fontReportPath"):
            validate_generated_path(row.get(label), label, errors, line)
        status = row.get("extractionStatus")
        if status not in (None, "") and str(status) not in INVENTORY_STATUS_VALUES:
            errors.append(f"{kind} line {line}: invalid extractionStatus {status!r}")
        for object_field in ("ocrStatus", "speechToTextStatus", "sourceInventoryRecord"):
            value = row.get(object_field)
            if value is not None and not isinstance(value, dict):
                errors.append(f"{kind} line {line}: {object_field} must be an object when present")
        for array_field in ("transcriptSegments", "exactSearchTerms", "exactSearchHits"):
            value = row.get(array_field)
            if value is not None and not isinstance(value, list):
                errors.append(f"{kind} line {line}: {array_field} must be an array when present")
        for number_field in ("timestampStart", "timestampEnd", "confidence"):
            value = row.get(number_field)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"{kind} line {line}: {number_field} must be a number when present")
        if kind == "chunk":
            content = str(row.get("content", ""))
            if row.get("contentHash") and sha_text(content) != str(row.get("contentHash")):
                errors.append(f"chunk line {line}: contentHash mismatch")
            if row.get("charCount") != len(content):
                errors.append(f"chunk line {line}: charCount mismatch")
            for pointer_key in ("pageNumber", "slideNumber"):
                value = row.get(pointer_key)
                if value is not None and not isinstance(value, int):
                    errors.append(f"chunk line {line}: {pointer_key} must be an integer or null")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    errors: list[str] = []
    manifest_rows = read_jsonl(Path(args.manifest)) if args.manifest else []
    chunk_rows = read_jsonl(Path(args.chunks)) if args.chunks else []
    if args.manifest:
        errors += validate_rows(manifest_rows, MANIFEST_REQUIRED, "manifest")
    if args.chunks:
        errors += validate_rows(chunk_rows, CHUNK_REQUIRED, "chunk")
    report = {"ok": not errors, "manifestRows": len(manifest_rows), "chunkRows": len(chunk_rows), "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def cmd_inventory_to_handoff(args: argparse.Namespace) -> int:
    out_root = Path(args.output_root or HANDOFF_ROOT)
    inventory_path = Path(args.inventory)
    text_index_path = Path(args.text_index) if args.text_index else None
    inventory_rows = read_jsonl(inventory_path)
    text_rows = read_jsonl(text_index_path) if text_index_path else []
    manifest_path = out_root / "manifests" / f"{args.run_id}.source_inventory.jsonl"
    chunks_path = out_root / "normalized_chunks" / f"{args.run_id}.inventory.chunks.jsonl"
    by_pointer = {str(row.get("canonicalPointer") or ""): row for row in text_rows}
    manifest: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    for row in inventory_rows:
        status = str(row.get("extractionStatus") or "")
        document_id = args.document_id or stable_doc_id(row.get("sourcePath"), "inventory-document")
        usable = status in {"indexed_full", "indexed_partial"} and row.get("recordType") == "source_inventory"
        meta = inventory_metadata(row, inventory_path)
        manifest_row = {
            "schemaVersion": "1",
            "runId": args.run_id,
            "taskScope": args.task_scope,
            "artifactType": "source_inventory",
            "documentId": document_id,
            "sourcePath": row.get("sourcePath") or "",
            "sourceAbsolutePath": row.get("sourceAbsolutePath") or "",
            "sourceSha256": row.get("sourceSha256") or "0" * 64,
            "producedPath": rel_or_abs(inventory_path),
            "producedSha256": sha_file(inventory_path),
            "extractionMethod": "source_inventory",
            "authorityStatus": "source",
            "usableForFacts": bool(usable),
            "manualReviewPromoted": False,
            "createdAt": now(),
            "notes": args.notes,
        }
        manifest_row.update(meta)
        manifest.append(manifest_row)
    for row in text_rows:
        content = str(row.get("content") or "")
        if not content:
            continue
        content_hash = str(row.get("contentHash") or sha_text(content))
        source_path = str(row.get("sourcePath") or "")
        pointer = str(row.get("canonicalPointer") or source_path)
        matching_inventory = next(
            (
                item for item in inventory_rows
                if str(item.get("sourcePath") or "") == source_path
                and (not row.get("containerPath") or item.get("containerPath") == row.get("containerPath"))
            ),
            {},
        )
        document_id = args.document_id or stable_doc_id(source_path, "inventory-document")
        section = str(row.get("sectionId") or pointer.rsplit("#", 1)[-1] or "inventory-text")
        meta = inventory_metadata(matching_inventory or row, inventory_path)
        chunk = {
            "schemaVersion": "1",
            "chunkId": sha_text("|".join([document_id, pointer, content_hash])),
            "documentId": document_id,
            "sourcePath": source_path,
            "sourceAbsolutePath": row.get("sourceAbsolutePath") or matching_inventory.get("sourceAbsolutePath") or source_path,
            "sourceSha256": row.get("sourceSha256") or matching_inventory.get("sourceSha256") or "0" * 64,
            "sectionId": section,
            "canonicalPointer": pointer,
            "heading": row.get("heading"),
            "pageNumber": row.get("pageNumber"),
            "slideNumber": row.get("slideNumber"),
            "sheetName": row.get("sheetName"),
            "cellRange": row.get("cellRange"),
            "content": content,
            "contentHash": content_hash,
            "contentSnippet": row.get("contentSnippet") or content[:300],
            "charCount": len(content),
            "extractionMethod": "source_inventory",
            "authorityStatus": row.get("authorityStatus") or "source",
            "usableForFacts": bool(row.get("usableForFacts", True)),
            "manualReviewPromoted": False,
            "handoffManifestPath": rel_or_abs(manifest_path),
        }
        chunk.update(meta)
        # Preserve exact-search hits from the extracted text row, which are
        # usually more precise than file-level inventory hits.
        for key in ("exactSearchTerms", "exactSearchHits"):
            if key in row:
                chunk[key] = row.get(key)
        chunks.append(chunk)
    write_jsonl(manifest_path, manifest)
    write_jsonl(chunks_path, chunks)
    print(json.dumps({"ok": True, "manifestPath": str(manifest_path), "chunksPath": str(chunks_path), "manifestRows": len(manifest), "chunkRows": len(chunks), "textIndexRows": len(text_rows)}, ensure_ascii=False, indent=2))
    return 0


def cmd_to_vector_manifest(args: argparse.Namespace) -> int:
    rows = read_jsonl(Path(args.chunks))
    out: list[dict[str, Any]] = []
    metadata_fields = [
        "sourceSha256",
        "extractionMethod",
        "authorityStatus",
        "usableForFacts",
        "manualReviewPromoted",
        "qualityEvidencePath",
        "qualityReportPath",
        "renderEvidencePath",
        "contactSheetPath",
        "fontReportPath",
        "conversionChain",
        "evidencePurpose",
        "factBoundaryNote",
        "pageNumber",
        "slideNumber",
        "sheetName",
        "cellRange",
    ]
    metadata_fields.extend(INVENTORY_EXTRA_FIELDS)
    for row in rows:
        usable = bool(row.get("usableForFacts"))
        if not usable and not args.include_unusable:
            continue
        source_path = str(row.get("sourcePath") or "").strip()
        section_id = str(row.get("sectionId") or "").strip()
        canonical_pointer = str(row.get("canonicalPointer") or "").strip()
        content = str(row.get("content") or "").strip()
        vector_id = sha_text("\n".join([source_path, section_id, canonical_pointer, content]))
        out.append({
            "id": vector_id, "handoffChunkId": row.get("chunkId"), "status": "accepted" if usable else "skipped",
            "skipReason": "" if usable else "not_usable_for_facts",
            "sourceQmdFile": row.get("handoffManifestPath") or "document_knowledge_handoff",
            "sourcePath": source_path, "sourceAbsolutePath": row.get("sourceAbsolutePath"),
            "sectionId": section_id, "canonicalPointer": canonical_pointer,
            "heading": row.get("heading") or "", "roleTags": ["document_knowledge_handoff"],
            "keywords": [str(row.get("extractionMethod") or ""), str(row.get("authorityStatus") or "")],
            "contentHash": row.get("contentHash"), "charCount": row.get("charCount"),
            "content": row.get("content"), "contentSnippet": row.get("contentSnippet"),
        })
        for field in metadata_fields:
            if field in row:
                out[-1][field] = row.get(field)
    output = Path(args.output)
    write_jsonl(output, out)
    print(json.dumps({"ok": True, "output": str(output), "rows": len(out), "sourceRows": len(rows)}, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="Create handoff runtime directories.")
    p.add_argument("--output-root")
    p.set_defaults(func=cmd_init)
    p = sub.add_parser("chunk-text", help="Build handoff manifest and normalized chunks from an extracted text file.")
    p.add_argument("--source", required=True); p.add_argument("--text", required=True)
    p.add_argument("--run-id", required=True); p.add_argument("--document-id", required=True)
    p.add_argument("--task-scope", default="substantive_tender_generation", choices=["substantive_tender_generation", "substantive_governance_material_generation"])
    p.add_argument("--extraction-method", default="manual_transcription", choices=["source_native_text", "source_inventory", "word_com", "poppler_text", "acrobat_ocr", "pdf_to_docx", "pdf_to_xlsx", "pdf_to_pptx", "manual_transcription"])
    p.add_argument("--authority-status", default="converted", choices=["source", "converted", "ocr_reconstructed", "pdf_reconstructed", "draft", "quality_evidence"])
    p.add_argument("--usable-for-facts", action="store_true")
    p.add_argument("--manual-review-promoted", action="store_true")
    p.add_argument("--output-root"); p.add_argument("--source-path"); p.add_argument("--section-id"); p.add_argument("--canonical-pointer"); p.add_argument("--heading"); p.add_argument("--page-number", type=int); p.add_argument("--slide-number", type=int); p.add_argument("--sheet-name"); p.add_argument("--cell-range"); p.add_argument("--quality-evidence-path"); p.add_argument("--quality-report-path"); p.add_argument("--render-evidence-path"); p.add_argument("--contact-sheet-path"); p.add_argument("--font-report-path"); p.add_argument("--conversion-chain-json"); p.add_argument("--evidence-purpose", choices=["factual_source_text", "converted_text", "reconstructed_text", "layout_rendering_only", "generated_draft"]); p.add_argument("--fact-boundary-note"); p.add_argument("--notes")
    p.add_argument("--chunk-chars", type=int, default=1600); p.add_argument("--overlap", type=int, default=200)
    p.set_defaults(func=cmd_chunk_text)
    p = sub.add_parser("validate", help="Validate handoff manifest and/or normalized chunks.")
    p.add_argument("--manifest"); p.add_argument("--chunks")
    p.set_defaults(func=cmd_validate)
    p = sub.add_parser("to-vector-manifest", help="Convert normalized chunks to the QMD-compatible manifest used by local_vector_db_mirror_ingest.py.")
    p.add_argument("--chunks", required=True); p.add_argument("--output", required=True); p.add_argument("--include-unusable", action="store_true")
    p.set_defaults(func=cmd_to_vector_manifest)
    p = sub.add_parser("inventory-to-handoff", help="Convert source inventory JSONL and optional text-index JSONL to handoff manifest/chunks.")
    p.add_argument("--inventory", required=True)
    p.add_argument("--text-index")
    p.add_argument("--run-id", required=True)
    p.add_argument("--document-id")
    p.add_argument("--task-scope", default="substantive_tender_generation", choices=["substantive_tender_generation", "substantive_governance_material_generation"])
    p.add_argument("--output-root")
    p.add_argument("--notes")
    p.set_defaults(func=cmd_inventory_to_handoff)
    args = parser.parse_args(argv)
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
