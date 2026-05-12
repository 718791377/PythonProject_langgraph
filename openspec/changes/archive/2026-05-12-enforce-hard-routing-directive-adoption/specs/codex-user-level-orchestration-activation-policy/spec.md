## ADDED Requirements

### Requirement: Hard routing directives SHALL require adoption or named blockers
The orchestration activation policy SHALL treat explicit requests for `omx` or `LangGraph` as hard routing directives for the current task flow.

When the capability chain, preflight, and task thresholds are satisfied, the session SHALL report the selected lane as `selected` or `running` and SHALL NOT remain in explanation-only mode. When the requested lane is not adopted, the trace SHALL report a named blocker or unmet threshold such as `blocked:backend_not_ready`, `blocked:preflight_failed`, `blocked:helper_missing`, `blocked:write_ownership_conflict`, or `threshold_not_met:no_frozen_plan`.

#### Scenario: Explicit directive is adopted
- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the capability chain, preflight, and task thresholds are satisfied
- **THEN** the activation trace SHALL report the requested lane as `selected` or `running`
- **AND** it SHALL NOT stay in explanation-only mode

#### Scenario: Explicit directive is blocked
- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the requested lane cannot be adopted
- **THEN** the activation trace SHALL report `blocked:<reason>` or `threshold_not_met:<reason>`
- **AND** it SHALL NOT describe the directive as an optional preference
