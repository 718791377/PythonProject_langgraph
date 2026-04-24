## ADDED Requirements

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
