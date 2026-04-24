## Context

The current user-level LangGraph lane is already additive, repo-local, and durable. It can persist thread state, checkpoint progress, interrupt for approvals, resume later, expose current thread posture through the canonical inspectable durable-state surface, persist frozen implementation briefs and survivor queues, and merge reducer-aware branch state.

The remaining gap is not durable execution itself. The gap is operator-grade replay and recovery. The operator needs a safe way to inspect how a thread arrived at its current state, to examine prior checkpoints or state snapshots, and to apply bounded recovery when the current durable state needs deliberate repair instead of blind resume.

This change is narrow: add replay, time-travel, state-history inspection, and explicit recovery or update-state-style controls for tracked user-level LangGraph threads. This is not a backend-selection change, routing-policy change, loop-policy rewrite, or reducer redesign.

## Goals / Non-Goals

**Goals:**

- define read-oriented replay and state-history inspection for tracked LangGraph threads
- define explicit checkpoint or state-history targeting for time-travel
- define bounded update-state-style recovery mutation for tracked LangGraph durable state
- surface replay or recovery posture and helper pointers through the canonical inspectable durable-state surface
- keep recovery explicit, source-attributed, and operator-auditable

**Non-Goals:**

- changing when `langgraph` is selected
- changing the stable default backend
- reopening activation thresholds or retrofit policy
- redesigning frozen briefs, survivor queues, or reducer channel classes
- introducing hidden auto-repair or blind auto-time-travel behavior

## Decisions

### Decision 1: Replay and history inspection stay read-first

Replay, checkpoint-history inspection, and state-history inspection stay read-oriented by default.

They should answer:

- which tracked thread is being inspected
- which checkpoints or historical state records exist
- what phase or recovery posture each record represents
- which source files or persisted records back the view
- which follow-up helpers are available for resume, replay, time-travel, or state repair

Alternative considered:

- merge replay and recovery into one opaque helper
  - rejected because operators must be able to inspect before mutating

### Decision 2: Time-travel is an explicit recovery action, not an inspect side effect

Time-travel should require an explicit target such as a checkpoint id, state-history record, or equivalent stable recovery pointer.

Inspection may recommend eligible targets, but inspection itself must not mutate thread state.

Alternative considered:

- infer the best rewind target automatically
  - rejected because recovery intent must remain deliberate and auditable

### Decision 3: Update-state-style recovery is bounded and schema-aware

The first rollout should allow explicit state repair only through bounded user-level controls that respect the existing LangGraph durable-state contract.

The recovery layer may update tracked state fields that are explicitly designated as recoverable, but it must not become a generic arbitrary-state editor.

Alternative considered:

- expose raw state-file editing as the operator path
  - rejected because it bypasses validation, attribution, and safety boundaries

### Decision 4: Recovery posture remains separate from accepted outcome

A replayed view, a historical checkpoint, or a recovered state is not itself the accepted final thread outcome.

The inspectable surface should distinguish:

- current active state
- replay target or historical record
- recovered-but-not-yet-resumed posture
- resumed or converged posture after recovery

Alternative considered:

- collapse recovered state into normal active-state reporting immediately
  - rejected because operators need to see that recovery occurred

### Decision 5: Existing durable artifacts remain inputs, not redesign targets

Replay and recovery may reference frozen implementation briefs, survivor queues, reducer-aware channels, interrupts, and checkpoints, but this change does not redefine those artifact families.

Where repair touches reducer-aware state, the recovery layer must preserve the existing reducer contract rather than introduce ad hoc merge behavior.

## Risks / Trade-offs

- [Risk] Recovery mutation may drift into a generic state editor. -> Mitigation: keep the first rollout bounded to explicit recoverable fields and explicit target records.
- [Risk] Operators may confuse replay with time-travel. -> Mitigation: keep replay read-only and reserve time-travel for explicit recovery actions.
- [Risk] Recovery may obscure provenance of the current thread state. -> Mitigation: require source attribution, recovery markers, and explicit helper output.
- [Risk] Old records may not carry enough history metadata for rich replay. -> Mitigation: classify them explicitly and allow reduced inspection fidelity without overstating guarantees.
- [Risk] Reducer-aware branch state may be repaired incorrectly. -> Mitigation: require recovery controls to preserve existing reducer semantics and reject invalid multi-writer repair shapes.

## Migration Plan

1. Add proposal, design, and delta spec contracts for LangGraph replay, history, and recovery controls.
2. Extend the LangGraph backend contract with read-only replay and history semantics plus explicit recovery mutation semantics.
3. Extend generated control surfaces and entrypoints with additive replay, history, time-travel, and update-state helpers.
4. Extend the canonical inspectable durable-state surface with replay or recovery posture, target pointers, and source attribution.
5. Validate read-only inspection, explicit mutation gating, and post-recovery resumability.

## Open Questions

- Which state fields are in-scope for first-rollout update-state-style recovery versus deferred to later rollout?
- Should time-travel create a new tracked recovery record or rewrite the tracked active record in place?
- Should pre-history or low-fidelity older LangGraph records expose limited replay only, or only a compatibility classification plus raw source pointers?
