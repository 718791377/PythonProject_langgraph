## Design

The managed wrapper is intentionally a repo-local contract and validation harness, not the final user-level `chrome-devtools-mcp` launcher.

### Command model

The wrapper exposes one implemented mode in this slice:

- `isolated-session plan` builds a sanitized start plan and does not mutate registry state.
- `isolated-session reserve` writes an owner lease through `browser_owner_registry.py` and writes a sanitized wrapper receipt.
- `isolated-session start --dry-run` produces the same non-mutating start plan for future launcher wiring.
- `isolated-session start` without `--install-receipt` fails closed with `install_receipt_required`.
- `isolated-session start` with an install receipt still fails closed in this repo-local MVP with `live_start_not_implemented_repo_local_mvp`.
- `isolated-session release` delegates ownership release to the owner registry and writes a wrapper release receipt.
- `isolated-session status` lists sanitized managed isolated leases.

### State model

By default, future user-level installations may store state under:

```text
C:\Users\lenovo\.codex\state\browser-automation\chrome-devtools-mcp
```

Tests pass `--state-dir` and do not touch the user-level state directory. The wrapper uses an `owner-registry` subdirectory for browser-owner leases and a `receipts` subdirectory for wrapper receipts.

### Safety boundaries

The wrapper response includes a safety block that records:

- `launches_browser=false`;
- `connects_to_cdp=false`;
- `mutates_user_codex_config=false`;
- `reads_cookies=false`;
- `writes_human_owned_profile=false`;
- `raw_profile_paths_in_output=false`;
- `requires_browser_lane_authorization_for_live_start=true`, which records that a later live launcher needs explicit browser-lane authorization.

The wrapper stores raw profile paths only in local runtime state and returns deterministic hashes in default output. Receipt paths are represented by hashes.

### Non-goals

Project-profile mode, live start, user-level wrapper installation, port allocator integration for a real local listener, stale cleanup execution, and browser-sensitive actions are deferred to later governed slices.
