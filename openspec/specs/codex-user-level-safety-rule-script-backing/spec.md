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
- **THEN** implemented rules SHALL exist for `post-plan-execution-governance-package` - the `/plan`-exit governance workflow policy rule - and `complete-local-flow-to-remote-gate` - the local-main-first gate condition rule
- **AND** `python tools/run_openspec_guard.py --root . --json` SHALL include `check_local_flow_scripted_enforcement`

### Requirement: Spec Kit authority guard SHALL validate generated surfaces and subordinate dry-run receipts

The repository SHALL keep Spec Kit below Comet, OpenSpec, Superpowers, local-main-first gates, and remote-publication gates by enforcing generated-surface and runtime-receipt checks before any Spec Kit surface can be treated as repository evidence.

`tools/check_spec_kit_authority_guard.py` SHALL fail closed on `.specify/`, root `specs/`, generated `.codex/commands/*speckit*`, generated `.codex/skills/*speckit*`, generated `.github/prompts/*speckit*`, `/speckit.*`, `$speckit-*`, extension, preset, and workflow-output surfaces unless a separate active authority-migration plan explicitly owns the change. Any `specify init` or `specify self check` command evidence SHALL remain blocked subordinate command evidence unless that same authority-migration plan explicitly owns the command boundary.

The repository SHALL provide `tools/spec_kit_subordinate_runtime.py` as a dry-run-only subordinate helper. The helper SHALL only support `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run`, SHALL reject live or apply mode names, SHALL NOT run live `specify`, SHALL NOT create `.specify/` or root `specs/`, and SHALL NOT write generated command, skill, prompt, extension, preset, or workflow-output surfaces.

Spec Kit subordinate runtime receipts SHALL include `dry_run_only=true`, `source_url`, `source_pin`, `authority_decision`, and `surface_status`. For R4, `authority_decision.decision` SHALL be only `blocked` or `subordinate`, SHALL record the winning authority layer, and SHALL preserve the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

#### Scenario: Generated Spec Kit command surface is blocked

- **WHEN** a changed or present repository path contains `.codex/commands/speckit.plan.md`
- **AND** no active Spec Kit authority-migration plan owns that generated command surface
- **THEN** `python tools/check_spec_kit_authority_guard.py --root . --json` SHALL fail

#### Scenario: Dry-run subordinate receipt is accepted

- **WHEN** `tools/spec_kit_subordinate_runtime.py probe --root <repo> --receipt-out <receipt>` writes a dry-run receipt
- **AND** the receipt records `authority_decision.decision=subordinate`, `dry_run_only=true`, source evidence, and complete surface status
- **THEN** `python tools/check_spec_kit_authority_guard.py --root <repo> --receipt <receipt> --json` SHALL pass

#### Scenario: Live or apply mode is rejected

- **WHEN** an operator requests `tools/spec_kit_subordinate_runtime.py apply-live --root <repo>`
- **THEN** the helper SHALL reject the mode before building a runtime payload
- **AND** it SHALL NOT run live Spec Kit commands or create generated Spec Kit surfaces
