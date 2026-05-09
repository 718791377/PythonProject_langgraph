# codex-evidence-intake-pipeline Specification

## ADDED Requirements

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
