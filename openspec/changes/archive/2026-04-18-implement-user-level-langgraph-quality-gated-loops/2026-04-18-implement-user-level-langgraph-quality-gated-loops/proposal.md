## Why

The current user-level LangGraph lane is real and usable, but it still stops short of a fully realized LangGraph-native orchestration runtime. The main remaining gap is not backend selection, capability switches, installation surfaces, or activation policy. Those are already covered by existing user-level changes. The missing step is graph-native execution behavior inside the LangGraph lane itself: conditional routing, iterative quality-gated loops, and loop-state visibility that allow the durable graph to keep working until acceptance criteria are met.

This change closes that gap for user-level `Codex CLI + oh-my-codex` team mode without replacing the current leader model, without changing default backend policy, and without duplicating already implemented routing-threshold or backend-selector work.

## What Changes

- Add graph-native conditional routing inside the LangGraph backend rather than relying only on wrapper-side lane choice.
- Add bounded quality-gated execution loops such as `draft -> review -> revise -> review -> accept` and `execute -> verify -> revise -> execute`.
- Persist loop budget, iteration count, last gate verdict, and stop reason in repo-local LangGraph state.
- Project loop-state and gate-state into the canonical inspectable durable-state surface.
- Keep `Codex CLI` as leader, keep LangGraph additive, and keep `native_omx` fallback behavior unchanged.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-quality-gated-loops`: user-level LangGraph graph-native conditional routing and bounded quality-gated loop semantics

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: extend the LangGraph backend contract from durable phase persistence into graph-native routing and iterative loop execution
- `codex-user-level-inspectable-team-state-surface`: expose normalized LangGraph loop and gate progress for tracked threads without changing the shared cross-backend summary contract

## Impact

- impact_scope:
  - repo-local LangGraph runtime state under `.omx/state/langgraph/`
  - user-level inspect and status surfaces for tracked LangGraph threads
  - LangGraph execution semantics inside the selected durable backend family
- explicit_non_goals:
  - no new backend-family selector work
  - no new capability-switch or enable/disable control work
  - no change to default backend preference policy
  - no replacement of `native_omx`
  - no introduction of reducer, replay, or reusable-subgraph scope unless directly required by loop delivery
- rollout_sequence:
  - define proposal, design, and spec contracts for graph-native quality-gated loops
  - add loop-state persistence and gate-verdict contracts inside the LangGraph backend
  - add inspectable projection for loop progress and stop reasons
  - validate one review loop, one execution loop, and one operator-interrupt path
- rollback_plan:
  - keep LangGraph additive and backend-selectable
  - preserve the current non-looping LangGraph execution path as a rollback-safe fallback until graph-native looping is proven stable
  - if graph-native looping fails or remains incomplete, avoid routing tasks into the loop-capable execution path while preserving existing durable-state inspection
- validation_path:
  - run `openspec validate --all`
  - validate graph-native branch transitions from one phase to another based on gate outputs
  - validate at least one `draft -> review -> revise -> review -> accept` loop and one `execute -> verify -> revise -> execute` loop
  - validate loop termination on accept, loop-budget exhaustion, and operator interrupt
  - validate inspectable state shows iteration count, gate verdict, and next step or stop reason
- mainline_classification:
  - existing mainline continuation
  - specifically a user-level LangGraph execution-semantics expansion under the Codex / oh-my-codex team-mode line
