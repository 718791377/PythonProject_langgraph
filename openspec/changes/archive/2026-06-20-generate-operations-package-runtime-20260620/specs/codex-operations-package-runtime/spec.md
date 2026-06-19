## ADDED Requirements

### Requirement: Operations Package Runtime Generates Governed Bilingual Packages

The repository SHALL provide a deterministic operations-package runtime that generates and validates governed bilingual operations packages for both the Codex CLI personal production durable team and personal production one-person-company operations systems.

#### Scenario: Codex durable-team package is generated

- **GIVEN** the Codex durable-team source authorities define 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books
- **WHEN** the operations-package generator runs for the Codex durable-team package
- **THEN** it SHALL generate bilingual package documents that preserve those counts and map documents, domains, agents, modules, and books to the existing authority stack
- **AND** it SHALL NOT merge the one-person-company 60-document operating system into the Codex durable-team package.

#### Scenario: One-person-company package is generated

- **GIVEN** the one-person-company source authorities define 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents
- **WHEN** the operations-package generator runs for the one-person-company package
- **THEN** it SHALL generate bilingual package documents that preserve those counts and explicitly identify the 12-document minimum startup path
- **AND** it SHALL distinguish minimum startup, lightweight, hybrid, and full operating packages.

### Requirement: Operations Package Tailoring Is Explicit And Checkable

The operations package SHALL define checkable architecture tailoring rules for full, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid architecture modes.

#### Scenario: Project architecture mode is selected

- **GIVEN** a project has risk, duration, external commitment, compliance, revenue, publication, durable-state, or multi-agent attributes
- **WHEN** the tailoring decision is recorded
- **THEN** the decision SHALL state why the selected architecture mode is not heavier or lighter
- **AND** it SHALL identify escalation triggers that move lightweight work toward hybrid or full architecture.

### Requirement: Execution-Facing Flows Use Process-Group Inputs Tools Outputs

Every execution-facing operations-package document SHALL expose process-group style Inputs, Tools And Techniques, and Outputs sections.

#### Scenario: Required generated document is checked

- **GIVEN** a required generated operations-package document is part of the Stage B output
- **WHEN** `tools/check_operations_package_docs.py` validates the package
- **THEN** the checker SHALL fail if required English documents omit `Inputs`, `Tools And Techniques`, or `Outputs`
- **AND** it SHALL fail if required Chinese companion documents omit equivalent localized headings.

### Requirement: Two-Stage Local Main Delivery Is Preserved

The operations-package work SHALL be delivered as two serial local-main-first packages.

#### Scenario: Stage A completes

- **GIVEN** Stage A creates only plan, OpenSpec, and registry artifacts
- **WHEN** Stage A validation passes
- **THEN** Stage A SHALL be committed and integrated into local `main` before Stage B runtime implementation begins.

#### Scenario: Stage B completes

- **GIVEN** Stage A has landed on local `main`
- **WHEN** Stage B implements generated documents, runtime, checker, tests, and registry updates
- **THEN** Stage B SHALL be validated, committed, and integrated into local `main`
- **AND** the repository SHALL stop at the remote-publication gate unless the user explicitly authorizes remote publication.
