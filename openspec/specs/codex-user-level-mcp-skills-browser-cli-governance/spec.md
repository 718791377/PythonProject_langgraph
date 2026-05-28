# codex-user-level-mcp-skills-browser-cli-governance Specification

## Purpose

This specification preserves the script-backed baseline governance requirements for user-level MCP, skills, browser automation, and CLI harness surfaces. It keeps Token/risk priority, authorization receipt, update receipt, evidence redaction, port registry/lease, OpenSpec slice, and fail closed rules visible before the later `skills2cli`, `mcp2cli`, browser, and `wecom-cli` implementation slices land.
## Requirements
### Requirement: User-level MCP skills browser CLI baseline SHALL be script-backed

The repository SHALL maintain an executable baseline checker for the user-level MCP, skills, browser automation, and CLI harness governance plan.

The checker SHALL validate that repository-owned plan and OpenSpec surfaces preserve token/risk priority, lane default states, sensitive authorization receipt fields, user-level tool update receipt fields, evidence redaction rules, and OpenSpec slice completion markers.

#### Scenario: Baseline checker runs in the repository guard

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregate guard SHALL include `check_user_level_mcp_skills_browser_cli_baseline`
- **AND** the checker SHALL pass only when the baseline governance surfaces are present

#### Scenario: Authorization receipt evidence is incomplete

- **WHEN** the baseline checker scans the implementation plan
- **AND** action, target, scope, expiry, session, or operator confirmation evidence is absent
- **THEN** the checker SHALL fail closed

#### Scenario: Update receipt evidence is incomplete

- **WHEN** the baseline checker scans the implementation plan
- **AND** install path, wrapper path, state path, pin/version, smoke command, updater command, rollback pointer, or owner lane evidence is absent
- **THEN** the checker SHALL fail closed

### Requirement: User-level port governance SHALL be preserved before allocator implementation

The baseline checker SHALL validate that the repository-owned plan and OpenSpec surfaces preserve the port registry/lease contract for Codex, the later external project range, OpenCLI, and managed browser automation.

The preserved contract SHALL include the Codex `39000-39299` helper range, the broader Codex `39000-39999` owner block, the later external `40000-40999` owner range, `codex-port` allocator ownership (codex-port allocator), allocator-driven OpenCLI `--port auto`, `pending_bind` provisional leases, `registry_revision` concurrency evidence, live-socket collision skipping, stale/crash evidence, and the rule that port governance never kills existing processes.

#### Scenario: Port-governance markers are removed

- **WHEN** the baseline checker scans the repository-owned plan and spec surfaces
- **AND** port registry/lease, `codex-port` allocator, `pending_bind`, `registry_revision`, owner ranges including `39000-39299` and `40000-40999`, or OpenCLI `--port auto` evidence is missing
- **THEN** the checker SHALL fail closed
- **AND** the operator SHALL restore the port-governance contract before committing

### Requirement: User-level MCP skills browser CLI evidence SHALL remain sanitized

Repository evidence for this plan SHALL NOT retain secrets, cookies, tokens, raw browser data, message contents, full personal runtime paths, or complete plugin description dumps.

#### Scenario: Evidence redaction markers are removed

- **WHEN** the baseline checker scans the repository-owned plan and spec surfaces
- **AND** the evidence redaction boundary is missing
- **THEN** the checker SHALL fail
- **AND** the operator SHALL restore the sanitized-evidence boundary before committing

### Requirement: User-level MCP skills browser CLI slices SHALL not become active without evidence

Each implementation slice SHALL remain `planned`, `implemented-local`, `installed-user-level`, or `smoke-tested` until implementation, tests, CI registration, OpenSpec updates, rollback evidence, and completed receipts are present.

#### Scenario: A slice has only documentation or research

- **WHEN** the slice lacks implementation, test, CI registration, rollback evidence, or completed receipt evidence
- **THEN** it SHALL NOT be marked `active`
- **AND** the baseline checker SHALL require the plan to preserve slice completion rules

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

### Requirement: Codex-port allocator MVP SHALL provide range-aware port leases

The repository SHALL provide a repo-local `codex-port` helper and range registry for compact, deterministic port lease governance.

The helper SHALL support at least:

