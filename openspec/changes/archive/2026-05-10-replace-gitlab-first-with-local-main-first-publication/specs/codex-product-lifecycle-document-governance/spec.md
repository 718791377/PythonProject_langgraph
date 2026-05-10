## MODIFIED Requirements

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
