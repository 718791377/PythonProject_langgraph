# codex-user-level-team-mode-controls Specification

## Purpose
TBD - created by archiving change implement-codex-user-level-team-mode-p0-controls. Update Purpose after archive.
## Requirements
### Requirement: The repository SHALL provide a repo-local installer for user-level team-mode control assets

The repository SHALL provide an installer or generator that renders user-level Codex team-mode control assets into an explicit target Codex home path without requiring direct writes to the real user home during repository development.

The generated asset set SHALL include at least:

- `agents/team-leader.toml` - user-level native-agent profile for the current main Codex CLI leader role.
- `bin/_codex-user-level-team-mode.ps1` - shared PowerShell helper used by generated team-mode control wrappers.
- `bin/codex-omx-on.ps1` - user-level script that enables the oh-my-codex workflow layer.
- `bin/codex-omx-off.ps1` - user-level script that disables the oh-my-codex workflow layer.
- `bin/codex-omx-status.ps1` - user-level script that reports the oh-my-codex workflow-layer state.
- `bin/codex-subagents-auto.ps1` - user-level script that sets expert routing to automatic mode.
- `bin/codex-subagents-manual.ps1` - user-level script that sets expert routing to manual mode.
- `bin/codex-subagents-off.ps1` - user-level script that disables expert routing.
- `bin/codex-routing-status.ps1` - user-level script that reports current routing posture and switches.
- `state/user-level-team-mode.json` - user-level state file storing layered team-mode capability switches.

#### Scenario: Generate the P0 control layer into a temporary Codex home

- **WHEN** the installer is run with an explicit target Codex home path
- **THEN** it SHALL create the required additive assets under that target path
- **AND** it SHALL keep the generation logic reusable across arbitrary project repositories on the same user profile

### Requirement: The installer SHALL preserve the native Codex base layer

The installer SHALL NOT create, replace, or modify the native base entrypoint names:

- `codex` - bare Codex entrypoint name checked for command shadowing and compatibility.
- `codex.cmd` - Windows command-shim form of the Codex CLI entrypoint.
- `codex.ps1` - PowerShell wrapper form of the Codex CLI entrypoint.

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

- `oh_my_codex = off` - default switch value that disables the oh-my-codex workflow layer.
- `subagent_routing = auto` - default switch value that enables automatic expert routing.

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

### Requirement: Generated controls SHALL expose a native-subagent limit surface

The user-level installer SHALL generate an additive control asset that exposes the managed native-subagent fan-out limits used by this workflow.

That generated asset SHALL allow the operator to inspect, and where supported manage, `agents.max_threads` and `agents.max_depth` without modifying the native `codex`, `codex.cmd`, or `codex.ps1` base entrypoints.

#### Scenario: Installer renders additive limit controls

- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate a native-subagent limit control asset
- **AND** that asset SHALL keep the native Codex base entrypoints unchanged

### Requirement: Generated controls SHALL persist the durable orchestration backend selection

The generated user-level control surface SHALL persist the durable orchestration backend as a separate explicit selector.

At minimum the selector SHALL support:

- `native_omx` - durable backend family for worker-centric oh-my-codex execution.
- `langgraph` - durable backend family for graph-shaped checkpointed execution.

The default durable orchestration backend SHALL remain the current native path until LangGraph is explicitly selected.

#### Scenario: Fresh install preserves the current backend by default

- **WHEN** the installer creates a fresh user-level control state
- **THEN** the durable orchestration backend selector SHALL default to `native_omx`
- **AND** LangGraph SHALL remain additive rather than replacing the current durable path automatically

#### Scenario: Backend status surface reports the full user-level backend policy contract

- **WHEN** the operator runs the generated backend status surface after installation
- **THEN** it SHALL report the selected backend, the stable default backend, and the preferred use cases for `native_omx` and `langgraph`
- **AND** it SHALL report that backend-family switching remains explicit or manual-only
- **AND** it SHALL report that one durable task stays within one backend family
- **AND** it SHALL identify the supporting user-level policy surfaces that repeat the same contract

### Requirement: Generated controls SHALL distinguish enabled capability layers from the effective execution lane

The generated user-level controls SHALL distinguish:

- which orchestration capability layers are enabled
- which effective execution lane a given task flow is using

They SHALL not treat those two concepts as the same field.

#### Scenario: Operator inspects user-level control output

- **WHEN** the operator inspects the generated user-level control surfaces
- **THEN** the surfaces SHALL distinguish enabled capability layers from the effective lane
- **AND** they SHALL not require a global backend flip for every task-flow-specific lane choice

### Requirement: Managed install backup and rollback SHALL include verifier and debugger specialist profiles when generated

When the installer manages `verifier.toml` and `debugger.toml`, those files SHALL be included in the managed asset write, backup snapshot, and rollback surface.

#### Scenario: A managed install is rolled back after verifier or debugger assets were targeted

- **WHEN** the installer targets managed verifier and debugger profiles and then fails after backup creation
- **THEN** rollback SHALL restore or remove those targeted verifier and debugger assets consistently with the rest of the managed asset set

### Requirement: Managed install backup and rollback SHALL include researcher, dependency-expert, and writer specialist profiles when generated

When the installer manages `researcher.toml`, `dependency-expert.toml`, and `writer.toml`, those files SHALL be included in the managed asset write, backup snapshot, and rollback surface.

#### Scenario: A managed install is rolled back after the new specialist assets were targeted

- **WHEN** the installer targets managed researcher, dependency-expert, and writer profiles and then fails after backup creation
- **THEN** rollback SHALL restore or remove those targeted specialist assets consistently with the rest of the managed asset set

### Requirement: Release gates SHALL prove native Codex preservation and rollback evidence before production marking

Before a user-level team-mode installer, launcher, or publication slice is marked production-ready, the repository SHALL provide a release gate that requires evidence for native Codex preservation, backup snapshots, rollback behavior, and config rewrite sentinel status.

The release gate SHALL remain read-only by default and SHALL NOT install into the real user Codex home unless a separate reviewed change and explicit operator consent allow it.

The release gate SHALL protect these native Codex entrypoint names:

- `codex` - native Codex base command name.
- `codex.cmd` - Windows npm shim name for native Codex.
- `codex.ps1` - PowerShell shim name that must not be replaced by this repository.

#### Scenario: A release candidate lacks rollback evidence

- **WHEN** a release candidate changes user-level team-mode installer or launcher behavior
- **AND** no release-gate evidence records backup snapshot and rollback validation
- **THEN** the release SHALL NOT be marked production-ready
- **AND** the operator SHALL keep using the stable native Codex or raw bypass entrypoints

#### Scenario: A release gate is checked in CI

- **WHEN** the aggregate OpenSpec guard runs in CI or local verification
- **THEN** it SHALL validate the release-gate template and static repository evidence
- **AND** it SHALL NOT mutate `C:\Users\lenovo\.codex\config.toml` or any real user-level Codex asset

### Requirement: Release gates SHALL keep manual rollback evidence explicit

The release gate SHALL include a manual rollback path field that points to backup snapshot evidence or documented restore steps.

It SHALL distinguish automatic rollback-on-error evidence from manual version rollback evidence.

#### Scenario: Backup snapshots exist but manual rollback is undocumented

- **WHEN** backup snapshot behavior exists in the installer
- **AND** the release gate lacks a manual rollback path or restore evidence
- **THEN** the release SHALL remain blocked from production marking
- **AND** the gap SHALL be recorded as a release hardening task rather than silently accepted
