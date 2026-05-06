# 后续项目消费平台能力生命周期

本文描述后续项目如何消费 Codex CLI 持久化团队平台。下游项目可以使用用户级 runtime、原生 Codex subagents、模板、治理思想和可选 durable lanes，但它拥有自己的仓库事实和业务工作。

## Non-Negotiable Boundary

`D:\PythonProject_langgraph` 是平台源码仓库；它拥有 Codex 编排线、模板、共享策略和 helper source。

下游项目拥有自己的产品范围、商业文档、OpenSpec tree、Git 历史、durable state、release state 和本地 lessons learned。下游项目不得把平台仓库当成自己的 repo-local durable truth。

## 下游生命周期裁剪叠加规则

下游项目应把通用 0-8 生命周期当作地图，而不是每个变更都必须填写的强制表格。

- 预测式门禁适合范围清楚、存在发布风险、影响金钱/用户/信任、涉及合规，或需要显式 rollback 的下游工作。
- 适应式切片适合需要探索、原型、浏览器验证、用户反馈或小型 MVP 后才能冻结设计的下游工作。
- 混合式交付适合仍需要 discovery，但最终必须通过本地 OpenSpec、tests、release、rollback 和 retrospective checks 的下游工作。

## 下游生命周期深度规则

下游项目使用以下深度：

- 完整 0-8 生命周期：用于新产品、重大业务转向、用户可见发布、合规敏感变更、支付或信任影响工作，或者长期平台化的下游系统。
- 项目 MVP 或 release 切片：保留 0-8 全部层级可见；风险较低时摘要 0、1、2、7 层，重点展开 3、4、5、6、8 层，用于战略、产品行为、技术安全、交付和学习。
- 普通本地变更：不重写完整文档栈。只记录被修改范围的输入、工具与技术、输出证据。代码类变更需要技术层和执行层证据。发布类变更需要验证、发布、回滚和复盘证据。

下游项目可以轻量，但必须保持 repo-local：它的 OpenSpec artifacts、`.omx/state/` 状态目录、release facts 和 lessons learned 都属于该项目。

## 下游采用画布

下游项目可以先使用 `adoption_canvas.md` 作为轻量 adoption canvas，然后再深入采用平台能力。adoption canvas 用来说明项目为什么需要平台帮助，以及如何衡量成功。

推荐字段：

- local project purpose 和 current friction；
- 正在采用的 platform capability；
- expected value outcome，例如减少 startup friction、减少 context loss、更安全 release flow 或更好的 browser verification；
- 不得移动到平台仓库的 repo-local boundaries；
- validation path 和 rollback path；
- 应作为 upstream improvement candidates 回传给平台的 feedback。

## 消费项目价值反馈

下游成功不只是安装成功或复制模板成功。下游项目应记录平台 adoption 是否改善了自己的交付结果，同时是否保留 repo-local truth。

反馈在 upstream 前应先分类：

- Local-only lesson：留在下游仓库。
- Reusable platform lesson：成为 upstream feedback，并且只有通过平台 OpenSpec change 才能进入本平台。
- Runtime defect：只有能在单一下游项目之外复现时，才成为平台 bug 或 hardening candidate。

## 0. 认知叙事层

问题：这个下游项目为什么存在，为什么要使用平台能力？

### 输入

- 项目想法、目标问题、本地仓库上下文，以及用户或操作者意图。
- 平台启动规则、本地项目模板文件和原生 Codex subagent 可用性。
- 外部约束，例如只使用本地 Git、IDE 选择、浏览器需求、隐私和预算。

### 工具与技术

- 项目叙事框架：解释项目目的，但不把项目变成平台实现工作。
- 冷启动摘要设计：帮助新的 Codex 会话恢复本地项目上下文。
- `README.md` 是项目总览；它解释这个项目是什么以及如何开始。
- `docs_bilingual/project_startup_summary.md` 是 ASCII 冷启动摘要；它帮助新的 Codex 会话理解项目。
- `docs_bilingual/project_startup_summary.zh-CN.md` 是同一启动摘要的 UTF-8 中文对照版。

### 输出

- 清晰的本地项目叙事和启动面。
- 项目自己的非目标和边界。
- 传递给商业层、市场层和战略层的输入。

## 1. 商业层

问题：这个下游项目是否值得做或继续做？

### 输入

- 认知层的项目目的和本地问题陈述。
- 用户价值、商业价值、时间预算、工具预算、模型预算和维护成本。
- 平台采用成本，包括模板更新和可选 durable-lane 复杂度。

### 工具与技术

- 商业价值分析：估算收入、成本节省、生产力提升或风险降低。
- 范围成本权衡：决定平台能力应该轻量使用还是深入使用。
- `docs_bilingual/business/brd.md` 是项目 BRD；它解释该项目的商业价值、成本、用户价值和回报预期。
- `docs_bilingual/business/brd.zh-CN.md` 是项目 BRD 的 UTF-8 中文对照版。

### 输出

- 项目 BRD、投资边界和继续/停止决策。
- 传递给项目战略和发布深度的成本价值假设。
- 关于本地 Git、OpenSpec 和原生 subagents 是否足够，或者是否需要可选 durable lanes 的决策。

