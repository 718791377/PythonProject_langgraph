# codex-product-lifecycle-document-governance 规格

## Purpose

定义本仓库的产品与商业文档生命周期图，并保持 Codex 平台建设文档和下游项目消费平台能力文档相互分离。

## Requirements

### Requirement: Product Lifecycle Reference Defines The 0-11 / 12-Layer Document Stack

仓库必须维护一份双语产品生命周期参考，定义认知叙事、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营和复盘层。该参考还必须总结从本地 `Business Management/` 源库综合出的仓库特定经验，且不得复制长篇源书正文。

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** 维护者阅读产品生命周期参考
- **WHEN** 维护者比较文档类型
- **THEN** 该参考说明白皮书用于改变认知，并解释为什么该方向存在
- **AND** 该参考说明北极星 Plan 属于指标层，用于把战略转化为可衡量方向、输入指标、护栏指标和分阶段决策阈值

#### Scenario: A maintainer applies the Business Management source library

- **GIVEN** 维护者阅读产品生命周期参考
- **WHEN** 维护者需要有源库支撑的生命周期指导
- **THEN** 该参考把本地 Business Management 源库主题映射到认知、商业、市场发现、战略、指标、产品、架构、组织、执行、增长、运营和学习循环
- **AND** 它把指导表达为仓库特定运营规则，而不是源书摘录

### Requirement: Platform Build And Project Consumption Stay Separate

仓库必须把 Codex CLI durable-team 平台建设生命周期，与后续项目消费该平台的生命周期分开记录。

#### Scenario: A later project uses the platform templates

- **GIVEN** 后续项目接收 templates、user-level runtime policies 和 subagent profiles
- **WHEN** 该项目开始自己的工作
- **THEN** 该项目拥有自己的 `AGENTS.md`；这是项目级 Codex 指令文件
- **AND** 该项目拥有自己的 `openspec/`；这是项目本地 OpenSpec 治理树
- **AND** 该项目拥有自己的 `.omx/state/`；这是项目本地 durable truth 目录

### Requirement: Platform Documents May Define Shared Governance But Not Business Runtime Truth

Codex 平台仓库可以定义可复用 governance、templates、checkers、role policies、release gates 和 shared tooling，但不得成为下游业务项目的 repo-local durable truth。

#### Scenario: A business project learns a reusable governance lesson

- **GIVEN** 经验教训来自下游业务项目
- **WHEN** 该经验足够通用，可以改进平台
- **THEN** 该项目必须先把它记录为 upstream feedback
- **AND** 平台只能通过平台 OpenSpec change 采纳该经验

### Requirement: PMI References Are A Governance Overlay

仓库必须把 PMI 项目管理参考资料作为 delivery、tailoring、quality、risk、change control 和 closing 的治理叠加层，而不是用它替代产品与商业生命周期。

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** 维护者把 `PMP/` 作为本地私有参考目录；该目录保存本地参考资料并继续被 Git 忽略
- **WHEN** 维护者更新仓库生命周期文档
- **THEN** 更新内容只能总结本仓库特定映射
- **AND** 更新内容不得复制 PMI 书籍正文
- **AND** 本地 `PMP/` 参考目录继续被 Git 忽略

### Requirement: Process Groups Map To OpenSpec Delivery Gates

仓库必须把 PMI process group model 映射到 OpenSpec 和 local-main-first delivery gates。OpenSpec 是仓库治理工作流；local-main-first delivery gates 是以本地 main 集成为先，并保留 GitLab/GitHub 远端确认与镜像的交付流程。

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

### Requirement: Platform White Paper And MRD Are First-Class Lifecycle Documents

仓库 SHALL 维护 Codex CLI personal production durable-team platform 的第一类双语 white paper 和 MRD 文档，然后才能把下游 implementation plans 视为完整 lifecycle coverage。

#### Scenario: A maintainer follows the lifecycle stack

