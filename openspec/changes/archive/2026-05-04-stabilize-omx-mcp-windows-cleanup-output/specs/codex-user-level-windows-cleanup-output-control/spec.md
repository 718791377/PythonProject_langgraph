## ADDED Requirements

### Requirement: Wrapped Codex launches SHALL suppress benign Windows cleanup success output

The user-level team-mode startup launcher SHALL install and use a scoped Windows cleanup-output control layer for wrapped `codex-ohmy` launches.

The control layer SHALL suppress normal successful `taskkill` output, including English `SUCCESS: The process with PID ... has been terminated.` lines and Chinese `??: ??? PID ... ????` lines, from the main Codex session.

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
