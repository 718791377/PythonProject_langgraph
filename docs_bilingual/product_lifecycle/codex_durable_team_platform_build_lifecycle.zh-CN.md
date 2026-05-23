# Codex CLI 持久化团队平台建设生命周期

本文适用于在 `D:\PythonProject_langgraph` 中建设 Codex CLI 个人开发者生产级持久化团队平台；这是 Codex 编排源码仓库。本文不描述下游业务项目如何管理自己的产品工作。

完整 0-11 / 12 层生命周期是权威平台地图：认知、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营、复盘。单个 MR、MVP 切片和 OpenSpec change 应按风险裁剪该地图的深度，而不是默认展开每一层。

本平台生命周期使用 `business_management_source_synthesis.zh-CN.md` 作为源库叠加层。它强化 Codex 平台是一套一人 operating system：先诊断再构建、让机制保持小、执行前先塑形、衡量结果、保护架构和信任边界、显式定义人和 Agent 的 ownership、保持运营可支持，并把重复经验转化为 checker 或模板。

## Scope

平台建设生命周期覆盖可复用的用户级和仓库级编排能力：

- `subagent` 是 Codex 原生专家委托层；它处理有边界的读取、设计、审查、实现和验证切片。
- `native_omx` 是 worker-centric durable backend lane；它只在计划冻结并且存在两个以上基本独立执行切片后使用。
- `langgraph` 是图式 checkpoint 和 approval-gate backend lane；它只在需要图阶段、checkpoint 恢复、interrupt gate 或 survivor queue 时使用。
- `OpenSpec` 是仓库治理工作流；它记录 durable proposal、design、tasks、stable specs 和 archive。
- `D:\PythonProject_General` 是本地项目模板目录；它初始化后续项目，但不把后续项目变成平台实现位置。
- `D:\PythonProject_General_2` 是其他未开发 OMX、LangGraph 功能和 Codex 环境的新电脑用的项目模板目录；它初始化后续项目，但不把后续项目变成平台实现位置，保留接口兼容后续升级到 OMX、LangGraph 以及 Codex CLI 个人开发者生产级持久化团队平台的可能。

## 生命周期裁剪叠加规则

平台建设工作使用三种交付风格：

- 预测式门禁适合需求清晰、回滚风险较高、checker 行为变化、launcher 或 runtime entrypoint 变化，或者需要显式 release evidence 的工作。
- 适应式切片适合需求不清楚，需要 discovery、spike、MVP、operator feedback 或 documentation experiment 后才能冻结设计的工作。
- 混合式交付适合仍需要探索，但最终必须通过 OpenSpec、checker、local-main-first publication、release、rollback 和 retrospective 门禁的工作。

这条叠加规则不是新的生命周期层级。它是应用在 0-11 平台建设生命周期上的治理视角。

## 平台价值结果

平台工作必须跟踪 value outcomes，而不只是交付文件。平台真正成功，是在保持 native Codex compatibility 和 repo-local truth 的同时，降低 operator friction。

平台 release slices 应使用以下 outcome checks：

- Operator friction reduction：operator 能比以前更快理解 status、next action 和 rollback path。
- Cold-start continuation success：新会话可以从 startup summaries、OpenSpec 和 project files 恢复必要上下文。
- Cross-session coordination quality：并发会话能识别 ownership 并避免 path collisions。
- Repo-local state safety：每个项目保留自己的 durable truth 和 release facts。
- Native Codex compatibility：原生 Codex raw path 仍可用、可恢复。
- Rollback evidence：影响 launchers、wrappers 或 runtime behavior 的 release slices 必须有已知安全回滚路径。

## AI 时代角色边界

AI 可以加速 research、draft generation、candidate planning、state summarization 和 verification support。AI 不得变成隐藏 approval authority。

human operator 和 current main Codex leader session 继续负责 value judgment、risk trade-offs、approval gates、release timing 和 rollback decisions。durable lanes 和 automation 是执行辅助，必须保持 inspectable 且受 consent boundary 约束。

