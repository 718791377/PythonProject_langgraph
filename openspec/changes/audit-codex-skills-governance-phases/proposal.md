## Why

The Codex user-level skills governance work already has Phase 0 and Phase 1 changes merged, and a follow-up Phase 2 MR was opened too quickly without first creating an OpenSpec change. This change retrofits the missing OpenSpec control point so the repository can re-audit the merged Phase 0/1 work, normalize the Phase 2 path, and defer any destructive Phase 3 cleanup until the required evidence exists.

## What Changes

- Re-audit Phase 0 and Phase 1 deliverables against `docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.zh-CN.md` and the English companion.
- Verify that Phase 0 baseline inventory exists, reports counts and duplicates, and did not delete user-level skills or disable plugins.
- Verify that Phase 1 governance policy, profiles registry, and docs registry entries exist and pass repository governance checks.
- Normalize Phase 2 as an OpenSpec-controlled follow-up before any additional CI/guard integration is merged.
- Keep GitLab MR !6 open but untouched while this OpenSpec change defines the review and acceptance path.
- Explicitly defer Phase 3 cleanup: no deletion, movement, or mutation of user-level skills; no Vercel plugin disablement; no OpenSpec nested duplicate cleanup until a clean-clone guard proves it is safe.
- Record validation, rollback, and publication constraints before further implementation proceeds.
- No **BREAKING** changes are intended.

## Capabilities

### New Capabilities

- `codex-user-level-skills-governance-lifecycle`: Defines the phase-gated lifecycle for auditing skills inventory, profile governance, governance checks, CI integration, and deferred cleanup safety in the user-level Codex skills governance line.

### Modified Capabilities

- None. Existing stable specs are not changed by this proposal; this change creates a missing OpenSpec contract around the already-started skills governance work.

## Impact

- Affected documentation and artifacts:
  - `docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md`
  - `docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.zh-CN.md`
  - `docs_bilingual/governance/codex_user_level_skills_governance_policy.md`
  - `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md`
  - `docs_bilingual/governance/codex_skills_profiles.registry.yaml`
  - `docs_bilingual/governance/codex_skills_inventory_baseline.json`
  - `docs_bilingual/docs_registry.yaml`
- Affected tooling and tests:
  - `tools/inventory_codex_skills.py`
  - `tools/check_codex_skills_governance.py`
  - `test/check_codex_skills_governance.test.py`
  - possible future guarded integration through `tools/run_openspec_guard.py`, `.gitlab-ci.yml`, or `.github/workflows/openspec-guard.yml`
- No user-level skill directory is to be edited by this change.
- `C:\Users\lenovo\.codex\config.toml` is out of scope and must not be modified.
- Browser automation capability for the browser-profile projects must remain available.
- Vercel plugin availability must not be disabled as part of this change.

## Impact Scope

This is a repository-local governance and audit change for the Codex user-level skills governance line. It may create OpenSpec artifacts, audit existing repository files, and propose future repository-local fixes, but it must not directly modify user-level skills, plugin cache files, user-level Codex configuration, or other repositories.

## Explicit Non-Goals

- Do not delete, move, rename, or shorten user-level skills in this change.
- Do not disable the Vercel plugin or remove browser automation capabilities.
- Do not automatically modify `C:\Users\lenovo\.codex\config.toml`.
- Do not merge, close, force-push, or otherwise mutate GitLab MR !6 while this audit proposal is being established.
- Do not perform Phase 3 cleanup of OpenSpec nested duplicate skills in this change.
- Do not create GitHub PRs for this repository.
- Do not treat repository-local `.omx/state` or OpenSpec state as global state for other projects.

## Rollout Sequence

1. Create this OpenSpec proposal and confirm the scope with the user.
2. Create the spec for `codex-user-level-skills-governance-lifecycle` to define phase-gated requirements.
3. Create design and tasks that separate:
   - Phase 0/1 audit of already merged artifacts,
   - Phase 2 normalization and decision on MR !6,
   - Phase 3 cleanup deferral and evidence requirements.
4. Run local validation only; do not publish until the OpenSpec artifacts are reviewed.
5. If fixes are needed, implement them in a new local branch or update an approved branch only after explicit user approval.

## Rollback Plan

- Before any new implementation is merged, rollback is simply deleting or revising this local OpenSpec change.
- If Phase 2 work from MR !6 is later rejected, close that MR or supersede it with a new OpenSpec-backed branch after user approval.
- Do not revert the already-merged Phase 0/1 mainline unless this audit identifies a concrete defect and the user approves a corrective GitLab-first MR.
- Any future cleanup branch must be reversible and must not touch user-level skills without explicit backup and approval.

## Validation Path

Minimum local validation for this audit change:

```powershell
git diff --check
python tools/check_document_governance_rules.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/inventory_codex_skills.py --root . --json
python tools/check_codex_skills_governance.py --root . --json
python test/check_codex_skills_governance.test.py
openspec status --change "audit-codex-skills-governance-phases"
openspec validate --all
```

If OpenSpec guard is required with `--require-clean-git`, run it in a clean temporary clone so unrelated local drafts do not affect the result.

## Mainline Classification

This is a cross-mainline governance correction for the Codex user-level skills governance and profile implementation work. It is not a new LangGraph-deepening mainline and does not supersede the current named repository mainline. Its purpose is to restore OpenSpec discipline around the skills governance work already started in Phase 0/1 and to gate Phase 2/3 continuation.
