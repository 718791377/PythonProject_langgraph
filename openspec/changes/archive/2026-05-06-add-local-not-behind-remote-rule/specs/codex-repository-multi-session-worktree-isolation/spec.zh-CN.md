## ADDED Requirements

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

仓库工作流 SHALL 保持本地 `main` 在新建可写任务、判断发布时机、push、创建 MR 或声明本地已对齐之前不落后于 `gitlab/main`。

local-first batching（本地优先批量发布）SHALL NOT 被当成允许继续基于陈旧远端基线工作的理由。

#### Scenario: 可写工作前本地 main 落后

- **GIVEN** `gitlab/main` 已经前进
- **AND** 本地 `main` 落后于它
- **WHEN** 会话准备创建新的可写任务分支
- **THEN** 会话 SHALL 先 fast-forward（快进）本地 `main` 再继续
- **AND** 该 freshness check（新鲜度检查）不得 reset 或丢弃 dirty work（脏工作）

#### Scenario: Feature branch 基于陈旧基线准备

- **GIVEN** 本地 feature branch 已经准备进入 release timing judgment（发布时机判断）
- **AND** 刷新后的 `gitlab/main` 显示该 feature branch 基于 stale base（陈旧基线）准备
- **WHEN** 会话评估 publication readiness（发布就绪度）
- **THEN** 它 SHALL 建议发布前先 rebase（变基）或 merge（合并）到刷新后的基线
- **AND** 只有用户明确接受风险时，MAY 继续从陈旧基线发布

#### Scenario: 本地仓库是最新的

- **GIVEN** 刷新后的 `gitlab/main` 与本地 `main` 一致
- **WHEN** 本地验证和 release-timing checks（发布时机检查）通过
- **THEN** 会话 MAY 建议远端发布
- **AND** GitLab pipeline 成功仍然是 merge gate（合并门禁）
