## ADDED Requirements

### Requirement: Repository Publication SHALL Prefer Local-First Runner Budgeting

仓库发布流程默认 SHALL 通过远端推送前的本地验证和批量整理来节省 GitLab runner minutes。

#### Scenario: 相关本地变更已准备好 review

- **GIVEN** 维护者在同一个 feature branch 上完成了一组相关变更
- **AND** 这些变更共享同一个主题、验证面和 rollback boundary
- **WHEN** 本地验证通过
- **THEN** 维护者 MAY 一次性推送该分支并创建或更新一个 GitLab MR
- **AND** GitLab pipeline 仍然是进入 GitLab `main` 前的 merge gate

#### Scenario: 仅为了节省 runner minutes 而想批量无关变更

- **GIVEN** 两个变更具有不同 review topics 或 rollback boundaries
- **WHEN** 维护者考虑仅为了减少 GitLab runner-minute 使用量而把它们合并发布
- **THEN** workflow SHALL 要求拆成不同 branch 或不同 MR
- **AND** 可评审性和回退安全 SHALL 优先于 CI 配额节省

#### Scenario: 用户明确要求提前跑远端 pipeline

- **GIVEN** 本地验证尚未全部完成
- **WHEN** 用户明确要求提前运行 GitLab pipeline check
- **THEN** 维护者 MAY 提前推送
- **AND** 该例外 SHALL 不得变成 routine checkpoints（常规检查点）的默认流程
