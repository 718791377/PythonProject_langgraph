# codex-product-lifecycle-document-governance Specification

## Purpose
Define the product and business document lifecycle map for this repository, and keep Codex platform-build documentation separate from downstream project-consumption documentation.
## Requirements
### Requirement: Product Lifecycle Reference Defines The 0-8 Document Stack

The repository SHALL maintain a bilingual product lifecycle reference that defines the cognitive narrative, business, market, strategy, product, technical, execution, growth, and retrospective layers.

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** the maintainer reads the product lifecycle reference
- **WHEN** the maintainer compares document types
- **THEN** the reference explains that a white paper changes cognition and frames why the direction exists
- **AND** the reference explains that a North Star plan turns strategy into measurable direction, metrics, levers, and staged execution

### Requirement: Platform Build And Project Consumption Stay Separate

The repository SHALL document the Codex CLI durable-team platform-build lifecycle separately from the lifecycle for later projects that consume the platform.

#### Scenario: A later project uses the platform templates

- **GIVEN** the later project receives templates, user-level runtime policies, and subagent profiles
- **WHEN** it starts its own work
- **THEN** it owns its own `AGENTS.md`, which is the project-level Codex instruction file
- **AND** it owns its own `openspec/`, which is the project-local OpenSpec governance tree
- **AND** it owns its own `.omx/state/`, which is the project-local durable truth directory

### Requirement: Platform Documents May Define Shared Governance But Not Business Runtime Truth

The Codex platform repository SHALL define reusable governance, templates, checkers, role policies, release gates, and shared tooling, but SHALL NOT become the repo-local durable truth for downstream business projects.

#### Scenario: A business project learns a reusable governance lesson

- **GIVEN** the lesson originates in a downstream business project
- **WHEN** the lesson is generic enough to improve the platform
- **THEN** the project records it as upstream feedback first
- **AND** the platform adopts it only through a platform OpenSpec change

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