- `lease reserve --owner <owner> --project <slug> --tool <tool> --range <range-name> --purpose <text> --ttl <seconds> --json`;
- `lease renew --lease-id <id> --owner-session <session-id> --ttl <seconds> --json`;
- `lease release --owner-session <session-id> --port <port> --json`;
- `lease list --owner <owner> --json`;
- `lease import-legacy --owner openclaw --port <port> --purpose <text> --json`;
- `lease gc --dry-run --json` for read-only stale-candidate inspection.

The allocator SHALL preserve Codex ranges before the external project range: Codex helper ports `39000-39299`, Codex OpenCLI ports `39300-39499`, Codex browser-automation ports `39500-39699`, Codex reserved ports `39700-39999`, and external project ports `40000-40999`.

#### Scenario: Codex reserves a helper port

- **WHEN** `python tools/codex_port.py lease reserve --owner codex --project pythonproject-langgraph --tool mcp2cli --range codex-helper --purpose test --ttl 300 --json` runs against an empty registry
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL allocate the first available Codex helper port
- **AND** it SHALL write a `pending_bind` lease with `registry_revision` evidence
- **AND** it SHALL write a sanitized reserve receipt

#### Scenario: Owner requests another owner range

- **WHEN** `python tools/codex_port.py lease reserve --owner codex --range openclaw --json` is requested
- **THEN** the command SHALL fail closed with an owner/range mismatch
- **AND** it SHALL NOT mutate the registry

#### Scenario: Live local socket already occupies a port

- **WHEN** a live socket already occupies the first candidate port in the requested range
- **AND** `codex-port lease reserve` runs
- **THEN** the allocator SHALL skip the occupied port
- **AND** it SHALL report a collision warning
- **AND** it SHALL NOT kill, attach to, or otherwise mutate the existing process

### Requirement: Codex-port lease lifecycle SHALL preserve ownership, stale evidence, and receipts

The repository-local `codex-port` helper SHALL require lease ownership evidence for write lifecycle actions and SHALL preserve crash/stale evidence before reusing stale ports.

#### Scenario: Lease renew promotes a bound pending lease

- **WHEN** `codex-port lease renew --lease-id <id> --owner-session <session-id> --ttl <seconds> --activate --json` runs for a matching owner session
- **THEN** the lease SHALL be renewed
- **AND** a `pending_bind` lease MAY be promoted to `active`
- **AND** a sanitized renew receipt SHALL be written

#### Scenario: Release owner session does not match

- **WHEN** `codex-port lease release --owner-session <different-session> --port <port> --json` runs
- **THEN** the release SHALL fail closed
- **AND** the existing lease SHALL remain unreleased

#### Scenario: Legacy openclaw-owner port is imported

- **WHEN** `codex-port lease import-legacy --owner openclaw --port 40000 --purpose <text> --json` runs
- **THEN** the registry SHALL record a `legacy_reserved` lease
- **AND** later Codex allocation SHALL NOT consume that external project range

#### Scenario: Garbage collection is dry-run

- **WHEN** `codex-port lease gc --dry-run --json` runs
- **THEN** stale or expired leases SHALL be reported as candidates
- **AND** the registry SHALL NOT be mutated
- **AND** no process SHALL be killed

### Requirement: Mcp2cli MVP SHALL provide compact allowed-profile discovery

The repository SHALL provide a repo-local `mcp2cli` helper and allowed-profile registry for compact MCP tool discovery.

The helper SHALL support at least:

- `list --profile <profile> --json` for compact profile tool inventory;
- `search <query> --profile <profile> --json` for compact query results;
- `show <tool> --profile <profile> --json` for compact per-tool metadata.

Default output SHALL include only compact, sanitized profile/tool metadata and SHALL NOT dump full tool schemas, secrets, cookies, tokens, raw browser data, full personal runtime paths, or complete private configuration details.

#### Scenario: Compact MCP profile list is requested

- **WHEN** `python tools/mcp2cli.py list --profile core-readonly --json` runs
- **THEN** the JSON output SHALL contain compact allowed tool metadata
- **AND** the output SHALL report `compact_output=true`
- **AND** the output SHALL NOT include full schemas by default

#### Scenario: Compact MCP search is requested

- **WHEN** `python tools/mcp2cli.py search browser --profile browser-readonly --json` runs
- **THEN** matching results SHALL contain compact summaries and risk metadata
- **AND** full tool schemas SHALL remain excluded by default

### Requirement: Mcp2cli MVP call facade SHALL fail closed for sensitive calls

The repository-local `mcp2cli call` command SHALL evaluate allowed profile registry metadata before any call result is emitted.

