## ADDED Requirements

### Requirement: Completed OpenSpec Changes SHALL Use Archive-Before-Publication Packaging

对已经本地完成、准备发布的 OpenSpec change，仓库流程 SHALL（必须）在打开 GitLab MR 前，在同一个 feature branch 内先 archive 该 change。

最终 publication package（发布包）SHALL（必须）在一个 MR 中同时包含实现或文档变更、归档后的 OpenSpec change 目录，以及被提升后的 stable spec 更新。

two-MR publication（双 MR 发布）只允许在实现规模大或风险高、需要先通过远端 CI 或 MR review 确认实现、archive promotion 会产生大量 stable-spec 冲突，或用户明确要求 implementation-only MR 时使用。

#### Scenario: Small completed governance change is ready to publish

- **GIVEN** 一个小型 governance、documentation、checker 或 test change 已经在 feature worktree 中完成
- **AND** 本地实现验证已经通过
- **WHEN** 会话准备发布建议
- **THEN** 它 SHALL 在打开 GitLab MR 前，在同一个 feature branch 内 archive 该 OpenSpec change
- **AND** 它 SHALL 在 archive 提升 stable specs 后重新运行本地验证
- **AND** 该 MR SHALL 同时包含实现、归档移动和 stable spec 更新

#### Scenario: Two-MR exception is justified

- **GIVEN** 实现规模大或风险高
- **OR** 需要先通过远端 CI 或 MR review 确认实现
- **OR** archive promotion 会产生大量 stable-spec 冲突
- **OR** 用户明确要求 implementation-only MR
- **WHEN** 会话建议发布
- **THEN** 它 MAY 先建议 implementation-only MR
- **AND** 它 SHALL 说明例外原因
- **AND** 它 SHALL 留下可见的 follow-up archive path，而不是宣称 OpenSpec 生命周期已经关闭

#### Scenario: Completed active change reaches main

- **GIVEN** 实现已经合并到 `main`
- **AND** 它的 OpenSpec change 仍处于 active 且 tasks 已完成
- **WHEN** 仓库评估 OpenSpec 生命周期健康度
- **THEN** 它 SHALL 把该状态视为 lifecycle gap（生命周期缺口）
- **AND** 它 SHALL 优先做 archive follow-up，再打开无关发布工作
