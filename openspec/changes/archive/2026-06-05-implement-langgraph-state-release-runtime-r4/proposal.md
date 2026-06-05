# Change: Implement LangGraph State Release Runtime R4

## Why

The Stage C checker work can reject stale `running` LangGraph state after completed work, but the runtime still needs a concrete close, release, and handoff helper that writes repo-local evidence. Without that helper, operators must rely on manual state edits or chat-only notes to prove that a completed LangGraph thread is no longer active.

## What Changes

- Add a repo-local LangGraph release helper command that closes, releases, or hands off a tracked thread.
- Persist a structured release receipt under `.omx/state/langgraph/store/releases/`.
- Update thread state and backend projections so completed work no longer reports `running`.
- Add runtime tests for close, release, handoff, receipt fields, and inspect/status projections.
- Update the active implementation plan status for Stage D/R4.

## Impact

- Affects `tools/langgraph_durable_orchestrator/` runtime and CLI surfaces.
- Adds Python regression coverage through the existing CI-managed state-release test module.
- Promotes a reusable release-runtime requirement into the LangGraph durable backend spec during archive.
- Remote publication remains outside this change unless explicitly authorized.
