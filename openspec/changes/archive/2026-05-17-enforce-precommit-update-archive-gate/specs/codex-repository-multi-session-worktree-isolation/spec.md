## ADDED Requirements

### Requirement: Local commits SHALL run a pre-commit update/archive review

The repository SHALL provide a local pre-commit update/archive checker that inspects the current branch diff plus staged, unstaged, and untracked files before local repository commits.

The checker SHALL verify at least:

- completed active OpenSpec changes are archived before commit, unless they explicitly record an archive deferral reason and follow-up;
- new CI-managed Python test files are registered in `tools/ci/ci_test_manifest.json` before commit;
- new checker scripts are registered in the aggregate guard or safety-rule backing registry before commit.

#### Scenario: Completed active OpenSpec change is not archived

- **WHEN** `tools/check_precommit_update_archive.py --root . --json` scans a branch or dirty worktree
- **AND** an active OpenSpec change touched by the current diff has all task checkboxes checked
- **AND** the same diff does not archive that change
- **AND** the active change does not declare both `x_archive_deferred_reason` and `x_archive_follow_up`
- **THEN** the checker SHALL fail
- **AND** it SHALL instruct the maintainer to archive the change or record the explicit two-step follow-up before commit

#### Scenario: New test is missing from CI manifest

- **WHEN** a new `test/*.test.py` file appears in the current diff
- **AND** its file name is absent from `tools/ci/ci_test_manifest.json`
- **THEN** the checker SHALL fail
- **AND** it SHALL identify the missing manifest update

#### Scenario: New checker is not registered

- **WHEN** a new `tools/check_*.py` checker appears in the current diff
- **AND** the checker is not referenced from `tools/run_openspec_guard.py`
- **AND** the checker is not referenced from `tools/safety_rule_script_backing_registry.json`
- **THEN** the checker SHALL fail
- **AND** it SHALL identify the missing guard or registry update

### Requirement: OpenSpec guard SHALL include the pre-commit update/archive checker

The aggregate repository OpenSpec guard SHALL run the pre-commit update/archive checker so the installed `.githooks/pre-commit` hook, local gate, and remote mirrored CI surface share the same update/archive enforcement.

#### Scenario: Aggregate guard emits JSON

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregated output SHALL include a `check_precommit_update_archive` step
- **AND** the aggregate guard SHALL fail if the checker reports errors
