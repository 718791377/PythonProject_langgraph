## MODIFIED Requirements

### Requirement: Activation traces SHALL expose full orchestration state
The user-level orchestration activation policy SHALL require activation traces to report task phase, capability-chain state, default durable backend, backend readiness, expert selection, durable workflow state, persistent-team state, and a concrete reason.

The trace vocabulary SHALL distinguish `not_needed`, `candidate`, `selected`, `blocked`, and `running`.

The repository SHALL provide an executable trace-evidence validator that can inspect saved activation trace text for required fields, capability-chain consistency, backend readiness semantics, durable workflow and persistent-team vocabulary, forbidden missing-reminder reasons, and expert-timeout evidence labels.

#### Scenario: Startup or continue emits an activation trace
- **WHEN** a Codex session starts, reloads, resumes, receives `continue`, changes task phase, detects durable state, or expands to two or more execution slices
- **THEN** the activation trace SHALL include `capability_chain`, `backend_default`, `backend_ready`, `experts`, `durable_workflow`, `persistent_team`, and `why`
- **AND** the trace SHALL explain the concrete threshold or blocker instead of citing missing user requests

#### Scenario: Saved trace evidence is checked
- **WHEN** a saved activation trace is passed to the repository trace-evidence validator
- **THEN** the validator SHALL fail if any required trace field is missing
- **AND** it SHALL fail if capability-chain dependency states are inconsistent
- **AND** it SHALL fail if durable workflow or persistent-team states use unsupported vocabulary
- **AND** it SHALL fail if expert timeout language is presented without a non-evidence, bounded-wait, respawn, durable-handoff, or main-session-takeover label
