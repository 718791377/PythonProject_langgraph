## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose multi-interrupt approval-queue posture for tracked threads

The user-level LangGraph backend SHALL expose bounded multi-interrupt approval-queue posture for tracked threads instead of collapsing every approval need into one generic interrupt record.

At minimum the backend SHALL be able to report:

- stable interrupt item identity
- queue ordering posture
- pending versus resolved item posture
- bounded resume-mapping posture when present

#### Scenario: Operator inspects a tracked thread with multiple pending interrupts

- **WHEN** a tracked LangGraph thread has surfaced multiple interrupt items in one invocation
- **THEN** the backend SHALL preserve ordered approval-queue posture in durable state
- **AND** it SHALL not collapse that state into one undifferentiated interrupt record

### Requirement: The LangGraph backend SHALL keep explicit resume mapping for multi-interrupt continuation

The user-level LangGraph backend SHALL keep explicit resume mapping for multi-interrupt continuation instead of treating later resume intent as queue-unaware thread state only.

#### Scenario: Operator resumes one item in a multi-interrupt queue

- **WHEN** the operator provides resume input for a tracked thread with multiple interrupt items
- **THEN** the backend SHALL preserve which interrupt item that resume input addresses
- **AND** it SHALL keep that resume mapping inspectable
