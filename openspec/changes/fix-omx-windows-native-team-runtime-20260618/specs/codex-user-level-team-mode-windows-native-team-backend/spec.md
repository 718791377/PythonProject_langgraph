## ADDED Requirements

### Requirement: Native OMX SHALL distinguish runtime backend from backend family

The `native_omx` durable backend family SHALL expose the concrete runtime backend used for operational launchability checks.

At minimum, `runtime_backend` SHALL support:

- `windows_prompt_process_controller` for the native Windows default.
- `unix_tmux` for the Unix/tmux implementation backend.
- `unknown` when no runtime backend is proven.

#### Scenario: Windows does not treat tmux as native_omx itself

- **GIVEN** the operator is on native Windows without `tmux` and without a `tmux` session
- **WHEN** a worker-centric durable task selects the `native_omx` backend family
- **THEN** the runtime SHALL evaluate `windows_prompt_process_controller` as the Windows runtime backend
- **AND** it SHALL NOT define `native_omx` as only the `unix_tmux` backend.

### Requirement: Native Windows operational preflight SHALL be explicit

Native Windows `omx team` execution SHALL report operational preflight fields before launch or reuse.

At minimum the preflight record SHALL include `runtime_backend`, `preflight_passed`, `operational_ready`, and `blockers`.

#### Scenario: No Windows runtime backend is launchable

- **GIVEN** the selected backend family is `native_omx`
- **AND** neither a Windows prompt/process controller nor an explicitly requested Unix/tmux backend can launch
- **WHEN** the runtime evaluates operational ability
- **THEN** it SHALL report `operational_ready=false`
- **AND** it SHALL include a named blocker such as `blocked:windows_backend_not_implemented`, `blocked:tmux_only_backend`, or `blocked:not_in_tmux_session`.
