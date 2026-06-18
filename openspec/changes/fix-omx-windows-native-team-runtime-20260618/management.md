# Management: Fix OMX Windows Native Team Runtime

## Open

- [x] Value: remove the false assumption that a Unix/tmux-only runtime is enough for native Windows `native_omx` durable teams.
- [x] Success criteria: Stage A freezes the contract; Stage B proves operational Windows launchability or named fail-closed blockers.
- [x] Constraints: local-only integration, no remote publication, no WSL2/tmux requirement for the Windows default path, repo-local durable state stays per project.

## Design

- [x] Delivery tailoring: two local-main packages, first plan freeze and then runtime implementation.
- [x] Risks/assumptions: readiness and selection are currently too easy to confuse with launchability; Stage B must use TDD before runtime edits.
- [x] Acceptance evidence path: OpenSpec validation, focused PowerShell tests, local gate, local MR review, and local-main helper evidence.

## Build

- [x] Execution mode for Stage A: isolated worktree with advisory experts and leader-owned local integration.
- [x] Quality evidence for Stage A: this management checklist plus proposal/design/tasks/spec/plan artifacts.
- [x] Blocker decision: persistent team launch waits until Stage A is frozen and Stage B has safe slices; the current bug means tmux-backed panes are not accepted as evidence.

## Verify

- [ ] Variance review after Stage A validation.
- [ ] Risk/change impact review after Stage A validation.
- [ ] Control decision after Stage A validation.

## Archive

- [ ] Value outcome recorded after Stage B runtime work.
- [ ] Lessons learned recorded after Stage B runtime work.
- [ ] Archive/sync evidence recorded after Stage B runtime work.

## Monitoring

- [x] Current facts: this machine has no usable `tmux` team pane environment for native Windows, so Stage A must not claim operational persistent-team launchability.
- [x] Return/no-return decision for Stage A: continue to local validation and local-main integration; no return loop needed.
