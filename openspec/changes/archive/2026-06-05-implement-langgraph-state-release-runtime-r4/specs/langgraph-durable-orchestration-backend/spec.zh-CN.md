## ADDED Requirements

### Requirement: LangGraph backend MUST persist explicit thread release receipts

This zh-CN companion preserves the same R4 requirement in ASCII-safe bilingual form: the LangGraph durable backend must provide a repo-local helper that can close, release, or hand off a tracked LangGraph thread and persist a release receipt under `.omx/state/langgraph/store/releases/`.

The receipt must record at least:

- `thread_id`: identifies the released LangGraph thread.
- `backend_family`: remains `langgraph` for this helper.
- `previous_state`: a full snapshot of the thread record before release; and `previous_status`: the pre-release value of the thread `status` field.
- `release_action`: one of `close`, `release`, or `handoff`.
- `survivor_queue_path` and `survivor_queue_status`: identify persisted survivor state.
- `handoff_target`: required for backend-family handoff.
- `checkpoint_path` and `artifact_path`: point to repo-local recovery evidence.
- `timeout_release`: records whether the release followed a timeout.
- `rollback_restore_note`: records recovery guidance without automatically rewriting state.
- `redaction_status`: records whether the receipt is safe for operator-visible evidence.

#### Scenario: Operator closes a completed tracked thread

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=close`
- **THEN** the backend must write a release receipt under `.omx/state/langgraph/store/releases/`
- **AND** the thread state must no longer report `status=running`
- **AND** status and inspect output must expose the release receipt path and release projection

#### Scenario: Operator hands off a thread to another backend family

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=handoff`
- **THEN** the backend must require `handoff_target` and `reason`
- **AND** the persisted thread state must record `handoff_at`, `handoff_target`, and `reason`
- **AND** the handoff must not implicitly start or switch to the target backend family
