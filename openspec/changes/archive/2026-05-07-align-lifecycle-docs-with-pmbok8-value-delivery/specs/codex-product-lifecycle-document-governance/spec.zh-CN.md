## MODIFIED Requirements

### Requirement: PMI References Are A Governance Overlay

仓库 SHALL 将 PMI 项目管理参考作为 delivery、tailoring、quality、risk、change control、closing 和 value delivery 的治理叠加层，而不是用它替代产品与商业生命周期。

仓库 SHALL 将 PMBOK 第8版作为 value-delivery framing、project-canvas alignment、performance-domain thinking、AI-era project governance、hybrid delivery 和 tailoring 的主要叠加层。

仓库 SHALL 将 PMBOK 第6版和 Process Groups 参考作为 initiating、planning、executing、monitoring and controlling、closing，以及 input/tool/output discipline 的操作补充。

仓库 SHALL 将 PMBOK 第7版作为 principles、performance-domain、value-delivery 和 tailoring 的桥接层。

仓库 SHALL 将 Agile references 作为 uncertainty、MVP slices、feedback loops 和 small reversible releases 的适应式/混合式交付补充。

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** 维护者将 `PMP/` 作为本地私有 reference directory；`PMP/` 是本地保存 PDF 和网页参考资料的目录
- **WHEN** 维护者更新仓库 lifecycle documentation；lifecycle documentation 是生命周期文档集合
- **THEN** 更新内容只总结 repository-specific mappings；repository-specific mappings 是适用于本仓库的映射
- **AND** 更新内容说明该映射中哪个 reference 是 primary，哪些 references 是 supplemental
- **AND** 更新内容不复制 PMI 书籍正文
- **AND** 本地 `PMP/` reference directory 继续被 Git 忽略

### Requirement: Product Lifecycle Reference Defines The 0-8 Document Stack

仓库 SHALL 维护一份双语 product lifecycle reference，用来定义 cognitive narrative、business、market、strategy、product、technical、execution、growth 和 retrospective layers。

lifecycle reference SHALL 说明文档完成本身不是目标；document stack 存在的目的是支持 value identification、value alignment、value delivery、value verification 和 learning。

lifecycle reference SHALL 定义轻量 project canvas 或 initiative canvas，作为展开完整文档栈前可选的 alignment artifact。

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** 维护者阅读 product lifecycle reference；product lifecycle reference 是产品生命周期参考文档
- **WHEN** 维护者比较 document types；document types 是不同文档类型
- **THEN** 该 reference 解释 white paper 用于改变认知并说明方向为什么存在
- **AND** 该 reference 解释 North Star plan 用于把 strategy 转成 measurable direction、metrics、levers 和 staged execution
- **AND** 该 reference 解释 project canvas 可在展开更重文档前对齐 purpose、value、stakeholders、boundaries、risks、delivery style 和 outcome checks

## ADDED Requirements

### Requirement: Platform And Downstream Lifecycles Shall Track Value Outcomes

platform-build lifecycle 和 downstream-consumption lifecycle SHALL 在交付工件之外定义 value outcomes。

platform-build value outcomes SHALL 包括 operator friction reduction、cold-start continuation success、cross-session coordination quality、repo-local state safety、native Codex compatibility 和 rollback evidence。

downstream-consumption value outcomes SHALL 包括平台 adoption 是否减少 startup friction、减少 context loss、提升 delivery coordination、保持 repo-local truth，并提供 actionable upstream feedback。

#### Scenario: A lifecycle document describes a delivered platform or downstream slice

- **GIVEN** 某个 lifecycle document 描述 implementation 或 adoption slice；adoption slice 是平台能力被下游项目采用的切片
- **WHEN** 读者检查该 slice 是否成功
- **THEN** 文档识别 delivered artifact；delivered artifact 是已经交付的文件、脚本、模板或治理工件
- **AND** 文档识别该 artifact 想改善的 value outcome 或 adoption outcome
- **AND** 文档识别可用于更新下一切片的 feedback 或 retrospective evidence

### Requirement: Durable-Team Plans Shall Use Value Increment Release Slices

长期 durable-team implementation plan SHALL 保持 draft 状态，直到单个 release slices 通过 OpenSpec 被提升。

每个 release slice SHALL 在被视为 release-ready 前说明 target repository、phase、task scope、value increment、feedback point、validation path、rollback boundary 和 operator consent boundary。

release slice SHALL NOT 宣称完整 personal production durable-team target 已经实现，除非 production acceptance 和 rollback evidence 已完成。

#### Scenario: A maintainer plans a future durable-team release slice

- **GIVEN** 长期 durable-team implementation plan 仍是 draft
- **WHEN** 维护者定义 release slice；release slice 是一个可验证、可回滚的小版本交付切片
- **THEN** 该 slice 包含 value increment 和 feedback point，而不只是 task list
- **AND** 该 slice 包含 validation 和 rollback boundaries
- **AND** 该 slice 默认可通过一个 OpenSpec change 和一个 GitLab MR 评审，除非用户明确批准更大的 batch
