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

## REMOVED Requirements

### Requirement: Publication SHALL follow explicit approval and GitLab-first workflow

**Reason**: Publication approval still matters, but the old requirement made GitLab the default gate before local `main` integration.

**Migration**: Use `Publication SHALL follow explicit approval and local-main-first workflow`.

## ADDED Requirements

### Requirement: Publication SHALL follow explicit approval and local-main-first workflow

Repository publication for this lifecycle SHALL require explicit user approval before commit, local `main` integration, push, MR update, MR creation, merge, or GitHub sync.

When local integration is approved, the repository SHALL use the local-main-first workflow: create a feature branch, run local CI and local MR review, keep the feature worktree clean, integrate the approved result into local `main`, and report any intentional remote lag. GitLab remote publication and GitHub sync SHALL remain later confirmation, backup, and mirror steps unless the user explicitly chooses a remote gate before local integration. GitHub PRs MUST NOT be created by default.

#### Scenario: Local OpenSpec artifacts are drafted

- **WHEN** OpenSpec artifacts are created locally for this lifecycle
- **THEN** the work SHALL remain uncommitted and unpublished unless the user explicitly requests commit, local integration, or remote publication
- **AND** existing remote MR candidates SHALL remain untouched unless the user explicitly requests an action on them

#### Scenario: Publication is explicitly approved

- **WHEN** the user explicitly approves publishing repository changes
- **THEN** the workflow SHALL use local `main` as the primary integration surface after local validation and local review pass
- **AND** GitLab SHALL be used as a remote publication and clean-environment confirmation surface
- **AND** GitHub SHALL be used only as the mirror/sync target unless the user explicitly overrides that rule
