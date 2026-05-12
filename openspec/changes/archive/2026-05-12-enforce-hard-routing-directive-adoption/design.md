# Design

## Scope
This is a static policy-enforcement slice for hard routing directive adoption semantics.

## Enforcement approach
`tools/check_orchestration_activation_policy.py` remains the script-backed guard for the orchestration activation boundary. This slice requires active policy and stable spec surfaces to include stable text for:

- explicit `omx` / `LangGraph` directives as hard routing directives;
- `selected` / `running` adoption when capability chain, preflight, and thresholds are satisfied;
- named blockers or unmet thresholds when the requested lane is not adopted;
- no explanation-only mode when adoption conditions are satisfied.

## Non-goals
- No runtime launcher implementation.
- No writes to `.omx/state`.
- No live durable-team smoke test.
