## Context

The current user-level LangGraph lane now exposes a layered runtime direction: graph-kernel posture, primary-runtime engine posture, compiled-invocation posture, and bounded live-execution posture. Those layers make the runtime progressively more concrete.

What still remains narrow is the live graph itself. The current live execution path is intentionally bounded to a small fixed branch. The next runtime gap is therefore not “more live execution” in the abstract; it is broader graph-native routing and loop execution that still preserves the stable seven-phase shell seen by the operator.

## Goals / Non-Goals

**Goals:**

- define a more generalized live `StateGraph` routing model for the user-level LangGraph lane
- map the current seven-phase shell into richer graph-native routing and loop posture
- preserve repo-local artifacts and inspectable operator surfaces while widening the live graph branch
- keep the rollout additive and compatibility-aware

**Non-Goals:**

- replacing native Codex as leader
- replacing `native_omx` as the worker-centric default backend
- forcing full parity with every official LangGraph feature in one monolithic rewrite
- introducing cloud-only orchestration infrastructure

## Decisions

### Decision 1: The next runtime step should widen the live graph rather than add another metadata layer

The repository already has multiple runtime posture layers. The next valuable step is to widen actual graph-native routing behavior.

### Decision 2: The seven-phase shell remains the stable external contract

The richer live routing model should continue to drive the existing seven-phase shell rather than replacing the operator-facing phase contract.

### Decision 3: Existing durable artifacts remain compatibility anchors

Thread ids, checkpoints, interrupts, implementation briefs, survivor queues, and inspectable summaries remain compatibility anchors during the generalized-routing rollout.

### Decision 4: Keep the scope bounded to generalized routing and loop posture

This change should focus on richer routing and loop execution inside the live graph. Broader automation or later runtime generalization can remain future work.

## Risks / Trade-offs

- [Risk] Broader live routing can destabilize helper surfaces that assume narrow branches. -> Mitigation: keep inspect/status contracts compatibility-aware.
- [Risk] The change can sprawl into a full runtime rewrite. -> Mitigation: keep scope centered on generalized routing, loop posture, and compatibility projections.
- [Risk] It may overclaim official parity too early. -> Mitigation: describe the result as a generalized live-routing step rather than full LangGraph parity.

## Validation Plan

1. Add proposal, design, and delta specs for generalized live routing.
2. Extend the LangGraph contract layer with generalized routing identity and loop posture.
3. Map the seven-phase shell into a richer live graph branch while preserving repo-local artifacts.
4. Extend user-level helper surfaces and canonical durable-state projection with generalized live-routing posture.
5. Validate generalized live-routing posture without regressing the current operator model.
