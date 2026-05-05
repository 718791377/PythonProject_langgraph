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
