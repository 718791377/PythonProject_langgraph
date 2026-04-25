## Context

The current user-level LangGraph lane now supports reusable subgraphs, command-driven handoffs, streaming observability, runtime/store injection, memory posture, graph migration, multi-interrupt approval queues, replay/recovery controls, and repo-local durable artifacts. That is a broad implemented contract surface.

What it still does not do is make a real `StateGraph` execution kernel the primary runtime center. The current lane still behaves like a projection-first durable shell that persists and inspects LangGraph posture rather than a graph-native execution kernel that directly models nodes, edges, and resumable graph state as the first-class runtime.

## Goals / Non-Goals

**Goals:**

- define a `StateGraph`-first runtime kernel for the user-level LangGraph lane
- map the current seven-phase durable shell into graph-native runtime nodes, edges, and loop posture
- preserve repo-local durable artifacts and inspectable operator surfaces while moving closer to official LangGraph execution semantics
- keep the rollout additive and compatibility-aware

**Non-Goals:**

- replacing native Codex as leader
- replacing `native_omx` as the worker-centric default durable backend
- redesigning every current LangGraph surface in one monolithic rewrite
- introducing cloud-only orchestration infrastructure

## Decisions

### Decision 1: Treat the runtime gap as kernel-first, not surface-first

The next mainline should move the execution core closer to `StateGraph` rather than merely adding more projection fields.

### Decision 2: Preserve the existing seven-phase operator model as the external contract

The user-level operator model already uses the seven-phase durable shell. The kernel change should therefore remap that shell into graph-native runtime state instead of discarding it.

### Decision 3: Keep compatibility explicit

The kernel rollout should preserve existing repo-local durable artifacts and inspectable summaries as much as possible, using compatibility-aware projections rather than silently breaking the operator surface.

### Decision 4: Do not overload this change with every future LangGraph feature

This change should focus on the kernel gap itself. Later expansions can still deepen policy, automation, or broader graph families once the runtime core is stronger.

## Risks / Trade-offs

- [Risk] A deeper kernel change can destabilize current helper surfaces. -> Mitigation: keep the external inspect/status contract compatibility-aware.
- [Risk] The change can sprawl into a full rewrite. -> Mitigation: keep scope centered on kernel identity, phase mapping, and compatibility projections.
- [Risk] It may overclaim official parity too early. -> Mitigation: keep the design explicit about “closer to `StateGraph`” rather than “full parity”.

## Validation Plan

1. Add proposal, design, and delta specs for the `StateGraph` runtime kernel.
2. Extend the LangGraph contract layer with graph-native kernel identity and node or edge posture.
3. Map the seven-phase durable shell into graph-native runtime state while preserving repo-local artifacts.
4. Extend user-level helper surfaces and canonical durable-state projection with kernel-aware posture.
5. Validate graph-native execution posture without regressing the current operator model.