## 2. 市场与用户层

问题：谁需要这个项目，在什么场景下需要？

### 输入

- 商业层的目标价值和约束。
- 用户访谈、观察、客服反馈、浏览器验证、使用数据或领域证据。
- 平台提供的能力分类，用于归类开发工作，而不是把一次性业务名称写成平台需求。

### 工具与技术

- 用户分层：区分目标用户、操作者、维护者、付费者和干系人。
- 场景分析：映射用户任务、约束和痛点。
- 反馈循环：使用原型、浏览器检查或小型 MVP 降低不确定性。
- `docs_bilingual/market/mrd.md` 是项目 MRD；它解释目标用户、使用场景、痛点和替代方案。
- `docs_bilingual/market/mrd.zh-CN.md` 是项目 MRD 的 UTF-8 中文对照版。
- `docs_bilingual/user_research/` 是用户研究目录；它可以保存访谈、观察和反馈证据。

### 输出

- 项目 MRD、目标用户、目标场景和优先级信号。
- 面向产品需求和战略的用户证据。
- 关于平台模板是否缺少可复用能力的反馈。

## 3. 战略与北极星层

问题：下游项目如何定义成功？

### 输入

- 商业层的成功标准和成本边界。
- 市场层的用户分层、场景和需求证据。
- 平台边界：把项目本地事实和共享平台 runtime 分开。

### 工具与技术

- 北极星指标设计：定义项目的主成功指标。
- 输入指标拆解：识别驱动项目北极星指标的前置指标。
- 交付深度裁剪：决定项目当前阶段需要完整 0-8、MVP/release 深度，还是小型本地变更路径。
- `docs_bilingual/north_star_plan.md` 是项目北极星 Plan；它定义该项目的主成功指标、输入指标和杠杆。
- `docs_bilingual/north_star_plan.zh-CN.md` 是同一计划的 UTF-8 中文对照版。

### 输出

- 项目北极星 Plan、输入指标、杠杆和非目标。
- 当前项目阶段的交付深度决策。
- 传递给产品层、技术层和执行层的优先级约束。

## 4. 产品层

问题：下游项目应该构建或修改什么？

### 输入

- 战略层的优先级、北极星指标、非目标和阶段边界。
- 市场层的用户场景和痛点。
- 技术层的可行性、依赖和安全约束。

### 工具与技术

- PRD 写作：把战略和用户证据转化为范围、流程、优先级和验收标准。
- 用户旅程映射：描述端到端体验。
- 原型和浏览器验证：检查预期行为是否容易理解。
- `docs_bilingual/prd.md` 是项目 PRD；它定义用户故事、功能、优先级、流程和验收标准。
- `docs_bilingual/prd.zh-CN.md` 是项目 PRD 的 UTF-8 中文对照版。
- `docs_bilingual/user_journey.md` 是用户旅程；它展示用户端到端路径。
- `docs_bilingual/user_journey.zh-CN.md` 是用户旅程的 UTF-8 中文对照版。

### 输出

- 项目 PRD、用户旅程、功能范围、验收标准和 out-of-scope list。
- 面向技术设计和执行计划的产品证据。
- 当期望范围超过所选交付深度时，向战略层反馈。

## 5. 技术层

问题：如何安全实现下游项目，同时不混淆平台 tooling 和业务 runtime？

### 输入

- 产品层的范围、验收标准和用户流程。
- 项目本地源码、测试、依赖、部署约束和数据约束。
- 平台提供的原生 Codex subagents、OpenSpec、可选 durable lanes 和本地模板检查指导。

### 工具与技术

- 技术设计：分离项目 business runtime 和 Codex platform tooling。
- 依赖分类：判断某个 package 属于项目业务 runtime，还是只属于 Codex tooling。
- 架构和 API 设计：定义模块、数据、接口、信任边界和兼容性。
- `docs_bilingual/technical/trd.md` 是项目技术设计；它解释技术选择、架构和权衡。
- `docs_bilingual/technical/trd.zh-CN.md` 是技术设计的 UTF-8 中文对照版。
- `docs_bilingual/technical/api_spec.md` 是项目 API 规格；当存在 API 时，它定义接口输入、输出、错误和权限。
- `docs_bilingual/technical/api_spec.zh-CN.md` 是 API 规格的 UTF-8 中文对照版。
- `src/` 是项目源码目录；它包含该项目拥有的业务或应用代码。
- `tests/` 是项目测试目录；它包含该项目拥有的测试。
- Codex 平台 `PySide6` 是 Codex tooling 的本地 GUI 控制中心依赖。下游项目 `PySide6` 依赖只有在该项目声明并拥有时，才是 business runtime dependency。
- 同样分离适用于 `SQLite`、`Redis`、`promptfoo` 和 `jina-embeddings`；不能因为平台使用它们，就自动把它们变成业务依赖。

### 输出

- 项目技术设计、API 规格、依赖分类和测试边界。
- 证明平台 tooling 没有污染业务 runtime dependencies 的证据。
- 面向本地 OpenSpec changes 和 Codex subagent tasks 的实施约束。

