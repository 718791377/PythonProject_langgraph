---
change_id: add-document-visual-rendering-qa-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# Proposal: Add Document Visual Rendering QA

## Why

The reusable document/PDF/vector tooling has already moved into `D:\PythonProject_langgraph`, and Poppler `pdftoppm` is available through the ignored local Poppler cache. The next gap is honest visual rendering QA for document deliverables: prior consumer work had to downgrade to OOXML-only structural checks when `pdf2image`, `soffice/libreoffice`, or `pdftoppm` were unavailable.

The shared pipeline needs a durable contract that detects these visual QA backends, records which backend was used or skipped, and prevents false claims of visual validation when optional tools are missing.

## What Changes

- Freeze a visual rendering QA contract for `pdftoppm`, Python `pdf2image`, and `soffice/libreoffice` before runtime edits begin.
- Define local install/use locations: Poppler under ignored `.local`, `pdf2image` in the project virtual environment, and LibreOffice under the Windows program installation path.
- Require structured JSON and Markdown evidence for backend availability, render attempts, downgrade reasons, and strict-backend failures.
- Keep optional backends optional by default; strict mode may require named backends and fail when they are unavailable.
- Split Stage B implementation into independent runtime and test/documentation slices that can use durable team execution after this plan is integrated into local `main`.

## Out of Scope

- Installing LibreOffice or downloading third-party binaries as tracked repository source.
- Moving or cleaning `D:\project` files.
- Migrating consumer configs, protected source material, vector indexes, embedding caches, generated reports, or deliverables into shared source.
- Remote publication, GitLab MR creation or merge, GitHub sync, or remote ref mutation.
