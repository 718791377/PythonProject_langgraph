## ADDED Requirements

### Requirement: Durable-state status SHALL report missing active selectors as refresh gaps

`codex-durable-state-status.ps1` SHALL report selected-backend readiness separately from repo-local active-selector presence.

When LangGraph is the selected/default durable backend, LangGraph is ready, and `.omx/state/selectors/active.json` is missing, the status output SHALL report a selector refresh gap. It SHALL NOT mark the backend unavailable solely because the selector is missing, and SHALL NOT silently downgrade the selected backend to another backend family.

The status output SHALL expose, at minimum:

- `backend_default` - the durable backend family selected as the current default.
- `backend_ready` - whether the selected default backend is ready to run.
- `selector_authority` - the canonical repo-local active selector path.
- `active_selector_status` - the inspected active selector classification.
- `selector_refresh_gap` - whether the ready default backend lacks a refreshed active selector.
- `selector_refresh_gap_reason` - the stable machine-readable reason for the refresh gap.

#### Scenario: LangGraph is ready but the active selector is missing

- **WHEN** the user-level durable backend selector is `langgraph`
- **AND** LangGraph is installed, enabled, selected, and ready
- **AND** the inspected repository does not contain `.omx/state/selectors/active.json`
- **THEN** `codex-durable-state-status.ps1 -Json` SHALL report `backend_default` as `langgraph`
- **AND** it SHALL report `backend_ready` as `true`
- **AND** it SHALL report `active_selector_status` as `missing`
- **AND** it SHALL report `selector_refresh_gap` as `true`
- **AND** it SHALL keep `selected_backend` as `langgraph`
- **AND** it SHALL NOT create `.omx` in the inspected repository
