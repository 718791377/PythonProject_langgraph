## ADDED Requirements

### Requirement: Release Timing SHALL Be Recommended By The Active Session Before Remote Publication

本地批次推送到 GitLab 之前，当前会话模型 SHALL 判断该批次是否适合远端发布，并向用户提出 publish-or-wait recommendation（发布或等待建议）。

用户 SHALL 仍然是 release decision authority（发布决策权威）。

#### Scenario: 本地批次适合发布

- **GIVEN** local validation（本地验证）已经通过
- **AND** active changes（活跃变更）已经完成或归档
- **AND** review scope（评审范围）和 rollback boundary（回退边界）是一致的
- **WHEN** 当前会话评估 release timing（发布时机）
- **THEN** 它 SHALL 向用户建议 publishing（发布）
- **AND** 它 SHALL 说明为什么这次 runner-minute cost（runner 分钟成本）值得消耗

#### Scenario: 本地批次应该等待

- **GIVEN** local validation（本地验证）尚未通过
- **OR** 预计马上还有 same-topic work（同主题工作）
- **OR** review scope（评审范围）或 rollback boundary（回退边界）不清晰
- **WHEN** 当前会话评估 release timing（发布时机）
- **THEN** 它 SHALL 建议 waiting（继续等待）
- **AND** 它 SHALL 说明远端发布前还应完成哪些本地工作

#### Scenario: 用户确认发布决策

- **GIVEN** 当前会话已经提出 publish-or-wait recommendation（发布或等待建议）
- **WHEN** 用户确认 publishing（发布）
- **THEN** 会话 MAY 推送到 GitLab 并创建或更新 MR
- **AND** GitLab pipeline 仍然是 merge gate（合并门禁）
