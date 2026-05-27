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

### Requirement: Document-pair and commit-language safety rules SHALL be script-backed

The repository SHALL register safety rules for forward bilingual document pairs and Chinese local commit subjects.

The forward bilingual document-pair rule SHALL require changed Markdown files under `docs_bilingual/`, `openspec/`, and `docs/` to have an English ASCII primary and a Chinese companion. The rule MAY treat historical unchanged files as baseline so unrelated work is not blocked by legacy archive gaps.

The local commit-language rule SHALL require feature commit subjects to contain Chinese text, while allowing ASCII conventional prefixes when the subject still contains Chinese.

#### Scenario: New checker rules are registered
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` runs
- **THEN** it SHALL include implemented rules for forward bilingual document pairs and local Git commit Chinese subjects
- **AND** each rule SHALL point to prompt reminders, executable script controls, and aggregate guard steps

#### Scenario: Guard runs the new checks
- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregated guard output SHALL include `check_document_pair_policy` and `check_git_commit_language`
- **AND** the guard SHALL fail if either checker reports errors

### Requirement: Implementation plans SHALL be active before implementation

The repository SHALL require any implementation plan referenced by an active Comet change in build, verify, or archive phase to be registered with `status: active` before implementation continues.

#### Scenario: Comet build references a draft implementation plan
- **WHEN** an active Comet change has `phase: build`, `phase: verify`, or `phase: archive`
- **AND** its `.comet.yaml` references a `docs_bilingual/implementation_plans/` file whose registry entry is not `active`
- **THEN** the implementation-plan checker SHALL fail
- **AND** it SHALL identify the change and plan that must be activated or replaced

### Requirement: Post-plan and complete-local-flow rules SHALL be script-backed
The repository SHALL register safety-rule script backing for both post-`/plan` execution governance and the complete local flow to the remote publication gate.

The registry SHALL point to prompt reminders, executable script controls, aggregate guard steps, local MR review wiring, and tests for the local-flow checker surface.

#### Scenario: Local-flow script backing is checked
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` runs
- **THEN** implemented rules SHALL exist for `post-plan-execution-governance-package` and `complete-local-flow-to-remote-gate`
- **AND** `python tools/run_openspec_guard.py --root . --json` SHALL include `check_local_flow_scripted_enforcement`