Tools with sensitive categories, medium/high/critical risk, or `requires_authorization=true` SHALL fail closed unless a matching authorization receipt is supplied.

#### Scenario: Sensitive call lacks authorization receipt

- **WHEN** `python tools/mcp2cli.py call browser.tabs.list --profile browser-readonly --json --args {}` runs without a receipt
- **THEN** the result SHALL report `ok=false`
- **AND** it SHALL report `blocked=true`
- **AND** it SHALL report `receipt_required=true`
- **AND** it SHALL report `call_performed=false`

#### Scenario: Authorization receipt is incomplete

- **WHEN** `mcp2cli call` receives an authorization receipt missing action, target, scope, expiry, session, or operator confirmation
- **THEN** the command SHALL fail closed
- **AND** the result SHALL include sanitized blocker codes instead of raw private receipt contents

#### Scenario: Low-risk allowed call is requested

- **WHEN** `python tools/mcp2cli.py call repo.openspec.list --profile core-readonly --json --args {}` runs
- **THEN** the result SHALL remain local and deterministic
- **AND** it SHALL not invoke a live external MCP server
- **AND** it SHALL report the call facade result without requiring a sensitive authorization receipt

### Requirement: Browser owner registry MVP SHALL coordinate browser automation ownership

The repository SHALL provide a repo-local browser owner registry helper that records browser automation ownership without launching Chrome, connecting to CDP, or mutating user-level Codex configuration.

The helper SHALL support at least:

- `lease reserve --owner-class <class> --project <slug> --session <id> --target <target> --profile-path <path> --purpose <text> --ttl <seconds> --json`;
- `lease renew --lease-id <id> --session <id> --ttl <seconds> --json`;
- `lease release --lease-id <id> --session <id> --json`;
- `lease list --json`;
- `stale-scan --dry-run --json`;
- Cleanup dry-run command: `cleanup dry-run --json`, used only to preview safe cleanup candidates without deleting browser profiles.

The registry SHALL preserve owner class, project slug, session id, target, sanitized profile-path evidence, profile-path hash, lease expiry, status, and receipt evidence for write actions.

#### Scenario: Isolated managed browser lease is reserved

- **WHEN** `python tools/browser_owner_registry.py lease reserve --owner-class codex-managed-isolated --project pythonproject-langgraph --session session-a --target tab:debug --profile-path <path> --purpose test --ttl 300 --json` runs against an empty registry
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL record an active managed isolated lease
- **AND** it SHALL write a sanitized reserve receipt
- **AND** default output SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Project profile lacks authorization

- **WHEN** `browser_owner_registry.py lease reserve` is requested for `codex-managed-project` without a current one-task authorization receipt
- **THEN** the command SHALL fail closed
- **AND** no lease SHALL be recorded

#### Scenario: Same target is already owned

- **WHEN** an active lease already owns the requested browser target
- **AND** another lease reserve request names the same target
- **THEN** the command SHALL fail closed with target ownership evidence
- **AND** it SHALL NOT overwrite the existing lease

### Requirement: Browser cleanup dry-run SHALL protect project and human-owned assets

The browser owner registry helper SHALL keep cleanup as dry-run only in the repo-local MVP and SHALL never treat project profiles or human-owned browser assets as cleanup candidates.

#### Scenario: Cleanup dry-run sees stale leases

- **WHEN** stale leases include a `codex-managed-isolated` profile and a `codex-managed-project` profile
- **AND** `python tools/browser_owner_registry.py cleanup dry-run --json` runs
- **THEN** only the stale `codex-managed-isolated` profile SHALL be listed as a cleanup candidate
- **AND** the stale project profile SHALL be listed as protected
- **AND** `cleanup_performed` SHALL be `false`
- **AND** `human_owned_cleanup_performed` SHALL be `false`

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate isolated sessions

The repository SHALL provide a repo-local `chrome-devtools-mcp` managed wrapper MVP for isolated-session browser automation contracts.

The wrapper SHALL support at least:

- `isolated-session plan --project <slug> --session <id> --purpose <text> --json`;
- `isolated-session reserve --project <slug> --session <id> --purpose <text> --ttl <seconds> --json`;
- `isolated-session start --project <slug> --session <id> --purpose <text> [--dry-run] [--install-receipt <path>] --json`;
- `isolated-session release --lease-id <id> --session <id> --json`;
- `isolated-session status --json`, which lists sanitized managed isolated lease state.

