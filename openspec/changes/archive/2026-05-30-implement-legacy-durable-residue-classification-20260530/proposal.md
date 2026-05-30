# Change: Implement Legacy Durable Residue Classification

## Why

Legacy repo-local `.omx` durable residue can remain after older native OMX teams, LangGraph threads, or selector experiments. Cold-start sessions need inspectable evidence that separates safe cleanup candidates, protected unmanaged state, stale selectors, active selector authority, and completed LangGraph state without auto-adopting unmanaged teams or stale workflows.

## What Changes

- Extend `tools/check_worktree_task_receipt.py` to emit a read-only `durable_residue_classification` section alongside existing worktree receipt classification.
- Add stable safe-next-action fields and `auto_adopt_allowed: false` on durable residue records.
- Add tests for non-empty unmanaged native team residue, completed LangGraph state, stale selector records, active current selector records, and integrated checker output.
- Update the durable-state cleanup and reconciliation stable spec to require this classification surface.

## Impact

Impact scope:

- `tools/check_worktree_task_receipt.py`: read-only durable residue classification implementation.
- `test/check_worktree_task_receipt.test.py`: regression tests for durable residue fixture classes.
- `openspec/specs/codex-user-level-durable-state-cleanup-and-reconciliation/spec.md`: stable requirement for inspectable legacy residue output.
- `docs_bilingual/implementation_plans/legacy_durable_residue_classification_plan.md` and `.zh-CN.md`: child-plan status, backlog, and evidence index updates.

Explicit non-goals:

- Do not launch, shut down, reuse, or auto-adopt durable teams or LangGraph threads.
- Do not mutate `.omx/state/` during classification.
- Do not push to GitLab or GitHub as part of this local integration package.

Rollout sequence:

1. Add failing tests for legacy residue fixture classes.
2. Implement read-only checker classification and summary output.
3. Update stable spec and child-plan evidence.
4. Run targeted tests, OpenSpec validation, repository guards, local gate, and local MR review.
5. Commit the feature branch and fast-forward merge it into local `main` only.

Rollback plan:

- Revert the single local commit or reset local `main` to the pre-merge rollback ref created before local integration.
- No remote rollback is required because remote publication is out of scope.
- No durable-state rollback is required because the checker is read-only.

Validation path:

- `python .\test\check_worktree_task_receipt.test.py` - runs the focused regression tests for worktree receipts and durable residue fixtures.
- `python .\tools\check_worktree_task_receipt.py --root . --json` - verifies read-only worktree receipt and durable residue classification output.
- `python .\tools\check_durable_artifact_state_surfaces.py --root . --json` - checks durable artifact/state-surface policy wiring.
- `openspec validate --all` - validates all OpenSpec specs and changes.
- `python .\tools\check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry, anchors, and bilingual pairs.
- `python .\tools\check_precommit_update_archive.py --root . --json` - checks pre-commit update and OpenSpec archive readiness.
- `python .\tools\run_openspec_guard.py --root . --json` - runs the aggregate repository OpenSpec guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate before integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local MR review gate before local main integration.

Mainline classification:

- Existing user-level durable-state isolation and team-mode orchestration maintenance under the current repository mainline.
