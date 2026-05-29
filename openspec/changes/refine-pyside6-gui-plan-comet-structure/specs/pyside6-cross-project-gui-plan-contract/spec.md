## ADDED Requirements

### Requirement: PySide6 GUI Plan Uses Full Comet Executable Structure

The PySide6 cross-project GUI capability plan SHALL use a full Comet executable-plan structure that separates shared-runtime readiness, consumer-project GUI readiness, explicit high-impact trigger gates, local integration, and remote publication authorization.

#### Scenario: Plan structure is implementation-slicing ready

- **GIVEN** an implementer opens `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md`
- **WHEN** they review the plan before runtime or consumer-project work
- **THEN** the plan exposes relationship model, goals/non-goals, work boundary, runtime architecture, source of truth, helper contracts, state model, readiness gates, implementation items, verification path, rollback rules, risks and self-checks
- **AND** it does not claim that any consumer project is GUI-ready without target-project evidence.

#### Scenario: Runtime capability is not overstated

- **GIVEN** the shared runtime can import PySide6 on the local machine
- **WHEN** no named consumer project has passed preview and import-only smoke
- **THEN** the plan keeps the consumer project below `project_gui_verified_with_shared_runtime`
- **AND** visible GUI and packaging states remain false unless explicitly triggered and evidenced.

#### Scenario: High-impact actions remain explicit

- **GIVEN** the user says only "continue" or asks to continue this plan generically
- **WHEN** the next possible action is project-local override, visible GUI validation, or executable packaging
- **THEN** the plan requires a named target project and explicit reason before proceeding.

#### Scenario: Comet script evidence is honest

- **GIVEN** the current Windows shell cannot run Comet `.sh` scripts
- **WHEN** the change records Comet state
- **THEN** the state records the script blocker and uses OpenSpec/repository gates as fallback evidence
- **AND** it does not claim `comet-state.sh` or `comet-guard.sh` passed.
