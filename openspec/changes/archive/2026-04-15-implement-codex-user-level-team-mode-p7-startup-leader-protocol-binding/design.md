## Context

User-level team mode already has installed assets, global controls, role thresholds, and durable-team helpers.

The remaining usability gap is not "can the platform route?" but "does a new session consistently start in a routing-first posture?"

At the moment:

- startup injects dynamic `developer_instructions`
- leader semantics are present in installed assets
- but startup does not enforce a stable first-turn leader protocol
- therefore users still have to guess whether automatic expert routing or durable-team thresholding happened

## Goals / Non-Goals

**Goals**

- make every new wrapped Codex session start as a leader-first routed session
- make startup classify task shape before the first substantive answer
- make startup expose a routing trace
- explain both positive and negative routing decisions

**Non-Goals**

- automatic durable-team launch on every startup
- changing the meaning of `oh_my_codex` or `subagent_routing`
- replacing native Codex bypass startup

## Decisions

### Decision 1: Treat startup leadership as a runtime protocol, not just an installed file

Why:

- installed `team-leader.toml` alone does not guarantee startup-time behavior
- the startup wrapper must actively bind the protocol

### Decision 2: Classify first, launch later

Why:

- startup should decide whether durable-team thresholds are met
- startup should not eagerly launch `omx team` before the task phase is known

### Decision 3: Make routing explainable on first turn

Why:

- users should not have to infer whether routing happened from later behavior
- negative decisions such as "not enough parallel slices yet" should be visible

## Validation Plan

1. Start a fresh wrapped Codex session and verify it reports a leader-first routing posture.
2. Verify that the first-turn routing trace explains whether expert subagents are needed.
3. Verify that the first-turn routing trace explains whether `omx team` thresholds are met.
4. Verify that early-phase tasks do not auto-launch a durable team.
5. Verify that execute-parallel tasks can point to the threshold that would trigger `omx team`.
