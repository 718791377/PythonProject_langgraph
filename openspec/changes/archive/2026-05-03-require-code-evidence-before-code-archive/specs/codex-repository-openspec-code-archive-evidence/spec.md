## ADDED Requirements

### Requirement: Code-affecting OpenSpec archives SHALL include validation evidence

A newly archived OpenSpec change that affects repository code, executable scripts, tests, CI, hooks, or guard behavior SHALL include concrete validation evidence through same-branch code changes or declared already-landed evidence paths in `.openspec.yaml`.

#### Scenario: Archived code-affecting change lacks evidence

- **WHEN** `python tools/check_openspec_code_archive_evidence.py --root . --json` scans current branch or working-tree archive diffs
- **AND** a newly archived change is classified as code, runtime, mixed, tooling, or CI work
- **AND** the same branch has no source, executable check, CI, or test file changes outside `docs_bilingual/` and `openspec/`
- **AND** the change does not declare an existing source, executable check, CI, or test path through `x_code_evidence_paths`
- **THEN** the checker SHALL fail
- **AND** it SHALL identify the change and the missing evidence requirement

#### Scenario: Archived code-affecting change declares already-landed code evidence

- **WHEN** the checker scans a newly archived OpenSpec change
- **AND** the change is classified as code, runtime, mixed, tooling, or CI work
- **AND** the archive branch has no new code diff because implementation already landed on `main`
- **AND** `.openspec.yaml` declares an existing source, executable check, CI, or test path through `x_code_evidence_paths`
- **THEN** the checker SHALL pass

#### Scenario: Documentation-only archived change passes

- **WHEN** the checker scans a newly archived OpenSpec change
- **AND** the change is explicitly documentation-only or does not mention code or executable repository surfaces
- **THEN** the checker SHALL pass without requiring code-validation evidence

### Requirement: OpenSpec guard SHALL enforce code archive evidence

The aggregate repository OpenSpec guard SHALL run the code archive evidence checker.

#### Scenario: Aggregate guard JSON includes archive evidence step

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregated output SHALL include a `check_openspec_code_archive_evidence` step
- **AND** the aggregate guard SHALL fail if the checker reports errors