## 6. 执行层

问题：下游项目如何安全交付变更？

### 输入

- 产品层的范围和验收标准。
- 技术层的设计、依赖分类和测试要求。
- 项目本地 OpenSpec tree、Git 状态、分支策略和发布预期。

### 工具与技术

- 本地 OpenSpec change control：记录为什么需要项目变更、如何设计、哪些任务完成它。
- 原生 Codex subagents：在当前 Codex 会话内处理有边界的专家工作。
- 可选 durable lanes：只有项目条件满足阈值时才选择。
- `openspec/config.yaml` 是项目 OpenSpec 配置；它把 OpenSpec workflow 绑定到本仓库。
- `openspec/changes/<change-id>/proposal.md` 是项目本地 OpenSpec proposal；它解释为什么需要某个项目变更。
- `openspec/changes/<change-id>/design.md` 是项目本地 OpenSpec design；它解释该项目变更如何实现。
- `openspec/changes/<change-id>/tasks.md` 是项目本地 OpenSpec task list；它跟踪项目工作。
- `openspec/changes/<change-id>/*.zh-CN.md` 是同一项目 change artifacts 的 UTF-8 中文对照文件。
- 使用原生 `subagent` 处理当前 Codex 会话内有边界的专家工作。
- 只有当项目存在已冻结计划并且有两个以上基本独立执行切片时，才使用 `native_omx`。
- 只有当项目需要 graph phases、checkpoint recovery、approval gates 或 survivor queues 时，才使用 `langgraph`。

### 输出

- 已实现并已验证的项目变更。
- 本地 OpenSpec evidence、test evidence 和 Git evidence。
- 可发布产物，或者明确说明停止、修订或回滚的理由。

## 7. 发布、增长与采用层

问题：下游项目如何发布、被采用并持续改进？

### 输入

- 执行层的可发布产物、验证证据和已知风险。
- 战略层的成功指标和增长杠杆。
- 用户反馈、采用摩擦和部署约束。

### 工具与技术

- 发布计划：定义 rollout、release gates、沟通和 rollback readiness。
- 指标追踪：衡量项目成功和质量。
- 变更日志和采用报告：记录用户可见或 operator 可见的变化。
- `docs_bilingual/release_plan.md` 是发布计划；它定义 rollout、release gates 和沟通方式。
- `docs_bilingual/release_plan.zh-CN.md` 是发布计划的 UTF-8 中文对照版。
- `docs_bilingual/rollback_plan.md` 是回滚计划；它定义如何回到安全版本。
- `docs_bilingual/rollback_plan.zh-CN.md` 是回滚计划的 UTF-8 中文对照版。
- `CHANGELOG.md` 是项目变更日志；它记录用户可见和 operator 可见的变化。
- `docs_bilingual/metrics.md` 是指标文档；它定义项目成功和质量指标。
- `docs_bilingual/metrics.zh-CN.md` 是指标文档的 UTF-8 中文对照版。

### 输出

- 已发布项目版本、changelog、rollback evidence 和 metrics evidence。
- 面向下一轮项目迭代的采用或增长发现。
- 当用户可见行为变化时，向产品层和战略层反馈。

## 8. 复盘与上游反馈层

问题：下游项目学到了什么，哪些经验应该反馈给上游平台？

### 输入

- 执行层的交付记录、测试结果、缺陷和发布结果。
- 发布层的指标、采用报告、回滚结果和用户反馈。
- 在模板、启动摘要、Codex subagent 使用或可选 durable-lane 规则中观察到的缺口。

### 工具与技术

- 复盘分析：把项目经验转化为本地可复用 lessons。
- 上游反馈：把平台改进想法和项目本地事实分开。
- 归档纪律：保持项目 OpenSpec、durable state 和 release state 属于该项目本地。
- `docs_bilingual/lessons_learned.md` 是项目经验教训文档；它记录本地可复用经验。
- `docs_bilingual/lessons_learned.zh-CN.md` 是经验教训文档的 UTF-8 中文对照版。
- `docs_bilingual/upstream_feedback.md` 是平台反馈文档；它记录可能改进 `D:\PythonProject_langgraph` 的经验。
- `docs_bilingual/upstream_feedback.zh-CN.md` 是平台反馈文档的 UTF-8 中文对照版。

### 输出

- 本地 lessons learned、upstream feedback candidates 和 follow-up tasks。
- 项目本地事实和平台改进请求之间的清晰分离。
- 面向未来模板更新、治理更新或项目迭代的输入。

## Minimal Downstream Project Checklist

小型下游项目可以从最小本地界面开始：

- `AGENTS.md` 作为项目级 Codex 指令文件。
- `docs_bilingual/project_startup_summary.md` 作为 ASCII 冷启动摘要。
- `docs_bilingual/project_startup_summary.zh-CN.md` 作为 UTF-8 中文冷启动摘要对照版。
- `openspec/` 作为项目本地 OpenSpec 治理树。
- `.omx/state/` 作为项目本地 durable state 目录；仅在使用 durable lanes 时需要。
- `.gitignore` 作为项目忽略文件；它用于忽略缓存、状态、生成产物和本地密钥。
