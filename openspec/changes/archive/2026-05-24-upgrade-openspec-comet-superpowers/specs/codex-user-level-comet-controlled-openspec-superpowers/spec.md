# codex-user-level-comet-controlled-openspec-superpowers Specification

## Purpose
Define how this repository adopts the Comet pattern as a governance target for OpenSpec work: OpenSpec remains the WHAT/spec-lifecycle authority, Superpowers supplies HOW/development-methodology practices, and Comet is the stateful control layer that coordinates phases, guards, resume, and archive evidence.

## ADDED Requirements

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
