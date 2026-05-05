## ADDED Requirements

### Requirement: Startup-binding release gates SHALL include native, raw, and wrapped launcher smoke evidence

Before startup-binding changes are marked production-ready, the release gate SHALL require explicit local smoke evidence for the native Codex entrypoint, the stable raw bypass entrypoint, and the stable wrapped entrypoint.

The required release evidence SHALL include at least:

- `codex --version` as the native Codex smoke command
- `codex-raw --version` as the stable raw bypass smoke command
- a short `codex-ohmy` help or version check as the stable wrapped launcher smoke command

The static repository checker MAY validate that these evidence fields are present without running authenticated Codex sessions in CI.

#### Scenario: Wrapped launcher changes but raw bypass is not proven

- **WHEN** a startup-binding release candidate changes `codex-ohmy` wrapper behavior
- **AND** the release evidence does not include `codex-raw --version`
- **THEN** the release SHALL NOT be marked production-ready
- **AND** the operator SHALL keep the raw bypass as the recovery path

#### Scenario: CI validates the release-gate template

- **WHEN** CI runs the release-gate template checker
- **THEN** it SHALL verify that native, raw bypass, and wrapped launcher smoke evidence fields exist
- **AND** it SHALL NOT launch a long-running Codex session
