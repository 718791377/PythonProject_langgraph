## MODIFIED Requirements

### Requirement: Skills governance lifecycle phases SHALL be explicit and gated

The Codex user-level skills governance lifecycle SHALL define separate acceptance gates for Phase 0 baseline inventory, Phase 1 policy and registry, Phase 2 governance checks, Phase 3 safe cleanup proposal, and later launcher/profile integration.

Each phase gate MUST preserve the safety boundaries from the implementation plan: no user-level skill mutation without an explicit installer invocation, no Vercel plugin disablement as a shortcut, no automatic user-level `config.toml` mutation during repository checks, and no GitHub PR publication by default.

#### Scenario: Operator reviews the lifecycle phase map

- **WHEN** the operator reviews the skills governance lifecycle
- **THEN** the lifecycle SHALL show Phase 0, Phase 1, Phase 2, Phase 3, and launcher/profile integration as distinct gates
- **AND** it SHALL identify which validation commands and safety boundaries apply to each gate

#### Scenario: Profile-helper implementation is requested

- **WHEN** the operator explicitly approves a plugin module profile-helper implementation
- **THEN** the lifecycle MAY proceed to a script-backed `plugin-modules` skill implementation
- **AND** repository validation SHALL remain non-mutating unless the operator separately runs the user-level installer or hard-load profile helper with `-Apply`
