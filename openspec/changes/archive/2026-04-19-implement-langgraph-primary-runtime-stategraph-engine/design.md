## Context

The current user-level LangGraph lane now supports reusable subgraphs, command-driven handoffs, streaming observability, runtime/store injection, memory posture, graph migration, multi-interrupt approval queues, replay/recovery controls, repo-local durable artifacts, and a bounded graph-kernel layer that maps the seven-phase shell into `StateGraph`-oriented node and transition posture.

What it still does not do is make a compiled `StateGraph` execution engine the primary runtime path. The kernel layer is currently an inspectable compatibility surface around a projection-first durable shell. The remaining runtime gap is to make graph-native invocation primary while preserving the operator-facing contracts already landed.

## Goals / Non-Goals

**Goals:**

- define a compiled `StateGraph`-first primary-runtime engine for the user-level LangGraph lane
- map the seven-phase durable shell, current subgraphs, and durable artifacts into graph-native invocation semantics
- preserve repo-local artifacts and inspectable operator surfaces while shifting the runtime center of gravity toward compiled graph execution
- keep the rollout additive and compatibility-aware

**Non-Goals:**

- replacing native Codex as leader
- replacing `native_omx` as the worker-centric default backend
- forcing full parity with every official LangGraph feature in one monolithic rewrite
- introducing cloud-only orchestration infrastructure

## Decisions

### Decision 1: The next runtime step should be execution-first, not projection-first

The bounded graph-kernel layer already gives the operator a graph-native vocabulary. The next step should therefore deepen the actual execution core rather than adding another projection-only layer.

### Decision 2: The seven-phase shell remains the operator contract

The current user-level operator model is built around the seven-phase shell. The new engine should compile and execute that model graph-natively rather than replacing the operator-facing phase contract.

### Decision 3: Preserve landed durable artifacts as compatibility anchors

Existing thread ids, checkpoints, interrupts, implementation briefs, survivor queues, and inspectable summaries are already part of the stable user-level story. The primary-runtime rollout should preserve them as compatibility anchors rather than treating them as disposable scaffolding.

### Decision 4: Keep the scope bounded to one deeper runtime step

This change should focus on the primary-runtime engine itself. Broader graph families, richer automation, or additional subgraph expansion can remain later work if still needed.

## Risks / Trade-offs

- [Risk] A deeper runtime step can destabilize current helper surfaces. -> Mitigation: keep the external inspect/status contract compatibility-aware.
- [Risk] The change can sprawl into a full runtime rewrite. -> Mitigation: keep scope centered on compiled graph execution posture, phase mapping, and compatibility projections.
- [Risk] It may overclaim official parity too early. -> Mitigation: describe the result as a primary-runtime engine step rather than full LangGraph parity.

## Validation Plan

1. Add proposal, design, and delta specs for the primary-runtime `StateGraph` engine.
2. Extend the LangGraph contract layer with engine identity and compiled graph-execution posture.
3. Map the current seven-phase shell into compiled graph-native invocation while preserving repo-local artifacts.
4. Extend user-level helper surfaces and canonical durable-state projection with primary-runtime engine posture.
5. Validate engine-centric execution posture without regressing the current operator model.
