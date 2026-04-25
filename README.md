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

- GitLab is the authoritative review and merge surface.
- Push repository changes to a GitLab feature branch and open or update a GitLab MR first.
- Merge only after the GitLab pipeline passes.
- After GitLab `main` is merged and green, sync the same `main` commit directly to GitHub.
- Do not open a GitHub PR unless explicitly requested; GitHub is the post-merge sync target.
