## Context

The current user-level LangGraph lane already persists repo-local threads, checkpoints, replay or recovery posture, reusable subgraph contracts, command-driven transitions, streaming posture, runtime/store injection, and memory posture. Those layers make the lane durable and inspectable.

What they still do not formalize is how persisted threads relate to a changing graph. Official LangGraph explicitly distinguishes migration-safe changes from changes that can make existing interrupted or resumable threads unsafe to continue. The local lane does not yet encode that distinction as durable operator-facing posture.

The bottleneck is therefore not migration execution itself. The bottleneck is missing compatibility classification that tells the operator whether an older tracked thread is still safe to resume under the current graph contract.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph graph-migration compatibility contract
- classify tracked threads against the current graph topology and state-schema posture
- persist compatibility posture in tracked LangGraph durable state
- expose migration-safe versus degraded versus incompatible posture through canonical durable-state inspection
- keep this layer additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- implementing automatic graph rewrites or silent state repair
- forcing thread migration in place without explicit operator inspection
- redesigning replay, recovery, reducer, command-driven, streaming, runtime/store, or memory behavior beyond compatibility-aware projection points
- introducing cloud-only migration orchestration or deployment gates

## Decisions

### Decision 1: Treat migration as compatibility classification before mutation

The first rollout should not attempt automatic migration. It should first tell the truth about thread compatibility.

The guard should therefore classify tracked threads into bounded postures such as:

- migration_safe
- degraded_compatible
- incompatible

Alternative considered:

- automatically rewrite persisted thread state on first inspect
  - rejected because migration safety must remain inspectable and explicit before mutation

### Decision 2: Separate topology compatibility from state-schema compatibility

Official LangGraph migration guidance distinguishes graph-node changes from state-schema changes. The local lane should preserve that distinction.

The first rollout should therefore allow separate bounded signals for:

- topology posture
- state-schema posture
- overall thread-compatibility verdict

Alternative considered:

- collapse all compatibility into one opaque boolean
  - rejected because the operator needs to know why a thread is or is not resumable

### Decision 3: Keep the first rollout bounded to operator-facing guardrails

The first rollout should focus on:

- current graph contract version or equivalent identity
- tracked thread contract version or equivalent identity
- compatibility verdict
- helper pointers for inspect, replay, or explicit operator decision

Alternative considered:

- implement full migration plans and automatic rollout sequencing in the same change
  - rejected because it would expand scope beyond compatibility guarding

### Decision 4: The canonical durable-state summary should expose migration posture, not raw diff detail

The canonical summary should stay operator-oriented and bounded. It should not become a raw migration diff report.

The first rollout should therefore project:

- compatibility verdict
- migration posture
- bounded reason codes
- relevant helper pointers

Alternative considered:

- dump raw topology or schema diffs directly into the canonical summary
  - rejected because it overloads a summary surface with low-level detail

### Decision 5: Preserve resumed-thread caution when compatibility is degraded

Some changes may be survivable but lower-confidence. The local lane should be able to mark such threads as degraded-compatible rather than pretending they are fully safe.

Alternative considered:

- treat every non-broken thread as migration-safe
  - rejected because that would overstate safety and mislead operators

## Risks / Trade-offs

- [Risk] Compatibility posture may under-specify actual migration hazards. -> Mitigation: keep reason codes explicit and bounded, and do not overclaim automatic safety.
- [Risk] Operators may expect automatic migration after seeing a guard. -> Mitigation: keep the first rollout inspection-first and helper-pointer oriented.
- [Risk] Version identifiers may drift from actual graph changes. -> Mitigation: keep contract-version metadata tied to the same Python-side contract and cover it with tests.
- [Risk] Another helper surface may add operator sprawl. -> Mitigation: keep the first rollout to one additive migration/compatibility inspection helper.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for graph migration and thread compatibility.
2. Extend the LangGraph contract layer with compatibility-classification metadata.
3. Extend tracked thread and backend projection state with bounded migration posture and reason codes.
4. Extend user-level helper surfaces and canonical durable-state projection with migration/compatibility inspection fields.
5. Validate migration-safe, degraded-compatible, and incompatible classifications without automatic rewrites.

Rollback strategy:

- revert migration and compatibility projection fields and helper surfaces only
- keep memory, runtime/store, command-driven, streaming, replay or recovery, and reusable subgraph behaviors intact

## Open Questions

- Should the first rollout use explicit contract-version strings, or derive compatibility from bounded feature flags?
- Should interrupted threads and completed threads use the same compatibility verdict scale, or should resumed-thread risk be stricter?
- Should migration posture expose bounded reason codes only, or also a compatibility timestamp in the first rollout?
