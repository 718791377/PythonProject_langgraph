## MODIFIED Requirements

### Requirement: The installer SHALL generate an inspectable user-level routing-policy surface

The installer SHALL generate an additive user-level routing-policy inspection script into the target Codex home.

The generated asset set SHALL include:

- `bin/codex-routing-policy.ps1`

The inspection output SHALL be read-only and SHALL reflect the same routing-policy model used by wrapped `codex` startup.

The inspection output SHALL also expose the generated burst-review role set and whether each burst-review role is currently installed as a callable user-level asset.

#### Scenario: Inspect the current routing policy after burst-review role installation

- **WHEN** the operator runs `codex-routing-policy.ps1 -Json`
- **THEN** it SHALL report the current startup mode, routing mode, and role-routing availability
- **AND** it SHALL expose the default role thresholds, startup-path semantics, and repository-scoped runtime-isolation notes
- **AND** it SHALL show `bug-finder`, `bug-rebutter`, and `bug-judge` as installed callable roles when their generated user-level profiles exist

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
- **AND** they SHALL not depend on OpenClaw-specific runtime commands
- **AND** they SHALL describe the burst-review triad as generated callable user-level roles
