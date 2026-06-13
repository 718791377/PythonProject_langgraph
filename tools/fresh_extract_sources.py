#!/usr/bin/env python3
"""Fresh local source extraction evidence for lifecycle documentation refreshes.

This tool intentionally writes extraction outputs under a caller-provided local
ignored directory.  It is meant to prove that source files were freshly read
before updating tracked synthesis documents; tracked repository files should
cite only the manifest/report and compact aggregate facts, not raw extracted
book text.

Supported source units:
* PDF: one record per page.
* EPUB: one record per spine item.
* Markdown: one record per full document.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import logging
import os
import re
import sys
import traceback
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


SOURCE_DIRS = ("Business Management", "PMP")
SOURCE_SUFFIXES = {".pdf", ".epub", ".md", ".markdown"}


# Some local PDFs contain noisy cross-reference/object warnings.  The evidence
# we need is per-source/per-unit status in our manifest, not library stderr.
warnings.filterwarnings("ignore")
logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("fitz").setLevel(logging.ERROR)


KEYWORD_GROUPS: dict[str, list[str]] = {
    "strategy": [
        "strategy",
        "strategic",
        "vision",
        "north star",
        "positioning",
        "market",
        "chasm",
        "traction",
        "战略",
        "市场",
        "定位",
        "愿景",
    ],
    "product_discovery": [
        "discovery",
        "customer",
        "interview",
        "prototype",
        "experiment",
        "prd",
        "mvp",
        "产品",
        "客户",
        "访谈",
        "实验",
    ],
    "metrics_value": [
        "metric",
        "measure",
        "okr",
        "analytics",
        "value",
        "outcome",
        "benefit",
        "指标",
        "价值",
        "收益",
    ],
    "architecture_engineering": [
        "architecture",
        "design",
        "dependency",
        "database",
        "security",
        "reliability",
        "架构",
        "安全",
        "可靠",
    ],
    "operations_org": [
        "operation",
        "process",
        "team",
        "topolog",
        "management",
        "pmo",
        "governance",
        "运营",
        "流程",
        "团队",
        "治理",
    ],
    "pmi_delivery": [
        "project",
        "program",
        "portfolio",
        "process group",
        "initiating",
        "planning",
        "executing",
        "monitoring",
        "controlling",
        "closing",
        "tailor",
        "agile",
        "项目",
        "项目集",
        "项目组合",
        "过程组",
        "启动",
        "规划",
        "执行",
        "监控",
        "收尾",
        "裁剪",
        "敏捷",
    ],
}


TARGET_DOC_HINTS: dict[str, list[str]] = {
    "business_management_source_synthesis": [
        "strategy",
        "product_discovery",
        "metrics_value",
        "architecture_engineering",
        "operations_org",
        "pmi_delivery",
    ],
    "codex_platform_inventory_map": [
        "strategy",
        "product_discovery",
        "metrics_value",
        "architecture_engineering",
        "operations_org",
    ],
    "one_person_company_inventory_map": [
        "strategy",
        "product_discovery",
        "metrics_value",
        "operations_org",
    ],
    "pmi_project_management_reference_map": ["pmi_delivery", "metrics_value", "operations_org"],
    "lifecycle_tailoring_rules": ["pmi_delivery", "operations_org", "architecture_engineering"],
    "whitepaper_and_research_bridge": [
        "strategy",
        "architecture_engineering",
        "operations_org",
        "pmi_delivery",
    ],
    "north_star_plan": ["metrics_value", "strategy", "pmi_delivery"],
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_posix(path: Path) -> str:
    return path.as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def count_keywords(text: str) -> dict[str, int]:
    lower = text.lower()
    counts: dict[str, int] = {}
    for group, words in KEYWORD_GROUPS.items():
        total = 0
        for word in words:
            total += lower.count(word.lower())
        counts[group] = total
    return counts


def short_sample(text: str, limit: int = 240) -> str:
    """Return a short non-authoritative diagnostic snippet for local cache only."""

    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:limit]


@dataclass
class SourceRecord:
    source_id: str
    family: str
    path: Path
    relative_path: str
    format: str
    size_bytes: int
    mtime_utc: str
    sha256: str
    status: str = "pending"
    error: str = ""
    unit_count: int = 0
    extracted_chars: int = 0
    blank_units: int = 0
    low_text_units: int = 0
    tool_chain: list[str] = field(default_factory=list)
    fallback_count: int = 0
    encrypted: bool | None = None
    notes: list[str] = field(default_factory=list)
    keyword_counts: Counter[str] = field(default_factory=Counter)

    def manifest_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "family": self.family,
            "path": self.relative_path,
            "format": self.format,
            "size_bytes": self.size_bytes,
            "mtime_utc": self.mtime_utc,
            "sha256": self.sha256,
            "status": self.status,
            "error": self.error,
            "unit_count": self.unit_count,
            "extracted_chars": self.extracted_chars,
            "blank_units": self.blank_units,
            "low_text_units": self.low_text_units,
            "tool_chain": self.tool_chain,
            "fallback_count": self.fallback_count,
            "encrypted": self.encrypted,
            "notes": self.notes,
            "keyword_counts": dict(self.keyword_counts),
        }


def discover_sources(source_root: Path) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    ordinal = 0
    for family in SOURCE_DIRS:
        base = source_root / family
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            suffix = path.suffix.lower()
            if suffix not in SOURCE_SUFFIXES:
                continue
            ordinal += 1
            stat = path.stat()
            records.append(
                SourceRecord(
                    source_id=f"S{ordinal:04d}",
                    family=family,
                    path=path,
                    relative_path=as_posix(path.relative_to(source_root)),
                    format=suffix.lstrip(".").lower(),
                    size_bytes=stat.st_size,
                    mtime_utc=_dt.datetime.fromtimestamp(stat.st_mtime, _dt.UTC)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    sha256=sha256_file(path),
                )
            )
    return records


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_unit_stats(source: SourceRecord, text: str, low_text_threshold: int) -> dict[str, int]:
    text_len = len(text)
    source.unit_count += 1
    source.extracted_chars += text_len
    if text_len == 0:
        source.blank_units += 1
    if text_len < low_text_threshold:
        source.low_text_units += 1
    kc = Counter(count_keywords(text))
    source.keyword_counts.update(kc)
    return dict(kc)


def extract_pdf_with_pypdf(source: SourceRecord, items_fh: Any, args: argparse.Namespace) -> bool:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on environment
        source.notes.append(f"pypdf_unavailable:{type(exc).__name__}")
        return False

    try:
        reader = PdfReader(str(source.path))
        source.tool_chain.append("pypdf")
        source.encrypted = bool(getattr(reader, "is_encrypted", False))
        if source.encrypted:
            try:
                reader.decrypt("")
                source.notes.append("pypdf_empty_password_decrypt_attempted")
            except Exception as exc:
                source.notes.append(f"pypdf_decrypt_failed:{type(exc).__name__}")
        total_pages = len(reader.pages)
        if args.summary_only:
            source.unit_count = total_pages
            source.status = "ok"
            return True
        for index, page in enumerate(reader.pages, start=1):
            page_tool = "pypdf"
            status = "ok"
            error = ""
            text = ""
            try:
                text = normalize_text(page.extract_text())
            except Exception as exc:
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
            keyword_counts = add_unit_stats(source, text, args.low_text_threshold)
            record = {
                "source_id": source.source_id,
                "family": source.family,
                "path": source.relative_path,
                "format": "pdf",
                "unit_type": "page",
                "unit_index": index,
                "unit_total": total_pages,
                "status": status,
                "tool": page_tool,
                "error": error,
                "text_chars": len(text),
                "keyword_counts": keyword_counts,
                "sample": short_sample(text),
                "text": text,
            }
            items_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        source.status = "ok"
        return True
    except Exception as exc:
        source.error = f"pypdf_file_failed:{type(exc).__name__}: {exc}"
        source.notes.append(source.error)
        return False


def extract_pdf_with_fitz(source: SourceRecord, items_fh: Any, args: argparse.Namespace) -> bool:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on environment
        source.notes.append(f"fitz_unavailable:{type(exc).__name__}")
        return False

    try:
        doc = fitz.open(str(source.path))
        source.tool_chain.append("fitz")
        source.fallback_count += 1
        source.encrypted = bool(getattr(doc, "needs_pass", False))
        total_pages = doc.page_count
        if source.encrypted:
            try:
                doc.authenticate("")
                source.notes.append("fitz_empty_password_auth_attempted")
            except Exception as exc:
                source.notes.append(f"fitz_auth_failed:{type(exc).__name__}")
        if args.summary_only:
            source.unit_count = total_pages
            source.status = "ok"
            doc.close()
            return True
        for index in range(total_pages):
            status = "ok"
            error = ""
            text = ""
            try:
                page = doc.load_page(index)
                text = normalize_text(page.get_text("text"))
            except Exception as exc:
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
            keyword_counts = add_unit_stats(source, text, args.low_text_threshold)
            record = {
                "source_id": source.source_id,
                "family": source.family,
                "path": source.relative_path,
                "format": "pdf",
                "unit_type": "page",
                "unit_index": index + 1,
                "unit_total": total_pages,
                "status": status,
                "tool": "fitz",
                "error": error,
                "text_chars": len(text),
                "keyword_counts": keyword_counts,
                "sample": short_sample(text),
                "text": text,
            }
            items_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        doc.close()
        source.status = "ok"
        return True
    except Exception as exc:
        source.error = f"fitz_file_failed:{type(exc).__name__}: {exc}"
        source.notes.append(source.error)
        return False


def extract_pdf(source: SourceRecord, items_fh: Any, args: argparse.Namespace) -> None:
    if extract_pdf_with_pypdf(source, items_fh, args):
        return
    # Reset page counters from a failed file-level pypdf attempt before fallback.
    source.unit_count = 0
    source.extracted_chars = 0
    source.blank_units = 0
    source.low_text_units = 0
    source.keyword_counts = Counter()
    if extract_pdf_with_fitz(source, items_fh, args):
        return
    source.status = "error"


def extract_epub(source: SourceRecord, items_fh: Any, args: argparse.Namespace) -> None:
    try:
        from bs4 import BeautifulSoup  # type: ignore
        from ebooklib import epub  # type: ignore
        from ebooklib import ITEM_DOCUMENT  # type: ignore
    except Exception as exc:
        source.status = "error"
        source.error = f"epub_dependencies_unavailable:{type(exc).__name__}: {exc}"
        source.notes.append(source.error)
        return

    try:
        book = epub.read_epub(str(source.path))
        source.tool_chain.append("ebooklib+bs4")
        spine_entries = [entry for entry in book.spine if entry and entry[0] != "nav"]
        if args.summary_only:
            source.unit_count = len(spine_entries)
            source.status = "ok"
            return
        manifest_items = {item.get_id(): item for item in book.get_items_of_type(ITEM_DOCUMENT)}
        total = len(spine_entries)
        for index, entry in enumerate(spine_entries, start=1):
            item_id = entry[0]
            item = manifest_items.get(item_id)
            status = "ok"
            error = ""
            href = ""
            title = ""
            text = ""
            if item is None:
                status = "skipped"
                error = "spine_item_not_document"
            else:
                href = item.get_name()
                try:
                    soup = BeautifulSoup(item.get_content(), "lxml")
                    title_node = soup.find(["title", "h1", "h2"])
                    title = normalize_text(title_node.get_text(" ")) if title_node else ""
                    text = normalize_text(soup.get_text("\n"))
                except Exception as exc:
                    status = "error"
                    error = f"{type(exc).__name__}: {exc}"
            keyword_counts = add_unit_stats(source, text, args.low_text_threshold)
            record = {
                "source_id": source.source_id,
                "family": source.family,
                "path": source.relative_path,
                "format": "epub",
                "unit_type": "spine_item",
                "unit_index": index,
                "unit_total": total,
                "spine_id": item_id,
                "href": href,
                "title": title,
                "status": status,
                "tool": "ebooklib+bs4",
                "error": error,
                "text_chars": len(text),
                "keyword_counts": keyword_counts,
                "sample": short_sample(text),
                "text": text,
            }
            items_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        source.status = "ok"
    except Exception as exc:
        source.status = "error"
        source.error = f"epub_file_failed:{type(exc).__name__}: {exc}"
        source.notes.append(source.error)


def read_markdown_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8-replace"


def extract_markdown(source: SourceRecord, items_fh: Any, args: argparse.Namespace) -> None:
    source.tool_chain.append("python-read_text")
    try:
        if args.summary_only:
            text, encoding = read_markdown_text(source.path)
            source.unit_count = 1
            source.extracted_chars = len(text)
            source.blank_units = 1 if not text.strip() else 0
            source.low_text_units = 1 if len(text.strip()) < args.low_text_threshold else 0
            source.keyword_counts.update(count_keywords(text))
            source.notes.append(f"encoding:{encoding}")
            source.status = "ok"
            return
        raw, encoding = read_markdown_text(source.path)
        text = normalize_text(raw)
        source.notes.append(f"encoding:{encoding}")
        keyword_counts = add_unit_stats(source, text, args.low_text_threshold)
        record = {
            "source_id": source.source_id,
            "family": source.family,
            "path": source.relative_path,
            "format": "markdown",
            "unit_type": "full_document",
            "unit_index": 1,
            "unit_total": 1,
            "status": "ok",
            "tool": f"python-read_text:{encoding}",
            "error": "",
            "text_chars": len(text),
            "keyword_counts": keyword_counts,
            "sample": short_sample(text),
            "text": text,
        }
        items_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        source.status = "ok"
    except Exception as exc:
        source.status = "error"
        source.error = f"markdown_file_failed:{type(exc).__name__}: {exc}"
        source.notes.append(source.error)


def aggregate(records: Iterable[SourceRecord]) -> dict[str, Any]:
    records = list(records)
    by_family: dict[str, dict[str, Any]] = {}
    by_format: dict[str, dict[str, Any]] = {}
    keyword_totals: Counter[str] = Counter()
    target_scores: dict[str, Counter[str]] = {name: Counter() for name in TARGET_DOC_HINTS}

    def empty_bucket() -> dict[str, Any]:
        return {
            "source_count": 0,
            "unit_count": 0,
            "extracted_chars": 0,
            "blank_units": 0,
            "low_text_units": 0,
            "status_counts": Counter(),
            "format_counts": Counter(),
        }

    for rec in records:
        fam = by_family.setdefault(rec.family, empty_bucket())
        fmt = by_format.setdefault(rec.format, empty_bucket())
        for bucket in (fam, fmt):
            bucket["source_count"] += 1
            bucket["unit_count"] += rec.unit_count
            bucket["extracted_chars"] += rec.extracted_chars
            bucket["blank_units"] += rec.blank_units
            bucket["low_text_units"] += rec.low_text_units
            bucket["status_counts"][rec.status] += 1
            bucket["format_counts"][rec.format] += 1
        keyword_totals.update(rec.keyword_counts)
        for target, groups in TARGET_DOC_HINTS.items():
            for group in groups:
                if rec.keyword_counts.get(group, 0):
                    target_scores[target][rec.relative_path] += rec.keyword_counts[group]

    def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
        return {
            **{k: v for k, v in bucket.items() if k not in {"status_counts", "format_counts"}},
            "status_counts": dict(bucket["status_counts"]),
            "format_counts": dict(bucket["format_counts"]),
        }

    target_top_sources = {
        target: [{"path": path, "score": score} for path, score in scores.most_common(10)]
        for target, scores in target_scores.items()
    }

    return {
        "total_sources": len(records),
        "total_units": sum(r.unit_count for r in records),
        "total_extracted_chars": sum(r.extracted_chars for r in records),
        "blank_units": sum(r.blank_units for r in records),
        "low_text_units": sum(r.low_text_units for r in records),
        "status_counts": dict(Counter(r.status for r in records)),
        "by_family": {k: finalize_bucket(v) for k, v in sorted(by_family.items())},
        "by_format": {k: finalize_bucket(v) for k, v in sorted(by_format.items())},
        "keyword_totals": dict(keyword_totals),
        "target_doc_top_sources": target_top_sources,
    }


def render_report(
    *,
    run_id: str,
    generated_at: str,
    source_root: Path,
    output_root: Path,
    manifest: dict[str, Any],
    lang: str,
) -> str:
    zh = lang == "zh-CN"
    agg = manifest["aggregate"]
    title = "Fresh Source Extraction Report" if not zh else "Fresh Source Extraction 报告"
    lines = [f"# {title}", ""]
    if zh:
        lines += [
            f"- 运行 ID：`{run_id}`",
            f"- 生成时间：`{generated_at}`",
            f"- Source root：`{source_root}`",
            f"- Output root：`{output_root}`",
            f"- 说明：该报告只记录本地 fresh reading 证据。原文抽取 JSONL 位于忽略态缓存，不应提交到 Git。",
        ]
    else:
        lines += [
            f"- Run ID: `{run_id}`",
            f"- Generated at: `{generated_at}`",
            f"- Source root: `{source_root}`",
            f"- Output root: `{output_root}`",
            "- Note: this report records local fresh-reading evidence only. Raw extraction JSONL stays in ignored cache and should not be committed.",
        ]
    lines += ["", "## Coverage" if not zh else "## 覆盖范围", ""]
    lines += [
        "| Family | Sources | Units | Extracted chars | Blank units | Low-text units | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for family, bucket in agg["by_family"].items():
        lines.append(
            f"| {family} | {bucket['source_count']} | {bucket['unit_count']} | {bucket['extracted_chars']} | {bucket['blank_units']} | {bucket['low_text_units']} | {bucket['status_counts']} |"
        )
    lines += ["", "## Format Coverage" if not zh else "## 格式覆盖", ""]
    lines += [
        "| Format | Sources | Units | Extracted chars | Blank units | Low-text units |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fmt, bucket in agg["by_format"].items():
        lines.append(
            f"| {fmt} | {bucket['source_count']} | {bucket['unit_count']} | {bucket['extracted_chars']} | {bucket['blank_units']} | {bucket['low_text_units']} |"
        )
    lines += ["", "## Source Status" if not zh else "## 来源状态", ""]
    lines += [
        "| Source | Format | Units | Chars | Blank | Low-text | Tool chain | Status | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for src in manifest["sources"]:
        notes = "; ".join(src.get("notes", []))
        tools = " + ".join(src.get("tool_chain", []))
        lines.append(
            f"| `{src['path']}` | {src['format']} | {src['unit_count']} | {src['extracted_chars']} | {src['blank_units']} | {src['low_text_units']} | {tools} | {src['status']} | {notes} |"
        )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--run-id", default="fresh-source-lifecycle-whitepaper-pmi-refresh-20260613")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--low-text-threshold", type=int, default=120)
    parser.add_argument("--fail-on-source-error", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = parse_args(argv)
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()

    records = discover_sources(source_root)
    items_path = output_root / "fresh_source_items.jsonl"

    with items_path.open("w", encoding="utf-8") as items_fh:
        for rec in records:
            try:
                if rec.format == "pdf":
                    extract_pdf(rec, items_fh, args)
                elif rec.format == "epub":
                    extract_epub(rec, items_fh, args)
                elif rec.format in {"md", "markdown"}:
                    extract_markdown(rec, items_fh, args)
                else:
                    rec.status = "skipped"
                    rec.error = "unsupported_format"
            except Exception as exc:  # pragma: no cover - final safety net
                rec.status = "error"
                rec.error = f"unexpected:{type(exc).__name__}: {exc}"
                rec.notes.append(traceback.format_exc(limit=3))

    agg = aggregate(records)
    manifest = {
        "schema_version": "1.0",
        "run_id": args.run_id,
        "generated_at": generated_at,
        "source_root": str(source_root),
        "output_root": str(output_root),
        "summary_only": bool(args.summary_only),
        "source_dirs": list(SOURCE_DIRS),
        "source_suffixes": sorted(SOURCE_SUFFIXES),
        "tool_version": "fresh_extract_sources.py@1",
        "aggregate": agg,
        "sources": [rec.manifest_dict() for rec in records],
    }
    write_json(output_root / "fresh_source_manifest.json", manifest)
    write_json(
        output_root / "fresh_source_synthesis.json",
        {
            "schema_version": "1.0",
            "run_id": args.run_id,
            "generated_at": generated_at,
            "aggregate": agg,
            "target_document_mapping_basis": TARGET_DOC_HINTS,
            "copyright_boundary": (
                "Tracked docs may cite aggregate facts and paraphrased synthesis, "
                "but raw extracted text remains local ignored cache."
            ),
        },
    )
    (output_root / "fresh_source_report.md").write_text(
        render_report(
            run_id=args.run_id,
            generated_at=generated_at,
            source_root=source_root,
            output_root=output_root,
            manifest=manifest,
            lang="en",
        ),
        encoding="utf-8",
    )
    (output_root / "fresh_source_report.zh-CN.md").write_text(
        render_report(
            run_id=args.run_id,
            generated_at=generated_at,
            source_root=source_root,
            output_root=output_root,
            manifest=manifest,
            lang="zh-CN",
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "ok": not any(r.status == "error" for r in records),
                "run_id": args.run_id,
                "summary_only": bool(args.summary_only),
                "output_root": str(output_root),
                "aggregate": agg,
                "error_sources": [r.relative_path for r in records if r.status == "error"],
            },
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    )
    if args.fail_on_source_error and any(r.status == "error" for r in records):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
