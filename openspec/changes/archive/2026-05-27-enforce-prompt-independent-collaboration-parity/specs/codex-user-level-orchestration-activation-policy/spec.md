## ADDED Requirements

### Requirement: Prompt-independent collaboration parity SHALL be checker-backed

The repository SHALL provide `tools/check_orchestration_collaboration_evidenceguard.py` and prompt fixture pairs that prove equivalent tasks produce equivalent routing decisions with or without collaboration phrases.

The checker SHALL also validate cold-start read-order evidence, durable/persistent evidenceguard records, structured expert lifecycle audit events, and LangGraph state release evidence.

#### Scenario: Prompt-independent fixture pairs are checked

- **WHEN** the evidenceguard validates prompt-independent collaboration fixtures
- **THEN** paired cases with and without collaboration phrases SHALL produce the same route fields for the same task shape
- **AND** missing user reminders SHALL NOT appear as routing reasons

#### Scenario: Durable evidenceguard rejects over-claims

- **WHEN** a saved durable or persistent team claim is checked
- **THEN** selected, running, or complete claims SHALL fail unless the evidence required by the claimed state is present
- **AND** bare plans, skill invocations, timeouts, branch names, or `.omx` directory existence SHALL NOT count as runtime team evidence

#### Scenario: LangGraph release evidence is checked

- **WHEN** a completed LangGraph task is checked
- **THEN** stale `running` state SHALL fail unless completion or handoff release fields are recorded
