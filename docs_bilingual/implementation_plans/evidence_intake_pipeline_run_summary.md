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

This summary records a local evidence run for the evidence intake pipeline. It does not reproduce source PDF pages or saved web-page bodies.

The local private reference root used for this run is ignored by Git. It contains PDF files and saved HTML pages used as local references.

`.local/evidence/local_reference/` is the ignored local evidence directory. It contains the full manifest, page text files, extracted HTML text files, and tool inventory JSON generated during the final text-only run.

## Extraction Result

The pipeline scanned 7 PDF files and 12 top-level saved HTML pages.

PDF text extraction completed for 2,753 pages by using Poppler `pdftotext`. `pdftotext` is the Poppler command-line tool that extracts text from PDF files.

The run marked 284 PDF pages as low quality or needing review. These pages require OCR, second-pass extraction, or human review before a strong page-level reading claim is made.

The run did not complete OCR because `tesseract` was not available. `tesseract` is the optional OCR command-line tool used to convert rendered page images into OCR text and confidence data.

The run did not render every PDF page to image in the final full run because full rendering was slow and because the committed summary should remain a text-extraction evidence summary. A separate smoke run proved that `pdftoppm` can render pages. `pdftoppm` is the Poppler command-line tool that renders PDF pages into images.

HTML extraction produced 12 visible-text records by using the Python standard-library HTML parser. The records are extracted text, not verified article bodies until reviewed.

## Local Evidence Location

The complete local manifest is `.local/evidence/local_reference/manifest.json`. This JSON file records source paths, page counts, extraction methods, quality metrics, and review flags.

The human-readable local summary is `.local/evidence/local_reference/summary.md`. This Markdown file summarizes counts and review notes without being committed.

The external tool inventory is `.local/evidence/local_reference/tool_inventory.json`. This JSON file records the external project read-only candidate scan.

## Tool Availability

- `pdftotext`: available; it is the Poppler PDF text extraction command.
- `pdfinfo`: available; it is the Poppler PDF metadata command used to count pages.
- `pdftoppm`: available; it is the Poppler PDF page rendering command.
- `tesseract`: not available; it is the optional OCR command and must be installed before OCR confidence evidence can be produced.

## External Project Inventory Result

The inventory scanned an external local project directory in read-only mode. That directory is not a source-truth location for this repository.

Useful candidates found:

- `tools/doc_pipeline/scripts/find_poppler.ps1`: a PowerShell helper that locates Poppler tools; it is a candidate adapter pattern, not a file to copy blindly.
- `tools/doc_pipeline/scripts/render_pdf_poppler.ps1`: a PowerShell helper that renders PDF pages through Poppler; it is a candidate adapter pattern, not a file to copy blindly.
- `tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin/pdftotext.exe`: a third-party Poppler binary; it should be treated as an installed local tool, not committed as repository source.
- `intermediate/.../extract_sources.py`: project-specific extraction scripts; they can inform patterns but should not be copied as source truth.

The inventory conclusion is: do not copy external project files in this change. If reuse is needed, open a separate OpenSpec change for adapter design and migration.

## Reading Claim Boundary

This run proves that extraction evidence exists for the local files. It does not prove semantic understanding of every page or article.

Future lifecycle, white paper, market-requirements, or implementation-plan updates may cite this run only as extraction evidence. Strong claims about low-quality pages still require OCR or human review.
