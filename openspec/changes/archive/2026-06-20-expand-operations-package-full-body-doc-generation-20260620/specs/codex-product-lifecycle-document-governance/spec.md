## ADDED Requirements

### Requirement: Product Lifecycle Governance Covers Full Body Operations Documents

The product lifecycle document governance SHALL treat generated operations-package body documents as execution-facing lifecycle artifacts governed by the 12-layer stack, process-group Inputs / Tools And Techniques / Outputs, and explicit tailoring decisions.

#### Scenario: A body document is generated from a core-document list

- **GIVEN** a Codex or one-person-company core-document list defines a document family and filename
- **WHEN** Stage B generates the corresponding body document
- **THEN** the document SHALL identify its 12-layer placement
- **AND** it SHALL expose Inputs, Tools And Techniques, and Outputs for execution-facing use
- **AND** it SHALL state how the document participates in full, lightweight, phase-local, module-level, or hybrid governance.

### Requirement: Tailoring May Be Whole Project Phase Local Module Level Or Hybrid

The lifecycle governance SHALL distinguish whole-project lightweight architecture from phase-local and module-level lightweight architecture, and SHALL allow hybrid architecture when only part of the project can safely be light.

#### Scenario: A project selects a lightweight scope

- **GIVEN** a project, phase, or module is being planned
- **WHEN** the operator records a tailoring decision
- **THEN** the decision SHALL state whether the entire project is lightweight, only one phase is lightweight, only one module is lightweight, or the overall approach is hybrid
- **AND** it SHALL state why the chosen scope is neither heavier nor lighter than needed
- **AND** it SHALL define escalation triggers for moving to hybrid or full architecture.

### Requirement: Registry Tracks Body Documents As First Class Artifacts

The bilingual document registry SHALL track generated body documents as first class lifecycle artifacts rather than treating them as unregistered runtime cache.

#### Scenario: A generated body document is added

- **GIVEN** the generator creates an English primary body document and a zh-CN companion
- **WHEN** the body layer is validated
- **THEN** `docs_bilingual/docs_registry.yaml` SHALL contain a unique `doc_id`
- **AND** it SHALL contain the English canonical path and zh-CN companion path
- **AND** the generated document SHALL be source-controlled Markdown, not an ignored cache file.
