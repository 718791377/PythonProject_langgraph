# codex-user-level-team-mode-windows-native-team-backend Specification

## Purpose
Define the native Windows durable-team backend contract for `omx team` so user-level team mode can run without WSL2 while preserving the repo-local team state and lifecycle surface.

## Requirements

### Requirement: `omx team` SHALL support a native Windows durable-team backend

The durable-team runtime SHALL support a native Windows backend that does not require WSL2 or Unix `tmux`.

#### Scenario: Launch a durable execution team on native Windows

- **WHEN** the operator runs `omx team 2:team-executor "ship feature X"` on native Windows
- **THEN** the runtime SHALL launch the team through the Windows backend
- **AND** it SHALL not fail only because Unix `tmux` is unavailable

#### Scenario: Native Windows prompt workers survive parent shell exit

- **WHEN** a native Windows durable team launches prompt-mode Codex workers through the Windows backend
- **THEN** those workers SHALL continue running after the launching shell exits
- **AND** the backend SHALL not rely on an ordinary detached child that dies with the parent shell

### Requirement: Native Windows backend SHALL preserve the repo-local team state contract

The native Windows backend SHALL keep the same repo-local state layout under `.omx/state/team/...`.

At minimum it SHALL preserve:

- team manifest and config
- task files
- mailbox state
- worker identity
- worker heartbeat

#### Scenario: Read team state after Windows launch

- **WHEN** a team is launched on native Windows
- **THEN** the repo-local `.omx/state/team/<team>/...` contract SHALL remain readable to existing lifecycle and API commands

#### Scenario: Controller-managed startup does not leak repeated ACK / claim loops into Windows worker execution

- **WHEN** the Windows backend controller has already sent startup ACK and initial task claim for a prompt worker
- **THEN** the worker guidance SHALL not require blind retries of those same startup actions
- **AND** Windows worker prompts SHALL prefer state-aware continuation over duplicate startup control flow

### Requirement: Native Windows backend SHALL support lifecycle parity

The native Windows backend SHALL support:

- `status` - lifecycle action for reading team or backend state.
- `await` - lifecycle action for waiting until team work reaches a terminal state.
- `resume` - lifecycle action for continuing a paused or resumable team run.
- `shutdown` - lifecycle action for stopping a team safely.

#### Scenario: Shut down a native Windows team cleanly

- **WHEN** the operator runs `omx team shutdown <team-name>` on native Windows
- **THEN** the runtime SHALL stop the tracked workers cleanly
- **AND** it SHALL leave team state in a terminal lifecycle state

#### Scenario: Shut down a breakaway-launched Windows team cleanly

- **WHEN** the operator runs `omx team shutdown <team-name>` against a native Windows team whose workers were launched through a breakaway launcher path
- **THEN** the runtime SHALL stop the real controller-owned worker processes cleanly
- **AND** it SHALL not depend on a short-lived launcher pid for shutdown correctness

### Requirement: The native Windows team backend SHALL define safe native residue cleanup boundaries
The native Windows durable-team backend SHALL define which native team-state residue is safe to remove and which residue must remain inspectable until explicit reconciliation.

At minimum:

- empty unmanaged native team directories SHALL be safe cleanup candidates
- stale tracked-record pointers to missing native team directories SHALL be reconcilable
- non-empty unmanaged native team residue SHALL remain protected or manual-inspection-required until later rules explicitly widen the safe cleanup set

#### Scenario: Operator reconciles empty unmanaged native team directories
- **WHEN** unmanaged native team directories exist and contain no files
- **THEN** the backend contract SHALL allow those directories to be classified as safe cleanup candidates
- **AND** it SHALL not require those empty directories to remain treated as protected terminal-state evidence

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
