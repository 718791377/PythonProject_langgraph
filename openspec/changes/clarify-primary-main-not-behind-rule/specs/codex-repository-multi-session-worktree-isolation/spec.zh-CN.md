## MODIFIED Requirements

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

仓库流程必须在新建可写任务、发布时机判断、push、创建/更新 MR 或声明主线状态之前，保持本地 `main` 不落后于 `gitlab/main`。

主目录 `D:\PythonProject_langgraph` 必须作为 primary main worktree（主 main 工作区）。它必须检出本地 `main`，不得落后于本地 `main` 分支引用，正常情况下应该与本地 `main` 分支引用完全一致。

local-first batching（本地优先批量发布）不得被用作继续使用陈旧远端基线的许可。

#### Scenario: Local main is behind before writable work

- **GIVEN** `gitlab/main` 已推进
- **AND** 本地 `main` 落后于它
- **WHEN** 会话准备创建新的可写任务分支
- **THEN** 会话必须先 fast-forward（快进）本地 `main` 再继续
- **AND** worktree hygiene checker 必须失败，直到本地 `main` 不再落后于 `gitlab/main`
- **AND** 该新鲜度检查不得 reset（重置）或丢弃脏工作

#### Scenario: Primary main worktree is not on local main

- **GIVEN** 主目录 `D:\PythonProject_langgraph` 没有检出本地 `main`
- **WHEN** worktree hygiene checker 运行
- **THEN** checker 必须失败
- **AND** 会话必须停止可写工作，直到主目录 hygiene 问题被解决

#### Scenario: Primary main worktree is behind local main

- **GIVEN** 主目录 `D:\PythonProject_langgraph` 已检出本地 `main`
- **AND** 它的 HEAD 不同于本地 `main` 分支引用
- **WHEN** worktree hygiene checker 运行
- **THEN** checker 必须失败
- **AND** 失败信息必须要求操作者把主目录 checkout（检出）或 fast-forward（快进）到本地 `main`

#### Scenario: Local main is ahead of gitlab main

- **GIVEN** 刷新后的 `gitlab/main` 是本地 `main` 的祖先
- **WHEN** worktree hygiene checker 运行
- **THEN** checker 必须把本地 `main` 视为没有落后于 `gitlab/main`
- **AND** 它必须提醒操作者不要把主目录 `main` 当作功能工作区

#### Scenario: Feature branch was prepared on a stale base

- **GIVEN** 本地 feature branch 已准备进入发布时机判断
- **AND** 刷新后的 `gitlab/main` 显示该 feature branch 基于陈旧基线准备
- **WHEN** 会话评估发布准备度
- **THEN** 它必须建议在发布前 rebase（变基）或 merge（合并）到刷新后的基线
- **AND** 只有用户明确接受风险时，才可以继续使用陈旧基线

#### Scenario: Local repository is current

- **GIVEN** 刷新后的 `gitlab/main` 与本地 `main` 一致
- **WHEN** 本地验证和发布时机检查通过
- **THEN** 会话可以建议远端发布
- **AND** GitLab pipeline 成功仍然是合并门禁
