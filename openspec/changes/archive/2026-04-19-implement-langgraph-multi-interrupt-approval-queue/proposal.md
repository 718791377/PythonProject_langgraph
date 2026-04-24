## Why

The user-level LangGraph durable lane now supports repo-local threads, checkpoints, replay and recovery controls, reusable subgraphs, command-driven handoffs, streaming observability, runtime/store injection, memory posture, and graph-migration compatibility posture. What it still lacks is an explicit multi-interrupt approval queue aligned with the official LangGraph interrupts model.

This gap matters because the current lane still collapses operator approval state into a single interrupt record. That is too weak once one invocation can surface multiple pending approvals or multiple resumable interrupt values. Without an explicit queue, the lane can over-collapse approval posture, lose ordering, or blur which pending approval a later resume is meant to satisfy.

Official LangGraph explicitly supports multiple interrupts in one invocation. The local lane should expose the same operator truth at the durable-state and helper-surface level.

## What Changes

- Add a first-class multi-interrupt approval queue for the user-level LangGraph durable lane.
- Define additive queue posture for multiple pending interrupts within one tracked thread.
- Persist interrupt-queue identity, ordering, approval status, and bounded resume-mapping posture in repo-local LangGraph durable state.
- Expose multi-interrupt approval posture through the canonical inspectable durable-state surface and generated user-level helper surfaces.
- Keep the first rollout inspection-first and operator-explicit rather than silently collapsing multiple pending approvals into one generic interrupt state.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-multi-interrupt-approval-queue`: multi-interrupt approval-queue contracts for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add multi-interrupt queue and resume-mapping semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: project interrupt-queue posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive approval-queue inspection entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` interrupt and thread metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not redesign replay, recovery, reducer, subgraph, command-driven, streaming, runtime/store, memory, or migration semantics beyond approval-queue-aware integration points
  - this change does not introduce automatic approval decisions or silent interrupt collapsing
  - this change does not introduce cloud-only interrupt orchestration infrastructure
- rollout_sequence:
  1. define proposal, design, and spec deltas for multi-interrupt approval queues
  2. extend the Python-side LangGraph contract layer with interrupt-queue and resume-mapping metadata
  3. persist bounded interrupt-queue posture through tracked thread and backend projection state
  4. expose approval-queue inspection through existing tooling and generated helper surfaces
  5. validate ordered queue inspection and explicit resume mapping without silent queue collapse
- rollback_plan:
  - revert only the multi-interrupt queue contracts, projections, and helper-surface updates introduced by this change
  - keep graph-migration, memory, runtime/store, command-driven, streaming, replay/recovery, and reusable subgraph behaviors intact
  - if queue posture proves too noisy, keep backend-local queue persistence while disabling user-level projection fields
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for multi-interrupt queue and resume-mapping posture
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
