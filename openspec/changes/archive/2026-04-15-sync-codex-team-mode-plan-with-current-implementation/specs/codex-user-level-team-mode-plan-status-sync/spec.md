## ADDED Requirements

### Requirement: The canonical bilingual team-mode implementation plan SHALL reflect current implementation state
The canonical bilingual implementation plan for the Codex / oh-my-codex user-level team-mode workflow SHALL distinguish clearly among:

- implemented current state
- optional advanced paths
- future work

It SHALL NOT continue to label already-landed user-level surfaces as merely planned once those surfaces are available and validated.

#### Scenario: A capability batch has already landed
- **WHEN** a user-level team-mode capability has been implemented, validated, and incorporated into the current operator surface
- **THEN** the canonical implementation plan SHALL describe it as implemented current state
- **AND** it SHALL not leave that capability marked as only planned

### Requirement: The bilingual team-mode implementation plan SHALL remain semantically aligned
The English and Chinese implementation plan files SHALL remain semantically aligned on current state, optional state, and future state.

#### Scenario: One language file is updated after implementation lands
- **WHEN** the implementation plan in one language is updated to reflect a new current state
- **THEN** the paired language file SHALL be updated to match the same state classification
- **AND** the bilingual pair SHALL not leave conflicting implementation-status meanings in place
