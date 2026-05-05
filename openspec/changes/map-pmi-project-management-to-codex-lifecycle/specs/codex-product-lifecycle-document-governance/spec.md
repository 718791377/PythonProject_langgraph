# codex-product-lifecycle-document-governance Specification Delta

## ADDED Requirements

### Requirement: PMI References Are A Governance Overlay

The repository SHALL treat PMI project-management references as a governance overlay for delivery, tailoring, quality, risk, change control, and closing rather than as a replacement for the product and business lifecycle.

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** the maintainer uses `PMP/` as a local private reference directory
- **WHEN** the maintainer updates repository lifecycle documentation
- **THEN** the update summarizes repository-specific mappings only
- **AND** the update does not reproduce PMI book content
- **AND** the local `PMP/` reference directory remains ignored by Git

### Requirement: Process Groups Map To OpenSpec Delivery Gates

The repository SHALL map the PMI process group model to OpenSpec and GitLab-first delivery gates.

#### Scenario: A platform change moves from idea to archive

- **GIVEN** a platform change is managed through OpenSpec and GitLab
- **WHEN** the change is planned and delivered
- **THEN** initiating maps to proposal and charter-like scope definition
- **AND** planning maps to design, tasks, risks, validation, release, and rollback planning
- **AND** executing maps to implementation work
- **AND** monitoring and controlling maps to checkers, pipeline, diff review, and change control
- **AND** closing maps to archive, stable spec sync, and lessons learned

### Requirement: Agile Guidance Supports Exploratory And Hybrid Work

The repository SHALL use agile guidance for uncertain, exploratory, MVP, and feedback-driven work, while keeping predictive process gates for high-risk or clearly scoped delivery.

#### Scenario: A task is not yet clear enough for implementation

- **GIVEN** the requested work has unresolved market, product, or technical uncertainty
- **WHEN** the leader selects an execution approach
- **THEN** the work starts with a small exploration, spike, or MVP slice
- **AND** the work does not launch a durable team until the plan is frozen and independent execution slices exist
