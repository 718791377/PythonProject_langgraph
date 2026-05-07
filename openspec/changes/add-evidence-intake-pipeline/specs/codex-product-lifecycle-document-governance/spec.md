## ADDED Requirements

### Requirement: Local Reference Claims Require Extraction Evidence

The repository SHALL NOT claim that ignored local reference PDFs or saved web pages were fully and correctly read unless a traceable evidence intake workflow has produced per-source evidence records.

#### Scenario: A maintainer uses local references to update lifecycle documents

- **GIVEN** the maintainer uses ignored local reference files
- **WHEN** the maintainer claims that a PDF was read page by page
- **THEN** the claim is backed by a per-page manifest with extraction method, text length, quality metrics, and review flags
- **AND** scanned or low-quality pages are marked for OCR, second-pass extraction, or human review
- **AND** the lifecycle document update summarizes repository-specific mapping only, not copyrighted or private source text

#### Scenario: A maintainer uses saved web pages as references

- **GIVEN** the maintainer uses saved HTML pages under a local reference directory
- **WHEN** the maintainer claims that article bodies were correctly read
- **THEN** the claim is backed by a per-HTML manifest with title, extracted text length, extraction method, quality metrics, and review flags
- **AND** the result is treated as extracted text until a reviewer confirms that it is the correct article body

### Requirement: Knowledge-Base Boundaries Are Explicit

The repository SHALL keep platform knowledge, project knowledge, and cross-project data exchange boundaries explicit.

#### Scenario: A project wants to reuse platform evidence or tooling facts

- **GIVEN** a consumer project needs platform-level tool or governance knowledge
- **WHEN** the data crosses project boundaries
- **THEN** the data is referenced read-only or exported explicitly
- **AND** the cross-project record includes source project, source path, optional source commit, timestamp, scope, classification, and provenance
- **AND** project business facts are not written into platform source truth by default

### Requirement: Reusable External Tool Candidates Are Inventoried Before Copying

The repository SHALL inventory reusable tool candidates from external local projects before copying or adapting them into this repository.

#### Scenario: A maintainer checks an external local project for reusable extraction tools

- **GIVEN** an external local project may contain document, PDF, HTML, or OCR helper scripts and third-party binaries
- **WHEN** the maintainer evaluates reuse for this repository
- **THEN** the repository records a read-only inventory report first
- **AND** generated outputs, cached dependencies, and project-specific artifacts are not copied as source truth
- **AND** third-party binaries are treated as installable local tools or adapters, not as repo source files by default
