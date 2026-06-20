## ADDED Requirements

### Requirement: Full Body Operations Package Generates Codex Forty Eight Documents

The operations-package runtime SHALL generate the Codex CLI personal production durable-team full-body document layer as exactly 48 English primary body documents and 48 zh-CN companion body documents.

#### Scenario: Codex full-body layer is generated

- **GIVEN** the tracked Codex durable-team authority defines 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books
- **WHEN** `tools/generate_operations_package.py --package codex` runs in write mode
- **THEN** it SHALL generate 48 Codex English primary body documents under `docs_bilingual/operations_packages/codex_cli_durable_team/`
- **AND** it SHALL generate 48 matching zh-CN companion body documents
- **AND** the 48 count SHALL be treated as generated body-document count, not merely a register row count.

#### Scenario: Codex full-body layer is checked

- **GIVEN** the Codex body layer has been generated
- **WHEN** `tools/check_operations_package_docs.py` validates the repository
- **THEN** it SHALL fail if the Codex body primary count is not 48
- **AND** it SHALL fail if the Codex body companion count is not 48
- **AND** it SHALL fail if any Codex body document pair is missing from `docs_bilingual/docs_registry.yaml`.

### Requirement: Full Body Operations Package Generates One Person Company Sixty Documents

The operations-package runtime SHALL generate the personal production one-person-company full-body document layer as exactly 60 English primary body documents and 60 zh-CN companion body documents.

#### Scenario: One-person-company full-body layer is generated

- **GIVEN** the tracked one-person-company authority defines 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimum startup documents
- **WHEN** `tools/generate_operations_package.py --package one-person-company` runs in write mode
- **THEN** it SHALL generate 60 one-person-company English primary body documents under `docs_bilingual/operations_packages/one_person_company/`
- **AND** it SHALL generate 60 matching zh-CN companion body documents
- **AND** the 60 count SHALL be treated as generated body-document count, not merely a register row count.

#### Scenario: One-person-company full-body layer is checked

- **GIVEN** the one-person-company body layer has been generated
- **WHEN** `tools/check_operations_package_docs.py` validates the repository
- **THEN** it SHALL fail if the one-person-company body primary count is not 60
- **AND** it SHALL fail if the one-person-company body companion count is not 60
- **AND** it SHALL fail if any one-person-company body document pair is missing from `docs_bilingual/docs_registry.yaml`.

### Requirement: Full Body Documents Use Process Group Inputs Tools And Outputs

Every generated full-body operations-package document SHALL expose a process-group style execution contract.

#### Scenario: Body document structure is validated

- **GIVEN** a generated body document is part of the Codex or one-person-company body layer
- **WHEN** the checker validates that document
- **THEN** the English primary document SHALL contain `Inputs`, `Tools And Techniques`, and `Outputs` sections in that order
- **AND** each section SHALL contain non-empty content
- **AND** the zh-CN companion SHALL contain localized input, tools and techniques, and output sections in that order
- **AND** each localized section SHALL contain non-empty content.

### Requirement: Full Body Documents Preserve Tailoring Decisions

Every generated full-body operations-package document SHALL make architecture tailoring explicit and checkable.

#### Scenario: Tailoring language is checked

- **GIVEN** a generated body document is part of the Codex or one-person-company body layer
- **WHEN** the checker validates the document
- **THEN** it SHALL require all five tailoring modes: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid architecture
- **AND** it SHALL require rationale explaining why the selected or default mode is not heavier or lighter
- **AND** it SHALL require escalation trigger language.

### Requirement: Full Body Runtime Keeps Package Isolation And Idempotency

The full-body operations-package runtime SHALL remain deterministic, package-specific, and locally checkable.

#### Scenario: Package-specific write mode is used

- **GIVEN** a caller selects `--package codex`
- **WHEN** the generator writes files
- **THEN** it SHALL write only Codex package files
- **AND** it SHALL NOT write one-person-company body files.

#### Scenario: Idempotency is checked

- **GIVEN** generated files are current
- **WHEN** the generator runs again in write mode and then check mode
- **THEN** the second write SHALL report no content drift
- **AND** the check mode SHALL return success.
