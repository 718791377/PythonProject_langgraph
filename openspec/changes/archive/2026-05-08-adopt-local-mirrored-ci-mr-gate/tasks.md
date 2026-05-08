## 1. Implementation

- [x] Add `tools/ci/local_gate.ps1` as the shared local/remote CI entrypoint.
- [x] Add `tools/ci/local_mr_review.ps1` as the local MR review and merge-simulation entrypoint.
- [x] Update `.gitlab-ci.yml` to call the shared local gate script.
- [x] Update `.github/workflows/openspec-guard.yml` to call the shared local gate script.
- [x] Update `AGENTS.md` publication workflow wording.
- [x] Update startup summary publication posture in English and Chinese.
- [x] Update multi-session worktree governance policy in English and Chinese.
- [x] Add bilingual OpenSpec artifacts for this change.

## 2. Validation

- [x] Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Json`.
- [x] Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Json`.
- [x] Run `openspec validate --all`.
- [x] Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] Run `git diff --check`.
