## ADDED Requirements

### Requirement: The repository SHALL provide a repo-local installer for user-level team-mode control assets

The repository SHALL provide an installer or generator that renders user-level Codex team-mode control assets into an explicit target Codex home path without requiring direct writes to the real user home during repository development.

The generated asset set SHALL include at least:

- `agents/team-leader.toml`
- `bin/_codex-user-level-team-mode.ps1`
- `bin/codex-omx-on.ps1`
- `bin/codex-omx-off.ps1`
- `bin/codex-omx-status.ps1`
- `bin/codex-subagents-auto.ps1`
- `bin/codex-subagents-manual.ps1`
- `bin/codex-subagents-off.ps1`
- `bin/codex-routing-status.ps1`
- `state/user-level-team-mode.json`

#### Scenario: Generate the P0 control layer into a temporary Codex home

- **WHEN** the installer is run with an explicit target Codex home path
- **THEN** it SHALL create the required additive assets under that target path
- **AND** it SHALL keep the generation logic reusable across arbitrary project repositories on the same user profile

### Requirement: The installer SHALL preserve the native Codex base layer

The installer SHALL NOT create, replace, or modify the native base entrypoint names:

- `codex`
- `codex.cmd`
- `codex.ps1`

This safety boundary applies even when the user-level team-mode assets are generated repeatedly.

#### Scenario: Existing native Codex sentinel files are present in the target home

- **WHEN** the installer runs against a Codex home that already contains `codex.cmd` or `codex.ps1`
- **THEN** those files SHALL remain unchanged
- **AND** the installer SHALL still generate only the additive team-mode assets

### Requirement: Generated controls SHALL persist `oh_my_codex` and `subagent_routing` as separate global states

The generated control surface SHALL persist `oh_my_codex` and `subagent_routing` separately in one shared state file.

The generated controls SHALL support at least these values:

- `oh_my_codex`: `on`, `off`
- `subagent_routing`: `auto`, `manual`, `off`

The default generated state SHALL be:

- `oh_my_codex = off`
- `subagent_routing = auto`

#### Scenario: Fresh install creates the default native-routed state

- **WHEN** the installer creates a new state file
- **THEN** the state SHALL default to `oh_my_codex=off`
- **AND** it SHALL default to `subagent_routing=auto`

#### Scenario: Operator toggles oh-my-codex without changing routing

- **WHEN** the operator runs `codex-omx-on.ps1` or `codex-omx-off.ps1`
- **THEN** only the `oh_my_codex` field SHALL change
- **AND** `subagent_routing` SHALL remain unchanged

#### Scenario: Operator toggles routing without changing oh-my-codex

- **WHEN** the operator runs `codex-subagents-auto.ps1`, `codex-subagents-manual.ps1`, or `codex-subagents-off.ps1`
- **THEN** only the `subagent_routing` field SHALL change
- **AND** `oh_my_codex` SHALL remain unchanged

#### Scenario: Pure debugging mode is derived from the two switches

- **WHEN** the persisted state becomes `oh_my_codex=off` and `subagent_routing=off`
- **THEN** the generated status surface SHALL report pure debugging mode
- **AND** it SHALL report role orchestration as unavailable

### Requirement: The generated leader profile SHALL represent the current main Codex CLI session

The generated `team-leader.toml` SHALL describe the current main Codex CLI session as the leader lane.

It SHALL NOT redefine the leader as a separate persistent worker pane.

#### Scenario: A maintainer inspects the generated leader profile

- **WHEN** the generated `team-leader.toml` is read
- **THEN** it SHALL describe the current main Codex CLI session as the team leader
- **AND** it SHALL keep worker semantics separate from leader semantics

### Requirement: The installer SHALL reject unmanaged collisions by default

If a target generated path already exists but is not marked as a managed team-mode asset, the installer SHALL fail rather than silently overwrite that file.

#### Scenario: A user already owns a conflicting wrapper path

- **WHEN** the installer encounters an unmanaged file at a generated asset path such as `bin/codex-omx-on.ps1`
- **THEN** the installer SHALL stop with an error by default
- **AND** it SHALL not overwrite the conflicting unmanaged file silently

### Requirement: The installer SHALL create backup snapshots and roll back partial failures

Before the installer writes any generated asset or creates the state file, it SHALL create a timestamped backup snapshot for every targeted managed path under a namespaced backup root inside the target Codex home.

If the installer fails after writes begin, it SHALL automatically restore the pre-install state for every targeted path and preserve the backup snapshot metadata for inspection.

#### Scenario: A failed reinstall restores the previous managed asset contents

- **WHEN** the installer has already begun updating managed team-mode assets and then hits a runtime failure
- **THEN** it SHALL restore every targeted managed path to its pre-install content or pre-install absence state
- **AND** it SHALL keep backup metadata available for diagnostics or later manual restore
- **AND** it SHALL leave native `codex`-named files unchanged

#### Scenario: A failed first install removes newly created managed files

- **WHEN** the installer runs against a target Codex home with no prior team-mode assets and fails after writing begins
- **THEN** it SHALL remove the newly created managed asset files during rollback
- **AND** it SHALL preserve the backup snapshot manifest that recorded the attempted install
