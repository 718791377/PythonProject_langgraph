## MODIFIED Requirements

### Requirement: Automatic expert routing SHALL be described as a leader-side overlay over explicit native spawning

The reusable routing policy SHALL describe automatic expert-role routing as a leader-side policy layered over explicit native Codex subagent spawning.

It SHALL NOT describe raw Codex as auto-spawning specialist roles by default.

For bounded multi-face research tasks that are still primarily about definition, classification, scoping, or repository-grounded comparison, the first parallel research round SHALL prefer homogeneous `analyst` fan-out.

For those tasks, `architect`, `planner`, or `writer` SHALL enter only after the leader has completed a first research fan-in and determined that the task has clearly moved into architecture, execution ordering, or document-finalization work.

#### Scenario: Operator inspects routing policy in native-routed mode

- **WHEN** the operator inspects the generated routing-policy surface for wrapped native-routed startup
- **THEN** it SHALL describe expert selection as leader-side routing over native Codex subagents
- **AND** it SHALL not describe raw Codex as automatically spawning those roles by default

#### Scenario: Routing policy describes bounded multi-face research fan-out

- **WHEN** the operator inspects the generated routing-policy surface for a bounded multi-face research task
- **THEN** it SHALL describe homogeneous `analyst` fan-out as the default first research round
- **AND** it SHALL describe `architect`, `planner`, and `writer` as later escalation roles rather than default first-round research roles
