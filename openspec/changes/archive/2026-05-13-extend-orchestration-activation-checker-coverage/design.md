# Design

## Scope
This is a static policy-enforcement slice. It strengthens the checker-backed contract for the active automatic orchestration routing plan without launching experts, durable workflows, or persistent teams.

## Enforcement approach
`tools/check_orchestration_activation_policy.py` remains the single repository guard for this user-level boundary. The checker continues to use stable snippets because the current risk is prompt/policy drift rather than a runtime algorithm defect. This slice expands coverage to the highest-value rules from plan v0.16 that can be enforced statically:

- smallest-sufficient role selection and analyst-first bounded multi-face research;
- native agent versus skill/profile/plugin surfaces and fresh follow-up agents;
- current main session as leader and adoption scoped to the current task flow;
- native Codex as base layer, oh-my-codex/LangGraph as additive layers, and one backend family per durable task;
- delegation quality, non-overlapping leader work, and sparse waiting;
- read-only exploration versus code-changing worker delegation;
- LangGraph entrypoints, repo-local durable artifacts, frozen research briefs, and adversarial survivor queues.

## Why no durable team is launched
The implementation is one coherent checker/spec slice with overlapping hotspot files. There are not two independent write slices with disjoint ownership, so durable-team launch remains below threshold.

## Non-goals
- No runtime orchestration launcher changes.
- No user-level profile or skill loading changes.
- No live LangGraph or native_omx exercise.
- No remote publication.
