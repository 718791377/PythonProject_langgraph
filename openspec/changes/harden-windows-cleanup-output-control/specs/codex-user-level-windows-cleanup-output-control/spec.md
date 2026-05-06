## ADDED Requirements

### Requirement: Cleanup-output control SHALL support opt-in taskkill executable interception

The user-level team-mode installer SHALL provide an explicit opt-in switch for installing a compiled `taskkill.exe` shim when cleanup callers bypass the default `taskkill.cmd` shim.

The installer SHALL NOT install or enable the compiled `taskkill.exe` shim by default.

When the opt-in switch is used, the installer SHALL compile the shim from managed repository source, write it under the generated `win-shims` directory, and report whether compilation was attempted and completed.

#### Scenario: Default installation keeps executable interception disabled

- **WHEN** the installer runs without the explicit EXE shim switch
- **THEN** the generated startup binding SHALL report `taskkill_exe_shim_enabled=false`
- **AND** wrapped launch SHALL NOT prioritize `.EXE` before the existing PATHEXT order

#### Scenario: Explicit executable interception is installed

- **WHEN** the installer runs with the explicit EXE shim switch
- **THEN** the installer SHALL compile `taskkill-shim-source.cs` into `win-shims\taskkill.exe`
- **AND** the generated startup binding SHALL report `taskkill_exe_shim_enabled=true`
- **AND** wrapped launch SHALL prioritize `.EXE` inside the wrapped child process tree

#### Scenario: Explicit executable interception cannot be compiled

- **WHEN** the installer runs with the explicit EXE shim switch
- **AND** no usable C# compiler is available
- **THEN** installation SHALL fail with a diagnostic reason
- **AND** the managed-install rollback path SHALL restore the previous managed state

### Requirement: Cleanup-output checker SHALL guard optional executable hardening

The repository cleanup-output checker SHALL verify that the installer source contains the optional executable shim switch, compile function, scoped launcher flag, and JSON report fields.

#### Scenario: Optional executable hardening source is removed

- **WHEN** the cleanup-output checker runs against installer source that no longer exposes the optional executable shim switch
- **THEN** the checker SHALL fail
- **AND** the checker output SHALL identify the missing executable-hardening marker
