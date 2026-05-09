# Codex User-Level Windows Cleanup Output Control

## Purpose

Define the scoped cleanup-output control that keeps normal Windows `taskkill` success messages out of wrapped `codex-ohmy` sessions while preserving direct `omx_*` MCP availability and failure diagnostics.
## Requirements
### Requirement: Wrapped Codex launches SHALL suppress benign Windows cleanup success output

The user-level team-mode startup launcher SHALL install and use a scoped Windows cleanup-output control layer for wrapped `codex-ohmy` launches.

The control layer SHALL suppress normal successful `taskkill` output, including English `SUCCESS: The process with PID ... has been terminated.` lines and Chinese successful termination lines, from the main Codex session.

The control layer SHALL preserve non-zero cleanup failures by forwarding captured failure output to stderr and returning the original exit code.

#### Scenario: `/resume` cleans up a temporary wrapped session

- **WHEN** the operator starts `codex-ohmy`, enters a temporary session, and then uses `/resume`
- **THEN** successful cleanup of the temporary session's Windows child process tree SHALL NOT print `taskkill` success lines into the resumed session
- **AND** the cleanup control SHALL NOT require disabling `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace`

#### Scenario: Cleanup fails

- **WHEN** the cleanup shim invokes the real Windows `taskkill.exe` and receives a non-zero exit code
- **THEN** it SHALL return the same non-zero exit code
- **AND** it SHALL forward captured diagnostic output to stderr

### Requirement: Cleanup-output control SHALL be scoped to wrapped launches

The startup launcher SHALL make cleanup-output control visible to the native Codex child process tree only for the wrapped launch.

The launcher SHALL restore the previous PATH after the native Codex command exits.

The repository implementation SHALL NOT mutate `C:\Users\lenovo\.codex\config.toml` to enable this control.

#### Scenario: Wrapped launch starts

- **WHEN** `codex-ohmy` invokes the native Codex command
- **THEN** the generated `win-shims` directory SHALL be prepended to PATH for that child process tree
- **AND** the original PATH SHALL be restored after the native command returns

#### Scenario: Native bypass starts

- **WHEN** the operator runs `codex-raw`, `codex-native`, or the native `codex` executable directly
- **THEN** the cleanup-output control layer SHALL NOT be required for that bypass path
- **AND** the bypass SHALL remain free of wrapper-specific PATH mutation

### Requirement: Cleanup-output control SHALL preserve direct `omx_*` MCP availability

When `oh_my_codex=on`, the wrapped launcher SHALL continue enabling direct Codex MCP entries for `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace`.

#### Scenario: Full wrapped mode starts

- **WHEN** the wrapped launcher computes startup arguments with `oh_my_codex=on`
- **THEN** it SHALL pass enabled overrides for `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace`
- **AND** it SHALL also enable the cleanup-output control layer

### Requirement: Cleanup-output control SHALL have script-backed validation

The repository SHALL include an executable checker that verifies the cleanup-output control source contract.

The checker SHALL fail when the installer no longer generates the scoped shim or when the wrapped launcher no longer applies scoped PATH control.

#### Scenario: Repository checker runs

- **WHEN** the operator runs the cleanup-output control checker
- **THEN** it SHALL verify that the installer generates `win-shims` cleanup artifacts
- **AND** it SHALL verify that wrapped launch restores PATH after invoking native Codex
- **AND** it SHALL verify that `omx_*` MCP startup overrides remain enabled in full wrapped mode

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

The user-level installer SHALL request explicit `taskkill.exe` cleanup-output shimming by default for wrapped `codex-ohmy` launches.

The installer SHALL discover a C# compiler from PATH and from standard Windows .NET Framework compiler directories, including both Framework64 and Framework locations, before declaring the executable shim unavailable.

The installer SHALL capture executable-shim compiler stdout and stderr in files under the generated shim directory rather than depending only on the ambient temp directory.

The generated executable shim SHALL suppress all stdout and stderr when the real Windows `taskkill.exe` exits with code 0, including localized Chinese success lines such as `成功: 已终止 PID ...`.

The generated launcher SHALL only prioritize `.EXE` in `PATHEXT` when the generated `win-shims\taskkill.exe` file exists at runtime. If that executable shim is unavailable, the launcher SHALL fall back to the existing `.CMD` shim without breaking the wrapped launch.

The installer SHALL provide an explicit opt-out switch for environments that cannot or should not compile the executable shim.

#### Scenario: Default install can intercept explicit taskkill.exe cleanup

- **WHEN** the installer can compile the generated `taskkill.exe` shim
- **THEN** the wrapped launcher SHALL prepend the `win-shims` directory to PATH
- **AND** it SHALL prioritize `.EXE` in `PATHEXT` for that wrapped child process tree
- **AND** successful explicit `taskkill.exe` cleanup output SHALL be suppressed by the shim

#### Scenario: Default install can intercept explicit taskkill.exe cleanup with Framework compiler fallback

- **WHEN** `csc.exe` is not on PATH but exists under a standard Windows .NET Framework compiler directory
- **THEN** the installer SHALL compile `win-shims\taskkill.exe`
- **AND** successful explicit `taskkill.exe` cleanup output SHALL be suppressed by the shim

#### Scenario: Localized successful cleanup output

- **WHEN** the real Windows `taskkill.exe` exits with code 0 and emits Chinese success lines beginning with `成功: 已终止 PID `
- **THEN** the executable shim SHALL return exit code 0
- **AND** it SHALL NOT forward those success lines to stdout or stderr

#### Scenario: Executable shim is unavailable

- **WHEN** the executable shim was requested but is not present at runtime
- **THEN** the wrapped launcher SHALL not prioritize `.EXE`
- **AND** it SHALL keep the existing `.CMD` fallback cleanup-output control active
- **AND** the wrapped Codex launch SHALL continue rather than failing solely because the executable shim is unavailable

#### Scenario: Operator explicitly opts out

- **WHEN** the installer is run with the explicit opt-out switch
- **THEN** it SHALL not create `win-shims\taskkill.exe`
- **AND** the wrapped launcher SHALL not prioritize `.EXE`
- **AND** the existing `.CMD` and `.ps1` cleanup shims SHALL remain installed
