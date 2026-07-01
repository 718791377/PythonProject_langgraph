# Delta Spec：Skills2CLI 隐藏库渐进披露

## ADDED Requirements

### Requirement：Hidden skills are discoverable without global restore

`skills2cli` SHALL provide a hidden-skill command surface that can discover standalone user skills moved into the visibility-disabled library without restoring those skills to the default model-visible skill list.

#### Scenario：Hidden library can be indexed

- **GIVEN** `CODEX_HOME/state/skills2cli/visibility-disabled` contains hidden skill directories
- **WHEN** `skills2cli hidden index --json` is executed
- **THEN** the output reports hidden skill records with `visibility_state=hidden`
- **AND** the output reports `global_restore_performed=false`, `mutates_config=false`, `edits_plugin_cache=false`, and `profile_apply_performed=false`.

#### Scenario：Current visible skills and hidden skills are searched together

- **GIVEN** a query matches either a current visible skill or a hidden skill
- **WHEN** `skills2cli hidden search <query> --json` is executed
- **THEN** the output returns compact candidates from both sources
- **AND** each candidate states whether it is `visible` or `hidden`.

### Requirement：Hidden skill soft-load reads exactly one selected skill

`skills2cli hidden load` SHALL read a single selected hidden `SKILL.md` into the command output without moving the skill directory or making it globally visible.

#### Scenario：Hidden load is read-only

- **GIVEN** a hidden skill id resolves to one `SKILL.md`
- **WHEN** `skills2cli hidden load <hidden_skill_id> --json` is executed
- **THEN** the output includes that skill body or a bounded chunk
- **AND** no hidden skill directory is moved to the visible skills directory
- **AND** the output reports `global_restore_performed=false` and `mutates_config=false`.

#### Scenario：Hidden load records usage evidence

- **GIVEN** `skills2cli hidden load <hidden_skill_id> --json` succeeds
- **WHEN** the command completes
- **THEN** a JSONL usage event is appended under `CODEX_HOME/state/skills2cli/usage-events.jsonl`
- **AND** the event contains a timestamp, event type, hidden skill id, frontmatter name, content hash, byte count, and `raw_paths_retained=false`.

### Requirement：Hidden aliases resolve known task names

The hidden-skill search surface SHALL support deterministic aliases for known task terms that do not match installed skill names exactly.

#### Scenario：Grill-me alias resolves hidden upstream adapter

- **GIVEN** the hidden library contains `mattpocock-skills-skills-productivity-grill-me-skill-md`
- **WHEN** `skills2cli hidden search grill-me --json` is executed
- **THEN** that hidden skill is returned as a high-confidence candidate.

#### Scenario：Stop-slop alias resolves AI slop cleaner

- **GIVEN** the hidden library contains `ai-slop-cleaner`
- **WHEN** `skills2cli hidden search stop-slop --json` is executed
- **THEN** `ai-slop-cleaner` is returned as an alias candidate
- **AND** the output explains that `stop-slop` is an alias rather than the installed skill name.

### Requirement：Visibility recommendations are evidence-driven and manual-only

`skills2cli visibility recommend` SHALL classify standalone user skills into promote, demote, and keep-soft-load buckets using usage evidence. Applying recommendations SHALL require an explicit user/operator command and SHALL NOT run automatically.

#### Scenario：Recommendations are generated from usage events

- **GIVEN** hidden skill usage events exist for a selected time window
- **WHEN** `skills2cli visibility recommend --days 30 --json` is executed
- **THEN** the output contains promote candidates for high-frequency hidden loads, keep-soft-load candidates for low-frequency hidden loads, and demote candidates for unused visible standalone user skills when evidence is sufficient.

#### Scenario：Apply recommendations requires explicit command

- **GIVEN** a recommendation receipt exists
- **WHEN** no operator runs `skills2cli visibility apply-recommendations --receipt <id> --apply --operator-confirmation --json`
- **THEN** no skill directories are moved.

#### Scenario：Apply recommendations is daily-limited and rollback-backed

- **GIVEN** a recommendation receipt exists and the operator invokes `apply-recommendations` with the required apply flags
- **WHEN** no apply has run on the current local day
- **THEN** at most three standalone user skills are moved
- **AND** a rollback receipt is written before moving and updated after each move.

#### Scenario：Second daily apply fails closed

- **GIVEN** `apply-recommendations` has already completed or partially completed on the current local day
- **WHEN** it is invoked again on the same local day
- **THEN** it fails closed and moves no additional skills.
