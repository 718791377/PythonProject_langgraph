## ADDED Requirements

### Requirement: User-level document tool runtime confirmation

The repository SHALL maintain a follow-up confirmation record for the reusable document/PDF/vector tooling runtime before claiming live runtime completion.

#### Scenario: Stage 1 freezes confirmation scope

- **GIVEN** reusable document tooling source already exists under `tools/user_level_document_tools/`
- **WHEN** a follow-up confirmation package is opened
- **THEN** it SHALL identify the remaining live runtime gaps
- **AND** it SHALL separate shared source, local-only runtime cache, and consumer-owned state.

#### Scenario: Stage 2 verifies live runtime from the shared repository

- **GIVEN** the Stage 1 confirmation package is integrated into local `main`
- **WHEN** live runtime implementation proceeds
- **THEN** Poppler/PDF, document-pipeline, and vector/retrieval behavior SHALL be verified from `D:\PythonProject_langgraph`
- **AND** real consumer vector data, source authority, and generated outputs SHALL remain consumer-owned.

### Requirement: Consumer project no-drift boundary

The tooling migration confirmation SHALL treat `D:\project` as a guarded consumer/source-comparison project rather than the shared implementation authority.

#### Scenario: Consumer project has unrelated dirty files

- **GIVEN** `D:\project` contains unrelated dirty files
- **WHEN** migration confirmation or cleanup is performed
- **THEN** those dirty files SHALL NOT be overwritten or cleaned by this repository's implementation flow
- **AND** any consumer-side mutation SHALL use `D:\project` guard evidence.
