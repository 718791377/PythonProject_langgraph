## Context

P5 already completed the leader-side routing layer:

- wrapped startup exposes durable-team capability in enhanced auto mode
- `omx-team-auto.ps1` can plan `launch`, `reuse`, `switch`, and `shutdown`
- tracked repo-local team metadata already exists

What is still missing is the runtime backend that can execute those actions on native Windows.

Current observed failure mode:

- planning works
- `-Apply` reaches the runtime edge
- the runtime fails because `omx team` still requires `tmux`

## Goals / Non-Goals

**Goals:**

- add a backend abstraction for `omx team`
- preserve the existing Unix `tmux` backend
- add a native Windows durable-team backend that does not require WSL2
- keep the `.omx/state/team/...` contract stable across backends
- make `omx-team-auto.ps1 -Apply` truly executable on native Windows

**Non-Goals:**

- rewriting the P0-P5 routing or control model
- making WSL2 the standard path
- replacing native Codex startup
- treating GUI pane automation as the first stable backend

## Decisions

### Decision 1: Separate routing from execution backend

P5 already solved the routing question. P6 will solve the execution backend question.

Why:

- the routing layer is already inspectable and tested
- the current blocker is below that layer

### Decision 2: Add backend abstraction under `omx team`

`omx team` should resolve a backend at runtime:

- Unix path: existing `tmux`
- Windows path: new native backend

Why:

- platform-specific worker launching is a backend concern
- status and state semantics should remain stable above that layer

### Decision 3: Prefer a Windows process backend before any pane-oriented backend

The first Windows backend should launch durable workers as controlled background processes with repo-local state and dedicated worktrees.

Why:

- process orchestration is more stable than GUI pane automation
- lifecycle control is easier to make testable
- P5 needs durable execution, not cosmetic panes

### Decision 4: Keep state, mailbox, and worktree contracts unchanged

Across backends, keep:

- `.omx/state/team/<team>/...`
- mailbox and task files
- worker identity and heartbeat
- worker worktree ownership
- `status / await / resume / shutdown / api` semantics

Why:

- this protects the user-level wrapper surface
- this avoids breaking P2 through P5

## Risks / Trade-offs

- [Risk] Windows process cleanup may be harder than tmux cleanup.
  Mitigation: make worker identity, pid tracking, shutdown ack, and stale-worker detection explicit.

- [Risk] Backend divergence could split behavior by platform.
  Mitigation: keep one state contract and one lifecycle contract above the backend layer.

- [Risk] Existing wrapper documentation may drift from runtime reality.
  Mitigation: update playbook and policy together with backend capability changes.

## Migration Plan

1. Create the P6 proposal, design, tasks, and spec deltas.
2. Add `omx team` backend abstraction.
3. Implement the native Windows backend.
4. Validate wrapper compatibility and `omx-team-auto.ps1 -Apply`.
5. Roll forward only after native Windows runtime tests pass.
