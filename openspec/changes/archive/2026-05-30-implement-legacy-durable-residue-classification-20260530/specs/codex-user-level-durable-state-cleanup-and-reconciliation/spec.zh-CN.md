# Delta Spec??????

### Requirement: Legacy durable residue classification SHALL be inspectable and non-adopting

Cleanup and reconciliation workflow SHALL expose a read-only classification surface for repo-local legacy durable residue under `.omx/state/`.

Each classification record SHALL include at least `kind`, `path`, `state_class`, `safe_next_action`, `auto_adopt_allowed`, and `reason`. In the first rollout, unmanaged residue and selector evidence SHALL NOT authorize automatic adoption by itself; `auto_adopt_allowed` SHALL be false.

#### Scenario: Legacy residue scan sees unmanaged native and completed LangGraph state
- **WHEN** repo-local `.omx/state/` contains a non-empty unmanaged native team directory
- **AND** it contains a completed LangGraph backend/thread record
- **THEN** classification output SHALL report the unmanaged native directory as protected residue with `manual-inspection-required`
- **AND** it SHALL report completed LangGraph state as inspect-or-archive evidence that must not be auto-resumed
- **AND** neither record SHALL allow automatic adoption by itself

#### Scenario: Legacy residue scan sees stale and current selectors
- **WHEN** `.omx/state/selectors/active.json` points to a different repository root
- **THEN** classification output SHALL classify it as a stale selector with a refresh-or-ignore safe next action
- **AND** it SHALL not treat that selector as current adoption authority

- **WHEN** `.omx/state/selectors/active.json` points to the current repository root or omits a conflicting repository root
- **THEN** classification output SHALL classify it as active current selector authority evidence
- **AND** it SHALL still not allow automatic adoption by that record alone