The wrapper SHALL coordinate with the browser owner registry, SHALL sanitize default output, and SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, or write human-owned profiles in the repo-local MVP.

#### Scenario: Isolated-session plan is a non-mutating dry run

- **WHEN** `python tools/chrome_devtools_mcp_managed.py isolated-session plan --project pythonproject-langgraph --session session-a --purpose test --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Isolated-session reserve writes managed ownership evidence

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session reserve --project pythonproject-langgraph --session session-a --purpose test --ttl 120 --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write an active `codex-managed-isolated` owner lease through the browser owner registry
- **AND** it SHALL write a sanitized wrapper receipt
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Live start lacks install receipt

- **WHEN** `python tools/chrome_devtools_mcp_managed.py isolated-session start --project pythonproject-langgraph --session session-a --purpose test --json` runs without an install receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report `install_receipt_required`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL NOT mutate browser owner registry state

#### Scenario: Isolated-session release delegates to owner registry

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session release --lease-id <id> --session session-a --json` runs for a matching active lease
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL mark the owner lease as released through the browser owner registry
- **AND** it SHALL write a sanitized wrapper release receipt

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate project profiles

The repository SHALL extend the repo-local `chrome-devtools-mcp` managed wrapper MVP with project-profile browser automation contracts.

The wrapper SHALL support at least:

- `project-profile plan --project <slug> --profile <name> --session <id> --purpose <text> --json`;
- `project-profile reserve --project <slug> --profile <name> --session <id> --purpose <text> --authorization-receipt <path> --ttl <seconds> --json`;
- `project-profile start --project <slug> --profile <name> --session <id> --purpose <text> [--dry-run] [--authorization-receipt <path>] [--install-receipt <path>] --json`;
- `project-profile release --lease-id <id> --session <id> --json`;
- `project-profile status --json`, which lists sanitized managed project-profile lease state.

Project profiles SHALL use the `codex-managed-project` owner class, SHALL be long-lived project assets, SHALL require a current project-profile authorization receipt before reserve or live start, and SHALL NOT be cleanup candidates in the repo-local MVP.

The repo-local MVP SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, write human-owned profiles, or perform live `chrome-devtools-mcp` startup.

#### Scenario: Project-profile plan is a non-mutating dry run

- **WHEN** `python tools/chrome_devtools_mcp_managed.py project-profile plan --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL report `owner_class=codex-managed-project`
- **AND** it SHALL report `profile_retention=long-lived-project-profile`
- **AND** it SHALL report `cleanup_allowed_after_stale_evidence=false`
- **AND** it SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Project-profile reserve lacks authorization

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile reserve --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --json` runs without an authorization receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report authorization receipt evidence is required
- **AND** it SHALL NOT mutate browser owner registry state
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Project-profile reserve writes protected ownership evidence

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile reserve --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --authorization-receipt <path> --json` runs with a current matching authorization receipt
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write an active `codex-managed-project` owner lease through the browser owner registry
- **AND** it SHALL write a sanitized wrapper receipt
- **AND** it SHALL report project-profile cleanup is not allowed
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Same project profile is already owned

- **WHEN** an active `codex-managed-project` lease already controls a project profile
- **AND** another session requests the same project profile or target
- **THEN** the wrapper SHALL fail closed through the browser owner registry
- **AND** it SHALL NOT overwrite the existing lease

#### Scenario: Project-profile live start is gated before repo-local deferral

- **WHEN** `project-profile start` runs without a current matching project-profile authorization receipt
- **THEN** the command SHALL fail closed before checking install receipt state
- **AND** it SHALL report `start_performed=false`

- **WHEN** `project-profile start` runs with a current matching project-profile authorization receipt but without an install receipt
- **THEN** the command SHALL fail closed with `install_receipt_required`
- **AND** it SHALL report `start_performed=false`

- **WHEN** `project-profile start` runs with both a current matching project-profile authorization receipt and an install receipt
- **THEN** the command SHALL still fail closed with `live_start_not_implemented_repo_local_mvp`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL NOT mutate browser owner registry state

#### Scenario: Project-profile release delegates to owner registry

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile release --lease-id <id> --session session-a --json` runs for a matching active project-profile lease
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL mark the owner lease as released through the browser owner registry
- **AND** it SHALL write a sanitized project-profile wrapper release receipt

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL expose safe stale scan and cleanup dry-run

