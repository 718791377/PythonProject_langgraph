## Context

The repository already documents a layered capability model: native subagent routing gates oh-my-codex, oh-my-codex gates LangGraph, and LangGraph can be the default durable backend only when selected and ready. The current activation-policy checker verifies text surfaces, but it does not independently validate user-level state JSON combinations.

This change adds a small deterministic checker for the state combinations. The checker does not mutate state; it reports invalid present state so launchers, CI, or future helpers can fail closed.

## Decisions

- Implement `tools/check_capability_switch_chain.py` as a dependency-free Python checker.
- Read user-level state from `CODEX_USER_LEVEL_TEAM_MODE_STATE`, `CODEX_TEAM_MODE_STATE`, `CODEX_HOME/state/user-level-team-mode.json`, or `<home>/.codex/state/user-level-team-mode.json`.
- Read repo-local LangGraph backend context from `<root>/.omx/state/langgraph/backend.json` unless overridden.
- Treat a missing user-level state file as a warning by default for clean CI, with `--require-state` available for fail-closed launch/runtime checks.
- Fail present invalid combinations rather than silently normalizing them.
- Keep `tools/run_openspec_guard.py` unchanged for this slice because it already runs `tools/check_orchestration_activation_policy.py`, and that checker now invokes the capability-chain checker.
- Keep `tools/safety_rule_script_backing_registry.json` unchanged to avoid overlapping the active remote-publication gate claim; the existing orchestration-activation-policy rule remains the registry entry for this subcheck.
- Keep `tools/ci/ci_test_manifest.json` unchanged because another active claim owns that hotspot.

## Risks

- User-level state can be absent in CI. Mitigation: absence warns by default; runtime callers that require it can pass `--require-state`.
- Repo-local backend context may be stale. Mitigation: backend context is optional and only strengthens validation when present; activation trace still distinguishes backend readiness from persistent-team running state.
- The checker could be mistaken for a normalizer. Mitigation: proposal, docs, and spec say it reports invalid present state and does not mutate user-level state.

## Rollout

1. Add checker and tests.
2. Make activation-policy guard call the checker.
3. Update policy and specs.
4. Validate locally and archive before local main integration.
