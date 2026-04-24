## Context

The current user-level LangGraph lane is durable and inspectable, but almost all operator visibility is snapshot-based. The operator can inspect current thread posture, replay prior checkpoints, recover bounded state, and examine reducer or command-driven metadata, but cannot watch graph activity stream in a LangGraph-native way.

The official LangGraph streaming surface is broader than token streaming. It supports event-oriented visibility such as `updates`, `checkpoints`, `tasks`, and `debug`, and can include nested subgraph emissions through `subgraphs=True`. Those are the parts most relevant to this repository's user-level durable orchestration line.

The bottleneck is therefore not basic visibility. The bottleneck is insufficient live, operator-grade observability for graph execution and nested handoffs. This change should solve that without turning the local lane into a full external observability platform.

## Goals / Non-Goals

**Goals:**

- define a user-level LangGraph streaming and debug observability contract
- expose additive stream modes for `updates`, `checkpoints`, `tasks`, and `debug`
- preserve nested subgraph visibility in the first rollout
- project latest stream posture and relevant helper pointers through canonical durable-state inspection
- keep the streaming model additive under the existing Codex CLI leader and oh-my-codex workflow layer

**Non-Goals:**

- changing when `langgraph` is selected as the effective durable backend
- introducing cloud-hosted tracing or dashboards
- designing a full front-end stream renderer
- reopening replay, recovery, reducer, or command-driven control-flow contracts beyond stream-aware integration points
- replacing snapshot inspection with streaming-only inspection

## Decisions

### Decision 1: Treat streaming as additive operator observability, not as a replacement for snapshot inspection

The current lane already has `inspect`, `history`, `replay`, and `recover`. Streaming should complement those surfaces, not replace them.

The first rollout should therefore keep snapshot inspection as the stable baseline while adding:

- stream session start or observe behavior
- latest streamed event posture
- stream helper pointers

Alternative considered:

- replace snapshot inspection with a stream-first operator surface
  - rejected because historical and stable inspection remains necessary even when no live stream is active

### Decision 2: Prioritize event modes that are operationally useful for durable-team diagnosis

Official LangGraph supports more modes than this repository needs immediately. The first rollout should prioritize the modes that best explain orchestration state:

- `updates`
- `checkpoints`
- `tasks`
- `debug`

These modes map directly to operator questions about progress, checkpoint churn, branch execution, and unexpected graph behavior.

Alternative considered:

- make token or message streaming the first-class focus
  - rejected because this repository's current line is oriented around orchestration and durable state rather than chat UX

### Decision 3: Nested subgraph visibility should be explicit in the first rollout

The current user-level lane already uses reusable subgraph contracts. If streaming ignores nested subgraphs, the operator loses exactly the detail needed to diagnose parent or child handoffs.

The first rollout should therefore preserve whether stream output includes nested subgraph emissions.

Alternative considered:

- defer nested subgraph visibility until later
  - rejected because it would leave the new streaming surface blind at the most important graph boundary

### Decision 4: Stream posture should project a bounded latest-event summary into canonical durable-state inspection

The canonical durable-state summary should not become a raw event log. It should remain a stable summary surface.

The first rollout should project only a bounded stream posture such as:

- selected stream modes
- whether nested subgraphs are included
- latest event kind
- latest checkpoint or task signal when present

Alternative considered:

- store and expose the full stream log through the canonical summary
  - rejected because it would overload a summary surface with high-volume transient data

### Decision 5: The user-level helper surface should stay small

The first rollout should use one additive stream-focused helper rather than many per-mode wrappers.

The minimal user-level helper should support selecting one or more modes and an optional nested-subgraph flag while routing through the same Python backend.

Alternative considered:

- create separate wrappers for each stream mode
  - rejected because it would create command sprawl with little operator benefit

## Risks / Trade-offs

- [Risk] Stream output may become too noisy for normal operators. -> Mitigation: keep the first rollout focused on a bounded set of modes and a latest-event summary.
- [Risk] Streaming posture may drift away from the actual backend behavior. -> Mitigation: keep stream metadata tied to the backend contract and covered by integration tests.
- [Risk] Nested subgraph visibility may expose too much low-level detail. -> Mitigation: make nested output explicit and opt-in through the helper surface.
- [Risk] Operators may confuse stream posture with persisted accepted outcome. -> Mitigation: keep stream summary separate from final accepted-state reporting.

## Migration Plan

1. Add proposal, design, and delta spec artifacts for streaming and debug observability.
2. Extend the LangGraph contract layer with stream-mode and latest-event contract fields.
3. Extend tracked thread or checkpoint state with bounded stream-session and latest-event posture.
4. Extend user-level helper surfaces and canonical durable-state projection with stream-aware inspection pointers.
5. Validate event-mode selection, nested subgraph visibility, and durable-state summary projection.

Rollback strategy:

- revert streaming helper surfaces and latest-event projection only
- keep snapshot inspection, replay or recovery, command-driven control flow, and reusable subgraph contracts intact

## Open Questions

- Should the first rollout persist only the latest stream event summary, or also a bounded recent-event ring for operator inspection?
- Should `values` be deferred entirely, or included later as an advanced high-volume mode after the event-oriented rollout lands?
- Should `debug` stream posture expose raw event payloads directly, or only a normalized summary in the canonical durable-state surface?
