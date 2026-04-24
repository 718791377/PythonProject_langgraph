# Codex User-Level Team Mode Plan Status Sync

## Purpose

Keep the canonical bilingual Codex / oh-my-codex user-level team-mode implementation plan aligned with the current implemented state, optional advanced paths, and true future work boundaries.
## Requirements
### Requirement: The canonical bilingual team-mode implementation plan SHALL reflect current implementation state

The canonical bilingual implementation plan for the Codex / oh-my-codex user-level team-mode workflow SHALL distinguish clearly among:

- implemented current state
- optional advanced paths
- future work

It SHALL NOT continue to label already-landed user-level surfaces as merely planned once those surfaces are available and validated.

It SHALL also reflect current operator-facing interpretation when that interpretation is already installed and validated in the user-level startup-readable surfaces.

#### Scenario: A capability batch has already landed

- **WHEN** a user-level team-mode capability has been implemented, validated, and incorporated into the current operator surface
- **THEN** the canonical implementation plan SHALL describe it as implemented current state
- **AND** it SHALL not leave that capability marked as only planned

#### Scenario: Installed user-level operator guidance already exists

- **WHEN** the current user-level installation already exposes an operator-facing interpretation through installed startup-readable surfaces such as routing-policy output, the leader profile, or the team-mode playbook
- **THEN** the canonical implementation plan SHALL describe that interpretation as current state rather than future direction
- **AND** it SHALL not leave the same interpretation framed as not yet landed

### Requirement: The bilingual team-mode implementation plan SHALL remain semantically aligned

The English and Chinese implementation plan files SHALL remain semantically aligned on:

- current state
- optional state
- future state
- operator-facing interpretation already installed at user level

#### Scenario: One language file is updated after implementation lands

- **WHEN** the implementation plan in one language is updated to reflect a new current state
- **THEN** the paired language file SHALL be updated to match the same state classification
- **AND** the bilingual pair SHALL not leave conflicting implementation-status meanings in place

#### Scenario: User-level orchestration guidance is clarified in one language

- **WHEN** one language file updates operator-facing interpretation for already-installed user-level behavior such as layered capability meaning, effective-lane meaning, or provider-pacing interpretation
- **THEN** the paired language file SHALL be updated to preserve the same operator-facing meaning
- **AND** the bilingual pair SHALL not split current user-level guidance across conflicting semantic classifications

### Requirement: The LangGraph capability-gap narrative SHALL reflect validated current implementation state

When LangGraph capability work has already landed and passed repository validation, the canonical bilingual implementation plan and startup-facing repository narrative SHALL reflect that landed state instead of leaving those surfaces framed as still planned.

At minimum this sync SHALL preserve a truthful distinction among:

- already implemented current state
- still bounded or still not fully generalized current state
- genuinely unimplemented future work

#### Scenario: LangGraph appendix still lists already-landed surfaces as future work

- **WHEN** the current bilingual implementation plan still places already-implemented LangGraph surfaces in a future-work section
- **THEN** the plan-status sync process SHALL move those surfaces into current-state classification
- **AND** it SHALL keep only genuinely unlanded LangGraph gaps in the future-work section

#### Scenario: Startup-facing summary still points at a completed sync pass as next work

- **WHEN** a startup-facing repository summary still treats the capability-gap sync pass as pending after that sync has been completed
- **THEN** the plan-status sync process SHALL update that startup-facing narrative
- **AND** it SHALL not leave a completed sync pass presented as the next unfinished priority

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after each closed LangGraph-deepening wave

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated current LangGraph capability surface rather than stale in-flight wording.

#### Scenario: A LangGraph-deepening mainline is archived after validation

- **WHEN** a LangGraph-deepening mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived mainline as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived fuller live-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the fuller live primary-execution-engine step has landed.

#### Scenario: The fuller live-engine mainline is archived after validation

- **WHEN** the fuller live `StateGraph` primary execution-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived fuller live-engine rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived richer automatic runtime-policy rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the richer automatic runtime-policy step has landed.

#### Scenario: The automatic runtime-policy mainline is archived after validation

- **WHEN** the richer automatic runtime-policy mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived automatic-policy rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived deeper live-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the deeper live primary-engine step has landed.

#### Scenario: The deeper live-engine mainline is archived after validation

- **WHEN** the deeper live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived deeper live-engine rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived broader automatic runtime-policy rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the broader automatic runtime-policy step has landed.

#### Scenario: The broader automatic runtime-policy mainline is archived after validation

- **WHEN** the broader automatic runtime-policy mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived broader automatic-policy rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived superstep live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the superstep live primary-engine step has landed.

#### Scenario: The superstep live primary-engine mainline is archived after validation

- **WHEN** the superstep live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived superstep live-engine rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived stateful live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the stateful live primary-engine step has landed.

#### Scenario: The stateful live primary-engine mainline is archived after validation

- **WHEN** the stateful live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived stateful live-engine rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived graph-resident boundary-state live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the graph-resident boundary-state live primary-engine step has landed.

#### Scenario: The graph-resident boundary-state live primary-engine mainline is archived after validation

- **WHEN** the graph-resident boundary-state live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived graph-resident boundary-state rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived subgraph-aware handoff-state live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the subgraph-aware handoff-state live primary-engine step has landed.

#### Scenario: The subgraph-aware handoff-state live primary-engine mainline is archived after validation

- **WHEN** the subgraph-aware handoff-state live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived subgraph-aware handoff-state rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived approval-aware resume-state live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the approval-aware resume-state live primary-engine step has landed.

#### Scenario: The approval-aware resume-state live primary-engine mainline is archived after validation

- **WHEN** the approval-aware resume-state live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived approval-aware resume-state rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived recovery-aware provenance-state live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the recovery-aware provenance-state live primary-engine step has landed.

#### Scenario: The recovery-aware provenance-state live primary-engine mainline is archived after validation

- **WHEN** the recovery-aware provenance-state live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived recovery-aware provenance-state rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived durable-artifact-aware live primary-engine rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the durable-artifact-aware live primary-engine step has landed.

#### Scenario: The durable-artifact-aware live-engine mainline is archived after validation

- **WHEN** the durable-artifact-aware live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived durable-artifact-aware rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived reducer-aware live primary-engine merge-state rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the reducer-aware live primary-engine merge-state step has landed.

#### Scenario: The reducer-aware live-engine mainline is archived after validation

- **WHEN** the reducer-aware live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived reducer-aware rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived command-aware live primary-engine control-state rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the command-aware live primary-engine control-state step has landed.

#### Scenario: The command-aware live-engine mainline is archived after validation

- **WHEN** the command-aware live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived command-aware rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived runtime-aware live primary-engine context-store rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the runtime-aware live primary-engine context-store step has landed.

#### Scenario: The runtime-aware live-engine mainline is archived after validation

- **WHEN** the runtime-aware live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived runtime-aware rollout as the current active implementation wave

### Requirement: The repository SHALL resynchronize the LangGraph capability-gap narrative after the archived memory-aware live primary-engine semantic-state rollout

The bilingual implementation plan and startup-facing repository summaries SHALL track the validated LangGraph capability surface after the memory-aware live primary-engine semantic-state step has landed.

#### Scenario: The memory-aware live-engine mainline is archived after validation

- **WHEN** the memory-aware live primary-engine mainline has been implemented, validated, and archived
- **THEN** the repository SHALL update the capability-gap appendix and startup-facing summaries to reflect that new validated state
- **AND** it SHALL not continue to describe the archived memory-aware rollout as the current active implementation wave

