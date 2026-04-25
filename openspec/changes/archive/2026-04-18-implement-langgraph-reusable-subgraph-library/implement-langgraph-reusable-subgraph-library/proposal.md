## Why

The current Codex durable-team line already has a LangGraph-backed root graph, bounded quality-gated loops, reducer-aware fan-in, and replay or recovery controls, but its "subgraphs" are still only a shallow role-name map. That is not yet a reusable persistent agent-team library, so the durable team still lacks stable subgraph contracts for research, planning, execution, verification, and adversarial review.

This change is needed now because the Codex persistent agent-team mainline should advance through reusable subgraph contracts instead of accumulating ad hoc role bundles inside one CLI file. The missing subgraph library is now the clearest remaining gap in the user-level LangGraph durable lane.

## What Changes

- Add a reusable LangGraph subgraph library for the user-level Codex durable-team line.
- Define stable subgraph identities and contracts for `research`, `planning`, `execution`, `verification`, and `adversarial-review`.
- Persist active-subgraph identity and subgraph-aware handoff metadata in repo-local LangGraph durable state.
- Expose subgraph-library inspection through the existing user-level LangGraph tooling and generated entrypoints.
- Keep the design additive: Codex CLI remains leader, oh-my-codex remains the workflow layer, and LangGraph remains the selected durable backend for graph-first flows.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-reusable-subgraph-library`: reusable, inspectable LangGraph subgraph contracts for the user-level Codex persistent agent-team lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: route the durable backend through reusable subgraph contracts instead of a shallow role-family map
- `codex-user-level-inspectable-team-state-surface`: project active-subgraph and subgraph-library inspection data for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive LangGraph subgraph-library inspection entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - user-level generated LangGraph entrypoints and inspect surfaces
  - repo-local `.omx/state/langgraph/` thread metadata
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not introduce cloud-only LangGraph deployment infrastructure
  - this change does not make every specialist role a default persistent worker
  - this change does not reopen replay, recovery, or reducer semantics except where subgraph contracts reference them
- rollout_sequence:
  1. define proposal, design, and spec deltas for reusable subgraph contracts
  2. implement the Python-side subgraph library and active-subgraph projection
  3. expose user-level inspection and generated entrypoint support
  4. validate repo-local durability, inspectability, and handoff boundaries
- rollback_plan:
  - revert only the reusable-subgraph-library contracts, entrypoints, and projections introduced by this change
  - keep the existing LangGraph root graph, loops, reducer semantics, and replay or recovery controls intact
  - if subgraph-aware projection proves confusing, keep the root graph while disabling the new library-specific helper surface
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for reusable subgraph contracts and active-subgraph inspection
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
