# codex-user-level-windows-cleanup-output-control Delta

## Modified Requirements

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

The user-level installer SHALL request explicit `taskkill.exe` cleanup-output shimming by default for wrapped `codex-ohmy` launches.

The installer SHALL discover a C# compiler from PATH and from standard Windows .NET Framework compiler directories, including both Framework64 and Framework locations, before declaring the executable shim unavailable.

The installer SHALL capture executable-shim compiler stdout and stderr in files under the generated shim directory rather than depending only on the ambient temp directory.

The generated executable shim SHALL suppress all stdout and stderr when the real Windows `taskkill.exe` exits with code 0, including localized Chinese success lines such as `成功: 已终止 PID ...`.

The generated executable shim SHALL preserve non-zero cleanup failures by forwarding captured output to stderr and returning the original exit code.

The generated launcher SHALL only prioritize `.EXE` in `PATHEXT` when the generated `win-shims\taskkill.exe` file exists at runtime. If that executable shim is unavailable, the launcher SHALL fall back to the existing `.CMD` shim without breaking the wrapped launch.

The installer SHALL provide an explicit opt-out switch for environments that cannot or should not compile the executable shim.

#### Scenario: Default install can intercept explicit taskkill.exe cleanup with Framework compiler fallback

- **WHEN** `csc.exe` is not on PATH but exists under a standard Windows .NET Framework compiler directory
- **THEN** the installer SHALL compile `win-shims\taskkill.exe`
- **AND** the wrapped launcher SHALL prepend the `win-shims` directory to PATH
- **AND** it SHALL prioritize `.EXE` in `PATHEXT` for that wrapped child process tree
- **AND** successful explicit `taskkill.exe` cleanup output SHALL be suppressed by the shim

#### Scenario: Localized successful cleanup output

- **WHEN** the real Windows `taskkill.exe` exits with code 0 and emits Chinese success lines beginning with `成功: 已终止 PID `
- **THEN** the executable shim SHALL return exit code 0
- **AND** it SHALL NOT forward those success lines to stdout or stderr

#### Scenario: Cleanup fails

- **WHEN** the real Windows `taskkill.exe` returns a non-zero exit code
- **THEN** the executable shim SHALL return the same non-zero exit code
- **AND** it SHALL forward captured diagnostic output to stderr