---
doc_id: cross_project_durable_state_read_only_inventory_2026-04-25
lang: en
canonical: docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.md
status: active
doc_class: memory
created_at: 2026-04-25
source_plan: docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md
---

# Cross-Project Durable State Read-Only Inventory - 2026-04-25

## Scope

This inventory is the Phase 0 no-touch baseline for the current durable-state isolation rollout.

Scanned project roots:

- `D:\PythonProject_langgraph`
- `D:\PythonProject_OpenClaw`
- `D:\PythonProject_CLIProxyAPI`
- `D:\project`

Collection rules:

- Read-only scan only.
- No `.omx/state` file or directory was edited, moved, renamed, or deleted.
- No durable team was launched for this inventory.
- The report records structure, counts, selected safe enum-like JSON fields, and top-level JSON keys only.
- The report does not copy durable artifact contents, prompts, event logs, worker mail, or secrets.

## Baseline Summary

| Project root | Git posture at scan | `.omx/state` posture | Activation posture | Classification |
| --- | --- | --- | --- | --- |
| `D:\PythonProject_langgraph` | Git worktree on `docs/freeze-active-implementation-boundary`, `afdbd34cc7ee` | Present: 11 files, 313 directories, 161330 bytes, 305 empty directories | No `.omx/state/selectors/active.json`; LangGraph backend record exists with `backend=langgraph`, `phase=define-target`, `status=running` | Preserved historical LangGraph record plus safe empty native residue |
| `D:\PythonProject_OpenClaw` | Git worktree on `main`, `947a1fa03007` | Present: 21 files, 62 directories, 282441 bytes, 52 empty directories | Active scoped selector exists with `backend_family=langgraph`; LangGraph backend has `phase=freeze-plan`, `status=resumed`, `routing_posture=active_scoped_selector` | Preserved active LangGraph selector/artifacts plus safe empty native residue |
| `D:\PythonProject_CLIProxyAPI` | Git worktree on `main`, `066290149602` | Present: 43 files, 15 directories, 105601 bytes, 2 empty directories | Active scoped selector exists with `backend_family=native_omx`; managed team record has `phase=stabilize`, `worker_count=2`, `worker_role=debugger` | Preserved active native OMX team state |
| `D:\project` | Not a Git worktree | Present: 4 files, 0 directories, 2986 bytes | No selector, LangGraph, or team state detected | Protected manual/user-level OMX UI state only |

## Per-Project Findings

### `D:\PythonProject_langgraph`

Key observations:

- `.omx/state/langgraph/backend.json` exists and should be treated as a preserved historical or inspectable LangGraph record for this rollout.
- `.omx/state/langgraph/threads`, `checkpoints`, and `history` each contain one file.
- `.omx/state/langgraph/interrupts` and `store` exist but are empty directories.
- `.omx/state/selectors/active.json` is absent.
- `.omx/state/selectors/leases` exists but is empty.
- `.omx/state/team` contains 300 empty `auto-team-*` directories and a `.fake-counter` file.
- `.omx/state/team/codex-auto-managed-team.json` is absent.

Classification:

- Preserved historical: LangGraph backend, thread, checkpoint, and history files.
- Safe empty: empty `auto-team-*` directories, empty selector leases directory, empty LangGraph interrupt/store directories.
- Protected manual: `.fake-counter`; do not remove in this phase because Phase 0 is no-touch.

Immediate implication:

- New activation logic must not let the preserved LangGraph backend record implicitly dominate unrelated future sessions.
- Native durable routing should be able to ignore empty unmanaged `auto-team-*` residue.

### `D:\PythonProject_OpenClaw`

Key observations:

