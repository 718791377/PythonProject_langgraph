## ADDED Requirements

### Requirement: Repository Publication SHALL Prefer Local-First Runner Budgeting

The repository publication workflow SHALL conserve GitLab runner minutes by defaulting to local-first validation and batching before remote push.

#### Scenario: Related local changes are ready for review

- **GIVEN** a maintainer has related changes on one feature branch
- **AND** the changes share one topic, validation surface, and rollback boundary
- **WHEN** local validation passes
- **THEN** the maintainer MAY push the branch once and open or update one GitLab MR
- **AND** the GitLab pipeline remains the merge gate before GitLab `main`

#### Scenario: Unrelated changes would be batched only to save runner minutes

- **GIVEN** two changes have different review topics or rollback boundaries
- **WHEN** a maintainer considers batching them only to reduce GitLab runner-minute usage
- **THEN** the workflow SHALL require separate branches or separate MRs
- **AND** reviewability and rollback safety SHALL take priority over CI quota savings

#### Scenario: Early remote pipeline is explicitly requested

- **GIVEN** local validation is not yet complete
- **WHEN** the user explicitly requests an early GitLab pipeline check
- **THEN** the maintainer MAY push early
- **AND** the exception SHALL not become the default workflow for routine checkpoints
