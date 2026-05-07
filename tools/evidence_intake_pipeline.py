#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PDF_SUFFIX = ".pdf"
HTML_SUFFIXES = {".html", ".htm"}
TEXT_SUFFIXES = {".py", ".ps1", ".cmd", ".bat", ".md", ".txt", ".json", ".yaml", ".yml"}
DEFAULT_OCR_LANGUAGES = "eng+chi_sim"
DEFAULT_RENDER_DPI = 144
CANDIDATE_TERMS = re.compile(
    r"pdf|html|ocr|extract|tesseract|poppler|pdftotext|pypdf|pymupdf|fitz|docx|xlsx|beautifulsoup|readability|lxml|vector|embedding",
    re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def flush_manifest(output: Path, manifest: dict[str, Any]) -> None:
    manifest["counts"] = summarize_counts(manifest.get("records", []))
    manifest["updated_at"] = utc_now()
    write_json(output / "manifest.json", manifest)
    write_summary(output / "summary.md", manifest)


def command_path(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=utf8_env(),
    )


def utf8_env() -> dict[str, str]:
    import os

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LANG", "C.UTF-8")
    return env


def as_output_rel(path: Path | None, output_dir: Path) -> str | None:
    return rel(path, output_dir) if path else None


def text_metrics(text: str) -> dict[str, Any]:
    chars = len(text)
    replacement_chars = text.count("\ufffd")
    control_chars = sum(1 for ch in text if ord(ch) < 32 and ch not in "\n\r\t")
    cjk_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    latin_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    whitespace_chars = sum(1 for ch in text if ch.isspace())
    suspicious_fragments = len(re.findall(r"[A-Za-z]\s[A-Za-z]\s[A-Za-z]|[\u00c0-\u00ff]{3,}", text))
    noise_units = replacement_chars * 5 + control_chars * 3 + suspicious_fragments
    noise_ratio = min(1.0, noise_units / max(chars, 1))
    if chars < 20:
        quality = "empty-or-tiny"
    elif noise_ratio >= 0.08:
        quality = "noisy"
    elif replacement_chars or suspicious_fragments > max(20, chars // 500):
        quality = "needs-review"
    else:
        quality = "usable"
    return {
        "chars": chars,
        "replacement_chars": replacement_chars,
        "control_chars": control_chars,
        "cjk_chars": cjk_chars,
        "latin_chars": latin_chars,
        "whitespace_chars": whitespace_chars,
        "suspicious_fragments": suspicious_fragments,
        "noise_ratio": round(noise_ratio, 6),
        "quality": quality,
        "needs_review": quality != "usable",
    }


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.parts: list[str] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs if key and value}
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
        if tag == "title":
            self.title_depth += 1
        if tag == "meta":
            name = (
                attr_map.get("name")
                or attr_map.get("property")
                or attr_map.get("itemprop")
                or attr_map.get("http-equiv")
            )
            content = attr_map.get("content")
            if name and content:
                self.meta[name.strip().lower()] = content.strip()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self.title_depth:
            self.title_parts.append(cleaned)
        if not self.skip_depth:
            self.parts.append(cleaned)

    @property
    def visible_text(self) -> str:
        return "\n".join(self.parts)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()


def likely_date(text: str) -> str | None:
    match = re.search(r"(20\d{2}[-/.年]\s*\d{1,2}[-/.月]\s*\d{1,2}\s*日?)", text)
    return match.group(1).strip() if match else None


def html_metadata(parser: VisibleTextParser, text: str) -> dict[str, Any]:
    meta = parser.meta
    return {
        "title": parser.title or meta.get("og:title"),
        "author": meta.get("author") or meta.get("article:author") or meta.get("byl"),
        "date": (
            meta.get("article:published_time")
            or meta.get("publishdate")
            or meta.get("date")
            or meta.get("pubdate")
            or likely_date(text)
        ),
    }


def is_saved_page_asset(path: Path, source_root: Path) -> bool:
    try:
        relative_parts = path.resolve().relative_to(source_root.resolve()).parts
    except Exception:
        relative_parts = path.parts
    return any(part.endswith("_files") for part in relative_parts[:-1])


def extract_html_file(path: Path, output_dir: Path, source_root: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    html = raw.decode("utf-8-sig", errors="replace")
    parser = VisibleTextParser()
    parser.feed(html)
    text = parser.visible_text
    slug = safe_slug(rel(path, source_root).replace("/", "__"))
    out_path = output_dir / "html_articles" / f"{slug}.txt"
    write_text(out_path, text)
    metrics = text_metrics(text)
    metadata = html_metadata(parser, text)
    return {
        "type": "html",
        "source_path": rel(path, source_root),
        "source_name": path.name,
        "source_display": safe_display(path.name),
        "title": metadata.get("title") or path.stem,
        "author": metadata.get("author"),
        "date": metadata.get("date"),
        "method": "python-htmlparser-visible-text",
        "output_path": rel(out_path, output_dir),
        "extracted_text_kind": "visible-text-not-yet-human-verified",
        **metrics,
    }


def safe_slug(value: str) -> str:
    value = value.strip().replace("\\", "/")
    value = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value[:120] or "item"


def safe_display(value: str | None) -> str | None:
    if value is None:
        return None
    encoded = value.encode("ascii", errors="backslashreplace").decode("ascii")
    return encoded.replace("`", "'")


def pdf_page_count(pdfinfo: str | None, path: Path) -> int | None:
    if not pdfinfo:
        return None
    result = run([pdfinfo, str(path)])
    if result.returncode != 0:
        return None
    match = re.search(r"^Pages:\s*(\d+)\s*$", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def extract_pdf_page(pdftotext: str, path: Path, page: int, out_path: Path) -> tuple[str, str | None]:
    if out_path.exists():
        try:
            return out_path.read_text(encoding="utf-8", errors="replace"), None
        except OSError:
            pass
    temp_path = out_path.with_suffix(".tmp.txt")
    result = run([pdftotext, "-f", str(page), "-l", str(page), "-layout", "-enc", "UTF-8", str(path), str(temp_path)])
    if result.returncode != 0:
        return "", result.stderr.strip() or result.stdout.strip() or f"pdftotext failed for page {page}"
    try:
        text = temp_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return "", repr(exc)
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
    write_text(out_path, text)
    return text, None


def extract_pdf_pages_whole_doc(
    pdftotext: str,
    path: Path,
    output_dir: Path,
    pdf_slug: str,
    limit: int,
) -> dict[int, tuple[str, str | None]]:
    text_dir = output_dir / "pdf_pages" / pdf_slug
    cached: dict[int, tuple[str, str | None]] = {}
    missing_pages: list[int] = []
    for page in range(1, limit + 1):
        out_path = text_dir / f"page-{page:04d}.txt"
        if out_path.exists():
            try:
                cached[page] = (out_path.read_text(encoding="utf-8", errors="replace"), None)
                continue
            except OSError:
                pass
        missing_pages.append(page)

    if not missing_pages:
        return cached

    temp_path = output_dir / ".tmp" / f"{pdf_slug}.whole.txt"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    result = run([pdftotext, "-layout", "-enc", "UTF-8", str(path), str(temp_path)])
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "whole-document pdftotext failed"
        return {page: cached.get(page, ("", error)) for page in range(1, limit + 1)}
    try:
        raw = temp_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {page: cached.get(page, ("", repr(exc))) for page in range(1, limit + 1)}
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass

    parts = raw.split("\f")
    for page in range(1, limit + 1):
        if page in cached:
            continue
        out_path = text_dir / f"page-{page:04d}.txt"
        if page <= len(parts):
            text = parts[page - 1]
            write_text(out_path, text)
            cached[page] = (text, None)
        else:
            cached[page] = ("", f"whole-document pdftotext did not include page {page}")
    return cached


def render_pdf_page(
    pdftoppm: str,
    path: Path,
    page: int,
    out_path: Path,
    dpi: int,
) -> str | None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0:
        return None
    base_path = out_path.with_suffix("")
    result = run(
        [
            pdftoppm,
            "-r",
            str(dpi),
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-png",
            str(path),
            str(base_path),
        ]
    )
    if result.returncode != 0:
        return result.stderr.strip() or result.stdout.strip() or f"pdftoppm failed for page {page}"
    if not out_path.exists():
        return f"pdftoppm did not create expected image: {out_path}"
    return None


def parse_tesseract_confidence(tsv: str) -> float | None:
    lines = [line for line in tsv.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    header = lines[0].split("\t")
    try:
        conf_index = header.index("conf")
    except ValueError:
        return None
    values: list[float] = []
    for line in lines[1:]:
        cols = line.split("\t")
        if conf_index >= len(cols):
            continue
        try:
            value = float(cols[conf_index])
        except ValueError:
            continue
        if value >= 0:
            values.append(value)
    return round(sum(values) / len(values), 3) if values else None


def ocr_image_page(tesseract: str, image_path: Path, text_out_path: Path, languages: str) -> dict[str, Any]:
    text_result = run([tesseract, str(image_path), "stdout", "-l", languages, "--psm", "3"])
    if text_result.returncode != 0:
        return {
            "ocr_error": text_result.stderr.strip() or text_result.stdout.strip() or "tesseract text OCR failed",
            "ocr_average_confidence": None,
        }
    write_text(text_out_path, text_result.stdout)
    tsv_result = run([tesseract, str(image_path), "stdout", "-l", languages, "--psm", "3", "tsv"])
    confidence = parse_tesseract_confidence(tsv_result.stdout) if tsv_result.returncode == 0 else None
    return {
        "ocr_output_path": text_out_path,
        "ocr_average_confidence": confidence,
        "ocr_metrics": text_metrics(text_result.stdout),
    }


def extract_pdf_file(
    path: Path,
    output_dir: Path,
    source_root: Path,
    max_pages: int | None = None,
    render_pages: bool = False,
    ocr_pages: bool = False,
    ocr_languages: str = DEFAULT_OCR_LANGUAGES,
    render_dpi: int = DEFAULT_RENDER_DPI,
) -> dict[str, Any]:
    pdftotext = command_path("pdftotext", "pdftotext.exe")
    pdfinfo_cmd = command_path("pdfinfo", "pdfinfo.exe")
    pdftoppm = command_path("pdftoppm", "pdftoppm.exe")
    tesseract = command_path("tesseract", "tesseract.exe")
    record: dict[str, Any] = {
        "type": "pdf",
        "source_path": rel(path, source_root),
        "source_name": path.name,
        "source_display": safe_display(path.name),
        "method": "pdftotext-page-range-with-optional-render-ocr" if pdftotext else "missing-pdf-text-extractor",
        "pages": [],
        "errors": [],
        "render_requested": render_pages,
        "ocr_requested": ocr_pages,
        "ocr_languages": ocr_languages if ocr_pages else None,
    }
    pages = pdf_page_count(pdfinfo_cmd, path) if pdfinfo_cmd else None
    total_pages = pages
    record["page_count"] = pages
    if not pdftotext:
        record["needs_ocr"] = True
        record["errors"].append("pdftotext not found; PDF requires OCR or another extractor.")
        return record
    if pages is None:
        pages = 1
        record["errors"].append("pdfinfo page count unavailable; extracted first page only.")
    limit = min(pages, max_pages) if max_pages else pages
    record["extraction_complete"] = total_pages is not None and limit >= total_pages
    record["extraction_limit"] = max_pages
    pdf_slug = safe_slug(path.stem)
    low_quality = 0
    rendered = 0
    ocr_completed = 0
    page_texts: dict[int, tuple[str, str | None]] | None = None
    if not render_pages and not ocr_pages:
        page_texts = extract_pdf_pages_whole_doc(pdftotext, path, output_dir, pdf_slug, limit)
    for page in range(1, limit + 1):
        out_path = output_dir / "pdf_pages" / pdf_slug / f"page-{page:04d}.txt"
        if page_texts is not None:
            text, error = page_texts.get(page, ("", f"missing extracted page {page}"))
        else:
            text, error = extract_pdf_page(pdftotext, path, page, out_path)
        metrics = text_metrics(text)
        page_record = {
            "page_number": page,
            "method": "pdftotext-page-range",
            "output_path": rel(out_path, output_dir),
            "text_output_path": rel(out_path, output_dir),
            **metrics,
        }
        image_path = output_dir / "pdf_images" / pdf_slug / f"page-{page:04d}.png"
        if render_pages or ocr_pages:
            if pdftoppm:
                render_error = render_pdf_page(pdftoppm, path, page, image_path, render_dpi)
                if render_error:
                    page_record["render_error"] = render_error
                    page_record["needs_review"] = True
                    record["errors"].append(render_error)
                else:
                    rendered += 1
                    page_record["render_method"] = f"pdftoppm-png-{render_dpi}dpi"
                    page_record["render_output_path"] = rel(image_path, output_dir)
            else:
                page_record["render_error"] = "pdftoppm not found; page image was not rendered."
                page_record["needs_review"] = True
        if ocr_pages:
            if not page_record.get("render_output_path"):
                page_record["ocr_error"] = "OCR requested but no page image is available."
            elif not tesseract:
                page_record["ocr_error"] = "tesseract not found; OCR text and confidence were not produced."
            else:
                ocr_path = output_dir / "pdf_ocr" / pdf_slug / f"page-{page:04d}.ocr.txt"
                ocr_record = ocr_image_page(tesseract, image_path, ocr_path, ocr_languages)
                if "ocr_output_path" in ocr_record:
                    ocr_completed += 1
                    ocr_record["ocr_output_path"] = rel(ocr_record["ocr_output_path"], output_dir)
                page_record.update(ocr_record)
        if error:
            page_record["error"] = error
            page_record["needs_review"] = True
            record["errors"].append(error)
        if page_record["needs_review"]:
            low_quality += 1
        record["pages"].append(page_record)
    record["extracted_pages"] = len(record["pages"])
    record["rendered_pages"] = rendered
    record["ocr_completed_pages"] = ocr_completed
    record["low_quality_pages"] = low_quality
    record["needs_ocr"] = bool(low_quality)
    return record


def extract_references(
    root: Path,
    source: Path,
    output: Path,
    max_pages: int | None,
    render_pages: bool = False,
    ocr_pages: bool = False,
    ocr_languages: str = DEFAULT_OCR_LANGUAGES,
    render_dpi: int = DEFAULT_RENDER_DPI,
) -> dict[str, Any]:
    source_root = (root / source if not source.is_absolute() else source).resolve()
    output = output.resolve()
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "source_root": str(source_root),
        "output_root": str(output),
        "records": [],
        "tools": {
            "pdftotext": command_path("pdftotext", "pdftotext.exe"),
            "pdfinfo": command_path("pdfinfo", "pdfinfo.exe"),
            "pdftoppm": command_path("pdftoppm", "pdftoppm.exe"),
            "tesseract": command_path("tesseract", "tesseract.exe"),
        },
        "warnings": [],
        "errors": [],
    }
    if not source_root.exists():
        manifest["errors"].append(f"Source root does not exist: {source_root}")
        flush_manifest(output, manifest)
        return manifest
    pdfs = sorted(source_root.rglob("*.pdf"))
    if max_pages == 0:
        pdfs = []
    htmls = sorted(
        [
            p
            for suffix in HTML_SUFFIXES
            for p in source_root.rglob(f"*{suffix}")
            if not is_saved_page_asset(p, source_root)
        ]
    )
    for pdf in pdfs:
        manifest["records"].append(
            extract_pdf_file(
                pdf,
                output,
                source_root,
                max_pages=max_pages,
                render_pages=render_pages,
                ocr_pages=ocr_pages,
                ocr_languages=ocr_languages,
                render_dpi=render_dpi,
            )
        )
        flush_manifest(output, manifest)
    for html in htmls:
        manifest["records"].append(extract_html_file(html, output, source_root))
        flush_manifest(output, manifest)
    flush_manifest(output, manifest)
    return manifest


def summarize_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    pdfs = [r for r in records if r.get("type") == "pdf"]
    htmls = [r for r in records if r.get("type") == "html"]
    return {
        "records": len(records),
        "pdfs": len(pdfs),
        "htmls": len(htmls),
        "pdf_pages": sum(len(r.get("pages", [])) for r in pdfs),
        "partial_pdfs": sum(1 for r in pdfs if not r.get("extraction_complete")),
        "rendered_pdf_pages": sum(int(r.get("rendered_pages", 0)) for r in pdfs),
        "ocr_completed_pdf_pages": sum(int(r.get("ocr_completed_pages", 0)) for r in pdfs),
        "low_quality_pdf_pages": sum(int(r.get("low_quality_pages", 0)) for r in pdfs),
        "html_needs_review": sum(1 for r in htmls if r.get("needs_review")),
    }


def write_summary(path: Path, manifest: dict[str, Any]) -> None:
    counts = manifest.get("counts", summarize_counts(manifest.get("records", [])))
    lines = [
        "# Evidence Intake Pipeline Summary",
        "",
        f"Generated: {manifest.get('generated_at')}",
        f"Source root: `{manifest.get('source_root')}`",
        f"Output root: `{manifest.get('output_root')}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in counts.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Tool Availability", ""])
    for key, value in manifest.get("tools", {}).items():
        lines.append(f"- `{key}`: {value or 'not found'}")
    lines.extend(["", "## Review Notes", ""])
    for record in manifest.get("records", []):
        source_label = record.get("source_display") or safe_display(record.get("source_path")) or "unknown-source"
        if record.get("type") == "pdf" and record.get("low_quality_pages"):
            lines.append(
                f"- `{source_label}` has {record.get('low_quality_pages')} low-quality extracted pages; use OCR, second-pass extraction, or human review before strong claims."
            )
        if record.get("type") == "pdf" and not record.get("extraction_complete"):
            lines.append(
                f"- `{source_label}` extraction is partial: {record.get('extracted_pages', 0)} of {record.get('page_count') or 'unknown'} pages were processed."
            )
        if record.get("type") == "pdf" and record.get("ocr_requested") and not record.get("ocr_completed_pages"):
            lines.append(
                f"- `{source_label}` requested OCR but no OCR page text was completed; check `tesseract` availability and language data."
            )
        if record.get("type") == "html" and record.get("needs_review"):
            lines.append(
                f"- `{source_label}` extracted text needs review before it is treated as verified article body."
            )
    if lines and lines[-1] == "## Review Notes":
        lines.append("No review warnings detected.")
    write_text(path, "\n".join(lines) + "\n")


def classify_candidate(path: Path, root: Path) -> dict[str, Any]:
    lowered = path.as_posix().lower()
    suffix = path.suffix.lower()
    if "__pycache__" in lowered or "pydeps" in lowered or "pip-" in lowered or "site-packages" in lowered:
        kind = "cached-dependency"
        recommendation = "do-not-copy"
    elif any(part in lowered for part in ["intermediate/", "result/", ".tmp/", ".project-runtime/"]):
        kind = "generated-or-project-artifact"
        recommendation = "project-specific-only"
    elif suffix in {".exe", ".dll"}:
        kind = "third-party-binary"
        recommendation = "third-party-install-instead"
    elif suffix in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
        kind = "document-or-reference-artifact"
        recommendation = "project-specific-only"
    elif suffix in TEXT_SUFFIXES:
        kind = "source-or-config"
        recommendation = "consider-adapter"
    else:
        kind = "other"
        recommendation = "review-manually"
    return {
        "path": rel(path, root),
        "suffix": suffix,
        "size": path.stat().st_size if path.exists() else None,
        "kind": kind,
        "recommendation": recommendation,
    }


def should_skip_inventory_path(path: Path, root: Path) -> bool:
    lowered = rel(path, root).lower()
    skip_markers = [
        "/.git/",
        "/.idea/",
        "/.venv/",
        "/__pycache__/",
        "/node_modules/",
        "/python_packages/",
        "/site-packages/",
        "/pip-",
        ".pyc",
    ]
    normalized = "/" + lowered.replace("\\", "/")
    return any(marker in normalized for marker in skip_markers)


def inventory_walk_roots(root: Path) -> list[Path]:
    preferred = [root / "tools", root / "scripts", root / "config"]
    ordered = [path for path in preferred if path.exists()]
    ordered.append(root)
    return ordered


def inventory_tools(root: Path, output: Path, limit: int = 500) -> dict[str, Any]:
    root = root.resolve()
    records: list[dict[str, Any]] = []
    seen: set[Path] = set()
    if root.exists():
        for walk_root in inventory_walk_roots(root):
            for path in walk_root.rglob("*"):
                if not path.is_file():
                    continue
                resolved = path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                if should_skip_inventory_path(path, root):
                    continue
                rel_path = rel(path, root)
                if CANDIDATE_TERMS.search(rel_path):
                    records.append(classify_candidate(path, root))
                if len(records) >= limit:
                    break
            if len(records) >= limit:
                break
    payload = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "root": str(root),
        "records": records,
        "counts": {
            "records": len(records),
            "consider_adapter": sum(1 for r in records if r["recommendation"] == "consider-adapter"),
            "third_party_install_instead": sum(1 for r in records if r["recommendation"] == "third-party-install-instead"),
            "do_not_copy": sum(1 for r in records if r["recommendation"] == "do-not-copy"),
            "project_specific_only": sum(1 for r in records if r["recommendation"] == "project-specific-only"),
        },
    }
    write_json(output, payload)
    return payload


def check_output(output: Path) -> dict[str, Any]:
    output = output.resolve()
    errors: list[str] = []
    manifest_path = output / "manifest.json"
    if not manifest_path.exists():
        errors.append(f"Missing manifest: {manifest_path}")
        manifest = {}
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid manifest JSON: {exc}")
            manifest = {}
    if manifest and manifest.get("schema_version") != 1:
        errors.append("manifest.json schema_version must be 1")
    if manifest and not isinstance(manifest.get("records"), list):
        errors.append("manifest.json records must be a list")
    summary_path = output / "summary.md"
    if not summary_path.exists():
        errors.append(f"Missing summary: {summary_path}")
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": "evidence_intake_output",
        "ok": not errors,
        "output": str(output),
        "errors": errors,
        "counts": {
            "errors": len(errors),
            "records": len(manifest.get("records", [])) if isinstance(manifest, dict) else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract local reference evidence and inventory external tool candidates.")
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="Extract ignored local PDF/HTML evidence.")
    extract.add_argument("--root", default=".", help="Repository root.")
    extract.add_argument("--source", default="local_reference", help="Local reference source directory, relative to root unless absolute.")
    extract.add_argument("--output", default=".local/evidence/local_reference", help="Ignored local output directory.")
    extract.add_argument("--max-pages", type=int, default=None, help="Optional page limit per PDF for smoke runs.")
    extract.add_argument("--render-pages", action="store_true", help="Render each extracted PDF page to PNG evidence when pdftoppm is available.")
    extract.add_argument("--ocr-pages", action="store_true", help="Run OCR for rendered PDF pages when tesseract is available.")
    extract.add_argument("--ocr-languages", default=DEFAULT_OCR_LANGUAGES, help="Tesseract OCR language list, for example eng+chi_sim.")
    extract.add_argument("--render-dpi", type=int, default=DEFAULT_RENDER_DPI, help="DPI for optional PDF page PNG rendering.")
    extract.add_argument("--json", action="store_true", help="Print JSON payload.")

    inv = sub.add_parser("inventory-tools", help="Inventory external local tool candidates without copying.")
    inv.add_argument("--root", required=True, help="External project root to inspect.")
    inv.add_argument("--output", required=True, help="Inventory JSON output path.")
    inv.add_argument("--limit", type=int, default=500, help="Maximum candidate records.")
    inv.add_argument("--json", action="store_true", help="Print JSON payload.")

    check = sub.add_parser("check", help="Validate an existing evidence output directory.")
    check.add_argument("--output", default=".local/evidence/local_reference", help="Evidence output directory.")
    check.add_argument("--json", action="store_true", help="Print JSON payload.")

    args = parser.parse_args()
    exit_code = 1
    if args.command == "extract":
        root = Path(args.root).resolve()
        output = root / args.output if not Path(args.output).is_absolute() else Path(args.output)
        payload = extract_references(
            root,
            Path(args.source),
            output,
            args.max_pages,
            render_pages=args.render_pages,
            ocr_pages=args.ocr_pages,
            ocr_languages=args.ocr_languages,
            render_dpi=args.render_dpi,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Extracted {payload.get('counts', {}).get('records', 0)} reference records to {payload.get('output_root')}.")
        exit_code = 0 if not payload.get("errors") else 1
    elif args.command == "inventory-tools":
        payload = inventory_tools(Path(args.root), Path(args.output), limit=args.limit)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Inventoried {payload['counts']['records']} candidate tool records to {args.output}.")
        exit_code = 0
    elif args.command == "check":
        payload = check_output(Path(args.output))
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"evidence_intake_output: {'ok' if payload['ok'] else 'failed'}")
            for error in payload["errors"]:
                print(f"ERROR: {error}")
        exit_code = 0 if payload["ok"] else 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
