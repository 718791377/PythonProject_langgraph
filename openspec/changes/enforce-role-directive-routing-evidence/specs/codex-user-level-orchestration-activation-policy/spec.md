## MODIFIED Requirements

### Requirement: Hard routing directives SHALL require adoption or named blockers

The orchestration activation policy SHALL treat explicit requests for `omx` or `LangGraph` as hard routing directives for the current task flow.

When the capability chain, preflight, and task thresholds are satisfied, the session SHALL report the selected lane as `selected` or `running` and SHALL NOT remain in explanation-only mode. When the requested lane is not adopted, the trace SHALL report a named blocker or unmet threshold such as `blocked:backend_not_ready`, `blocked:preflight_failed`, `blocked:helper_missing`, `blocked:write_ownership_conflict`, or `threshold_not_met:no_frozen_plan`.

The repository SHALL provide `tools/check_role_routing_directive_evidence.py` to validate saved hard-directive adoption and explanation-only evidence.

#### Scenario: Explicit directive is adopted

- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the capability chain, preflight, and task thresholds are satisfied
- **THEN** the activation trace SHALL report the requested lane as `selected` or `running`
- **AND** it SHALL NOT stay in explanation-only mode
- **AND** saved evidence SHALL pass the role/directive checker

#### Scenario: Explicit directive is blocked

- **WHEN** the user explicitly requests `omx` or `LangGraph`
- **AND** the requested lane cannot be adopted
- **THEN** the activation trace SHALL report `blocked:<reason>` or `threshold_not_met:<reason>`
- **AND** it SHALL NOT describe the directive as an optional preference

### Requirement: Smallest-sufficient role selection SHALL stay trigger-based

The orchestration activation policy SHALL select the smallest sufficient expert role set for the current phase. It SHALL NOT add roles merely because those roles are available. Bounded multi-face research SHALL start with homogeneous `analystxN` fan-out and SHALL escalate to `architect`, `planner`, or `writer` only after analyst fan-in exposes architecture, execution-ordering, or document-finalization work.

The repository SHALL provide `tools/check_role_routing_directive_evidence.py` to validate saved role-routing, role-minimality, and analyst-first evidence.

#### Scenario: Bounded multi-face research starts analyst-first

- **WHEN** the current task is bounded multi-face research
- **THEN** the first expert fan-out SHALL use `analystxN`
- **AND** it SHALL NOT include architect, planner, or writer by default before analyst fan-in
- **AND** saved evidence SHALL pass the role/directive checker
