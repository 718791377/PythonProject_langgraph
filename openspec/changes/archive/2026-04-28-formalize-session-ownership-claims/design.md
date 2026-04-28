# Design: Session ownership claims

## Claim location

Claim files live under `.omx/session-claims/`, a local ignored directory used only for temporary session coordination. `.omx/session-claims/` is not durable runtime state and is not committed.

## Claim format

Each claim is a JSON object with:

- `schema_version` - claim schema version, currently `1`.
- `session_id` - operator-readable session identifier.
- `status` - active claims use `active`; released or inactive claims are ignored.
- `branch` - Git branch that owns the claim.
- `worktree` - optional absolute or relative worktree path used to detect stale copied claims.
- `task_type` - task class such as `implementation`, `archive`, or `docs`.
- `openspec_changes` - OpenSpec change names owned by this session.
- `paths` - repository-relative path scopes owned by this session.

## Checker behavior

`tools/check_session_ownership_claims.py` is read-only. It scans every registered Git worktree for `.omx/session-claims/*.json`.

The checker fails when:

- an active claim is invalid JSON or misses required fields
- two active claims own the same OpenSpec change
- two active claims own overlapping repository-relative path scopes
- a dirty current feature worktree runs with `--allow-current-dirty` but has no active claim

The checker passes in clean CI clones with no local claims.

## Guard integration

`tools/run_openspec_guard.py` runs the checker with `--allow-current-dirty` after the worktree hygiene checker. This keeps local feature work strict while allowing CI clean clones to pass without local session files.
