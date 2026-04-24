## Context

The plan already defines the intended operator surface after P1:

- `omx-team-dev.ps1`
- `omx-team-debug.ps1`
- `omx-team-verify.ps1`
- `omx-team-ops.ps1`
- `omx-team-hybrid.ps1`
- `docs/team-mode-playbook.md`

Local reality now also confirms:

- `omx team` is available locally
- the supported lifecycle commands are `status`, `await`, `resume`, `shutdown`, and `api`
- worktrees are created automatically by current `omx team`
- user-scope native agents already exist for `analyst`, `architect`, `planner`, `researcher`, `verifier`, `test-engineer`, `security-reviewer`, `writer`, `executor`, `team-executor`, and `debugger`

This means the next useful implementation slice is not another state switch. It is a reusable team-entrypoint layer that turns the approved operating model into explicit user-level scripts.

## Goals / Non-Goals

**Goals:**

- generate reusable user-level wrappers for common `omx team` workflows
- keep the generated wrappers additive-only and explicitly bound to a resolved `omx` command path
- expose safe team lifecycle operations through one `ops` wrapper
- provide a hybrid staffing wrapper that maps expert counts to a leader-side plan plus one homogeneous durable worker swarm
- provide a verification wrapper that reinforces leader-side native verification roles instead of default persistent verifier panes
- generate a concise playbook under the target Codex home
- keep backup snapshot and rollback behavior for all new generated assets
- make the new wrappers testable with a fake `omx` target in a temporary Codex home

**Non-Goals:**

- implementing a mixed persistent pane compose manifest
- mutating the native `omx` executable or adding a startup binding around `omx`
- making `verifier` a default persistent team worker
- auto-spawning native expert subagents from PowerShell wrappers
- changing OpenClaw runtime or service configuration

## Decisions

### Decision 1: Reuse the existing generated support script instead of adding a second state runtime

P0/P1 already generate a shared support script under `bin/_codex-user-level-team-mode.ps1`.

P2 extends that support layer with helper functions for:

- resolving the latest team name from `.omx/state/team`
- building team launch defaults
- building `omx team api` read-only requests
- emitting verification and hybrid plans

Why:

- it preserves one user-level runtime source of truth
- it keeps the wrapper scripts thin
- it lets tests validate wrapper behavior without duplicating logic

### Decision 2: Resolve the native `omx` command path explicitly at install time

The installer will resolve the real `omx` command path, or accept an explicit override such as `-OmxCommandPath`.

Generated wrappers will call that resolved path directly.

Why:

- it avoids accidental recursion through future wrapper aliases
- it makes the wrapper set testable with a fake `omx` target
- it preserves the native `omx` command as the actual execution backend

### Decision 3: `omx-team-dev.ps1` and `omx-team-debug.ps1` will be thin launch presets

`omx-team-dev.ps1`:

- default worker count: `2`
- default worker role: `team-executor`
- optional override to `executor`

`omx-team-debug.ps1`:

- default worker count: `2`
- fixed worker role: `debugger`

Both wrappers will call the canonical CLI form:

- `omx team N:role "<task>"`

Why:

- it encodes the approved defaults without hiding the real CLI surface
- it avoids inventing repository-local orchestration

### Decision 4: `omx-team-ops.ps1` will wrap lifecycle commands plus safe read-only API operations

This wrapper will support:

- `status`
- `await`
- `resume`
- `shutdown`
- `list-tasks`
- `mailbox-list`
- `get-summary`
- `read-manifest`

If the operator omits the team name, the wrapper may resolve the most recently updated team under the current repository's `.omx/state/team/`.

Why:

- forgetting the team name is a common operator friction point
- these are the exact commands called out in the plan and the current CLI help
- restricting API wrapping to read-only operations avoids accidental mutation creep

### Decision 5: `omx-team-hybrid.ps1` will be a planning-and-launch bridge, not a mixed-pane orchestrator

The hybrid wrapper will accept counts such as:

- `-Architect 1`
- `-Planner 1`
- `-Executor 2`
- `-Verifier 1`

It will produce a structured plan that states:

- which expert roles are leader-side native subagents
- what the durable worker swarm is
- the canonical `omx team` launch command for that swarm
- the checkpoints where expert roles should be called

It may optionally launch the durable swarm, but it will not pretend to spawn all expert roles as persistent panes.

Why:

- this matches the approved "heterogeneous orchestration, homogeneous durable workers" rule
- it keeps the wrapper useful today without inventing a heavier compose layer

### Decision 6: `omx-team-verify.ps1` will emit a verification plan instead of launching a persistent verifier team by default

The verification wrapper will output a leader-side native verification plan that can include:

- `verifier`
- `test-engineer`
- `security-reviewer`
- `writer`

Selection will be driven by simple flags such as behavior change, security-sensitive scope, and docs/operator-impact.

Why:

- the plan explicitly says final judgment should move back to leader-side native subagents
- generating a verification plan is consistent with that requirement
- it avoids turning `verifier` into the wrong default team shape

### Decision 7: Generate a user-level playbook alongside the wrappers

The playbook will document:

- the meaning of `oh_my_codex` and `subagent_routing`
- what each wrapper does
- the supported `omx team` lifecycle
- hybrid staffing interpretation
- the rule that research and implementation should be different roles for open-ended tasks

Why:

- the wrappers alone are not enough for reusable cross-repo operation
- the user explicitly wants a workflow reusable by other Codex CLI projects

## Risks / Trade-offs

- [Risk] The wrappers could drift from current `omx team` CLI behavior.
  Mitigation: base them on live local `omx team --help` and `omx team api --help`, and keep their logic thin.

- [Risk] Auto-discovering the latest team name could target the wrong team when several teams exist.
  Mitigation: prefer explicit `-TeamName`, and use most-recent discovery only as a convenience fallback.

- [Risk] Operators may read `omx-team-hybrid.ps1` as a full heterogeneous persistent team launcher.
  Mitigation: make the wrapper output explicit that expert roles stay leader-side native subagents.

- [Risk] `omx-team-verify.ps1` may be mistaken for a durable verification swarm.
  Mitigation: keep it as a verification-plan surface and document that final sign-off is leader-side.

## Migration Plan

1. Create proposal, design, spec, and tasks artifacts for P2.
2. Extend the installer with `-OmxCommandPath` resolution and generation of the new wrapper/playbook assets.
3. Extend the shared support script with helper functions for team name discovery, ops dispatch, hybrid planning, and verification planning.
4. Add wrapper validation to the PowerShell test using a fake `omx` command target.
5. Validate OpenSpec and repo guard health.
6. Reinstall into the real user Codex home after repository validation passes.
