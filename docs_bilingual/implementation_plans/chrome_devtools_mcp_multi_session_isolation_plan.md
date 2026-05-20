---
doc_id: chrome_devtools_mcp_multi_session_isolation_plan
lang: en
doc_class: implementation_plan
status: draft
---

# Chrome DevTools MCP Multi-Project Multi-Session Isolation Plan

## 1. Background

Multiple projects and multiple Codex sessions must not share the same Chrome `userDataDir` when they use `chrome-devtools-mcp`.
The usual default directory is:

```text
C:\Users\lenovo\.cache\chrome-devtools-mcp\chrome-profile
```

If multiple MCP servers or sessions share this directory, Chrome profile locking can block later sessions with an error like:

```text
The browser is already running for ... chrome-profile. Use --isolated to run multiple browser instances.
```

## 2. Why bare `--isolated` is not enough

`--isolated` lets each MCP client session use a separate temporary Chrome profile and avoids profile lock contention.
However, bare `--isolated` has a long-running operational risk:

- if an old session does not exit cleanly, its Chrome instance may remain alive;
- a new session may start another Chrome instance;
- over time Chrome windows or `chrome.exe` processes may accumulate;
- temporary profile cleanup normally depends on the browser closing cleanly, so it is not lifecycle governance.

Therefore the production default should not be only:

```toml
args = ["-y", "chrome-devtools-mcp@latest", "--isolated"]
```

It should become a managed isolation mode.

## 3. Recommended target mode

Recommended target mode:

```text
chrome-devtools = isolated-session-managed
```

Meaning:

1. each Codex session uses an independent Chrome profile;
2. the same session tries to reuse its own Chrome instance;
3. a new session does not reuse an old session's temporary profile;
4. startup scans and cleans clearly stale managed instances;
5. a maximum active instance limit prevents long-term accumulation;
6. only Chrome processes that clearly belong to managed `chrome-devtools-mcp` profiles are managed;
7. the user's daily Chrome is never closed, killed, or taken over.

## 4. Managed wrapper design

Future configuration should not call bare `npx chrome-devtools-mcp@latest` directly. It should point to a user-level wrapper:

```toml
[mcp_servers.chrome-devtools]
command = "powershell"
args = [
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File",
  "C:\\Users\\lenovo\\.codex\\tools\\chrome-devtools-mcp-managed.ps1",
  "--mode", "isolated-session"
]
```

The wrapper then starts:

```powershell
npx -y chrome-devtools-mcp@latest --isolated
```

Or it can use a session-specific `--user-data-dir` when an auditable profile path is required.

## 5. Lease records

Each managed Chrome DevTools MCP instance should write a lease file on startup.
Suggested directory:

```text
C:\Users\lenovo\.codex\state\chrome-devtools-mcp\leases\
```

Each lease should record at least:

- `lease_id`;
- `project_path`;
- `codex_session_id` or available session namespace;
- `mcp_server_pid`;
- `chrome_root_pid`;
- `user_data_dir`;
- `started_at`;
- `last_seen_at`;
- `mode`: `isolated-session` / `project-profile`;
- `status`: `active` / `stale` / `cleaned` / `unknown`;
- `owner_command_hash` or command summary;
- `cleanup_policy` for the safe cleanup strategy and retention rules.

## 6. Pre-start cleanup rules

Before starting a new instance, run a read-only scan:

1. read the lease directory;
2. check whether `mcp_server_pid` still exists;
3. check whether `chrome_root_pid` still exists;
4. check whether the Chrome command line contains the managed profile path;
5. check whether the lease exceeds the stale TTL;
6. clean only when the owner process is gone and Chrome clearly belongs to the managed profile;
7. mark the lease as `cleaned` after cleanup instead of deleting evidence immediately.

Forbidden behavior:

- do not kill all `chrome.exe` processes without command-line or lease ownership evidence;
- do not clean the normal Chrome user profile;
- do not clean Chrome instances outside the managed directory;
- do not treat `--isolated` as lifecycle management.

## 7. Instance limit

Suggested defaults:

```text
max_active_managed_instances = 3
stale_ttl_minutes = 120
```

When active managed instances exceed the limit:

1. prefer reporting and refusing to start another instance;
2. or clean only confirmed stale instances;
3. do not clean unknown-state instances that may still be active;
4. when human confirmation is needed, print candidate leases and PIDs instead of mutating them directly.

## 8. Mode selection

### 8.1 Normal Codex browser automation

Use `isolated-session-managed`.

Suitable for:

- local web debugging;
- DOM / console / network inspection;
- one-off UI verification;
- concurrent multi-project and multi-session work.

### 8.2 Projects that need persistent login state

Use a project-specific profile:

```text
C:\Users\lenovo\.cache\chrome-devtools-mcp\profiles\<project-slug>
```

Restrictions:

- the same project profile can be used by only one session at a time;
- concurrent sessions should still use independent session profiles;
- persistent login profiles must be marked as long-lived profiles and must not have their directories removed by stale cleanup.

## 9. Validation and audit

Future implementation should add checkers that verify at least:

- `config.toml` no longer uses the shared default `chrome-profile` directly;
- the managed wrapper exists;
- the lease directory exists and is readable;
- cleanup matches only managed profiles;
- normal Chrome cannot be killed by mistake;
- stale cleanup keeps receipts;
- multiple sessions do not contend for the same `userDataDir`.

## 10. Current conclusion

Bare `--isolated` can solve profile lock contention, but it can create long-term window/process accumulation.
The long-term recommended direction is:

```text
--isolated + session ownership lease + stale cleanup + max instance limit
```

This is the production-grade default direction for independent Chrome DevTools MCP use across multiple projects and sessions.
