# codex-product-lifecycle-document-governance Specification

## Purpose
Define the product and business document lifecycle map for this repository, and keep Codex platform-build documentation separate from downstream project-consumption documentation.
## Requirements
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

The repository SHALL map the PMI process group model to OpenSpec and local-main-first delivery gates.

#### Scenario: A platform change moves from idea to archive

- **GIVEN** a platform change is managed through OpenSpec and local-main-first publication
- **WHEN** the change is planned and delivered
- **THEN** initiating maps to proposal and charter-like scope definition
- **AND** planning maps to design, tasks, risks, validation, release, and rollback planning
- **AND** executing maps to implementation work
- **AND** monitoring and controlling maps to local checkers, optional remote pipeline confirmation, diff review, and change control
- **AND** closing maps to archive, stable spec sync, local `main` integration, mirror sync, and lessons learned

### Requirement: Agile Guidance Supports Exploratory And Hybrid Work

The repository SHALL use agile guidance for uncertain, exploratory, MVP, and feedback-driven work, while keeping predictive process gates for high-risk or clearly scoped delivery.

#### Scenario: A task is not yet clear enough for implementation

- **GIVEN** the requested work has unresolved market, product, or technical uncertainty
- **WHEN** the leader selects an execution approach
- **THEN** the work starts with a small exploration, spike, or MVP slice
- **AND** the work does not launch a durable team until the plan is frozen and independent execution slices exist

### Requirement: Platform White Paper And MRD Are First-Class Lifecycle Documents

The repository SHALL maintain first-class bilingual white paper and MRD documents for the Codex CLI personal production durable-team platform before treating downstream implementation plans as complete lifecycle coverage.

#### Scenario: A maintainer follows the lifecycle stack

- **GIVEN** the maintainer reads the platform lifecycle documentation
- **WHEN** the maintainer needs the cognitive narrative and market requirements
- **THEN** the maintainer can find the canonical white paper under `docs_bilingual/whitepapers/`, which is the white-paper directory
- **AND** the maintainer can find the MRD under `docs_bilingual/market_requirements/`, which is the market-requirements directory
- **AND** concrete workload-to-profile mappings are available inside the MRD appendix rather than a separate implementation-plan reference

### Requirement: Lifecycle Governance Defines Two 12-Layer Target Architectures

The repository SHALL define two explicit 12-layer architecture targets derived from the local Business Management and PMP source libraries: the Codex CLI personal production durable-team target and the personal production one-person-company operating-system target.

#### Scenario: A maintainer compares the two targets

- **GIVEN** the maintainer reads the product lifecycle documents
- **WHEN** they compare the Codex platform target with the one-person-company target
- **THEN** the Codex platform target lists 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books
- **AND** the one-person-company target lists 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents

### Requirement: Execution-Facing Lifecycle Guidance Uses Process-Group Style

Lifecycle guidance that affects execution SHALL be written in a process-group style that separates Inputs, Tools and Techniques, and Outputs for every layer or delivery gate.

#### Scenario: A maintainer plans a lifecycle-guided change

- **GIVEN** the maintainer uses the lifecycle documents for execution planning
- **WHEN** they inspect a lifecycle layer or delivery gate
- **THEN** the guidance states the inputs used to start work
- **AND** it states the tools and techniques used to analyze, decide, execute, monitor, or close the work
- **AND** it states the outputs that become deliverables, evidence, or inputs to another layer

### Requirement: Local Reference Coverage Is Summarized Without Reproducing Source Text

The repository SHALL summarize local Business Management and PMP reference coverage by file, format, page count, spine item count, and reading method without committing extracted source text or reproducing long copyrighted passages.

#### Scenario: A maintainer audits source-backed lifecycle updates

- **GIVEN** the maintainer reads the source synthesis documents
- **WHEN** they check how the reference libraries were used
- **THEN** the documents state that PDFs were read by page, EPUBs by spine item, and Markdown files by full text
- **AND** they summarize repository-specific governance mappings only
- **AND** ignored extraction artifacts remain outside tracked Git files
