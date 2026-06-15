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
- [x] Execution mode is selected. Direct implementation ran in an isolated worktree, with durable worker lane selected for independent slices.
- [x] Quality evidence is recorded: TDD, review, test, or equivalent. Evidence includes extraction coverage, diff review, OpenSpec validation, repository guard, local gate, local MR review, and post-merge local gate.
- [x] Blockers are cleared or have an explicit decision. Build blockers from claim-lock, receipt schema, stale-cache wording, and bilingual drift were corrected before final local integration.
- [x] Current evidence run recorded as `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` generated at `2026-06-14T10:48:53Z`.
- [x] Native expert review found Chinese mojibake and bilingual drift; leader fixed those blockers before final validation.

## Verify
- [x] Variance from scope, design, and acceptance criteria is checked. Stale-cache wording, bilingual pair, claim-lock, and receipt-schema blockers were corrected.
- [x] Risk and change impact are assessed. Tracked docs keep only derived evidence; raw source text stays ignored.
- [x] Control decision is recorded. Continue to archive after final validation, local main integration, and post-merge local gate.
- [x] Re-run OpenSpec validation, repository guard, pre-commit update/archive review, local gate, and local MR review after the 2026-06-14 evidence and bilingual fixes.
- [x] Fresh validation evidence before final commit: `openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` passed; `python tools/run_openspec_guard.py --root . --json` passed 66/66; `python tools/check_precommit_update_archive.py --root . --json` passed; `tools/ci/local_gate.ps1 -StepTimeoutSeconds 5400` returned `local_ci_gate: ok`.

## Archive
- [x] Value outcome is summarized. The fresh 2026-06-14 source-read refresh updated lifecycle, whitepaper, research, North Star, PMI tailoring, and bridge documents, then merged to local main at `571129adc94dbe1482fa7f3c94fbbf92e681a475`.
- [x] Lessons learned or reusable guidance are recorded. Keep whitepaper and research as separate lifecycle roles; use the 10-to-12 bridge and playbook authority stack instead of duplicating or physically merging them.
- [x] Delta spec sync, verification evidence, and archive path are confirmed. Delta specs are merged into the existing stable capability `openspec/specs/codex-product-lifecycle-document-governance/`; archive path is `openspec/changes/archive/2026-06-15-fresh-source-lifecycle-whitepaper-pmi-refresh-20260613/`.

## Monitoring
- [x] Current facts are checked.
- [x] Continue, adjust, stop, or return decision is made. Decision: continue to archive; no return to earlier phase is required.
