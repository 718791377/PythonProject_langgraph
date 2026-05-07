# Proposal：澄清主 main 工作区新鲜度规则

## 摘要

澄清 `D:\PythonProject_langgraph` 是 primary main worktree（主 main 工作区），必须检出本地 `main`，并且不得落后于本地 `main`。本地 `main` 在开始写入工作、发布判断、push、创建/更新 MR 或声明主线状态前，不得落后于最新拉取的 `gitlab/main`。

## 动机

之前的表述是主目录必须与 `main` 对齐，容易被理解为所有场景都要求绝对相等，没有清楚表达预期的新鲜度链路：

```text
主 main 工作区不得落后于本地 main；本地 main 不得落后于最新 gitlab/main
```

该规则还必须有 checker 支撑，不能只停留在提示词提醒。

## 范围

- 更新 `AGENTS.md` 仓库指令面。
- 更新双语 worktree 隔离治理策略。
- 更新 `tools/check_worktree_session_hygiene.py`，让本地 `main` 落后于 `gitlab/main` 成为错误；本地 `main` 领先于 `gitlab/main` 时按“不落后”处理。
- 增加落后和领先两种场景的单元测试。

## 非目标

- 不授权直接在主目录 `main` 上实施功能。
- 不直接 push 或 merge `main`。
- 不清理或删除已有 worktree。
