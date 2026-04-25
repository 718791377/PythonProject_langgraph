## Why

The repository has now closed the subgraph-aware live primary-engine handoff-state mainline and the follow-up capability-gap sync pass. The most concrete remaining runtime gap is no longer subgraph-aware handoff posture; it is approval-aware resume state inside the live primary engine itself.

The current live-engine line now carries next-hop decisions, graph-resident boundary posture, and subgraph-aware handoff semantics in graph-native state. But approval-queue identity, resolved-versus-pending queue posture, and resume-mapping semantics are still primarily projected from adjacent approval surfaces rather than being carried as first-class live-engine state.

The next justified mainline is therefore an approval-aware live primary-engine resume-state step that moves more approval-queue and resume-mapping semantics into the live-engine state itself while preserving the seven-phase shell and the current durable artifacts.

## What Changes

- deepen the current live primary-engine beyond subgraph-aware handoff state into approval-aware resume state
- preserve the seven-phase operator shell, durable artifacts, and current inspectable control surfaces during the rollout
- keep the result additive to the current Codex leader model and existing LangGraph runtime layers

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-approval-aware-live-primary-engine-resume-state`: approval-aware live primary-engine resume-state semantics for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: deepen the live primary-engine beyond the current subgraph-aware handoff-state posture into approval-aware resume handling
- `codex-user-level-inspectable-team-state-surface`: expose approval-aware live-engine resume posture without breaking the canonical durable-state summary
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the approval-aware resume-state lane

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
  - this change does not reopen automatic-policy or subgraph-expansion work in the same mainline
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for approval-aware live-engine resume posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
