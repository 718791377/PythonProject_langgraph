# CDP Bridge Read-Only Defaults Local Receipt

- status: implemented-local
- user_level_install_performed: false
- mutates_config: false
- edits_user_codex_config: false
- launches_browser: false
- connects_to_cdp: false
- reads_cookies: false
- executes_javascript: false
- clicks_or_types: false
- navigates_browser: false
- live_dispatch_implemented: false
- read_only_default_guard: true
- sensitive_actions_fail_closed: true
- requires_owner_lease_for_sensitive_actions: true
- requires_authorization_receipt_for_sensitive_actions: true
- raw_profile_paths_in_default_output: false
- rollback: revert the repository commit or reset local main to the pre-merge rollback ref

## Smoke commands

```text
python test/cdp_bridge_governance.test.py
python tools/cdp_bridge_governance.py --state-dir .tmp/cdp-bridge-governance-smoke check --action tab.list --target tab:debug-1 --session session-a --json
python tools/cdp_bridge_governance.py --state-dir .tmp/cdp-bridge-governance-smoke check --action cookie.read --target tab:debug-1 --session session-a --json
```

## Deferred to later slices

- live CDP Bridge dispatch;
- OpenCLI on-demand enforcement;
- user-level CDP Bridge or OpenCLI wrapper installation;
- user-level smoke evidence;
- user-level tool update receipts and rollback pointers.
