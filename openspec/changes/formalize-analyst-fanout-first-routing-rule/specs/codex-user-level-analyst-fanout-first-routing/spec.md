## ADDED Requirements

### Requirement: Bounded multi-face research tasks SHALL prefer homogeneous analyst fan-out first

For a task that is still primarily about definition, classification, scoping, or repository-grounded comparison, and that has multiple bounded research faces, the routing model SHALL prefer homogeneous leader-side `analyst` fan-out for the first parallel research round.

This first-round preference SHALL apply before the router escalates into mixed-role research fan-out involving `architect`, `planner`, or `writer`.

#### Scenario: A bounded multi-face research task enters the first research round

- **WHEN** the task is still in the bounded research or classification stage and has multiple independent research faces
- **THEN** the routing model SHALL prefer multiple leader-side `analyst` calls for the first parallel round
- **AND** it SHALL not treat mixed `architect` / `planner` / `writer` fan-out as the default first-round pattern

### Requirement: Cross-role escalation SHALL occur only after the first research fan-in

After the first homogeneous analyst fan-out completes, the leader-side routing model SHALL allow escalation into other specialist roles only when the absorbed analyst outputs show that the task has clearly moved into another layer.

Those later layers include at minimum:

- architecture design
- execution ordering or rollout planning
- final document-production or operator-facing writing

#### Scenario: The leader absorbs analyst outputs and discovers a design-layer task

- **WHEN** the first homogeneous analyst round has already completed and the leader determines that the next question is architectural
- **THEN** the routing model SHALL allow escalation to `architect`
- **AND** that escalation SHALL happen after, not during, the first homogeneous analyst fan-out round

#### Scenario: The leader absorbs analyst outputs and discovers a planning-layer task

- **WHEN** the first homogeneous analyst round has already completed and the leader determines that the next question is execution ordering or rollout planning
- **THEN** the routing model SHALL allow escalation to `planner`
- **AND** that escalation SHALL happen after, not during, the first homogeneous analyst fan-out round

#### Scenario: The leader absorbs analyst outputs and discovers a document-finalization task

- **WHEN** the first homogeneous analyst round has already completed and the leader determines that the next question is final documentation or operator-facing writing
- **THEN** the routing model SHALL allow escalation to `writer`
- **AND** that escalation SHALL happen after, not during, the first homogeneous analyst fan-out round
