# Proposal: Adopt Document Evidence Adapters From External Tools

## Why

The evidence intake pipeline already has inline Poppler, HTML, and OCR command handling. Earlier inventory of an external local project identified reusable document pipeline patterns, especially Poppler discovery and page rendering helpers. These patterns should become repository-maintained adapters before the OCR evidence run is expanded.

## What Changes

- Add repository-local evidence adapter modules for Poppler discovery, PDF text extraction, PDF page rendering, Tesseract OCR, and saved HTML visible-text extraction.
- Refactor `tools/evidence_intake_pipeline.py` to call these adapters instead of keeping all command handling inline.
- Preserve the rule that external local project files are not copied blindly and third-party binaries are not committed as source.
- Add tests for adapter discovery, rendering command construction, graceful missing-tool behavior, and pipeline compatibility.

## Capabilities

- `codex-evidence-intake-pipeline` - the capability governing local PDF, HTML, OCR, and reference evidence intake.

## Impact

- Affects local evidence intake tooling and tests only.
- Does not commit private reference PDFs, OCR output, rendered images, or third-party binaries.
- Prepares the next change, `add-page-level-ocr-evidence-run`, to rely on stable adapter boundaries.
