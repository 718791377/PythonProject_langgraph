#!/usr/bin/env python3
"""Inventory tender source files and produce coverage-aware exact-search evidence.

The tool is intentionally read-only for supplied source roots. It inventories
files, safely extracts bounded text from formats that can be parsed without
executing code, writes runtime outputs outside protected source folders, and
keeps unsupported or multimodal files visible in coverage reports.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path.cwd()
CANONICAL_ROOT = Path.cwd()
CONFIG_ROOT = PROJECT_ROOT / "config" / "document_knowledge_handoff"
DEFAULT_REGISTRY = CONFIG_ROOT / "extractor_registry.json"
PROTECTED_NAMES = ("current_progress", "regulations", "requirement")
STATUS_VALUES = {
    "indexed_full",
    "indexed_partial",
    "ocr_required",
    "speech_to_text_required",
    "encrypted",
    "unsupported",
    "failed",
    "skipped_by_policy",
    "metadata_only",
}
INDEXED_STATUSES = {"indexed_full", "indexed_partial"}
TEXTISH_FAMILIES = {"text_config_log_web", "structured_data_database", "code_notebook"}
OOXML_EXTENSIONS = {".docx", ".docm", ".dotx", ".dotm", ".pptx", ".pptm", ".ppsx", ".potx", ".potm", ".xlsx", ".xlsm", ".xltx", ".xltm"}
ZIP_EXTENSIONS = {".zip"}
OOXML_EMBEDDED_PREFIXES = (
    "word/embeddings/",
    "word/media/",
    "ppt/embeddings/",
    "ppt/media/",
    "xl/embeddings/",
    "xl/media/",
)


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    ensure_output_safe(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_output_safe(path)
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
                raise ValueError(f"{path}:{line_no}: JSONL row must be an object")
            rows.append(value)
    return rows


def protected_dirs() -> list[Path]:
    roots = [PROJECT_ROOT]
    if CANONICAL_ROOT not in roots:
        roots.append(CANONICAL_ROOT)
    return [(root / name).resolve(strict=False) for root in roots for name in PROTECTED_NAMES]


def is_under(path: Path, parent: Path) -> bool:
    child = os.path.normcase(str(path.resolve(strict=False)))
    base = os.path.normcase(str(parent.resolve(strict=False)))
    return child == base or child.startswith(base + os.sep)


def ensure_output_safe(path: Path) -> None:
    for protected in protected_dirs():
        if is_under(path, protected):
            raise ValueError(f"Refusing to write under protected source directory: {path}")


def rel_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(root.resolve(strict=False))).replace("\\", "/")
    except ValueError:
        return path.name


def project_rel_or_abs(path: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(PROJECT_ROOT.resolve(strict=False))).replace("\\", "/")
    except ValueError:
        return str(path.resolve(strict=False))


def load_registry(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    registry = read_json(path)
    by_ext: dict[str, dict[str, Any]] = {}
    fallback: dict[str, Any] | None = None
    for extractor in registry.get("extractors", []):
        if not isinstance(extractor, dict):
            continue
        if extractor.get("extractorId") == "unknown_unsupported":
            fallback = extractor
        for ext in extractor.get("extensions", []):
            by_ext[str(ext).lower()] = extractor
    if fallback is None:
        fallback = {
            "extractorId": "unknown_unsupported",
            "extractorName": "Unknown unsupported format inventory",
            "extractorVersion": "1",
            "formatFamily": "unknown",
            "modality": "unknown",
            "defaultExtractionStatus": "unsupported",
            "safeToExecute": False,
        }
    return registry, by_ext, fallback


def classify(path: Path, by_ext: dict[str, dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    ext = path.suffix.lower()
    return by_ext.get(ext, fallback)


def mime_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def decode_text(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\x00", " ")).strip()


def text_snippet(value: str, limit: int = 300) -> str:
    value = compact_text(value)
    if len(value) <= limit:
        return value
    return value[:limit] + "..."


def xml_text_from_bytes(data: bytes) -> str:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return ""
    parts: list[str] = []
    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1] if isinstance(elem.tag, str) else ""
        if tag in {"t", "instrText"} and elem.text:
            parts.append(elem.text)
        for attr in ("title", "descr", "name"):
            if elem.attrib.get(attr):
                parts.append(str(elem.attrib[attr]))
    return compact_text(" ".join(parts))


def natural_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def extract_docx_text(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    wanted_prefixes = (
        "word/document.xml",
        "word/header",
        "word/footer",
        "word/footnotes",
        "word/endnotes",
        "word/comments",
    )
    with zipfile.ZipFile(path) as zf:
        names = sorted([name for name in zf.namelist() if name.startswith(wanted_prefixes)], key=natural_key)
        parts: list[str] = []
        for name in names:
            parts.append(xml_text_from_bytes(zf.read(name)))
        text = compact_text(" ".join(part for part in parts if part))
        if text:
            rows.append({"canonicalPointer": f"{project_rel_or_abs(path)}#document", "content": text})
    return rows


def extract_pptx_text(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    slide_re = re.compile(r"ppt/slides/slide(\d+)\.xml$")
    notes_re = re.compile(r"ppt/notesSlides/notesSlide(\d+)\.xml$")
    with zipfile.ZipFile(path) as zf:
        names = sorted(zf.namelist(), key=natural_key)
        for name in names:
            match = slide_re.match(name) or notes_re.match(name)
            if not match:
                continue
            number = int(match.group(1))
            text = xml_text_from_bytes(zf.read(name))
            if text:
                rows.append(
                    {
                        "canonicalPointer": f"{project_rel_or_abs(path)}#slide-{number}",
                        "slideNumber": number,
                        "content": text,
                    }
                )
        chart_names = [name for name in names if name.startswith("ppt/charts/") and name.endswith(".xml")]
        chart_text = compact_text(" ".join(xml_text_from_bytes(zf.read(name)) for name in chart_names))
        if chart_text:
            rows.append({"canonicalPointer": f"{project_rel_or_abs(path)}#charts", "content": chart_text})
    return rows


def extract_xlsx_text(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        names = sorted(zf.namelist(), key=natural_key)
        parts: list[str] = []
        for name in names:
            if name == "xl/sharedStrings.xml" or (name.startswith("xl/worksheets/") and name.endswith(".xml")):
                text = xml_text_from_bytes(zf.read(name))
                if text:
                    parts.append(text)
        text = compact_text(" ".join(parts))
        if text:
            rows.append({"canonicalPointer": f"{project_rel_or_abs(path)}#workbook", "content": text})
    return rows


def extract_ipynb_text(path: Path, max_text_bytes: int) -> list[dict[str, Any]]:
    raw = path.read_bytes()[:max_text_bytes]
    data = json.loads(decode_text(raw))
    rows: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return rows
    for index, cell in enumerate(data.get("cells", []), 1):
        if not isinstance(cell, dict):
            continue
        source = cell.get("source", "")
        if isinstance(source, list):
            content = "".join(str(item) for item in source)
        else:
            content = str(source)
        content = compact_text(content)
        if content:
            rows.append(
                {
                    "canonicalPointer": f"{project_rel_or_abs(path)}#cell-{index}",
                    "content": content,
                    "cellRange": f"cell-{index}",
                }
            )
    return rows


def extract_plain_text(path: Path, max_text_bytes: int) -> tuple[list[dict[str, Any]], bool]:
    data = path.read_bytes()
    partial = len(data) > max_text_bytes
    text = decode_text(data[:max_text_bytes])
    text = compact_text(text)
    if not text:
        return [], partial
    return [{"canonicalPointer": f"{project_rel_or_abs(path)}#text", "content": text}], partial


def extract_text_rows(path: Path, extractor: dict[str, Any], max_text_bytes: int) -> tuple[list[dict[str, Any]], str | None, str | None]:
    ext = path.suffix.lower()
    family = str(extractor.get("formatFamily") or "unknown")
    try:
        if ext in {".docx", ".docm", ".dotx", ".dotm"}:
            return extract_docx_text(path), "indexed_partial", None
        if ext in {".pptx", ".pptm", ".ppsx", ".potx", ".potm"}:
            return extract_pptx_text(path), "indexed_partial", None
        if ext in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
            return extract_xlsx_text(path), "indexed_partial", None
        if ext == ".ipynb":
            return extract_ipynb_text(path, max_text_bytes), "indexed_partial", None
        if family in TEXTISH_FAMILIES:
            rows, partial = extract_plain_text(path, max_text_bytes)
            return rows, "indexed_partial" if partial else "indexed_full", None
    except (OSError, UnicodeError, zipfile.BadZipFile, json.JSONDecodeError, ET.ParseError) as exc:
        return [], "failed", str(exc)
    return [], None, None


def default_ocr_status(status: str, family: str) -> dict[str, Any]:
    if status == "ocr_required" or family == "image":
        return {"required": True, "status": "required", "confidence": None, "manualReviewStatus": "not_reviewed"}
    if family == "pdf":
        return {"required": False, "status": "not_assessed", "confidence": None, "manualReviewStatus": "not_reviewed"}
    return {"required": False, "status": "not_required", "confidence": None, "manualReviewStatus": "not_reviewed"}


def default_speech_status(status: str, family: str) -> dict[str, Any]:
    if status == "speech_to_text_required" or family in {"audio", "video"}:
        return {"required": True, "status": "required", "confidence": None, "speakerLabels": None}
    return {"required": False, "status": "not_required", "confidence": None, "speakerLabels": None}


def make_text_index_rows(
    *,
    run_id: str,
    file_record: dict[str, Any],
    extracted_rows: list[dict[str, Any]],
    terms: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, item in enumerate(extracted_rows, 1):
        content = str(item.get("content") or "")
        content_hash = sha_text(content)
        hits = term_hits(terms, content, item.get("canonicalPointer"))
        out.append(
            {
                "schemaVersion": "1",
                "recordType": "source_text_index",
                "runId": run_id,
                "sourcePath": file_record["sourcePath"],
                "sourceAbsolutePath": file_record["sourceAbsolutePath"],
                "sourceSha256": file_record["sourceSha256"],
                "formatFamily": file_record["formatFamily"],
                "modality": file_record["modality"],
                "extractorId": file_record["extractorId"],
                "extractionStatus": file_record["extractionStatus"],
                "canonicalPointer": item.get("canonicalPointer") or f"{file_record['sourcePath']}#text-{idx}",
                "pageNumber": item.get("pageNumber"),
                "slideNumber": item.get("slideNumber"),
                "sheetName": item.get("sheetName"),
                "cellRange": item.get("cellRange"),
                "containerPath": file_record.get("containerPath"),
                "content": content,
                "contentHash": content_hash,
                "contentSnippet": text_snippet(content),
                "charCount": len(content),
                "authorityStatus": "source",
                "usableForFacts": file_record["extractionStatus"] in INDEXED_STATUSES,
                "exactSearchTerms": terms,
                "exactSearchHits": hits,
            }
        )
    return out


def term_hits(terms: list[str], content: str, canonical_pointer: Any = None) -> list[dict[str, Any]]:
    folded = content.casefold()
    hits: list[dict[str, Any]] = []
    for term in terms:
        if not term:
            continue
        pos = folded.find(term.casefold())
        if pos < 0:
            continue
        start = max(0, pos - 80)
        end = min(len(content), pos + len(term) + 80)
        hits.append(
            {
                "term": term,
                "canonicalPointer": str(canonical_pointer or ""),
                "contentSnippet": text_snippet(content[start:end], 220),
            }
        )
    return hits


def zip_entry_records(
    *,
    run_id: str,
    path: Path,
    root: Path,
    source_hash: str,
    by_ext: dict[str, dict[str, Any]],
    fallback: dict[str, Any],
    max_entries: int,
    max_entry_bytes: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if path.suffix.lower() not in ZIP_EXTENSIONS:
        return records
    try:
        with zipfile.ZipFile(path) as zf:
            entries = [info for info in zf.infolist() if not info.is_dir()]
            limit_reached = len(entries) > max_entries
            for info in entries[:max_entries]:
                entry_ext = Path(info.filename).suffix.lower()
                extractor = by_ext.get(entry_ext, fallback)
                encrypted = bool(info.flag_bits & 0x1)
                status = "encrypted" if encrypted else str(extractor.get("defaultExtractionStatus") or "metadata_only")
                if info.file_size > max_entry_bytes and status in INDEXED_STATUSES:
                    status = "skipped_by_policy"
                entry_hash = None
                if not encrypted and info.file_size <= max_entry_bytes:
                    try:
                        entry_hash = sha_bytes(zf.read(info))
                    except RuntimeError:
                        status = "encrypted"
                record = base_record(
                    run_id=run_id,
                    root=root,
                    path=path,
                    source_hash=source_hash,
                    extractor=extractor,
                    status=status,
                    error=None,
                    record_type="source_container_entry",
                    container_path=f"zip://{project_rel_or_abs(path)}!/{info.filename}",
                    container_depth=1,
                    relative_path=f"{rel_to_root(path, root)}!/{info.filename}",
                    size_bytes=int(info.file_size),
                    entry_sha256=entry_hash,
                )
                record["archiveRecursionStatus"] = "listed"
                if limit_reached:
                    record["extractionStatusReason"] = "archive entry list truncated by max_entries"
                records.append(record)
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        records.append(
            base_record(
                run_id=run_id,
                root=root,
                path=path,
                source_hash=source_hash,
                extractor=by_ext.get(path.suffix.lower(), fallback),
                status="failed",
                error=str(exc),
                record_type="source_container_entry",
                container_path=f"zip://{project_rel_or_abs(path)}",
                container_depth=1,
                relative_path=rel_to_root(path, root),
                size_bytes=0,
                entry_sha256=None,
            )
        )
    return records


def container_child_record(
    *,
    run_id: str,
    root: Path,
    path: Path,
    source_hash: str,
    filename: str,
    size_bytes: int,
    entry_bytes: bytes | None,
    container_scheme: str,
    by_ext: dict[str, dict[str, Any]],
    fallback: dict[str, Any],
    max_entry_bytes: int,
    reason: str | None = None,
) -> dict[str, Any]:
    extractor = by_ext.get(Path(filename).suffix.lower(), fallback)
    status = str(extractor.get("defaultExtractionStatus") or "metadata_only")
    if size_bytes > max_entry_bytes and status in INDEXED_STATUSES:
        status = "skipped_by_policy"
        reason = reason or "container entry exceeded max entry byte limit"
    entry_hash = sha_bytes(entry_bytes) if entry_bytes is not None and size_bytes <= max_entry_bytes else None
    record = base_record(
        run_id=run_id,
        root=root,
        path=path,
        source_hash=source_hash,
        extractor=extractor,
        status=status,
        error=reason,
        record_type="source_container_entry",
        container_path=f"{container_scheme}://{project_rel_or_abs(path)}!/{filename}",
        container_depth=1,
        relative_path=f"{rel_to_root(path, root)}!/{filename}",
        size_bytes=size_bytes,
        entry_sha256=entry_hash,
    )
    record["extension"] = Path(filename).suffix.lower()
    record["mimeType"] = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    record["archiveRecursionStatus"] = "listed"
    return record


def ooxml_embedded_records(
    *,
    run_id: str,
    path: Path,
    root: Path,
    source_hash: str,
    by_ext: dict[str, dict[str, Any]],
    fallback: dict[str, Any],
    max_entries: int,
    max_entry_bytes: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if path.suffix.lower() not in OOXML_EXTENSIONS:
        return records
    try:
        with zipfile.ZipFile(path) as zf:
            entries = [
                info for info in zf.infolist()
                if not info.is_dir() and any(info.filename.startswith(prefix) for prefix in OOXML_EMBEDDED_PREFIXES)
            ]
            for info in entries[:max_entries]:
                entry_bytes = None
                if info.file_size <= max_entry_bytes:
                    entry_bytes = zf.read(info)
                records.append(
                    container_child_record(
                        run_id=run_id,
                        root=root,
                        path=path,
                        source_hash=source_hash,
                        filename=info.filename,
                        size_bytes=int(info.file_size),
                        entry_bytes=entry_bytes,
                        container_scheme="ooxml",
                        by_ext=by_ext,
                        fallback=fallback,
                        max_entry_bytes=max_entry_bytes,
                    )
                )
            if len(entries) > max_entries:
                records.append(
                    base_record(
                        run_id=run_id,
                        root=root,
                        path=path,
                        source_hash=source_hash,
                        extractor=by_ext.get(path.suffix.lower(), fallback),
                        status="skipped_by_policy",
                        error="OOXML embedded-object listing truncated by max_entries",
                        record_type="source_container_entry",
                        container_path=f"ooxml://{project_rel_or_abs(path)}!/...",
                        container_depth=1,
                        relative_path=f"{rel_to_root(path, root)}!/...",
                        size_bytes=0,
                        entry_sha256=None,
                    )
                )
    except (OSError, zipfile.BadZipFile, RuntimeError):
        return records
    return records


def eml_records_and_text(
    *,
    run_id: str,
    path: Path,
    root: Path,
    source_hash: str,
    by_ext: dict[str, dict[str, Any]],
    fallback: dict[str, Any],
    max_entries: int,
    max_entry_bytes: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    try:
        msg = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    except Exception as exc:  # noqa: BLE001 - inventory should report bad email files, not crash.
        return [], [], str(exc)
    subject = str(msg.get("subject") or "")
    sender = str(msg.get("from") or "")
    recipients = str(msg.get("to") or "")
    body = msg.get_body(preferencelist=("plain",))
    content = "\n".join(part for part in [subject, sender, recipients, body.get_content() if body else ""] if part).strip()
    text_rows = []
    if content:
        text_rows.append({"canonicalPointer": f"{project_rel_or_abs(path)}#email-body", "content": content})
    children: list[dict[str, Any]] = []
    attachments = [part for part in msg.walk() if part.get_filename()]
    for part in attachments[:max_entries]:
        filename = part.get_filename() or "attachment.bin"
        payload = part.get_payload(decode=True) or b""
        children.append(
            container_child_record(
                run_id=run_id,
                root=root,
                path=path,
                source_hash=source_hash,
                filename=filename,
                size_bytes=len(payload),
                entry_bytes=payload if len(payload) <= max_entry_bytes else None,
                container_scheme="eml",
                by_ext=by_ext,
                fallback=fallback,
                max_entry_bytes=max_entry_bytes,
            )
        )
    if len(attachments) > max_entries:
        children.append(
            base_record(
                run_id=run_id,
                root=root,
                path=path,
                source_hash=source_hash,
                extractor=by_ext.get(".eml", fallback),
                status="skipped_by_policy",
                error="email attachment listing truncated by max_entries",
                record_type="source_container_entry",
                container_path=f"eml://{project_rel_or_abs(path)}!/...",
                container_depth=1,
                relative_path=f"{rel_to_root(path, root)}!/...",
                size_bytes=0,
                entry_sha256=None,
            )
        )
    return children, text_rows, None


def base_record(
    *,
    run_id: str,
    root: Path,
    path: Path,
    source_hash: str,
    extractor: dict[str, Any],
    status: str,
    error: str | None,
    record_type: str = "source_inventory",
    container_path: str | None = None,
    container_depth: int = 0,
    relative_path: str | None = None,
    size_bytes: int | None = None,
    entry_sha256: str | None = None,
) -> dict[str, Any]:
    family = str(extractor.get("formatFamily") or "unknown")
    record = {
        "schemaVersion": "1",
        "recordType": record_type,
        "runId": run_id,
        "sourceRoot": str(root.resolve(strict=False)),
        "relativePath": relative_path or rel_to_root(path, root),
        "sourcePath": project_rel_or_abs(path),
        "sourceAbsolutePath": str(path.resolve(strict=False)),
        "extension": path.suffix.lower(),
        "mimeType": mime_type(path),
        "typeGuess": str(extractor.get("extractorName") or ""),
        "sizeBytes": int(size_bytes if size_bytes is not None else path.stat().st_size),
        "sourceSha256": source_hash,
        "containerPath": container_path,
        "containerDepth": container_depth,
        "entrySha256": entry_sha256,
        "formatFamily": family,
        "modality": str(extractor.get("modality") or "unknown"),
        "extractorId": str(extractor.get("extractorId") or "unknown_unsupported"),
        "extractorName": str(extractor.get("extractorName") or ""),
        "extractorVersion": str(extractor.get("extractorVersion") or "1"),
        "extractionStatus": status,
        "extractionStatusReason": error,
        "archiveRecursionStatus": "not_container",
        "ocrStatus": default_ocr_status(status, family),
        "speechToTextStatus": default_speech_status(status, family),
        "safeToExecute": bool(extractor.get("safeToExecute", False)),
        "contentPath": None,
        "contentHash": None,
        "contentSnippet": None,
        "exactSearchTerms": [],
        "exactSearchHits": [],
        "error": error,
        "createdAt": iso_now(),
    }
    if family == "archive_container":
        record["archiveRecursionStatus"] = "not_attempted"
    return record


def inventory_file(
    *,
    run_id: str,
    root: Path,
    path: Path,
    by_ext: dict[str, dict[str, Any]],
    fallback: dict[str, Any],
    terms: list[str],
    max_text_bytes: int,
    max_archive_entries: int,
    max_archive_entry_bytes: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    text_rows: list[dict[str, Any]] = []
    extractor = classify(path, by_ext, fallback)
    try:
        source_hash = sha_file(path)
    except OSError as exc:
        source_hash = "0" * 64
        record = base_record(run_id=run_id, root=root, path=path, source_hash=source_hash, extractor=extractor, status="failed", error=str(exc))
        records.append(record)
        return records, text_rows

    default_status = str(extractor.get("defaultExtractionStatus") or "metadata_only")
    extracted, extracted_status, error = extract_text_rows(path, extractor, max_text_bytes)
    nested_records: list[dict[str, Any]] = []
    if path.suffix.lower() == ".eml":
        nested_records, email_text_rows, email_error = eml_records_and_text(
            run_id=run_id,
            path=path,
            root=root,
            source_hash=source_hash,
            by_ext=by_ext,
            fallback=fallback,
            max_entries=max_archive_entries,
            max_entry_bytes=max_archive_entry_bytes,
        )
        if email_text_rows:
            extracted = email_text_rows
            extracted_status = "indexed_partial"
        if email_error:
            error = email_error
            extracted_status = "failed"
    status = extracted_status or default_status
    if status not in STATUS_VALUES:
        status = "unsupported"
    record = base_record(run_id=run_id, root=root, path=path, source_hash=source_hash, extractor=extractor, status=status, error=error)
    if extracted:
        combined = "\n".join(str(row.get("content") or "") for row in extracted)
        record["contentHash"] = sha_text(combined)
        record["contentSnippet"] = text_snippet(combined)
        record["exactSearchTerms"] = terms
        record["exactSearchHits"] = term_hits(terms, combined, record["sourcePath"])
        text_rows.extend(make_text_index_rows(run_id=run_id, file_record=record, extracted_rows=extracted, terms=terms))
    if path.suffix.lower() in ZIP_EXTENSIONS:
        nested = zip_entry_records(
            run_id=run_id,
            path=path,
            root=root,
            source_hash=source_hash,
            by_ext=by_ext,
            fallback=fallback,
            max_entries=max_archive_entries,
            max_entry_bytes=max_archive_entry_bytes,
        )
        record["archiveRecursionStatus"] = "listed" if nested else "failed"
        records.extend(nested)
    if path.suffix.lower() in OOXML_EXTENSIONS:
        embedded = ooxml_embedded_records(
            run_id=run_id,
            path=path,
            root=root,
            source_hash=source_hash,
            by_ext=by_ext,
            fallback=fallback,
            max_entries=max_archive_entries,
            max_entry_bytes=max_archive_entry_bytes,
        )
        if embedded:
            record["archiveRecursionStatus"] = "listed"
            records.extend(embedded)
    if path.suffix.lower() == ".pdf":
        try:
            head = path.read_bytes()[:5_000_000]
        except OSError:
            head = b""
        if b"/EmbeddedFiles" in head or b"/Collection" in head:
            record["archiveRecursionStatus"] = "unsupported"
            record["extractionStatusReason"] = "PDF portfolio or embedded file markers detected; nested extraction requires an explicit PDF portfolio extractor."
    if nested_records:
        record["archiveRecursionStatus"] = "listed"
        records.extend(nested_records)
    records.insert(0, record)
    return records, text_rows


def make_coverage(records: list[dict[str, Any]], text_rows: list[dict[str, Any]], terms: list[str]) -> dict[str, Any]:
    by_root = Counter(str(row.get("sourceRoot") or "") for row in records)
    by_ext = Counter(str(row.get("extension") or "") for row in records)
    by_family = Counter(str(row.get("formatFamily") or "") for row in records)
    by_modality = Counter(str(row.get("modality") or "") for row in records)
    by_extractor = Counter(str(row.get("extractorId") or "") for row in records)
    by_status = Counter(str(row.get("extractionStatus") or "") for row in records)
    by_archive = Counter(str(row.get("archiveRecursionStatus") or "") for row in records)
    by_ocr = Counter(str((row.get("ocrStatus") or {}).get("status") or "") for row in records)
    by_speech = Counter(str((row.get("speechToTextStatus") or {}).get("status") or "") for row in records)
    incomplete = {key: value for key, value in by_status.items() if key not in INDEXED_STATUSES and value}
    hits_by_term: dict[str, list[dict[str, Any]]] = {term: [] for term in terms}
    for row in text_rows:
        content = str(row.get("content") or "")
        for hit in term_hits(terms, content, row.get("canonicalPointer")):
            enriched = dict(hit)
            enriched.update(
                {
                    "sourcePath": row.get("sourcePath"),
                    "sourceSha256": row.get("sourceSha256"),
                    "slideNumber": row.get("slideNumber"),
                    "sheetName": row.get("sheetName"),
                    "cellRange": row.get("cellRange"),
                    "extractionStatus": row.get("extractionStatus"),
                    "formatFamily": row.get("formatFamily"),
                    "modality": row.get("modality"),
                }
            )
            hits_by_term[hit["term"]].append(enriched)
    negative: dict[str, str] = {}
    for term in terms:
        if hits_by_term.get(term):
            continue
        if incomplete:
            negative[term] = (
                "Not found in successfully indexed content, but source coverage is incomplete "
                f"({', '.join(f'{k}={v}' for k, v in sorted(incomplete.items()))}); "
                "this is not a complete negative conclusion."
            )
        else:
            negative[term] = "Not found in indexed content; all inventoried records were indexed_full or indexed_partial."
    return {
        "schemaVersion": "1",
        "createdAt": iso_now(),
        "recordCount": len(records),
        "textIndexRowCount": len(text_rows),
        "countsByRoot": dict(sorted(by_root.items())),
        "countsByExtension": dict(sorted(by_ext.items())),
        "countsByFormatFamily": dict(sorted(by_family.items())),
        "countsByModality": dict(sorted(by_modality.items())),
        "countsByExtractor": dict(sorted(by_extractor.items())),
        "countsByArchiveRecursionStatus": dict(sorted(by_archive.items())),
        "countsByOcrStatus": dict(sorted(by_ocr.items())),
        "countsBySpeechToTextStatus": dict(sorted(by_speech.items())),
        "countsByExtractionStatus": dict(sorted(by_status.items())),
        "incompleteCoverageCounts": dict(sorted(incomplete.items())),
        "exactSearchTerms": terms,
        "exactSearchHits": hits_by_term,
        "boundedNegativeResultWording": negative,
    }


def write_coverage_md(path: Path, coverage: dict[str, Any]) -> None:
    ensure_output_safe(path)
    lines = ["# Source Inventory Coverage Report", ""]
    lines.append(f"- Created at: {coverage['createdAt']}")
    lines.append(f"- Inventory records: {coverage['recordCount']}")
    lines.append(f"- Text index rows: {coverage['textIndexRowCount']}")
    for title, key in [
        ("Extraction status", "countsByExtractionStatus"),
        ("Format family", "countsByFormatFamily"),
        ("Modality", "countsByModality"),
        ("Extension", "countsByExtension"),
        ("Extractor", "countsByExtractor"),
        ("Archive recursion status", "countsByArchiveRecursionStatus"),
        ("OCR status", "countsByOcrStatus"),
        ("Speech-to-text status", "countsBySpeechToTextStatus"),
    ]:
        lines.extend(["", f"## {title}", ""])
        counts = coverage.get(key, {})
        if not counts:
            lines.append("- (none)")
        for name, count in counts.items():
            lines.append(f"- `{name or '<none>'}`: {count}")
    lines.extend(["", "## Exact-search terms", ""])
    for term in coverage.get("exactSearchTerms", []):
        hits = coverage.get("exactSearchHits", {}).get(term, [])
        lines.append(f"- `{term}`: {len(hits)} hit(s)")
        for hit in hits[:10]:
            lines.append(f"  - {hit.get('sourcePath')} :: {hit.get('canonicalPointer')} :: {hit.get('contentSnippet')}")
        notice = coverage.get("boundedNegativeResultWording", {}).get(term)
        if notice:
            lines.append(f"  - Coverage notice: {notice}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_inventory(args: argparse.Namespace) -> int:
    registry, by_ext, fallback = load_registry(Path(args.registry))
    terms = args.term or []
    output = Path(args.output)
    text_output = Path(args.text_index_output) if args.text_index_output else None
    if not args.root and not args.path:
        raise SystemExit("at least one --root or --path is required")
    roots = [Path(item).resolve(strict=False) for item in args.root]
    explicit_paths = [Path(item).resolve(strict=False) for item in args.path]
    records: list[dict[str, Any]] = []
    text_rows: list[dict[str, Any]] = []
    scanned = 0
    for path in explicit_paths:
        if not path.exists() or not path.is_file():
            raise SystemExit(f"source path does not exist or is not a file: {path}")
        root = path.parent.resolve(strict=False)
        file_records, file_text_rows = inventory_file(
            run_id=args.run_id,
            root=root,
            path=path,
            by_ext=by_ext,
            fallback=fallback,
            terms=terms,
            max_text_bytes=args.max_text_bytes,
            max_archive_entries=args.max_archive_entries,
            max_archive_entry_bytes=args.max_archive_entry_bytes,
        )
        records.extend(file_records)
        text_rows.extend(file_text_rows)
    for root in roots:
        if not root.exists():
            raise SystemExit(f"source root does not exist: {root}")
        for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: str(p).lower()):
            scanned += 1
            if args.max_files and scanned > args.max_files:
                break
            file_records, file_text_rows = inventory_file(
                run_id=args.run_id,
                root=root,
                path=path,
                by_ext=by_ext,
                fallback=fallback,
                terms=terms,
                max_text_bytes=args.max_text_bytes,
                max_archive_entries=args.max_archive_entries,
                max_archive_entry_bytes=args.max_archive_entry_bytes,
            )
            records.extend(file_records)
            text_rows.extend(file_text_rows)
        if args.max_files and scanned > args.max_files:
            break
    write_jsonl(output, records)
    if text_output:
        write_jsonl(text_output, text_rows)
    coverage = make_coverage(records, text_rows, terms)
    if args.coverage_json:
        write_json(Path(args.coverage_json), coverage)
    if args.coverage_md:
        write_coverage_md(Path(args.coverage_md), coverage)
    print(
        json.dumps(
            {
                "ok": True,
                "registryId": registry.get("registryId"),
                "output": str(output),
                "textIndexOutput": str(text_output) if text_output else None,
                "records": len(records),
                "textIndexRows": len(text_rows),
                "coverageJson": args.coverage_json,
                "coverageMd": args.coverage_md,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_exact_search(args: argparse.Namespace) -> int:
    inventory_rows = read_jsonl(Path(args.inventory))
    text_rows = read_jsonl(Path(args.text_index)) if args.text_index else []
    terms = args.term or []
    coverage = make_coverage(inventory_rows, text_rows, terms)
    payload = {
        "ok": True,
        "terms": terms,
        "hits": coverage["exactSearchHits"],
        "boundedNegativeResultWording": coverage["boundedNegativeResultWording"],
        "incompleteCoverageCounts": coverage["incompleteCoverageCounts"],
    }
    if args.output:
        write_json(Path(args.output), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def validate_inventory_rows(rows: list[dict[str, Any]]) -> list[str]:
    required = [
        "schemaVersion",
        "recordType",
        "runId",
        "sourceRoot",
        "relativePath",
        "sourcePath",
        "sourceAbsolutePath",
        "extension",
        "mimeType",
        "sizeBytes",
        "sourceSha256",
        "containerPath",
        "formatFamily",
        "modality",
        "extractorId",
        "extractionStatus",
        "createdAt",
    ]
    errors: list[str] = []
    for idx, row in enumerate(rows, 1):
        for key in required:
            if key not in row:
                errors.append(f"line {idx}: missing {key}")
        status = str(row.get("extractionStatus") or "")
        if status not in STATUS_VALUES:
            errors.append(f"line {idx}: invalid extractionStatus {status!r}")
        sha = str(row.get("sourceSha256") or "")
        if not re.match(r"^[0-9a-fA-F]{64}$", sha):
            errors.append(f"line {idx}: sourceSha256 is not sha256 hex")
        for protected in protected_dirs():
            for output_key in ("contentPath",):
                value = row.get(output_key)
                if value and is_under(Path(str(value)), protected):
                    errors.append(f"line {idx}: {output_key} targets protected source directory")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    rows = read_jsonl(Path(args.inventory))
    errors = validate_inventory_rows(rows)
    payload = {"ok": not errors, "rows": len(rows), "errors": errors}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory", help="Inventory one or more source roots and write JSONL/coverage outputs.")
    p.add_argument("--root", action="append", default=[], help="Source root to scan. Repeatable.")
    p.add_argument("--path", action="append", default=[], help="Single source file to inventory. Repeatable.")
    p.add_argument("--output", required=True, help="Inventory JSONL output path.")
    p.add_argument("--text-index-output", help="Optional extracted text JSONL output path.")
    p.add_argument("--coverage-json", help="Optional coverage JSON output path.")
    p.add_argument("--coverage-md", help="Optional coverage Markdown output path.")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Extractor registry path.")
    p.add_argument("--run-id", default="source-inventory-" + time.strftime("%Y%m%d%H%M%S"))
    p.add_argument("--term", action="append", default=[], help="Exact-search regression term. Repeatable.")
    p.add_argument("--max-files", type=int, default=0, help="Stop after this many filesystem files; 0 means no limit.")
    p.add_argument("--max-text-bytes", type=int, default=2_000_000)
    p.add_argument("--max-archive-entries", type=int, default=200)
    p.add_argument("--max-archive-entry-bytes", type=int, default=5_000_000)
    p.set_defaults(func=cmd_inventory)
    p = sub.add_parser("exact-search", help="Run exact search over inventory text-index rows.")
    p.add_argument("--inventory", required=True)
    p.add_argument("--text-index")
    p.add_argument("--term", action="append", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_exact_search)
    p = sub.add_parser("validate", help="Validate required source-inventory fields.")
    p.add_argument("--inventory", required=True)
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
