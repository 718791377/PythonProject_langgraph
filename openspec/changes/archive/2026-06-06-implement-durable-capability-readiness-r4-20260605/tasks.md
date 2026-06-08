# Tasks

## 1. OpenSpec package
- [x] 1.1 Create the bounded OpenSpec package for R4 readiness refresh.
- [x] 1.2 Record local-only scope, non-adoption boundary, rollback, and validation path.

## 2. Implementation
- [x] 2.1 Add explicit `-RefreshReadiness` support to `codex-durable-state-status.ps1`.
- [x] 2.2 Write `.omx/state/readiness/durable-capability-readiness-projection.json` only on explicit refresh.
- [x] 2.3 Preserve distinct readiness fields plus blockers/source evidence.
- [x] 2.4 Ensure the receipt states no durable workflow or persistent team was adopted.

## 3. Validation and local integration
- [x] 3.1 Add checker and PowerShell regression coverage.
- [x] 3.2 Run targeted tests, OpenSpec validation, precommit review, and local gate.
- [x] 3.3 Update plan evidence and prepare this change for archive/sync in the single local integration package.
- [x] 3.4 Record the post-archive handoff: after archive and commit, run local MR review, merge into local `main`, run post-merge validation, and stop at the remote-publication gate.
