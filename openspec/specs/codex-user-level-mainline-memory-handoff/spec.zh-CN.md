# codex-user-level-mainline-memory-handoff 规范

## Purpose（目的）

定义 current mainline memory summary（当前主线记忆摘要）如何让 cold-start handoff（冷启动交接）与最新落地的 governance、checker、tooling 或 workflow 增量保持一致。

`current mainline memory summary` 是当前主线的会话交接摘要，用来告诉新会话仓库目前进展到哪里。
`governance` 是仓库治理规则文档，用来定义长期约束和发布边界。
`checker` 是可执行检查脚本，用来把安全规则从提示词提醒提升为脚本控制。
`tooling` 是辅助脚本或命令入口，用来支持仓库维护、验证或发布。
`workflow` 是任务执行流程，用来描述从设计、实施、验证到发布的顺序。

## Requirements（需求）

### Requirement: Mainline memory handoffs SHALL identify the latest landed increment

Current mainline memory summary 在列出候选下一步动作前，SHALL 先识别最新落地的 governance、checker、tooling 或 workflow 增量。

该 handoff SHALL 包含：

- 适用时列出最新归档的 OpenSpec change 名称；OpenSpec change 是一次受 OpenSpec 管理的变更单元。
- 适用时列出受影响的 script、checker 或 documentation path；这些路径说明本次增量落在哪些文件上。
- 当前 active-change 状态；active-change 是尚未归档的 OpenSpec change。
- 下一会话应重新打开设计，还是从已实现行为继续。
- 当仓库采用 GitLab-first plus GitHub mirror workflow（GitLab 优先并镜像到 GitHub 的流程）时，列出当前 publication-ref alignment（发布引用对齐状态）。
- 当最新落地增量新增 governance surface（治理入口）时，列出 policy routing pointer（策略路由指针）。

#### Scenario: A new cold-start session resumes after a checker-backed increment landed

- **WHEN** 新冷启动会话读取 current mainline memory summary
- **THEN** summary SHALL 识别最新落地的 checker-backed 增量
- **AND** 它 SHALL 说明是否存在 active OpenSpec changes
- **AND** 它 SHALL 列出安全的下一步选择，不暗示较早已完成增量仍需实现

#### Scenario: A new cold-start session resumes after MCP scope policy work landed

- **WHEN** 新会话在 MCP scope policy（MCP 范围策略）和 memory-handoff archive（记忆交接归档）工作落地后读取当前 mainline memory summary
- **THEN** summary SHALL 识别最新落地的 MCP Router scope policy 增量
- **AND** 它 SHALL 在推荐实施前说明是否存在 active OpenSpec changes
- **AND** 它 SHALL 把 MCP Router 与 Codex-direct MCP（Codex 直连 MCP）问题路由到稳定 MCP scope policy 文档
- **AND** 它 SHALL 避免把已经落地的 replay（重放）或 task-ownership（任务所有权）增量描述成下一步必做实施

### Requirement: Mainline memory handoffs SHALL refresh after durable rollout status-sync archive work lands

当仓库发布了会改变安全下一步队列的 durable rollout status-sync archive 后，当前 mainline memory summaries 必须刷新。

#### Scenario: Durable rollout status sync is archived after MR 5 is complete

- **WHEN** durable rollout status sync 和 archive closeout 已经落地到 GitLab `main`
- **AND** GitHub `main` 镜像同一个提交
- **THEN** 当前 mainline memory summary 必须把该 status-sync archive 标识为最新落地增量
- **AND** 必须说明 MR 5 helper mirror source-of-truth 工作已经完成
- **AND** 必须把后续 MR 6 readiness 或 automatic durable routing hookup 工作路由到 ownership precheck 之后的单独命名 OpenSpec changes

### Requirement: Mainline memory handoffs SHALL refresh after cleanup-output closeout and durable routing readiness land / cleanup-output closeout 和 durable routing readiness 落地后必须刷新 mainline memory handoff

当仓库已经发布 durable routing readiness closeout，并且又发布了会改变冷启动恢复或操作员控制面预期的 cleanup-output control closeout 后，当前 mainline memory summaries 必须刷新。

#### Scenario: Cleanup-output closeout lands after durable routing readiness / cleanup-output closeout 在 durable routing readiness 后落地

- **WHEN** MR 6 durable routing readiness 已经落地到 GitLab `main`
- **AND** Windows cleanup-output control implementation 和 archive closeout 也已经落地到 GitLab `main`
- **AND** GitHub `main` 镜像同一个最新提交
- **THEN** 当前 mainline memory summary 必须把这两个增量标记为已完成 baseline work
- **AND** 它必须在推荐下一步前说明是否存在 active OpenSpec changes
- **AND** 它必须把未来 live durable routing smoke 或 adoption-gate 工作路由到一个单独命名、经过 reviewed 的 change，并且该 change 必须说明 target repository、phase、task 和 operator consent boundary
- **AND** 它不得暗示已完成的 MR 6 readiness 或 cleanup-output 工作仍需要实施
