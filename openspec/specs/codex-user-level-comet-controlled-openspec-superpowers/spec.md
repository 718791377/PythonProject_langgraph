# codex-user-level-comet-controlled-openspec-superpowers Specification

## Purpose
Define how this repository adopts the Comet pattern as a governance target for OpenSpec work: OpenSpec remains the WHAT/spec-lifecycle authority, Superpowers supplies HOW/development-methodology practices, and Comet is the stateful control layer that coordinates phases, guards, resume, and archive evidence.
## Requirements
### Requirement: Comet-controlled workflow SHALL preserve layer boundaries

The repository SHALL describe the Comet-style workflow as an additive control layer over OpenSpec and Superpowers rather than a replacement for either project.

OpenSpec SHALL remain the WHAT layer for proposal, delta specs, tasks, spec lifecycle, validation, and archive/sync authority. Superpowers SHALL remain the HOW layer for brainstorming, technical design, implementation planning, TDD, subagent-driven development, code review, and branch finishing. Comet SHALL be described as the orchestrating control layer for phase dispatch, workflow state, transition guards, resume, and evidence gates.

#### Scenario: Operator reviews the workflow boundary
- **WHEN** the operator reads the Comet/OpenSpec/Superpowers workflow policy
- **THEN** the policy SHALL identify OpenSpec as WHAT, Superpowers as HOW, and Comet as the control layer
- **AND** it SHALL state that Comet does not replace OpenSpec, Superpowers, native Codex subagents, native_omx, or LangGraph

#### Scenario: Skill or profile evidence is evaluated
- **WHEN** the workflow references OpenSpec skills, Superpowers skills, or Comet skills
- **THEN** the repository SHALL continue to treat those skills as workflow instruction surfaces
- **AND** it SHALL NOT treat a skill or profile invocation as native subagent evidence

### Requirement: Comet-controlled workflow SHALL define a five-phase pipeline

The repository SHALL define the Comet-style full workflow as Open -> Design -> Build -> Verify -> Archive.

The phase ownership model SHALL be: OpenSpec owns Open and Archive, Superpowers owns Design and Build, and both layers participate in Verify.

#### Scenario: Full workflow is documented
- **WHEN** a maintainer reads the workflow policy
- **THEN** the five phases SHALL be visible with their owner and expected artifacts
- **AND** the policy SHALL identify proposal/spec/tasks artifacts, design documents, implementation plans, verification reports, branch handling, delta-to-main spec sync, and archive state

#### Scenario: Preset workflow is documented
- **WHEN** hotfix or tweak flow is discussed
- **THEN** skipped deep-design or full-plan steps SHALL be explicit
- **AND** verification and archive evidence SHALL remain mandatory unless a later OpenSpec change explicitly defines a narrower accepted exception

### Requirement: Comet-controlled workflow SHALL map PMBOK8 Project Management Focus Areas

The repository SHALL map the Comet state machine to PMBOK8 Project Management Focus Areas without replacing the five-phase Comet workflow or making the focus areas a prescriptive waterfall sequence.

The mapping SHALL be Open = Initiating, Design = Planning, Build = Executing, Verify = Controlling, and Archive = Closing. Monitoring SHALL be documented as a cross-cutting focus area implemented through phase detection, transition guards, evidence gates, verify-fail feedback, archive readiness checks, and explicit operator decisions; it SHALL NOT become a sixth Comet phase.

#### Scenario: PMBOK8 focus areas are documented
- **WHEN** the operator reads the Comet/OpenSpec/Superpowers workflow policy
- **THEN** the policy SHALL show the Open/Design/Build/Verify/Archive mapping to Initiating/Planning/Executing/Controlling/Closing
- **AND** it SHALL describe Monitoring as cross-cutting, non-prescriptive, recurring, overlapping, and tailorable across the workflow

### Requirement: Comet runtime SHALL support iterative management returns

The Comet runtime SHALL implement management focus areas as executable state and evidence checks rather than only as documentation labels.

Each active change SHALL have a management record with checklist evidence for Open, Design, Build, Verify, Archive, and the cross-cutting Monitoring loop. Monitoring SHALL be able to record a control decision that returns work from the current phase to `open`, `design`, `build`, or `verify` when earlier evidence is incomplete or assumptions change.

The runtime SHALL return work from the current phase to `open`, `design`, `build`, or `verify` through an explicit Monitoring transition rather than by silently editing phase metadata.

