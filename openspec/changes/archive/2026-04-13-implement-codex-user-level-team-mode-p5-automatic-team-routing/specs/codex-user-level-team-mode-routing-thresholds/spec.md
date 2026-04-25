## MODIFIED Requirements

### Requirement: The installer SHALL generate an inspectable user-level routing-policy surface

The installer SHALL generate an additive user-level routing-policy inspection script into the target Codex home.

The generated asset set SHALL include:

- `bin/codex-routing-policy.ps1`

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
