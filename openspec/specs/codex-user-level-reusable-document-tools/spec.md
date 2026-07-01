# codex-user-level-reusable-document-tools Specification

## Purpose
Define reusable document-tool requirements for local/offline evidence generation, review sidecars, and source-safe runtime boundaries that can be reused by consumer projects without moving project business data into shared tooling.

## Requirements
### Requirement: PPT Visual Review Sidecar Produces Portable Local Review Artifacts

The reusable document tooling SHALL provide a local/offline PPT visual review sidecar that creates portable review artifacts from rendered slide PNGs without modifying the source PPTX.

#### Scenario: Review session is built from slide PNGs

- **GIVEN** a directory of slide PNGs and an optional source PPTX path
- **WHEN** the operator runs the PPT review tool with an output directory
- **THEN** the tool SHALL write `session_manifest.json`, `comments.json`, `review_report.json`, and `review_report.html`
- **AND** the manifest SHALL include source input metadata, slide count, copied slide images, and output artifact names.

#### Scenario: Region comments are normalized

- **GIVEN** raw review comments with slide number, normalized ROI, severity, category, issue text, and optional suggested fix
- **WHEN** the tool normalizes the comments
- **THEN** each comment SHALL include stable `slide`, `roi`, `severity`, `category`, `comment`, `suggested_fix`, `status`, and timestamp fields
- **AND** invalid ROI coordinates SHALL fail closed instead of producing misleading visual evidence.

#### Scenario: Offline report is generated

- **GIVEN** a review session and comments
- **WHEN** the HTML report is written
- **THEN** it SHALL embed or reference only local session data and assets
- **AND** it SHALL NOT depend on external CDN, HTTP, or HTTPS resources.

### Requirement: PPT Visual Review Tool Preserves Source and Runtime Boundaries

The reusable document tooling SHALL keep PPT review outputs, rendered slide images, and source decks outside tracked shared-tool source unless explicitly supplied as tests or examples.

#### Scenario: Source deck is reviewed read-only

- **GIVEN** a source PPTX path is provided
- **WHEN** the review session is created
- **THEN** the source PPTX SHALL be recorded as provenance metadata
- **AND** the tool SHALL NOT edit, rewrite, or add native comments to that source PPTX.
