## Purpose

定义稳定契约，用于确定性的受治理双语运营包生成、校验、裁剪、过程组式 I/T/O 覆盖以及本地 main 优先交付。

## Requirements

### Requirement: 运营包 Runtime 生成受治理双语运营包

仓库必须提供确定性的运营包 runtime，为 Codex CLI 个人开发者生产级持久化团队与个人级生产级一人公司运营两套系统生成并校验受治理的双语运营包。

#### Scenario: 生成 Codex 持久化团队运营包

- **GIVEN** Codex 持久化团队来源权威定义 12 层主干、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent、12 本推荐书籍
- **WHEN** 运营包生成器为 Codex 持久化团队运行
- **THEN** 它必须生成保留这些计数的双语运营包文档，并把文档、责任域、Agent、模块和书籍映射到现有权威栈
- **AND** 它不得把一人公司 60 文档运营系统混入 Codex 持久化团队运营包。

#### Scenario: 生成一人公司运营包

- **GIVEN** 一人公司来源权威定义 12 层主干、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍、12 个最小启动文档
- **WHEN** 运营包生成器为一人公司运营包运行
- **THEN** 它必须生成保留这些计数的双语运营包文档，并明确 12 文档最小启动路径
- **AND** 它必须区分最小启动、轻量、混合和完整运营包。

### Requirement: 运营包裁剪规则显式且可检查

运营包必须定义可检查的架构裁剪规则，覆盖完整架构、全项目轻量、阶段局部轻量、模块级轻量和混合架构模式。

#### Scenario: 选择项目架构模式

- **GIVEN** 项目具有风险、周期、外部承诺、合规、收入、发布、durable-state 或多 Agent 属性
- **WHEN** 记录裁剪决策
- **THEN** 决策必须说明为什么所选架构模式不是更重或更轻
- **AND** 必须识别让轻量工作升级到混合或完整架构的触发条件。

### Requirement: 执行层流程使用过程组式输入工具输出

每个涉及执行层面的运营包文档都必须具备过程组式 Inputs、Tools And Techniques 和 Outputs 部分。

#### Scenario: 校验必需生成文档

- **GIVEN** 一个必需生成的运营包文档属于 Stage B 输出
- **WHEN** `tools/check_operations_package_docs.py` 校验运营包
- **THEN** 如果必需英文文档缺少 `Inputs`、`Tools And Techniques` 或 `Outputs`，检查器必须失败
- **AND** 如果必需中文伴随文件缺少 `输入`、`工具与技术` 或 `输出`，检查器必须失败。

### Requirement: 保持两阶段本地 Main 交付

运营包工作必须作为两个串行本地 main 优先包交付。

#### Scenario: Stage A 完成

- **GIVEN** Stage A 只创建方案、OpenSpec 和 registry artifacts
- **WHEN** Stage A 验证通过
- **THEN** Stage A 必须提交并合入本地 `main`，然后 Stage B runtime 实现才能开始。

#### Scenario: Stage B 完成

- **GIVEN** Stage A 已经落入本地 `main`
- **WHEN** Stage B 实现生成文档、runtime、checker、tests 和 registry 更新
- **THEN** Stage B 必须经过验证、提交并合入本地 `main`
- **AND** 除非用户显式授权远端发布，否则仓库必须停在远端发布门。

### Requirement: 正文级运营包生成 Codex 四十八个文档

运营包 runtime 必须把 Codex CLI 个人开发者生产级持久化团队正文层生成为精确的 48 个英文主正文文档和 48 个 zh-CN 伴随正文文档。

#### Scenario: 生成 Codex 正文层

- **GIVEN** 已跟踪的 Codex 持久化团队权威定义 12 层主干、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent 和 12 本推荐书籍
- **WHEN** `tools/generate_operations_package.py --package codex` 以写入模式运行
- **THEN** 它必须在 `docs_bilingual/operations_packages/codex_cli_durable_team/` 下生成 48 个 Codex 英文主正文文档
- **AND** 它必须生成 48 个匹配的 zh-CN 伴随正文文档
- **AND** 48 这个数量必须被视为生成的正文文档数量，而不是登记表行数。

#### Scenario: 检查 Codex 正文层

- **GIVEN** Codex 正文层已经生成
- **WHEN** `tools/check_operations_package_docs.py` 校验仓库
- **THEN** 如果 Codex 正文主文档数量不是 48，它必须失败
- **AND** 如果 Codex 正文伴随文档数量不是 48，它必须失败
- **AND** 如果任何 Codex 正文文档对缺少 `docs_bilingual/docs_registry.yaml` 条目，它必须失败。

### Requirement: 正文级运营包生成一人公司六十个文档

运营包 runtime 必须把个人级生产级一人公司正文层生成为精确的 60 个英文主正文文档和 60 个 zh-CN 伴随正文文档。

#### Scenario: 生成一人公司正文层

- **GIVEN** 已跟踪的一人公司权威定义 12 层主干、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍和 12 个最小启动文档
- **WHEN** `tools/generate_operations_package.py --package one-person-company` 以写入模式运行
- **THEN** 它必须在 `docs_bilingual/operations_packages/one_person_company/` 下生成 60 个一人公司英文主正文文档
- **AND** 它必须生成 60 个匹配的 zh-CN 伴随正文文档
- **AND** 60 这个数量必须被视为生成的正文文档数量，而不是登记表行数。

#### Scenario: 检查一人公司正文层

- **GIVEN** 一人公司正文层已经生成
- **WHEN** `tools/check_operations_package_docs.py` 校验仓库
- **THEN** 如果一人公司正文主文档数量不是 60，它必须失败
- **AND** 如果一人公司正文伴随文档数量不是 60，它必须失败
- **AND** 如果任何一人公司正文文档对缺少 `docs_bilingual/docs_registry.yaml` 条目，它必须失败。

### Requirement: 正文文档使用过程组式输入工具输出

每个生成的正文级运营包文档都必须暴露过程组式执行契约。

#### Scenario: 校验正文文档结构

- **GIVEN** 某个生成正文文档属于 Codex 或一人公司正文层
- **WHEN** 检查器校验该文档
- **THEN** 英文主文档必须按顺序包含 `Inputs`、`Tools And Techniques`、`Outputs`
- **AND** 每个部分都必须有非空内容
- **AND** zh-CN 伴随文档必须按顺序包含本地化的输入、工具与技术、输出部分
- **AND** 每个本地化部分都必须有非空内容。

### Requirement: 正文文档保留裁剪决策

每个生成的正文级运营包文档都必须让架构裁剪显式且可检查。

#### Scenario: 检查裁剪语言

- **GIVEN** 某个生成正文文档属于 Codex 或一人公司正文层
- **WHEN** 检查器校验该文档
- **THEN** 它必须要求五种裁剪模式：完整架构、全项目轻量、阶段局部轻量、模块级轻量、混合架构
- **AND** 它必须要求解释所选或默认模式为什么既不更重也不更轻
- **AND** 它必须要求升级触发器语言。

### Requirement: 正文级 runtime 保持分包隔离与幂等

正文级运营包 runtime 必须保持确定性、分包专属且本地可检查。

#### Scenario: 使用分包写入模式

- **GIVEN** 调用方选择 `--package codex`
- **WHEN** 生成器写入文件
- **THEN** 它只能写入 Codex package 文件
- **AND** 它不得写入一人公司正文文件。

#### Scenario: 检查幂等

- **GIVEN** 生成文件已经是最新状态
- **WHEN** 生成器再次运行写入模式，然后运行检查模式
- **THEN** 第二次写入必须报告没有内容漂移
- **AND** 检查模式必须成功返回。
