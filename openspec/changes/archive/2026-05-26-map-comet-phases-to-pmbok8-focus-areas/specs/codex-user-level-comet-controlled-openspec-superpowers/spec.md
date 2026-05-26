# codex-user-level-comet-controlled-openspec-superpowers Specification Delta

## ADDED Requirements

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