- **GIVEN** 维护者阅读 platform lifecycle documentation（平台生命周期文档）
- **WHEN** 维护者需要 cognitive narrative（认知叙事）和 market requirements（市场需求）
- **THEN** 维护者可以在 `docs_bilingual/whitepapers/` 找到 canonical white paper；`docs_bilingual/whitepapers/` 是白皮书目录，用来保存认知叙事文档
- **AND** 维护者可以在 `docs_bilingual/market_requirements/` 找到 MRD；`docs_bilingual/market_requirements/` 是市场需求目录，用来保存 market-requirements documents
- **AND** concrete workload-to-profile mappings（具体工作负载到 profile 的映射）位于 MRD appendix，而不是单独的 implementation-plan reference

### Requirement: 生命周期治理定义两个 12 层目标架构

仓库必须基于本地 Business Management 与 PMP 源库定义两个明确的 12 层架构目标：Codex CLI 个人开发者生产级持久化团队目标，以及个人级生产级一人公司经营系统目标。

#### Scenario: 维护者比较两个目标

- **GIVEN** 维护者阅读产品生命周期文档
- **WHEN** 维护者比较 Codex 平台目标与一人公司目标
- **THEN** Codex 平台目标列出 12 层主干、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent 和 12 本推荐书籍
- **AND** 一人公司目标列出 12 层主干、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍和 12 个最小启动文档

### Requirement: 面向执行的生命周期指导使用过程组式写法

任何影响执行的生命周期指导，都必须用过程组式写法表达，并为每个层级或交付门区分输入、工具与技术、输出。

#### Scenario: 维护者规划一个生命周期驱动的变更

- **GIVEN** 维护者使用生命周期文档进行执行规划
- **WHEN** 维护者检查某个生命周期层或交付门
- **THEN** 指导说明启动工作的输入
- **AND** 指导说明用于分析、决策、执行、监控或收尾的工具与技术
- **AND** 指导说明会成为交付物、证据或其他层级输入的输出

### Requirement: 本地参考覆盖只能摘要，不能复制源文本

仓库必须按文件、格式、页数、spine item 数与读取方式摘要本地 Business Management 与 PMP 参考覆盖，不得提交抽取源文本，也不得复现长篇版权内容。

#### Scenario: 维护者审计来源支撑的生命周期更新

- **GIVEN** 维护者阅读来源综合文档
- **WHEN** 维护者检查参考库如何被使用
- **THEN** 文档说明 PDF 按页读取、EPUB 按 spine item 读取、Markdown 按全文读取
- **AND** 文档只总结仓库特定治理映射
- **AND** 被忽略的抽取工件仍位于 Git 跟踪文件之外

### Requirement: 生命周期裁剪规则定义完整架构与轻量架构的使用

仓库必须定义明确的生命周期裁剪规则，用于判断什么时候使用完整 12 层目标架构，什么时候使用轻量架构。这些规则必须区分整个项目轻量、阶段局部轻量、模块级轻量，以及重新升级到更完整治理的条件。

#### Scenario: 维护者为生命周期驱动变更选择治理深度

- **GIVEN** 维护者阅读产品生命周期裁剪指导
- **WHEN** 工作影响金钱、用户、信任、合规、安全、数据、runtime entrypoints、release safety、跨项目模板、durable state、共享接口或长期平台行为
- **THEN** 指导要求对受影响范围采用完整架构路径
- **AND** 当低风险阶段或模块的边界与回滚证据明确时，指导仍可允许未受影响的低风险阶段或模块保持轻量

#### Scenario: 维护者安全使用轻量路径

- **GIVEN** 请求的工作是小型本地 note、低风险内部工具、一次性 spike、可逆文档实验，或没有外部用户、金钱、信任边界、合规影响或 durable-state 变更的早期想法
- **WHEN** 维护者选择轻量路径
- **THEN** 指导说明轻量化适用于整个项目、本地阶段，还是某个模块
- **AND** 它为裁剪决策记录输入、工具与技术、输出
- **AND** 它定义当风险、不确定性、耦合、采用、发布影响或干系人影响增长时的升级触发条件

### Requirement: Fresh source reading evidence for lifecycle refreshes

凡是声称使用 Business Management 或 PMP/PMI evidence 刷新的 lifecycle、whitepaper、research 与 North Star 文档，在更新 tracked conclusions 前 SHALL 记录 fresh extraction run。

