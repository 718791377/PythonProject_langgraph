---
doc_id: evidence_intake_pipeline_run_summary
lang: en
canonical: docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.md
zh_cn: docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.zh-CN.md
doc_class: implementation_plan
status: draft
---

# Evidence Intake Pipeline Run Summary

## Run Scope

This summary records local evidence runs for the evidence intake pipeline. It does not reproduce source PDF pages, OCR full text, rendered images, or saved web-page bodies.

The local private reference roots used for these runs are ignored by Git. They contain source PDFs, saved HTML pages, rendered page images, OCR text files, and machine-readable manifests.

## Text-Only Reference Extraction Result

The first full text-only run scanned 7 PDF files and 12 top-level saved HTML pages.

PDF text extraction completed for 2,753 pages by using Poppler `pdftotext`. `pdftotext` is the Poppler command-line tool that extracts text from PDF files.

The text-only run marked 284 PDF pages as low quality or needing review. Those pages required OCR, second-pass extraction, or human review before a strong page-level reading claim could be made.

HTML extraction produced 12 visible-text records by using the Python standard-library HTML parser. The records are extracted text, not verified article bodies until reviewed.

## PMBOK Sixth Edition Page-Level OCR Result

A later page-level OCR evidence run processed the local PMBOK Sixth Edition Chinese PDF. The PDF itself is local reference material and is not committed.

Local ignored output root: `.local/evidence/pmbok6_ocr/`.

Run parameters:

- Scope: `all`.
- Page count: 812.
- Render DPI: 144.
- OCR language list used for this source PDF: `eng+chi_sim`.
- Rationale for OCR language selection: the source PDF is mainly Simplified Chinese with English acronyms. Other installed language packs are available for future sources but were not included in this run to avoid unnecessary slowdown and recognition noise.

Counts:

- Requested pages: 812.
- Rendered pages: 812.
- OCR completed pages: 812.
- Blocked pages: 0.
- Failed pages: 0.
- Pages needing review: 16.

Confidence metrics:

- Pages with confidence metrics: 812.
- Average confidence: 90.503.
- Minimum confidence: 44.374.
- Maximum confidence: 95.421.
- Pages below confidence 60: 2 pages, page 74 and page 540.
- Pages marked for review: pages 6, 36, 38, 74, 88, 210, 432, 576, 578, 598, 650, 674, 676, 710, 810, and 811.

The OCR run completed for the requested page set. Low-confidence and review-flagged pages still require second-pass OCR or human review before making strong semantic claims about those pages.

## OCR Tool Installation Result

Tesseract OCR is available at `C:\Program Files\Tesseract-OCR\tesseract.exe`. The current Windows user `Path` includes `C:\Program Files\Tesseract-OCR`, so new user terminals can run `tesseract` directly.

Installed or verified Tesseract language data:

- `eng`: generic English, used for both en-GB and en-US needs.
- `chi_sim`: Simplified Chinese.
- `chi_tra`: Traditional Chinese, used for zh-HK and zh-TW needs.
- `fra`: French.
- `deu`: German.
- `jpn`: Japanese.
- `kor`: Korean.
- `lat`: Latin. It can also help with Latin-script text such as Hanyu Pinyin, while Chinese-to-Pinyin conversion still requires a separate transliteration tool.
- `rus`: Russian.
- `ara`: Arabic.
- `osd`: orientation and script detection.

Tesseract standard traineddata packages do not split English into separate en-GB and en-US packages, do not split Traditional Chinese into separate zh-HK and zh-TW packages, and do not provide a dedicated Hanyu Pinyin OCR language package. The generic language/script packages are the practical Tesseract mapping.

## Local Evidence Location

The text-only extraction manifest is `.local/evidence/local_reference/manifest.json`.

The text-only human-readable summary is `.local/evidence/local_reference/summary.md`.

The external tool inventory is `.local/evidence/local_reference/tool_inventory.json`.

The PMBOK OCR manifest is `.local/evidence/pmbok6_ocr/manifest.json`.

The PMBOK OCR human-readable local summary is `.local/evidence/pmbok6_ocr/summary.md`.

The PMBOK OCR page text files are under `.local/evidence/pmbok6_ocr/pdf_ocr/` and remain ignored.

The PMBOK rendered page images are under `.local/evidence/pmbok6_ocr/pdf_images/` and remain ignored.

## External Project Inventory Result

The inventory scanned an external local project directory in read-only mode. That directory is not a source-truth location for this repository.

Useful candidates found:

- `tools/doc_pipeline/scripts/find_poppler.ps1`: a PowerShell helper that locates Poppler tools; it is a candidate adapter pattern, not a file to copy blindly.
- `tools/doc_pipeline/scripts/render_pdf_poppler.ps1`: a PowerShell helper that renders PDF pages through Poppler; it is a candidate adapter pattern, not a file to copy blindly.
- `tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin/pdftotext.exe`: a third-party Poppler binary; it should be treated as an installed local tool, not committed as repository source.
- `intermediate/.../extract_sources.py`: project-specific extraction scripts; they can inform patterns but should not be copied as source truth.

The adapter migration is implemented in this repository under `tools/evidence_adapters/`. Third-party binaries remain local install dependencies.

## Reading Claim Boundary

This run proves that extraction and OCR evidence exists for the local files. It does not prove semantic understanding of every page or article.

Future lifecycle, white paper, market-requirements, or implementation-plan updates may cite this run only as extraction and OCR evidence. Strong claims about low-confidence or review-flagged pages still require second-pass OCR or human review.
