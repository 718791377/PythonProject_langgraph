## Design

### Contract boundary

This slice implements a governance guard only. The helper classifies CDP Bridge actions and returns dispatch decisions. It does not perform browser automation or inspect live browser state.

### Read-only default

The guard allows these actions without owner or authorization evidence because they are inventory-oriented and non-mutating:

- `tab.list` - enumerates tabs without reading cookies or changing state.
- `dom.scan` - scans DOM structure without JavaScript execution or mutation.
- `screenshot.capture` - captures a screenshot without clicks, typing, or navigation.
- `inventory` - reports bridge inventory without dispatching browser actions.

### Sensitive-action gate

The guard treats these actions as sensitive:

- `cookie.read` - would read cookies if dispatched by a live bridge.
- `js.evaluate` - would execute JavaScript if dispatched by a live bridge.
- `mouse.click` - would click inside a browser if dispatched by a live bridge.
- `keyboard.type` - would type into a browser if dispatched by a live bridge.
- `page.navigate` - would navigate a browser if dispatched by a live bridge.
- unknown action names - are treated as sensitive by default.

Sensitive actions require both active browser-owner lease evidence and a current authorization receipt. Missing, expired, mismatched, or malformed evidence blocks dispatch.

### Owner evidence

The guard reads browser owner registry state from the configured owner-registry directory. It accepts only active, unexpired leases matching the requested target and session. Allowed sensitive owner classes are `codex-managed-isolated`, `codex-managed-project`, and `human-delegated`; `human-owned` remains outside managed dispatch.

### Safety invariants

The helper reports all checks as governance-only:

- `governance_check_only=true` - confirms the helper only decides whether dispatch is allowed.
- `launches_browser=false` - confirms the helper never starts Chrome.
- `connects_to_cdp=false` - confirms the helper never contacts CDP.
- `reads_cookies=false` - confirms the helper itself never reads cookies.
- `mutates_browser_state=false` - confirms the helper never clicks, types, navigates, or executes JavaScript.
- `raw_profile_paths_in_output=false` - confirms default output is sanitized.

### Deferred work

OpenCLI enforcement, live CDP Bridge dispatch, user-level wrapper installation, and user-level smoke tests remain deferred to later slices.
