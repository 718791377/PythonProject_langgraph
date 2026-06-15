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

### Requirement: PMI tailoring and execution grammar authority
Lifecycle, whitepaper, research, and North Star refreshes that use PMI evidence SHALL distinguish strategic narrative from execution grammar and SHALL record explicit tailoring rules for full, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid governance.

#### Scenario: Execution-facing lifecycle layer is updated
- **WHEN** a lifecycle layer or delivery gate drives execution
- **THEN** the receiving document states Inputs, Tools and Techniques, and Outputs
- **AND** records whether the full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid outcome applies to the affected scope

#### Scenario: PMI editions and practice guides are referenced
- **WHEN** PMBOK, Process Groups, Agile, program, portfolio, or PMO sources are referenced
- **THEN** the document states the primary overlay and supplemental role
- **AND** avoids expanding older editions unless they add execution vocabulary, continuity, translation clarity, or historical comparison
- **AND** states entry and exit conditions for Agile, program, portfolio, and PMO overlays.

### Requirement: Bilingual UTF-8 document integrity
Paired English and zh-CN documents updated by this change SHALL preserve the same governance decisions and SHALL NOT contain mojibake or replacement-marker additions.

#### Scenario: zh-CN document is touched
- **WHEN** a zh-CN tracked document is updated
- **THEN** the changed text is valid UTF-8 Chinese or intentional technical terminology
- **AND** no newly added three-ASCII-question-mark or replacement-character text remains
- **AND** English-only governance additions have a zh-CN counterpart when the paired document exists.
