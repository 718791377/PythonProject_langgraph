## Why

The repository now exposes a bounded graph-kernel layer and a bounded primary-runtime engine posture for the user-level LangGraph lane, but the runtime still does not treat a compiled graph invocation path as the primary execution surface. The next meaningful LangGraph gap is therefore not another projection layer, but a real compiled `StateGraph` invocation path that can serve as the live execution core for the existing seven-phase shell.

## What Changes

- Introduce a compiled `StateGraph` invocation path for the user-level LangGraph durable lane.
- Define how the current seven-phase shell, kernel posture, and primary-runtime engine posture map into a live compiled graph execution path.
- Preserve repo-local durable artifacts and existing inspect surfaces while making compiled invocation and graph-native streaming a first-class execution path.
- Keep the rollout additive and compatibility-aware instead of replacing the existing user-level operator model in one unsafe rewrite.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-compiled-stategraph-invocation-path`: a live compiled `StateGraph` invocation path for the user-level LangGraph lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: move from bounded primary-runtime engine posture toward an actual compiled graph invocation path
- `codex-user-level-inspectable-team-state-surface`: expose compiled invocation posture while preserving the canonical summary contract
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level entrypoints and playbook guidance for the compiled invocation lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/langgraph_durable_orchestrator/runtime.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime and compiled-execution metadata
  - LangGraph inspect/status/helper projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace native Codex as leader
  - this change does not replace `native_omx` as the stable worker-centric default backend
  - this change does not require full parity with every official LangGraph feature in one rollout
  - this change does not introduce cloud-only orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and delta specs for the compiled invocation path
  2. extend the Python-side LangGraph contract layer with compiled invocation identity and execution posture
  3. map the current seven-phase shell into a live compiled graph path while preserving repo-local artifacts
  4. extend user-level helper surfaces and canonical durable-state projection with compiled invocation posture
  5. validate compiled invocation posture without regressing the current operator surfaces
- rollback_plan:
  - revert only the compiled-invocation contracts, runtime state, and helper-surface updates introduced by this change
  - keep the already-implemented subgraphs, command flow, streaming, runtime/store, memory, migration, multi-interrupt, replay/recovery, graph-kernel, and bounded primary-runtime engine surfaces intact
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for compiled invocation posture and compatibility with current durable artifacts
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
