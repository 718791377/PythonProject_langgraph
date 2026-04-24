## Why

The user-level LangGraph durable lane already has additive backend selection, repo-local durable state, reusable subgraph contracts, command-driven handoffs, and streaming or debug observability. What it still lacks is a first-class runtime-context and store-injection contract aligned with official LangGraph `context_schema`, `Runtime.context`, and `Runtime.store`.

This gap matters now because the current lane still treats most durable behavior as state-file and helper-surface oriented. Without an explicit runtime injection contract, the operator and implementation layer cannot clearly distinguish static invocation context, mutable graph state, and injected store access, which makes later memory and dependency-injection work harder than it needs to be.

## What Changes

- Add a first-class user-level runtime-context and store-injection contract for the LangGraph durable lane.
- Define additive support for `context_schema`-style runtime context and bounded `Runtime.context` projection.
- Define additive support for injected `Runtime.store` presence and store-capability posture without yet introducing semantic-memory policy.
- Persist runtime-injection posture and store-availability metadata in repo-local LangGraph durable state.
- Expose runtime-context and store-injection posture through the canonical inspectable durable-state surface and generated user-level helper surfaces.

## Capabilities

### New Capabilities
- `codex-user-level-langgraph-runtime-context-and-store-injection`: runtime context and store-injection contracts for the user-level LangGraph durable lane

### Modified Capabilities
- `langgraph-durable-orchestration-backend`: add runtime-context, injected-store, and context-schema semantics for tracked LangGraph threads
- `codex-user-level-inspectable-team-state-surface`: project runtime-context and store-injection posture for tracked LangGraph threads
- `codex-user-level-team-mode-team-entrypoints`: expose additive runtime-context or store-inspection entrypoints and playbook guidance

## Impact

- impact_scope:
  - `tools/langgraph_durable_orchestrator/contracts.py`
  - `tools/langgraph_durable_orchestrator/cli.py`
  - `tools/install-codex-user-level-team-mode.ps1`
  - repo-local `.omx/state/langgraph/` runtime-injection metadata
  - LangGraph durable-state inspection and helper-pointer projections
  - LangGraph durable-team tests and install-surface integration tests
- explicit_non_goals:
  - this change does not change backend-selection policy
  - this change does not replace `native_omx` as the stable worker-centric default durable backend
  - this change does not introduce semantic-memory policy, embedding pipelines, or long-term memory retrieval behavior
  - this change does not redesign replay, recovery, reducer, command-driven, or streaming semantics beyond runtime-injection integration points
  - this change does not introduce cloud-only runtime configuration infrastructure
- rollout_sequence:
  1. define proposal, design, and spec deltas for runtime context and store injection
  2. extend the Python-side LangGraph contract layer with context-schema and store-injection metadata
  3. persist runtime-injection posture through tracked thread and backend projection state
  4. expose runtime-context and store-injection inspection through existing tooling and generated helper surfaces
  5. validate bounded runtime-context metadata and injected-store posture without reopening semantic-memory scope
- rollback_plan:
  - revert only the runtime-context and store-injection contracts, projections, and helper-surface updates introduced by this change
  - keep the existing root graph, reusable subgraph library, command-driven control flow, streaming surfaces, replay or recovery controls, and reducer semantics intact
  - if injected-store posture proves confusing, keep backend-local metadata while disabling the user-level projection fields
- validation_path:
  - `python -m compileall D:\\PythonProject_langgraph\\tools\\langgraph_durable_orchestrator`
  - targeted Python tests for runtime-context and store-injection projection
  - `cmd /d /s /c test\\run-install-codex-user-level-team-mode-test.cmd`
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - existing Codex persistent agent-team mainline continuation
