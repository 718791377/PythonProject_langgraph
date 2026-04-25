## Why

The repository now exposes bounded graph-kernel, primary-runtime, compiled-invocation, and live-execution layers, but the actual live execution path is still intentionally narrow: it routes into a small fixed set of phase nodes and does not yet generalize broader graph-native routing or loop families. The next meaningful LangGraph gap is therefore a more generalized live `StateGraph` routing model that can execute richer graph-native paths while preserving the current seven-phase operator shell.

## What Changes

- Introduce generalized live `StateGraph` routing for the user-level LangGraph durable lane.
- Define how the current seven-phase shell maps into a richer graph-native routing and loop model rather than a narrowly bounded execution branch.
- Preserve repo-local durable artifacts and current inspect surfaces while widening the live graph execution model.
- Keep the rollout additive and compatibility-aware instead of replacing the user-level operator model in one unsafe rewrite.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-generalized-live-stategraph-routing`: broader live graph-native routing for the user-level LangGraph lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: move from bounded live execution toward a more generalized graph-native routing model
- `codex-user-level-inspectable-team-state-surface`: expose generalized live-routing posture while preserving the canonical summary contract
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level entrypoints and playbook guidance for generalized live-routing inspection

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/langgraph_durable_orchestrator/runtime.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` live-routing metadata
  - LangGraph inspect/status/helper projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace native Codex as leader
  - this change does not replace `native_omx` as the stable worker-centric default backend
  - this change does not require full parity with every official LangGraph feature in one rollout
  - this change does not introduce cloud-only orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and delta specs for generalized live routing
  2. extend the Python-side LangGraph contract layer with generalized routing identity and loop posture
  3. map the seven-phase shell into a richer live graph branch while preserving repo-local artifacts
  4. extend user-level helper surfaces and canonical durable-state projection with generalized live-routing posture
  5. validate generalized live-routing posture without regressing current operator surfaces
- rollback_plan:
  - revert only the generalized live-routing contracts, runtime state, and helper-surface updates introduced by this change
  - keep the already-implemented subgraphs, command flow, streaming, runtime/store, memory, migration, multi-interrupt, replay/recovery, graph-kernel, primary-runtime, compiled-invocation, and bounded live-execution surfaces intact
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for generalized live-routing posture and compatibility with current durable artifacts
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
