## MODIFIED Requirements

### Requirement: Automatic durable routing SHALL choose the effective lane per task flow from enabled capabilities
Automatic durable routing SHALL choose the effective lane per task flow from the enabled orchestration capability set.

It SHALL not require a global backend-family switch every time the task flow is better suited to another enabled lane.

When scoped durable activation exists, it SHALL use that scoped activation as the authoritative activation source for future-session durable decisions.

Legacy repo-local durable artifacts MAY remain inspectable, but they SHALL NOT dominate future-session lane selection only because a legacy tracked record or `thread_id` exists.

#### Scenario: Worker-centric task flow uses native_omx while LangGraph remains enabled

- **WHEN** the layered capability set enables both oh-my-codex durable features and LangGraph
- **AND** the current task flow is better suited to worker-centric durable execution
- **THEN** the automatic durable routing layer SHALL choose `native_omx` as the effective lane
- **AND** it SHALL not require LangGraph capability to be globally disabled first

#### Scenario: Preserved legacy LangGraph backend record does not dominate a future unrelated task flow

- **WHEN** a repository contains a preserved legacy LangGraph backend record
- **AND** no scoped activation selector declares that record active for the current future session
- **THEN** automatic durable routing SHALL treat that record as inspectable legacy state rather than as the authoritative effective lane
- **AND** it SHALL not auto-resume or auto-select LangGraph only because the legacy tracked record exists

### Requirement: Automatic durable routing SHALL honor cleanup and reconciliation classification
Automatic durable-team routing SHALL honor cleanup and reconciliation classification instead of silently treating stale or unmanaged residue as active tracked durable state.

At minimum:

- safe empty residue MAY be ignored or cleaned through the approved reconciliation path
- empty unmanaged native residue SHALL NOT by itself force `manual-inspection-required`
- unmanaged residue SHALL NOT be auto-adopted as tracked state
- protected or ambiguous residue SHALL force a manual-inspection-required or equivalent safe decision

#### Scenario: Empty unmanaged native residue exists beside a tracked durable backend
- **WHEN** a tracked durable backend exists
- **AND** empty unmanaged native team residue is also present
- **THEN** automatic durable routing SHALL not auto-adopt that residue as tracked state
- **AND** it SHALL preserve a safe routing decision that treats the residue as cleanup or reconciliation context rather than as the active durable backend

#### Scenario: Empty unmanaged native residue does not block future native launch
- **WHEN** a repository contains empty unmanaged native team directories but no non-empty unmanaged native residue
- **AND** the desired future-session durable decision is a native launch, reuse, or switch
- **THEN** automatic durable routing SHALL ignore that empty residue as a blocker
- **AND** it SHALL not force `manual-inspection-required` only because those unmanaged directories exist
