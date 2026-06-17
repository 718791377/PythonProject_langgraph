# Management: Confirm User-Level Document Tool Runtime

## Open

- [x] Value: prove the reusable document/PDF/vector tooling line is confirmed from `D:\PythonProject_langgraph` before live-runtime completion is claimed.
- [x] Success criteria: Stage 1 freezes a verifiable follow-up plan; Stage 2 verifies Poppler/PDF, document-pipeline, and vector/retrieval behavior from the shared repository.
- [x] Constraints: no remote publication; no `D:\project` protected-source drift; no tracked third-party Poppler binaries.

## Design

- [x] Delivery tailoring: two local-main integration packages, first plan freeze and then runtime implementation.
- [x] Risks/assumptions: `D:\project` contains unrelated dirty files and must be treated as a guarded consumer/source-comparison project.
- [x] Acceptance evidence path: validation commands in `tasks.md` and the refreshed implementation plan pair.

## Build

- [x] Execution mode: worktree isolation with local-main-first integration.
- [x] Quality evidence: OpenSpec validation, plan/document checks, precommit checker, local gate, local MR review.
- [x] Blocker decision: Stage 1 does not claim runtime completion; Stage 2 remains the implementation backlog.

## Verify

- [ ] Variance review completed after Stage 2 runtime work.
- [ ] Risk/change impact reviewed after Stage 2 runtime work.
- [ ] Control decision recorded after Stage 2 runtime work.

## Archive

- [ ] Value outcome recorded after Stage 2 runtime work.
- [ ] Lessons learned recorded after Stage 2 runtime work.
- [ ] Archive/sync evidence recorded after Stage 2 runtime work.

## Monitoring

- [x] Current facts: migration source exists, but current checkout lacks `.local` Poppler cache and has three document-pipeline PowerShell parser failures.
- [x] Return/no-return decision: continue with Stage 1 freeze, then Stage 2 runtime implementation.
