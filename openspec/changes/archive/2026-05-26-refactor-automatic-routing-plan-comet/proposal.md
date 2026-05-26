## Why

The automatic orchestration routing enforcement plan is the active baseline for Codex user-level collaboration behavior, but it has grown through several follow-up reviews. Readers need a Comet-tracked documentation refactor that separates current completion evidence, planned Phase 4 follow-up work, runtime-evidence boundaries, and local execution/verification expectations.

## What Changes

- Refactor `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` with a clear reading map, Comet traceability note, and implementation-ready Phase 4 summary.
- Preserve the existing policy facts: Phase 0-3 are complete, Phase 4 is planned follow-up, and the document itself is not runtime evidence that experts, durable teams, or persistent teams ran.
- Keep this as a documentation-only Comet tweak with no runtime, checker, source-template, user-home, target-project, local-main, or remote-publication mutation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

## Impact

- Affected document:
  - `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` - target Chinese implementation plan to refactor
- Affected workflow artifact:
  - `openspec/changes/refactor-automatic-routing-plan-comet/` - Comet/OpenSpec trace directory for this documentation tweak
- No runtime code, generated user-level assets, stable governance policy, target-project files, local `main`, or remote refs are changed by this tweak.

## impact_scope

- single implementation-plan documentation refactor
- Comet/OpenSpec traceability for the documentation tweak
- no runtime enforcement implementation

## explicit_non_goals

- no new checker or test implementation
- no change to automatic routing runtime behavior
- no durable/persistent team launch evidence claim
- no local-main integration
- no GitLab/GitHub publication

## rollout_sequence

1. Create isolated feature worktree `docs/refactor-automatic-routing-plan-comet` from current local `main`.
2. Create lightweight Comet/OpenSpec artifacts for the documentation tweak.
3. Refactor the Chinese implementation plan without changing the underlying policy status.
4. Run OpenSpec, document, local gate, and local MR-review checks.
5. Commit locally on the feature branch and stop before local-main integration or remote publication.

## rollback_plan

- Revert the feature-branch commit if the refactor wording proves misleading.
- If the Comet trace is not retained, revert or remove the corresponding OpenSpec archive entry together with the document commit.
- Do not touch runtime state, user-level Codex assets, target projects, local `main`, or remote refs during rollback.

## validation_path

- `git diff --check` - verifies whitespace and patch formatting
- `openspec validate --all` - validates stable specs and active changes
- `python .\tools\check_startup_instruction_mojibake.py` - verifies startup/instruction surfaces remain UTF-8-clean
- `python .\tools\check_context_retention_canary_surface.py` - verifies canary prompt confinement
- `python .\tools\check_precommit_update_archive.py --root . --json` - checks pre-commit update/archive readiness
- `python .\tools\run_openspec_guard.py --root .` - runs repository OpenSpec/governance guard suite
- `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate
- `.\tools\ci\local_mr_review.ps1` - runs local MR-style review before integration

## mainline_classification

- automatic orchestration routing documentation maintenance
