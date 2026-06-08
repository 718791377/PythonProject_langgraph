# Change: Implement R4 Capability Receipt Runtime Governance

## Why

The user-level capability receipt plan has an explicit Stage D gap: later runtime lanes need reusable receipt validation for install/update/smoke/live/cleanup/rollback evidence. Existing helper coverage validates authorization and R3-style update/install receipts, but it cannot yet validate an R4 `smoke-tested` receipt with bounded read-only smoke evidence, timeout release, rollback readiness, and transcript redaction.

## What Changes

- Add R4 smoke receipt validation to `tools/user_level_receipt_governance.py` without running any real user-level command.
- Add rollback receipt validation for dry-run/apply evidence without executing rollback commands.
- Extend receipt templates and tests so later runtime lanes can emit sanitized `smoke-tested` evidence before any R5 live handoff.
- Update the OpenSpec delta and stable governance spec to reflect the implemented R4 helper contract while leaving implementation-plan file ownership to its existing plan-maintenance worktree.

## Scope

- `tools/user_level_receipt_governance.py` - receipt governance helper that gains read-only R4 smoke and rollback receipt validation.
- `test/user_level_receipt_governance.test.py` - focused regression tests for smoke, rollback, and template behavior.
- `openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md` and `.zh-CN.md` - stable governance specs updated during archive.
- This OpenSpec change package - proposal, design, tasks, management, and delta spec evidence for the R4 package.

## Non-Goals

- Do not install, update, start, smoke, or live-run any real user-level MCP, browser, CLI, WXWork, Pi, oh-my-pi, or harness runtime.
- Do not perform R5 live handoff, browser actions, cookie reads, external message sends, or sensitive MCP calls.
- Do not mutate user-level Codex configuration, browser profiles, MCP Router state, or remote Git refs.

## Rollout

1. Create this OpenSpec package and local worktree claim.
2. Add failing R4 smoke/rollback receipt tests.
3. Implement helper validation and sanitized summaries.
4. Update plan evidence and delta spec.
5. Run focused tests, OpenSpec validation, repository guard, local gate, and local MR review.
6. Archive the change and merge the verified package into local `main`.

## Rollback

- Revert the feature commit or the local `main` merge commit.
- If local `main` has moved, use the rollback ref created by the local integration helper.
- No external user-level runtime state is mutated by this slice.

## Verification

- `python test/user_level_receipt_governance.test.py` - runs the focused receipt governance regression suite.
- `openspec validate implement-capability-receipt-r4-runtime --strict` - validates the active OpenSpec change before archive.
- `python tools/check_precommit_update_archive.py --root . --json` - checks update/archive readiness before commit.
- `python tools/run_openspec_guard.py --root .` - runs the repository OpenSpec aggregate guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.
