## 新增需求

### Requirement: 本地实施流程默认执行到远端发布门
对已经获得用户实施授权的仓库本地任务，仓库将本地流程视为已授权到本地 `main` 集成和受保护清理为止。

本地流程包括 feature worktree 创建、session claim 创建、本地检查、本地提交、local gate、local MR review、刷新 `gitlab/main` 基线、本地 rollback backup ref、`git merge --ff-only` 合入本地 `main`、合入后 local gate、completed claim 保存，以及清理已集成的本地 feature worktree 和本地 feature branch。

该默认本地授权必须停在远端发布门；不得授权 GitLab push、GitLab MR 创建/更新/合并、GitHub sync、删除 remote ref、删除 backup ref、force push、reset 或破坏性清理。

#### 场景：本地 package 已 ready
- **WHEN** feature worktree 已干净、已验证，且本地 `main` 不落后 `gitlab/main`
- **THEN** 会话可以创建 rollback backup ref 并快进合入本地 `main`，无需再次询问本地集成确认
- **AND** 清理前必须运行合入后 local gate

#### 场景：集成后本地 main 领先远端
- **WHEN** 本地 `main` 包含已集成 package，且 `gitlab/main` 或 `github/main` 落后
- **THEN** 会话必须报告 intentional remote lag
- **AND** 除非当前用户消息明确批准远端发布，否则必须停在任何远端变更前

### Requirement: 本地提交主题必须包含中文
仓库本地 feature commit 的提交主题必须包含中文。ASCII conventional prefix 只有在主题仍包含中文时才允许。

#### 场景：提交主题使用 ASCII prefix 和中文正文
- **WHEN** 本地 feature commit 主题为 `docs: 更新治理规则`
- **THEN** commit-language checker 必须通过

#### 场景：提交主题为纯 ASCII
- **WHEN** 本地 feature commit 主题为 `docs: update governance rules`
- **THEN** commit-language checker 必须失败
- **AND** local MR review 或 commit-msg hook 必须要求改为中文主题后才能完成

### Requirement: 完整本地流程必须有受保护 helper
仓库必须提供 `tools/complete_local_flow_to_remote_gate.py`，作为 dry-run 优先的完整本地流程 helper。execute 模式下，该 helper 必须要求 feature worktree 干净、主目录 `main` worktree 干净，运行 local gate 和 local MR review，创建 rollback backup ref，快进合入本地 `main`，运行合入后 local gate，并停在远端发布前。

#### 场景：implementation plan 更新已本地 ready
- **WHEN** implementation-plan 更新已经在干净 feature branch 上提交
- **THEN** helper 必须能展示或执行直到 `git merge --ff-only <feature-branch>` 的本地流程
- **AND** 不得 push GitLab、变更 GitLab MR 或同步 GitHub
