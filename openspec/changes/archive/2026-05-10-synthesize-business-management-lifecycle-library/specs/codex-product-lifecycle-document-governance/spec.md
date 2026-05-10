# codex-product-lifecycle-document-governance Specification Delta

## MODIFIED Requirements

### Requirement: Product Lifecycle Reference Defines The 0-11 / 12-Layer Document Stack

The repository SHALL maintain a bilingual product lifecycle reference that defines the cognitive narrative, business, market, strategy, metrics, product, technical, organization, execution, growth, operations, and retrospective layers. The reference SHALL also summarize repository-specific lessons synthesized from the local `Business Management/` source library without reproducing long source passages.

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** the maintainer reads the product lifecycle reference
- **WHEN** the maintainer compares document types
- **THEN** the reference explains that a white paper changes cognition and frames why the direction exists
- **AND** the reference explains that a North Star plan belongs in the metrics layer and turns strategy into measurable direction, input metrics, guardrails, and staged decision thresholds

#### Scenario: A maintainer applies the Business Management source library

- **GIVEN** the maintainer reads the product lifecycle reference
- **WHEN** the maintainer needs source-backed lifecycle guidance
- **THEN** the reference maps the local Business Management library themes to cognition, business, market discovery, strategy, metrics, product, technical architecture, organization, execution, growth, operations, and learning loops
- **AND** it expresses the guidance as repository-specific operating rules rather than source-book excerpts

### Requirement: Platform Build And Project Consumption Stay Separate

The repository SHALL document the Codex CLI durable-team platform-build lifecycle separately from the lifecycle for later projects that consume the platform. Both lifecycles SHALL use the shared source-library synthesis only as a governance overlay and SHALL keep platform runtime truth separate from downstream business runtime truth.

#### Scenario: A later project uses the platform templates

- **GIVEN** the later project receives templates, user-level runtime policies, and subagent profiles
- **WHEN** it starts its own work
- **THEN** it owns its own `AGENTS.md`, which is the project-level Codex instruction file
- **AND** it owns its own `openspec/`, which is the project-local OpenSpec governance tree
- **AND** it owns its own `.omx/state/`, which is the project-local durable truth directory
