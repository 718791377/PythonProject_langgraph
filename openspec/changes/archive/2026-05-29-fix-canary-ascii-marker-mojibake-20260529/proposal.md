## Why

A live resumed session showed the context-retention canary reminder rendered as mojibake even though the UTF-8 startup summary pair remained clean. The previous visible markers were non-ASCII, so the marker itself was vulnerable to the same encoding boundary it was meant to diagnose.

## What Changes

- Change the user-visible startup-summary canary markers to ASCII-stable start/end tokens while keeping the literal marker text confined to the startup summary pair.
- Keep checker support for the historical non-ASCII markers and their legacy-encoding corrupted variants so stale runtime payloads fail closed instead of being treated as valid canary evidence.
- Update canary and startup-mojibake tests to prove ASCII canonical evidence passes and legacy/corrupted visible evidence fails.
- Archive this change as one local integration package after local validation; no remote publication is authorized by this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-context-retention-canary-surface`: visible canary marker selection and checker compatibility requirements now require ASCII canonical markers plus legacy/corruption rejection.

## Impact

- Impact scope: startup summary pair, canary/mojibake checker constants, response/session diagnostics, and targeted tests.
- Explicit non-goals: no user-level wrapper rewrite, no remote publication, no persistent team launch, and no broad Chinese mojibake linter expansion.
- Rollout sequence: update docs and checkers, run targeted tests/checkers, archive OpenSpec, run local gates, commit, then merge to local `main` only.
- Rollback plan: revert this feature commit to restore the previous marker definition and checker behavior, then rerun the same targeted checkers.
- Validation path: run the two checker test modules, the two checker commands, OpenSpec guard, precommit update/archive check, local gate, and local MR review.
- Mainline classification: existing current mainline follow-up under the Codex user-level orchestration line, not a new mainline candidate.
