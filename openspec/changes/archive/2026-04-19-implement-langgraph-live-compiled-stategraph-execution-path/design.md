## Context

The current user-level LangGraph lane now supports a broad contract surface and several progressively deeper runtime layers: graph-kernel posture, primary-runtime engine posture, and compiled-invocation posture. Those layers make the runtime direction inspectable.

What they still do not do is make an actually executed compiled graph branch the primary live execution surface. The remaining gap is therefore no longer about vocabulary or projection. It is about crossing the line from “the runtime reports a compiled path” to “the runtime can actually drive work through a compiled graph branch when the environment supports it”.

## Goals / Non-Goals

**Goals:**

- define a live compiled `StateGraph` execution path for the user-level LangGraph lane
- map the current seven-phase shell and durable artifacts into an actually executed compiled graph branch
- preserve repo-local artifacts and inspectable operator surfaces while shifting toward real live compiled execution
- keep the rollout additive and compatibility-aware

**Non-Goals:**

- replacing native Codex as leader
- replacing `native_omx` as the worker-centric default backend
- forcing full parity with every official LangGraph feature in one monolithic rewrite
- introducing cloud-only orchestration infrastructure

## Decisions

### Decision 1: The next step should cross from posture to live execution

The repository already exposes bounded compiled-invocation posture. The next worthwhile step is to add a real live execution branch rather than adding another descriptive layer.

### Decision 2: The seven-phase shell remains the stable external contract

The live compiled execution path should drive the existing seven-phase shell graph-natively rather than replacing the operator-facing phase model.

### Decision 3: Existing durable artifacts remain compatibility anchors

Thread ids, checkpoints, interrupts, implementation briefs, survivor queues, and inspectable summaries remain compatibility anchors during the live-execution rollout.

### Decision 4: Keep the scope bounded to one deeper runtime step

This change should focus on live compiled execution itself. Broader graph families, richer automation, or additional runtime generalization can remain future work.

## Risks / Trade-offs

- [Risk] Live execution can destabilize helper surfaces that currently depend on bounded posture only. -> Mitigation: keep inspect/status contracts compatibility-aware.
- [Risk] The change can sprawl into a full runtime rewrite. -> Mitigation: keep scope centered on live execution identity, phase mapping, and compatibility projections.
- [Risk] It may overclaim official parity too early. -> Mitigation: describe the result as a live compiled-execution step rather than full LangGraph parity.

## Validation Plan

1. Add proposal, design, and delta specs for the live compiled execution path.
2. Extend the LangGraph contract layer with live-execution identity and runtime posture.
3. Map the seven-phase shell into an actual compiled graph execution branch while preserving repo-local artifacts.
4. Extend user-level helper surfaces and canonical durable-state projection with live-execution posture.
5. Validate live compiled execution posture without regressing the current operator model.
