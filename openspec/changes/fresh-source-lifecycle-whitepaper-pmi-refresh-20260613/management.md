# Management Checklist

## Open
- [x] Value and why recorded in proposal.
- [x] Success criteria recorded as fresh extraction, bilingual refresh, and validation evidence.
- [x] Constraints recorded: no raw source text commit, no old-cache reuse, no remote publication.

## Design
- [x] Delivery tailoring recorded: documentation/governance refresh with local ignored extraction evidence.
- [x] Risks recorded: PDF extraction fallback, stale cache wording, bilingual drift, and whitepaper/research role confusion.
- [x] Acceptance evidence path recorded: extraction manifest, source report, OpenSpec validation, guard, local gate.

## Build
- [x] Execution mode recorded: direct implementation in isolated worktree with durable worker lane selected for independent slices.
- [x] Quality evidence will be recorded through extraction coverage, diff review, and checker runs.
- [x] Blocker decision: none at build start.
- [x] Current evidence run recorded as `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` generated at `2026-06-14T10:48:53Z`.
- [x] Native expert review found Chinese mojibake and bilingual drift; leader fixed those blockers before final validation.

## Verify
- [x] Variance review recorded: stale-cache wording, bilingual pair, claim-lock, and receipt-schema blockers were corrected.
- [x] Risk/change impact recorded: tracked docs keep only derived evidence; raw source text stays ignored.
- [x] Control decision recorded: continue to local gate after repository guard passed in JSON mode.
- [ ] Re-run OpenSpec validation, repository guard, pre-commit update/archive review, local gate, and local MR review after the 2026-06-14 evidence and bilingual fixes.
- [x] Fresh validation evidence before final commit: `openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` passed; `python tools/run_openspec_guard.py --root . --json` passed 66/66; `python tools/check_precommit_update_archive.py --root . --json` passed; `tools/ci/local_gate.ps1 -StepTimeoutSeconds 5400` returned `local_ci_gate: ok`.

## Archive
- [ ] Value outcome summarized after local validation.
- [ ] Lessons learned recorded before archive.
- [ ] Archive/sync evidence captured by archive path and stable specs if promoted.

## Monitoring
- [x] Current facts recorded.
- [x] Return/no-return decision: continue.
