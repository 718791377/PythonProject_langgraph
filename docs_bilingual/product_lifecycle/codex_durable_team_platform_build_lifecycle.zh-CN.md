# Codex CLI 持久化团队平台建设生命周期

本文适用于在 `D:\PythonProject_langgraph` 中建设 Codex CLI 个人开发者生产级持久化团队平台；这是 Codex 编排源码仓库。本文不描述下游业务项目如何管理自己的产品工作。

完整 0-8 生命周期会保留为平台建设地图。单个 MR、MVP 切片和 OpenSpec change 应按风险裁剪该地图的深度，而不是默认展开每一层。

## Scope

平台建设生命周期覆盖可复用的用户级和仓库级编排能力：

- `subagent` 是 Codex 原生专家委托层；它处理有边界的读取、设计、审查、实现和验证切片。
- `native_omx` 是 worker-centric durable backend lane；它只在计划冻结并且存在两个以上基本独立执行切片后使用。
- `langgraph` 是图式 checkpoint 和 approval-gate backend lane；它只在需要图阶段、checkpoint 恢复、interrupt gate 或 survivor queue 时使用。
- `OpenSpec` 是仓库治理工作流；它记录 durable proposal、design、tasks、stable specs 和 archive。
- `D:\PythonProject_General_2` 是本地项目模板目录；它初始化后续项目，但不把后续项目变成平台实现位置。

## 生命周期裁剪叠加规则

平台建设工作使用三种交付风格：

- 预测式门禁适合需求清晰、回滚风险较高、checker 行为变化、launcher 或 runtime entrypoint 变化，或者需要显式 release evidence 的工作。
- 适应式切片适合需求不清楚，需要 discovery、spike、MVP、operator feedback 或 documentation experiment 后才能冻结设计的工作。
- 混合式交付适合仍需要探索，但最终必须通过 OpenSpec、checker、GitLab pipeline、release、rollback 和 retrospective 门禁的工作。

这条叠加规则不是新的生命周期层级。它是应用在 0-8 平台建设生命周期上的治理视角。

## 平台生命周期深度规则

规划平台变更时使用以下深度：

- 完整 0-8 生命周期：用于北极星更新、大版本 release train 定义、backend-family 决策、persistent-team 架构、原生 Codex 兼容性变化，或者可能影响多个项目的用户级编排策略变化。
- MVP 或 release 切片：保留 0-8 全部层级可见，但只摘要 0、1、2、7 层；重点展开 3、4、5、6、8 层，因为它们定义战略、产品行为、技术契约、交付门禁和学习沉淀。
- 普通 OpenSpec change 或 MR：不重写完整 0-8 文档栈。只记录被修改控制面的输入、工具与技术、输出证据。代码类变更在归档前必须包含技术层和执行层证据。发布类变更必须包含验证、发布、回滚和复盘证据。

平台不应把完整 0-8 文档当作官僚化默认流程。平台应使用完整地图来防止遗漏商业价值、用户影响、原生 Codex 兼容性、发布安全、回滚和长期治理反馈。

## 0. 认知叙事层

问题：为什么个人开发者需要生产级持久化团队？

### 输入

- 单次会话上下文丢失、多会话串台、只靠 prompt 约束导致治理规则失效等重复问题。
- 下游项目对安全接续、浏览器能力、本地模板和可复现发布门禁的需求。
- 操作者对“原生 Codex 保持基础层、oh-my-codex 只做增量层”的期望。

### 工具与技术

- 叙事框架：把生产基础设施和 prompt collection 区分开。
- 失败模式分析：把反复出现的会话、上下文和发布问题转化为持久化平台需求。
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` 是 canonical ASCII 白皮书；它解释为什么单次 chat session 不足以支撑生产工作。canonical ASCII 白皮书是英文主版白皮书。
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` 是 UTF-8 中文对照版；它为中文维护者承载同一论证。

### 输出

- 一份持久叙事，说明这是生产基础设施项目，而不是 prompt collection。
- 明确非目标，包括不替代原生 Codex、不把下游项目变成平台实现仓库。
- 传递给商业层、市场层和战略层的方向候选。

## 1. 商业层

问题：这个平台是否值得长期维护？

### 输入

- 认知叙事层给出的个人开发者持久化基础设施理由。
- 脚本、模板、checker、skills、原生 subagents 和可选 durable backends 的维护成本。
- 上下文丢失、dirty worktree、发布门失败、不安全回滚和跨项目状态泄漏造成的风险成本。

### 工具与技术

