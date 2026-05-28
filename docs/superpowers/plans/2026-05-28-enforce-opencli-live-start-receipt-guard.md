# Plan: Enforce OpenCLI live-start receipt guard

- [x] Confirm scope: repo-local governance only, no user-level runtime mutation.
- [x] Add Stage A plan-state commit before code changes.
- [x] Implement install receipt validation in `tools/opencli_governance.py`.
- [x] Add `start` preflight command requiring owner, install, and port evidence.
- [x] Add unit tests for missing install receipt, missing owner evidence, and complete-evidence deferral.
- [x] Update bilingual implementation plan state and checklist.
- [x] Add archived OpenSpec evidence and stable spec requirement.
- [x] Run targeted tests and repository validation.
- [x] Merge to local `main` after local gate and local MR review pass.
