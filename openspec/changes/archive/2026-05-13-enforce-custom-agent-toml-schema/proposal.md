# Change: Enforce custom agent TOML schema

## Why

The automatic orchestration routing enforcement plan requires native Codex agent surfaces to stay distinct from skills and plugin profiles, but the repository currently has no executable checker for standalone custom agent TOML shape.

Without a schema checker, user-level or repo-local native-agent roles can silently omit `name`, `description`, or `developer_instructions`, causing cold-start routing, role discovery, or expert brief loading to degrade while documentation still appears correct.

## What Changes

- Add a repository-local custom agent TOML schema checker.
- Validate standalone native-agent TOMLs under the user-level Codex agents directory and repo-local `.codex/agents/` when those directories exist.
- Require each parsed TOML to define non-empty top-level `name`, `description`, and `developer_instructions` string fields.
- Report missing agent directories as warnings instead of failures so clean CI environments without user-level agents remain usable.
- Register the checker as a script-backed safety rule and run it from the OpenSpec guard.
- Update governance and stable OpenSpec wording so native-agent TOML validity is enforced as a distinct surface from skills and plugin profiles.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-team-mode-native-subagent-boundaries`: adds executable schema validation for user-level and repo-local native-agent TOMLs.
- `codex-user-level-orchestration-activation-policy`: records the checker-backed boundary between native agents, skills, profiles, and follow-up surfaces.

## Impact

- `tools/check_custom_agent_toml_schema.py`: new checker.
- `test/check_custom_agent_toml_schema.test.py`: checker regression tests.
- `tools/run_openspec_guard.py`: runs the checker in JSON and text guard paths.
- `tools/safety_rule_script_backing_registry.json`: registers the safety rule.
- `AGENTS.md`: documents the minimum custom agent TOML schema and checker.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: document the native-agent TOML checker.
- `openspec/specs/codex-user-level-team-mode-native-subagent-boundaries/spec.md`: records the stable checker requirement.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: records activation-policy surface distinction.
- `tools/ci/ci_test_manifest.json`: out of scope for this slice because another active claim owns that path.

## impact_scope

Static validation of native Codex custom-agent TOML files, plus governance, OpenSpec guard, and safety-rule registry wiring.

## explicit_non_goals

- No live durable-team launch.
- No `omx-team-auto.ps1 -Apply` run.
- No user-level agent TOML mutation.
- No user-level Codex config or plugin cache mutation.
- No CI manifest registration in this slice.
- No runtime subagent launcher behavior change.

## rollout_sequence

1. Add the checker and regression tests.
2. Register the checker in the safety-rule registry and OpenSpec guard.
3. Update AGENTS.md, governance policy, and stable spec wording.
4. Validate targeted tests, policy checker, OpenSpec validation, OpenSpec guard, local gate, and local MR review.
5. Defer CI manifest registration until the active owner of `tools/ci/ci_test_manifest.json` releases that path.

## rollback_plan

Revert this branch commit to remove the checker, tests, registry entry, guard step, policy wording, and spec updates. No durable runtime state, user-level agent TOML, or remote publication is changed by this slice.

## validation_path

- `python tools/check_custom_agent_toml_schema.py --root . --json` - validates present repo-local and user-level agent TOMLs.
- `python test/check_custom_agent_toml_schema.test.py` - runs direct checker regression tests.
- `python tools/check_orchestration_activation_policy.py --root . --json` - confirms orchestration policy surfaces mention the checker-backed boundary.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - confirms guard and safety-rule registry linkage.
- `openspec validate --all --json` - validates active changes and stable specs.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` - runs the shared local/remote CI gate.

## mainline_classification

Existing mainline follow-up for `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`; this is a small checker-backed enforcement slice under the active automatic orchestration routing plan.
