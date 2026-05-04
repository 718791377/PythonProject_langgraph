## ADDED Requirements

### Requirement: Durable routing smoke gates SHALL declare the target, phase, task, and consent boundary

Before any live durable routing smoke test or adoption gate exercises automatic routing behavior, the reviewed change SHALL declare four gate fields:

- `target_repository` - the repository root that owns the source, OpenSpec artifacts, and repo-local durable state for the exercise.
- `phase` - the project phase that drives routing thresholds, such as read-context, verify-accept, execute-parallel, integrate-converge, or stabilize.
- `task` - the concrete work item or validation question being evaluated by the routing plan.
- `operator_consent_boundary` - the explicit boundary between read-only planning and mutating actions such as `-Apply`, `.omx/state/` writes, or durable-team launch.

The default consent boundary SHALL be read-only unless the reviewed change and the operator explicitly authorize mutation.

#### Scenario: A future smoke gate stays read-only until consent is explicit

- **WHEN** a reviewed change declares a durable routing smoke gate without explicit mutation consent
- **THEN** the routing exercise SHALL be limited to dry-run planning or read-only inspection
- **AND** it SHALL NOT run `omx-team-auto.ps1 -Apply`
- **AND** it SHALL NOT write `.omx/state/`
- **AND** it SHALL NOT launch or shut down a durable team

#### Scenario: A future adoption gate names its repository and task before runtime exercise

- **WHEN** a future adoption gate proposes to exercise automatic durable routing
- **THEN** it SHALL identify `target_repository`, `phase`, `task`, and `operator_consent_boundary` before the exercise begins
- **AND** the routing result SHALL explain why it selected or rejected `native_omx`, `langgraph`, or no durable team for that task flow
