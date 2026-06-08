# Management Checklist

## Open

- [x] Value and why evidence checked: R4 closes the documented runtime gap between validation-only lifecycle labels and automated local metadata advancement.
- [x] Success criteria checked: helper, integration hooks, tests, plan pair, OpenSpec delta, validation, archive, and local-main integration.
- [x] Stakeholders and constraints checked: main Codex leader session owns the write scope; remote publication is not authorized; no durable team launch.

## Design

- [x] Delivery tailoring checked: one focused helper plus integration hooks, not a broad durable-team runtime.
- [x] Risks and assumptions checked: invalid transition order, dirty cleanup, missing rollback evidence, and remote publication must fail closed.
- [x] Acceptance evidence path checked: focused tests, receipt checker, precommit review, OpenSpec guard, local gate, local MR review.

## Build

- [x] Execution mode checked.
- [x] TDD / review / quality evidence checked.
- [x] Blockers cleared or decided.

## Verify

- [x] Variance review checked.
- [x] Risk/change impact checked.
- [x] Control decision checked.

## Archive

- [x] Value outcome checked.
- [x] Lessons learned checked.
- [x] Archive/sync evidence checked.

## Monitoring

- [x] Current facts checked: no active R4 change existed before this branch; implementation uses an isolated feature worktree and active portable claim.
- [x] Return/no-return decision checked: continue in current change; no return to earlier phase required.

## Evidence Notes

- Build evidence: focused lifecycle, cleanup, and complete-flow tests passed after the R4 helper was implemented.
- Verify evidence: full validation is run before commit and archive; remote publication remains unauthorized.
- Archive decision: single integration package is intended because R4 is a focused runtime/checker/test/spec update with one rollback boundary.
