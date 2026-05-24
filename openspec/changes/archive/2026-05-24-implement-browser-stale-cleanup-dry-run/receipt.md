# Browser Stale Scan And Cleanup Dry-Run Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_user_codex_config: false
- launches_browser: false
- connects_to_cdp: false
- reads_cookies: false
- writes_human_owned_profile: false
- cleanup_performed: false
- cleanup_execution_implemented: false
- cleanup_dry_run_only: true
- project_profile_cleanup_allowed: false
- human_delegated_cleanup_allowed: false
- raw_profile_paths_in_default_output: false
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python test/browser_owner_registry.test.py
python test/chrome_devtools_mcp_managed.test.py
python tools/chrome_devtools_mcp_managed.py --state-dir .tmp/chrome-devtools-mcp-managed-smoke stale-scan --dry-run --json
python tools/chrome_devtools_mcp_managed.py --state-dir .tmp/chrome-devtools-mcp-managed-smoke cleanup dry-run --json
```

## Deferred to later slices

- user-level `chrome-devtools-mcp` managed wrapper installation;
- browser launch and CDP connection behavior;
- real cleanup execution;
- CDP Bridge/OpenCLI write-action gates;
- user-level tool update receipts and wrapper smoke evidence.
