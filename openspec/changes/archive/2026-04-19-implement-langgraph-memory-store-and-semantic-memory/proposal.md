## Why

The user-level LangGraph durable lane already has additive backend selection, repo-local durable state, reusable subgraph contracts, command-driven handoffs, streaming observability, and bounded runtime/store injection posture. What it still lacks is a first-class memory-store and semantic-memory contract aligned with the official LangGraph memory and semantic search model.

This gap matters now because the current lane can inject store posture, but it still does not define durable long-term memory behavior. Without an explicit memory-store contract, later graph work cannot reliably distinguish injected store availability from actual durable memory, retrieval, and semantic lookup semantics.

## What Changes

- Add a first-class user-level memory-store and semantic-memory contract for the LangGraph durable lane.
- Define additive support for durable memory-store presence and bounded long-term memory posture.
- Define additive support for semantic-memory lookup posture and bounded semantic search metadata without forcing one provider implementation.
- Persist memory-store and semantic-memory posture in repo-local LangGraph durable state.
- Expose memory-store and semantic-memory posture through the canonical inspectable durable-state surface and generated user-level helper surfaces.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-memory-store-and-semantic-memory`: memory-store and semantic-memory contracts for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add durable memory-store, semantic lookup, and long-term memory posture semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: project memory-store and semantic-memory posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive memory/store inspection entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` memory and semantic-store metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not force one embedding provider, vector database, or semantic-search backend
  - this change does not redesign replay, recovery, reducer, command-driven, streaming, or runtime-injection semantics beyond memory-aware integration points
  - this change does not introduce cloud-only memory infrastructure
- rollout_sequence:
  1. define proposal, design, and spec deltas for memory-store and semantic-memory support
  2. extend the Python-side LangGraph contract layer with memory-store and semantic-memory metadata
  3. persist bounded memory-store and semantic-search posture through tracked thread and backend projection state
  4. expose memory/store inspection through existing tooling and generated helper surfaces
  5. validate bounded memory metadata and semantic-search posture without forcing one provider implementation
- rollback_plan:
  - revert only the memory-store and semantic-memory contracts, projections, and helper-surface updates introduced by this change
  - keep the existing root graph, reusable subgraph library, command-driven control flow, streaming surfaces, runtime/store injection, replay or recovery controls, and reducer semantics intact
  - if semantic-memory posture proves too premature, keep durable memory-store posture while disabling semantic-search projection fields
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for memory-store and semantic-memory projection
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
