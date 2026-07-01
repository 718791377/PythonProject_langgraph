# Tasks: Add Document Visual Rendering QA

## Stage A: Freeze plan

- [x] Confirm install/use locations for Poppler `pdftoppm`, Python `pdf2image`, and LibreOffice `soffice.exe`.
- [x] Create the OpenSpec change and bilingual design/proposal/task artifacts.
- [x] Create the bilingual implementation plan under `docs_bilingual/implementation_plans/`.
- [x] Define optional-backend and strict-backend behavior before runtime edits.
- [x] Validate, commit, and integrate the Stage A plan-freeze package into local `main`.

## Stage B: Implement live runtime

- [x] Update detection to report `pdftoppm`, `pdf2image`, `LibreOffice`, and visual-QA readiness.
- [x] Add `pdf2image` PDF rendering helper with structured JSON/Markdown evidence.
- [x] Add `soffice/libreoffice` DOCX-to-PDF fallback wrapper with structured evidence.
- [x] Add the visual rendering QA orchestrator and wire it into the document quality-check flow.
- [x] Add tests for missing dependency degradation, strict backend failures, and gated success smokes.
- [x] Update setup/dependency notes and sanitized config examples.
- [x] Validate, commit, and integrate the Stage B runtime package into local `main`.
