## Why

LangGraph can be installed, enabled, selected, and ready while a repository has not yet refreshed its repo-local active selector at `.omx/state/selectors/active.json`. Current durable-state status output does not make that gap explicit enough, which can make a missing selector look like LangGraph backend unavailability or a silent `native_omx` downgrade.

## What Changes

- Extend the read-only durable-state status helper projection with selector status fields.
- Report the selected/default backend and whether that backend is ready independently from repo-local durable state presence.
- When the active selector is missing while the selected backend is ready, report a selector refresh gap instead of downgrading or auto-adopting compatibility records.
- Add regression coverage for the no-state, LangGraph-ready case and preserve read-only behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codex-user-level-team-mode-automatic-team-routing`: clarify and enforce status-helper reporting for missing active selectors while LangGraph is selected and ready.

## Impact

- `tools/install-codex-user-level-team-mode.ps1`: generated `codex-durable-state-status.ps1` runtime projection and text output.
- `test/install-codex-user-level-team-mode.test.ps1`: regression coverage for missing active selector with LangGraph selected and ready.
- `openspec/changes/enforce-active-selector-status-helper/specs/codex-user-level-team-mode-automatic-team-routing/spec.md`: delta requirement for the status-helper behavior.

## Scope controls

- `impact_scope`: user-level helper generation and tests only.
- `explicit_non_goals`: no durable team launch, no `.omx/state` mutation from status inspection, no user-level LangGraph install or upgrade, and no adoption of compatibility records as active selectors.
- `rollout_sequence`: update spec -> update helper projection -> add regression tests -> run targeted validation -> run repository gates.
- `rollback_plan`: revert this change to restore the previous durable-state status projection without changing repo-local durable state.
- `validation_path`: OpenSpec guard, install-team-mode regression test, and `git diff --check`.
- `mainline_classification`: existing mainline follow-up under automatic orchestration routing enforcement.
