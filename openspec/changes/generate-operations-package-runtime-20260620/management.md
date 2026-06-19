# Management: Generate Operations Package Runtime

## Open

- [x] Value: turn two already-refreshed operating-system corpora into executable, checkable, bilingual operations packages.
- [x] Success criteria: Stage A freezes the contract on local `main`; Stage B generates and validates the live operations-package runtime and documents on local `main`.
- [x] Constraints: local-only integration, bilingual pairs, registry coverage, process-group I/T/O for execution-facing flow, no remote publication.

## Design

- [x] Delivery tailoring: two serial local-main integration packages, first plan freeze and then runtime/package implementation.
- [x] Risks/assumptions: generated documents must not replace white papers/North Stars; not every future 48/60 document body is required in Stage B, but registers and required package docs must be complete.
- [x] Acceptance evidence path: OpenSpec validation, package checker, focused tests, local gate, local MR review, and local-main helper evidence.

## Build

- [x] Execution mode for Stage A: isolated worktree and leader-owned local integration with advisory experts.
- [x] Quality evidence for Stage A: proposal/design/tasks/management/spec/plan artifacts.
- [x] Blocker decision: durable/persistent team launch waits until Stage A is integrated and Stage B opens 2+ independent execution slices.

## Verify

- [ ] Variance review after Stage A validation.
- [ ] Risk/change impact review after Stage A validation.
- [ ] Control decision after Stage A validation.

## Archive

- [ ] Value outcome recorded after Stage B runtime work.
- [ ] Lessons learned recorded after Stage B runtime work.
- [ ] Archive/sync evidence recorded after Stage B runtime work.

## Monitoring

- [x] Current facts: source white papers, North Stars, inventories, lifecycle tailoring, PMI map, and process-group contract already exist.
- [x] Return/no-return decision for Stage A: continue to local validation and local-main integration; no return loop needed.
