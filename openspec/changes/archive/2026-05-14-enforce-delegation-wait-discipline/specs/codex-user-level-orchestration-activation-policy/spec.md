## ADDED Requirements

### Requirement: Delegation and leader wait discipline SHALL be script-checkable

The orchestration activation policy SHALL require delegated expert or worker work to be concrete, bounded, self-contained, non-duplicative, and materially advancing while the current main Codex CLI session remains the leader.

The leader SHALL identify immediate critical-path local work before delegation, keep urgent blocking critical-path work local unless a handoff is explicitly recorded, continue meaningful non-overlapping leader work while experts run, and use `wait_agent` only when the next leader step is blocked by the delegated result.

The repository SHALL provide `tools/check_delegation_wait_discipline_evidence.py` to validate repository policy surfaces and saved run-summary or worker-brief evidence for delegation design, code-worker ownership, duplicate-work prevention, and leader wait discipline.

#### Scenario: Delegation evidence is validated

- **GIVEN** a saved run summary describes delegated expert or worker work
- **WHEN** the evidence checker is run against that summary
- **THEN** it SHALL fail if the summary omits immediate critical-path local work
- **AND** it SHALL fail if the delegated task is not described as concrete, bounded, self-contained sidecar work that materially advances the task
- **AND** it SHALL fail if duplicate-work prevention or non-overlapping ownership is missing
- **AND** it SHALL fail if code-changing worker delegation lacks file/module ownership, "not alone in the codebase" instructions, or changed-path reporting expectations

#### Scenario: Leader waits for delegated work

- **GIVEN** a saved run summary describes `wait_agent` or equivalent waiting for delegated work
- **WHEN** the evidence checker is run against that summary
- **THEN** it SHALL fail if the wait is indefinite, silent, or reflexive
- **AND** it SHALL require either meaningful non-overlapping leader work during the wait or a clear critical-path blocker explaining why the leader is blocked until the delegated result returns
