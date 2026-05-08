# Design: Document Evidence Adapters

## Context

The external local project inventory found useful Poppler helper patterns:

- `tools/doc_pipeline/scripts/find_poppler.ps1` locates Poppler binaries from PATH, known install locations, and optional search roots.
- `tools/doc_pipeline/scripts/render_pdf_poppler.ps1` renders PDF pages through Poppler and records report metadata.
- Local Poppler binaries are third-party tools and must remain installed local dependencies rather than repository source.
- Project-specific extraction scripts may inform patterns but must not become source truth here.

## Decisions

1. Create a Python adapter package under `tools/evidence_adapters/`.
2. Keep adapters dependency-light and cold-start friendly.
3. Use command-line tools when available: `pdfinfo`, `pdftotext`, `pdftoppm`, and `tesseract`.
4. Support explicit Poppler binary directories through an option and environment variable before falling back to PATH and known install roots.
5. Return structured results instead of printing directly so the pipeline can write manifests consistently.
6. Keep generated text, rendered images, OCR output, and third-party binaries outside Git.

## Adapter Layout

- `tools/evidence_adapters/common.py`: shared command execution, UTF-8 environment, safe paths, and quality metrics.
- `tools/evidence_adapters/poppler_adapter.py`: Poppler tool discovery, page counts, PDF text extraction, and page rendering.
- `tools/evidence_adapters/tesseract_adapter.py`: Tesseract availability, OCR text, TSV confidence parsing, and graceful missing-tool results.
- `tools/evidence_adapters/html_visible_text_adapter.py`: visible text extraction for saved HTML pages.

## External Tool Handling

Adapters may learn from `D:\project` patterns, but they must not copy project-specific absolute output paths or report directories. Any external helper path is evidence for design only. The repository source truth remains under `D:\PythonProject_langgraph`.

## Validation

- Unit tests cover adapter discovery with fake executable directories.
- Unit tests cover Tesseract confidence parsing.
- Pipeline smoke tests ensure existing extract behavior still produces manifests.
- OpenSpec validation and local gate must pass before publication.
