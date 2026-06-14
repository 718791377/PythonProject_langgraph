#!/usr/bin/env python3
"""Normalize document conversion and visual-QA outputs into evidence records.

The records produced by this tool are evidence pointers for layout/rendering
review. They intentionally do not promote visual evidence, OCR output, or
PDF-to-Office reconstruction to factual tender-source authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path.cwd()
CANONICAL_PROJECT_ROOT = Path(os.environ.get("DOCUMENT_PIPELINE_PROJECT_ROOT", str(Path.cwd())))
PROTECTED_NAMES = ("current_progress", "regulations", "requirement")
AUTHORITY_STATUSES = {
    "source",
    "converted",
    "ocr_reconstructed",
    "pdf_reconstructed",
    "quality_evidence",
    "draft",
}
HEX64_RE = re.compile(r"^[0-9a-fA-F]{64}$")
FACT_BOUNDARY_NOTE = (
    "Visual, font, render, contact-sheet, OCR, and PDF-to-Office reconstruction "
    "evidence supports layout/rendering review only. It is not proof of tender "
    "facts such as contract amounts, durations, owners, equipment quantities, "
    "model numbers, or source page references."
)


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def as_text(value: Any) -> str:
    return "" if value is None else str(value)


def load_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    value = json.loads(load_text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def sha_file(path_value: str | Path | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def absolute_path_text(path_value: str | Path | None) -> str | None:
    if not path_value:
        return None
    try:
        return str(Path(path_value).resolve(strict=False))
    except OSError:
        return str(path_value)


def slugify(value: str, default: str = "document") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or default


def infer_file_type(path_value: str | None, input_type: str | None = None) -> str:
    if input_type:
        normalized = input_type.strip().lower().lstrip(".")
        aliases = {
            "word": "docx",
            "docx": "docx",
            "doc": "doc",
            "excel": "xlsx",
            "xlsx": "xlsx",
            "xls": "xls",
            "powerpoint": "pptx",
            "pptx": "pptx",
            "ppt": "ppt",
            "pdf": "pdf",
        }
        if normalized in aliases:
            return aliases[normalized]
    suffix = Path(path_value or "").suffix.lower().lstrip(".")
    return suffix if suffix in {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "txt", "md"} else "unknown"


def read_quality_report(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in load_text(path).splitlines():
        match = re.match(r"^\s*-\s*([^:]+):\s*(.*?)\s*$", line)
        if match:
            key = re.sub(r"[^a-z0-9]+", "_", match.group(1).strip().lower()).strip("_")
            values[key] = match.group(2).strip()
    return values


def infer_companion(base_path: Path | None, suffix: str) -> Path | None:
    if base_path is None:
        return None
    name = base_path.name
    if name.endswith("_quality_report.md"):
        stem = name[: -len("_quality_report.md")]
    else:
        stem = base_path.stem
    candidate = base_path.with_name(stem + suffix)
    return candidate if candidate.exists() else None


def first_existing_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


def collect_protected_dirs() -> list[Path]:
    dirs: list[Path] = []
    for base in (PROJECT_ROOT, CANONICAL_PROJECT_ROOT):
        for name in PROTECTED_NAMES:
            candidate = (base / name).resolve(strict=False)
            if candidate not in dirs:
                dirs.append(candidate)
    return dirs


def is_under(path_value: str | Path, parent: Path) -> bool:
    try:
        child = Path(path_value).resolve(strict=False)
        parent_resolved = parent.resolve(strict=False)
        child_key = os.path.normcase(str(child))
        parent_key = os.path.normcase(str(parent_resolved))
        return child_key == parent_key or child_key.startswith(parent_key + os.sep)
    except OSError:
        return False


def validate_target_paths(evidence: dict[str, Any]) -> dict[str, Any]:
    protected_dirs = collect_protected_dirs()
    checked: list[str] = []
    violations: list[str] = []
    path_keys = [
        "outputPdfPath",
        "reconstructedOfficePath",
        "renderRoot",
        "contactSheetPath",
        "fontReportPath",
        "qualityReportPath",
    ]
    for key in path_keys:
        value = evidence.get(key)
        if value:
            checked.append(str(value))
    for value in evidence.get("pageImages") or []:
        if value:
            checked.append(str(value))
    for value in checked:
        for protected in protected_dirs:
            if is_under(value, protected):
                violations.append(f"{value} is under protected source directory {protected}")
    return {
        "ok": not violations,
        "checkedOutputPaths": checked,
        "protectedDirectories": [str(path) for path in protected_dirs],
        "violations": violations,
    }


def validate_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "schemaVersion",
        "recordType",
        "runId",
        "documentId",
        "sourcePath",
        "sourceSha256",
        "sourceFileType",
        "conversionChain",
        "authorityStatus",
        "usableForFacts",
        "evidencePurpose",
        "factBoundaryNote",
        "pageImages",
        "pageImageHashes",
        "protectedPathValidation",
    ]
    for key in required:
        if key not in evidence or evidence.get(key) in (None, ""):
            errors.append(f"missing required field: {key}")
    if evidence.get("schemaVersion") != "1":
        errors.append("schemaVersion must be '1'")
    if evidence.get("recordType") != "document_quality_evidence":
        errors.append("recordType must be 'document_quality_evidence'")
    if evidence.get("authorityStatus") not in AUTHORITY_STATUSES:
        errors.append(f"unsupported authorityStatus: {evidence.get('authorityStatus')}")
    if evidence.get("evidencePurpose") != "layout_rendering_only":
        errors.append("evidencePurpose must be layout_rendering_only")
    if evidence.get("authorityStatus") in {"ocr_reconstructed", "pdf_reconstructed", "quality_evidence"} and evidence.get("usableForFacts") is True:
        errors.append("reconstructed/OCR/quality evidence must not default usableForFacts=true")
    for key in (
        "sourceSha256",
        "outputPdfSha256",
        "reconstructedOfficeSha256",
        "contactSheetSha256",
        "fontReportSha256",
        "qualityReportSha256",
    ):
        value = evidence.get(key)
        if value not in (None, "") and not HEX64_RE.match(str(value)):
            errors.append(f"{key} is not a sha256 hex digest")
    page_images = [str(path) for path in evidence.get("pageImages") or []]
    image_hashes = evidence.get("pageImageHashes") or {}
    if not isinstance(image_hashes, dict):
        errors.append("pageImageHashes must be an object")
    else:
        for path in page_images:
            if path not in image_hashes:
                errors.append(f"missing page image hash entry: {path}")
        for path, digest in image_hashes.items():
            if digest not in (None, "") and not HEX64_RE.match(str(digest)):
                errors.append(f"pageImageHashes[{path}] is not a sha256 hex digest")
    path_validation = validate_target_paths(evidence)
    evidence["protectedPathValidation"] = path_validation
    if not path_validation["ok"]:
        errors.extend(path_validation["violations"])
    return errors


def conversion_status(*parts: Any) -> str:
    for part in parts:
        text = as_text(part).strip()
        if text:
            return text
    return "unknown"


def build_conversion_chain(
    conversion_report: dict[str, Any],
    render_report: dict[str, Any],
    pdf_info_report: dict[str, Any],
    quality_report_path: Path | None,
    font_report_path: Path | None,
) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    if conversion_report:
        if conversion_report.get("input_pdf") and any(conversion_report.get(key) for key in ("output_docx", "output_xlsx", "output_pptx")):
            output_path = first_existing_value(conversion_report.get("output_docx"), conversion_report.get("output_xlsx"), conversion_report.get("output_pptx"))
            steps.append(
                {
                    "stage": "pdf_to_office",
                    "tool": "acrobat_pro",
                    "inputPath": conversion_report.get("input_pdf"),
                    "outputPath": output_path,
                    "startedAt": conversion_report.get("started_at"),
                    "finishedAt": conversion_report.get("finished_at"),
                    "status": conversion_status(conversion_report.get("export_result"), conversion_report.get("open_result")),
                    "warnings": [str(item) for item in conversion_report.get("warnings") or []],
                    "errors": [str(item) for item in conversion_report.get("errors") or []],
                }
            )
        else:
            input_path = first_existing_value(
                conversion_report.get("input_docx"),
                conversion_report.get("input_xlsx"),
                conversion_report.get("input_pptx"),
                conversion_report.get("input_office"),
            )
            steps.append(
                {
                    "stage": "office_to_pdf",
                    "tool": "office_com",
                    "toolVersion": first_existing_value(conversion_report.get("word_version"), conversion_report.get("office_version")),
                    "inputPath": input_path,
                    "outputPath": conversion_report.get("output_pdf"),
                    "startedAt": conversion_report.get("started_at"),
                    "finishedAt": conversion_report.get("finished_at"),
                    "status": conversion_status(conversion_report.get("export_result"), conversion_report.get("open_result")),
                    "warnings": [str(item) for item in conversion_report.get("warnings") or []],
                    "errors": [str(item) for item in conversion_report.get("errors") or []],
                }
            )
    if render_report:
        steps.append(
            {
                "stage": "pdf_render",
                "tool": as_text(render_report.get("renderer") or "pdftoppm"),
                "toolPath": render_report.get("renderer_path"),
                "inputPath": render_report.get("input_pdf"),
                "outputPath": render_report.get("output_dir"),
                "startedAt": render_report.get("started_at"),
                "finishedAt": render_report.get("finished_at"),
                "status": "ok" if render_report.get("exit_code") == 0 else conversion_status(render_report.get("exit_code")),
                "warnings": [],
                "errors": [] if render_report.get("exit_code") in (0, None) else [as_text(render_report.get("tool_output"))],
            }
        )
    if pdf_info_report:
        pdfinfo = pdf_info_report.get("pdfinfo") if isinstance(pdf_info_report.get("pdfinfo"), dict) else {}
        steps.append(
            {
                "stage": "pdf_info",
                "tool": "pdfinfo",
                "toolPath": pdfinfo.get("path"),
                "inputPath": pdf_info_report.get("input_pdf"),
                "outputPath": None,
                "startedAt": pdf_info_report.get("generated_at"),
                "finishedAt": pdf_info_report.get("generated_at"),
                "status": "ok" if pdfinfo.get("exit_code") in (0, None) else conversion_status(pdfinfo.get("exit_code")),
                "warnings": [],
                "errors": [] if not pdfinfo.get("error") else [as_text(pdfinfo.get("error"))],
            }
        )
    if font_report_path:
        steps.append(
            {
                "stage": "font_report",
                "tool": "pdffonts",
                "inputPath": None,
                "outputPath": str(font_report_path),
                "startedAt": None,
                "finishedAt": None,
                "status": "ok" if font_report_path.exists() else "missing",
                "warnings": [],
                "errors": [] if font_report_path.exists() else ["font report path does not exist"],
            }
        )
    if quality_report_path:
        steps.append(
            {
                "stage": "quality_report",
                "tool": "document_quality_report",
                "inputPath": None,
                "outputPath": str(quality_report_path),
                "startedAt": None,
                "finishedAt": None,
                "status": "ok" if quality_report_path.exists() else "missing",
                "warnings": [],
                "errors": [] if quality_report_path.exists() else ["quality report path does not exist"],
            }
        )
    return steps


def build_evidence(args: argparse.Namespace) -> dict[str, Any]:
    quality_report_path = Path(args.quality_report) if args.quality_report else None
    quality_values = read_quality_report(quality_report_path)
    conversion_path = Path(args.conversion_report) if args.conversion_report else infer_companion(quality_report_path, "_word_export_status.json")
    render_path = Path(args.render_report) if args.render_report else infer_companion(quality_report_path, "_render.json")
    contact_path = Path(args.contact_sheet_report) if args.contact_sheet_report else infer_companion(quality_report_path, "_render_contact_sheet.json")
    pdf_info_path = Path(args.pdf_info_report) if args.pdf_info_report else infer_companion(quality_report_path, "_pdf_info.json")
    font_report_path = Path(args.font_report) if args.font_report else infer_companion(quality_report_path, "_pdffonts.txt")

    conversion_report = load_json(conversion_path)
    render_report = load_json(render_path)
    contact_report = load_json(contact_path)
    pdf_info_report = load_json(pdf_info_path)

    source_path = first_existing_value(
        args.source_path,
        conversion_report.get("input_docx"),
        conversion_report.get("input_xlsx"),
        conversion_report.get("input_pptx"),
        conversion_report.get("input_office"),
        conversion_report.get("input_pdf"),
        quality_values.get("source"),
    )
    output_pdf_path = first_existing_value(
        args.output_pdf,
        conversion_report.get("output_pdf"),
        render_report.get("input_pdf"),
        quality_values.get("pdf_inspected"),
        pdf_info_report.get("input_pdf"),
    )
    reconstructed_office_path = first_existing_value(
        args.reconstructed_office_path,
        conversion_report.get("output_docx"),
        conversion_report.get("output_xlsx"),
        conversion_report.get("output_pptx"),
    )
    source_file_type = infer_file_type(source_path, quality_values.get("input_type"))

    page_images = [str(item) for item in first_existing_value(render_report.get("rendered_files"), contact_report.get("files"), []) or []]
    page_image_hashes = {path: sha_file(path) for path in page_images}
    contact_sheet_path = first_existing_value(args.contact_sheet_path, contact_report.get("output"), quality_values.get("contact_sheet"))
    render_root = first_existing_value(args.render_root, render_report.get("output_dir"), contact_report.get("input_dir"), quality_values.get("render_directory"))
    page_count = first_existing_value(args.page_count, conversion_report.get("page_count"), render_report.get("rendered_count"), contact_report.get("page_count"), pdf_info_report.get("page_count"))
    render_dpi = first_existing_value(args.render_dpi, render_report.get("dpi"), quality_values.get("dpi"))
    job_name = first_existing_value(
        args.job_name,
        conversion_report.get("job_name"),
        render_report.get("job_name"),
        pdf_info_report.get("job_name"),
        quality_values.get("job"),
        quality_report_path.stem if quality_report_path else None,
    )
    document_id = args.document_id or slugify(Path(as_text(source_path or job_name)).stem or as_text(job_name), default="document")
    run_id = args.run_id or slugify(as_text(job_name or document_id), default="document-quality-evidence")

    is_pdf_to_office = bool(conversion_report.get("input_pdf") and reconstructed_office_path)
    authority_status = args.authority_status or ("pdf_reconstructed" if is_pdf_to_office else "quality_evidence")
    usable_for_facts = bool(args.usable_for_facts)
    if authority_status in {"ocr_reconstructed", "pdf_reconstructed", "quality_evidence"} and not args.force_usable_for_facts:
        usable_for_facts = False

    warnings: list[str] = []
    errors: list[str] = []
    for report in (conversion_report, render_report):
        warnings.extend(str(item) for item in report.get("warnings") or [])
        errors.extend(str(item) for item in report.get("errors") or [])
    for path_value, label in ((source_path, "sourcePath"), (output_pdf_path, "outputPdfPath"), (quality_report_path, "qualityReportPath")):
        if path_value and not Path(path_value).exists():
            warnings.append(f"{label} does not exist: {path_value}")

    evidence: dict[str, Any] = {
        "schemaVersion": "1",
        "recordType": "document_quality_evidence",
        "runId": run_id,
        "jobName": job_name,
        "documentId": document_id,
        "createdAt": now_utc(),
        "sourcePath": as_text(source_path),
        "sourceAbsolutePath": absolute_path_text(source_path),
        "sourceSha256": sha_file(source_path),
        "sourceFileType": source_file_type,
        "conversionChain": build_conversion_chain(conversion_report, render_report, pdf_info_report, quality_report_path, font_report_path),
        "authorityStatus": authority_status,
        "usableForFacts": usable_for_facts,
        "evidencePurpose": "layout_rendering_only",
        "factBoundaryNote": FACT_BOUNDARY_NOTE,
        "outputPdfPath": as_text(output_pdf_path) if output_pdf_path else None,
        "outputPdfSha256": sha_file(output_pdf_path),
        "reconstructedOfficePath": as_text(reconstructed_office_path) if reconstructed_office_path else None,
        "reconstructedOfficeSha256": sha_file(reconstructed_office_path),
        "isReconstructed": bool(is_pdf_to_office or args.is_reconstructed),
        "ocrUsed": bool(args.ocr_used or authority_status == "ocr_reconstructed"),
        "pageCount": int(page_count) if as_text(page_count).isdigit() else None,
        "renderDpi": int(render_dpi) if as_text(render_dpi).isdigit() else None,
        "renderRoot": as_text(render_root) if render_root else None,
        "pageImages": page_images,
        "pageImageHashes": page_image_hashes,
        "contactSheetPath": as_text(contact_sheet_path) if contact_sheet_path else None,
        "contactSheetSha256": sha_file(contact_sheet_path),
        "fontReportPath": str(font_report_path) if font_report_path else None,
        "fontReportSha256": sha_file(font_report_path),
        "qualityReportPath": str(quality_report_path) if quality_report_path else None,
        "qualityReportSha256": sha_file(quality_report_path),
        "visualReviewStatus": args.visual_review_status,
        "visualReviewNotes": args.visual_review_notes,
        "warnings": warnings,
        "errors": errors,
        "protectedPathValidation": {"ok": True, "checkedOutputPaths": [], "protectedDirectories": []},
    }
    validation_errors = validate_evidence(evidence)
    if validation_errors:
        evidence.setdefault("errors", []).extend(validation_errors)
    return evidence


def write_or_print_json(value: dict[str, Any], output_path: str | None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not output_path:
        sys.stdout.write(text)
        return
    out = Path(output_path)
    for protected in collect_protected_dirs():
        if is_under(out, protected):
            raise ValueError(f"output path is under protected source directory {protected}: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(out)}, ensure_ascii=False, indent=2))


def cmd_normalize(args: argparse.Namespace) -> int:
    evidence = build_evidence(args)
    validation_errors = validate_evidence(evidence)
    if validation_errors:
        report = {"ok": False, "errors": validation_errors, "evidence": evidence}
        write_or_print_json(report, args.output)
        return 1
    write_or_print_json(evidence, args.output)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    evidence = load_json(Path(args.evidence))
    errors = validate_evidence(evidence)
    report = {"ok": not errors, "errors": errors, "evidencePath": args.evidence}
    write_or_print_json(report, args.output)
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("normalize", help="Normalize existing document quality outputs into one evidence JSON record.")
    p.add_argument("--quality-report", help="Markdown quality report, normally *_quality_report.md.")
    p.add_argument("--conversion-report", help="Office-to-PDF or Acrobat PDF-to-Office JSON report.")
    p.add_argument("--render-report", help="Poppler render JSON report, normally *_render.json.")
    p.add_argument("--contact-sheet-report", help="Contact sheet JSON report, normally *_render_contact_sheet.json.")
    p.add_argument("--pdf-info-report", help="PDF info JSON report, normally *_pdf_info.json.")
    p.add_argument("--font-report", help="pdffonts text report, normally *_pdffonts.txt.")
    p.add_argument("--source-path", help="Override source path when reports do not include it.")
    p.add_argument("--output-pdf", help="Override output PDF path.")
    p.add_argument("--reconstructed-office-path", help="PDF-to-Office reconstruction output path.")
    p.add_argument("--contact-sheet-path", help="Override contact sheet image path.")
    p.add_argument("--render-root", help="Override render root directory.")
    p.add_argument("--job-name")
    p.add_argument("--run-id")
    p.add_argument("--document-id")
    p.add_argument("--authority-status", choices=sorted(AUTHORITY_STATUSES))
    p.add_argument("--usable-for-facts", action="store_true", help="Request usableForFacts=true; ignored for reconstructed/quality evidence unless --force-usable-for-facts is also set.")
    p.add_argument("--force-usable-for-facts", action="store_true", help="Allow usableForFacts=true for exceptional manually reviewed records.")
    p.add_argument("--is-reconstructed", action="store_true")
    p.add_argument("--ocr-used", action="store_true")
    p.add_argument("--page-count", type=int)
    p.add_argument("--render-dpi", type=int)
    p.add_argument("--visual-review-status", default="not_reviewed", choices=["not_reviewed", "pass", "warning", "fail", "unknown"])
    p.add_argument("--visual-review-notes")
    p.add_argument("--output", help="Optional output JSON path. If omitted, the evidence record is printed to stdout.")
    p.set_defaults(func=cmd_normalize)

    p = sub.add_parser("validate", help="Validate an existing evidence JSON record with built-in project path checks.")
    p.add_argument("--evidence", required=True)
    p.add_argument("--output", help="Optional validation report output path. If omitted, print to stdout.")
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
