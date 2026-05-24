## Design

### Contract boundary

This slice keeps cleanup as a dry-run-only repository-local contract. It does not delete files or mutate user-level runtime configuration. The intent is to make cleanup decisions visible and testable before any later real cleanup lane exists.

### Wrapper command shape

`tools/chrome_devtools_mcp_managed.py` exposes:

```text
stale-scan --dry-run --json
cleanup dry-run --json
```

Both commands use the wrapper state directory and delegate to the owner registry under the wrapper's `owner-registry` subdirectory.

### Candidate classification

The browser owner registry already knows owner classes:

- `codex-managed-isolated` - temporary Codex-managed isolated browser profile ownership.
- `codex-managed-project` - reusable project-profile browser ownership that must be retained.
- `human-owned` - personal browser assets that remain outside managed cleanup scope.
- `human-delegated` - user-delegated browser assets that must be protected from cleanup.

Only expired `codex-managed-isolated` leases are cleanup candidates. Expired `codex-managed-project` and `human-delegated` leases are listed as protected profiles. `human-owned` cannot be reserved as a managed lease and remains outside cleanup scope.

### Safety invariants

The wrapper reports all maintenance commands as:

- `dry_run=true` - confirms the command is only previewing maintenance action.
- `registry_mutated=false` - confirms owner registry state was not changed.
- `cleanup_performed=false` - confirms no cleanup execution occurred.
- `human_owned_cleanup_performed=false` - confirms human-owned or delegated assets were not cleaned.
- `managed_profiles_only=true` - confirms cleanup candidates are limited to managed profile classes.

Default output is sanitized and uses compact lease data from the owner registry. Raw private profile paths are not emitted.

### Deferred work

Real cleanup execution remains deferred. A future cleanup execution slice must require stronger stale evidence, user-level install receipts, rollback evidence, and explicit cleanup-specific approval before deleting any profile directory.
