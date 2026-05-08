## ADDED Requirements

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

The user-level installer SHALL request explicit `taskkill.exe` cleanup-output shimming by default for wrapped `codex-ohmy` launches.

The generated launcher SHALL only prioritize `.EXE` in `PATHEXT` when the generated `win-shims\taskkill.exe` file exists at runtime. If that executable shim is unavailable, the launcher SHALL fall back to the existing `.CMD` shim without breaking the wrapped launch.

The installer SHALL provide an explicit opt-out switch for environments that cannot or should not compile the executable shim.

#### Scenario: Default install can intercept explicit taskkill.exe cleanup

- **WHEN** the installer can compile the generated `taskkill.exe` shim
- **THEN** the wrapped launcher SHALL prepend the `win-shims` directory to PATH
- **AND** it SHALL prioritize `.EXE` in `PATHEXT` for that wrapped child process tree
- **AND** successful explicit `taskkill.exe` cleanup output SHALL be suppressed by the shim

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