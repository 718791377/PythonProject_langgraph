## Context

The current user-level LangGraph lane now covers durable execution, replay or recovery, reusable subgraphs, command-driven handoffs, streaming observability, and bounded runtime/store injection posture. Those layers define execution, inspection, and dependency injection.

What they still do not define is actual long-term memory behavior. Official LangGraph treats memory as more than injected store availability: it includes durable memory-store usage and semantic lookup or semantic search patterns over persisted memory. The current local lane has not yet formalized that layer.

The current bottleneck is therefore not store injection itself. The bottleneck is missing memory behavior and semantic lookup posture on top of that injected store capability.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph memory-store contract
- define bounded semantic-memory posture without hard-coding one provider
- persist memory-store and semantic lookup metadata in tracked LangGraph durable state
- expose memory-store and semantic-memory posture through canonical durable-state inspection
- keep this layer additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- forcing one embedding provider, vector database, or semantic-search service
- turning the first rollout into a full production search platform
- redesigning command-driven, streaming, runtime-injection, replay or recovery, or reducer behavior beyond memory-aware integration points
- introducing cloud-only memory persistence requirements

## Decisions

### Decision 1: Build memory-store posture on top of runtime/store injection instead of replacing it

The previous runtime/store mainline already established injected store posture. The memory mainline should refine that layer, not replace it.

The first rollout should therefore distinguish:

- injected store is available
- durable memory store is configured
- semantic lookup is available or not available

Alternative considered:

- collapse runtime store injection and memory store into one undifferentiated store model
  - rejected because dependency injection and memory semantics are not the same layer

### Decision 2: Keep semantic-memory posture provider-neutral in the first rollout

This repository should not lock the user-level lane to one provider too early. The first rollout should preserve bounded provider-neutral posture such as:

- semantic search enabled or not enabled
- semantic store kind
- retrieval namespace or memory scope

Alternative considered:

- require one vector backend and embedding provider immediately
  - rejected because it would overconstrain the product line before operator policy is settled

### Decision 3: Project bounded memory metadata, not raw memory contents, into the canonical summary

The inspectable durable-state summary should stay bounded and operator-facing. It should not become a raw memory dump.

The first rollout should focus on:

- store configured or not configured
- semantic lookup enabled or not enabled
- memory namespaces or bounded memory scopes
- helper pointers for deeper local inspection

Alternative considered:

- expose full memory entries through the canonical summary
  - rejected because it overloads the summary surface and may expose sensitive memory contents

### Decision 4: One additive helper surface is enough for the first rollout

The current lane already has many additive helpers. Memory/store inspection should therefore stay small and additive.

The minimal user-level helper should allow bounded inspection of memory-store and semantic-memory posture without fragmenting into many provider-specific wrappers.

Alternative considered:

- separate wrappers for memory store and semantic lookup from day one
  - rejected because the operator question is usually one combined memory question

### Decision 5: Keep semantic-memory behavior bounded to posture and inspectability before advanced retrieval flows

The first rollout should not attempt full agent memory behavior. It should instead establish:

- stable contract fields
- durable posture in tracked state
- helper surfaces for inspection
- tests that prove bounded memory metadata is projected

Alternative considered:

- immediately implement full retrieval augmentation and long-horizon memory policy
  - rejected because it would expand scope far beyond the current mainline sequencing rule

## Risks / Trade-offs

- [Risk] Memory-store posture may be mistaken for full semantic-memory quality. -> Mitigation: keep semantic-memory projection bounded and provider-neutral.
- [Risk] Memory metadata may expose sensitive namespaces or content hints. -> Mitigation: project bounded namespaces or capability posture, not raw memory contents.
- [Risk] Store injection and memory behavior may drift apart conceptually. -> Mitigation: keep memory-store posture explicitly layered on top of the existing runtime/store injection contract.
- [Risk] Another helper surface may add operator sprawl. -> Mitigation: keep the first rollout to one additive memory/store inspection helper.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for memory-store and semantic-memory support.
2. Extend the LangGraph contract layer with bounded memory-store and semantic-memory metadata.
3. Extend tracked thread and backend projection state with memory-store and semantic lookup posture.
4. Extend user-level helper surfaces and canonical durable-state projection with memory/store inspection fields.
5. Validate bounded memory posture, semantic-search posture, and helper-surface behavior without forcing one provider implementation.

Rollback strategy:

- revert memory-store and semantic-memory projection fields and helper surfaces only
- keep runtime/store injection, command-driven, streaming, replay or recovery, and reusable subgraph behaviors intact

## Open Questions

- Should the first rollout distinguish durable memory namespaces from semantic-search namespaces, or is one bounded namespace list enough?
- Should semantic-memory posture expose an embedding-provider hint, or remain fully provider-neutral until a later rollout?
- Should memory inspection expose bounded memory entry counts, or only store configured/semantic enabled posture in the first rollout?
