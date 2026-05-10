## MODIFIED Requirements

### Requirement: Cleanup-output control SHALL be scoped to wrapped launches

The startup launcher SHALL make cleanup-output control visible to the native Codex child process tree only for the wrapped launch.

The launcher SHALL restore the previous PATH, PATHEXT, and cleanup-shim environment bridge after the native Codex command exits.

The repository implementation SHALL NOT mutate `C:\Users\lenovo\.codex\config.toml` to enable this control.

#### Scenario: Wrapped launch starts

- **WHEN** `codex-ohmy` invokes the native Codex command
- **THEN** the generated `win-shims` directory SHALL be prepended to PATH for that child process tree
- **AND** the launcher SHALL expose that directory through a scoped process environment bridge for descendant login shells
- **AND** the original PATH, PATHEXT, and environment bridge state SHALL be restored after the native command returns

#### Scenario: Spawned login shell resets PATH

- **WHEN** a PowerShell login shell spawned under a wrapped launch resets PATH from Machine/User environment
- **AND** the wrapped launcher has exposed the cleanup shim directory through the scoped environment bridge
- **THEN** the managed profile block SHALL re-prepend the generated `win-shims` directory after the reset
- **AND** `taskkill.exe` SHALL resolve to the generated executable shim when it exists
- **AND** the profile bridge SHALL NOT be required for native bypass sessions

#### Scenario: Native bypass starts

- **WHEN** the operator runs `codex-raw`, `codex-native`, or the native `codex` executable directly
- **THEN** the cleanup-output control layer SHALL NOT be required for that bypass path
- **AND** the bypass SHALL remain free of wrapper-specific PATH mutation