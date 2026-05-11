# 主工作区备份分支对账方案

## 状态

本 active 方案规定如何在保持本地 `main` 对齐 `gitlab/main` 的前提下，对账本地备份分支里的旧改动。

## 问题

本地主工作区已经对齐到 `gitlab/main`，但备份分支 `backup/mainworktree-dirty-before-main-align-20260426-234655` 仍然保存着之前的本地改动。这些改动可能包括有价值的名称解释补注释、文档更新、checker 更新和临时草稿。

仓库必须保持本地 `main` 等于 `gitlab/main`，同时不能丢失备份分支里有价值的内容。因此，对账必须通过干净 feature branch 和 GitLab merge request 进行，不能直接把整个备份分支合进 `main`。

## 目标

- 保持 `main` 和 `gitlab/main` 对齐。`main` 是本地镜像 GitLab main 的分支。
- 保留 `backup/mainworktree-dirty-before-main-align-20260426-234655`。这是保存对齐前脏工作区内容的本地备份分支。
- 把备份内容分成 local-only、target-only、both-changed-different、both-changed-same 四类。
- 通过小步 local-main-first integration package 迁移有价值的 local-only 和 both-changed-different 内容。
- 防止把整个备份分支直接合进 `main`。
- 在操作者明确选择文档目标前，不把临时草稿并入 main。

## 非目标

- 不合并整个备份分支。
- 不提交 `.worktrees/`。`.worktrees/` 是本地 Git secondary worktree 容器。
- 不推送备份分支，除非操作者明确要求远端备份。
- 不用旧备份内容覆盖 GitLab main 的新内容。
- 不在未经复核时把本地草稿当作正式文档。

## 对账来源和目标

- `backup/mainworktree-dirty-before-main-align-20260426-234655`：保存脏工作区内容的本地备份分支。
- `gitlab/main`：GitLab 远端跟踪分支，也是经过评审的权威目标。
- `e0e0acb8c4d70d891a1b91c9628b38f567966dc3`：本方案开始时的 GitLab main 提交。
- `81de0bbc2605915fb996446ac0fc15b3043092b3`：本方案开始时的本地备份提交。
- `afdbd34cc7ee71f3d7acf8000e030c571fa71be7`：用于分类备份分支和目标分支变化的共同基线。

## Phase 1：清单和护栏

新增 `tools/report_main_worktree_reconciliation.py`。这是只读报告脚本，用来比较备份内容和 `gitlab/main`。

脚本必须报告：

- `local_only`：备份分支更新但 `gitlab/main` 没更新的路径。
- `target_only`：`gitlab/main` 更新但备份分支没更新的路径。
- `both_changed_different`：双方都更新且最终内容不同的路径。
- `both_changed_same_content`：双方都更新但最终内容相同的路径。
- `local_changed_already_same_as_target`：看起来是本地改动但已经等同目标内容的路径。

生成：

- `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.md`：英文对账清单报告。
- `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.zh-CN.md`：中文对账清单报告。

## Phase 2：双方都更新的文档合并

创建 `reconcile/active-docs-three-way-merge`。这是从 `gitlab/main` 创建的干净分支，用来合并 active 文档。

人工合并：

- `docs_bilingual/project_startup_summary.md`：英文启动摘要，需要双方合并复核。
- `docs_bilingual/project_startup_summary.zh-CN.md`：中文启动摘要，需要双方合并复核。
- `docs_bilingual/implementation_plans/` 下的 active implementation plans：双方都更新过的 active 方案。
- `docs_bilingual/governance/` 下的 active governance files：双方都更新过的治理文档。

## Phase 3：checker 和 test 合并

创建 `reconcile/checker-three-way-merge`。这是从 `gitlab/main` 创建的干净分支，用来合并工具和测试。

人工合并：

- `tools/run_openspec_guard.py`：双方都更新过的 OpenSpec guard 入口脚本。
- `tools/check_name_clarity_rules.py`：双方都存在且内容不同的名称解释 checker。
- `tools/name_clarity_baseline.json`：名称解释 findings 的兼容基线。
- `test/run_openspec_guard_json.test.py`：双方都更新过的 guard JSON 测试。

## Phase 4：本地-only 双语文档复核

创建 `reconcile/local-only-doc-name-clarity`。这是从 `gitlab/main` 创建的干净分支，用来复核本地-only 文档更新。

只恢复备份分支里的本地-only 文档文件。只有在当前 GitLab main 状态下仍然有效的改动才能合入。

## Phase 5：OpenSpec 名称解释批次

创建小批量分支 `reconcile/openspec-name-clarity-batch-<n>`。这是从 `gitlab/main` 创建的 OpenSpec 补注释迁移分支。

每个批次必须：

- 只从备份分支恢复少量 OpenSpec 文件夹；
- 确认恢复内容是名称用途解释，而不是过期行为变更；
- 运行 `openspec validate --all`。这是 OpenSpec specs 和 changes 的完整验证命令；
- 运行 `python .\tools\check_name_clarity_rules.py --root . --json`。这是文档和 OpenSpec 名称解释 checker。

## Phase 6：临时草稿处置

除非明确提升为正式文档，否则本地草稿文件只保留在备份分支里：

- `commn_layer.md`：关于 legacy external provider 和 service 分层的本地笔记。
- `reference.md`：legacy external tooling 相关材料的本地参考列表。
- `rollout20260422.md`：本地 rollout 转录和研究笔记。
- `.githooks/.githooks/pre-commit`：嵌套 hook 路径，复用前必须人工复核。
- `.trae/.ignore`：本地 Trae ignore 文件，未经复核不能成为仓库策略。

## 每个对账 MR 的必需流程

```powershell
git fetch gitlab main
```

这条命令在创建分支前刷新 `gitlab/main`。

```powershell
git worktree add .worktrees/<name> -b <branch> gitlab/main
```

这条命令从最新 GitLab main 创建干净隔离 worktree。

```powershell
git checkout backup/mainworktree-dirty-before-main-align-20260426-234655 -- <path>
```

这条命令从备份分支恢复一个选定路径或路径组。

```powershell
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

这条命令在发布前运行仓库 OpenSpec guard。

## 验证

对账队列满足以下条件才健康：

- 每个 MR 后，本地 `main` 和 `gitlab/main` 仍然是同一个提交；
- 每个迁移路径都通过基于 `gitlab/main` 的干净分支进入；
- both-changed 文件经过人工合并，而不是直接覆盖；
- local-only OpenSpec 改动分批迁移并验证；
- 临时草稿不进入 main，除非操作者明确提升。
