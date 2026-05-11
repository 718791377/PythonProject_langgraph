## ADDED Requirements

### Requirement: Durable-team thresholds SHALL be explained on first activation

The routing-threshold policy SHALL require the first activation trace for a task flow to explain either the durable-team threshold that was met or the specific threshold that was not met.

#### Scenario: A plan is not frozen

- **WHEN** the task does not yet have a frozen plan
- **THEN** the trace SHALL report durable team as not needed or not selected
- **AND** it SHALL cite the missing frozen plan threshold

#### Scenario: Parallel execution is eligible

- **WHEN** the plan is frozen and there are at least two mostly independent execution slices
- **THEN** durable-team adoption MAY be selected through the approved automatic helper
- **AND** the trace SHALL cite the named slice count and ownership boundary as the trigger
