## ADDED Requirements

### Requirement: Project MOE GUI Plan Uses Executable Implementation Structure

The Project MOE Agent GUI implementation plan SHALL use an executable-plan structure aligned with the newer Pi sidecar plan while preserving Project MOE-specific contracts and boundaries.

#### Scenario: Structure-aligned plan remains domain-specific

- **GIVEN** the plan is rewritten into the newer structure
- **WHEN** an implementer reads it
- **THEN** it exposes goals, architecture, source-of-truth, contracts, gates, rollback, risks, and self-check sections
- **AND** it still preserves Phase 1/Phase 2, Ready/Bootstrap/Repair lanes, target-project install boundaries, JSON state contracts, and Project MOE privacy rules.
