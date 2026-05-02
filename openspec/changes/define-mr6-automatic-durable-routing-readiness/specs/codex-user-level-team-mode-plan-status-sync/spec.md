## ADDED Requirements

### Requirement: MR 6 readiness review SHALL reconcile automatic routing evidence before opening duplicate runtime hookup work
When a durable-state rollout queue names MR 6 as the next automatic durable routing hookup, the plan-status sync process SHALL first check whether the repository already contains stable automatic routing specs, generated helper source, and tests that satisfy that hookup. If the evidence exists, the queue SHALL mark MR 6 readiness review as complete and SHALL direct any future runtime exercise into a separate explicit smoke or adoption-gate slice.

#### Scenario: Automatic routing evidence already exists
- **WHEN** `codex-user-level-team-mode-automatic-team-routing` already specifies `omx-team-auto.ps1` behavior
- **AND** repository tests cover effective lane selection, selector safety, empty residue handling, native_omx lifecycle actions, and LangGraph graph-signal selection
- **THEN** the durable-state rollout plan SHALL not keep MR 6 labeled as an unimplemented automatic durable routing hookup
- **AND** it SHALL point cold-start sessions at a future explicit live smoke or adoption-gate step instead of duplicate runtime implementation
