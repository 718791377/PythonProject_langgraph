## Why

The repository has now closed the broader automatic runtime-policy wave and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer automatic policy; it is the live primary engine itself.

The current `deeper-engine` lane can project multi-step phase and node paths, stop boundaries, and recursion-limit-aware posture. But its compiled graph path is still intentionally bounded: the engine preview computes the path first, while the compiled graph layer remains a single passthrough node instead of a superstep-aware multi-node `StateGraph` execution lane.

The next justified mainline is therefore a new additive live-engine layer that preserves the seven-phase shell while exposing superstep-aware live primary-engine posture through a compiled multi-node graph path.

## What Changes

- add a new superstep-aware live primary-engine lane on top of the existing fuller and deeper live-engine layers
- keep the rollout additive, inspectable, and compatible with the current seven-phase operator shell
- preserve the existing durable artifacts, automatic-policy layer, routing layer, and current leader model

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-superstep-live-primary-engine`: superstep-aware live primary-engine semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: expose an additive superstep-aware live primary-engine lane beyond the current deeper projected-path posture
- `codex-user-level-inspectable-team-state-surface`: expose superstep live-engine posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the superstep live-engine lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` live-engine projection data
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace the current Codex CLI leader model
  - this change does not replace `native_omx` as the worker-centric default backend
  - this change does not claim a fully generalized LangGraph-native runtime in one pass
  - this change does not reopen broader automatic-policy work in the same mainline
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for superstep live-engine posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
