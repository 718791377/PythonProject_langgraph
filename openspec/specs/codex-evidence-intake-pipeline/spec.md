# codex-evidence-intake-pipeline Specification

## Purpose

This specification defines the repository-maintained evidence intake pipeline used to turn local reference files into traceable extraction, rendering, OCR, and quality evidence without committing private source material or large generated artifacts.

## Requirements

### Requirement: Evidence Intake Uses Repository-Maintained Adapters

The repository SHALL maintain document evidence adapters for PDF text extraction, PDF page rendering, OCR, and saved HTML visible-text extraction instead of relying on copied external project scripts.

#### Scenario: External document tooling is adopted

- **GIVEN** an external local project contains Poppler or document pipeline helpers
- **WHEN** the repository adopts reusable behavior from those helpers
- **THEN** the behavior is implemented as repository-maintained adapter source under `tools/evidence_adapters/`
- **AND** third-party binaries remain local install dependencies rather than tracked repository source
- **AND** project-specific absolute paths from the external project are not copied into default behavior

### Requirement: Evidence Adapters Degrade Gracefully When Tools Are Missing

The evidence intake pipeline SHALL record structured missing-tool evidence instead of failing silently or claiming a page was understood.

#### Scenario: OCR or rendering tools are unavailable

- **GIVEN** `pdftoppm` or `tesseract` is not available on the current machine
- **WHEN** the evidence pipeline requests rendering or OCR
- **THEN** the manifest records the missing tool and marks affected pages for review
- **AND** the pipeline does not claim OCR text or confidence was produced

#### Scenario: Tesseract is installed in a standard Windows location outside PATH

- **GIVEN** Tesseract OCR is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **AND** the current process PATH does not resolve `tesseract`
- **WHEN** the Tesseract adapter discovers OCR tooling
- **THEN** it finds the standard Windows installation path
- **AND** OCR runs do not incorrectly report Tesseract as missing

### Requirement: Page-Level OCR Runs Are Traceable And Scoped

The evidence intake pipeline SHALL support page-level OCR evidence runs with explicit page scope, per-page rendered image evidence, OCR text evidence, confidence metrics, and quality flags stored in ignored local evidence directories.

#### Scenario: A maintainer requests OCR for every page of a PDF

- **GIVEN** a local PDF is available and the maintainer requests all-page OCR
- **WHEN** the OCR evidence run is executed
- **THEN** the run manifest records the requested page set
- **AND** each requested page has a page record with render status, OCR status, confidence when available, and review flags
- **AND** large rendered images and OCR full text remain ignored local artifacts

### Requirement: OCR Completion Claims Require Evidence Or Explicit Failure Records

The repository SHALL NOT claim that a PDF page was correctly OCR-read unless the evidence run produced page-level OCR output and quality metrics for that page.

#### Scenario: OCR tooling is missing or a page fails

- **GIVEN** OCR tooling is missing or a page render/OCR command fails
- **WHEN** the evidence run writes its manifest
- **THEN** the affected page is marked as blocked or failed with the concrete reason
- **AND** the summary says OCR is incomplete for that page set
- **AND** downstream lifecycle or white-paper updates do not treat that page as fully read