#### Scenario: PDF source is included
- **WHEN** local PDF source 属于 refresh 范围
- **THEN** extraction evidence 逐页记录 status row
- **AND** 记录每个 page 或 file fallback 使用 `pypdf` 还是 PyMuPDF/fitz

#### Scenario: EPUB source is included
- **WHEN** local EPUB source 属于 refresh 范围
- **THEN** extraction evidence 按 spine item 记录 status row
- **AND** 显式记录 skipped navigation 或 non-content items

#### Scenario: Markdown source is included
- **WHEN** local Markdown source 属于 refresh 范围
- **THEN** extraction evidence 记录 full-document reading status、hash、modified time 与 character count

### Requirement: Whitepaper and research relationship preservation

Codex durable-team whitepaper 与 solo-maintainable production persistent team research note SHALL 保持分离，除非后续 governed change 证明其中一个不再有独立 lifecycle role。

#### Scenario: 10-layer and 12-layer models both appear
- **WHEN** tracked documents 同时提到两个模型
- **THEN** 它们把 10-layer model 标识为 runtime/governance research view
- **AND** 把 12-layer model 标识为 product/business lifecycle view
- **AND** 提供 bridge，而不是把两个模型视为矛盾。

### Requirement: PMI tailoring and execution grammar authority

凡是使用 PMI evidence 刷新的 lifecycle、whitepaper、research 与 North Star 文档，SHALL 区分 strategic narrative 与 execution grammar，并显式记录完整架构、整个项目轻量、阶段局部轻量、模块级轻量和混合治理的裁剪规则。

#### Scenario: Execution-facing lifecycle layer is updated
- **WHEN** 某个 lifecycle layer 或 delivery gate 会驱动执行
- **THEN** 接收方文档写明输入、工具与技术、输出
- **AND** 记录受影响范围采用完整架构、整个项目轻量、阶段局部轻量、模块级轻量，还是混合模式

#### Scenario: PMI editions and practice guides are referenced
- **WHEN** 文档引用 PMBOK、Process Groups、Agile、项目集、项目组合或 PMO 来源
- **THEN** 文档说明 primary overlay 与 supplemental role
- **AND** 只有当旧版能提供执行词汇、连续性、翻译澄清或历史比较时才展开旧版
- **AND** 写明 Agile、项目集、项目组合与 PMO 叠加层的进入和退出条件。

### Requirement: Bilingual UTF-8 document integrity

本变更更新的英文与 zh-CN 成对文档 SHALL 保持相同治理决策，并 SHALL NOT 留下 mojibake 或 replacement-marker 新增内容。

#### Scenario: zh-CN document is touched
- **WHEN** zh-CN tracked document 被更新
- **THEN** changed text 是有效 UTF-8 中文或有意保留的技术术语
- **AND** 不保留新增的 three ASCII question marks 或 replacement-character 文本
- **AND** 如果存在成对文档，英文新增治理规则必须有 zh-CN 对应内容。

### Requirement: 生命周期治理必须维护持久化团队证明面

生命周期治理 SHALL 将持久化团队交付矩阵、来源追踪索引和过程组契约注册并保留为一等生命周期证明面。当有来源支撑的持久化团队刷新影响白皮书、研究稿、北极星计划、生命周期地图、实施方案、playbook 或 OpenSpec 规格时，生命周期栈 SHALL 使用这些证明面。

过程组契约 SHALL 作为判断生命周期层级、交付门或发布切片何时需要“输入 / 工具与技术 / 输出”的交接权威。来源追踪索引 SHALL 作为当前来源运行身份以及已跟踪 / 被忽略证据边界的交接权威。

#### Scenario: 生命周期刷新改变面向执行的指导

- **GIVEN** 某次生命周期刷新使用 Business Management 或 PMP 证据，并改变面向执行的持久化团队指导
- **WHEN** 维护者检查该刷新是否受治理
- **THEN** 注册表暴露三组证明面双语文档
- **AND** 生命周期规格要求来源追踪索引标识当前 fresh-reading 运行
- **AND** 生命周期规格要求面向执行的规则在完成前经过过程组契约
- **AND** 生命周期规格保持原始抽取文本和本地缓存日志不进入已跟踪权威
