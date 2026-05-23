## MODIFIED Requirements
### Requirement: Local Reference Coverage Is Summarized Without Reproducing Source Text

The repository SHALL summarize local Business Management and PMP reference coverage by file, format, page count, spine item count, and reading method without committing extracted source text or reproducing long copyrighted passages. When a fresh-read refresh is requested, the repository SHALL regenerate ignored extraction artifacts for that run before updating tracked synthesis docs.

#### Scenario: A maintainer audits source-backed lifecycle updates

- **GIVEN** the maintainer reads the source synthesis documents
- **WHEN** they check how the reference libraries were used
- **THEN** the documents state that PDFs were read by page, EPUBs by spine item, and Markdown files by full text
- **AND** they summarize repository-specific governance mappings only
- **AND** ignored extraction artifacts remain outside tracked Git files
- **AND** the tracked docs do not rely on old extraction caches as the evidence for the current refresh

### Requirement: Lifecycle Governance Defines Two 12-Layer Target Architectures

The repository SHALL define two explicit 12-layer architecture targets derived from the local Business Management and PMP source libraries: the Codex CLI personal production durable-team target and the personal production one-person-company operating-system target. The repository SHOULD keep canonical inventory maps for these targets so repeated count statements do not drift across lifecycle, whitepaper, MRD, and implementation-plan documents.

#### Scenario: A maintainer compares the two targets

- **GIVEN** the maintainer reads the product lifecycle documents
- **WHEN** they compare the Codex platform target with the one-person-company target
- **THEN** the Codex platform target lists 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books
- **AND** the one-person-company target lists 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents
- **AND** the docs identify which inventory document is canonical for each target

### Requirement: Lifecycle Tailoring Rules Define Full And Lightweight Architecture Use

The repository SHALL define explicit lifecycle tailoring rules for when to use the full 12-layer target architecture and when to use a lightweight architecture. The rules SHALL distinguish whole-project lightweight tailoring, phase-local lightweight tailoring, module-level lightweight tailoring, and escalation back to fuller governance. The rules SHALL also state whether lightening applies to the whole project, a phase, a gate, or a module.

#### Scenario: A maintainer chooses governance depth for a lifecycle-guided change

- **GIVEN** the maintainer reads the product lifecycle tailoring guidance
- **WHEN** the work affects money, users, trust, compliance, security, data, runtime entrypoints, release safety, cross-project templates, durable state, shared interfaces, or long-lived platform behavior
- **THEN** the guidance requires a full architecture path for the affected scope
- **AND** the guidance may still allow unaffected low-risk phases or modules to stay lightweight when their boundaries and rollback evidence are explicit

#### Scenario: A maintainer uses a lightweight path safely

- **GIVEN** the requested work is a small local note, low-risk internal tool, one-off spike, reversible documentation experiment, or early idea without external users, money, trust boundary, compliance impact, or durable-state change
- **WHEN** the maintainer selects a lightweight path
- **THEN** the guidance states whether the whole project, a local phase, or a module is lightweight
- **AND** it records Inputs, Tools and Techniques, and Outputs for the tailoring decision
- **AND** it defines escalation triggers if risk, uncertainty, coupling, adoption, release impact, or stakeholder impact grows
