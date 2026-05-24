## Design

The browser owner registry is intentionally a local state coordinator, not a browser automation adapter.

### State model

The registry stores active and historical leases in a JSON file under the selected state directory. Tests pass `--state-dir`; later user-level wrappers may use `C:\Users\lenovo\.codex\state\browser-automation`.

Each lease records:

- `lease_id`;
- `owner_class`;
- `project_slug`;
- `session_id`;
- `target`;
- `profile_path` in local runtime state only;
- `profile_path_hash` for compact output and repository evidence;
- `lease_expiry`;
- `status`;
- optional authorization summary.

### Safety boundaries

- `codex-managed-isolated` can be reserved without one-task authorization.
- `codex-managed-project` requires an authorization receipt and is exclusive by profile-path hash.
- `human-owned` cannot be reserved as a Codex-managed lease.
- `human-delegated` requires an authorization receipt and remains one-task scoped.
- Any already-owned target blocks another active owner.
- Cleanup is dry-run only and only reports stale `codex-managed-isolated` profiles as cleanup candidates.

### Non-goals

The helper never starts browsers, never connects to CDP, never changes Codex config, and never deletes profile directories.
