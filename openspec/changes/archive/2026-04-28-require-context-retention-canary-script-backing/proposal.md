## Why

Long sessions can outgrow or lose prompt-only reminders. Safety boundaries that affect durable state, publication, cleanup, activation, or cross-project scope therefore need executable controls that still protect a cold-start model with no prior conversation context.

This change also clarifies the context-retention canary placement rule: startup summaries own the literal canary prompt, while `AGENTS.md` remains a required recovery reread target and must not contain the literal canary prompt.

## What Changes

- Add a safety-rule script-backing registry and aggregate checker.
- Run the aggregate checker from the repository OpenSpec guard.
- Strengthen the existing context-retention canary checker so recovery text must require rereading `AGENTS.md`.
- Update startup summaries and implementation plans to say that safety rules require script control plus prompt reminders.
- Keep the literal canary prompt out of `AGENTS.md`, user-level startup summaries, implementation plans, wrappers, and launcher payloads.

## Capabilities

### New Capabilities

- `codex-user-level-safety-rule-script-backing`: verifies that registered system-level, user-level, and project-level safety rules have script controls, prompt reminder locations, guard linkage, and implementation status.

### Modified Capabilities

- `codex-user-level-context-retention-canary-surface`: requires canary recovery text to include `AGENTS.md` as a cold-start reread target while keeping the literal canary prompt confined to the startup summary pair.

## Impact

- Adds `tools/check_safety_rule_script_backing.py` - aggregate checker for registered safety rules.
- Adds `tools/safety_rule_script_backing_registry.json` - machine-readable registry of safety rules and their controls.
- Updates `tools/run_openspec_guard.py` - repository guard that runs the aggregate checker.
- Updates `tools/check_context_retention_canary_surface.py` - canary placement checker that now also verifies `AGENTS.md` recovery wording.
- Updates `docs_bilingual/project_startup_summary.*` and selected implementation plans.

## Impact Scope

This is a repository governance and guard change. It does not modify `.omx/state/`, user-level Codex config, user-level installed helpers, or consumer project repositories.

## Explicit Non-Goals

- Do not place the literal canary prompt in `AGENTS.md`.
- Do not inject the canary prompt into user-level wrapper payloads.
- Do not mutate durable state or launch a durable team.
- Do not clean or delete existing worktrees.

## Rollout Sequence

1. Add the registry, aggregate checker, and guard step.
2. Update startup-summary recovery wording and implementation-plan policy text.
3. Validate OpenSpec and guard output locally.
4. Publish through GitLab-first MR and sync GitHub only after GitLab `main` is merged and green.

## Rollback Plan

Revert this change branch or MR. The rollback removes the aggregate checker and registry while leaving existing canary placement enforcement unchanged unless the modified checker file is also reverted.

## Validation Path

- `python tools/check_context_retention_canary_surface.py --root . --json` - verifies startup-summary canary placement and `AGENTS.md` recovery wording.
- `python tools/check_safety_rule_script_backing.py --root . --json` - verifies registered safety rules have script controls, prompt reminders, and guard linkage.
- `openspec validate --all --json` - validates all OpenSpec specs and active changes.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - runs the repository aggregate guard used by CI.

## Mainline Classification

Existing mainline: Codex user-level orchestration governance and durable-team safety controls.
