# Change: Enforce hard routing directive adoption wording

## Why
The active automatic orchestration plan requires explicit `omx` and `LangGraph` requests to be treated as hard routing directives. If capability chain, preflight, and task thresholds are satisfied, the session must actually adopt the selected lane instead of staying in explanation-only mode. Existing policy text mentions hard routing directives, but the checker does not yet require stable wording for directive adoption, named blockers, or explanation-only prevention.

## What Changes
- Strengthen governance/spec surfaces for hard routing directive adoption and named blockers.
- Extend `tools/check_orchestration_activation_policy.py` required snippets.
- Add regression coverage proving missing directive adoption wording fails.

## Impact
- Static policy/checker enforcement only.
- Does not launch experts, durable workflows, or persistent teams.
- Does not mutate `.omx/state`.
