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
- [x] Archive/sync evidence recorded after Stage B local-main integration: Stage B landed on local `main` at `5cd3491`; user-level install refresh and `D:\project` live smoke evidence were recorded; remote publication remains unauthorized.

## Monitoring

- [x] Current facts: this machine has no usable `tmux` team pane environment for native Windows, so Stage A must not claim operational persistent-team launchability.
- [x] Return/no-return decision for Stage A: continue to local validation and local-main integration; no return loop needed.
- [x] Stage B monitoring decision: persistent-team evidence must use the Windows prompt/process controller lifecycle surfaces or named blockers, not stale compatibility team records alone.
- [x] Stage B live smoke closeout fact: `windows-native-prompt-process` launched through the Windows prompt/process controller, shut down cleanly, left `D:\project` clean, and did not create smoke state in `D:\PythonProject_langgraph`.

## Archive / Closing

- [x] Value outcome is summarized. Native Windows OMX team launchability now requires operational preflight and prompt/process lifecycle evidence instead of selected/ready state alone.
- [x] Lessons learned or reusable guidance are recorded. Prompt/process controller replay must cover startup evidence, child exec status, status/await/resume behavior, shutdown cleanup, and cross-project state isolation together.
- [x] Delta spec sync, verification evidence, and archive path are confirmed. Stage B landed on local `main` at `5cd3491`; user-level install refresh and `D:\project` live smoke evidence are recorded; archive path is `openspec/changes/archive/2026-06-19-fix-omx-windows-native-team-runtime-20260618/`; remote publication remains unauthorized.

## Monitoring Loop

- [x] Current facts are checked. This machine has `TMUX=<unset>` and no `tmux` command; live smoke used `windows-native-prompt-process` in `D:\project` and left both `D:\project` and `D:\PythonProject_langgraph` clean of smoke team state.
- [x] Continue, adjust, stop, or return decision is made. Continue to archive/sync in the same local-only closeout package and stop at the remote-publication gate.
