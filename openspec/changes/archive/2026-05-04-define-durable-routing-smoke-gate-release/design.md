## Context

The active team-mode and durable-state plans have completed the bounded MR 1 through MR 6 queue. The next useful increment is not another runtime implementation of automatic routing; it is a small release gate that defines when a future smoke or adoption-gate change may exercise `omx-team-auto.ps1`, the generated user-level helper that plans or applies automatic durable routing.

The final production durable-team plan remains draft-only. It needs a release-train overlay so later work can be discussed as MVP or release slices without implying that the full target state is already implementation-ready.

## Goals / Non-Goals

**Goals:**

- Define Release 0.6 as a read-first durable routing smoke/adoption gate.
- Make `target_repository`, `phase`, `task`, and `operator_consent_boundary` mandatory for future live routing exercises.
- Document that the default boundary is dry-run/read-only: no `-Apply`, no `.omx/state/` writes, and no durable-team launch.
- Keep the production durable-team plan in draft status while adding a clear MVP/release breakdown.

**Non-Goals:**

- Do not execute `omx-team-auto.ps1 -Apply`; `-Apply` is the mutating execution switch for the helper.
- Do not run `omx team`; `omx team` is the durable worker-team runtime command.
- Do not change `.omx/state/`; `.omx/state/` is the repo-local durable-state directory.
- Do not modify user-level Codex configuration or MCP Router state.

## Decisions

1. Use a Release 0.6 label instead of adding more MR numbers.
   - Rationale: MR 1 through MR 6 are already completed, and a release label describes user-visible readiness more clearly than another implementation-number queue.
   - Alternative considered: reopen MR 6. Rejected because MR 6 readiness review already closed and duplicate runtime work would create drift.

2. Treat smoke/adoption gates as separate reviewed OpenSpec changes.
   - Rationale: runtime exercise depends on a target repository, phase, concrete task, and explicit operator consent boundary.
   - Alternative considered: run smoke immediately from the plan update. Rejected because the current change is documentation/spec sequencing only.

3. Keep the production durable-team draft as north-star material.
   - Rationale: the draft contains useful long-term architecture, but its full scope is too large for a single safe implementation wave.
   - Alternative considered: promote the whole draft to active. Rejected because it would blur already-landed MVP-shaped behavior with not-yet-built production targets.

## Risks / Trade-offs

- [Risk] Release labels can drift from implementation reality. -> Mitigation: keep the labels tied to OpenSpec requirements and checker-backed validation.
- [Risk] A future session might treat smoke as permission to mutate state. -> Mitigation: make the default boundary read-only and require explicit operator consent before `-Apply` or state writes.
- [Risk] Draft production goals may still look like active work. -> Mitigation: explicitly state that Release 1.0 and Release 2.0 are future stages, not current implementation claims.
