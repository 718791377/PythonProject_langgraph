## ADDED Requirements

### Requirement: Automatic durable routing SHALL honor the selected durable orchestration backend
The automatic durable routing layer SHALL honor the selected durable orchestration backend instead of assuming that every durable decision launches directly through the current native `omx team` path.

When the selected backend is `langgraph`, the planned durable execution result SHALL identify the LangGraph backend as the target durable path.

#### Scenario: Automatic routing plans LangGraph durable execution
- **WHEN** the durable orchestration backend selector is `langgraph`
- **AND** the task meets durable execution thresholds
- **THEN** the automatic durable routing plan SHALL identify LangGraph as the selected backend
- **AND** it SHALL not misreport the decision as a direct `omx team` launch
