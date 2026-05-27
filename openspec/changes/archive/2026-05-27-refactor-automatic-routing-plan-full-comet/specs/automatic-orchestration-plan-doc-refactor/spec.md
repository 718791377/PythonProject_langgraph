## ADDED Requirements

### Requirement: Full Comet traceability for automatic routing plan refactors

The repository SHALL keep full `/comet` refactors of the automatic orchestration routing enforcement plan traceable without implying runtime enforcement has changed.

#### Scenario: Full workflow documentation refactor

- **WHEN** a user asks to refactor `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` according to complete `/comet`
- **THEN** the repository records a full OpenSpec change with proposal, design, tasks, and delta spec
- **AND** the repository records Superpowers design and implementation-plan artifacts
- **AND** the target plan identifies those artifacts and states the refactor is documentation-only

#### Scenario: Runtime evidence boundary is preserved

- **WHEN** the refactor updates plan structure or reading paths
- **THEN** the document keeps Phase 0-3 completion separate from Phase 4 planned follow-up
- **AND** the document does not claim that durable teams, persistent teams, LangGraph workflows, or native experts ran
- **AND** the document does not treat LangGraph backend readiness as persistent team runtime evidence

#### Scenario: Comet shell helper unavailable

- **WHEN** Comet shell scripts cannot run because `bash` is unavailable in the current Windows shell
- **THEN** the change records the blocker explicitly
- **AND** validation uses OpenSpec artifacts and repository checks as fallback evidence
- **AND** reports must not claim `comet-state.sh` or `comet-guard.sh` transitions succeeded

#### Scenario: Bilingual companion alignment

- **WHEN** the Chinese implementation plan receives a full Comet framing update
- **THEN** the English companion receives matching high-level framing in the same batch unless a future user explicitly approves a temporary exception
