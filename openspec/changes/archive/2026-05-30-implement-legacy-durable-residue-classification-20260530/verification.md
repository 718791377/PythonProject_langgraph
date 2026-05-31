# Verification

Verification commands and results are recorded during the local feature-branch run:

- `python .\test\check_worktree_task_receipt.test.py` - passed; 7 tests.
- `python .\tools\check_worktree_task_receipt.py --root . --json` - required before commit.
- `python .\tools\check_durable_artifact_state_surfaces.py --root . --json` - required before commit.
- `openspec validate --all` - required before commit.
- `python .\tools\check_implementation_plan_rules.py --root . --json` - required before commit.
- `python .\tools\check_precommit_update_archive.py --root . --json` - required before commit.
- `python .\tools\run_openspec_guard.py --root . --json` - required before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - required before local main integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - required before local main integration.

Remote publication is not part of this verification record.
