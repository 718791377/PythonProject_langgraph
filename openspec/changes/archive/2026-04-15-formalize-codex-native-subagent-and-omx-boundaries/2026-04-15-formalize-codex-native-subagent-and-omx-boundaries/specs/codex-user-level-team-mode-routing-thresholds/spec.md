## ADDED Requirements

### Requirement: Automatic expert routing SHALL be described as a leader-side overlay over explicit native spawning
The reusable routing policy SHALL describe automatic expert-role routing as a leader-side policy layered over explicit native Codex subagent spawning.

It SHALL NOT describe raw Codex as auto-spawning specialist roles by default.

#### Scenario: Operator inspects routing policy in native-routed mode
- **WHEN** the operator inspects the generated routing-policy surface for wrapped native-routed startup
- **THEN** it SHALL describe expert selection as leader-side routing over native Codex subagents
- **AND** it SHALL not describe raw Codex as automatically spawning those roles by default

### Requirement: Routing policy SHALL gate write-heavy fan-out more strictly than read-heavy fan-out
The routing policy SHALL prefer read-heavy or otherwise tightly bounded native-subagent fan-out.

For write-heavy multi-agent execution, the routing policy SHALL require explicit ownership isolation, hotspot serialization, and leader-owned final integration before the task is treated as eligible for parallel routing.

#### Scenario: Routing policy evaluates a write-heavy task without ownership isolation
- **WHEN** the task requires multiple writers and ownership isolation has not been defined
- **THEN** the routing policy SHALL classify the task as not yet eligible for write-heavy parallel execution
- **AND** it SHALL require ownership isolation or worktree separation before write-heavy fan-out is approved
