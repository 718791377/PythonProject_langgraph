# Proposal: Add Evidence Intake Pipeline

## Why

The repository needs a traceable evidence gate before local PDFs, saved web pages, OCR outputs, and other private reference materials are used to update lifecycle documents, white papers, market requirements, implementation plans, or knowledge-base indexes.

Saved PDFs and web pages can be hard to audit. Scanned PDFs may expose noisy OCR text, and saved web pages may include page chrome, scripts, duplicated titles, image placeholders, and non-body text. A maintainer should be able to see what was extracted, which pages are low quality, and which inputs still need OCR or human review.

## What Changes

- Add a repository-local evidence intake pipeline that can inspect local private references without committing the private reference corpus.
- Generate per-PDF page text records with extraction method, character counts, noise metrics, and low-quality flags.
- Generate per-HTML visible-text records with title, metadata, extracted text, character counts, and noise metrics.
- Generate manifest and summary reports that state what was extracted, what remains uncertain, and which inputs need human or second-pass OCR review.
- Add a read-only inventory mode for external local projects so candidate reusable document/PDF/HTML tools can be evaluated before any copy or migration.
- Document platform knowledge-base, project knowledge-base, cross-project data, and platform-tool maintenance boundaries.

## Scope

In scope:

- Tooling under `tools/`.
- Tests under `test/`.
- OpenSpec requirements for lifecycle-document governance.
- A bilingual implementation plan documenting the evidence intake workflow.
- A local run summary that records counts without committing extracted private text.

Out of scope:

- Committing ignored private source PDFs or saved web pages.
- Copying third-party binaries from external projects into this repository during this change.
- Claiming semantic understanding of every page or article without reviewing generated evidence.
- Replacing human review for low-quality OCR pages.
- Creating a production vector database or project knowledge base.

## Validation

- Run the evidence intake pipeline against available local references in report mode.
- Run the external project inventory mode.
- Run unit tests for noise metrics, HTML extraction, and inventory classification.
- Run `openspec validate --all`.
- Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- Run `git diff --check`.
