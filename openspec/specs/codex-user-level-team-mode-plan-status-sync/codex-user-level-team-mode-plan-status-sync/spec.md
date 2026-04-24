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