## 平台生命周期深度规则

规划平台变更时使用以下深度：

- 完整 0-11 生命周期：用于 white paper 或 thesis 更新、business-model 决策、MRD 更新、战略变化、指标契约、PRD/control-surface 变化、架构决策、组织或 Agent 治理变化、交付系统变化、采用/模板变化、支持/运营变化，或者可能影响多个项目的复盘驱动治理更新。
- MVP 或 release 切片：保留 12 层全部可见，但只展开风险触达的层级。代码类平台切片通常展开战略、指标、产品、技术、组织、执行、运营和复盘证据；模板或采用切片还要展开增长证据。
- 普通 OpenSpec change 或 MR：不重写完整 12 层文档栈。只记录被修改控制面的输入、工具与技术、输出证据。代码类变更在归档前必须包含技术层、组织层、执行层、运营层和复盘证据。发布类变更必须包含验证、发布、回滚、支持和学习证据。

平台不应把完整生命周期文档当作官僚化默认流程。平台应使用完整地图来防止遗漏商业价值、用户影响、可衡量结果、原生 Codex 兼容性、ownership 边界、发布安全、运营可支持性、回滚和长期治理反馈。

在把平台变更分类为轻量之前，先使用 `lifecycle_tailoring_rules.zh-CN.md`。对本仓库而言，凡是影响可复用编排行为、原生 subagent 路由、`native_omx`、LangGraph、worktree safety、OpenSpec governance、user-level launcher policy、skill/profile governance、local-main-first publication 或 shared templates 的变更，都需要对受影响范围采用完整架构。只有不改变 runtime entrypoints、durable state、secrets、CI gates、release gates 或下游项目依赖的有边界纯文档 appendix 或本地 helper，才可以作为模块级轻量处理。

## Codex 目标清单规则

Codex CLI 平台目标固定为：

- 12 层主干：认知叙事、商业、市场、战略、指标、产品、技术、组织、执行、增长、运营、复盘。
- 4 个虚拟部门：Strategy & Product Office；Engineering & Platform Office；Agent Governance Office；Growth & Knowledge Office。
- 24 个责任域：CEO/战略、Chief of Staff、商业模式、财务、市场情报、客户研究、产品战略、PM/PRD、CLI/UX、指标、架构、工程管理、代码质量、DevOps、平台/工具链、安全、隐私/数据保护、数据治理、Agent 治理、Agent 评估、文档、支持、品牌/信任、知识/复盘。
- 18 个横切模块：财务、运营、工程管理、组织设计、法务合规、安全、知识管理、风险管理、个人产能、AI Agent 治理、数据治理、品牌信任、工具链治理、SLA 治理、资产/IP 治理、用户研究治理、渠道治理、退出治理。
- 48 个核心文档：覆盖战略/商业、市场/产品、指标/数据、工程/平台、安全/风险、Agent 治理、增长/运营、复盘/知识。
- 12 个受治理 AI Agent：Research、PM、Architect、Code、Review、Test、Security、DevOps、Data、Docs、Ops、Risk。
- 12 本推荐书籍：Scaling People、Working Backwards、High Output Management、INSPIRED、Product Operations、Team Topologies、Accelerate、Shape Up、Lean Analytics、Designing Data-Intensive Applications、Secure by Design、The Staff Engineer's Path。

任何非平凡的平台发布切片，都必须说明它触及哪一层、哪个虚拟部门、哪个责任域、哪个横切模块、哪个核心文档以及哪个受治理 Agent 边界。若切片改变执行行为，还必须为受影响 gate 写明输入、工具与技术、输出。


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
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md` 是当前 MRD；它描述个人开发者和下游项目的目标用户、能力画像、运行归属边界与采用/风险场景。
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.zh-CN.md` 是当前 MRD 的中文对照版。
- 抽象能力映射现在位于 MRD 附录 A，不再使用单独 reference 文件。
- 中文能力映射同样位于中文 MRD 附录 A。

### 输出

