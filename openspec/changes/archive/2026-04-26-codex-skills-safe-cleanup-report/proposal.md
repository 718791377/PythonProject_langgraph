## Why

Phase 0, Phase 1, and Phase 2 of the Codex user-level skills governance plan are now in place. The next phase must make cleanup reviewable without deleting user-level skills, plugin files, or generated-looking OpenSpec assets prematurely.

This change implements Phase 3 as a safe, evidence-producing cleanup report. It identifies duplicate and preferred-source candidates, records why destructive cleanup is deferred, and preserves browser/web capabilities while preparing a later explicit cleanup decision.

## What Changes

- Add a repository-local safe-cleanup report generator for Codex skills governance.
- Produce a generated JSON report artifact that classifies:
  - same-layer repository OpenSpec duplicate candidates,
  - cross-layer GitHub duplicate skill candidates,
  - plugin-managed/report-only entries,
  - user-level long-description candidates,
  - required evidence before any cleanup action.
- Keep cleanup actions non-destructive:
  - no user-level skill deletion, movement, or description rewrite,
  - no plugin cache mutation,
  - no Vercel plugin disablement,
  - no user-level `config.toml` mutation.
- Add tests for the safe-cleanup report classification behavior.
- Keep Phase 4 launcher/profile integration out of scope until Phase 3 evidence is reviewable.
- No **BREAKING** changes are intended.

## Capabilities

### New Capabilities

- `codex-skills-safe-cleanup-reporting`: Defines how the repository generates, validates, and uses a non-destructive skills cleanup report for Phase 3 governance.

### Modified Capabilities

- None. This adds a new reporting capability rather than changing existing archived specs.

## Impact

- Affected documentation and artifacts:
  - `docs_bilingual/governance/codex_skills_safe_cleanup_report.json` - records the generated safe-cleanup candidate inventory for governance review.
  - `openspec/changes/codex-skills-safe-cleanup-report/` - stores the OpenSpec proposal, tasks, and design artifacts for this reporting change.
- Affected tooling and tests:
  - `tools/report_codex_skills_cleanup_candidates.py` - generates the report-only safe-cleanup candidate artifact without changing skill files.
  - `test/report_codex_skills_cleanup_candidates.test.py` - verifies the reporting tool keeps cleanup decisions evidence-based and non-destructive.
- Affected policy inputs:
  - `docs_bilingual/governance/codex_skills_profiles.registry.yaml` - defines profile ownership and preferred skill sources used by the report.
  - `docs_bilingual/governance/codex_skills_inventory_baseline.json` - provides the current skill inventory baseline compared by the report.
  - `tools/inventory_codex_skills.py` - collects installed skill metadata that feeds the governance inventory baseline.
  - `tools/check_codex_skills_governance.py` - enforces skill-governance constraints that the cleanup report must not weaken.
- No user-level skill directory, plugin cache file, Vercel plugin setting, or user-level Codex config file is modified.

## Impact Scope

This is a repository-local Phase 3 evidence and reporting change for the Codex user-level skills governance plan. It prepares review data for future cleanup but does not perform cleanup.

## Explicit Non-Goals

- Do not delete, move, rename, or edit user-level skills.
- Do not delete nested OpenSpec duplicate candidates.
- Do not disable or partially remove the Vercel plugin.
- Do not mutate `C:\Users\lenovo\.codex\config.toml`.
- Do not implement Phase 4 launcher aliases or profile-based launcher filtering in this change.
- Do not create GitHub PRs.

## Rollout Sequence

1. Create this OpenSpec change and validate the reporting contract.
2. Implement the non-destructive report generator and tests.
3. Generate the Phase 3 cleanup report artifact.
4. Run repository validation commands.
5. Publish through a GitLab-first MR only after local validation passes.

## Rollback Plan

- Before merge, rollback is deleting this feature branch or reverting its local changes.
- After merge, rollback is reverting the report generator, generated report artifact, and tests.
- No user-level skill, plugin, or config rollback is needed because this change does not mutate those locations.

## Validation Path

Minimum validation:

```powershell
git diff --check
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/inventory_codex_skills.py --root . --json
python tools/check_codex_skills_governance.py --root . --json
python tools/report_codex_skills_cleanup_candidates.py --root . --json
python test/report_codex_skills_cleanup_candidates.test.py
openspec status --change "codex-skills-safe-cleanup-report"
openspec validate "codex-skills-safe-cleanup-report" --strict
python tools/run_openspec_guard.py --root . --tool codex --json
```

If `--require-clean-git` OpenSpec guard evidence is needed, run it in a clean temporary clone, not in a dirty local workspace.

## Mainline Classification

This is a continuation of the Codex user-level skills governance and profiles implementation plan. It is a cross-mainline governance/reporting correction, not a new LangGraph-deepening mainline.
