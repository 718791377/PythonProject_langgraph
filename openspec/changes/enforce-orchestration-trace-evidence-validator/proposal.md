# Change: Enforce orchestration trace evidence validator

## Why

The automatic orchestration routing enforcement plan now has broad policy-surface and snippet-backed checker coverage, but it still lacks a small executable validator for concrete activation trace text.

Without a trace-level validator, regressions can still pass when documentation contains the right policy words but live or recorded traces omit required fields, cite missing user reminders, collapse backend readiness into team launch, or treat expert timeouts as accepted evidence.

## What Changes

- Add a repository-local activation trace evidence validator.
- Validate required trace fields: phase, capability_chain, backend_default, backend_ready, experts, durable_workflow, persistent_team, and why.
- Validate capability-chain dependency consistency for `subagent`, `omx`, and `langgraph` states.
- Validate durable workflow and persistent-team vocabulary.
- Reject missing-reminder reasons such as “user did not request parallelism/subagents”.
- Reject expert timeout evidence unless the text explicitly labels timeout as not used as evidence, main-session takeover, bounded wait, respawn, or durable handoff.
- Update governance policy and stable OpenSpec requirements to describe the executable trace validator.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-orchestration-activation-policy`: adds executable trace-evidence validation for saved activation traces.

## Impact

- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: document the trace-evidence validator.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: records the stable trace-evidence validator requirement.
- `tools/check_orchestration_trace_evidence.py`: new trace-evidence validator.
- `test/check_orchestration_trace_evidence.test.py`: direct regression tests for the validator.
- `tools/ci/ci_test_manifest.json`: out of scope for this slice because another active claim currently owns that path.

## impact_scope

Static trace-evidence validation for activation trace text, plus governance and stable spec language.

## explicit_non_goals

- No live durable-team launch.
- No `omx-team-auto.ps1 -Apply` run.
- No user-level config or plugin cache mutation.
- No CI manifest registration in this slice.
- No runtime launcher change.

## rollout_sequence

1. Add trace-evidence checker and unit tests.
2. Update active policy and stable spec wording.
3. Validate OpenSpec, targeted tests, policy checker, local gate, and local MR review.
4. Defer CI manifest registration until the active owner of `tools/ci/ci_test_manifest.json` releases that path.

## rollback_plan

Revert this branch commit to remove the checker, tests, policy wording, and spec text. No durable runtime state or remote publication is changed by this slice.

## validation_path

- `python tools/check_orchestration_trace_evidence.py --trace <file> --json` - validates a saved activation trace evidence file.
- `python test/check_orchestration_trace_evidence.test.py` - runs direct trace-evidence validator regression tests.
- `python tools/check_orchestration_activation_policy.py --root . --json` - confirms policy surfaces reference the validator.
- `openspec validate --all --json` - validates active changes and stable specs.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local/remote CI gate.

## mainline_classification

Existing mainline follow-up for `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`; this is a small checker-backed enforcement slice under the active automatic orchestration routing plan.
