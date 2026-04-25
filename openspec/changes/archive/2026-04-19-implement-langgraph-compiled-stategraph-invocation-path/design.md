## Context

The current user-level LangGraph lane now supports a broad contract surface: reusable subgraphs, command-driven handoffs, streaming observability, runtime/store injection, memory posture, graph migration, multi-interrupt approval queues, replay/recovery controls, repo-local durable artifacts, a bounded graph-kernel layer, and a bounded primary-runtime engine posture.

What it still does not do is make a live compiled graph invocation path the primary runtime surface. The remaining gap is therefore not just “stronger posture reporting”; it is the absence of a compiled `StateGraph` invocation path that acts as the real execution core while preserving the user-level operator model.

## Goals / Non-Goals

**Goals:**

- define a live compiled `StateGraph` invocation path for the user-level LangGraph lane
- map the current seven-phase shell, graph-kernel posture, and primary-runtime engine posture into compiled graph-native invocation
- preserve repo-local artifacts and inspectable operator surfaces while shifting toward real graph execution
- keep the rollout additive and compatibility-aware

**Non-Goals:**

- replacing native Codex as leader
- replacing `native_omx` as the worker-centric default backend
- forcing full parity with every official LangGraph feature in one monolithic rewrite
- introducing cloud-only orchestration infrastructure

## Decisions

### Decision 1: The next runtime step should be live invocation, not only richer engine projection

The repository already exposes bounded engine posture. The next worthwhile step is to add a live compiled invocation path instead of just another metadata layer.

### Decision 2: The seven-phase shell remains the stable external contract

The compiled invocation path should execute the seven-phase shell graph-natively rather than replacing the operator-facing phase model.

### Decision 3: Existing durable artifacts remain compatibility anchors

Thread ids, checkpoints, interrupts, implementation briefs, survivor queues, and inspectable summaries must remain compatibility anchors during the compiled invocation rollout.

### Decision 4: Keep the change bounded to one deeper runtime step

This change should focus on compiled invocation as the new execution center. Broader graph families, richer policies, or later automation can remain future work if still needed.

## Risks / Trade-offs

- [Risk] Live invocation can destabilize helper surfaces that currently depend on bounded posture only. -> Mitigation: keep inspect/status contracts compatibility-aware.
- [Risk] The change can sprawl into a full runtime rewrite. -> Mitigation: keep scope centered on compiled invocation identity, phase mapping, and compatibility projections.
- [Risk] It may overclaim official parity too early. -> Mitigation: describe the result as a compiled invocation step rather than full LangGraph parity.

## Validation Plan

1. Add proposal, design, and delta specs for the compiled invocation path.
2. Extend the LangGraph contract layer with compiled invocation identity and execution posture.
3. Map the current seven-phase shell into a live compiled graph path while preserving repo-local artifacts.
4. Extend user-level helper surfaces and canonical durable-state projection with compiled invocation posture.
5. Validate compiled invocation posture without regressing the current operator model.
