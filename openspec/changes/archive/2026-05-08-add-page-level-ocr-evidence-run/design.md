# Design: Page-Level OCR Evidence Run

## Context

A PDF may contain an embedded text layer, page images, tables, or scanned pages. `pdftotext` can prove what text is extractable from the PDF text layer, but it cannot prove that image-only content was read. OCR evidence must therefore be page-scoped, reproducible, and honest about missing tools or low confidence.

## Modes

- `text-low-quality`: OCR only pages already marked low quality by text extraction metrics.
- `text-short`: OCR pages below a configurable extracted-character threshold.
- `pages`: OCR an explicit page list or page range.
- `all`: OCR every page of the selected PDF.

## Outputs

Ignored local outputs:

- `.local/evidence/<run>/pdf_images/<pdf-slug>/page-0001.png` - rendered page image evidence for OCR and visual review.
- `.local/evidence/<run>/pdf_ocr/<pdf-slug>/page-0001.ocr.txt` - per-page OCR text output kept as ignored local evidence.
- `.local/evidence/<run>/manifest.json` - machine-readable OCR run manifest with page status and quality metrics.
- `.local/evidence/<run>/summary.md` - human-readable OCR run summary with counts and completion status.

Tracked outputs may include only short summaries, counts, paths, hashes, and quality metrics. Tracked outputs must not reproduce full copyrighted pages.

## Confidence

The Tesseract adapter reports average TSV confidence when available. The OCR run also records extracted character counts, replacement characters, CJK character counts, Latin character counts, noise ratios, and `needs_review` flags.

## Completion Semantics

An OCR run is complete only for the requested page set when each requested page has either OCR text and confidence evidence or an explicit missing-tool/render/OCR failure record. A missing-tool report is a valid evidence result but not a successful OCR completion.

## Validation

Tests use tiny generated PDFs or fake adapters where possible. Full book OCR is an operator run because it may be slow and creates large ignored local artifacts.
