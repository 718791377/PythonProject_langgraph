# 主工作区对齐 GitLab Main 安全方案

## 状态

本方案是当前仓库维护任务的 active 方案。它规定在把主工作区对齐到 `gitlab/main` 之前，如何先保护本地改动。`gitlab/main` 是 GitLab 远端 main 分支的本地跟踪引用，也是本仓库的上游新鲜度基线。

## 背景

`D:\PythonProject_langgraph` 是本仓库通常打开的主本地工作区，目前没有对齐 `gitlab/main`。`gitlab/main` 是 GitLab main 分支的远端跟踪引用，用作 local-main-first 流程下的上游新鲜度基线。

当前主工作区还有 tracked 修改和 untracked 文件。这些文件里可能有其他会话留下的真实更新，也可能有过期的 OpenSpec refresh 输出或临时草稿。因此，对齐操作必须是“先保全，再对齐”的维护任务，不能当成简单清理。

## 目标

- 在任何破坏性 Git 操作前保护本地改动。
- 在选择保留或丢弃前，把文件分成 remote-only、local-only、both-changed、already-equal 四类。
- 只有在备份证据存在后，才把本地 `main` 分支对齐到 `gitlab/main`。`main` 是本地用于镜像 GitLab main 的分支。
- 不提交也不手动删除 `.worktrees/`。`.worktrees/` 是保存 Git 注册 secondary worktree 的本地目录。
- 提供恢复路径，让冷启动会话可以从备份分支找回本地改动。

## 非目标

- 本方案不判断本地改动没有价值。
- 本方案不删除 `.worktrees/`。`.worktrees/` 是本地 secondary worktree 容器。
- 本方案不绕过 local-main-first 发布流程。
- 本方案不自动把本地临时笔记并入正式文档。
- 本方案不默认推送备份分支，除非操作者明确要求远端备份。

## 关键名称

- `D:\PythonProject_langgraph`：本仓库的主本地工作区，也是操作者通常打开的目录。
- `gitlab/main`：GitLab main 分支的远端跟踪引用，是上游新鲜度基线。
- `main`：本地 main 分支，对齐完成后应当和 `gitlab/main` 指向同一个提交。
- `HEAD`：当前工作区检出的提交，用来判断当前从哪里开始漂移。
- `merge-base`：当前 `HEAD` 和 `gitlab/main` 的共同祖先，用来区分本地漂移和线上推进。
- `backup/mainworktree-dirty-before-main-align-<timestamp>`：本地备份分支命名模式，用来保存当前脏工作区。
- `.worktrees/`：本地 secondary worktree 容器目录，由 Git worktree 机制管理。
- `.git/info/exclude`：本地-only 忽略文件，用来忽略本机路径而不修改仓库提交的 `.gitignore`。

## Phase 0：只读盘点

创建备份或 reset 之前，先运行只读检查：

```powershell
git fetch gitlab main
```

这条命令刷新 `gitlab/main` 引用，不修改当前工作区文件。

```powershell
git rev-parse HEAD
```

这条命令打印当前工作区提交，方便后续追溯备份来源。

```powershell
git rev-parse gitlab/main
```

这条命令打印最新 GitLab main 提交，让对齐目标明确。

```powershell
git merge-base HEAD gitlab/main
```

这条命令打印共同祖先，用来判断当前工作区是否落后 GitLab main。

```powershell
git status --porcelain=v1 --untracked-files=all
```

这条命令用稳定的机器可读格式列出 tracked 和 untracked 本地改动。

```powershell
git diff --name-status HEAD gitlab/main
```

这条命令列出当前 `HEAD` 之后 GitLab main 上发生变化的路径。

## Phase 1：分类

对齐前必须先给每个路径分类：

- Remote-only path：只在 `gitlab/main` 更新、本地没有更新，直接接受 GitLab 版本。
- Local-only path：只在本地更新、`gitlab/main` 没有更新，对齐前必须进入备份。
- Both-changed path：本地和 `gitlab/main` 都更新，后续需要人工合并或选择性迁移。
- Already-equal path：本地显示脏，但内容已经等于 `gitlab/main`，备份证据存在后可以安全 reset。

当前仓库已观察到的类别包括：

