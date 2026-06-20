## ADDED Requirements

### Requirement: 产品生命周期治理覆盖正文级运营文档

产品生命周期文档治理必须把生成的运营包正文文档视为执行层生命周期产物，并由 12 层堆栈、过程组式 Inputs / Tools And Techniques / Outputs 以及显式裁剪决策治理。

#### Scenario: 根据核心文档清单生成正文文档

- **GIVEN** Codex 或一人公司核心文档清单定义了文档家族和文件名
- **WHEN** Stage B 生成对应正文文档
- **THEN** 该文档必须识别自己的 12 层落位
- **AND** 它必须为执行层使用暴露 Inputs、Tools And Techniques、Outputs
- **AND** 它必须说明该文档如何参与完整、轻量、阶段局部、模块级或混合治理。

### Requirement: 裁剪可以是全项目、阶段局部、模块级或混合

生命周期治理必须区分全项目轻量架构、阶段局部轻量架构、模块级轻量架构，并在只有部分项目可以安全轻量时允许混合架构。

#### Scenario: 项目选择轻量范围

- **GIVEN** 正在规划一个项目、阶段或模块
- **WHEN** operator 记录裁剪决策
- **THEN** 决策必须说明是整个项目轻量、只有一个阶段轻量、只有一个模块轻量，还是整体采用混合方式
- **AND** 它必须说明所选范围为什么既不更重也不更轻
- **AND** 它必须定义升级到混合或完整架构的触发器。

### Requirement: Registry 把正文文档作为一等产物跟踪

双语文档 registry 必须把生成的正文文档作为一等生命周期产物跟踪，而不是把它们当作未登记 runtime cache。

#### Scenario: 添加生成的正文文档

- **GIVEN** 生成器创建英文主正文文档和 zh-CN 伴随文件
- **WHEN** 校验正文层
- **THEN** `docs_bilingual/docs_registry.yaml` 必须包含唯一 `doc_id`
- **AND** 它必须包含英文 canonical path 和 zh-CN companion path
- **AND** 生成文档必须是纳入源码控制的 Markdown，而不是被忽略的 cache 文件。