Return transitions SHALL preserve the rework reason and increment an iteration counter. Monitoring SHALL NOT become a sixth phase, and the runtime field names SHALL NOT depend on the literal `PMBOK8` term.

#### Scenario: Monitoring returns work to an earlier focus area
- **WHEN** verification discovers that design assumptions are incomplete
- **THEN** the runtime SHALL allow a recorded return to the design phase
- **AND** it SHALL preserve the rework reason and iteration count before forward progress resumes

#### Scenario: Forward transition lacks management evidence
- **WHEN** a phase guard runs and required checklist evidence is missing
- **THEN** the guard SHALL fail closed
- **AND** it SHALL identify the missing management evidence instead of advancing only because phase files exist

### Requirement: Comet-controlled workflow SHALL use decoupled state and resume evidence

The repository SHALL describe separate OpenSpec and Comet state surfaces for Comet-style adoption.

`.openspec.yaml` or the installed OpenSpec equivalent SHALL own spec lifecycle and change metadata. `.comet.yaml` or a repository-approved equivalent SHALL own workflow phase, workflow preset, design/plan/report references, build decisions, isolation decisions, verification result, branch handling, and archive state.

#### Scenario: Interrupted work is resumed
- **WHEN** a Comet-style workflow is resumed after interruption
- **THEN** the workflow SHALL use persisted state to identify the active change and current phase
- **AND** it SHALL NOT rely only on chat history or unchecked markdown inference

#### Scenario: Multiple active changes exist
- **WHEN** a resume/status command finds multiple active changes
- **THEN** the operator SHALL be asked to select the intended change before stateful execution continues

### Requirement: Comet-controlled workflow SHALL guard phase transitions with executable checks

The repository SHALL require script-backed phase-transition checks before Comet-style phases advance.

The guard surface SHALL fail closed for missing artifacts, invalid state values, illegal phase jumps, missing build/isolation choices, missing verification reports, unhandled branch status, and archive attempts before verification passes.

#### Scenario: Guard detects missing evidence
- **WHEN** a phase transition lacks a required artifact, verification report, or branch-handling state
- **THEN** the guard SHALL stop the transition
- **AND** it SHALL provide an actionable hard-stop message or equivalent structured failure

#### Scenario: Full workflow tries direct build without override
- **WHEN** the full workflow records `build_mode: direct`
- **THEN** a guard SHALL require an explicit `direct_override` or equivalent recorded exception before the workflow can leave the build phase

### Requirement: Comet-controlled workflow SHALL keep archive evidence authoritative

The repository SHALL preserve the existing verify-before-archive rule for Comet-style workflow adoption.

Archive SHALL require completed tasks, validation evidence, an existing verification report, handled branch status, and delta-to-main spec synchronization before an OpenSpec change is treated as complete.

#### Scenario: Archive is requested without verification evidence
- **WHEN** archive is requested and the verification report is missing or branch status is not handled
- **THEN** the workflow SHALL block archive
- **AND** it SHALL keep the change active until the missing evidence is produced

#### Scenario: Archive succeeds
- **WHEN** archive completes for a Comet-style workflow
- **THEN** the stable specs SHALL reflect approved deltas
- **AND** the change SHALL move to archive history with state indicating archive completion

### Requirement: Comet adoption SHALL be explicit and repository-local before runtime installation

The repository SHALL treat this first upgrade as governance and validation for a Comet-style control layer, not as permission to mutate user-level tools or consumer projects.

Installing `@rpamis/comet`, running `comet init`, installing Superpowers, or overwriting generated platform skills SHALL require explicit operator approval or a later OpenSpec change that defines the exact write scope and rollback plan.

#### Scenario: Maintainer wants to install Comet
- **WHEN** a maintainer proposes `npm install -g @rpamis/comet` or `comet init`
- **THEN** the workflow SHALL require explicit approval and a scoped write plan
- **AND** it SHALL preview whether writes are project-local, user-level, or global before applying them

#### Scenario: Consumer project impact is considered
- **WHEN** Comet/OpenSpec/Superpowers governance is updated in this repository
- **THEN** the update SHALL NOT mutate consumer repositories outside `D:\PythonProject_langgraph`, generic project-root workspaces outside this repository, or their `.omx/state` directories
- **AND** any later consumer-project rollout SHALL keep repo-local durable truth in that consumer project

### Requirement: Comet runtime adoption SHALL be explicit, backed up, and reversible

