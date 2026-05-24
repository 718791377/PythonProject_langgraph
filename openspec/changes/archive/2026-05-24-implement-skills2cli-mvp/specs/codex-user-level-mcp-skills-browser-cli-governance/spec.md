## ADDED Requirements

### Requirement: Skills2cli MVP SHALL provide compact sanitized skill discovery

The repository SHALL provide a repo-local `skills2cli` helper that indexes available Codex skill metadata without dumping full skill bodies, private paths, secrets, cookies, tokens, raw browser data, or complete plugin description dumps in default output.

The helper SHALL support at least:

- `index --json` for compact skill inventory metadata;
- `search <query> --json` for compact query results;
- `show <skill-id> --json` for compact per-skill metadata.

Default metadata SHALL include skill id, source layer, sanitized location hint, short description summary, description hash, frontmatter validity, and availability status.

#### Scenario: Compact index output is requested

- **WHEN** `python tools/skills2cli.py index --json` runs
- **THEN** the JSON output SHALL contain compact skill metadata
- **AND** it SHALL NOT contain full skill bodies or complete plugin description dumps
- **AND** it SHALL keep private filesystem paths sanitized

#### Scenario: Search output is requested

- **WHEN** `python tools/skills2cli.py search browser --json` runs
- **THEN** matching results SHALL contain compact summaries and sanitized location hints
- **AND** the output SHALL NOT include full SKILL.md bodies by default

#### Scenario: Show output is requested without full expansion

- **WHEN** `python tools/skills2cli.py show <skill-id> --json` runs
- **THEN** the result SHALL report `full_body_included=false`
- **AND** the output SHALL remain compact and sanitized

### Requirement: Skills2cli profile suggestion SHALL be preview-only

The repository-local `skills2cli profile suggest --task <text> --json` command SHALL recommend candidate profiles/modules without applying them, editing user-level configuration, or editing plugin cache files.

#### Scenario: Profile suggestion is requested

- **WHEN** `python tools/skills2cli.py profile suggest --task "browser debugging" --json` runs
- **THEN** the result SHALL include profile/module suggestions
- **AND** `mutates_config` SHALL be `false`
- **AND** `profile_apply_performed` SHALL be `false`
- **AND** `approval_required_for_apply` SHALL be `true`

### Requirement: Skills2cli warning audit SHALL summarize budget and skipped-loading warnings

The repository-local `skills2cli audit warnings --since <duration> --json` command SHALL summarize Codex skills context budget warnings and skipped-loading warnings from available session logs without retaining raw log paths or private path details.

#### Scenario: Warning audit finds warning lines

- **WHEN** Codex session logs contain `Exceeded skills context budget of 2%` or `Skipped loading` warning text
- **AND** `python tools/skills2cli.py audit warnings --since 7d --json` runs
- **THEN** the result SHALL include budget-warning and skipped-loading counts
- **AND** recent excerpts SHALL be sanitized
- **AND** raw log paths SHALL NOT be retained
