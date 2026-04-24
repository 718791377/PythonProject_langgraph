## Why

The bounded graph-kernel rollout is now implemented and validated, but the current lane still centers execution around a projection-first durable shell that reports `StateGraph` posture rather than making a compiled graph-native engine the primary execution path. The next meaningful LangGraph gap is therefore not another additive surface, but a deeper primary-runtime engine that turns the current kernel model into real graph-driven execution.

## What Changes

- Introduce a primary-runtime `StateGraph` execution engine for the user-level LangGraph durable lane.
- Define how the current seven-phase shell, subgraphs, interrupts, replay/recovery, and durable artifacts map into compiled graph execution rather than shell-first orchestration.
- Preserve repo-local durable artifacts and existing operator-facing inspect surfaces through compatibility-aware projections while shifting runtime execution toward graph-native invocation.
- Keep the rollout additive and bounded instead of replacing the existing user-level operator model in one unsafe rewrite.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-primary-runtime-stategraph-engine`: a compiled `StateGraph`-first primary-runtime engine for the user-level LangGraph lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: move from bounded graph-kernel projection toward a primary-runtime `StateGraph` execution engine
- `codex-user-level-inspectable-team-state-surface`: expose primary-runtime engine posture while preserving the canonical summary contract
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level entrypoints and playbook guidance for the primary-runtime engine lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/langgraph_durable_orchestrator/runtime.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime state and execution metadata
  - LangGraph inspect/status/helper projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace native Codex as leader
  - this change does not replace `native_omx` as the stable worker-centric default backend
  - this change does not require full parity with every official LangGraph feature in one rollout
  - this change does not introduce cloud-only orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and delta specs for the primary-runtime engine
  2. extend the Python-side LangGraph contract layer with primary-runtime engine identity and compiled graph execution posture
  3. map the seven-phase durable shell into compiled graph-native invocation while preserving repo-local artifacts
  4. extend user-level helper surfaces and canonical durable-state projection with primary-runtime engine posture
  5. validate engine-centric execution posture without regressing current operator surfaces
- rollback_plan:
  - revert only the primary-runtime engine contracts, runtime state, and helper-surface updates introduced by this change
  - keep the already-implemented subgraphs, command flow, streaming, runtime/store, memory, migration, multi-interrupt, replay/recovery, and bounded graph-kernel surfaces intact
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for primary-runtime engine posture and compatibility with current durable artifacts
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