- 稳定的抽象 capability profiles，而不是一次性业务名称列表。
- 输出给战略层和指标层的用户与采用假设。
- 输出给战略、指标、产品、技术、组织和运营层的能力缺口。

## 3. 战略层

问题：长期目标是什么，哪些事情要明确拒绝？

### 输入

- 商业层输出的平台维护价值和成本边界。
- 市场层输出的工作流分群和能力 profile。
- 来自 native Codex 兼容性、user-level helpers、repo-local durable state 和本地模板的技术约束。
- 真实平台事故带来的运营和复盘反馈。

### 工具与技术

- Strategy kernel 分析：记录平台诊断、指导方针、连贯行动和明确非目标。
- Release train planning：区分 MVP、release slice 和长期 persistent-team 目标。
- Backend-family selection：保持 `subagent`、`native_omx` 和 `langgraph` 是彼此不同的控制面。
- Kill criteria 设计：定义 helper、template、skill profile、durable lane 或 automation path 何时暂停或退役。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 是 ASCII 北极星草案；它是长期目标，不是运行时已实现证明。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 是该草案的 UTF-8 中文伴随文档和当前主要讨论表面。

### 输出

- 面向 durable team 投资的平台战略方向。
- 明确取舍、非目标和 backend-family selection 规则。
- 输出给指标、产品、技术、组织、执行、增长、运营和复盘层的 release 范围与优先级约束。

## 4. 指标层

问题：如何衡量平台进展？

### 输入

- 战略层输出的目标、非目标和发布优先级。
- 商业层输出的成本与收益假设。
- 市场层输出的采用假设和能力缺口。
- 之前 release 的执行、运营和复盘证据。

### 工具与技术

- 北极星指标设计：聚焦跨会话、跨项目的安全冷启动续接。
- OKR 与输入指标设计：跟踪摩擦降低、恢复成功、发布安全和回滚信心。
- 护栏指标设计：保护 native Codex 兼容性、repo-local durable truth、provider pacing budget、operator attention 和 CI minutes。
- Tracking plan 设计：定义 local gate、MR review、release evidence、incident 和 context-retention reload 的计数方式。

### 输出

- 候选北极星指标：cold-start continuation success rate，即新 Codex 会话能以最少重复解释安全恢复项目任务的比例。
- 输入指标：OpenSpec guard 通过率、local gate 通过率、local MR review 通过率、需要时的 remote pipeline 通过率、context-retention reload incident、多会话冲突 incident、rollback success rate 和 manual context-restatement count。
- 成本、skill-context 噪声、状态泄漏、native Codex 回归、hidden automation 和未授权 durable-lane launch 的护栏。
- 可触发继续、暂停、细化、回滚或退役决策的阈值。

## 5. 产品层

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

## 6. 技术层

问题：如何在不破坏原生 Codex 的前提下实现平台？

### 输入

- 产品层的控制面和验收标准。
- 战略层对 native subagents、native_omx 和 LangGraph 的 backend-family 边界。
- 组织层输出的 ownership 和 approval constraints。
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
- 传递给 OpenSpec changes 和 local-main-first delivery 的实施约束。


## 7. 组织层

问题：平台里的每项责任、决策和批准由谁或什么机制承担？

### 输入

- 战略、指标、产品范围、技术边界和运营约束。
- human operator authority、current main Codex leader responsibility、native subagent roles、可选 durable-worker roles 和外部工具边界。
- Session ownership claims、worktree isolation evidence 和 approval requirements。

### 工具与技术

- Role-map design：区分 human operator、当前主 Codex leader session、native expert subagents、durable workers 和 external reviewers。
- Agent-governance design：定义哪些 agent 可以读取、写入、提议、审查、测试、部署，或必须请求批准。
- Durable-team threshold design：防止计划未冻结、独立执行切片不足时自动启动 durable team。
- Responsibility matrix：把 release decision、rollback decision、state mutation、remote publication 和 mirror sync 映射到明确 owner。
- Session-ownership checks：防止多个会话在未协调时写同一路径。

### 输出

