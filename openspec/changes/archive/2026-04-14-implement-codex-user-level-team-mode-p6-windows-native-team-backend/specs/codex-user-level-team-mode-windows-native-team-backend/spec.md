## ADDED Requirements

### Requirement: `omx team` SHALL support a native Windows durable-team backend

The durable-team runtime SHALL support a native Windows backend that does not require WSL2 or Unix `tmux`.

#### Scenario: Launch a durable execution team on native Windows

- **WHEN** the operator runs `omx team 2:team-executor "ship feature X"` on native Windows
- **THEN** the runtime SHALL launch the team through the Windows backend
- **AND** it SHALL not fail only because Unix `tmux` is unavailable

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

### Requirement: Native Windows backend SHALL support lifecycle parity

The native Windows backend SHALL support:

- `status`
- `await`
- `resume`
- `shutdown`

#### Scenario: Shut down a native Windows team cleanly

- **WHEN** the operator runs `omx team shutdown <team-name>` on native Windows
- **THEN** the runtime SHALL stop the tracked workers cleanly
- **AND** it SHALL leave team state in a terminal lifecycle state