The repository-local `chrome-devtools-mcp` managed wrapper MVP SHALL expose browser stale scan and safe cleanup dry-run commands that delegate to the browser owner registry.

The wrapper SHALL support at least:

- `stale-scan --dry-run --json` - previews stale browser owner-registry leases without mutation;
- `cleanup dry-run --json` - previews safe cleanup candidates without deleting profiles.

Both commands SHALL be non-mutating dry runs in the repo-local MVP. They SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, delete browser profiles, or clean up human-owned or project-profile assets.

#### Scenario: Wrapper stale-scan delegates to owner registry without mutation

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> stale-scan --dry-run --json` runs with expired isolated and project-profile leases in registry state
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `cleanup_performed=false`
- **AND** it SHALL list sanitized stale candidates without raw private profile paths

#### Scenario: Wrapper cleanup dry-run protects project and human-owned assets

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> cleanup dry-run --json` runs with expired isolated, project-profile, and human-delegated leases in registry state
- **THEN** only expired `codex-managed-isolated` leases SHALL appear as cleanup candidates
- **AND** project-profile or human-delegated leases SHALL appear as protected profiles
- **AND** `cleanup_performed` SHALL be `false`
- **AND** `human_owned_cleanup_performed` SHALL be `false`
- **AND** `deleted_profiles` SHALL be empty

### Requirement: CDP Bridge governance guard SHALL keep read-only defaults and fail closed sensitive actions

The repository SHALL provide a repo-local CDP Bridge governance guard that classifies CDP Bridge actions before any live browser dispatch can occur.

The guard SHALL treat read-only inventory actions as allowed without browser-owner or authorization evidence. The read-only inventory actions SHALL include `tab.list`, `dom.scan`, `screenshot.capture`, and `inventory`.

The guard SHALL treat cookie reads, JavaScript execution, click, type, navigation, and unknown actions as sensitive. Sensitive actions SHALL require both active browser-owner lease evidence and a current one-task authorization receipt before dispatch is allowed.

The guard SHALL be non-mutating. It SHALL NOT launch Chrome, connect to CDP, read cookies, execute JavaScript, click, type, navigate, mutate user-level Codex configuration, or emit raw private profile paths.

#### Scenario: Read-only tab inventory is allowed without owner evidence

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action tab.list --target tab:debug-1 --session session-a --json` runs without an owner registry or authorization receipt
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `authorization_required=false`
- **AND** it SHALL report `owner_required=false`
- **AND** it SHALL report `connects_to_cdp=false`

#### Scenario: Cookie reads fail closed without evidence

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action cookie.read --target tab:debug-1 --session session-a --json` runs without owner lease evidence or authorization receipt evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL include `authorization_receipt_required` in blockers
- **AND** it SHALL report `reads_cookies=false`

#### Scenario: JavaScript execution requires active owner lease and authorization receipt

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action js.evaluate --target tab:debug-1 --session session-a --owner-lease-id <lease> --authorization-receipt <receipt> --json` runs with matching active owner lease evidence and current one-task authorization receipt evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `authorization_verified=true`
- **AND** it SHALL report `executes_javascript=false`

#### Scenario: Click, type, navigation, and unknown actions are sensitive by default

- **WHEN** the guard checks `mouse.click`, `keyboard.type`, `page.navigate`, or an unknown action without owner and authorization evidence
- **THEN** each check SHALL fail closed
- **AND** each check SHALL report `dispatch_allowed=false`
- **AND** each check SHALL require owner lease evidence
- **AND** each check SHALL require authorization receipt evidence

### Requirement: OpenCLI governance guard SHALL remain on-demand and require browser owner evidence

The repository SHALL provide a repo-local OpenCLI governance guard that evaluates browser-target actions before any live OpenCLI dispatch can occur.

The guard SHALL keep OpenCLI as an on-demand adapter. Any request that attempts always-on or persistent adapter mode SHALL fail closed.

The guard SHALL require active browser-owner lease evidence for every target-bound OpenCLI action, including read-only inspection. The read-only actions SHALL include `adapter.inventory`, `session.inspect`, `page.snapshot`, and `screenshot.capture`.

The guard SHALL treat cookie reads, JavaScript execution, click, type, navigation, and unknown actions as sensitive. Sensitive actions SHALL require both active browser-owner lease evidence and a current one-task authorization receipt before dispatch is allowed.

The guard SHALL be non-mutating. It SHALL NOT install OpenCLI, start OpenCLI, launch browsers, connect to browser targets, read cookies, execute JavaScript, click, type, navigate, mutate user-level Codex configuration, or emit raw private profile paths.

#### Scenario: Read-only inspection requires a browser-owner lease

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> check --action session.inspect --target tab:opencli-1 --session session-a --json` runs without owner lease evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL report `authorization_required=false`

