## Why

The context-retention canary was intentionally added to make prompt loss visible, but its literal prompt text is currently duplicated across startup and routing surfaces. Duplicating that text in `AGENTS.md` makes it look like a per-turn project instruction source rather than a startup-summary-owned canary and increases the chance of drift when the canary is changed later.

This change is needed now because the operator explicitly wants the canary prompt to live only in `project_startup_summary.*` while retaining script-backed enforcement for the placement rule.

## What Changes

- Make `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md` the only active files that contain the literal context-retention canary prompt.
- Update `AGENTS.md` so it points to the startup-summary canary source and recovery action without duplicating the literal canary prompt.
- Update the active user-level team-mode implementation plan so it describes the startup-summary-only canary surface without repeating the literal prompt.
- Add a repository checker that fails closed if the literal canary prompt is missing from the startup summaries or appears in another active instruction surface.
- Add the checker to the OpenSpec guard sequence so a cold-start or CI run can catch accidental prompt duplication.

## Capabilities

### New Capabilities
- `codex-user-level-context-retention-canary-surface`: defines the startup-summary-only source of truth for the context-retention canary prompt and the executable guard that enforces that placement in active repository files.

### Modified Capabilities
- `codex-user-level-team-mode-startup-binding`: clarify that startup and launcher-facing surfaces may point to the startup-summary canary, but must not duplicate the literal canary prompt outside the startup summary pair.

## Impact

Impact scope:
- project startup summaries
- repository instruction surface (`AGENTS.md`)
- active team-mode implementation plan
- OpenSpec change artifacts and stable specs after archive
- OpenSpec guard and related tests

Explicit non-goals:
- Do not change the canary phrase itself.
- Do not remove context-loss detection.
- Do not modify user-level skills, Vercel plugin state, browser automation capability, or `C:\Users\lenovo\.codex\config.toml`.
- Do not change durable-team routing thresholds or backend-family selection.

Rollout sequence:
1. Write this OpenSpec change and its tasks before editing implementation files.
2. Update startup-summary and plan surfaces first.
3. Add checker coverage and guard integration.
4. Modify `AGENTS.md` last so it no longer contains the literal canary prompt.
5. Validate, archive the OpenSpec change if complete, then publish through GitLab-first review and sync GitHub main after merge.

Rollback plan:
- Revert the feature branch or MR before merge.
- After merge, revert the merge commit in GitLab main and resync GitHub main.
- If the checker is too strict, narrow its scan scope while keeping startup summaries as the canary source of truth.

Validation path:
- `git diff --check` - verifies whitespace-safe diffs.
- `python tools/check_context_retention_canary_surface.py --root . --json` - verifies startup-summary-only canary prompt placement.
- `python .\test\check_context_retention_canary_surface.test.py; python .\test\run_openspec_guard_json.test.py` - runs the new checker tests and guard JSON aggregation tests.
- `python tools/check_document_governance_rules.py --root . --json` - verifies document governance rules.
- `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation-plan governance rules.
- `python tools/run_openspec_guard.py --root . --json` - runs the aggregate OpenSpec guard.
- `openspec validate --all` - validates active OpenSpec changes and stable specs.

Mainline classification:
- Cross-mainline governance issue under the Codex user-level orchestration line.
