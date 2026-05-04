## ADDED Requirements / 新增需求

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