#### Scenario: Read-only inspection is allowed with an active owner lease

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> check --action session.inspect --target tab:opencli-1 --session session-a --owner-lease-id <lease> --json` runs with matching active owner lease evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `adapter_mode=on-demand`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `connects_to_browser=false`

#### Scenario: Always-on adapter mode is blocked

- **WHEN** the guard checks an OpenCLI action with `--adapter-mode always-on`
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `opencli_must_remain_on_demand` in blockers
- **AND** it SHALL report `autoload_allowed=false`

#### Scenario: Cookie reads fail closed without evidence

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> check --action cookie.read --target tab:opencli-1 --session session-a --json` runs without owner lease evidence or authorization receipt evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL include `authorization_receipt_required` in blockers
- **AND** it SHALL report `reads_cookies=false`

#### Scenario: JavaScript execution requires active owner lease and authorization receipt

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> check --action js.evaluate --target tab:opencli-1 --session session-a --owner-lease-id <lease> --authorization-receipt <receipt> --json` runs with matching active owner lease evidence and current one-task authorization receipt evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `authorization_verified=true`
- **AND** it SHALL report `executes_javascript=false`

#### Scenario: Click, type, navigation, and unknown actions are sensitive by default for OpenCLI

- **WHEN** the guard checks `mouse.click`, `keyboard.type`, `page.navigate`, or an unknown OpenCLI action without owner and authorization evidence
- **THEN** each check SHALL fail closed
- **AND** each check SHALL report `dispatch_allowed=false`
- **AND** each check SHALL require owner lease evidence
- **AND** each check SHALL require authorization receipt evidence

### Requirement: CLI-Anything governance guard SHALL require receipt evidence and harness-generation boundaries

The repository SHALL provide a repo-local CLI-Anything governance guard that validates install/update receipt evidence and harness-generation boundaries before any future user-level CLI-Anything or CLI Hub adaptation is treated as eligible.

The guard SHALL support at least:

- `install-record --receipt-dir <dir> --pin <pin> --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command <cmd> --rollback-pointer <pointer> --json`;
- `validate --receipt <path> --json`;
- `update-plan --current-receipt <path> --new-pin <pin> --staging-dir <path> --smoke-status <status> --json`;
- `update-record --current-receipt <path> --receipt-dir <dir> --new-pin <pin> --staging-dir <path> --smoke-command <cmd> --smoke-status <status> --json`;
- `rollback-plan --receipt <path> --json` - reports rollback evidence without executing rollback;
- `harness-plan --capability <text> --output-dir <path> --target-process <process> --json` - reports harness-generation eligibility without generating or running a live harness.

The guard SHALL keep CLI-Anything as harness-generation support only until install/update receipts, smoke evidence, and rollback evidence exist. It SHALL NOT clone CLI-Anything, perform network fetches, install wrappers, run CLI-Anything, mutate user-level Codex configuration, hard-load bulk skills, control live applications, or emit raw private install/wrapper/state/output paths in default output.

#### Scenario: Pinned CLI-Anything install receipt is written without installing the tool

- **WHEN** `python tools/cli_anything_governance.py install-record --receipt-dir <tmp> --pin v0.1.0 --install-path <path> --wrapper-path <path> --state-path <path> --smoke-command "cli-anything --help" --rollback-pointer <pointer> --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write a `cli-anything.lock.json` receipt
- **AND** it SHALL report path hashes instead of raw private paths
- **AND** it SHALL report `installs_cli_anything=false`, `runs_cli_anything=false`, `hard_loads_skills=false`, and `harness_generation_boundary_only=true`

#### Scenario: CLI-Anything hard-load skill attempts are blocked

- **WHEN** the receipt guard is asked to write an install receipt with hard-loaded skills enabled
- **THEN** it SHALL fail closed with `hard_load_skills_must_be_false`
- **AND** no receipt SHALL be written

#### Scenario: CLI-Anything update pin switch requires smoke evidence and rollback pointer

