## MODIFIED Requirements

### Requirement: Skills usage audit reports SHALL redact runtime paths

Every Skills usage audit JSON report and sanitized Markdown summary SHALL avoid retaining raw local runtime paths for the repository root, Codex home, and user-level `config.toml` path.

The report MUST retain path-kind evidence through `runtime_paths` placeholders such as `[REPO_ROOT]`, `[CODEX_HOME]`, and `[CODEX_HOME]/config.toml` instead of raw Windows, POSIX home, or UNC paths. `runtime_paths.raw_paths_retained` MUST be `false`. The field contract MUST fail when top-level `root`, top-level `codex_home`, `config_summary.config_path`, or `runtime_paths.root/codex_home/config_path` contains a raw private path or when the runtime-path privacy policy is missing or malformed.

#### Scenario: Reviewer reads runtime path evidence

- **WHEN** the audit script generates a JSON report
- **THEN** the report SHALL include sanitized `runtime_paths` placeholders and path-kind labels
- **AND** top-level compatibility fields `root`, `codex_home`, and `config_summary.config_path` SHALL use the same sanitized placeholders
- **AND** the serialized report SHALL NOT contain the raw repository path, raw user Codex home path, or raw user-level config path

#### Scenario: Runtime path privacy is broken

- **WHEN** the report field contract validates a generated or candidate-source audit report
- **AND** any runtime path field retains a raw private path or sets `raw_paths_retained=true`
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed
