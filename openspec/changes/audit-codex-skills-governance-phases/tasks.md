## 1. OpenSpec Artifact Completion

- [x] 1.1 Review `proposal.md`, `design.md`, and the lifecycle spec for consistency with the skills governance implementation plan.
- [x] 1.2 Run `openspec status --change "audit-codex-skills-governance-phases"` and confirm all required artifacts are present.
- [x] 1.3 Run `openspec validate "audit-codex-skills-governance-phases" --strict` and record the result.

## 2. Phase 0 Inventory Audit

- [x] 2.1 Verify `tools/inventory_codex_skills.py` exists and does not mutate user-level skills, plugin cache files, or repository skill files.
- [x] 2.2 Run `python tools/inventory_codex_skills.py --root . --json` and confirm the output reports counts by source layer.
- [x] 2.3 Confirm the inventory output reports duplicate skill-name groups, description lengths, suspected profiles, and status suggestions.
- [x] 2.4 Verify `docs_bilingual/governance/codex_skills_inventory_baseline.json` exists and matches the Phase 0 baseline expectations.
- [x] 2.5 Record Phase 0 findings without deleting, moving, renaming, or rewriting any user-level skill.

## 3. Phase 1 Policy and Registry Audit

- [x] 3.1 Verify the bilingual skills governance policy files exist under `docs_bilingual/governance/`.
- [x] 3.2 Verify `docs_bilingual/governance/codex_skills_profiles.registry.yaml` exists and defines the required profiles.
- [x] 3.3 Confirm the browser-profile legacy application project and `D:\PythonProject_CLIProxyAPI` retain browser-capable profile assignments.
- [x] 3.4 Verify the policy and registry are registered in `docs_bilingual/docs_registry.yaml`.
- [x] 3.5 Run `python tools/check_document_governance_rules.py --root . --json` and record the result.
- [x] 3.6 Run `python tools/check_implementation_plan_rules.py --root . --json` and record the result.
- [x] 3.7 Confirm the registry remains declarative and does not modify `C:\Users\lenovo\.codex\config.toml`.

## 4. Phase 2 Governance Check Normalization

- [x] 4.1 Verify `tools/check_codex_skills_governance.py` and `test/check_codex_skills_governance.test.py` exist.
- [x] 4.2 Run `python tools/check_codex_skills_governance.py --root . --json` and confirm errors, warnings, and deferred cleanup candidates are classified separately.
- [x] 4.3 Run `python -m pytest test/check_codex_skills_governance.test.py` or the repository-approved equivalent and record the result.
- [x] 4.4 Confirm Phase 2 local checks do not require disabling the Vercel plugin or editing plugin-managed files.
- [x] 4.5 Keep GitLab MR !6 open and untouched unless the user explicitly approves reuse, replacement, update, closure, or merge.
- [x] 4.6 After local evidence is reviewed, document whether Phase 2 should reuse MR !6, supersede it with a new branch, or defer guard integration.

## 5. Phase 3 Cleanup Deferral

- [x] 5.1 Identify duplicate OpenSpec skill candidates and other cleanup candidates as deferred, not as immediate deletion work.
- [x] 5.2 If OpenSpec guard cleanup evidence is required, prepare it in a clean temporary clone rather than the dirty local workspace.
- [x] 5.3 Require clean-clone evidence for OpenSpec regeneration and guard validation before proposing any repository skill deletion.
- [x] 5.4 Confirm no user-level skills, plugin cache files, Vercel plugin capabilities, or browser automation capabilities are removed by this change.

## 6. Local Validation and Reporting

- [x] 6.1 Run `git diff --check` and record the result.
- [x] 6.2 Run `openspec status --change "audit-codex-skills-governance-phases"` and record final artifact progress.
- [x] 6.3 Run `openspec validate "audit-codex-skills-governance-phases" --strict` and record the result.
- [x] 6.4 Report changed files, validation commands, MR !6 status, and any manual next steps.
- [x] 6.5 Do not commit, push, create, update, merge, close, or sync any MR/PR unless the user explicitly approves publication.
