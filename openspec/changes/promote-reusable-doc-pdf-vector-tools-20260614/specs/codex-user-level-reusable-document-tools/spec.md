## ADDED Requirements

### Requirement: User-Level Document Tools Keep Consumer State External

The repository SHALL provide reusable document/PDF/vector tooling source that keeps consumer data, filled configuration, source-authority policy, guard rules, permissions, and output paths outside the shared tool source.

#### Scenario: Consumer project uses reusable document tools

- **GIVEN** a consumer project has its own data, config, guard, and output policy
- **WHEN** it invokes the reusable document tooling from this repository
- **THEN** the tool accepts explicit config and output roots
- **AND** it does not default to `D:/project` as a data, output, guard, or authority root.

### Requirement: Poppler Is Discoverable Without Tracking Third-Party Binaries

The repository SHALL provide Poppler discovery and execution helpers while keeping third-party Poppler binaries as local ignored dependencies or caller-provided paths.

#### Scenario: Portable Poppler is cached for observation

- **GIVEN** a portable Poppler copy exists under an ignored local cache
- **WHEN** the PDF helpers run with that Poppler `bin` path
- **THEN** they can execute `pdfinfo` and rendering commands
- **AND** the portable binary payload is not treated as tracked repository source.

### Requirement: Vector Retrieval Framework Is Config Driven

The repository SHALL provide generic local vector/retrieval framework helpers that require explicit consumer configuration for stores, manifests, and embedding endpoints.

#### Scenario: Manifest validation runs without consumer data

- **GIVEN** a temporary JSONL manifest and no project-local database
- **WHEN** the generic vector toolkit validates or exact-searches the manifest
- **THEN** it reports structured success or errors
- **AND** it does not read consumer data paths unless explicitly configured.