- **WHEN** `update-plan` receives a valid current receipt but the new smoke status is not `pass`
- **THEN** it SHALL fail closed
- **AND** it SHALL report `pin_switch_allowed=false`
- **AND** it SHALL NOT perform a network fetch

- **WHEN** `update-record` receives a valid current receipt, immutable new pin, and passing smoke evidence
- **THEN** it SHALL write an update receipt
- **AND** the update receipt SHALL include previous receipt id and previous pin rollback evidence

#### Scenario: CLI-Anything harness planning remains generation-only

- **WHEN** `harness-plan --capability <text> --output-dir <path> --target-process WXWork.exe --json` runs without hard-loaded skills
- **THEN** it SHALL return `harness_generation_allowed=true`
- **AND** it SHALL report repo-local source and live-control authorization gates
- **AND** it SHALL NOT run CLI-Anything, control WXWork, hard-load skills, or emit raw private output paths

- **WHEN** `harness-plan` is asked to hard-load skills
- **THEN** it SHALL fail closed with `hard_load_skills_must_be_false`

### Requirement: WeCom CLI governance guard SHALL prefer API/Webhook and fail closed for WXWork GUI automation

The repository SHALL provide a repo-local `wecom-cli` governance guard that models Enterprise WeChat / WeCom / WXWork control boundaries without attaching to `WXWork.exe`, probing local processes, calling live APIs or webhooks, reading message content, sending messages, mutating user-level Codex configuration, or controlling GUI state.

The guard SHALL support at least:

- `api-status --json` - reports the API/Webhook-first posture without probing the process table;
- `webhook-plan --name <name> --secret-ref <ref> --json` - plans webhook usage without calling WeCom or retaining secret values;
- `gui-plan --target-process WXWork.exe --json` - reports GUI gate requirements without live control;
- `gui-check --action <action> --session <id> --authorization-receipt <path> --lease-receipt <path> --json` - fail-closed precheck for sensitive GUI actions.

WXWork GUI actions SHALL require a global WXWork lease receipt, operator authorization receipt, session match, future expiry, and timeout release evidence. Valid receipts MAY allow only dry-run dispatch eligibility in the repo-local MVP; they SHALL NOT cause live GUI control.

#### Scenario: API/Webhook status is requested

- **WHEN** `python tools/wecom_cli_governance.py api-status --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `api_or_webhook_first`
- **AND** it SHALL report no process probe, no GUI control, no message-content read, and no WeCom API call

#### Scenario: Webhook planning receives an inline secret

- **WHEN** `python tools/wecom_cli_governance.py webhook-plan --name ops --secret-ref "secret=<value>" --json` runs
- **THEN** the command SHALL fail closed
- **AND** it SHALL not call a webhook
- **AND** it SHALL not retain the raw secret value in default output

#### Scenario: GUI planning is requested

- **WHEN** `python tools/wecom_cli_governance.py gui-plan --target-process WXWork.exe --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report global lease, operator confirmation, and timeout release requirements
- **AND** it SHALL report live GUI control is not allowed by the repo-local MVP

#### Scenario: GUI attach lacks receipts

- **WHEN** `python tools/wecom_cli_governance.py gui-check --action gui.attach --session session-a --json` runs without receipts
- **THEN** the command SHALL fail closed
- **AND** it SHALL require both operator authorization receipt and global WXWork lease receipt
- **AND** it SHALL report `gui_control_performed=false`

#### Scenario: GUI attach has valid receipts

- **WHEN** `gui-check` receives matching, current operator authorization and global WXWork lease receipts
- **THEN** it SHALL return `dispatch_allowed=true`
- **AND** it SHALL remain `dry_run_only=true`
- **AND** it SHALL report `gui_control_performed=false`
- **AND** it SHALL not emit raw private receipt paths

### Requirement: User-level receipt governance guard SHALL validate authorization, update, rollback, and redaction evidence

The repository SHALL provide a repo-local generic receipt governance guard for user-level MCP, skills, browser, and CLI harness lanes. The guard SHALL validate one-task authorization receipt schema, update receipt schema, rollback pointer presence, smoke evidence, and redaction boundaries without installing tools, calling MCP servers, controlling browsers, reading browser data, mutating user-level Codex configuration, or emitting raw private paths or raw secrets in default output.

The guard SHALL support at least:

