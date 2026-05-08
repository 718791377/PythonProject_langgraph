# Tasks: Add Page-Level OCR Evidence Run

## 1. Artifacts

- [x] 1.1 Create proposal, design, spec, and tasks artifacts.
- [x] 1.2 Add bilingual companion artifacts for repository governance checks.

## 2. OCR run implementation

- [x] 2.1 Add OCR page-scope selection for all pages, explicit pages, text-short pages, and text-low-quality pages.
- [x] 2.2 Add run manifest fields for requested pages, rendered images, OCR outputs, confidence, and page failure records.
- [x] 2.3 Add a summary writer that distinguishes successful OCR completion from missing-tool or failed-page evidence.
- [x] 2.4 Add CLI options for OCR run output directory, page scope, threshold, languages, DPI, and Poppler bin directory.

## 3. Tests and validation

- [x] 3.1 Add tests for page-scope parsing and OCR manifest semantics.
- [x] 3.2 Run a small local smoke run without committing generated evidence files.
- [x] 3.3 Run OpenSpec validation, repository guard, local gate, and `git diff --check`.
