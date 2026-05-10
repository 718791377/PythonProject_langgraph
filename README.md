# PythonProject_langgraph

This repository is the primary home for the Codex user-level orchestration line:

- native Codex subagent routing behavior
- oh-my-codex user-level workflow surfaces
- OMX durable-team entrypoints and Windows-native execution support
- LangGraph durable orchestration, state, and inspection surfaces

It is intentionally split out from `D:\PythonProject_OpenClaw`.

`D:\PythonProject_OpenClaw` is not the source of truth for this line after migration.

Current active implementation mainline:

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`

Next recommended change:

- none beyond the active sync mainline

Next recommended action:

- sync the bilingual capability-gap appendix and startup-facing pointers after the archived migration-aware live-engine rollout

## Publication workflow

- Local `main` is the primary integration surface after local validation, local MR review, a clean feature worktree, and explicit user approval.
- GitLab is the remote publication, clean-environment confirmation, backup, and audit surface; it is not the default gate before local `main` integration.
- GitHub is the mirror/sync target. Do not open a GitHub PR unless explicitly requested.
