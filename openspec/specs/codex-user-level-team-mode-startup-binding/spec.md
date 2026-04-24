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

