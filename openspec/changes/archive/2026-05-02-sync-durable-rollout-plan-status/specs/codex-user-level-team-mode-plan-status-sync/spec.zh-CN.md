## ADDED Requirements / 新增要求

### Requirement: Durable-state rollout queues SHALL not point at already archived slices as next active work / durable-state rollout 队列不得把已归档切片列为下一步 active work

一旦仓库证据显示某个 rollout slice 已经落地、通过验证并归档，双语 durable-state implementation plans 必须把该 slice 标记为已完成。

#### Scenario: Helper mirror source-of-truth slice has already landed / helper mirror source-of-truth 切片已经落地

- **WHEN** 仓库包含 helper mirror source-of-truth 切片的归档证据
- **AND** 稳定 specs 和 tests 已经验证 helper mirror provenance contract
- **THEN** cross-session durable-state isolation plan 必须把 MR 5 标记为已完成
- **AND** 不得继续把 MR 5 描述为下一步 active implementation slice
- **AND** 必须把 MR 6 或有界 MR 6 readiness review 标识为下一步 decision point