- 生产力与风险降低分析：估算持久化接续节省的工作是否大于新增维护成本。
- 成本分析：把平台 tooling 成本和下游业务 runtime 成本分开。
- `docs_bilingual/business/codex_cli_durable_team_brd.md` 是未来 ASCII 商业需求文档；它应该估算生产力提升、维护成本、模型成本和风险降低。
- `docs_bilingual/business/codex_cli_durable_team_brd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一商业决策。

### 输出

- 决定该平台是否值得持续维护 release gates、templates 和本地 tooling。
- 指导发布深度和回滚预期的成本收益假设。
- 传递给战略层和产品层的约束。

## 2. 市场与用户层

问题：哪些开发者工作流需要该平台？

### 输入

- 个人开发者和小团队工作流痛点。
- 下游项目对本地 Git、OpenSpec、浏览器自动化和原生 Codex subagents 的采用需求。
- 应抽象为 reusable capability profiles 的具体 workload examples，而不是一次性业务名称列表。

### 工具与技术

- 用户分层：区分平台维护者、下游项目维护者、操作者和偶发消费者。
- 能力画像：把具体工作抽象为可复用开发能力。
- `docs_bilingual/market/codex_cli_durable_team_mrd.md` 是未来 ASCII 市场需求文档；它应该描述个人开发者和小团队的用户分层、痛点和采用场景。
- `docs_bilingual/market/codex_cli_durable_team_mrd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一市场需求。
- `docs_bilingual/references/codex_business_capability_mapping.md` 是 ASCII 抽象能力映射；它把具体 workload examples 映射到抽象 capability profiles。
- `docs_bilingual/references/codex_business_capability_mapping.zh-CN.md` 是 UTF-8 中文对照版；它承载同一映射。

### 输出

- 稳定的抽象 capability profiles，而不是一次性业务名称列表。
- 传递给北极星 plan 的用户假设和采用假设。
- 传递给产品层和技术层的能力缺口。

## 3. 战略与北极星层

问题：长期目标是什么，如何衡量进展？

### 输入

- 商业层的维护价值判断和成本边界。
- 市场层的工作流分层和 capability profiles。
- 来自原生 Codex 兼容性、用户级 helper、repo-local durable state 和本地模板的技术约束。

### 工具与技术

- 北极星指标设计：聚焦跨会话、跨项目的安全冷启动接续。
- release train 规划：区分 MVP、release 切片和长期 persistent-team 目标。
- backend-family 选择：保持 `subagent`、`native_omx` 和 `langgraph` 为不同控制面。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 是 ASCII 北极星 plan；它定义十层框架、release train 和长期 durable-team 目标。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 是 UTF-8 中文对照版，也是当前同一北极星 plan 的主要讨论面。

### 输出

- 平台投入具有可衡量方向。
- 候选北极星指标：冷启动接续成功率；它表示新 Codex 会话在最少重复用户解释下安全接续项目任务的比例。
- 输入指标：OpenSpec guard 通过率、merge request pipeline 通过率、context-retention reload 事件数、multi-session collision 事件数、rollback 成功率和用户手动重复补充上下文次数。
- 传递给产品层、技术层和执行层的发布范围与优先级约束。

## 4. 产品层

问题：平台应该暴露哪些控制面？

### 输入

- 战略层的 release targets、routing thresholds 和 success metrics。
- 用户对启动恢复、角色路由、状态检查、模板和安全发布的需求。
- 来自原生 Codex、用户级 launcher、MCP scope 和 repo-local state isolation 的技术约束。

### 工具与技术

