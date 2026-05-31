# codex-user-level-team-mode-startup-binding Specification

## Purpose
TBD - created by archiving change implement-codex-user-level-team-mode-p1-startup-binding. Update Purpose after archive.
## Requirements
### Requirement: The installer SHALL generate a PowerShell startup-binding launcher

The installer SHALL generate a launcher script that reads the persisted user-level team-mode state and computes Codex CLI runtime overrides for PowerShell-based `codex` launches.

The launcher SHALL preserve the native Codex executable path instead of replacing it.

#### Scenario: Startup-binding assets are generated into the target Codex home

- **WHEN** the installer runs for startup binding
- **THEN** it SHALL generate a launcher asset under the target Codex home
- **AND** the launcher SHALL know how to invoke the native Codex command path without recursion

### Requirement: The installer SHALL add a managed PowerShell profile block without replacing the native executable

The installer SHALL add a managed block to the selected PowerShell profile path that defines a wrapped `codex` function and a raw `codex-native` bypass function.

It SHALL NOT modify the npm-installed `codex`, `codex.cmd`, or `codex.ps1` files.

#### Scenario: A new PowerShell session loads the startup binding

- **WHEN** a PowerShell session loads the managed profile block
- **THEN** calling `codex` SHALL route through the generated launcher
- **AND** calling `codex-native` SHALL route directly to the native Codex command
- **AND** the native Codex installation files SHALL remain unchanged

### Requirement: The launcher SHALL map `oh_my_codex` state to startup behavior

The launcher SHALL read `oh_my_codex` from the persisted state file and map it to Codex CLI runtime overrides.

At minimum:

- `oh_my_codex=on` SHALL keep omx startup behavior enabled
- `oh_my_codex=off` SHALL disable omx-specific startup behavior for the wrapped launch

#### Scenario: Wrapped launch runs in native mode when omx is off

- **WHEN** the wrapped `codex` launch sees `oh_my_codex=off`
- **THEN** it SHALL disable omx-specific MCP startup surfaces for that launch
- **AND** it SHALL use the native-mode developer-instruction preset for that launch

### Requirement: The launcher SHALL map `subagent_routing` state to multi-agent availability

The launcher SHALL read `subagent_routing` from the persisted state file and map it to Codex CLI routing behavior.

At minimum:

- `auto` SHALL keep multi-agent available and use automatic-routing instructions
- `manual` SHALL keep multi-agent available and use manual-routing instructions
- `off` SHALL disable multi-agent for the wrapped launch

#### Scenario: Wrapped launch disables multi-agent in no-routing mode

- **WHEN** the wrapped `codex` launch sees `subagent_routing=off`
- **THEN** it SHALL pass the equivalent of `--disable multi_agent`
- **AND** it SHALL use the no-routing developer-instruction preset

### Requirement: Startup-binding installation SHALL be covered by backup snapshots and rollback

The installer SHALL include the PowerShell profile path and startup-binding launcher assets in the same timestamped backup-and-rollback transaction used for other team-mode assets.

#### Scenario: A partial startup-binding install restores the previous profile content

- **WHEN** startup-binding installation fails after profile or launcher writes begin
- **THEN** the installer SHALL restore the previous PowerShell profile content
- **AND** it SHALL restore or remove startup-binding assets to their pre-install state
- **AND** it SHALL preserve backup metadata for diagnostics

### Requirement: Startup-binding surfaces SHALL avoid duplicating project canary prompts

Startup-binding, launcher, and repository instruction surfaces SHALL NOT duplicate a project-level context-retention canary prompt outside the project startup summary pair.

They MAY point to the project startup summary as the source of truth and MAY describe the cold-start recovery path.

#### Scenario: Launcher or instruction text refers to context-loss recovery

- **WHEN** startup-binding or repository instruction text documents context-loss recovery
- **THEN** it SHALL refer readers to the project startup summary for the canary prompt
- **AND** it SHALL NOT embed the literal canary prompt text in launcher payloads, generated wrappers, or `AGENTS.md`

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

### Requirement: Startup launchers SHALL pass generated model instructions through a file reference

User-level startup launchers SHALL keep generated model-instruction bodies out of command-line startup overrides.

When a generated instruction body is required for wrapped Codex startup, the launcher support layer SHALL write that body to a managed UTF-8 state file and SHALL pass only a short `model_instructions_file` reference on the command line.

The startup argument builder SHALL NOT pass inline `developer_instructions` startup overrides for generated user-level orchestration instructions.

The repository SHALL keep an executable checker that validates the source launcher generator for this file-backed transport pattern and that checker SHALL be included in the aggregate OpenSpec guard.

#### Scenario: Wrapped startup carries generated instructions safely

- **WHEN** the generated launcher needs user-level team-mode model instructions
- **THEN** it SHALL write those instructions to a managed UTF-8 model-instructions file
- **AND** it SHALL pass exactly one short `model_instructions_file` startup override
- **AND** it SHALL forward that startup override before user-supplied arguments

#### Scenario: Inline generated developer instructions are reintroduced

- **WHEN** the startup argument builder or generated launcher attempts to pass `developer_instructions=` as a command-line override for generated startup instructions
- **THEN** the launcher payload context-boundary checker SHALL fail
- **AND** the aggregate OpenSpec guard SHALL report the launcher payload boundary violation

