## ADDED Requirements

### Requirement: The installer SHALL generate LangGraph durable orchestration entrypoints
The installer SHALL generate additive LangGraph-oriented durable orchestration entrypoints into the target Codex home.

The generated LangGraph asset set SHALL include operator surfaces for at least:

- run or start
- status or inspect
- resume
- interrupt inspection

The generated playbook SHALL document how these LangGraph entrypoints relate to the existing `omx team` entrypoints.

#### Scenario: Operator inspects generated LangGraph entrypoints
- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate additive LangGraph entrypoint assets there
- **AND** the generated playbook SHALL explain how they coexist with the existing `omx team` wrappers
