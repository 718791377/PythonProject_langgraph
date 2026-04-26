## 1. OpenSpec Contract

- [x] 1.1 Validate `proposal.md`, `design.md`, and `specs/codex-skills-safe-cleanup-reporting/spec.md` for Phase 3 scope, safety constraints, and non-destructive cleanup boundaries.
- [x] 1.2 Run `openspec status --change "codex-skills-safe-cleanup-report"` to confirm all artifacts are present before implementation.
- [x] 1.3 Run `openspec validate "codex-skills-safe-cleanup-report" --strict` to confirm the change contract is valid before implementation.

## 2. Report Generator

- [x] 2.1 Add `tools/report_codex_skills_cleanup_candidates.py`, a non-destructive command that builds a Phase 3 cleanup candidate report from the existing skills inventory and profile registry.
- [x] 2.2 Make the report command support `--root . --json` for stdout JSON review.
- [x] 2.3 Make the report command support `--output docs_bilingual/governance/codex_skills_safe_cleanup_report.json` for a repository-local generated evidence artifact.
- [x] 2.4 Include candidate classifications for same-layer repository duplicates, nested OpenSpec duplicates, user/plugin duplicate preferred-source decisions, user-level long descriptions, and plugin-managed report-only entries.
- [x] 2.5 Include safety constraints and evidence requirements that keep destructive cleanup blocked until clean-clone evidence and explicit user approval exist.

## 3. Tests and Generated Evidence

- [x] 3.1 Add `test/report_codex_skills_cleanup_candidates.test.py` with fixture-based tests for non-destructive JSON generation.
- [x] 3.2 Test that known same-layer OpenSpec duplicate candidates are classified as deferred cleanup requiring clean-clone evidence.
- [x] 3.3 Test that user/plugin duplicate candidates include preferred-source decisions without recommending immediate user-level deletion.
- [x] 3.4 Generate `docs_bilingual/governance/codex_skills_safe_cleanup_report.json` using the new report command.
- [x] 3.5 Verify the generated report records zero cleanup actions performed.

## 4. Validation

- [x] 4.1 Run `git diff --check` for whitespace and patch hygiene.
- [x] 4.2 Run `python tools/check_document_governance_rules.py --root . --json` for document governance.
- [x] 4.3 Run `python tools/check_implementation_plan_rules.py --root . --json` for implementation-plan governance.
- [x] 4.4 Run `python tools/inventory_codex_skills.py --root . --json` for Phase 0 inventory continuity.
- [x] 4.5 Run `python tools/check_codex_skills_governance.py --root . --json` for Phase 2 governance continuity.
- [x] 4.6 Run `python tools/report_codex_skills_cleanup_candidates.py --root . --json` for Phase 3 report generation.
- [x] 4.7 Run `python test/report_codex_skills_cleanup_candidates.test.py` for report command tests.
- [x] 4.8 Run `openspec validate "codex-skills-safe-cleanup-report" --strict`.
- [x] 4.9 Run `python tools/run_openspec_guard.py --root . --tool codex --json`.

## 5. Publication

- [x] 5.1 Commit only the OpenSpec change, report generator, tests, and generated report artifact.
- [x] 5.2 Push the feature branch to GitLab and create a GitLab MR.
- [x] 5.3 Wait for the GitLab pipeline to pass before merging.
- [x] 5.4 After GitLab main is merged and green, sync the exact GitLab main commit to GitHub main without creating a GitHub PR.