- `AGENTS.md`：仓库启动和路由说明文件，目前 `gitlab/main` 更新。
- `docs_bilingual/project_startup_summary.md`：英文启动摘要，目前本地和 `gitlab/main` 都更新，若本地内容有价值需要合并。
- `docs_bilingual/project_startup_summary.zh-CN.md`：中文启动摘要，目前本地和 `gitlab/main` 都更新，若本地内容有价值需要合并。
- `tools/run_openspec_guard.py`：OpenSpec guard 入口脚本，目前本地和 `gitlab/main` 都更新，需要合并判断。
- `.worktrees/`：Git 注册 secondary worktree 容器，目前是 local-only，但不是提交候选。
- `commn_layer.md`：本地临时笔记，目前是 local-only，需要操作者判断。
- `reference.md`：本地参考链接笔记，目前是 local-only，需要操作者判断。
- `rollout20260422.md`：本地 rollout 笔记，目前是 local-only，需要操作者判断。

## Phase 2：备份

对齐前先创建本地备份分支：

```powershell
git switch -c backup/mainworktree-dirty-before-main-align-<timestamp>
```

这条命令从当前脏工作区创建本地备份分支，不改变文件内容。

```powershell
git add -A -- . ':(exclude).worktrees/**'
```

这条命令暂存当前本地改动，但排除 `.worktrees/`，因为 Git 注册 worktree 不能当普通文件提交。

```powershell
git commit -m "Backup dirty main worktree before aligning main"
```

这条命令把当前脏工作区快照保存成本地备份提交，后续可以恢复。

如果某些 untracked 草稿文件不适合进入备份提交，先复制到本地备份目录：

```powershell
New-Item -ItemType Directory -Force .local\main-align-backups\<timestamp>
```

这条命令创建本地备份目录，用来保存不适合提交的草稿文件。

```powershell
Copy-Item commn_layer.md, reference.md, rollout20260422.md .local\main-align-backups\<timestamp>\ -ErrorAction SilentlyContinue
```

这条命令在这些草稿文件存在时，把它们复制进本地备份目录。

## Phase 3：对齐主本地 main 分支

备份提交存在后，再对齐本地 `main`：

```powershell
git switch main
```

这条命令切换到本地 main 分支，也就是应该镜像 GitLab main 的本地分支。

```powershell
git reset --hard gitlab/main
```

这条命令把本地 `main` 的 tracked 文件强制对齐为 `gitlab/main`。

把 worktree 容器加入本地-only 忽略：

```powershell
Add-Content .git\info\exclude "`n.worktrees/"
```

这条命令只让当前本机忽略 `.worktrees/`，不会修改仓库提交的忽略规则。

## Phase 4：验证对齐

运行最终检查：

```powershell
git status --short --branch
```

这条命令确认当前分支是否为 `main`，并显示是否还有本地残留文件。

```powershell
git rev-parse HEAD
```

这条命令打印对齐后的本地 `main` 提交。

```powershell
git rev-parse gitlab/main
```

这条命令打印 GitLab main 提交，应该和本地 `HEAD` 完全一致。

## Phase 5：后续恢复或迁移本地更新

如果后续要恢复 local-only 或 both-changed 路径，必须从备份分支恢复，而不是凭记忆重写：

```powershell
git show backup/mainworktree-dirty-before-main-align-<timestamp>:<path>
```

这条命令从备份分支打印指定文件内容，供人工检查。

```powershell
git checkout backup/mainworktree-dirty-before-main-align-<timestamp> -- <path>
```

这条命令把备份分支里的单个路径恢复到新的干净功能分支。

任何恢复出来的改动都必须走 local-main-first 流程：

- 从 `gitlab/main` 创建 feature branch：feature branch 是承载单组改动的评审分支。
- 只恢复一个选定路径或一个逻辑切片：逻辑切片是本次 MR 要评审的最小改动集合。
- 运行 repository checkers：repository checkers 是保护 OpenSpec 和文档规则的验证脚本。
- 需要远端确认时打开 GitLab merge request：GitLab merge request 是本仓库的远端评审与确认入口。
- GitLab 远端确认变绿后，或用户明确要求 direct mirror 时，再同步 GitHub：GitHub 是 mirror / sync 目标。

## 回滚

如果对齐后发现异常，切回备份分支：

```powershell
git switch backup/mainworktree-dirty-before-main-align-<timestamp>
```

这条命令回到保存本地改动的备份分支。

如果以后还要再次恢复本地 `main`，确认备份分支仍存在后，重新执行 Phase 3。

## 验收

本方案满足以下条件才算有效：

- 运行任何 `git reset --hard` 之前，备份分支已经存在。
- `.worktrees/` 被排除在提交之外，并且没有被手动删除。
- 对齐后，本地 `main` 和 `gitlab/main` 指向同一个提交。
- local-only 或 both-changed 内容后续只能通过新的 local-main-first 分支和 merge request 迁移。
