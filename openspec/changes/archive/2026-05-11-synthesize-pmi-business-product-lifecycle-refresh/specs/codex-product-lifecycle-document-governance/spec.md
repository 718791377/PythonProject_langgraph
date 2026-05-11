# codex-product-lifecycle-document-governance Delta

## ADDED Requirements

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
