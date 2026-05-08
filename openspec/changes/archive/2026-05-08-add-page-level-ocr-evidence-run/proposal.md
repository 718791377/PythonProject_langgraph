# Proposal: Add Page-Level OCR Evidence Run

## Why

The current evidence intake pipeline can identify low-quality PDF text extraction and has optional rendering and OCR entrypoints. It has not yet produced a traceable page-level OCR evidence run for image-heavy PDFs. The repository needs a reproducible OCR run mode before making strong claims that every page of a scanned or image-heavy PDF was read.

## What Changes

- Add an OCR evidence run mode that can process selected pages or all pages of a PDF.
- Store rendered page images, OCR text, confidence metrics, and page-level quality records under ignored local evidence directories.
- Generate a short tracked run summary template without committing copyrighted source text, rendered images, or full OCR text.
- Support missing OCR tools by producing a blocked/missing-tool report instead of claiming completion.

## Capabilities

- `codex-evidence-intake-pipeline` - the capability governing local PDF, HTML, OCR, and reference evidence intake.

## Impact

- Builds on `adopt-document-evidence-adapters-from-external-tools`.
- May generate large ignored local files under `.local/evidence/` during actual runs.
- Does not require committing OCR outputs to Git.
