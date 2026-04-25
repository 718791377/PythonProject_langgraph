## Why

The repository has now closed the current bounded runtime layers, generalized live routing, subgraph persistence or state inspection, and the fuller live primary-execution-engine step. After the latest capability-gap sync pass, the most concrete remaining runtime gap is no longer execution structure. It is richer automatic runtime policy.

The current LangGraph lane is still inspection-first and manual-first. That is safe, but it leaves two recurring policy gaps explicitly called out by the implementation plan:

- automatic migration handling
- automatic approval or queue-resolution behavior where bounded policy is safe

The next justified mainline is therefore a bounded automatic-runtime-policy layer that remains compatibility-aware and operator-visible rather than silent or over-automated.

## What Changes

- Introduce bounded richer automatic runtime policies for the user-level LangGraph lane.
- Add explicit automatic-policy posture for migration handling and approval or queue-resolution behavior.
- Keep the rollout additive, inspectable, and manual-first by default.
- Preserve the current Codex leader model, seven-phase shell, and cross-backend summary contract.

## Capabilities

### New Capabilities

- `codex-user-level-langgraph-richer-automatic-runtime-policies`: bounded automatic runtime-policy posture for the user-level LangGraph lane

### Modified Capabilities

- `langgraph-durable-orchestration-backend`: add bounded automatic-policy posture for migration and approval handling
- `codex-user-level-inspectable-team-state-surface`: expose automatic runtime-policy posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive inspection helpers for the automatic runtime-policy lane

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime-policy projection data
  - LangGraph Python tests and install-surface integration tests
- explicit_non_goals:
  - this change does not replace manual-first operator control
  - this change does not silently auto-switch backend family
  - this change does not redesign the Codex CLI leader model
  - this change does not land unbounded autonomous policy behavior
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for automatic runtime-policy posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
