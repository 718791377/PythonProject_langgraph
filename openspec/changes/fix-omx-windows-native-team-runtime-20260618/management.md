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
- [x] Stage B implementation: native Windows preflight now separates runtime backend, preflight, operational readiness, and blockers; generated wrappers avoid tmux-only routing by default.
- [x] Stage B lifecycle replay patches: prompt runtime/controller shutdown and child-exec status patchers are covered by Node tests and official-install replay tests.

## Verify

- [x] Variance review after Stage A validation: Stage A landed on local `main`; Stage B used the same change and did not broaden to remote publication.
- [x] Risk/change impact review after Stage B focused validation: tmux remains an explicit opt-in backend that fail-closes when unavailable; Windows default routes to the prompt/process controller path.
- [x] Control decision after Stage B focused validation: continue to repository gates, local MR review, and local-main integration; no remote publication is authorized.

## Archive

- [x] Value outcome recorded after Stage B runtime work: native Windows OMX team launchability is no longer inferred from selected/ready state alone and now requires operational preflight evidence.
- [x] Lessons learned recorded after Stage B runtime work: prompt/process controller patch replay must cover startup evidence, child exec status, and shutdown cleanup together.
- [ ] Archive/sync evidence recorded after Stage B local-main integration.

## Monitoring

- [x] Current facts: this machine has no usable `tmux` team pane environment for native Windows, so Stage A must not claim operational persistent-team launchability.
- [x] Return/no-return decision for Stage A: continue to local validation and local-main integration; no return loop needed.
- [x] Stage B monitoring decision: persistent-team evidence must use the Windows prompt/process controller lifecycle surfaces or named blockers, not stale compatibility team records alone.
