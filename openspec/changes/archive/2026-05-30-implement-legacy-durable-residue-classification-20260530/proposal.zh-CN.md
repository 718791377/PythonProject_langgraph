# 变更：实现 Legacy Durable Residue 分类

## 为什么

旧版 repo-local `.omx` durable residue 可能在早期 native OMX team、LangGraph thread 或 selector 实验后保留下来。冷启动会话需要可检查证据，把安全清理候选、受保护的 unmanaged state、stale selector、当前 active selector authority 和已完成 LangGraph state 区分开，同时不得自动接管 unmanaged team 或 stale workflow。

## 变更内容

- 扩展 `tools/check_worktree_task_receipt.py`，在既有 worktree receipt 分类旁输出只读 `durable_residue_classification`。
- 为 durable residue record 增加稳定的 safe-next-action 字段，并明确 `auto_adopt_allowed: false`。
- 为 non-empty unmanaged native team residue、completed LangGraph state、stale selector、active current selector 和 checker 汇总输出添加回归测试。
- 更新 durable-state cleanup and reconciliation 稳定 spec，要求该 legacy residue 可检查输出。

## 影响

影响范围：

- `tools/check_worktree_task_receipt.py`：只读 durable residue 分类实现。
- `test/check_worktree_task_receipt.test.py`：durable residue fixture 类回归测试。
- `openspec/specs/codex-user-level-durable-state-cleanup-and-reconciliation/spec.md`：可检查 legacy residue 输出的稳定要求。
- `docs_bilingual/implementation_plans/legacy_durable_residue_classification_plan.md` 与 `.zh-CN.md`：子方案状态、任务清单和证据索引更新。

明确非目标：

- 不启动、关闭、复用或自动接管 durable team 或 LangGraph thread。
- 分类过程中不修改 `.omx/state/`。
- 本地集成包不推送 GitLab 或 GitHub。

发布顺序：

1. 为 legacy residue fixture 类添加失败优先测试。
2. 实现只读 checker 分类和汇总输出。
3. 更新稳定 spec 与子方案证据。
4. 运行 targeted tests、OpenSpec validation、repository guard、local gate 和 local MR review。
5. 提交 feature 分支并仅 fast-forward 合入本地 `main`。

回滚计划：

- revert 单个本地提交，或把本地 `main` reset 回本地集成前创建的 rollback ref。
- 因远端发布不在范围内，不需要远端回滚。
- checker 只读，不需要 durable-state 回滚。

验证路径：

- `python .\test\check_worktree_task_receipt.test.py` - ?? worktree receipt ? durable residue fixture ????????
- `python .\tools\check_worktree_task_receipt.py --root . --json` - ???? worktree receipt ? durable residue ?????
- `python .\tools\check_durable_artifact_state_surfaces.py --root . --json` - ?? durable artifact/state-surface policy wiring?
- `openspec validate --all` - ???? OpenSpec specs ? changes?
- `python .\tools\check_implementation_plan_rules.py --root . --json` - ?? implementation-plan registry?anchors ? bilingual pairs?
- `python .\tools\check_precommit_update_archive.py --root . --json` - ?? pre-commit update ? OpenSpec archive readiness?
- `python .\tools\run_openspec_guard.py --root . --json` - ?????? OpenSpec guard?
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - ????????? local CI gate?
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - ?? main ????? local MR review gate?

主线分类：

- 属于当前仓库主线下既有 user-level durable-state isolation 与 team-mode orchestration 维护。
