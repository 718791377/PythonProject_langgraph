## ADDED Requirements / 新增要求

### Requirement: Mainline memory handoffs SHALL refresh after durable rollout status-sync archive work lands / durable rollout status-sync 归档落地后必须刷新 mainline memory handoff

当仓库发布了会改变安全下一步队列的 durable rollout status-sync archive 后，当前 mainline memory summaries 必须刷新。

#### Scenario: Durable rollout status sync is archived after MR 5 is complete / MR 5 完成后 durable rollout status sync 已归档

- **WHEN** durable rollout status sync 和 archive closeout 已经落地到 GitLab `main`
- **AND** GitHub `main` 镜像同一个提交
- **THEN** 当前 mainline memory summary 必须把该 status-sync archive 标识为最新落地增量
- **AND** 必须说明 MR 5 helper mirror source-of-truth 工作已经完成
- **AND** 必须把后续 MR 6 readiness 或 automatic durable routing hookup 工作路由到 ownership precheck 之后的单独命名 OpenSpec changes
