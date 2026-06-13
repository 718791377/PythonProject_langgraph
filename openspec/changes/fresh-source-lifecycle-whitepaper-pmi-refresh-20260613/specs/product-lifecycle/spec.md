# Delta: Product Lifecycle Fresh Source Evidence

## ADDED Requirements

### Requirement: Fresh source reading evidence for lifecycle refreshes
Lifecycle, whitepaper, research, and North Star refreshes that claim Business Management or PMP/PMI evidence SHALL record a fresh extraction run before updating tracked conclusions.

#### Scenario: PDF source is included
- **WHEN** a local PDF source is part of the refresh
- **THEN** the extraction evidence records one status row per page
- **AND** records whether `pypdf` or PyMuPDF/fitz was used for each page or file fallback

#### Scenario: EPUB source is included
- **WHEN** a local EPUB source is part of the refresh
- **THEN** the extraction evidence records one status row per spine item
- **AND** records skipped navigation or non-content items explicitly

#### Scenario: Markdown source is included
- **WHEN** a local Markdown source is part of the refresh
- **THEN** the extraction evidence records full-document reading status, hash, modified time, and character count

### Requirement: Whitepaper and research relationship preservation
The Codex durable-team whitepaper and solo-maintainable production persistent team research note SHALL remain separate unless a later governed change proves that one no longer has an independent lifecycle role.

#### Scenario: 10-layer and 12-layer models both appear
- **WHEN** tracked documents mention both models
- **THEN** they identify the 10-layer model as runtime/governance research view
- **AND** identify the 12-layer model as product/business lifecycle view
- **AND** provide a bridge rather than treating the models as contradictory.
