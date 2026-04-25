## Context

The current user-level LangGraph lane already persists repo-local threads, checkpoints, replay/recovery posture, reusable subgraph contracts, command-driven transitions, streaming posture, runtime/store injection, memory posture, and graph-migration compatibility. Those layers make the lane durable and inspectable.

What they still do not formalize is how one tracked thread can surface more than one pending interrupt or approval need in the same invocation. Official LangGraph explicitly allows multiple interrupts in one invocation. The local lane still represents interrupt posture as one flat record, which is not enough once approvals must remain ordered and resume values must stay attributable.

The bottleneck is therefore not human approval itself. The bottleneck is missing durable queue structure that tells the operator which interrupt items are pending, which have been satisfied, and which resume payload belongs to which interrupt item.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph multi-interrupt approval-queue contract
- persist ordered interrupt items for tracked threads
- preserve bounded queue status and resume mapping in repo-local LangGraph durable state
- expose approval-queue posture through canonical durable-state inspection
- keep this layer additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- implementing automatic approval resolution or silent queue draining
- redesigning replay, recovery, reducer, subgraph, command-driven, streaming, runtime/store, memory, or graph-migration behavior beyond approval-queue-aware projection points
- introducing cloud-only approval infrastructure

## Decisions

### Decision 1: Treat multiple interrupts as an ordered queue instead of a single flat record

The first rollout should preserve interrupt ordering explicitly.

The guard should therefore represent pending approval posture as an ordered queue of interrupt items rather than one flattened interrupt blob.

Alternative considered:

- keep one interrupt record and append opaque metadata
  - rejected because the operator still needs stable item-level inspection

### Decision 2: Separate queue posture from resume mapping

The local lane should distinguish:

- which interrupt items are pending
- which items have been satisfied
- what bounded resume values or resume keys are associated with the operator response

Alternative considered:

- treat resume data as a queue-less thread-level blob
  - rejected because it loses item-level attribution

### Decision 3: Keep the first rollout bounded to operator-facing queue truth

The first rollout should focus on:

- interrupt item identity
- queue order
- item status
- bounded resume mapping
- helper pointers for inspect or explicit resume

Alternative considered:

- add automatic queue resolution and approval policies in the same change
  - rejected because it would expand scope beyond durable queue truth

### Decision 4: The canonical durable-state summary should expose queue posture, not raw interrupt payload dumps

The canonical summary should stay operator-oriented and bounded.

The first rollout should therefore project:

- queue size
- pending item identifiers or bounded summaries
- current approval posture
- relevant helper pointers

Alternative considered:

- dump every raw interrupt payload directly into the canonical summary
  - rejected because it overloads a summary surface with low-level detail

## Risks / Trade-offs

- [Risk] Queue posture may under-specify some interrupt semantics. -> Mitigation: keep reason/status fields explicit and bounded.
- [Risk] Operators may expect automatic approval handling after seeing a queue. -> Mitigation: keep the first rollout inspection-first and explicit-resume oriented.
- [Risk] Resume mappings may drift from pending queue items. -> Mitigation: preserve stable interrupt identifiers and cover mapping behavior with tests.
- [Risk] Another helper surface may add operator sprawl. -> Mitigation: keep the first rollout to one additive approval-queue inspection helper.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for multi-interrupt approval queues.
2. Extend the LangGraph contract layer with interrupt-queue and resume-mapping metadata.
3. Extend tracked thread and backend projection state with bounded queue posture.
4. Extend user-level helper surfaces and canonical durable-state projection with approval-queue fields.
5. Validate ordered queue inspection and explicit resume mapping without silent queue collapse.

Rollback strategy:

- revert multi-interrupt queue projection fields and helper surfaces only
- keep graph-migration, memory, runtime/store, command-driven, streaming, replay/recovery, and reusable subgraph behaviors intact

## Open Questions

- Should the first rollout expose queue item ids only, or also a bounded queue summary label per item?
- Should resume mapping allow one payload per item only, or also ordered aggregate resume payloads?
- Should interrupted threads and accepted threads expose the same queue posture scale, or should queue posture collapse after resolution?
