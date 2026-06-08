# Design: Durable Capability Readiness R4 Runtime Refresh

## Runtime boundary
`codex-durable-state-status.ps1` remains read-only by default. R4 adds only an explicit `-RefreshReadiness` path that writes `<repo>/.omx/state/readiness/durable-capability-readiness-projection.json`.

## Receipt shape
The receipt records `schema_version`, `receipt_kind`, `promotion_marker=smoke-tested`, `generated_at`, `repo_root`, `selected_backend`, `backend_default`, `backend_ready`, `capability_readiness`, `blockers`, `source_receipts`, `selector_evidence`, `version_evidence`, `durable_workflow_adopted=false`, `persistent_team_launched=false`, and smoke metadata.

## Safety
The refresh copies computed status projection evidence and never runs backend launch commands. Default status reads must not create `.omx`.
