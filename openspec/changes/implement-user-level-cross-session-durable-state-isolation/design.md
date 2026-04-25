## Context

The current user-level orchestration line already distinguishes:

- startup-loaded policy and developer instructions
- user-level installed helper surfaces under `C:\Users\lenovo\.codex\bin`
- repo-local durable artifacts under `.omx/state`
- live session or thread context

The bottleneck is that legacy repo-local durable artifacts still act too much like activation truth.

Two concrete failures are already visible:

1. A preserved LangGraph `backend.json` can dominate automatic durable routing for a later unrelated session even when the operator only meant to preserve that thread for inspection or explicit resume.
2. Empty unmanaged native `auto-team-*` directories can still force `manual-inspection-required` even though they contain no recoverable team state.

The fix must not mutate, rename, or delete existing legacy artifacts in either `D:\PythonProject_OpenClaw` or `D:\PythonProject_langgraph`.

References to `D:\PythonProject_OpenClaw` in this design describe legacy artifact preservation and migration-safety scope only. They do not make the old repository an active implementation authority for the current orchestration line.

## Goals / Non-Goals

**Goals:**

- separate activation truth from legacy durable artifacts
- keep legacy durable artifacts readable and inspectable
- make future durable activation session-scoped rather than inferred only from repo-local historical files
- stop empty unmanaged native residue from blocking automatic routing
- preserve existing orchestration-retrofit rules for existing live sessions

**Non-Goals:**

- rewriting or rekeying legacy LangGraph thread artifacts
- deleting legacy native team directories as part of the first implementation step
- changing global capability-switch semantics
- collapsing `native_omx` and `langgraph` into one backend family
- introducing a new operator-facing requirement to manually migrate old sessions before new sessions can use updated helpers

## Decisions

### Decision 1: Split durable control into artifact, activation, and inspection planes

Legacy files under `.omx/state/langgraph/*` and `.omx/state/team/*` remain the artifact plane.

They preserve historical and active durable evidence, but they no longer implicitly declare which durable record is active for future sessions.

Add a new activation plane for scoped selectors or leases. This becomes the only source of activation truth for new durable decisions.

Keep legacy `backend.json` and tracked native-team record behavior in the inspection plane, where they remain inspectable and source-attributed.

Alternative considered:

- continue using `backend.json` and latest team directory as implicit activation selectors

Rejected because:

- it keeps historical artifact preservation coupled to future-session activation
- it recreates the same cross-session interference we are trying to remove

### Decision 2: Keep rollout additive with dual-read and scoped-write

New logic reads both:

- legacy artifact state for inspection and compatibility
- scoped activation state for future durable routing decisions

New writes go only to the scoped activation plane.

Alternative considered:

- migrate legacy artifact files in place

Rejected because:

- it risks altering active or historical sessions
- it turns a routing fix into a destructive migration

### Decision 3: Treat empty unmanaged native residue as cleanup context, not active blocker state

Automatic routing should inspect native team directory metadata and ignore unmanaged directories that are empty.

Only non-empty unmanaged native residue remains a blocker that forces `manual-inspection-required`.

Alternative considered:

- continue treating any latest unmanaged team directory as blocking residue

Rejected because:

- it makes safe empty residue operationally equivalent to meaningful recovery state
- it contradicts the current cleanup classification contract

### Decision 4: Add explicit LangGraph routing eligibility projection

LangGraph backend records need an explicit routing-eligibility signal, such as `auto_route_eligible` or a richer `routing_posture`.

Future durable lane selection must use that signal instead of raw `exists && thread_id`.

Alternative considered:

- infer eligibility only from `thread_id` plus file presence

Rejected because:

- historical records and active records become indistinguishable for future routing
- it preserves the current accidental auto-resume or auto-dominance behavior

### Decision 5: Keep active-session retrofit semantics unchanged

Existing live sessions remain retrofit-capable on:

- reload
- restart
- explicit user routing directive
- tracked durable-state detection

This implementation should not narrow that policy.

## Risks / Trade-offs

- [Risk] The scoped activation plane may drift from legacy artifact summaries.
  Mitigation: keep inspectable status source-attributed and expose both activation-plane and artifact-plane evidence.

- [Risk] Some existing helper scripts may still assume legacy implicit activation.
  Mitigation: update the shared source logic first, then regenerate mirrored user-level helpers in lockstep.

- [Risk] Operators may misread preserved legacy artifacts as broken active state.
  Mitigation: add explicit state classification for legacy preserved versus active scoped activation.

- [Risk] The change may appear to delay cleanup because empty residue is not deleted immediately.
  Mitigation: keep cleanup preview/apply as a later optional maintenance step after routing behavior is safe.

## Migration Plan

1. Implement scoped activation logic in `D:\PythonProject_langgraph` source first.
2. Add LangGraph routing-eligibility projection and native empty-residue filtering in source logic.
3. Add tests that cover:
   - preserved legacy LangGraph records
   - active scoped selectors
   - empty unmanaged native residue
   - non-empty unmanaged native residue
4. Refresh mirrored user-level helper scripts only after source and tests pass.
5. Leave legacy repo-local artifacts untouched.
6. Optionally clean empty unmanaged native residue later through the existing preview-first reconciliation path.

Rollback:

- revert source and generated-helper changes
- keep legacy durable artifacts intact
- fall back to current legacy implicit activation if scoped activation proves unsafe

## Open Questions

- Whether the first scoped activation plane should use a single `active.json`, per-session lease records, or both from the first rollout
- Whether terminal LangGraph thread posture should be encoded as a boolean eligibility flag or a richer routing-posture enum
- Whether the inspectable state surface should expose both legacy and scoped identifiers in one shared summary row or a nested compatibility section
