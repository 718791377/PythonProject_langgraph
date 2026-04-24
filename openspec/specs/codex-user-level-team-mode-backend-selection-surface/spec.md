# Codex User-Level Team Mode Backend Selection Surface

## Purpose

Define the primary user-level operator-facing surface for durable backend selection under Codex / oh-my-codex team mode.

This capability ensures operators can choose between `native_omx` and `langgraph` from installed user-level artifacts alone, while keeping repository-local OpenSpec specs and bilingual implementation plans as the development authority for evolving the policy.

## Requirements

### Requirement: The user-level installation SHALL expose a primary backend-selection policy surface

The user-level installation SHALL expose a primary operator-facing backend-selection policy surface under the user-level Codex home.

That primary surface SHALL answer at least:

- what backend is selected now
- what backend is the stable default
- when `native_omx` is preferred
- when `langgraph` is preferred
- whether backend-family switching is explicit or automatic
- whether one durable task may span multiple backend families

The primary surface SHALL identify supporting user-level policy views that repeat the same contract.

#### Scenario: Operator inspects the primary backend-selection surface

- **WHEN** the operator runs the generated backend status surface
- **THEN** it SHALL report the selected backend and the stable default
- **AND** it SHALL report preferred use cases for both `native_omx` and `langgraph`
- **AND** it SHALL report that backend-family switching stays explicit or manual-only
- **AND** it SHALL report that one durable task stays within one backend family

### Requirement: The user-level backend-selection surface SHALL distinguish operator authority from repository development authority

The user-level backend-selection surface SHALL state that user-level artifacts are the primary operator-facing source of truth for backend choice.

It SHALL also state that repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth for evolving the policy.

#### Scenario: Operator reads backend policy without reopening repository docs

- **WHEN** the operator reads the user-level backend-selection surface
- **THEN** the surface SHALL be sufficient to choose between `native_omx` and `langgraph`
- **AND** it SHALL still distinguish user-level operator guidance from repository-local development authority

### Requirement: The backend-selection surface SHALL evolve into effective-lane selection over enabled capabilities

The user-level backend-selection surface SHALL evolve from one global backend-family selector into an inspectable effective-lane selection surface over enabled capability layers.

It SHALL still preserve operator visibility into:

- current enabled capability layers
- current effective lane
- why that lane was selected

#### Scenario: Operator inspects a task flow while LangGraph is enabled but not selected

- **WHEN** LangGraph capability is enabled but the current task flow is routed to another effective lane
- **THEN** the user-level surface SHALL show that LangGraph remains enabled
- **AND** it SHALL still show the task-flow-specific effective lane separately
