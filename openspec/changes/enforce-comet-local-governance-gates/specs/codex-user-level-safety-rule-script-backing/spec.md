## ADDED Requirements

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
