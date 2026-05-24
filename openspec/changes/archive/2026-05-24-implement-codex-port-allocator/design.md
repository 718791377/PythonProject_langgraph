# Design: codex-port allocator MVP

## Boundaries

`codex-port` is repo-local in this slice. Tests pass a temporary `--state-dir`; runtime wrappers may later set `CODEX_PORT_STATE_DIR` or install a user-level wrapper.

## Registry model

The registry is JSON with `schema_version`, monotonic `registry_revision`, and a `leases` array. Lease records include owner, project slug, tool, host, port, lease id, PID, timestamps, TTL, lease expiry, owner session, purpose, status, and range.

## Range model

`tools/codex_port_ranges.json` defines:

- `codex-helper`: `39000-39299`;
- `codex-opencli`: `39300-39499`;
- `codex-browser`: `39500-39699`;
- `codex-reserved`: `39700-39999`;
- `openclaw`: `40000-40999`.

Owner/range mismatches fail closed.

## Lifecycle

`reserve` writes a `pending_bind` lease and receipt. `renew --activate` can promote a matching pending lease to `active`. `release` requires matching `owner_session`. `import-legacy` records openclaw/external reservations as `legacy_reserved`. `gc --dry-run` reports stale candidates without mutation; non-dry-run GC marks candidates `stale` and writes a receipt.

## Safety

The allocator uses an exclusive registry lock for state writes and atomic JSON replacement for registry persistence. It probes local port availability by attempting a local bind and skips occupied ports. It never kills, attaches to, or mutates existing port-holder processes.
