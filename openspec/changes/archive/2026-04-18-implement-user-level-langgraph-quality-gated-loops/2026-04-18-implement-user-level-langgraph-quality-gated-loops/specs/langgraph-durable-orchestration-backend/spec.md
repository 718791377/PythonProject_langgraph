## MODIFIED Requirements

### Requirement: The LangGraph backend SHALL mirror the seven-phase development flow in a root graph

The LangGraph backend SHALL provide a root graph that mirrors the durable team workflow phases:

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

The root graph SHALL support conditional edges driven by structured gate verdicts.

Selected flows MAY re-enter earlier nodes through bounded quality-gated loops when the gate result indicates the work remains repairable but not yet acceptable.

Persisted graph state SHALL record whether the current execution is first-pass, looping, interrupted, exhausted, or accepted.

#### Scenario: Graph state advances from planning to loop-capable execution

- **WHEN** the task has a frozen plan and enough execution slices to justify durable execution
- **THEN** the root graph SHALL be able to transition from `freeze-plan` into `execute-parallel`
- **AND** it SHALL preserve the current phase and loop-capable execution posture in persisted graph state

### Requirement: The LangGraph backend SHALL support interrupts and operator-driven resume

The durable orchestration backend SHALL support human approval points that interrupt execution and later resume it from persisted state.

At minimum the first rollout SHALL support interruptable approval points around:

- plan freeze
- risky stabilization decisions
- failed final verification
- loop verdicts that require human input

Interrupts SHALL preserve active loop metadata when the thread pauses at a gate.

Resume SHALL return to the same conditional graph path rather than flattening back to a one-pass wrapper.

#### Scenario: Plan-freeze or loop-gate approval pauses the graph

- **WHEN** the workflow reaches a plan-freeze approval point or a gate verdict that requires human input
- **THEN** the graph SHALL be able to interrupt and expose the pending state to the operator
- **AND** the operator SHALL be able to resume the same thread with the preserved loop metadata and conditional execution path
