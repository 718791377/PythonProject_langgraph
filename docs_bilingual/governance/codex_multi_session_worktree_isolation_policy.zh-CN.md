---
doc_id: codex_multi_session_worktree_isolation_policy
lang: zh-CN
doc_class: governance
status: active
---

# Codex 多会话 Worktree 隔离治理策略

## 1. 目的

本策略定义多个 Codex 会话同时处理本仓库时，如何避免脏文件、分支漂移和跨会话覆盖风险。

核心规则是：

```text
一个可写任务 = 一个 Git worktree + 一个 feature branch
```

仓库根目录 `D:\PythonProject_langgraph` 是协调区和 mainline 镜像区；它不能变成多个会话共享的临时写入目录。

## 2. 权威边界

本策略属于仓库级治理。它适用于所有会修改本仓库的 Codex 会话，包括普通 Codex、oh-my-codex 包装会话、native subagents、durable-team workers，以及后续 LangGraph 驱动的执行上下文。

本策略不授权删除 worktree、重置分支或丢弃本地编辑。任何破坏性清理仍然必须先有 preservation-first plan（先保存再清理的计划）和操作者确认。

## 3. 必需 Worktree 模型

- `main` - 本地镜像已评审 `gitlab/main` 的分支；不要把它当作可写任务分支。
- `gitlab/main` - 指向权威 GitLab mainline 的远端跟踪分支。
- `github/main` - GitLab main 变绿后同步过去的 GitHub 镜像分支。
- `.worktrees/` - 本地 secondary Git worktrees 的容器；它是本地工作区基础设施，不是文档或源码目录。
- `backup/*` - 在风险对齐操作前保存脏工作区快照的本地备份分支命名空间。

每个可写任务必须使用：

1. 一个能说明任务的专用 feature branch。
2. 一个位于 `.worktrees/` 下的专用 worktree。
3. 一个 GitLab-first MR，合并后才能进入 `main`。

## 4. 多会话安全规则

多个会话可以并行准备相互独立的工作，但前提是写入范围相互隔离。

必需规则：

- 不要让两个会话写同一个 worktree。
- 不要让两个会话同时编辑同一批热点文件，除非由 leader 串行整合。
- 不要直接在 `main` 上写文件。
- 不要手动删除 `.worktrees/`；需要清理时，先做保存检查，再使用 Git worktree 命令。
- 不要假设某个脏文件一定属于当前会话。
- 在确认归属前，不要 reset、checkout、clean、move 或 delete 未知脏文件。
- GitLab MR 合并后，先把本地 `main` 分支引用快进到同一个 GitLab main commit，再把该 exact commit 同步到 GitHub。

## 5. 脏文件分类

处理脏文件前必须先分类：

- current-task edits（当前任务编辑） - 当前会话故意修改的文件。
- other-session edits（其他会话编辑） - 可能属于其他仍在运行或刚中断会话的文件。
- generated artifacts（生成产物） - checker、refresh 或 report 生成的文件。
- scratch notes（临时笔记） - 尚未批准进入正式文档的本地笔记。
- stale residue（陈旧残留） - 废弃 worktree 或生成输出，需要 preservation-first cleanup plan（先保存再清理的计划）。

如果归属未知，保留该文件并报告，不要为了图省事直接删除。

## 6. 脚本控制

这个安全边界不能只靠提示词提醒。

仓库提供：

- `tools/check_worktree_session_hygiene.py` - 只读 checker，用来检查已登记 Git worktrees、脏状态、重复脏路径和 `main` 对齐风险。

推荐用法：

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --json
```

上面的命令会运行只读 hygiene checker（工作区卫生检查器），并输出给冷启动会话或 CI 使用的 JSON 报告。

如果本地 feature branch 正在编辑，当前 worktree 有意处于 dirty 状态，可以使用：

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --allow-current-dirty --json
```

`--allow-current-dirty` 选项允许当前非 main worktree 处于 dirty 状态，但仍会检查 dirty `main` 和跨 worktree 冲突风险。

## 7. GitLab-First 集成

所有仓库变更仍然遵守 GitLab-first 发布流程：

1. 从最新 `gitlab/main` 创建 feature branch。
2. 为该分支使用专用 `.worktrees/<task>` worktree。
3. 推送到 GitLab 并创建 GitLab MR。
4. 等待 GitLab pipeline 通过。
5. 合并到 GitLab `main`。
6. 把 exact GitLab main commit 同步到 GitHub。
7. 快进本地 `main` 分支引用。

本仓库默认不使用 GitHub PR。

