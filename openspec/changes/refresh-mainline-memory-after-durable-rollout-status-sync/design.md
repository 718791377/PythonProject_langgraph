## Design

This is a handoff-refresh change. It updates startup-facing memory text only; no runtime code, generated user-level helper, durable state, or MCP configuration is changed.

The refreshed summary should make three facts obvious to a cold-start session:

1. The latest published mainline includes the Codex direct browser/design MCP policy and the durable rollout plan status-sync archive.
2. MR 5 helper mirror source-of-truth work is completed and must not be reopened as the next durable-state slice.
3. Any MR 6 readiness or routing hookup must be opened as a separately named OpenSpec change after ownership precheck, because this change is only a memory refresh.

Archive is intentionally deferred if another active session owns broad `openspec/specs` scope. Publishing an active, complete change is acceptable as an intermediate state only when the final archive is explicitly serialized later.
