## Context

The archived `P6` batch proved that native Windows durable teams can launch and that runtime-root isolation can keep worker sidefiles out of worker worktrees.

What follow-up live validation then showed is more specific:

- the backend itself is no longer blocked by `tmux`
- the remaining failure is Windows worker survival and lifecycle tracking after parent shell exit
- ordinary detached child launch is not a strong enough persistence boundary on native Windows
- once workers stay alive, shutdown must still cleanly stop the real long-lived controller pid

## Goals / Non-Goals

**Goals**

- give Windows prompt workers a stronger breakaway launcher path
- capture and store the real long-lived controller pid
- keep live worker liveness and shutdown behavior consistent with the new launch path
- document controller-owned ACK / initial claim behavior for Windows prompt workers

**Non-Goals**

- redesigning leader-side routing
- changing Unix backend behavior
- adding new durable-team phases

## Decisions

### Decision 1: Treat this as a lifecycle correction batch, not a new routing batch

Why:

- routing thresholds and tracked-team planning already exist
- the live failure happens after the planned launch decision

### Decision 2: Use a Windows launcher path that breaks away more strongly than an ordinary detached child

Why:

- ordinary detached child launch still tracks parent shell lifetime too loosely on native Windows
- a launcher hop can return the real controller pid back to the runtime

### Decision 3: Track the real controller pid even when the immediate launcher process exits

Why:

- liveness checks and shutdown should follow the process that actually owns the worker loop
- a short-lived launcher pid is not a durable lifecycle identity

### Decision 4: Keep worker startup guidance aligned with controller-managed startup

Why:

- once the controller sends startup ACK and first claim, worker prompts should stop retrying them blindly
- Windows constrained PowerShell makes repeated inline `--input` JSON especially noisy

## Risks / Trade-offs

- [Risk] A stronger launcher path may complicate shutdown.
  Mitigation: keep pid tracking explicit and validate clean shutdown on real live teams.

- [Risk] Guidance changes may diverge from Unix worker behavior.
  Mitigation: scope the new wording to native Windows Codex prompt workers only.

## Validation Plan

1. Launch a fresh Windows durable team and verify workers remain alive after the launching shell exits.
2. Verify task claims remain `in_progress` and workers do not immediately become `worker_stopped`.
3. Run a clean `omx team shutdown ... --force --confirm-issues` against the live team.
4. Verify tracked-team isolation still works across separate repositories.
