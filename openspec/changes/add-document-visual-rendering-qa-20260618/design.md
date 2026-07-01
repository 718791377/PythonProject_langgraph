---
change_id: add-document-visual-rendering-qa-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# Design: Document Visual Rendering QA

## Runtime Boundary

`D:\PythonProject_langgraph` remains the shared source authority for document tooling. `D:\project` remains a consumer/source-comparison project and must not be modified by this change.

Runtime dependency placement is fixed as follows:

- Poppler and `pdftoppm.exe` live in the ignored local cache, currently `D:\PythonProject_langgraph\.local\user_level_document_tools\poppler-25.07.0-0\poppler-25.07.0\Library\bin`.
- Python `pdf2image` is installed into the project virtual environment used by the document pipeline, currently `D:\PythonProject_langgraph\.venv`.
- LibreOffice `soffice.exe` is installed outside the repository, normally `C:\Program Files\LibreOffice\program\soffice.exe`.

No third-party application payload is tracked by Git.

## Backend Contract

The Stage B runtime SHALL expose a visual QA orchestrator that accepts PDF and DOCX inputs and writes evidence under ignored `.local/user_level_document_tools/` output roots.

Default backend behavior:

1. For PDF input, `pdftoppm` is the Poppler baseline renderer when available.
2. `pdf2image` is an optional Python renderer and must report that it still depends on a Poppler backend path for reliable Windows rendering.
3. For DOCX input, `soffice/libreoffice` is an optional fallback converter to PDF; after conversion, PDF rendering uses the selected PDF renderer.
4. Missing optional backends produce `skipped` or `unavailable` evidence, not a false visual-QA pass.
5. Strict mode accepts named required backends and fails if any required backend is unavailable.

## Evidence Contract

Stage B SHALL write:

- a detection report listing `pdftoppm`, `pdf2image`, and `LibreOffice` rows;
- a visual QA JSON report with attempted backends, selected backend, skipped backends, failure reasons, rendered file counts, and output paths;
- a Markdown companion summary suitable for operator review;
- render outputs under ignored `.local/user_level_document_tools/visual_render_qa/`.

The existing `.local/user_level_document_tools/doc_quality_reports/` report root may continue to hold summaries. The existing `.local/user_level_document_tools/renders/` root remains valid for legacy Poppler rendering output.

## Implementation Slices

After Stage A is integrated into local `main`, Stage B is eligible for durable team execution because it has at least two mostly independent slices:

1. Runtime backend slice: detection updates, `pdf2image` renderer helper, `soffice` DOCX-to-PDF wrapper, and visual QA orchestrator.
2. Test/documentation slice: dependency-missing tests, gated success smokes, setup notes, and config examples.

The leader session owns final fan-in, validation, local commit, local `main` integration, and remote-publication stop.

## Validation

Baseline tests must pass on machines without `pdf2image` or LibreOffice. Environment-gated smoke tests may run when the backend is actually present. Validation must include OpenSpec checks, the document-tool focused test suite, local CI gate, local MR review, and local-main integration helper evidence.
