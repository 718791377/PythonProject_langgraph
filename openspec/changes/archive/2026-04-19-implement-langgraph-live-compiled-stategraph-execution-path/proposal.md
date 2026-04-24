## Why

The repository now exposes bounded graph-kernel, primary-runtime, and compiled-invocation surfaces, but those layers still stop at posture and compatibility reporting. The next real LangGraph runtime gap is a live compiled execution path that drives durable behavior through an actually executed compiled graph branch rather than only surfacing what such a path would look like.

## What Changes

- Introduce a live compiled `StateGraph` execution path for the user-level LangGraph durable lane.
- Define how the current seven-phase shell and durable artifacts are driven by an actual compiled graph branch instead of only by projected invocation posture.
- Preserve repo-local durable artifacts and operator-facing inspect surfaces while making live compiled execution a first-class runtime lane.
- Keep the rollout additive and compatibility-aware instead of replacing the existing user-level operator model in one unsafe rewrite.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-live-compiled-stategraph-execution-path`: a live compiled `StateGraph` execution path for the user-level LangGraph lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: move from bounded compiled-invocation posture toward an actual live compiled execution path
- `codex-user-level-inspectable-team-state-surface`: expose live compiled-execution posture while preserving the canonical summary contract
- `codex-user-level-team-mode-team-entrypoints`: expose additive user-level entrypoints and playbook guidance for the live compiled-execution lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/langgraph_durable_orchestrator/runtime.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime and execution metadata
  - LangGraph inspect/status/helper projections
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace native Codex as leader
  - this change does not replace `native_omx` as the stable worker-centric default backend
  - this change does not require full parity with every official LangGraph feature in one rollout
  - this change does not introduce cloud-only orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and delta specs for the live compiled execution path
  2. extend the Python-side LangGraph contract layer with live-execution identity and runtime posture
  3. map the current seven-phase shell into an actual compiled graph execution branch while preserving repo-local artifacts
  4. extend user-level helper surfaces and canonical durable-state projection with live-execution posture
  5. validate live compiled execution posture without regressing the current operator surfaces
- rollback_plan:
  - revert only the live-execution contracts, runtime state, and helper-surface updates introduced by this change
  - keep the already-implemented subgraphs, command flow, streaming, runtime/store, memory, migration, multi-interrupt, replay/recovery, graph-kernel, primary-runtime, and compiled-invocation surfaces intact
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for live compiled execution posture and compatibility with current durable artifacts
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
