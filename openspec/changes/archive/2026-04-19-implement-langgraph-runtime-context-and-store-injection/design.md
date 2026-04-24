## Context

The current user-level LangGraph lane already models durable execution, replay or recovery, reusable subgraph contracts, command-driven handoffs, and bounded streaming or debug observability. Those layers describe how the graph moves and how the operator inspects it.

What they do not yet describe clearly is how runtime dependencies enter the graph. Official LangGraph separates:

- static invocation context through `context_schema` and `Runtime.context`
- mutable run-local graph state through the graph state object
- injected cross-run storage through `Runtime.store`

The current local lane does not yet formalize that separation. The missing contract is therefore not memory behavior itself; it is runtime dependency injection and bounded store-availability posture.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph runtime-context contract aligned with `context_schema`
- define bounded injected-store posture for `Runtime.store`
- persist runtime-context and store-availability metadata in tracked LangGraph durable state
- expose runtime-injection posture through canonical durable-state inspection
- keep this layer additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- implementing semantic memory, retrieval policy, or embedding-backed search
- introducing a general-purpose dependency injection container
- redesigning command-driven, replay or recovery, reducer, or streaming behavior beyond runtime-injection integration points
- introducing cloud-hosted runtime configuration or remote secret-management policy

## Decisions

### Decision 1: Distinguish runtime context from mutable graph state explicitly

The first rollout should preserve the official conceptual split:

- runtime context is invocation-scoped and externally provided
- graph state is mutable and reducer-aware
- injected store is a separate capability surface

Alternative considered:

- encode runtime context as just another state channel
  - rejected because it would blur mutability and lifetime boundaries that LangGraph documents explicitly

### Decision 2: Treat injected store posture as capability metadata before semantic-memory behavior

This repository still has later queued work for memory store and semantic memory. The first runtime/store change should therefore stop at:

- whether a store is configured
- what store posture is available
- whether nodes may assume injected store access

Alternative considered:

- combine runtime injection and semantic memory into one change
  - rejected because it would mix dependency injection with later memory policy

### Decision 3: Keep user-level inspection bounded and non-secretive

Runtime context can include sensitive or environment-specific values. The inspectable durable-state surface should therefore expose bounded metadata, not raw secret-like payloads.

The first rollout should focus on:

- context schema name or shape indicators
- selected context keys or bounded key lists
- store configured or not configured
- helper pointers for deeper local inspection if needed

Alternative considered:

- expose full raw runtime context in the canonical durable-state summary
  - rejected because it risks leaking sensitive operator-facing values and overloads the summary surface

### Decision 4: One additive helper surface is enough for the first rollout

The current lane already has `inspect`, `history`, `replay`, `recover`, `subgraphs`, and `stream`. Runtime/store inspection should therefore stay small and additive.

The minimal additive user-level helper should allow runtime-context and injected-store posture inspection without creating many specialized wrappers.

Alternative considered:

- create separate helpers for context-only and store-only inspection
  - rejected because the operator question is usually one combined runtime-injection question

### Decision 5: Persist runtime-injection posture in tracked thread state, not only in docs

The current product line already values inspectable durable state. Runtime/store posture should therefore become durable metadata, not just playbook prose.

Alternative considered:

- document runtime injection in the playbook only
  - rejected because it would leave the operator unable to inspect actual repo-local posture

## Risks / Trade-offs

- [Risk] Runtime-context projection may expose sensitive information. -> Mitigation: project bounded schema or key metadata rather than raw secret-like values.
- [Risk] Store posture may be mistaken for semantic-memory readiness. -> Mitigation: keep store injection and semantic-memory behavior explicitly separated in contracts and docs.
- [Risk] Runtime metadata may drift from actual backend behavior. -> Mitigation: keep projection fields tied to the same Python-side contract and cover them with tests.
- [Risk] Additional helper surfaces may create operator sprawl. -> Mitigation: keep the first rollout to one additive runtime-inspection helper and canonical summary projection.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for runtime context and store injection.
2. Extend the LangGraph contract layer with context-schema and store-injection metadata.
3. Extend tracked thread and backend projection state with bounded runtime-injection posture.
4. Extend user-level helper surfaces and canonical durable-state projection with runtime/store inspection fields.
5. Validate bounded projection, injected-store posture, and helper-surface behavior without reopening semantic-memory scope.

Rollback strategy:

- revert runtime-context and store-injection projection fields and helper surfaces only
- keep command-driven, streaming, replay or recovery, and reusable subgraph behaviors intact

## Open Questions

- Should the first rollout project only context key names, or also classify context values by kind such as `user_id`, `model_provider`, or `db_dependency`?
- Should injected-store posture distinguish `configured but empty` from `configured and populated`, or is `configured` enough until semantic-memory work starts?
- Should runtime inspection expose stream-writer availability in this change, or leave that under streaming observability only?
