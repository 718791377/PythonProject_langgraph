## Context

The existing additive LangGraph backend already establishes repo-local threads, checkpoints, graph phases, interrupts, research handoff, and survivor queues. What remains weak is not the presence of those concepts, but the stability of the artifact contract around the two durable objects that justify choosing LangGraph for graph-shaped work:

- `frozen implementation brief`
- `survivor queue`

The main bottleneck is artifact semantics and inspectability, not backend policy.

## Goals / Non-Goals

**Goals:**

- make the frozen implementation brief a stable, first-class durable artifact
- make the survivor queue a stable, first-class durable artifact
- define minimum fields, lifecycle rules, and consumption boundaries for both artifacts
- expose artifact presence and pointers through the canonical inspectable durable-state surface
- keep the current additive LangGraph backend model unchanged

**Non-Goals:**

- adding a new backend-selection surface
- adding a new activation-policy surface
- requiring LangGraph to become the stable default backend
- forcing `native_omx` to adopt the same artifact persistence model
- changing bug-triad routing or startup-routing policy

## Decisions

### Decision 1: Harden existing LangGraph artifacts rather than inventing a parallel artifact family

This change extends the artifacts already identified in the LangGraph backend contract instead of adding a second artifact model. That preserves continuity with the current user-level plan and avoids policy drift.

### Decision 2: The frozen implementation brief is a first-class durable handoff object

The brief is the durable handoff artifact created after open-ended research and before implementation begins in a fresh execution context.

Minimum stable fields:

- `brief_id`
- `thread_id`
- `objective`
- `non_goals`
- `accepted_decisions`
- `constraints`
- `interfaces`
- `ownership_boundaries`
- `acceptance_criteria`
- `validation_plan`
- `source_evidence_refs`
- `frozen_at`

### Decision 3: The survivor queue persists only judged survivors

The survivor queue is the durable repair queue that remains after adversarial review and judge arbitration.

Minimum stable fields per item:

- `bug_id`
- `title`
- `severity`
- `evidence`
- `judge_verdict`
- `owner_lane`
- `status`
- `verification_result`
- `updated_at`

Persist only judged survivors, not every candidate claim from the bug triad.

### Decision 4: Inspectability is presence-and-pointer oriented

The canonical inspectable durable-state summary does not need to render the full artifact body. It does need to report:

- whether a frozen implementation brief exists
- whether a survivor queue exists
- survivor count or status when known
- inspect pointer
- resume pointer when relevant

### Decision 5: Fresh-context and repair-lane consumption stay explicit

Implementation reads from the frozen brief instead of from the full open-ended research context. Repair or debugger lanes consume the persisted survivor queue instead of requiring the bug triad to remain persistent workers.

## Risks / Trade-offs

- [Risk] Hardening artifact fields may expose inconsistencies in existing LangGraph state. -> Mitigation: keep the first rollout additive and tolerate older records where strict fields are unavailable.
- [Risk] Over-specifying artifact rendering could bloat the inspectable summary. -> Mitigation: expose presence, counts, and pointers instead of full artifact bodies.
- [Risk] Survivor queues could become noisy if candidate bugs are persisted too early. -> Mitigation: persist only judge-approved survivors.
- [Risk] Fresh-context execution could regress if consumers still lean on old research context. -> Mitigation: make the frozen brief the explicit handoff source in the contract.

## Migration Plan

1. Add proposal, design, and delta spec contracts for hardened LangGraph durable artifacts.
2. Extend the LangGraph backend spec with stable frozen-brief and survivor-queue field requirements.
3. Extend the inspectable durable-state surface with artifact-presence and pointer requirements.
4. Validate fresh-context implementation handoff and resumable repair-lane consumption.
5. Keep the existing additive LangGraph backend and routing policy unchanged while artifact semantics harden.

## Open Questions

- Should artifact versions be explicitly recorded so future schema expansion can be handled without ambiguity?
- Should survivor queue inspection expose only counts and pointers, or also a small severity summary?
- Should re-freeze of an implementation brief be modeled as revision of the same `brief_id` or creation of a new durable artifact?
