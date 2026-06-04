# Comet Management Checklist

## Open / Value Definition

- [x] Value/why is stated: prevent English/ASCII transport from corrupting embedded non-ASCII canary text.
- [x] Success criteria are stated: English summary ASCII-only, Chinese summary literal markers retained, checkers/tests pass.
- [x] Stakeholders or constraints are identified: cold-start recovery, launcher payload safety, no remote publication.

## Design / Delivery Framing

- [x] Delivery approach is tailored to the change size: tweak-style single implementation slice.
- [x] Risks and key assumptions are recorded: user-visible marker semantics do not change.
- [x] Acceptance evidence path is identified: targeted tests, checker commands, OpenSpec guard, local gate, local MR review.

## Build / Execution

- [x] Execution mode is selected and completed.
  - Evidence: direct tweak execution in the isolated `ascii-startup-canary-markers` worktree.
- [x] Quality evidence is recorded.
  - Evidence: `verification.md` records the targeted unittest, checker, and OpenSpec validation commands.
- [x] Blockers are cleared or explicitly decided.
  - Evidence: no remaining implementation blocker; final integration remains local-main-first and stops before remote publication.

## Verify / Acceptance

- [x] Variance from proposal/design/tasks is checked.
  - Evidence: storage location changed only; user-visible canary semantics are unchanged.
- [x] Risk and change impact are assessed.
  - Evidence: English source becomes ASCII-only, Chinese source remains UTF-8 literal, and rollback is one local feature commit revert.
- [x] Control decision is recorded.
  - Evidence: continue to archive, final local gates, local `main` integration, and remote-publication stop gate.

## Archive / Closing

- [x] Value outcome is summarized.
  - Evidence: English startup summary is ASCII-only while the Chinese companion remains the literal visible marker source.
- [x] Lessons learned or reusable guidance are recorded.
  - Evidence: avoid storing non-ASCII sentinel text in English/ASCII startup surfaces; enforce the split with checkers.
- [x] Delta spec sync, verification evidence, and archive path are confirmed.
  - Evidence: stable specs were manually synchronized as complete specs; archive used `openspec archive --skip-specs` to preserve the full stable spec; archive path is `openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/` and verification report path is `openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/verification.md`.

## Monitoring Loop

- [x] Current facts are checked.
- [x] Continue, adjust, stop, or return decision is made.
