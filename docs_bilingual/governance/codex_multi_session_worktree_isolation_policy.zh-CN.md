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
- 在创建新的任务 worktree、编辑文件、修复 guard 失败项，或接手 OpenSpec / governance artifacts 之前，必须先执行任务认领预检。任务认领预检是一种只读扫描，用来在创建新写入范围前识别语义上的归属信号。
- 任务认领预检必须检查已登记 Git worktrees、本地分支、远端跟踪分支、打开中的 GitLab MRs、active OpenSpec changes、本地 `.omx/session-claims/*.json` 认领文件，以及目标路径，包括 ignored files。
- 只要 worktree 名称、branch 名称、MR 标题、MR source branch、OpenSpec change id、claim path 或目标文件路径出现语义匹配，就应视为 ownership signal（归属信号）；即使对应 worktree 是干净的、也没有领先 `main` 的提交，也仍然算作认领信号。
- 如果发现匹配的 ownership signal，在 leader 明确串行化 handoff、继续使用已有 worktree，或把该信号归类为 completed stale residue 之前，都必须把该任务视为已认领。
- 位于 guard 扫描目录中的 ignored 或 local-only 文件，只要会影响仓库检查结果，就仍然是 task object（任务对象）。在修复、移动、排除或删除它们之前，必须先判断其预期归属。
- GitLab MR 合并后，先把本地 `main` 分支引用快进到同一个 GitLab main commit，再把该 exact commit 同步到 GitHub。

## 5. 脏文件分类

处理脏文件前必须先分类：

- current-task edits（当前任务编辑） - 当前会话故意修改的文件。
- other-session edits（其他会话编辑） - 可能属于其他仍在运行或刚中断会话的文件。
- generated artifacts（生成产物） - checker、refresh 或 report 生成的文件。
- scratch notes（临时笔记） - 尚未批准进入正式文档的本地笔记。
- stale residue（陈旧残留） - 废弃 worktree 或生成输出，需要 preservation-first cleanup plan（先保存再清理的计划）。

如果归属未知，保留该文件并报告，不要为了图省事直接删除。

接管任务前必须先分类任务认领状态：

- unclaimed（未认领） - worktrees、branches、MRs、OpenSpec changes、claim files 或目标路径中都不存在语义匹配。
- claimed-not-started（已认领但未开始） - 存在匹配 worktree、branch、MR、OpenSpec change、claim file 或 ignored target path，但还没有 dirty diff、额外提交或打开中的 MR 进展。
- in-progress（处理中） - 匹配 worktree 已经有 dirty files、领先提交、open MR、active OpenSpec change，或带有重叠路径的 active claim。
- completed-stale（已完成但残留） - 匹配 branch 或 claim 属于已经合并或归档的工作；只有 leader 明确把 handoff 串行化并确认 preservation-safe 后，才可以复用。

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



### 6.1 会话认领规则

在任何会把 feature worktree 变成 dirty 状态的写入任务开始前，当前会话必须先创建本地会话认领文件。

- `.omx/session-claims/` - 本地忽略的会话认领目录，用来声明当前会话拥有哪个 OpenSpec change 或路径范围；它不是 `.omx/state/` durable truth。
- `.omx/session-claims/<session>.json` - 单个会话认领文件，用 JSON 记录会话 ID、分支、worktree、任务类型、OpenSpec change 和路径范围。
- `tools/check_session_ownership_claims.py` - 只读 checker，用来扫描所有已注册 Git worktree 的本地 claim 文件，并在重复认领同一个 OpenSpec change 或重叠路径范围时失败。

示例 claim 文件：

```json
{
  "schema_version": 1,
  "session_id": "session-ownership-claims",
  "status": "active",
  "branch": "feature/session-ownership-claims",
  "worktree": "D:\\PythonProject_langgraph\\.worktrees\\session-ownership-claims",
  "task_type": "implementation",
  "openspec_changes": ["formalize-session-ownership-claims"],
  "paths": [
    "tools/check_session_ownership_claims.py",
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md",
    "openspec/changes/formalize-session-ownership-claims"
  ]
}
```

`session_id` 是本地操作者可读的会话名称，`openspec_changes` 是当前会话认领的 OpenSpec change 列表，`paths` 是当前会话认领的仓库相对热点路径范围。

推荐检查命令：

```powershell
python .\tools\check_session_ownership_claims.py --root . --allow-current-dirty --json
```

上面的命令会运行只读会话认领 checker，并输出 JSON 报告，供冷启动会话或本地发布前检查使用。

?? checker ????????

- ?? claim ??????? `.omx/session-claims/*.json` ????`.omx/session-claims/*.json` ??? ignored JSON ????????????????? OpenSpec change ??????
- ?????????????????? worktrees?branches?remote-tracking branches?active OpenSpec changes?active claim files?target paths??? ignored ? local-only ? guard-scanned files????????????????? checker-backed ???

?????? worktree ??? guard ??????????????????

```powershell
python .\tools\check_session_ownership_claims.py --root . --precheck-task "<task-slug-or-description>" --target-path "<repo-relative-path>" --openspec-change "<change-id>" --json
```

??????????????? checker?`--precheck-task` ???????????`--target-path` ??????????`--openspec-change` ???????? OpenSpec change id?`--json` ???????????????????????? token???? `--check-gitlab-mrs` ????? GitLab MRs ????????????????? GitLab MRs ??? fail closed ???????? `--require-gitlab-mrs`?

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

## 8. OpenSpec 生命周期

任何创建或修改本策略的变更都属于结构性仓库治理变更，必须遵守本仓库 OpenSpec 生命周期。

必需生命周期：

1. 实施前先创建或更新 OpenSpec change。
2. 让治理策略、checker 行为和 guard 集成与该 change 保持一致。
3. 发布前运行仓库验证命令。
4. 在实现完成后 archive 该 OpenSpec change，使 delta spec 进入 stable spec。
5. 通过 GitLab-first 流程发布 archive 和 stable spec。

归档隔离规则：

- 如果 change 会影响代码、可执行检查、CI、stable specs、startup instructions、仓库指令面或结构性治理规则，必须先在专用 archive worktree 中完成归档，再合回主工作区。专用 archive worktree 是只用于 archive branch 及其 stable-spec 更新的独立 Git worktree。
- archive worktree 必须先通过相关验证命令，之后才能提交 archive branch。archive branch 合入主工作区后，主工作区必须再次通过验证。
- 纯说明性文本改动如果不改变可执行的仓库行为，可以使用轻量归档流程；无法判断时应使用专用 archive worktree 流程。

如果 worktree 隔离相关 OpenSpec change 已经实现并合并到 `main`，就不要继续让它保持 active。即使 tasks 全部勾选，完成后仍然 active 也是生命周期缺口。
