## ADDED Requirements

### Requirement: Legacy durable residue classification SHALL be inspectable and non-adopting

The cleanup and reconciliation workflow SHALL expose a read-only classification surface for repo-local legacy durable residue under `.omx/state/`.

At minimum, each classification record SHALL include:

- `kind` - stable residue class.
- `path` - source path for the residue or authority record.
- `state_class` - safety grouping for cleanup or inspection.
- `safe_next_action` - operator-safe next action.
- `auto_adopt_allowed` - whether this record can authorize adoption by itself.
- `reason` - source-attributed explanation.

For the first rollout, unmanaged residue and selector evidence SHALL NOT authorize automatic adoption by itself; their `auto_adopt_allowed` value SHALL be false.

#### Scenario: Legacy residue scan sees unmanaged native and completed LangGraph state

- **WHEN** repo-local `.omx/state/` contains a non-empty unmanaged native team directory
- **AND** it contains a completed LangGraph backend/thread record
- **THEN** the classification output SHALL report the unmanaged native directory as protected residue with `manual-inspection-required`
- **AND** it SHALL report the completed LangGraph state as inspect-or-archive evidence that must not be auto-resumed
- **AND** neither record SHALL allow automatic adoption by itself

#### Scenario: Legacy residue scan sees stale and current selectors

- **WHEN** `.omx/state/selectors/active.json` points to a different repository root
- **THEN** the classification output SHALL classify it as a stale selector with a refresh-or-ignore safe next action
- **AND** it SHALL not treat that selector as current adoption authority

- **WHEN** `.omx/state/selectors/active.json` points to the current repository root or omits a conflicting repository root
- **THEN** the classification output SHALL classify it as active current selector authority evidence
- **AND** it SHALL still not allow automatic adoption by that record alone
