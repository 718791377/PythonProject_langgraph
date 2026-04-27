## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, specs, and tasks for startup-summary-only canary prompt placement.

## 2. Startup and plan surfaces

- [x] 2.1 Update `docs_bilingual/project_startup_summary.md` to declare the startup summary pair as the only literal canary prompt location.
- [x] 2.2 Update `docs_bilingual/project_startup_summary.zh-CN.md` with the same rule.
- [x] 2.3 Update `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` to remove duplicated literal canary prompt text and point to startup summaries.
- [x] 2.4 Update `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` with the same rule.
- [x] 2.5 Update the north-star durable-team draft plan pair to remove duplicated literal canary prompt text and point to startup summaries.

## 3. Script enforcement

- [x] 3.1 Add `tools/check_context_retention_canary_surface.py`.
- [x] 3.2 Add unit tests for allowed startup-summary placement, missing startup prompt, and duplicate active-file prompt.
- [x] 3.3 Add the checker to `tools/run_openspec_guard.py` and update guard JSON tests.

## 4. AGENTS last

- [x] 4.1 Update `AGENTS.md` last so it points to startup-summary canary recovery without duplicating the literal prompt.

## 5. Verification and publication

- [x] 5.1 Run `git diff --check`.
- [x] 5.2 Run the new canary checker and unit tests.
- [x] 5.3 Run document governance and implementation-plan checks.
- [x] 5.4 Run the OpenSpec guard and `openspec validate --all`.
- [x] 5.5 Prepare the OpenSpec change for archive after validation; GitLab-first publication is handled after archive as the repository release step.
