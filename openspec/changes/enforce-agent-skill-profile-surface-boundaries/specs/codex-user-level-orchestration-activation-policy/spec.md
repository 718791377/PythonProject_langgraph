## ADDED Requirements

### Requirement: Agent skill and profile surfaces SHALL remain distinct

The orchestration activation policy SHALL keep native Codex agents, workflow skills, plugin-provided skills, plugin modules, and profile helpers as distinct surfaces, and SHALL reject evidence that treats skill/profile invocation as native subagent or expert-result evidence.

#### Scenario: Repository policy surfaces distinguish execution surfaces

- **GIVEN** the repository OpenSpec guard runs
- **WHEN** it checks orchestration activation policy surfaces
- **THEN** the policy surfaces SHALL state that native agents are loaded from agent TOMLs, skills are loaded from `SKILL.md`, profile helpers change visible procedural context only, and skill/profile invocation is not expert evidence.

#### Scenario: Evidence rejects skill or profile claims as expert evidence

- **GIVEN** a saved routing report is checked
- **WHEN** it claims a skill invocation or plugin profile load as an expert returned result, native subagent, worker, or durable-team evidence
- **THEN** the checker SHALL fail that evidence unless it separately identifies an actual expert result, durable checkpoint, or local verification source.
