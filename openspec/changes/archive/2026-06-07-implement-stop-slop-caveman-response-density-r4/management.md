# Management Checklist

## Open
- [x] Value and why recorded in proposal.
- [x] Success criteria recorded as checker-backed R4 runtime evidence.
- [x] Constraints recorded: no user-level install or remote publication.

## Design
- [x] Delivery tailoring recorded: repo-local runtime and checker only.
- [x] Risks recorded: protected spans and smoke evidence fail closed.
- [x] Acceptance evidence path recorded: focused tests, guard, CI manifest, precommit, local gate, local MR review.

## Build
- [x] Execution mode recorded: direct in isolated worktree.
- [x] Quality evidence recorded: RED/GREEN tests, Unicode punctuation coverage, and smoke receipts.
- [x] Blocker decision recorded: shared CI manifest, OpenSpec guard wiring, and safety registry hotspots are still claimed by other active dirty worktrees; do not force local integration until ownership is serialized.

## Verify
- [x] Focused verification recorded in tasks and implementation-plan evidence.
- [x] Risk/change impact recorded in proposal, design, and specs.
- [x] Control decision: continue after serialized hotspot ownership clears.

## Archive
- [ ] Value outcome summarized in verification and stable specs.
- [ ] Lessons learned recorded in implementation plan evidence.
- [ ] Archive/sync evidence captured by archive path and validation output.

## Monitoring
- [x] Current facts recorded.
- [x] Return/no-return decision: continue when ownership blocker clears.
