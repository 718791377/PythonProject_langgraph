# codex-user-level-team-mode-burst-review-agents Specification

## Purpose
TBD - created by archiving change implement-codex-user-level-team-mode-p4-burst-review-agents. Update Purpose after archive.
## Requirements
### Requirement: The installer SHALL generate user-level burst-review agent profiles

The installer SHALL generate additive user-level agent profiles into the target Codex home.

The generated asset set SHALL include:

- `agents/bug-finder.toml` - user-level native-agent TOML for overinclusive candidate bug discovery.
- `agents/bug-rebutter.toml` - user-level native-agent TOML for challenging weak bug claims.
- `agents/bug-judge.toml` - user-level native-agent TOML for arbitrating evidence-backed bug survivors.

The installer SHALL NOT replace unmanaged files at those paths unless explicitly forced.

#### Scenario: Generate burst-review agent profiles into a temporary Codex home

- **WHEN** the installer is run against an explicit target Codex home
- **THEN** it SHALL generate the three burst-review role profiles there
- **AND** it SHALL keep the new files additive-only

### Requirement: The generated burst-review roles SHALL stay leader-side and read-only by default

The generated `bug-finder`, `bug-rebutter`, and `bug-judge` profiles SHALL describe leader-side short-burst review roles.

They SHALL default to read-only review behavior and SHALL NOT present themselves as durable worker panes.

#### Scenario: An operator inspects the generated role definitions

- **WHEN** the user opens the generated burst-review agent files
- **THEN** each profile SHALL describe a leader-side burst-review role
- **AND** each profile SHALL preserve read-only-by-default review discipline

### Requirement: The generated burst-review roles SHALL encode the adversarial review contract

The generated role prompts SHALL encode the approved adversarial review loop:

- `bug-finder` maximizes plausible bug recall with weighted severity scoring
- `bug-rebutter` attempts to falsify weak bug claims with asymmetric scoring pressure
- `bug-judge` arbitrates the two reports and preserves only the survivor set for escalation

#### Scenario: A user-level install is inspected for burst-review behavior

- **WHEN** the generated role files are reviewed after installation
- **THEN** the three prompts SHALL expose distinct finder, rebutter, and judge responsibilities
- **AND** the judge SHALL be the gate for escalation into execution or debugging lanes

### Requirement: Burst-review agent generation SHALL be covered by backup snapshots and rollback

The installer SHALL include the burst-review agent files in the same backup snapshot and rollback-on-error transaction used for the rest of the user-level team-mode assets.

#### Scenario: A partial install restores pre-install burst-review state

- **WHEN** installation fails after burst-review agent files have been written
- **THEN** the installer SHALL restore previously existing managed burst-review files
- **AND** it SHALL remove newly created burst-review files for fresh installs
- **AND** it SHALL preserve backup metadata for diagnostics

