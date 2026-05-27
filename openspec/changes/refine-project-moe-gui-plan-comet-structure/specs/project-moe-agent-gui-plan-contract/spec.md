## ADDED Requirements

### Requirement: Project MOE GUI Plan Uses Full Comet Executable Structure

The Project MOE Agent GUI implementation plan SHALL use a full Comet executable-plan structure that separates documentation readiness, target-project readiness, GUI runtime completion, local integration, and remote publication authorization.

#### Scenario: Plan structure is implementation-slicing ready

- **GIVEN** an implementer opens `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`
- **WHEN** they review the plan before code implementation
- **THEN** the plan exposes goal, architecture, relationship model, source-of-truth, install artifacts, CLI contract, GUI contract, JSON state model, readiness lanes, safety rules, rollback rules, verification path, implementation tasks, risk decisions and self-checks
- **AND** it does not claim target projects are GUI-ready without readiness evidence.

#### Scenario: Runtime capability is not overstated

- **GIVEN** the plan is structurally ready
- **WHEN** a target project only has static Phase 1 evidence or blockers
- **THEN** the plan keeps that target project in Ready-candidate or Repair Lane
- **AND** `control_mode_allowed` remains false until the target project's readiness checker proves ready.

#### Scenario: Comet script evidence is honest

- **GIVEN** the current Windows shell cannot run Comet `.sh` scripts
- **WHEN** the change records Comet state
- **THEN** the state records the script blocker and uses OpenSpec/repository gates as fallback evidence
- **AND** it does not claim `comet-state.sh` or `comet-guard.sh` passed.
