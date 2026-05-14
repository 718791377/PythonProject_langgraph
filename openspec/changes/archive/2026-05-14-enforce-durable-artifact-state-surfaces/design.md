# Design: Durable artifact state-surface enforcement

## Context

The implementation plan distinguishes read-only exploration from code-changing workers, LangGraph graph/checkpoint state from compatibility records, and durable artifacts from transient chat context. These boundaries need script-backed regression coverage just like activation traces and delegation wait discipline.

## Decisions

1. Add `tools/check_durable_artifact_state_surfaces.py` with two modes:
   - repository mode checks policy surfaces, guard wiring, and safety registry wiring;
   - evidence mode checks saved run summaries, worker briefs, or durable handoff notes.
2. Treat evidence as text-first so it can validate Markdown summaries, JSON summaries, or copied worker briefs without introducing a new schema dependency.
3. Fail closed for these regressions:
   - exploration is not specific/well-scoped/read-only;
   - exploration replaces a clear bounded code-changing worker task;
   - graph/checkpoint work lacks LangGraph entrypoint naming or repo-local `.omx/state/langgraph/` state;
   - automatic durable-team adoption relies on compatibility records without `.omx/state/selectors/active.json`;
   - durable artifacts, frozen briefs, or survivor queues exist only in transient chat context;
   - research handoff lacks frozen brief fields;
   - bug triad roles become persistent workers instead of persisting survivors for debugger-lane follow-up.
4. Wire the checker into local gate through the existing OpenSpec guard and local Python manifest.

## Risks

- The evidence checker uses marker-based text validation and can be conservative. Mitigation: repository mode is strict; evidence mode warns when no relevant markers exist and only fails after relevant markers appear.
- There is overlap with the delegation/wait checker. Mitigation: this checker owns durable artifact and state-surface evidence, while the previous checker owns critical-path delegation/wait discipline.

## Rollback

Revert the checker, test, guard/registry/manifest wiring, and policy/spec text updates. The implementation plan remains as historical context.
