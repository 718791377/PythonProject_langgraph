## Design

The implementation is a projection-only change in the generated helper runtime. It does not create selectors, refresh selectors, or mutate repo-local durable state.

`Get-CodexUserLevelInspectableDurableState` already reads the repo-local active selector, compatibility records, user-level backend selection, and capability readiness. This change adds a small selector-status projection after capability readiness is computed:

- `backend_default`: the selected user-level durable backend reported by the compatibility backend selector.
- `backend_ready`: whether the selected backend's readiness record is ready.
- `selector_authority`: the canonical selector path, `.omx/state/selectors/active.json`.
- `active_selector_status`: `missing`, `active_scoped`, `released`, `cross_repo`, or `unscoped_or_invalid`.
- `active_selector`: the read selector record for inspection.
- `selector_refresh_gap`: true when the selected/default backend is ready but the active selector is missing.
- `selector_refresh_gap_reason`: a stable reason string for operator-facing diagnosis.

The key behavior is that backend readiness remains derived from installed/enabled/selected capability state, not from active-selector presence. Missing active selector is therefore a refresh gap, not proof that LangGraph is unavailable and not permission to fall back silently to `native_omx`.

The generated `codex-durable-state-status.ps1` text output is extended with the new fields while JSON output keeps the full projection. Tests simulate a ready shared LangGraph runtime by creating the expected shared Python path in the isolated Codex home; the status helper must still avoid creating `.omx` in a no-state repository.
