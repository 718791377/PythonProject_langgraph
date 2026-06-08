## ADDED Requirements

### Requirement: Durable routing R4 smoke receipts SHALL prove smoke-tested status without adoption

The repository SHALL provide a read-only R4 durable routing smoke runner and a receipt checker before any future apply-mode adoption helper claims selected, running, adopted, or released durable workflow state.

The runner SHALL execute only bounded safe local checker commands by default, write one explicit receipt path, and record sanitized evidence for `runtime_stage=R4` and `stage=smoke-tested`. The receipt SHALL include timeout release evidence, rollback readiness, bounded transcript hashes or redacted excerpts, backend-family evidence, and explicit false values for adoption, mutation, durable-team launch, `omx-team-auto.ps1 -Apply`, LangGraph thread start, and remote publication authorization.

The checker SHALL fail closed if a receipt claims adoption, selected/running/adopted durable workflow state, user-level mutation, durable-state mutation, durable-team launch, apply-mode execution, LangGraph thread start, remote publication authorization, unbounded raw transcript evidence, timeout failure, missing rollback readiness, or unsafe backend-family evidence.

#### Scenario: R4 smoke success remains non-adoption evidence

- **WHEN** `tools/run_durable_routing_smoke.py` writes a passing R4 smoke receipt for a bounded safe local checker command
- **THEN** `tools/check_durable_routing_smoke_receipts.py --receipt <path> --json` SHALL report the receipt valid
- **AND** the receipt summary SHALL identify `runtime_stage=R4` and `stage=smoke-tested`
- **AND** it SHALL NOT report selected, running, adopted, or launched durable workflow state
- **AND** it SHALL report `adoption_performed=false`, `mutation_allowed=false`, `durable_team_launched=false`, `omx_apply_performed=false`, `langgraph_thread_started=false`, and `remote_publication_authorized=false`.

#### Scenario: Adoption or apply markers fail closed

- **GIVEN** an R4 smoke receipt claims adoption, selected/running/adopted durable workflow state, `omx-team-auto.ps1 -Apply`, LangGraph thread start, user-level mutation, or remote publication authorization
- **WHEN** the receipt checker runs
- **THEN** it SHALL fail closed with sanitized blocker codes
- **AND** it SHALL NOT treat smoke success as durable workflow adoption.
