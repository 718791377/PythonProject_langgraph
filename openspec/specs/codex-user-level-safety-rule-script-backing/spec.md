# codex-user-level-safety-rule-script-backing Specification

## Purpose
Require safety-critical system-level, user-level, and project-level rules to have both prompt reminders and executable checker coverage so new sessions cannot depend on model memory alone.
## Requirements
### Requirement: Registered safety rules SHALL declare script backing

The repository SHALL maintain a machine-readable registry of safety rules that affect system-level, user-level, or project-level boundaries.

Each implemented registered rule SHALL declare at least one prompt reminder location and at least one executable script control.

#### Scenario: Aggregate checker validates implemented rules

- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` runs
- **THEN** every implemented registered rule SHALL have existing prompt reminder paths
- **AND** every implemented registered rule SHALL have existing script control paths

### Requirement: Safety-rule guard linkage SHALL be executable

Registered rules that declare OpenSpec guard steps SHALL be checked against the repository guard script.

#### Scenario: Registered guard step is missing

- **WHEN** a registered rule declares a `guard_steps` entry that is not referenced by `tools/run_openspec_guard.py`
- **THEN** the aggregate checker SHALL fail
- **AND** it SHALL report the rule id and missing guard step

### Requirement: Non-implemented safety rules SHALL be tracked gaps

A registered rule whose status is not `implemented` SHALL include tracked-gap text so a cold-start model can see that the missing control is known.

#### Scenario: Planned rule omits gap text

- **WHEN** a registered rule has status `planned` or `tracked_gap`
- **AND** it has no non-empty `gap` field
- **THEN** the aggregate checker SHALL fail

### Requirement: OpenSpec guard SHALL run the aggregate safety checker

The repository OpenSpec guard SHALL run the aggregate safety-rule script-backing checker as part of standard verification.

#### Scenario: OpenSpec guard emits JSON

- **WHEN** `python tools/run_openspec_guard.py --root . --tool codex --json` runs
- **THEN** the aggregated guard output SHALL include a `check_safety_rule_script_backing` step
- **AND** the guard SHALL fail if the aggregate checker reports errors
