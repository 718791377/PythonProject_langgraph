# Design: Agent, skill, and profile surface boundary enforcement

## Approach

Implement one Python checker with two modes:

1. Repository mode validates that core policy surfaces explicitly distinguish native agents, skills, plugin profiles, profile helpers, and expert evidence.
2. Evidence mode validates saved traces or reports so skill/profile invocations are not claimed as native subagent results or expert evidence.

The checker complements `check_custom_agent_toml_schema.py`: TOML schema validation proves native custom agents have required fields; this change proves the surrounding policy and evidence do not confuse those agents with skills or profiles.

## CI and guard wiring

- Add the checker test to `tools/ci/ci_test_manifest.json`.
- Add a no-input guard step in `tools/run_openspec_guard.py`.
- Add the checker to `tools/safety_rule_script_backing_registry.json` under `orchestration-activation-policy`.

## Non-goals

- Do not modify user-level plugin cache or installed skills.
- Do not change the skill loader or profile helper implementation.
- Do not start a durable team; this is a single checker/CI execution slice.
