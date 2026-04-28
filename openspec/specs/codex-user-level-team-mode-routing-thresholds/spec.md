# Codex User-Level Team Mode Routing Thresholds

## Purpose

Define the user-level routing-threshold, startup-path, and runtime-isolation rules for Codex / oh-my-codex team mode.

This capability keeps wrapped `codex` startup inspectable and reusable across repositories while preserving native Codex as the permanent base layer.
## Requirements
### Requirement: The installer SHALL generate an inspectable user-level routing-policy surface

The installer SHALL generate an additive user-level routing-policy inspection script into the target Codex home.

The generated asset set SHALL include:

- `bin/codex-routing-policy.ps1` - user-level script for inspecting or changing routing policy.

The inspection output SHALL be read-only and SHALL reflect the same routing-policy model used by wrapped `codex` startup.

The inspection output SHALL also expose:

- the generated burst-review role set and whether each burst-review role is installed
- the automatic durable-team routing section
- the helper path for automatic durable-team routing
- the tracked-team record path and non-adoption rule for unmanaged teams

#### Scenario: Inspect the routing policy after P5 installation

- **WHEN** the operator runs `codex-routing-policy.ps1 -Json`
- **THEN** it SHALL report the current startup mode, routing mode, and role-routing availability
- **AND** it SHALL expose the durable-team phase map, helper path, reuse or switch or shutdown rules, and tracked-team safety boundary

#### Scenario: Routing policy repeats the promoted backend-selection contract

- **WHEN** the operator runs `codex-routing-policy.ps1 -Json`
- **THEN** it SHALL expose the same backend-selection contract as the user-level backend status surface
- **AND** it SHALL report the primary backend-policy surface and supporting views
- **AND** it SHALL preserve the rule that backend-family switching remains explicit or manual-only

### Requirement: Wrapped startup SHALL derive developer instructions from a structured routing-policy model

The generated shared support script SHALL expose a structured routing-policy model that covers:

- general routing principles
- role-specific thresholds
- research-to-implementation handoff rules
- adversarial bug-review rules
- startup-path semantics for wrapped `codex` and `codex-native`
- automatic durable-team routing semantics in enhanced auto mode

The startup launcher SHALL derive its developer-instruction payload from that shared model instead of an unrelated handwritten summary.

#### Scenario: Enhanced auto mode exposes the durable-team helper without changing startup semantics

- **WHEN** wrapped `codex` starts with `oh_my_codex=on` and `subagent_routing=auto`
- **THEN** it SHALL inject developer instructions that mention the automatic durable-team helper and phase thresholds
- **AND** it SHALL state that startup itself still does not auto-launch a durable team

### Requirement: The routing policy SHALL preserve the approved startup semantics

The routing policy SHALL distinguish:

- wrapped native-routed startup
- enhanced startup
- pure debugging startup

It SHALL preserve the rule that enabling oh-my-codex changes startup mode and capability flags, but does not auto-launch a durable team on every `codex` start.

#### Scenario: Enhanced mode remains startup-only until the operator launches a team

- **WHEN** the operator enables oh-my-codex globally and starts wrapped `codex`
- **THEN** the routing policy SHALL report enhanced startup
- **AND** it SHALL not claim that a durable team was automatically launched

### Requirement: Generated leader and playbook assets SHALL mirror the routing and isolation rules

The generated `team-leader.toml` and `docs/team-mode-playbook.md` SHALL document:

- wrapped `codex` vs `codex-native`
- the role-routing thresholds
- research-to-implementation handoff discipline
- adversarial bug-review usage
- the rule that multi-project runtime isolation comes from per-repository `.omx` state roots

When burst-review roles are generated, these assets SHALL describe them as real leader-side callable roles rather than abstract future placeholders.

#### Scenario: A user reads the generated assets from another repository after P4 installation

- **WHEN** the user opens the generated leader profile or playbook outside this repository
- **THEN** the assets SHALL still describe a reusable cross-repository operating model
- **AND** they SHALL not depend on downstream application-specific runtime commands
- **AND** they SHALL describe the burst-review triad as generated callable user-level roles

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

### Requirement: Routing policy SHALL gate write-heavy fan-out more strictly than read-heavy fan-out

The routing policy SHALL prefer read-heavy or otherwise tightly bounded native-subagent fan-out.

For write-heavy multi-agent execution, the routing policy SHALL require explicit ownership isolation, hotspot serialization, and leader-owned final integration before the task is treated as eligible for parallel routing.

#### Scenario: Routing policy evaluates a write-heavy task without ownership isolation

- **WHEN** the task requires multiple writers and ownership isolation has not been defined
- **THEN** the routing policy SHALL classify the task as not yet eligible for write-heavy parallel execution
- **AND** it SHALL require ownership isolation or worktree separation before write-heavy fan-out is approved

### Requirement: Routing policy SHALL expose mandatory orchestration re-check triggers

The user-level routing policy SHALL expose orchestration re-check triggers beyond first-turn startup.

At minimum it SHALL include:

- task-phase change
- expansion from one slice to two or more execution slices
- tracked durable-state detection
- explicit user requests for `omx`, `LangGraph`, resume, continue, or parallel execution

#### Scenario: Operator inspects orchestration re-check triggers

- **WHEN** the operator runs `codex-routing-policy.ps1 -Json`
- **THEN** it SHALL expose the mandatory orchestration re-check triggers
- **AND** it SHALL not present activation as a first-turn-only decision

### Requirement: Routing policy SHALL treat explicit orchestration requests as hard directives

The user-level routing policy SHALL treat explicit user requests to use `omx` or `LangGraph` as hard routing directives.

When activation thresholds are met and no concrete blocker exists, Codex CLI SHALL actually adopt the orchestration path rather than remaining in explanation-only mode.

#### Scenario: User explicitly requests `LangGraph`

- **WHEN** the user explicitly requests `LangGraph`
- **THEN** Codex CLI SHALL treat that as a hard routing directive
- **AND** it SHALL adopt the orchestration path unless a concrete blocker exists
- **AND** if orchestration is not adopted, it SHALL explain the concrete blocker

### Requirement: Routing thresholds SHALL keep mixed persistent pane compose outside the default path

The user-level routing-threshold model SHALL keep mixed persistent pane compose outside the default path.

Automatic routing SHALL continue to use the normal hybrid model unless the operator explicitly invokes compose mode.

#### Scenario: Thresholds are met for ordinary durable execution

- **WHEN** ordinary durable-routing thresholds are met for a task
- **THEN** the workflow SHALL continue to choose the default hybrid operating model
- **AND** it SHALL not silently activate mixed persistent pane compose without an explicit compose request
