# codex-skills-safe-cleanup-reporting Specification

## Purpose
Define the non-destructive Codex skills safe-cleanup reporting contract, candidate classifications, JSON evidence shape, and cleanup approval gates.
## Requirements
### Requirement: Safe cleanup reporting SHALL be non-destructive

The Codex skills safe-cleanup report generator SHALL inspect repository-local inventory and profile policy data without deleting, moving, renaming, or editing user-level skills, repository skills, plugin cache files, Vercel plugin settings, browser automation capabilities, or user-level Codex configuration.

#### Scenario: Report generation runs
- **WHEN** the operator runs the safe-cleanup report command
- **THEN** the command SHALL emit a report without mutating scanned skill files
- **AND** it SHALL not mutate plugin-managed files or user-level Codex configuration

#### Scenario: Cleanup candidates are found
- **WHEN** the report identifies duplicate or long-description candidates
- **THEN** it SHALL classify them as review evidence
- **AND** it SHALL not treat those candidates as permission to delete or rewrite files

### Requirement: Safe cleanup reporting SHALL classify candidate types

The safe-cleanup report SHALL classify at least these candidate types:

- same-layer repository duplicate candidates,
- OpenSpec nested duplicate candidates,
- cross-layer user/plugin duplicate candidates,
- user-level long-description candidates,
- plugin-managed report-only entries.

Each candidate SHALL include a severity or disposition, source layer, relevant file paths, and the required next evidence before destructive cleanup can be considered.

#### Scenario: OpenSpec nested duplicates are reported
- **WHEN** nested repository OpenSpec duplicate skill candidates are present
- **THEN** the report SHALL classify them as deferred cleanup requiring clean-clone OpenSpec regeneration evidence
- **AND** it SHALL include the candidate skill names and repository-local file paths

#### Scenario: GitHub duplicate skills are reported
- **WHEN** duplicate skill names are present across user and plugin layers and policy declares a preferred source
- **THEN** the report SHALL include the preferred source decision
- **AND** it SHALL keep the candidate non-destructive unless the user later approves user-level cleanup

#### Scenario: Plugin-managed skills are reported
- **WHEN** plugin skills are detected
- **THEN** the report SHALL classify plugin entries as report-only
- **AND** it SHALL preserve Vercel browser and web capabilities instead of recommending plugin disablement

### Requirement: Safe cleanup reporting SHALL produce stable JSON evidence

The safe-cleanup report command SHALL support a JSON output mode suitable for review, tests, and MR evidence.

The JSON output SHALL include:

- schema version,
- generation timestamp,
- repository root,
- input scan roots,
- summary counts,
- candidate list,
- policy decisions,
- safety constraints,
- validation notes.

#### Scenario: JSON report is generated to stdout
- **WHEN** the operator runs the report command with `--json`
- **THEN** stdout SHALL contain valid JSON
- **AND** the JSON SHALL include summary counts and a candidate list

#### Scenario: JSON report is written to an artifact
- **WHEN** the operator runs the report command with `--output <path>`
- **THEN** the command SHALL write the same report schema to the requested repository-local artifact path
- **AND** it SHALL create parent directories as needed without modifying scanned skill files

### Requirement: Safe cleanup reporting SHALL preserve Phase 3 gates

The safe-cleanup report SHALL state that destructive cleanup remains blocked unless clean-clone evidence and explicit user approval exist.

At minimum, OpenSpec duplicate cleanup SHALL require:

- OpenSpec regeneration evidence in a clean temporary clone,
- guard validation with a clean working tree,
- comparison against current generated-looking files,
- explicit user approval before deletion.

#### Scenario: Clean-clone evidence is absent
- **WHEN** the report is generated without clean-clone evidence
- **THEN** OpenSpec duplicate cleanup SHALL remain deferred
- **AND** the report SHALL explain the missing evidence

#### Scenario: Future cleanup is considered
- **WHEN** a future session reviews the report before cleanup
- **THEN** it SHALL find the required evidence checklist
- **AND** it SHALL not infer permission to modify user-level skills or plugin files from the report alone
