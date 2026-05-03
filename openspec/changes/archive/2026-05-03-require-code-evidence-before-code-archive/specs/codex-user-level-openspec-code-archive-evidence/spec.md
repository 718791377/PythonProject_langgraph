## ADDED Requirements

### Requirement: Code-class OpenSpec archives SHALL include source or test evidence
When an OpenSpec change is archived as code-class work, the repository guard SHALL require changed source, executable check, CI, or test evidence in the same branch before allowing the archive to pass.

#### Scenario: Code-class archive has no code evidence
- **WHEN** a branch archives an OpenSpec change whose artifacts or metadata classify it as code, runtime, mixed, tooling, or CI work
- **AND** the same branch has no source, executable check, CI, or test file changes outside `docs_bilingual/` and `openspec/`
- **THEN** `python tools/run_openspec_guard.py --root .` SHALL fail through `tools/check_openspec_code_archive_evidence.py`
- **AND** the failure SHALL instruct the maintainer to land code/test evidence before archive or explicitly mark the change as docs-only when that is true

#### Scenario: Docs-only archive is explicit
- **WHEN** an archived OpenSpec change declares `x_change_class: docs`, `spec`, `governance`, `memory`, `research`, `plan`, or `status`
- **THEN** the code evidence checker SHALL not require source or test changes for that archive
