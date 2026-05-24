# Chrome DevTools MCP Project-Profile Wrapper MVP Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_user_codex_config: false
- launches_browser: false
- connects_to_cdp: false
- reads_cookies: false
- writes_human_owned_profile: false
- cleanup_performed: false
- project_profile_cleanup_allowed: false
- raw_profile_paths_in_default_output: false
- project_profile_reserve_without_authorization: fail-closed
- project_profile_live_start_without_authorization: fail-closed
- project_profile_live_start_without_install_receipt: fail-closed
- project_profile_live_start_with_install_receipt: deferred/fail-closed
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python tools/chrome_devtools_mcp_managed.py project-profile plan --project pythonproject-langgraph --profile dev-login --session smoke --purpose smoke --json
python test/chrome_devtools_mcp_managed.test.py
```

## Deferred to later slices

- user-level `chrome-devtools-mcp` managed wrapper installation;
- browser launch and CDP connection behavior;
- safe cleanup dry-run and cleanup execution;
- CDP Bridge/OpenCLI write-action gates;
- user-level tool update receipts and wrapper smoke evidence.
