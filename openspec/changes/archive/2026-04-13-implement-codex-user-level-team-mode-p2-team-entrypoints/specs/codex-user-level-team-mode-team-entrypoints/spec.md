## ADDED Requirements

### Requirement: The installer SHALL generate user-level OMX team entrypoint assets

The installer SHALL generate additive user-level team entrypoint assets into the target Codex home.

The generated asset set SHALL include at least:

- `bin/omx-team-dev.ps1`
- `bin/omx-team-debug.ps1`
- `bin/omx-team-verify.ps1`
- `bin/omx-team-ops.ps1`
- `bin/omx-team-hybrid.ps1`
- `docs/team-mode-playbook.md`

#### Scenario: Generate the P2 team entrypoint layer into a temporary Codex home

- **WHEN** the installer is run against an explicit target Codex home
- **THEN** it SHALL generate the team entrypoint wrappers and playbook there
- **AND** it SHALL keep the new assets additive-only

### Requirement: Generated wrappers SHALL call a resolved native OMX command path

The installer SHALL resolve the native `omx` command path, or accept an explicit override, and generated wrappers SHALL call that resolved path directly.

The installer SHALL NOT replace or overwrite the native `omx` executable.

#### Scenario: A test install uses a fake OMX target

- **WHEN** the installer is run with an explicit fake `omx` command path
- **THEN** the generated wrappers SHALL call that fake command path
- **AND** wrapper behavior SHALL remain testable without modifying the real user install

### Requirement: Development and debug wrappers SHALL encode approved durable-team defaults

`omx-team-dev.ps1` SHALL encode a durable development-team preset.

At minimum:

- default worker count: `2`
- default worker role: `team-executor`
- optional override to `executor`

`omx-team-debug.ps1` SHALL encode a durable debug-team preset.

At minimum:

- default worker count: `2`
- default worker role: `debugger`

#### Scenario: Development wrapper launches a conservative worker swarm

- **WHEN** the operator runs `omx-team-dev.ps1 -Task "ship feature X"`
- **THEN** it SHALL invoke the equivalent of `omx team 2:team-executor "ship feature X"`

#### Scenario: Debug wrapper launches a debugger swarm

- **WHEN** the operator runs `omx-team-debug.ps1 -Task "stabilize regression X"`
- **THEN** it SHALL invoke the equivalent of `omx team 2:debugger "stabilize regression X"`

### Requirement: The ops wrapper SHALL expose the supported team lifecycle and safe read-only team inspection surface

`omx-team-ops.ps1` SHALL wrap the supported lifecycle commands:

- `status`
- `await`
- `resume`
- `shutdown`

It SHALL also support safe read-only team API operations such as:

- `list-tasks`
- `mailbox-list`
- `get-summary`
- `read-manifest`

#### Scenario: Ops wrapper shows team status

- **WHEN** the operator runs `omx-team-ops.ps1 -Action status -TeamName my-team`
- **THEN** it SHALL invoke the equivalent of `omx team status my-team`

#### Scenario: Ops wrapper uses read-only team API inspection

- **WHEN** the operator runs `omx-team-ops.ps1 -Action list-tasks -TeamName my-team`
- **THEN** it SHALL invoke the corresponding `omx team api` read-only operation
- **AND** it SHALL provide the team name as API input

### Requirement: The hybrid wrapper SHALL map heterogeneous staffing to leader-side experts plus one homogeneous durable worker team

`omx-team-hybrid.ps1` SHALL accept staffing counts such as architect, planner, executor, and verifier.

It SHALL interpret them by:

- keeping expert roles as leader-side native subagents
- mapping executor count to one homogeneous durable worker swarm
- emitting a structured plan that states the expert counts, the durable worker launch shape, and the expected checkpoints for expert use

It MAY optionally launch the durable worker swarm.

It SHALL NOT claim that every requested role becomes a persistent pane by default.

#### Scenario: Hybrid wrapper interprets expert counts without creating mixed persistent panes

- **WHEN** the operator runs `omx-team-hybrid.ps1 -Architect 1 -Planner 1 -Executor 2 -Verifier 1 -Task "implement rollout X"`
- **THEN** it SHALL report that architect, planner, and verifier remain leader-side native roles
- **AND** it SHALL derive one durable worker swarm from the executor count

### Requirement: The verify wrapper SHALL reinforce leader-side native verification roles

`omx-team-verify.ps1` SHALL output a verification plan for leader-side native roles instead of defaulting to a persistent verifier swarm.

At minimum it SHALL be able to plan use of:

- `verifier`
- `test-engineer`
- `security-reviewer`
- `writer`

#### Scenario: Verification wrapper plans final sign-off without launching a verifier pane

- **WHEN** the operator runs `omx-team-verify.ps1` for a behavior-changing multi-file change
- **THEN** it SHALL recommend leader-side native verification roles
- **AND** it SHALL not require a persistent verifier pane as the default path

### Requirement: The installer SHALL generate a reusable playbook for cross-repository operation

The installer SHALL generate a user-level playbook that documents:

- team-mode state meanings
- wrapper usage
- team lifecycle commands
- hybrid staffing interpretation
- the separation between open-ended research roles and implementation roles

#### Scenario: A user reads the generated playbook from another repository

- **WHEN** the user opens the generated playbook outside this repository
- **THEN** it SHALL still describe a reusable operator workflow
- **AND** it SHALL not depend on OpenClaw-specific runtime commands
