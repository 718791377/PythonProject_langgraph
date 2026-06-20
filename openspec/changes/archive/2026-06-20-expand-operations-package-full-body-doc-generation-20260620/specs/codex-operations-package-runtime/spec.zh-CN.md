## ADDED Requirements

### Requirement: 正文级运营包生成 Codex 四十八个文档

运营包 runtime 必须把 Codex CLI 个人开发者生产级持久化团队正文层生成为精确的 48 个英文主正文文档和 48 个 zh-CN 伴随正文文档。

#### Scenario: 生成 Codex 正文层

- **GIVEN** 已跟踪的 Codex 持久化团队权威定义 12 层主干、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent、12 本推荐书籍
- **WHEN** `tools/generate_operations_package.py --package codex` 以写入模式运行
- **THEN** 它必须在 `docs_bilingual/operations_packages/codex_cli_durable_team/` 下生成 48 个 Codex 英文主正文文档
- **AND** 它必须生成 48 个匹配的 zh-CN 伴随正文文档
- **AND** 48 这个数量必须被视为生成的正文文档数量，而不是登记表行数。

#### Scenario: 检查 Codex 正文层

- **GIVEN** Codex 正文层已经生成
- **WHEN** `tools/check_operations_package_docs.py` 校验仓库
- **THEN** 如果 Codex 正文主文档数量不是 48，它必须失败
- **AND** 如果 Codex 正文伴随文件数量不是 48，它必须失败
- **AND** 如果任何 Codex 正文文档对缺少 `docs_bilingual/docs_registry.yaml` 条目，它必须失败。

### Requirement: 正文级运营包生成一人公司六十个文档

运营包 runtime 必须把个人级生产级一人公司正文层生成为精确的 60 个英文主正文文档和 60 个 zh-CN 伴随正文文档。

#### Scenario: 生成一人公司正文层

- **GIVEN** 已跟踪的一人公司权威定义 12 层主干、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍、12 个最小启动文档
- **WHEN** `tools/generate_operations_package.py --package one-person-company` 以写入模式运行
- **THEN** 它必须在 `docs_bilingual/operations_packages/one_person_company/` 下生成 60 个一人公司英文主正文文档
- **AND** 它必须生成 60 个匹配的 zh-CN 伴随正文文档
- **AND** 60 这个数量必须被视为生成的正文文档数量，而不是登记表行数。

#### Scenario: 检查一人公司正文层

- **GIVEN** 一人公司正文层已经生成
- **WHEN** `tools/check_operations_package_docs.py` 校验仓库
- **THEN** 如果一人公司正文主文档数量不是 60，它必须失败
- **AND** 如果一人公司正文伴随文件数量不是 60，它必须失败
- **AND** 如果任何一人公司正文文档对缺少 `docs_bilingual/docs_registry.yaml` 条目，它必须失败。

### Requirement: 正文文档使用过程组式输入工具输出

每个生成的正文级运营包文档都必须暴露过程组式执行契约。

#### Scenario: 校验正文文档结构

- **GIVEN** 一个生成正文文档属于 Codex 或一人公司正文层
- **WHEN** 检查器校验该文档
- **THEN** 英文主文档必须按顺序包含 `Inputs`、`Tools And Techniques`、`Outputs`
- **AND** 每个部分都必须有非空内容
- **AND** zh-CN 伴随文件必须按顺序包含本地化的输入、工具与技术、输出部分
- **AND** 每个本地化部分都必须有非空内容。

### Requirement: 正文文档保留裁剪决策

每个生成的正文级运营包文档都必须让架构裁剪显式且可检查。

#### Scenario: 检查裁剪语言

- **GIVEN** 一个生成正文文档属于 Codex 或一人公司正文层
- **WHEN** 检查器校验该文档
- **THEN** 它必须要求五种裁剪模式：完整架构、全项目轻量、阶段局部轻量、模块级轻量、混合架构
- **AND** 它必须要求解释所选或默认模式为什么不是更重也不是更轻
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
