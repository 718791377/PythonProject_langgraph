## Why

The automatic orchestration routing enforcement plan is the active baseline for user-level collaboration routing, but the prior Comet pass was intentionally a tweak-level documentation cleanup. The user now requested a full `/comet` refactor of `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` and a local Git commit.

A full pass is needed to make the documentation maintenance itself auditable: OpenSpec artifacts should explain the change, Superpowers artifacts should capture the design and implementation plan, and the target plan should clearly distinguish policy expectations, completed Phase 0-3 evidence, planned Phase 4 hardening, and runtime evidence boundaries.

## What Changes

- Refactor the Chinese target implementation plan with a full Comet reading path, artifact map, and explicit documentation-only evidence boundary.
- Update the English companion plan with the same high-level full Comet framing so bilingual authority surfaces remain aligned for this refactor.
- Add full Comet/OpenSpec/Superpowers trace artifacts for design, implementation plan, management checklist, delta spec, tasks, and verification.
- Preserve the substantive policy facts: Phase 0-3 remain completed, Phase 4 remains planned follow-up, LangGraph ready is not persistent team running, and plan text is not runtime evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `automatic-orchestration-plan-doc-refactor`: document-maintenance traceability for full Comet refactors of the automatic orchestration routing enforcement plan.

## Impact

- Affected documents:
  - `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` - primary Chinese implementation plan receiving the full Comet refactor framing.
  - `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md` - English companion receiving matching high-level framing.
- Affected workflow artifacts:
  - `openspec/changes/refactor-automatic-routing-plan-full-comet/` - full OpenSpec change trace for the documentation-only refactor.
  - `docs/superpowers/specs/2026-05-27-automatic-routing-plan-full-comet-refactor-design.md` - Superpowers design doc for the selected refactor approach.
  - `docs/superpowers/plans/2026-05-27-automatic-routing-plan-full-comet-refactor.md` - Superpowers implementation plan for execution and verification.
- No runtime code, generated user-level assets, target-project files, local `main`, or remote refs are changed by this documentation-only refactor.

## Non-Goals

- Do not implement Phase 4 prompt-independent parity checkers in this change.
- Do not claim that durable teams, persistent teams, LangGraph workflows, or native experts ran.
- Do not mutate user-level Codex assets, `.omx` durable state, or external project repositories.
- Do not integrate into local `main` or publish to GitLab/GitHub without a separate explicit user request.

## Validation Path

- `git diff --check` - checks whitespace and patch formatting.
- `openspec validate --all` - validates OpenSpec specs and active changes.
- `python .\tools\check_startup_instruction_mojibake.py` - verifies startup and instruction surfaces remain UTF-8 clean.
- `python .\tools\check_context_retention_canary_surface.py` - verifies canary prompt confinement.
- `python .\tools\check_precommit_update_archive.py --root . --json` - checks commit readiness and OpenSpec archive policy.
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec guard suite.
- `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `.\tools\ci\local_mr_review.ps1` - runs the local MR-style review gate after commit.

## Rollback

Revert the feature-branch commit. Because this is documentation-only, rollback must not touch runtime state, user-level assets, local `main`, remote refs, or target-project files.
