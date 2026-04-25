## Context

The repository already documents reducer-backed fan-out / fan-in merging as a missing next-layer LangGraph capability. The current user-level LangGraph lane is usable, but still explicitly described as partial rather than fully graph-native. This change addresses that specific gap.

The target is narrow: make parallel branch state updates safe, deterministic, and inspectable inside the existing user-level LangGraph durable lane. This is not a backend-policy or routing-policy change.

## Goals / Non-Goals

**Goals:**

- define a reducer-aware state contract for parallel LangGraph branches
- distinguish reducer-merged channels from single-writer channels
- make fan-in deterministic and checkpoint-resumable
- surface reducer merge status through the canonical inspectable durable-state view

**Non-Goals:**

- changing when `langgraph` is selected
- changing whether `langgraph` is additive versus default
- redefining loop families or iteration policy
- introducing reusable subgraphs or replay controls
- forcing `native_omx` to adopt the same merge semantics

## Decisions

### Decision 1: Reducers apply only to explicitly declared merge channels

The first rollout does not infer reducer behavior from arbitrary branch writes.

State fields are classified as one of:

- reducer-merged
- single-writer overwrite
- leader-owned derived summary

Unclassified multi-writer branch updates must not silently merge.

### Decision 2: Fan-out results merge into stable reducer-backed channels

Reducer-backed channels cover branch outputs that are naturally many-writer and additive, such as:

- branch findings or observations
- branch evidence references
- branch artifact pointers
- branch completion records
- branch-local warnings or blockers

The exact field names may evolve in implementation, but the contract requires explicit reducer declaration per mergeable channel.

### Decision 3: Single-writer fields remain protected from accidental branch fan-in

Fields such as current phase, thread identity, selected backend family, final acceptance posture, and frozen top-level execution directives remain single-writer fields.

Parallel branches may read them, but branch fan-in must not silently overwrite them from multiple writers.

### Decision 4: Fan-in must be deterministic under resume and replay-from-checkpoint conditions

Reducer semantics must be order-stable enough that resumed execution produces the same merged durable state meaning for the same set of completed branch outputs.

The contract therefore requires:

- idempotent branch result handling where feasible
- stable item identity for append-like merged records
- no dependence on incidental arrival order for correctness-critical fields

### Decision 5: Inspectability remains summary-first, not full-state rendering

The canonical durable-state surface does not need to print the full merged payload. It does need to expose enough reducer-aware status to explain what happened.

At minimum the LangGraph projection should be able to report:

- whether reducer-backed channels are present
- whether parallel branch fan-out is active or completed
- which merge channels received branch results
- whether any branch writes were rejected as invalid multi-writer updates
- source pointers for the merged state

## Risks / Trade-offs

- [Risk] Reducer scope may become too broad too early. -> Mitigation: the first rollout formalizes only explicitly declared merge channels.
- [Risk] Append-like reducers may accumulate duplicate branch records. -> Mitigation: require stable per-branch item identity or equivalent dedup-safe merge behavior.
- [Risk] Operators may confuse merged branch state with final accepted output. -> Mitigation: keep leader-owned final summary fields distinct from reducer-merged branch channels.
- [Risk] Older checkpoints may not contain reducer metadata. -> Mitigation: keep rollout additive and allow older records to inspect as pre-reducer state.

## Migration Plan

1. Add proposal, design, and delta spec contracts for reducer-backed fan-out / fan-in semantics.
2. Extend the LangGraph backend spec with explicit merge-channel classification and deterministic fan-in rules.
3. Extend the inspectable durable-state surface with reducer-aware merge status and source-attribution expectations.
4. Validate deterministic merge behavior, invalid multi-writer rejection, and checkpoint-safe reducer resume.
5. Keep routing and backend-selection policy unchanged while reducer semantics harden.

## Open Questions

- Which reducer-merged channels should be first-rollout mandatory versus optional?
- Should reducer metadata include explicit reducer names, or only channel classification and source attribution?
- Should pre-reducer threads surface a distinct compatibility flag in the canonical durable-state summary, or only in backend-specific projection data?
