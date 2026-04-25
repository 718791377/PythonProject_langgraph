## Why

The initial LangGraph deepening queue is now implemented and validated, but the current local lane still persists and projects durable orchestration posture through a projection-first Python shell rather than a real `StateGraph`-first runtime kernel. That means the repository has closed many additive capability gaps without yet closing the deeper runtime gap called out in the implementation plan.

## What Changes

- Introduce a first-class `StateGraph`-oriented runtime kernel for the user-level LangGraph durable lane.
- Define how the current seven-phase durable shell maps into graph-native nodes, edges, loop boundaries, and resumable graph state.
- Preserve repo-local durable artifacts and inspectable operator surfaces while moving the runtime center of gravity closer to official LangGraph graph execution.
- Keep the rollout additive and compatibility-aware instead of replacing the existing user-level operator model in one unsafe jump.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-stategraph-runtime-kernel`: a `StateGraph`-first runtime contract for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: change the backend contract from projection-first durable shell posture toward a graph-native `StateGraph` execution kernel
- `codex-user-level-inspectable-team-state-surface`: expose kernel-level graph posture while preserving the existing canonical summary contract
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level entrypoints and playbook guidance for the graph-native kernel lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/langgraph_durable_orchestrator/runtime.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` graph runtime state
  - LangGraph inspect/status/helper projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace native Codex as leader
  - this change does not replace `native_omx` as the stable worker-centric default backend
  - this change does not attempt a cloud-only orchestration rewrite
  - this change does not require every future LangGraph feature to land in the same rollout
- rollout_sequence:
  1. define proposal, design, and delta specs for the `StateGraph` runtime kernel
  2. extend the Python-side LangGraph contract layer with graph-native kernel identity and node or edge posture
  3. map the current seven-phase lane into graph-native runtime state while preserving repo-local artifacts
  4. extend user-level helper surfaces and canonical durable-state projection with kernel-aware posture
  5. validate graph-native execution posture without regressing current operator surfaces
- rollback_plan:
  - revert only the kernel-specific contracts, runtime state, and helper-surface updates introduced by this change
  - keep the already-implemented subgraphs, command flow, streaming, runtime/store, memory, migration, multi-interrupt, and replay/recovery surfaces intact
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for graph-native kernel posture and compatibility with current durable artifacts
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
