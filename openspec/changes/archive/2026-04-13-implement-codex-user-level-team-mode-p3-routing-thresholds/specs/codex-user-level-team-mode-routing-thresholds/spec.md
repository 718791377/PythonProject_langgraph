## ADDED Requirements

### Requirement: The installer SHALL generate an inspectable user-level routing-policy surface

The installer SHALL generate an additive user-level routing-policy inspection script into the target Codex home.

The generated asset set SHALL include:

- `bin/codex-routing-policy.ps1`

The inspection output SHALL be read-only and SHALL reflect the same routing-policy model used by wrapped `codex` startup.

#### Scenario: Inspect the current routing policy

- **WHEN** the operator runs `codex-routing-policy.ps1 -Json`
- **THEN** it SHALL report the current startup mode, routing mode, and role-routing availability
- **AND** it SHALL expose the default role thresholds, startup-path semantics, and repository-scoped runtime-isolation notes

### Requirement: Wrapped startup SHALL derive developer instructions from a structured routing-policy model

The generated shared support script SHALL expose a structured routing-policy model that covers:

- general routing principles
- role-specific thresholds
- research-to-implementation handoff rules
- adversarial bug-review rules
- startup-path semantics for wrapped `codex` and `codex-native`

The startup launcher SHALL derive its developer-instruction payload from that shared model instead of an unrelated handwritten summary.

#### Scenario: Auto routing injects the approved thresholds

- **WHEN** wrapped `codex` starts with `oh_my_codex=off` and `subagent_routing=auto`
- **THEN** it SHALL inject developer instructions that include the approved expert-role thresholds
- **AND** it SHALL describe the session as wrapped native-routed startup rather than raw native startup

#### Scenario: Manual routing preserves the thresholds without proactive auto-routing

- **WHEN** wrapped `codex` starts with `subagent_routing=manual`
- **THEN** it SHALL keep the routing policy visible in the developer instructions
- **AND** it SHALL state that proactive auto-routing is disabled unless the user explicitly asks

#### Scenario: Routing-off mode disables orchestration

- **WHEN** wrapped `codex` starts with `subagent_routing=off`
- **THEN** it SHALL disable role orchestration
- **AND** it SHALL describe the session as a plain single-agent debugging path

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

#### Scenario: A user reads the generated assets from another repository

- **WHEN** the user opens the generated leader profile or playbook outside this repository
- **THEN** the assets SHALL still describe a reusable cross-repository operating model
- **AND** they SHALL not depend on OpenClaw-specific runtime commands