- `.omx/state/selectors/active.json` exists and reports `backend_family=langgraph`, `routing_eligible=true`, and `routing_posture=active_scoped_selector`.
- `.omx/state/selectors/leases` contains one lease file.
- `.omx/state/langgraph/backend.json` exists and reports `backend=langgraph`, `phase=freeze-plan`, `status=resumed`, and `routing_posture=active_scoped_selector`.
- LangGraph artifact directories contain:
  - `threads`: 2 files
  - `checkpoints`: 2 files
  - `history`: 1 file
  - `interrupts`: 2 files
  - `store`: empty
- `.omx/state/team` contains 51 empty `auto-team-*` directories and a `.fake-counter` file.
- `.omx/state/team/codex-auto-managed-team.json` is absent.

Classification:

- Preserved active: scoped LangGraph selector, lease, backend record, and LangGraph artifacts.
- Safe empty: empty `auto-team-*` directories and empty LangGraph store directory.
- Protected manual: `.fake-counter`; do not remove in this phase because Phase 0 is no-touch.

Immediate implication:

- `D:\PythonProject_OpenClaw` is not only a historical fixture; it currently has an active scoped LangGraph selector. Future activation logic must distinguish this active scoped selector from stale unscoped residue.

### `D:\PythonProject_CLIProxyAPI`

Key observations:

- `.omx/state/selectors/active.json` exists and reports `backend_family=native_omx`, `phase=stabilize`, `routing_eligible=true`, and `routing_posture=active_scoped_selector`.
- `.omx/state/selectors/leases` contains one lease file.
- `.omx/state/team/codex-auto-managed-team.json` exists and reports `phase=stabilize`, `team_name=diagnose-cliproxyapi-auth-file`, `worker_count=2`, and `worker_role=debugger`.
- `.omx/state/team/diagnose-cliproxyapi-auth-file` is non-empty and contains team runtime files.
- No `.omx/state/langgraph` backend or LangGraph artifact directories were detected.

Classification:

- Preserved active: scoped native OMX selector, lease, managed-team record, and non-empty team runtime directory.
- Safe empty: only nested empty approvals/claims directories inside the managed team tree.
- Protected manual: non-empty team runtime state; do not edit in this phase.

Immediate implication:

- Durable-state isolation must preserve active native OMX teams and must not treat every `.omx/state/team` tree as cleanup residue.

### `D:\project`

Key observations:

- The root exists but is not a Git worktree.
- `.omx/state` contains only four files: HUD, notification, leader nudge, and tmux hook state.
- No `.omx/state/selectors`, `.omx/state/langgraph`, or `.omx/state/team` paths were detected.

Classification:

- Protected manual/user-level UI state only.
- No durable activation selector was found.
- No native team or LangGraph durable artifact plane was found.

Immediate implication:

- Future helpers should not infer a durable backend from this root's generic OMX UI state.

## Cross-Project Conclusions

1. The four scanned roots are not equivalent:
   - `D:\PythonProject_OpenClaw` has active scoped LangGraph state.
   - `D:\PythonProject_CLIProxyAPI` has active scoped native OMX team state.
   - `D:\PythonProject_langgraph` has preserved LangGraph records and many empty native residue directories, but no active selector.
   - `D:\project` has only generic UI/hook state.
2. Empty native `auto-team-*` directories are common in `D:\PythonProject_langgraph` and `D:\PythonProject_OpenClaw`, but non-empty team state in `D:\PythonProject_CLIProxyAPI` is active and must be preserved.
3. New routing must prefer scoped selectors and leases over legacy backend files.
4. Legacy or inspectable backend records remain valuable evidence, but they must not auto-activate unrelated future sessions.
5. Phase 1 implementation can proceed without deleting or rewriting any legacy `.omx/state` artifact.

## Phase 1 Contract Inputs

The next implementation phase should encode these rules in source and tests:

- Empty `auto-team-*` directories are safe-empty residue and must not block native durable routing.
- Non-empty managed team records remain preserved active state.
- A scoped selector with a live lease is stronger activation evidence than a legacy backend record.
- Generic HUD/notification/tmux state is not durable backend activation evidence.
- Repo-local `.omx/state` remains the source of truth for that repository only.

