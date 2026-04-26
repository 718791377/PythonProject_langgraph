# Phase 2/3 Audit Evidence

Date: 2026-04-25

Scope: local audit and minimal repository-local check hardening. No commit, push, MR update, user-level skill mutation, plugin cache mutation, Vercel plugin disablement, browser capability removal, or user-level `config.toml` mutation was performed.

## Phase 2: Governance Check Normalization

### Artifacts

- `tools/check_codex_skills_governance.py`: present.
- `test/check_codex_skills_governance.test.py`: present.

### Initial audit finding

The Phase 2 check already distinguished blocking `errors` from non-blocking `warnings`, but the lifecycle spec requires cleanup candidates to be reported separately as `deferred`.

Before the local hardening in this audit, known same-layer OpenSpec duplicate candidates were represented as warnings. That made the cleanup safety boundary less explicit than the OpenSpec lifecycle requires.

### Local hardening performed

`tools/check_codex_skills_governance.py` now emits a top-level `deferred` list and `counts.deferred`.

Known same-layer duplicate exceptions, such as generated-looking nested OpenSpec skill duplicates, are now classified as deferred cleanup candidates rather than warnings.

`test/check_codex_skills_governance.test.py` now includes a regression test that verifies a known same-layer OpenSpec duplicate exception is reported as deferred cleanup with no blocking error.

### Command evidence

```powershell
python tools/check_codex_skills_governance.py --root . --json
```

Result: exit code 0.

Summary:

- `ok`: true
- errors: 0
- warnings: 33
- deferred: 10
- total skills: 131
- duplicate name groups: 12

Deferred cleanup candidates:

- `openspec-apply-change` - nested generated OpenSpec apply skill candidate deferred for clean-clone verification.
- `openspec-archive-change` - nested generated OpenSpec archive skill candidate deferred for clean-clone verification.
- `openspec-continue-change` - nested generated OpenSpec continue skill candidate deferred for clean-clone verification.
- `openspec-explore` - nested generated OpenSpec explore skill candidate deferred for clean-clone verification.
- `openspec-ff-change` - nested generated OpenSpec fast-forward skill candidate deferred for clean-clone verification.
- `openspec-new-change` - nested generated OpenSpec new-change skill candidate deferred for clean-clone verification.
- `openspec-onboard` - nested generated OpenSpec onboarding skill candidate deferred for clean-clone verification.
- `openspec-propose` - nested generated OpenSpec proposal skill candidate deferred for clean-clone verification.
- `openspec-sync-specs` - nested generated OpenSpec spec-sync skill candidate deferred for clean-clone verification.
- `openspec-verify-change` - nested generated OpenSpec verification skill candidate deferred for clean-clone verification.

The warnings remain non-blocking user-level description and plugin bundle findings. No plugin file or user-level skill file was edited.

### Test evidence

```powershell
python -m pytest test/check_codex_skills_governance.test.py
```

Result: not available in this environment because `pytest` is not installed.

Repository-approved equivalent:

```powershell
python test/check_codex_skills_governance.test.py
```

Result: exit code 0, 4 tests passed.

### MR !6 decision

GitLab MR !6 remains a frozen external candidate. This audit does not reuse, update, close, merge, or supersede it.

Recommended next decision after review:

- Keep MR !6 untouched until the user explicitly chooses one of:
  - reuse it after aligning it with this OpenSpec change,
  - close it and replace it with a new OpenSpec-backed branch,
  - defer guard/CI integration.

## Phase 3: Cleanup Deferral

Phase 3 cleanup remains deferred.

This audit identified cleanup candidates only through the governance check output. It did not delete or move repository OpenSpec skills, user-level skills, or plugin files.

Required future evidence before any cleanup proposal:

- run OpenSpec regeneration in a clean temporary clone,
- compare regenerated OpenSpec skill files with current nested duplicates,
- run the OpenSpec guard with `--require-clean-git` in a clean clone,
- obtain explicit user approval before any deletion.

No clean-clone guard was run in this local dirty workspace because this audit did not perform cleanup and the workspace contains unrelated local drafts.
