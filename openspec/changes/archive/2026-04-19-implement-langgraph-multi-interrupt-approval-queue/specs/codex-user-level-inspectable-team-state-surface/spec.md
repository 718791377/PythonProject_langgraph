## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project multi-interrupt approval-queue posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread with interrupt-queue metadata, the canonical inspectable durable-state surface SHALL expose LangGraph-specific approval-queue projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- queue size or bounded queue summary
- pending interrupt-item posture
- bounded resume-mapping posture when present
- the relevant approval-queue inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread with a queued approval backlog

- **WHEN** the current repository has a tracked LangGraph thread whose approval posture spans multiple interrupt items
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded approval-queue projection data
