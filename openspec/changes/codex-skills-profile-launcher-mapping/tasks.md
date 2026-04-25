## 1. OpenSpec Contract

- [x] 1.1 Validate `proposal.md`, `design.md`, and `specs/codex-skills-profile-launcher-mapping/spec.md` for Phase 4 scope and non-mutating launcher boundaries.
- [x] 1.2 Run `openspec status --change "codex-skills-profile-launcher-mapping"` to confirm all artifacts are present before implementation.
- [x] 1.3 Run `openspec validate "codex-skills-profile-launcher-mapping" --strict` to confirm the change contract is valid before implementation.

## 2. Registry and Documentation

- [x] 2.1 Add a declarative `launcher_mapping` section to `docs_bilingual/governance/codex_skills_profiles.registry.yaml` for profile-to-launcher metadata.
- [x] 2.2 Add `docs_bilingual/governance/codex_skills_profile_launcher_mapping.md` as the English governance document explaining the mapping and future optional aliases.
- [x] 2.3 Add `docs_bilingual/governance/codex_skills_profile_launcher_mapping.zh-CN.md` as the Chinese governance companion.
- [x] 2.4 Register the bilingual launcher mapping governance document in `docs_bilingual/docs_registry.yaml`.

## 3. Checker and Tests

- [x] 3.1 Add `tools/check_codex_skills_profile_launcher_mapping.py`, a JSON-emitting checker for profile launcher mapping metadata.
- [x] 3.2 Make the checker validate required mappings for `core`, `browser`, `web`, `github`, and `full`.
- [x] 3.3 Make the checker validate non-mutation, browser/web plugin preservation, reduced-scope `core`, and temporary `full` constraints.
- [x] 3.4 Add `test/check_codex_skills_profile_launcher_mapping.test.py` with fixture-based pass/fail cases.

## 4. Validation

- [x] 4.1 Run `git diff --check`.
- [x] 4.2 Run `python tools/check_document_governance_rules.py --root . --json`.
- [x] 4.3 Run `python tools/check_implementation_plan_rules.py --root . --json`.
- [x] 4.4 Run `python tools/check_codex_skills_governance.py --root . --json`.
- [x] 4.5 Run `python tools/check_codex_skills_profile_launcher_mapping.py --root . --json`.
- [x] 4.6 Run `python test/check_codex_skills_profile_launcher_mapping.test.py`.
- [x] 4.7 Run `openspec validate "codex-skills-profile-launcher-mapping" --strict`.
- [x] 4.8 Run `python tools/run_openspec_guard.py --root . --tool codex --json`.

## 5. Publication

- [ ] 5.1 Commit only the OpenSpec change, registry/docs updates, checker, and tests.
- [ ] 5.2 Push the feature branch to GitLab and create a GitLab MR.
- [ ] 5.3 Wait for the GitLab pipeline to pass before merging.
- [ ] 5.4 After GitLab main is merged and green, sync the exact GitLab main commit to GitHub main without creating a GitHub PR.
