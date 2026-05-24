## Context

`mcp2cli` is the third implementation slice from the user-level MCP/skills/browser/CLI governance plan. It gives Codex a compact repository-local MCP discovery surface while preserving fail-closed boundaries for sensitive calls.

## Design

### Command surface

The MVP exposes these repository-local commands:

```text
python tools/mcp2cli.py list --profile <profile> --json
python tools/mcp2cli.py search <query> --profile <profile> --json
python tools/mcp2cli.py show <tool> --profile <profile> --json
python tools/mcp2cli.py show <tool> --profile <profile> --full --json
python tools/mcp2cli.py call <tool> --profile <profile> --json --args <json>
python tools/mcp2cli.py call <tool> --profile <profile> --json --args <json> --authorization-receipt <path>
```

### Registry

The allowed-profile registry is a repository-local JSON file. It records profile ids, allowed tools, compact summaries, categories, risk levels, sensitive categories, and whether call authorization is required.

Default registry content includes:

- `core-readonly` for low-risk repository/governance discovery metadata;
- `browser-readonly` for browser inventory discovery that remains sensitive for calls;
- `remote-infra-readonly` for remote-infrastructure discovery that remains sensitive for calls.

### Compact output

`list`, `search`, and default `show` emit only compact fields: profile id, tool id, source, category, risk level, sensitive categories, summary, and availability. Full metadata is hidden unless `--full` is explicit.

### Call gating

The MVP does not invoke real MCP servers. `call` is a guarded facade:

- low-risk tools with `call.requires_authorization=false` can return a deterministic dry-run-safe facade result;
- tools with sensitive categories or `call.requires_authorization=true` fail closed unless an authorization receipt is supplied;
- even with a valid receipt, this repo-local MVP returns guarded evidence instead of executing sensitive tools.

Authorization receipt validation requires action, target, scope, expiry, session, and operator confirmation fields. Missing or mismatched receipts fail closed.

### Privacy boundary

The helper redacts private paths, secrets, tokens, cookies, and password-like values from JSON output, command arguments, and receipt error summaries. It does not store raw call arguments in repository evidence.

## Alternatives considered

- Installing the upstream `mcp2cli` user-level package now: deferred because this slice is the repository-local governance and test MVP.
- Calling live MCP servers from tests: rejected because tests must be deterministic, local, and low-risk.
- Allowing medium-risk read-only browser calls without receipts: rejected because browser state can include user-sensitive information.

## Risks

- The initial registry is intentionally small and advisory. Later slices must expand profiles with explicit risk and receipt coverage.
- The facade shape may need adapter changes before user-level installation. This slice preserves the safety contract first.
