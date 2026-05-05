# codex-product-lifecycle-document-governance 规格增量

## ADDED Requirements

### Requirement: PMI References Are A Governance Overlay

仓库必须把 PMI 项目管理参考资料作为 delivery、tailoring、quality、risk、change control 和 closing 的治理叠加层，而不是用它替代产品与商业生命周期。

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** 维护者把 `PMP/` 作为本地私有参考目录
- **WHEN** 维护者更新仓库生命周期文档
- **THEN** 更新内容只能总结本仓库特定映射
- **AND** 更新内容不得复制 PMI 书籍正文
- **AND** 本地 `PMP/` 参考目录继续被 Git 忽略

### Requirement: Process Groups Map To OpenSpec Delivery Gates

仓库必须把 PMI process group model 映射到 OpenSpec 和 GitLab-first delivery gates。

#### Scenario: A platform change moves from idea to archive

- **GIVEN** 平台 change 通过 OpenSpec 和 GitLab 管理
- **WHEN** 该 change 被规划和交付
- **THEN** initiating 映射到 proposal 和类似 project charter 的范围定义
- **AND** planning 映射到 design、tasks、risks、validation、release 和 rollback planning
- **AND** executing 映射到 implementation work
- **AND** monitoring and controlling 映射到 checkers、pipeline、diff review 和 change control
- **AND** closing 映射到 archive、stable spec sync 和 lessons learned

### Requirement: Agile Guidance Supports Exploratory And Hybrid Work

仓库必须把 agile guidance 用于不确定、探索型、MVP 和反馈驱动工作，同时为高风险或范围清晰的交付保留 predictive process gates。

#### Scenario: A task is not yet clear enough for implementation

- **GIVEN** 请求的工作仍存在未解决的市场、产品或技术不确定性
- **WHEN** leader 选择执行方式
- **THEN** 工作先从小型 exploration、spike 或 MVP slice 开始
- **AND** 在计划冻结且存在独立执行切片之前，不启动 durable team
