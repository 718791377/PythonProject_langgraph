## 上下文

本地读取审计已经从本地私有 `PMP/` 参考树中抽取了 7 份 PDF 和 12 个主 HTML 页面。审计确认 PMBOK 第8版 PDF、英文 Process Groups 指南和英文 Agile Practice Guide 是最可靠的来源。若干中文 PDF 抽取存在 OCR 或编码噪声，只适合做结构级参考。

仓库不应复制 PMI 正文，而应把可用结构转化为仓库自己的治理语言。

## 目标 / 非目标

目标：

- 将 PMBOK 第8版作为价值交付、项目画布、绩效域、AI 时代项目治理和裁剪的主要叠加层。
- 将 PMBOK 第6版和 Process Groups 作为启动、规划、执行、监控、收尾，以及输入/工具/输出纪律的操作补充。
- 将 PMBOK 第7版作为原则、绩效域、价值交付和裁剪的桥接层。
- 将 Agile guidance 作为 MVP slices、feedback loops 和小 MR releases 的适应式/混合式交付补充。
- 保持平台建设生命周期与下游项目消费生命周期分离。
- 新增轻量 Codex 平台项目画布，但不要求每个小变更都展开完整生命周期。

非目标：

- 不把 PMI 书籍正文复制进仓库。
- 不把仓库改成传统 PMP 模板仓库。
- 不修改 runtime launchers、MCP configuration、Codex wrappers、`native_omx` 或 `langgraph` 行为。
- 不宣称长期持久化团队 draft 已经实现。
- 不把低文本或 OCR 污染的抽取结果当作精确引用来源。

## 决策

### 决策 1：将 PMBOK 第8版作为主要叠加层，而不是替代生命周期

仓库会把 PMBOK 第8版描述为价值交付和项目治理的主要叠加层，但不替代既有白皮书、MRD、北极星 Plan、PRD、技术设计、implementation plan、OpenSpec 或 checker 结构。

原因：

- 既有 0-8 生命周期已经与本仓库文档模型对齐。
- PMBOK 第8版提供的价值交付和项目画布语言可以增强生命周期，但不需要替代它。

### 决策 2：将 Project Canvas 作为轻量对齐工件

新增 Codex 平台项目画布，作为一页式对齐文档。它位于 startup summary 和长 implementation plans 之间。

原因：

- 冷启动读者需要快速理解 purpose、value、boundaries、stakeholders、risks、delivery style 和 outcomes。
- 画布能降低维护者在 initiative 尚未成熟时就展开全量生命周期文档的概率。

### 决策 3：保留过程组思维作为执行支撑

Process Groups 和 PMBOK 第6版会映射到 OpenSpec 与 GitLab-first 交付门禁，但只作为执行支撑模型。

原因：

- 过程组模型对输入/工具/输出纪律和 closeout gates 很有价值。
- 它不应覆盖 PMBOK 第8版的价值交付叙事，也不应覆盖仓库 OpenSpec 工作流。

### 决策 4：将 tailoring 作为治理系统决策

裁剪覆盖治理深度、文档深度、角色协作深度、验证深度、发布证据、回滚证据和复盘深度。

原因：

- 本仓库经常处理小型只读审查、中型文档变更、runtime hardening 和跨项目 durable-state 工作。
- 这些任务需要不同治理深度，而不是一套强制文档栈。

### 决策 5：显式保留 AI 时代责任边界

白皮书和平台生命周期会说明：AI 可以加速 research、drafting、candidate planning、state summarization 和 verification support，但 human operator 与 main leader session 仍负责 value judgment、risk trade-offs、approvals 和 release responsibility。

原因：

- 这符合仓库规则：native Codex 保持基础层，自动 durable teams 必须满足阈值和 consent。
- 这能防止 hidden automation 被误认为治理本身。

## 风险 / 权衡

- 风险：更新内容变成宽泛 PMI 摘要。缓解：所有新增内容都保持仓库特定映射，不复制 PMI 正文。
- 风险：项目画布被误解成强制文档。缓解：文档中说明它是轻量工件，小变更可选。
- 风险：更多生命周期语言被误读成 runtime 已成熟。缓解：持久化团队实施方案继续保持 draft，并说明本变更不实现 runtime features。

## 迁移计划

1. 创建本次文档对齐的 OpenSpec proposal、design、spec 和 tasks。
2. 更新 PMI reference map 和 product lifecycle 文档。
3. 新增 Codex platform project canvas 双语文件。
4. 用价值交付和 release-slice 语言更新 white paper 与 durable-team plan。
5. 运行 OpenSpec 和文档治理检查。
6. 本地提交并在发布到 GitLab 前请求发布确认。

## 开放问题

- 后续是否要把 performance-domain outcome checks 转成 checker-backed templates。
- 下游项目模板是否默认包含空白 adoption canvas，还是只把它记录为可选工件。
