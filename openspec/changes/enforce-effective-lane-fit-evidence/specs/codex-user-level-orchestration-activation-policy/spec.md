## MODIFIED Requirements

### Requirement: Native Codex SHALL remain the base layer and durable lanes SHALL be task-fit choices

Native Codex SHALL remain the base layer. oh-my-codex, native_omx, skills, profile helpers, and LangGraph SHALL be described as additive workflow or durable-state layers, not as Codex replacements. A durable task SHALL use one backend family at a time. Worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control SHALL justify `native_omx`; graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues SHALL justify LangGraph.

Effective lane-fit evidence SHALL be script-checkable. The repository SHALL provide `tools/check_effective_lane_fit_evidence.py` to validate repository policy surfaces and saved run-summary evidence for `native_omx` worker-centric fit, LangGraph graph-shaped fit, default-backend-not-enough decisions, and explicit close/handoff before backend-family switching.

#### Scenario: Effective lane differs from default backend

- **WHEN** LangGraph is ready but the task is worker-centric
- **THEN** activation MAY select `native_omx` as the effective lane with a named worker-centric reason
- **AND** it SHALL NOT mix `native_omx` worker lifecycle with LangGraph checkpoint state without explicit close or handoff
- **AND** saved lane-fit evidence SHALL pass `tools/check_effective_lane_fit_evidence.py`

#### Scenario: LangGraph lane is selected for graph-shaped work

- **WHEN** a durable task selects LangGraph as the effective lane
- **THEN** the evidence SHALL cite graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, persisted survivor queues, or equivalent graph-shaped fit
- **AND** it SHALL NOT rely only on `backend_default=langgraph` or backend readiness as the task-level adoption reason

#### Scenario: Backend family switching is explicit

- **WHEN** saved evidence mentions both `native_omx` and LangGraph in one durable task flow
- **THEN** it SHALL show one backend family for the active task or record explicit close/handoff before switching
- **AND** it SHALL fail lane-fit evidence if the switch is silent or implicit