- `auth-check --receipt <path> --action <action> --target <target> --session <id> --json` - validates one-task authorization evidence.
- `update-check --receipt <path> --tool-name <name> --owner-lane <lane> --json` - validates install/update evidence.
- `redact-check --receipt <path> --json` - validates sensitive-data redaction boundaries.
- `template --kind authorization --json` - prints the authorization receipt field template.
- `template --kind update --json` - prints the update receipt field template.

Receipt field glossary:

| Field | Meaning |
| --- | --- |
| `action` | Requested sensitive operation. |
| `target` | Resource or adapter target authorized for that operation. |
| `scope` | Allowed action set; it must include the requested operation or `*`. |
| `expiry` | Future timestamp after which the authorization is invalid. |
| `session` | Current Codex session or owner session id. |
| `operator_confirmation` | Boolean proof that the operator approved the sensitive action. |
| `tool_name` | User-level helper or adapter being installed or updated. |
| `installed_version` | Pinned version, tag, or commit of the installed artifact. |
| `source_url` | Public source location, without credentials. |
| `install_path`, `wrapper_path`, `state_path` | Private local paths that default output must hash or redact. |
| `smoke_test_command`, `smoke_test_result` | Repeatable validation command and pass/fail evidence. |
| `updater_command` | Pin-aware update command. |
| `rollback_pointer` | Previous version, backup directory, or rollback reference. |
| `owner_lane` | Owning lane such as `skills2cli`, `mcp2cli`, or `browser`. |
| `redaction_status` | Evidence that secrets, cookies, tokens, raw browser data, message contents, API keys, passwords, and plugin description dumps are absent or redacted. |

#### Scenario: Authorization receipt is missing required fields

- **WHEN** `python tools/user_level_receipt_governance.py auth-check --receipt <path> --action browser.click --target tab:123 --session session-a --json` runs on an incomplete receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report missing authorization receipt fields
- **AND** it SHALL report no user-level mutation, no external tool run, and no browser-data read

#### Scenario: Valid authorization receipt is summarized safely

- **WHEN** `auth-check` receives a matching future-expiry authorization receipt with operator confirmation
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `authorization_valid=true`
- **AND** it SHALL emit a receipt path hash instead of the raw receipt path

#### Scenario: Update receipt lacks rollback or passing smoke evidence

- **WHEN** `python tools/user_level_receipt_governance.py update-check --receipt <path> --tool-name skills2cli --owner-lane skills2cli --json` runs on an update receipt without rollback pointer or passing smoke evidence
- **THEN** the command SHALL fail closed
- **AND** it SHALL report rollback and smoke blockers

#### Scenario: Valid update receipt hashes private paths and rollback pointer

- **WHEN** `update-check` receives a valid update receipt with install, wrapper, state, smoke, updater, owner-lane, redaction, and rollback evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `rollback_ready=true`
- **AND** it SHALL emit hashes for install path, wrapper path, state path, and rollback pointer

#### Scenario: Redaction check detects raw sensitive payloads

- **WHEN** `python tools/user_level_receipt_governance.py redact-check --receipt <path> --json` runs on a receipt containing cookies, inline token values, message contents, or plugin description dumps
- **THEN** the command SHALL fail closed
- **AND** it SHALL report redaction findings
- **AND** it SHALL not read browser data or emit raw secrets in default output

### Requirement: Governance plan SHALL use the executable modern Comet structure

The user-level MCP, skills, browser automation, and CLI harness governance plan SHALL include worker-facing Goal, Architecture, and Tech Stack opening blocks plus execution-oriented sections for file ownership, readiness, task backlog, acceptance, evidence, rollback, and risks.

#### Scenario: Modern sections are present

- **WHEN** the plan is reviewed manually
- **THEN** it SHALL include Goal, Architecture, Tech Stack, file responsibility map, definition of ready, task-level backlog, acceptance criteria, required evidence, rollback, and risks
- **AND** it SHALL preserve Token/risk priority, authorization receipt, update receipt, evidence redaction, port registry/lease, codex-port allocator, pending_bind, registry_revision, 39000-39299, 40000-40999, OpenSpec slice, and fail closed governance markers

#### Scenario: Runtime lanes remain risk-gated

- **WHEN** a lane lacks install, smoke, receipt, or rollback evidence
- **THEN** it SHALL stay below active
- **AND** sensitive MCP, browser, CDP Bridge, OpenCLI, CLI-Anything, and WeCom actions SHALL require current authorization receipt evidence

