# Design

## Scope
This is a static policy-enforcement slice. It does not implement runtime agent orchestration or durable-team launching.

## Enforcement approach
`tools/check_orchestration_activation_policy.py` remains the script-backed guard for this user-level boundary. The checker will require explicit durable-team threshold wording on the active governance and stable spec surfaces.

## Non-goals
- No changes to `omx-team-auto.ps1` runtime behavior.
- No writes to `.omx/state`.
- No live durable-team smoke test.