- 控制面设计：把战略转化为 commands、startup behavior、role routing、state inspection 和 template flows。
- 验收标准设计：把 operator workflows 转化为可检查行为。
- `docs_bilingual/product/codex_cli_durable_team_prd.md` 是未来 ASCII PRD；它应该定义用户可见命令、启动行为、角色路由、状态检查、发布门和模板更新流程。
- `docs_bilingual/product/codex_cli_durable_team_prd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一 PRD。
- `AGENTS.md` 是项目级 Codex 指令面；它告诉 Codex 如何处理本仓库。
- `docs_bilingual/project_startup_summary.md` 是 ASCII 冷启动摘要；它告诉新会话如何恢复上下文。
- `docs_bilingual/project_startup_summary.zh-CN.md` 是 UTF-8 中文冷启动摘要对照版。

### 输出

- 显式的 operator workflows 和 acceptance criteria。
- 原生 Codex 兼容性和增量编排的产品级边界。
- 传递给技术层和执行层的输入。

## 5. 技术层

问题：如何在不破坏原生 Codex 的前提下实现平台？

### 输入

- 产品层的控制面和验收标准。
- 战略层对 native subagents、native_omx 和 LangGraph 的 backend-family 边界。
- 来自 Windows shells、MCP servers、官方 LangGraph runtime、本地模型服务和 Git 仓库的外部约束。

### 工具与技术

- 架构边界设计：分离 user-level runtime、repo-local source、repo-local durable state 和 downstream project state。
- 兼容性设计：在增加 wrapper 或 helper 层前保留原生 Codex 行为。
- checker-backed governance：把安全规则变成脚本控制，而不是只靠 prompt 提醒。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` 是 ASCII MCP 范围策略；它决定哪些 MCP server 属于 Codex direct config、MCP Router 或都不属于。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` 是 UTF-8 中文 MCP 范围策略对照版。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` 是 ASCII LangGraph runtime 策略；它定义官方 LangGraph runtime 应放在哪里。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` 是 UTF-8 中文 LangGraph runtime 策略对照版。
- `tools/langgraph_durable_orchestrator/` 是 repo-local LangGraph 兼容源码目录；它是源代码，不是 durable state。
- `.omx/state/langgraph/` 是 repo-local LangGraph durable state 目录；它不得移动到用户级共享 runtime。

### 输出

- 技术契约和 checker-backed boundaries。
- user-level helpers、repo-local source 和 repo-local durable truth 的 source-of-truth 决策。
- 传递给 OpenSpec changes 和 GitLab-first delivery 的实施约束。

## 6. 执行层

问题：平台变更如何安全交付？

### 输入

- 产品层的 acceptance criteria 和技术层的技术契约。
- OpenSpec proposal、design、tasks、stable specs 和 archive 状态。
- GitLab-first 发布规则和当前 session ownership claims。

### 工具与技术

- OpenSpec change control：记录 proposal、design、tasks、specs 和 archive evidence。
- GitLab-first delivery：使用 feature branches、merge requests、pipelines 和 post-merge GitHub sync。
- 仓库 checker：验证双语文档、名称解释、session claims、安全规则脚本背书和 OpenSpec health。
- `openspec/changes/<change-id>/proposal.md` 是 ASCII OpenSpec 提案；它解释为什么需要某个具体平台变更。
- `openspec/changes/<change-id>/design.md` 是 ASCII OpenSpec 设计；它解释该平台变更如何实现。
- `openspec/changes/<change-id>/tasks.md` 是 ASCII OpenSpec 任务清单；它跟踪该 change 的完成状态。
- `openspec/changes/<change-id>/*.zh-CN.md` 是同一 change artifacts 的 UTF-8 中文对照文件。
- `tools/run_openspec_guard.py` 是 OpenSpec guard 脚本；它验证官方 refresh、仓库规则和 clean-git 预期。

### 输出

- 带显式验证证据的小步 GitLab-first MR。
- 已完成或已归档的 OpenSpec changes，并在需要时同步 stable specs。
- 平台影响类变更的 release、rollback 和 verification evidence。

## 7. 增长与采用层

问题：平台如何扩展到多个项目，同时不共享 repo-local truth？

### 输入

- 执行层输出的 releases、templates、helper scripts 和 operator guidance。
- 下游项目对本地 Git、OpenSpec、原生 subagents、浏览器能力和不共享 repo-local truth 的需求。
- 已初始化项目返回的模板反馈。

### 工具与技术

- 模板打包：区分 new-PC bootstrap files、reusable project files 和 project-local generated state。
- 采用分析：追踪哪些能力跨项目复用，同时不合并 durable state。
- 模板更新策略：定义已初始化项目如何接收后续改进。
- `D:\PythonProject_General_2\START_HERE.cmd` 是 Windows 双击模板启动器；它初始化或检查本地项目。
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` 是模板清单；它解释哪些文件属于本地项目模板。
- `docs_bilingual/templates/template_update_policy.md` 是未来 ASCII 模板更新策略；它应解释已初始化项目如何接收后续模板更新。
- `docs_bilingual/templates/template_update_policy.zh-CN.md` 是未来 UTF-8 中文模板更新策略对照版。

### 输出

- 下游项目可以采用平台，但不会变成平台实现仓库。
- 模板更新规则和 adoption reports。
- 当采用摩擦出现时，向战略层、产品层和技术层反馈。

## 8. 复盘与学习层

问题：哪些平台经验应该变成规则、checker 或模板？

### 输入

- 执行层的 validation results、release outcomes、rollback outcomes 和 incidents。
- 增长层的 adoption reports 和 downstream feedback。
- 真实工作中观察到的 session-collision、context-loss、MCP noise、wrapper 和 toolchain failures。

### 工具与技术

- 复盘分析：把重复失败转化为治理规则。
- checker 设计：把规则变成脚本控制，使新会话不只依赖 prompt memory。
- archive 和 memory updates：在重大变更后捕获 durable context。
- `docs_bilingual/memory/mainline_memory_summary.md` 是 ASCII 主线记忆摘要；它在重大变更后捕获 durable context。
- `docs_bilingual/memory/mainline_memory_summary.zh-CN.md` 是 UTF-8 中文记忆摘要对照版。
- `docs_bilingual/governance/` 是治理目录；它保存应该跨越单次对话长期有效的规则。
- `tools/check_*.py` 脚本是 checker 文件；它们在不只依赖 prompt 的情况下执行治理规则。

### 输出

- 重复失败被沉淀为脚本、policy、OpenSpec specs 或模板更新。
- 面向未来 release slicing 和 routing policy 的 lessons learned。
- 必要时更新 startup summaries、governance documents 和 checkers。

## Release Slicing Rule

一个平台 MR 通常只应该修改一个层级或一个控制面。好的例子包括：新增一份 lifecycle reference、新增一个 checker、归档一个 OpenSpec change、细化一个 release gate 或更新一条模板规则。
