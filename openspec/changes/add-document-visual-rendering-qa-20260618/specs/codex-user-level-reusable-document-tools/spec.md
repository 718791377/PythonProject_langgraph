## ADDED Requirements

### Requirement: Document Visual Rendering QA Reports Backend Truth

The reusable document pipeline SHALL report visual rendering QA backend availability and usage truthfully for Poppler `pdftoppm`, Python `pdf2image`, and `soffice/libreoffice`.

#### Scenario: Optional backend is unavailable

- **GIVEN** a visual QA backend is not installed or cannot be resolved
- **WHEN** the shared document pipeline detects or attempts visual QA
- **THEN** it SHALL record the backend as `unavailable` or `skipped`
- **AND** it SHALL NOT claim that backend produced visual validation evidence.

#### Scenario: Strict backend is required

- **GIVEN** a caller requires one or more named visual QA backends
- **WHEN** any required backend is unavailable
- **THEN** the visual QA command SHALL fail with structured evidence naming the missing backend
- **AND** any generated report SHALL distinguish strict failure from optional skip.

#### Scenario: Visual render succeeds

- **GIVEN** a requested visual QA backend is available
- **WHEN** the pipeline renders a PDF or a DOCX converted to PDF
- **THEN** it SHALL write JSON and Markdown evidence naming the selected backend, output paths, rendered file count, and any skipped alternatives.

### Requirement: Visual QA Runtime Dependencies Stay Outside Tracked Source

The reusable document pipeline SHALL keep visual QA runtime dependencies and generated render artifacts outside tracked repository source.

#### Scenario: Local runtime dependencies are configured

- **GIVEN** Poppler, `pdf2image`, or LibreOffice is installed on the machine
- **WHEN** the shared tooling uses those dependencies
- **THEN** Poppler may be read from ignored `.local` cache, `pdf2image` from the project virtual environment, and LibreOffice from the Windows program installation path
- **AND** third-party application payloads and generated render files SHALL NOT be tracked as repository source.