When this repository moves from Comet governance into actual runtime installation or user-level Codex mutation, the adoption SHALL record explicit operator approval, backup paths, write scope, validation evidence, and rollback instructions before the change is treated as complete.

#### Scenario: Operator approves runtime adoption
- **WHEN** the operator asks to install `@rpamis/comet`, run `comet init`, or edit user-level Codex configuration
- **THEN** the workflow SHALL record that request in an OpenSpec change or equivalent durable evidence
- **AND** it SHALL define the allowed write scope before mutation

#### Scenario: User-level Codex configuration is edited
- **WHEN** `C:\Users\lenovo\.codex\config.toml` is changed for Comet adoption
- **THEN** a timestamped backup SHALL exist before the edit
- **AND** the evidence SHALL describe the exact intended config delta and rollback source

#### Scenario: Comet initialization writes skills or scripts
- **WHEN** `comet init` installs or updates Codex/OpenSpec/Superpowers/Comet skills
- **THEN** the workflow SHALL capture the generated or changed paths when available
- **AND** existing skills SHALL be skipped or backed up before overwrite

#### Scenario: Runtime adoption is verified
- **WHEN** installation and initialization complete
- **THEN** the workflow SHALL run Comet status or doctor checks when available
- **AND** repository OpenSpec validation SHALL still pass

### Requirement: Comet workflow governance SHALL be checker-backed

The repository SHALL include an executable checker that verifies the registered bilingual governance surface for the Comet-controlled OpenSpec + Superpowers workflow.

The checker SHALL validate the English and Chinese policy paths, the docs registry entry, and core boundary terms for Comet, OpenSpec, Superpowers, WHAT/HOW, five phases, decoupled state, guards, resume, and no implicit runtime installation.

#### Scenario: Policy surface is intact
- **WHEN** the checker runs against the repository
- **THEN** it SHALL report success with JSON fields for checked files and required terms

#### Scenario: Policy surface drifts
- **WHEN** a policy file, registry entry, or required boundary term is missing
- **THEN** the checker SHALL report a blocking error
- **AND** the repository guard SHALL fail when the checker is part of the guard run

### Requirement: Post-plan execution SHALL start with a docs_bilingual governance package

When a confirmed `/plan` exits into execution and the next task is not documentation-only, the repository SHALL create or update the local governance package before runtime or code implementation begins.

The package SHALL update `docs_bilingual/` first, using the most suitable document class and directory. Existing `docs_bilingual/` files SHALL be updated before creating a new file when they can cleanly carry the decision. The repository SHALL NOT treat `implementation_plans/` as the only valid `docs_bilingual/` destination.

OpenSpec artifacts and `docs/` artifacts SHALL be derived from the `docs_bilingual/` decision. The repository SHALL update `openspec/` only when durable capability, spec lifecycle, structural governance, or stable requirement evidence is needed. It SHALL update `docs/` only when Superpowers runtime artifacts or the `docs/` directory contract itself need changes.

#### Scenario: Non-documentation implementation follows `/plan`
- **WHEN** the user asks the session to implement a confirmed plan for a non-documentation-only task
- **THEN** the session SHALL first update the appropriate `docs_bilingual/` governance, guide, memory, product-lifecycle, or implementation-plan surface
- **AND** it SHALL complete the local governance package through local `main` integration before code or runtime implementation continues

#### Scenario: docs_bilingual update does not imply OpenSpec or docs files
- **WHEN** a `docs_bilingual/` update fully captures the local governance decision
- **THEN** the session SHALL NOT create `openspec/` or `docs/` artifacts only because `docs_bilingual/` changed
- **AND** any additional `openspec/` or `docs/` file SHALL be justified by the task content itself

### Requirement: Post-plan governance flow SHALL be enforced by local range checks
The repository SHALL keep a script-backed range check for post-`/plan` non-document execution. The check SHALL require the first commit in a non-document execution range to be a docs-only local governance package that touches `docs_bilingual/` first.

Local MR review SHALL run that range check before local `main` integration. The aggregate OpenSpec guard SHALL run a static local-flow checker that verifies the range checker, complete local-flow helper, policy documents, and CI test registrations remain wired.

#### Scenario: Non-document execution branch skips the governance package
- **WHEN** a feature branch contains non-document changes and the first commit does not update `docs_bilingual/`
- **THEN** `tools/check_plan_exit_execution_governance.py` SHALL fail for that range
- **AND** `tools/ci/local_mr_review.ps1` SHALL block local integration
