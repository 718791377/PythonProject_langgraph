---
change: prevent-codex-npm-eperm-cleanup-warning-20260624
verified-at: 2026-06-25T00:49:37Z
head: 84e8d624b964fe6a85032164183137937ee91e74
result: pass
---

# Verification Report: Codex npm EPERM Update Preflight

## Result

PASS. The Windows npm EPERM update-preflight runtime change has landed on local `main` and the follow-up governance state is being closed in this branch.

## Requirement Evidence

| Requirement | Evidence | Result |
| --- | --- | --- |
| Detect likely Windows Codex lock risk before global npm mutation | `tools/codex-official-update-patch-replay-template.ps1` emits `windows_codex_lock_preflight`; focused PowerShell regression asserts detected lock blocks npm before install and override records risk. | PASS |
| Fail closed when process inventory is unknown unless explicitly overridden | Focused regression covers invalid fake process inventory, `lock_risk=unknown`, `recommended_action=manual_review`, no `official_update` by default, and override continuation. | PASS |
| Classify cleanup EPERM warnings only for successful npm installs | Focused regression covers `cleanup_eperm` with exit `0` producing `windows_file_lock_eperm`; `eperm_only` does not classify. | PASS |
| Preserve non-zero npm install failure semantics | Focused regression covers non-zero fake npm install with cleanup text, no cleanup-warning success masking, and no `omx_setup` continuation. | PASS |
| Report leftover staging candidates without deleting them | Runtime preflight reports `.codex-*` candidates; implementation contains no automatic staging-directory deletion path; tests keep fake staging state under temp npm root. | PASS |
| Local-main-first integration and remote-publication stop | Local main contains `84e8d624b964fe6a85032164183137937ee91e74`; completed claim records `RemotePublication=false`; related feature branch/worktree was cleaned and rollback refs exist. | PASS |

## Fresh Verification Commands

The following commands were run from local `main` after integration during the completion audit:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File .\test\codex-official-update-patch-replay-template.test.ps1
# observed: codex-official-update-patch-replay-template: ok

openspec validate prevent-codex-npm-eperm-cleanup-warning-20260624 --strict
# observed: Change 'prevent-codex-npm-eperm-cleanup-warning-20260624' is valid

python .\tools\check_precommit_update_archive.py --root . --json
# observed: ok=true

git diff --check HEAD~1..HEAD
# observed: exit code 0

python .\tools\run_openspec_guard.py --root . --tool codex --json
# observed: ok=true, steps_total=81, steps_passed=81, steps_failed=0
```

## Branch Handling

The Stage 2 runtime implementation branch was handled by `tools\complete_local_flow_to_remote_gate.py --execute`; it merged commit `84e8d624b964fe6a85032164183137937ee91e74` into local `main`, preserved rollback ref `refs/backup/local-main/20260625-072630-before-implement-codex-npm-eperm-runtime-20260624`, preserved the completed claim, removed the feature worktree/branch, and stopped at the remote-publication gate.

This report is added by the OpenSpec/Comet closure branch so the change can transition through verify/archive and keep repository governance evidence consistent.
