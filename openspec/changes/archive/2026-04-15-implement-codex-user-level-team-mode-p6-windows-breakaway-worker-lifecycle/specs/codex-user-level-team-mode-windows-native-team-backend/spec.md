## MODIFIED Requirements

### Requirement: `omx team` SHALL support a native Windows durable-team backend

The durable-team runtime SHALL support a native Windows backend that does not require WSL2 or Unix `tmux`.

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

#### Scenario: Controller-managed startup does not leak repeated ACK / claim loops into Windows worker execution

- **WHEN** the Windows backend controller has already sent startup ACK and initial task claim for a prompt worker
- **THEN** the worker guidance SHALL not require blind retries of those same startup actions
- **AND** Windows worker prompts SHALL prefer state-aware continuation over duplicate startup control flow

### Requirement: Native Windows backend SHALL support lifecycle parity

The native Windows backend SHALL support:

- `status`
- `await`
- `resume`
- `shutdown`

#### Scenario: Shut down a breakaway-launched Windows team cleanly

- **WHEN** the operator runs `omx team shutdown <team-name>` against a native Windows team whose workers were launched through a breakaway launcher path
- **THEN** the runtime SHALL stop the real controller-owned worker processes cleanly
- **AND** it SHALL not depend on a short-lived launcher pid for shutdown correctness
