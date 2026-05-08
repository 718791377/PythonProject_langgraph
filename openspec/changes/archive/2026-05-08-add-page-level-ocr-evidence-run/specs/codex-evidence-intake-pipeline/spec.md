# codex-evidence-intake-pipeline Specification

## ADDED Requirements

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
