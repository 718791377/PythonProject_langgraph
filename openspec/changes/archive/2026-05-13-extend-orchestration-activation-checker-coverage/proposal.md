# Change: Extend orchestration activation checker coverage

## Why
The active automatic orchestration routing plan has grown beyond the first checker slices for trace fields, durable-team thresholds, and hard routing directives. Several high-value rules remain documented in the plan but are not yet required by the script-backed guard, so a cold-start or resumed session could regress on role minimality, surface boundaries, leader ownership, delegation discipline, or durable artifact handling without local CI noticing.

## What Changes
- Strengthen the active orchestration activation governance policy with concise rules for smallest-sufficient role selection, agent/skill/profile boundaries, leader ownership, base/wrapper layer terminology, effective lane choice, delegation discipline, exploration versus implementation worker boundaries, and research/adversarial handoff persistence.
- Extend `tools/check_orchestration_activation_policy.py` required snippets so those rules are checked on active governance and stable OpenSpec surfaces.
- Add regression tests for the new checker coverage; defer local/remote CI manifest registration because another active claim currently owns `tools/ci/ci_test_manifest.json`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-orchestration-activation-policy`: extends the policy contract for role minimality, execution-surface separation, leader-owned fan-in, base-layer terminology, delegation wait discipline, exploration/worker boundaries, and persisted handoff artifacts.

## Impact
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: add concise active policy text for the newly guarded rules.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: records the stable requirement language checked by the guard.
- `tools/check_orchestration_activation_policy.py`: expands required snippets.
- `test/check_orchestration_activation_policy.test.py`: adds regression tests for missing advanced routing coverage.
- `tools/ci/ci_test_manifest.json`: out of scope for this slice because `enforce-remote-publication-approval-gate` currently owns that path.

## impact_scope
Static governance, stable OpenSpec policy text, repository checker coverage, and CI test registration for orchestration activation enforcement.

## explicit_non_goals
- No live durable-team launch.
- No `omx-team-auto.ps1 -Apply` run.
- No `.omx/state/` mutation beyond the ignored local session-claim file for this worktree.
- No user-level config or plugin cache mutation.
- No change to provider pacing or native subagent runtime implementation.

## rollout_sequence
1. Update the active policy and stable spec wording.
2. Extend checker snippets and regression tests.
3. Keep CI manifest registration deferred until the active owner of `tools/ci/ci_test_manifest.json` releases that path.
4. Run targeted checker tests, OpenSpec guard, and local gate before recommending local integration.

## rollback_plan
Revert this branch commit to restore the previous checker snippet set, policy wording, spec text, and CI manifest. No runtime state or remote publication is changed by this slice.

## validation_path
- `python tools/check_orchestration_activation_policy.py --root . --json` - verifies the orchestration activation policy surfaces and snippets.
- `python test/check_orchestration_activation_policy.test.py` - runs the direct regression tests for the checker.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - runs the repository OpenSpec guard and registered safety checks.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local/remote CI gate; this confirms guard coverage while the manifest registration remains deferred.

## mainline_classification
Existing mainline follow-up for `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`; this is a small checker-backed enforcement slice under the active automatic orchestration routing plan.