- Agent governance、role map、responsibility matrix、launch thresholds 和 approval boundaries。
- 输出给执行、运营和复盘层的 ownership 约束。
- 明确 decision rights，避免 automation 变成 hidden authority。


## 8. 执行层

问题：平台变更如何安全交付？

### 输入

- 产品层的 acceptance criteria 和技术层的技术契约。
- OpenSpec proposal、design、tasks、stable specs 和 archive 状态。
- local-main-first 发布规则和当前 session ownership claims。

### 工具与技术

- OpenSpec change control：记录 proposal、design、tasks、specs 和 archive evidence。
- local-main-first delivery：使用 feature branches、merge requests、pipelines 和 post-merge GitHub sync。
- 仓库 checker：验证双语文档、名称解释、session claims、安全规则脚本背书和 OpenSpec health。
- `openspec/changes/<change-id>/proposal.md` 是 ASCII OpenSpec 提案；它解释为什么需要某个具体平台变更。
- `openspec/changes/<change-id>/design.md` 是 ASCII OpenSpec 设计；它解释该平台变更如何实现。
- `openspec/changes/<change-id>/tasks.md` 是 ASCII OpenSpec 任务清单；它跟踪该 change 的完成状态。
- `openspec/changes/<change-id>/*.zh-CN.md` 是同一 change artifacts 的 UTF-8 中文对照文件。
- `tools/run_openspec_guard.py` 是 OpenSpec guard 脚本；它验证官方 refresh、仓库规则和 clean-git 预期。

### 输出

- 带显式验证证据的小步 local-main-first integration package。
- 已完成或已归档的 OpenSpec changes，并在需要时同步 stable specs。
- 平台影响类变更的 release、rollback 和 verification evidence。

## 9. 增长层

问题：平台如何扩展到多个项目，同时不共享 repo-local truth？

### 输入

- 执行层输出的 releases、templates、helper scripts 和 operator guidance。
- 指标层输出的 adoption 和 friction signals。
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
- Template update rules、onboarding notes、adoption reports 和 profile-selection guidance。
- 当采用摩擦出现时，向战略、指标、产品、技术、组织和运营层反馈。


## 10. 运营层

问题：平台发布后如何保持可用、可支持、可恢复？

### 输入

- 执行层输出的已发布 helpers、templates、specs、startup summaries 和 checker behavior。
- 增长层输出的 adoption reports、operator questions、skill-profile feedback、support friction 和 incident signals。
- 技术约束、ownership boundaries 和 rollback paths。

### 工具与技术

- Support playbook 设计：定义 wrapper failure、cleanup-output noise、skill-context budget warning、MCP startup issue 和 CI drift 的 triage 路径。
- Health-check 与 status-surface review：保持 read-only status helpers 在启动任何 durable lane 前可用。
- 文档运营：把重复 operator questions 转化为 startup summary、governance、template 或 FAQ 更新。
- Changelog 与 release-note discipline：记录用户可见控制面变化。
- Runner-minute 与 provider-pacing review：让发布和 agent fan-out 成本保持可见。

### 输出

- Support notes、troubleshooting guidance、FAQ updates、changelog entries 和 health-check expectations。
- 证明已发布平台工作仍可理解、可恢复、可支持的运营证据。
- 输出给产品、技术、组织、增长和复盘层的反馈。


## 11. 复盘层

问题：哪些平台经验应该变成规则、checker 或模板？

### 输入

- 执行层的 validation results、release outcomes、rollback outcomes 和 incidents。
- 增长层的 adoption reports 和 downstream feedback。
- 运营层的 support records、startup noise、skill-profile issues 和 toolchain failures。
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
- 向认知、商业、市场、战略、指标、产品、技术、组织、执行、增长和运营层反馈可复用经验。

## Release Slicing Rule

一个平台 MR 通常只应该修改一个层级或一个控制面。好的例子包括：新增一份 lifecycle reference、新增一个 checker、归档一个 OpenSpec change、细化一个 release gate 或更新一条模板规则。
