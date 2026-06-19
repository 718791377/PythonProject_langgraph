## Purpose

????????????????????????? I/T/O ?????? main ??????????

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
