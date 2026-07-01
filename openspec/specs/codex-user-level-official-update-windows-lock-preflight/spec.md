## Purpose

Prevent ambiguous Windows Codex npm official-update states by detecting likely active `codex.exe` / Node file-lock risks before global npm mutation, classifying successful npm cleanup EPERM warnings separately from install failures, and reporting leftover `.codex-*` staging candidates for manual review without deleting them automatically.

## Requirements

### Requirement: Official update SHALL detect Windows Codex lock risk before npm mutation

The official update patch replay template SHALL run a Windows lock preflight before invoking `npm install -g @openai/codex oh-my-codex` when the selected stage or switches would mutate global npm packages.

#### Scenario: Active Codex process blocks update by default

- **GIVEN** the operator runs the official update template on Windows with a stage that runs the official npm update
- **AND** the preflight detects a likely active Codex or Node process that can lock the npm-installed Codex executable or package tree
- **WHEN** no explicit locked-update override is provided
- **THEN** the template SHALL fail before invoking npm install
- **AND** the structured report SHALL record `lock_risk=detected`, matched process evidence, and `recommended_action=close_codex_sessions_then_rerun`

#### Scenario: Explicit override records risk and continues

- **GIVEN** the preflight detects a likely lock risk
- **WHEN** the operator provides the explicit locked-update override
- **THEN** the template MAY invoke npm install
- **AND** the structured report SHALL record that the override was used

#### Scenario: No lock risk allows update path

- **GIVEN** the template runs on Windows
- **AND** the preflight does not detect likely Codex lock holders
- **WHEN** the stage runs the official npm update
- **THEN** the template SHALL keep the existing npm update behavior
- **AND** the structured report SHALL record `lock_risk=clear`

### Requirement: Official update SHALL classify npm cleanup EPERM warnings without masking install failure

The official update patch replay template SHALL classify npm cleanup warnings caused by Windows file locks separately from package-install failure.

#### Scenario: EPERM cleanup warning after successful npm install is reported as cleanup warning

- **GIVEN** npm install exits with code `0`
- **AND** npm output includes `npm warn cleanup`, `EPERM`, and an `unlink` path ending in `codex.exe`
- **WHEN** the template builds its report
- **THEN** it SHALL record an `official_update_cleanup_warnings` entry with type `windows_file_lock_eperm`
- **AND** it SHALL preserve the successful npm exit code

#### Scenario: EPERM text does not mask non-zero npm install failure

- **GIVEN** npm install exits with a non-zero code
- **AND** npm output includes EPERM cleanup text
- **WHEN** the template evaluates the update result
- **THEN** it SHALL treat the official update command as failed according to existing command semantics
- **AND** it SHALL NOT report the update as successful solely because the warning is classifiable

### Requirement: Official update SHALL report leftover Codex staging candidates without deleting them by default

The official update patch replay template SHALL report `.codex-*` staging directory candidates under the npm global `@openai` package root and SHALL NOT delete them automatically by default.

#### Scenario: Leftover staging directory is visible in report

- **GIVEN** the npm global package root contains one or more `@openai/.codex-*` directories
- **WHEN** the preflight or post-update report runs
- **THEN** the structured report SHALL list those directories as leftover staging candidates
- **AND** the generated checklist SHALL instruct the operator to close active Codex/Node sessions before manual cleanup
- **AND** the template SHALL NOT remove those directories unless a future explicit cleanup feature is added
