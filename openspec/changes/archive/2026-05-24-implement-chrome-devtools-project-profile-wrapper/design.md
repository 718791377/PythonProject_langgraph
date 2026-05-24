## Design

### Contract boundary

This slice is a repository-local wrapper contract only. It models how a future user-level `chrome-devtools-mcp` wrapper must treat long-lived project profiles, but it does not install a wrapper, start Chrome, connect to CDP, or read browser data.

### Project-profile ownership

Project-profile commands derive a stable project profile path under the wrapper state directory:

```text
profiles/project/<project>/<profile>
```

The path is never emitted raw in default output. The wrapper emits sanitized path hints and profile-path hashes.

`project-profile reserve` delegates lease creation to `tools/browser_owner_registry.py` using:

```text
owner_class=codex-managed-project
target=chrome-devtools-mcp:project:<project>:<profile>
```

The browser owner registry already enforces authorization for `codex-managed-project`, target exclusivity, and same profile-path exclusivity.

### Authorization and live-start gates

Project-profile reserve requires `--authorization-receipt`. Project-profile live start validates the receipt before checking install receipt state. This preserves the more sensitive logged-in-profile boundary even though live start is not implemented in the repo-local MVP.

Live start fail-closed order:

1. missing or invalid project-profile authorization receipt => `project_profile_authorization_required`;
2. valid authorization but missing install receipt => `install_receipt_required`;
3. both receipts present => `live_start_not_implemented_repo_local_mvp`.

All three cases report `start_performed=false` and do not mutate registry state.

### Retention and cleanup

Project profiles are long-lived project assets. The wrapper records:

```text
profile_retention=long-lived-project-profile
cleanup_allowed_after_stale_evidence=false
```

Cleanup remains deferred to a later safe cleanup dry-run slice. This slice explicitly protects project profiles from cleanup.

### Security and privacy

Default output is sanitized through the wrapper's `sanitize_json` and `sanitize_text` helpers. It does not include raw private paths, cookies, tokens, browser data, user-level config contents, or personal Chrome profile data.

### CI and OpenSpec

The existing `chrome_devtools_mcp_managed.test.py` manifest entry covers this expanded test file. The stable spec gains a project-profile requirement while this completed change is archived immediately because the implementation and tests land in the same local package.
