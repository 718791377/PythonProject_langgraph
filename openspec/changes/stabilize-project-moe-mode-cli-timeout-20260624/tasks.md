# Tasks

## 1. OpenSpec and planning package

- [x] 1.1 Create the bounded OpenSpec change package for Project MOE Mode CLI timeout stabilization.
- [x] 1.2 Record design, management, rollback, validation path, and archive deferral for local-main-first integration.

## 2. Implementation

- [x] 2.1 Add a configurable Mode CLI timeout helper to the shared Project MOE GUI toolchain runner.
- [x] 2.2 Add the same timeout helper behavior to the Project MOE GUI shell runner.
- [x] 2.3 Replace hard-coded 20 second subprocess timeouts with the helper result.

## 3. Regression coverage

- [x] 3.1 Add a test that proves `toolchain.run_cli()` uses `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS` when set.
- [x] 3.2 Add a test that proves the default Mode CLI timeout has full-suite headroom.
- [x] 3.3 Add a test that proves GUI write/readback subprocess calls share one timeout budget when an override is set.
- [x] 3.4 Add a test that proves GUI write/readback subprocess calls use the default full-suite timeout budget when no override is set.

## 4. Validation and local integration

- [x] 4.1 Run focused timeout tests and the full Project MOE GUI toolchain test file.
- [ ] 4.2 Run OpenSpec validation, precommit update/archive review, repository guard, local gate, and local MR review.
- [ ] 4.3 Merge the clean hotfix worktree into local `main` with rollback evidence and stop before remote publication.
