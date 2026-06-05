## ADDED Requirements

### Requirement: The LangGraph backend SHALL persist explicit thread release receipts

The LangGraph durable backend SHALL provide a repo-local helper that closes, releases, or hands off a tracked LangGraph thread and persists a release receipt under `.omx/state/langgraph/store/releases/`.

The receipt SHALL record at least:

- `thread_id`, which identifies the released LangGraph thread.
- `backend_family`, which remains `langgraph` for this helper.
- `previous_state`, meaning a full snapshot of the thread record before release, and `previous_status`, meaning the pre-release value of the thread `status` field; together they preserve the pre-release posture.
- `release_action`, which is one of `close`, `release`, or `handoff`.
- `survivor_queue_path` and `survivor_queue_status`, which identify persisted survivor state.
- `handoff_target`, which is required for backend-family handoff.
- `checkpoint_path` and `artifact_path`, which point to repo-local recovery evidence.
- `timeout_release`, which records whether the release followed a timeout.
- `rollback_restore_note`, which records recovery guidance without automatically rewriting state.
- `redaction_status`, which records whether the receipt is safe for operator-visible evidence.

#### Scenario: Operator closes a completed tracked thread

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=close`
- **THEN** the backend SHALL write a release receipt under `.omx/state/langgraph/store/releases/`
- **AND** the thread state SHALL no longer report `status=running`
- **AND** status and inspect output SHALL expose the release receipt path and release projection

#### Scenario: Operator hands off a thread to another backend family

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=handoff`
- **THEN** the backend SHALL require `handoff_target` and `reason`
- **AND** the persisted thread state SHALL record `handoff_at`, `handoff_target`, and `reason`
- **AND** the handoff SHALL NOT implicitly start or switch to the target backend family
