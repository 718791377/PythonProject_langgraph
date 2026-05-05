---
doc_id: codex_cli_personal_production_durable_team_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md
translation_of: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md
doc_class: implementation_plan
status: draft
---

# Codex CLI 个人开发者生产级持久化团队实施方案

> 适用范围与文档身份
>
> - 本文不是纯用户级权威规则总表，也不是单仓库任务清单。
> - 本文是一份**兼顾用户级与项目级**的 implementation plan，用于指导同一 machine / user / Codex home 下，所有 `PyCharm / Codex CLI` 项目可共用的个人开发者生产级持久化团队方案如何部署。
> - 用户级部分负责描述共享控制面、共享运行时、共享角色目录和长期契约方向。
> - 项目级部分负责说明每个仓库如何承接 repo-local 源码、repo-local durable state、OpenSpec、项目文档、测试与例外规则。
> - 稳定用户级规则应以下列治理文档为准：`docs_bilingual/governance/`；当前仓库的结构性落地与多文件改动仍应进入 OpenSpec。

## 1. 文档定位与目标

本方案定义在以下**目标假设基线**下，如何为 `Codex CLI` 建设“个人开发者可长期维护的生产级持久化团队”，并把它落实成一套可由所有 `PyCharm / Codex CLI` 项目共用的长期方案：

- `subagent` 保持现有职责不变
- `native_omx` 保持现有职责不变
- `langgraph` 视为已基本达到 `fully realized LangGraph-native orchestration runtime`
- 不允许为了新能力而破坏现有三条 `lane`，即三条长期稳定的能力与职责分工通道，的正常使用
- 允许复用外部工具，但复用必须服从仓库现有安全边界与 additive-only 治理纪律

本方案**不修改**白皮书：

- [solo_maintainable_production_persistent_team_research.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/governance/solo_maintainable_production_persistent_team_research.zh-CN.md)

本方案在文档体系中的定位是：

| 层级 | 本文角色 |
| --- | --- |
| 用户级 | 描述所有 `PyCharm / Codex CLI` 项目共用的目标态、共享控制面、共享运行时和长期契约方向 |
| 跨项目共享层 | 说明共享 launcher、共享 support scripts、共享 venv、共享角色目录与安装产物如何工作，以及哪些内容不能承载 canonical durable state |
| 项目级 | 说明单个仓库如何承接 repo-local 状态、源码、OpenSpec、项目文档、测试与 rollout |

本方案的作用是：

- 把白皮书里的十层框架映射到一套可供所有 `PyCharm / Codex CLI` 项目共用的个人开发者生产级持久化团队方案
- 说明在该假设基线下，用户级、跨项目共享层和项目级各自应如何落地
- 定义哪些能力可直接复用，哪些只能借鉴，哪些不应进入主栈
- 说明多个项目如何共享同一套个人开发者生产级持久化团队方案，同时保持项目 durable state 隔离
- 说明已有 `experts / durable_team / persistent team` 如何纳入统一管理，而不抹平三者差异
- 给出在不破坏现有行为的前提下的分阶段 rollout 路线

## 2. 问题陈述与设计驱动

在该目标假设基线下，真正的问题已经不再是“LangGraph 能不能用”，而是：

- 三条 lane 如何在长期生产使用中保持稳定分工
- 哪些 durable truth 应放在 `langgraph`，哪些仍应留在 `native_omx`
- `subagent` 如何继续作为 leader-side `burst expert`，即按需短时调用的专家角色，而不被误下沉成持久 worker
- 个人开发者如何在冷启动、上下文中断、部分失败、审批阻塞、版本切换后仍能恢复系统
- 如何在不引入第二套隐式控制面的前提下，逐步增加记忆、检索、回归、GUI 与安全能力

本方案的设计驱动固定为五条：

1. `恢复优先于自动化` - design principle that recovery must be reliable before more automation is added.
2. `控制面清晰优先于执行面复杂` - design principle that operator control must stay clear before execution becomes richer.
3. `additive-only 优先于替代式重构`：新能力只能做增量扩展，不能重写既有 lane 语义
4. `manual-first 优先于黑箱自动推进`：高风险动作默认先人工控制，再谈自动化
5. `单人长期维护优先于平台级复杂度` - design principle that solo maintainability wins over platform-scale complexity.

## 3. 目标能力与非目标

### 3.1 目标能力

本方案要实现的目标能力是：

- 为 `Codex CLI` 定义一套长期可持续、可跨多个 `PyCharm / Codex CLI` 项目共用的持久化团队模型
- 让 `langgraph` 成为图式持久化团队编排主后端之一
- 保持 `native_omx` 作为 worker-centric durable lane
- 保持 `subagent` 作为 leader-side expert routing lane
- 为十层框架建立 repo-grounded 的落地映射
- 明确记忆、检索、回归、安全、GUI 的引入顺序与边界
- 明确哪些能力属于用户级共享层，哪些属于跨项目共享层，哪些必须留在项目级
- 让个人开发者在不读源码的情况下也能 inspect、approve、recover、resume 大多数运行中线程

### 3.2 非目标

本方案不做以下事情：

- 不把 `langgraph` 写成三条 lane 的统一替代层
- 不重新定义 `subagent` 的 burst delegation 语义
- 不重新定义 `native_omx` 的 worker-centric durable lane 语义
- 不把 `leader session`，即当前主 `Codex CLI` 会话本身，下沉成新的持久 leader pane
- 不一次性上全量 heterogeneous persistent team
- 不把 GUI 提前做成主运行时
- 不为了记忆或向量检索，重写已有 durable truth

### 3.3 恢复的十层框架落地映射

白皮书中的十层框架是本 draft 的必备组织模型。它必须保留在本方案中，确保冷启动维护者不用先读完整治理白皮书，也能看到“生产级持久化团队”目标态如何拆解。

恢复后的十层模型如下：

| 层级 | 生产含义 | 本方案中的落地规则 |
| --- | --- | --- |
| 1. 持久化内核 | 负责状态、checkpoint、event history、执行位置与恢复语义。 | `.omx/state/` 是仓库本地 durable-state 目录；它保存每个仓库自己的 canonical durable truth，不能被共享成用户级全局状态目录。 |
| 2. 交互与执行层 | 负责 command、event、task、executor、本地或远端执行。 | `codex-ohmy` 是日常使用的 Codex wrapper 启动器；`codex-raw` 是绕过 wrapper 的原生 Codex 启动器；两者都应保持为薄入口，真正约束放在脚本与文档化命令里。 |
| 3. 团队编排层 | 负责角色分工、任务调度、并行切片、冲突收敛与人工介入。 | `subagent` 是 leader-side burst expert lane，即主会话短时调用专家的通道；`native_omx` 是 worker-centric durable execution lane，即以 worker 生命周期为中心的持久执行通道；`langgraph` 是 graph-shaped checkpoint/resume orchestration lane，即图式 checkpoint 与恢复编排通道。 |
| 4. 长期记忆层 | 负责跨会话、跨任务保存事实、经验、规则和 artifact 摘要。 | memory 可以增强执行，但不能成为 workflow truth、approval truth 或唯一恢复来源。 |
| 5. 上下文增强层 | 负责 retrieval、filtering、reranking、compression、injection 与 context-budget governance。 | startup summary、governance docs、OpenSpec artifacts 和受控检索可以增强上下文，但必须可检查、可预算控制。 |
| 6. 向量数据库与检索存储层 | 负责 vector indexing、tenant isolation、filtering、backup/restore 与 lifecycle strategy。 | vector storage 是可选能力，必须放在 provider adapter 后面；它不能替代 repo-local durable state 或权威文档。 |
| 7. 质量保障层 | 负责运行时约束、输出校验、工具校验、approval gate 与 acceptance gate。 | 重要安全规则必须由 script controls、checkers、CI gates 和 approval prompts 共同支撑，不能只靠 prompt reminders。 |
| 8. 评测与回归层 | 负责 benchmark sets、experiment comparison、online evaluation、regression gates 与 version comparison。 | regression fixtures 和 evaluation reports 应在 durable core 已具备可观测状态与 rollback evidence 后逐步加入。 |
| 9. 安全与持久化增强层 | 负责 authorization、audit、secrets、data classification、encryption、tamper resistance 与 recovery safety。 | MCP scope、secret handling、permission boundaries 与 state write scopes 必须在冷启动会话没有历史上下文时也能 fail closed。 |
| 10. 本地 GUI 控制中心 | 让维护者无需直接读源码，也能 inspect state、approve actions、replay、intervene 和 recover。 | GUI 或 dashboard 必须 observer-first，并且必须在 read-only state inspection、recovery surfaces 和 guarded action semantics 之后再推进。 |

由此得到的 release 规则是：

- R0 和 R0.5 只在最小 governance 与 read-only inspection 层面覆盖第 1、7、9 层。
- R0.6 到 R0.8 通过小型 smoke/adoption gate 演练第 1 到第 3 层，不宣称完整生产目标已经实现。
- R1.0 到 R1.2 让第 1 到第 3 层在多项目中可用，同时把第 4 到第 10 层保持为受控、可选或 observer-first。
- R2.0 各切片再补齐 durable memory、recovery hardening、graph-native orchestration、security hardening、performance tests、operator dashboard、maintenance strategy 与 rollback evidence。
## 4. 三条 Lane 的职责分层

### 4.1 `subagent`

固定定位：

- leader-side bounded expert delegation：leader 会话按需短时调用的专家通道，而不是常驻持久 worker
- architect / planner / verifier / researcher 等 burst role 的主要落点
- 不拥有团队级 durable truth
- 不承担长期持久 worker 身份

### 4.2 `native_omx`

固定定位：

- worker-centric durable execution lane：以 worker 生命周期、worktree、mailbox 和稳定执行为中心的持久化执行通道
- 负责 `worker lifecycle`，即 worker 的启动、运行、等待、退出和恢复生命周期
- 负责 `mailbox state`，即 worker 收件箱中的任务与消息状态
- 负责 `worktree-scoped execution state`，即绑定到某个 worktree 的局部执行状态
- 负责 `worker team identity`，即 durable team 中 worker 的稳定身份信息
- 适合长期稳定执行、任务分发、同质 worker lane
- 不应被文档重写成“过渡能力”

### 4.3 `langgraph`

在本假设基线下的目标定位：

- graph-native persistent team kernel：以图状态、checkpoint、approval、resume、replay 和 phase graph 为核心的持久化团队内核
- 负责 `checkpoint-native orchestration state`，即以 checkpoint 为主的图式编排状态
- 负责 `thread phase`，即线程当前所处的阶段位置
- 负责 `approval state`，即审批中的阻塞、决议和关联对象状态
- 负责 `replay/recovery provenance`，即回放和恢复动作的来源、目标与依据
- 负责 `frozen implementation brief`，即被冻结、可长期引用的实现 brief 工件
- 负责 `survivor queue`，即经裁决后仍需继续处理的问题或工件队列
- 承担图式多阶段持久化团队的主后端之一
- 但仍保持 `durable backend family` 的 additive 角色，而不是替代整个产品线

### 4.4 三条 Lane 的长期关系

长期稳定关系应固定为：

- `subagent` = 专家路由与 leader-side burst 协同
- `native_omx` = worker-centric durable execution
- `langgraph` = graph-shaped durable orchestration，即图式多阶段持久化团队流

这三条 lane 是互补关系，不是替代关系。

## 5. 工具复用与共享约束

### 5.1 复用原则

允许工具复用，但必须服从以下规则：

- 不得让外部工具成为新的权威控制面
- 不得让外部工具成为新的 durable truth
- 不得让外部工具隐式改变现有 lane 的职责边界
- 外部工具只能挂接到既有 orchestration line
- 所有复用都必须经过 `bounded adapter`，即能力范围、输入输出和副作用边界都被显式限制的适配层，而不是直接把外部项目的运行时范式并入主栈

### 5.2 共享依赖与运行时归属

`D:\PythonProject_langgraph` - 当前 orchestration repository，即共享 Codex CLI durable-team 工具、adapter、checker 和 installer logic 的源码真相源。

本仓库可以统一管理 Codex CLI durable-team 控制面所需的 dependency declarations、installation scripts、wrappers 和 adapter contracts。实际第三方 runtime 产物应保留在 ignored local runtime directories，例如 `.runtime/`、`.venv-tools/` 或 `.toolchains/`；这些目录是机器本地依赖缓存或虚拟环境，不是源码真相文件。

默认规则：

- 用于 evaluation、GUI control、queues、embeddings、vector retrieval、dashboarding 和 recovery tooling 的第三方依赖，原则上只服务各开发项目的 Codex CLI durable-team runtime。
- 这些依赖默认不得和具体 business runtime dependencies 混用。
- 如果具体业务项目也需要同名 library，必须在该业务项目仓库里自行声明、安装、测试、打包和发布业务依赖。
- 共享 durable-team wrappers 只能通过显式 adapters、profiles 和 release gates 调用业务仓库。

窄模型服务例外：

- 本地 Llama 部署是一种 local model service，可以同时被 Codex CLI durable-team runtime 和具体 business runtimes 调用。
- 共享本地模型服务必须通过 provider adapters 和 provider profiles 访问。
- provider adapters 必须隔离 policy、logging、permissions、prompts、secrets、customer data、business state 和 durable-team state。
- 本地模型服务不能成为任何一侧的 durable truth。

`PySide6` 边界：

- 本方案中的 `PySide6` 指 Codex CLI durable-team local GUI control center，即用于 inspect runs、approvals、recovery candidates、regression results、helper state 和 template state 的操作员工具。
- 具体业务项目也可以使用 `PySide6`，但那是独立的 business GUI。它的 dependencies、packaging、state、user interface 和 release rules 属于业务项目，不属于本 durable-team 控制中心。
- 两个 GUI surface 不得共享 runtime state、approval state、customer data 或 release artifacts。

### 5.3 推荐复用的工具
#### 强烈推荐

- `SQLite` - 适配层：持久化内核层
  - 适配层：持久化内核层
  - 用途：`run index`、`thread index`、`event ledger`、`approval ledger`、`audit ledger`、`artifact index`

- `promptfoo` - 适配层：评测与回归层
  - 适配层：评测与回归层
  - 用途：offline eval、CI regression、red team、版本比较

- `QMD` - 适配层：上下文增强层
  - 适配层：上下文增强层
  - 用途：本地 authority/spec/docs 的 first local lookup sidecar

#### 条件推荐

- `jina-embeddings` - 适配层：上下文增强层 / 向量检索层
  - 适配层：上下文增强层 / 向量检索层
  - 用途：`optional embedding provider`，即可插拔 embedding 提供者
  - 约束：必须通过 `provider adapter` 接入，不得绑定为唯一模型路线

- `PySide6` - 适配层：本地 GUI 控制中心
  - 适配层：本地 GUI 控制中心
  - 用途：observer-first / guarded-actions desktop control center

- `Redis` - 适配层：交互与执行层 / 团队编排层
  - 适配层：交互与执行层 / 团队编排层
  - 用途：presence、短期队列、锁、Pub/Sub
  - 约束：不得作为唯一 durable truth

#### 仅借鉴设计，不建议纳入主线

- `ClawTeam-OpenClaw` - 只借 swarm/worktree/mailbox/product model
  - 只借 swarm/worktree/mailbox/product model

- `OpenViking` - 只借 context database / session archiving / memory extraction 的边界模型
  - 只借 context database / session archiving / memory extraction 的边界模型

- `lossless-claw-enhanced` - 只借 context compaction / CJK-aware summarization 思路
  - 只借 context compaction / CJK-aware summarization 思路

#### 不纳入主线

- `Light Judge` - 只保留轻量 judge 策略思路，不纳入外部依赖
  - 只保留轻量 judge 策略思路，不纳入外部依赖

- `memory-lancedb-pro-skill` - 作为知识包参考，不作为生产基础设施
  - 作为知识包参考，不作为生产基础设施

### 5.4 抽象业务能力 Profiles

Business capability profiles 是覆盖十层框架的横向 workload classification，不是第十一层，也不是具体业务名称。任何新增 workload 在实施前，都应先映射到一个或多个 profile。

| Capability profile | 通用目的 | 主要十层需求 |
| --- | --- | --- |
| Interactive frontend product delivery | 交付可测试、可发布的用户前端、小程序、Web 或 app surface。 | 第 2、3、7、8、9 层。 |
| Generated media asset pipeline | 管理生成式图片、视频、音频、prompts、parameters、asset selection 和 downstream approval。 | 第 1、4、5、7、9 层。 |
| Platform content operations | 治理内容生成、排期、发布、回执记录、失败重试和 audit。 | 第 1、2、7、8、9 层，以及可选第 10 层。 |
| Customer message automation with human handoff | 治理客户自动回复、敏感内容处理、人工接管和 audit。 | 第 1、4、5、7、9 层，以及可选第 10 层。 |
| External domain-agent runtime governance | 当最终用户面对的 agent runtime 位于 Codex CLI 之外时，治理 domain-agent profiles、knowledge updates、regression tests、release gates、logs 和 recovery。 | 第 1、3、4、5、7、8、9 层。 |
| Knowledge retrieval and citation workflows | 治理 retrieval、citation、evidence chains、summary quality 和 hallucination checks。 | 第 4、5、6、7、8 层。 |
| Professional tool teaching and guided operation | 治理 step-by-step operation help、screenshots、case libraries、error recovery 和 risk notices。 | 第 2、4、5、7 层，以及可选第 10 层。 |
| Solo business operations management | 治理 solo operator 的 projects、customers、sales、delivery、cost summaries 和 review cycles。 | 第 1、3、4、7 层，以及可选第 10 层。 |
| High-risk decision support | 治理需要 simulation、approval、audit、rollback 或 stop-loss behavior 的高风险决策。 | 第 1、7、8、9 层，以及可选第 10 层。 |
| Layout-sensitive document transformation | 治理 formatted documents 的 extraction、replacement、rendering、human review 和 layout regression。 | 第 1、2、5、7、8 层。 |
| Structured proposal and compliance document delivery | 治理 template libraries、source collection、section generation、citations、compliance checks、approvals 和 delivery records。 | 第 1、4、5、7、8、9 层。 |
| Template and project bootstrap lifecycle | 治理 new-computer bootstrap、project template initialization、existing-project update、backups 和 checker verification。 | 第 1、2、7、9 层。 |

具体 workload examples 应放在 `docs_bilingual/implementation_plans/codex_business_capability_profiles.zh-CN.md` 这个参考对照表中。生产级持久化团队总方案应保持抽象，避免未来业务名称反向改写架构。
## 6. 面向 Codex CLI 的控制面

个人开发者的最小 `control surface`，即用来观察、批准、恢复、回放、切换与排障的统一控制面，必须回答五个问题：

1. 现在有哪些 run / thread 在执行？
2. 哪些被阻塞？阻塞原因是什么？
3. 哪些审批在等待？下一步可执行动作是什么？
4. 最近一次失败发生在哪里？失败前后的 durable 证据是什么？
5. 如何在不读源码的情况下 pause / approve / reject / resume / recover？

因此，推荐控制面应至少提供：

- CLI-first 统一入口：以主 `Codex CLI` 为第一操作入口，不再额外发明新的默认入口
- loopback control API：只对本机回环地址开放的统一控制接口
- `inspect summary`：面向操作员暴露的稳定、有限、可读的检查摘要
- `approval surface`：集中展示与处理审批等待项的控制面
- `recovery surface`：集中展示恢复候选、恢复原因和恢复动作入口的控制面
- replay / time-travel 入口：回放执行历史或跳回旧检查点的受控入口
- cost / concurrency / backlog 简表：帮助单人维护者快速判断负载、排队和成本的最小状态板

## 7. 生产级持久化团队模型

在本方案下，`生产级持久化团队` 不是“更多常驻 agent”，而是以下组合：

- 一个 `leader session`
- 一组 leader-side burst experts
- 一条 worker-centric durable lane
- 一条 graph-centric durable lane
- 一套统一的 inspect / approval / audit / recovery contract

团队模型至少要显式定义：

- `role assignment`：角色如何分工、哪些角色常驻、哪些角色 burst 调用
- `ownership`：任务、分支、工件和恢复动作的责任归属
- `parallel slice planning`：并行切片如何拆分和命名
- `convergence`：并行分支如何收敛成单一下一步决策
- `conflict detection`：并行推进时如何发现状态和写入冲突
- `approval wait`：因等待显式审批而进入的权威阻塞状态
- `manual takeover`：操作员显式接管某个线程、分支或恢复动作
- `failure branch recovery`：失败分支如何局部 redrive、局部修复或回退

默认模型推荐：

- `subagent` 继续承接 architect / planner / researcher / verifier
- `native_omx` 继续承接 homogeneous durable workers，即默认以同质 worker 为主，而不是全异构常驻团队
- `langgraph` 负责持久化团队 phase graph、interrupt graph、approval graph、recovery graph
- `mixed compose opt-in`：异构 persistent compose 只作为高级显式开启模式

### 7.1 多个 `PyCharm / Codex CLI` 项目如何共用同一套方案

本方案面向的不是某一个仓库单独自造一套 persistent team，而是同一 machine / user / Codex home 下的多个 `PyCharm / Codex CLI` 项目共用同一套个人开发者生产级持久化团队运行模型。

共用方式应固定为：

- **共享用户级控制面**
  - 共用 launcher、共用 capability switches、共用 expert routing 语义、共用 inspect / approval / recovery / replay 心智模型

- **共享跨项目运行时底座**
  - 共用 shared venv、shared support scripts、shared role catalog、shared helper 安装产物、shared schema / template

- **隔离项目级 durable truth**
  - 每个项目仍保留自己的 repo-local 源码、repo-local `.omx/state/`、OpenSpec、项目文档、项目测试、项目 artifacts、项目 reports

因此，共享的是：

- 工具
- 规则
- 控制面语义
- 角色目录
- 共享运行时底座

隔离的是：

- canonical durable state
- repo-local 源码
- repo-local OpenSpec 变更
- 项目记忆、项目工件和项目恢复证据

必须长期坚持：

- 同一项 durable task 绑定一个明确的 `repo_root`
- 同一项 durable task 只使用一个 durable backend family
- 用户级共享层不得承载任何单项目的 canonical durable state

### 7.2 `experts / durable_team / persistent team` 的统一管理

在本方案下，这三个词必须分层，不再混用：

- `experts` - 指 leader-side burst experts
  - 指 leader-side burst experts
  - 本质是角色与调用方式，而不是持久 worker
  - 例如 `analyst / architect / planner / writer / verifier`

- `durable_team` - 指 durable backend family 下的执行对象
  - 指 durable backend family 下的执行对象
  - 在 `native_omx` 下更接近 tracked worker team / durable execution swarm
  - 在 `langgraph` 下更接近 tracked durable thread / graph execution posture

- `persistent team` - 指产品化总模型
  - 指产品化总模型
  - 它不是第三种 backend，也不是第三套 state root
  - 它表示的是：`leader session + burst experts + durable lane + 统一的 inspect / approval / recovery contract`

统一管理的原则不是把三者写成同一个东西，而是统一到同一套 operator-facing control contract 下：

- 统一的 inspect / status / run surface
- 统一的 approval surface
- 统一的 recovery surface
- 统一的审计与身份模型

因此，推荐的长期管理方式是：

- `experts` 进入用户级 routing catalog，但不进入 durable truth
- `durable_team` 进入 backend-specific execution state，并通过统一 inspect summary 暴露
- `persistent team` 保持为上位操作模型，用来组织用户级目标态和项目级承接

### 7.3 安全控制必须组合脚本与提示词

生产级持久化团队不能依赖模型在上下文变长后仍然记得一大段提示词。

所有系统级、用户级、项目级安全边界都必须同时使用两层控制：

- 脚本控制 - 可执行 checker、生成式 helper 逻辑、受保护状态转移或 CI gate；即使是没有历史上下文的冷启动模型执行，也必须默认 fail closed。
- prompt reminder - startup summary and implementation plan text; `AGENTS.md` is only a recovery reread target, not the literal canary prompt source.

最低生产要求：

- `experts` routing 在被宣称为自动行为前，必须有脚本可见的阈值或 checker 证据。
- `durable_team` 启动必须由计划已冻结和独立切片检查保护，不能只靠提示词提醒。
- `persistent team` 状态必须由可执行 helper 按仓库和 backend family 进行 scope，而不能只写在文档里。
- 发布、清理、状态修改和跨项目激活必须有脚本 gate，或者明确登记为尚未落地的 gap。
- 用户级总安全边界 checker 必须验证每条已登记安全规则都有脚本控制、提示词提醒和实施状态；否则必须报告为 tracked gap。

启动层还应加入上下文保留哨兵，但哨兵字面提示词属于项目级并由 startup summary 持有。它只能放在每个仓库自己的 `project_startup_summary.*` 文件对中，不进入 `AGENTS.md`、用户级启动摘要、implementation plan、生成式 wrapper 或 launcher payload。当前哨兵约定是：

- startup summary 定义本仓库完整模型回复的字面提示词，除非更高优先级 system 或 developer 指令阻止。
- 如果 startup summary 本应已读取，但完整回复缺少哨兵文本，则视为可能的上下文丢失信号。
- 恢复方式是从 `AGENTS.md` 和 `docs_bilingual/project_startup_summary.*` 重新执行冷启动阅读顺序，然后只补读继续当前任务必须需要的文件。

用户级 canary 能力应是 checker，而不是提示词注入器。它在收到 transcript 或 response text 时检查 startup-summary-defined canary；如果缺失，就输出上面的冷启动恢复指令。没有 transcript 或 response 输入时，它只检查当前项目是否在 `project_startup_summary.*` 中声明该哨兵，并且没有在其他 active instruction surface 重复字面提示词。

## 8. 状态、记忆与工件持久化

### 8.1 Durable Truth 的分层

必须区分以下真相层：

- `canonical durable state`：系统中真正承载 durable run / thread 恢复、续跑、审批、审计与跨后端一致性的主权状态面；其他状态若与它冲突，应以它为准
- `artifact state`：`canonical durable state` 中专门描述 durable artifacts 的那一层，负责 artifact 的存在性、身份、引用关系、队列状态和可恢复边界
- `memory state`：`canonical durable state` 中专门描述 memory surface 的那一层，负责记录记忆机制本身的运行语义，而不是长期记忆库全文
- `retrieval substrate`：为检索服务的底层承载层，例如 vector store、embedding index 或其元数据层，只负责“找得到什么”
- `derived inspect projection`：从 `canonical durable state` 以及相邻 artifact / memory surface 派生出来的只读检查视图，服务于 `status`、`inspect`、operator summary 等观察面

不得把它们混成一个“memory”或一个“dashboard feed”。

### 8.2 推荐持久化分工

#### `langgraph`

主负责：

- checkpoint-native orchestration state：以 checkpoint 为主的图式编排状态
- thread phase：线程当前所处的阶段位置
- approval state：审批中的阻塞、决议和关联对象状态
- replay/recovery provenance：回放和恢复动作的来源、目标与依据
- frozen implementation brief：被冻结、可长期引用的实现 brief 工件
- survivor queue：经裁决后仍需继续处理的问题或工件队列

#### `native_omx`

主负责：

- worker lifecycle：worker 的启动、运行、等待、退出和恢复生命周期
- mailbox state：worker 收件箱中的任务与消息状态
- worktree-scoped execution state：绑定到某个 worktree 的局部执行状态
- worker team identity：durable team 中 worker 的稳定身份信息

#### `SQLite`

推荐作为共享 durability substrate，承接：

- run index：run 级对象的快速索引
- thread index：thread 级对象的快速索引
- event ledger：按时间追加记录关键 durable 事件的账本层
- approval ledger：审批动作与审批结果的账本层
- audit ledger：高风险动作与责任归属的审计账本层
- artifact index：durable artifact 的索引层
- memory metadata：长期记忆配置、命名空间和引用元数据
- retrieval metadata：检索层、embedding 层和向量层的元数据

#### 文件系统

继续承接：

- artifacts：durable artifact 的正文或文件载体
- reports：评测、回归、恢复、排障等报告文件
- exported logs：导出的原始或归档日志
- checkpoints 的可视化 sidecar：帮助操作员理解 checkpoint 的旁路可视化材料
- cached summaries：为冷启动和 inspect 加速准备的缓存摘要

### 8.3 记忆层与检索层边界

必须显式区分：

- `procedural memory`：规则、提示词、技能和程序性知识
- `short-term thread memory`：线程级短期上下文和最近状态
- `semantic long-term memory`：事实、偏好、规则等语义长期记忆
- `episodic memory`：过往案例、轨迹、few-shot 样本等情节记忆
- `document knowledge base`：用于检索增强的文档知识库

其中：

- thread state 不得被当成长久记忆
- long-term memory 不得承担 workflow recovery 语义
- vector store 只作为 retrieval substrate，不得取代 canonical durable state

### 8.4 历史经验教训的沉淀与再利用

这一节要解决的不是“复盘要不要写”，而是：过去踩过的坑、验证过的做法、失败后的修正，今后到底怎样才能被重复利用，而不是又靠人脑去记。

本方案对“历史经验教训”的工作定义是：

- 历史经验教训不是流水账
- 它是从过去的运行、设计、实施、失败和恢复中，抽出来的可复用约束、判断依据、默认做法和反模式
- 它的目标不是保存背景故事，而是减少重复试错、减少重复返工、提高后续主线的稳定性和恢复性

#### 8.4.1 什么内容值得作为经验教训沉淀

以下内容值得进入经验归档：

- 会重复出现的问题
- 会影响恢复、稳定、成本、审批或可维护性的问题
- 已经形成明确处理办法的问题
- 能进一步转成规则、检查项、默认做法或测试门的问题

以下内容通常不必进入长期经验归档：

- 一次性的临时环境噪声
- 纯情绪化描述
- 没有原因判断和处理办法的零散观察
- 只对某一次手工操作有意义、无法复用的偶发细节

#### 8.4.2 经验教训按什么分类

建议把经验教训按“对象类型 + 五条辅助轴”来组织，而不是把所有内容混成一张大表。

首先看对象类型。对本仓库最有价值的对象包括：

| 对象类型 | 典型内容 | 成功经验主要沉淀什么 | 失败教训主要沉淀什么 |
| --- | --- | --- | --- |
| 项目级 | 仓库长期方向、产品线边界、治理模型 | 长期有效的原则、默认边界、稳定叙事 | 系统性风险、长期漂移源、必须禁止的反模式 |
| 主线 / 变更级 | mainline、OpenSpec change、迁移波次 | 标准推进顺序、验收门、回滚点 | 容易卡死的阶段、前置条件缺口、错误拆分方式 |
| 支线 / 试验级 | canary、shadow、一次试验路线 | 低成本高信号的试验方法 | 不具代表性的试验方式、不能外推的结论 |
| 方案 / 架构级 | lane 分工、state model、backend 选择 | 何时选哪条 lane、哪些边界值得保留 | 哪些耦合会破坏恢复性、可观察性或兼容性 |
| 实施 / rollout 级 | 上线顺序、迁移策略、兼容策略 | 正确的 rollout 顺序、灰度方式、影子验证方式 | 会导致污染、不可逆升级或大面积返工的 rollout 方式 |
| 实现路线级 | 先改哪层、先修哪面 | 哪类问题先从哪层入手最稳 | 不该把问题塞到错误层处理的反例 |
| 工具调用级 | CLI 命令、脚本调用、环境约束 | 稳定命令模板、推荐调用姿势 | 长命令、编码、权限、路径、幂等边界等失败模式 |
| skill 使用级 | 何时用 analyst / planner / verifier / writer | 哪类任务用哪类 skill 最省上下文、最稳 | 误用 skill 放大复杂度或误导执行的情况 |
| prompt / 指令级 | brief 模板、developer instructions、任务提示 | 有效 prompt 模板、冻结 brief 结构 | 过长、冲突、重复、把状态和策略混写的反模式 |
| 接口 / 契约级 | CLI 参数、状态字段、resume contract | 稳定输入输出、清晰版本字段、可恢复入口 | 隐式字段、兼容性破坏、状态语义塌缩 |
| 规则 / 治理级 | additive-only、manual-first 等 | 值得长期强制的规则 | 模糊规则、危险默认值、容易误解的说法 |
| 用户 / 操作者习惯级 | 高频操作方式、常见误操作 | 对系统友好的操作习惯 | 需要被产品吸收掉的高频误操作负担 |

除了对象类型，还建议给每条经验补五个辅助判断：

- 粒度：项目级、主线级、方案级、步骤级，还是单次事件级
- 时效性：是长期稳定，还是只对当前版本/当前 rollout 有效
- 复用范围：是跨项目可复用，还是只在本仓库、某条主线内复用
- 结构化程度：是规则/枚举/checklist，还是案例说明
- 行动性：是下次可以直接照做，还是只能作为判断参考

这样做的目的，是把“经验”从散乱描述变成后续能复用的输入。

#### 8.4.3 这些经验分别放在哪里

经验教训不能只问“记不记”，还要问“放哪一层最合适”。原则是：

- 默认不要把经验教训直接塞进 canonical durable state
- canonical durable state 负责运行真相，不负责承载大段经验正文
- 经验教训通常应分成“原始证据、归因结论、可复用规则”三层存放

推荐落点如下：

| 内容层次 | 放置位置 | 说明 |
| --- | --- | --- |
| 原始事件证据 | `reports`、`exported logs`、incident note、变更记录 | 记录当时发生了什么，保留现场证据 |
| 当前主线可直接引用的摘要 | 当前 implementation plan、当前 OpenSpec design/tasks | 只保留和本主线直接相关的摘要、约束和行动项 |
| 仓库长期规则与边界 | `docs_bilingual/governance/`、operator playbook、长期 policy 文档 | 用于沉淀跨主线、长期稳定的规则和反模式 |
| 工具 / skill / prompt / 接口的专属经验 | 对应 `tools/` 文档、skill 文档、prompt 模板、接口契约文档、测试 | 让经验回到真正的 owner 位置，而不是永远挂在总文档里 |
| 统一检索与索引信息 | `SQLite` 中的索引和元数据 | 只存 lesson metadata、标签、关联对象、指针，不存全部正文 |
| 长期可检索案例 | 经验清单、专题说明、案例文档 | 用于后续检索增强和 cold-start 阅读 |

因此，最稳妥的做法不是把所有经验都堆到一个“memory”里，而是：

1. 原始失败或成功案例，先保留在事件和报告层  
2. 与当前主线直接相关的部分，摘要写进当前 implementation plan  
3. 已经被验证值得长期保留的规则，再提升到治理文档、工具文档、测试或默认行为里  

如果后续需要统一检索，可以在 `SQLite` 增加 lesson index 或 lessons metadata；但它仍然只是索引层，不是新的真相源。

#### 8.4.4 从经验归档到可执行动作

经验教训只有在能转成后续动作时，才真正有价值。建议固定三种转化方式：

- 转成约束  
  - 例如：新增入口时，必须检查是否存在命令行长度上限风险

- 转成检查项  
  - 例如：在 rollout 前增加一条验证，确认默认入口不会因为超长参数而失效

- 转成默认做法  
  - 例如：优先用配置文件、参数文件、状态文件或短参数引用承载稳定上下文，而不是把大段信息直接拼进命令行

在维护机制上，建议长期坚持：

- 只有当某条经验已经影响实现路径选择时，才进入长期归档
- 有新结论时更新原条目，而不是重复新增相似条目
- 已失效的经验要标记“仅供历史参考”，不能继续当作现行约束
- 每次主线收尾时，都检查是否有值得提升为规则、测试或默认做法的新经验

#### 8.4.5 示例：`codex-ohmy` “命令行太长”该放在哪里

示例：

> `PS D:\PythonProject_langgraph> codex-ohmy`  
> `命令行太长。`

这个案例首先属于：

- 工具调用级失败经验

但它真正值得长期沉淀的，不是“某次命令失败了”，而是背后的抽象结论：

- launcher / 控制面入口不应以内联超长参数承载大段 instructions 或 prompt
- 长指令应优先文件化、状态化或改成短参数引用

因此，这个案例建议分三层放置：

1. **原始事件层**  
   - 放在 incident note、排障报告、日志或 change 记录里  
   - 记录当时的命令、报错现象、触发环境和影响范围

2. **当前主线摘要层**  
   - 放在当前 implementation plan 的这一节里  
   - 作用是提醒后续设计与 rollout：新增入口时，默认避免继续堆长命令

3. **长期规则层**  
   - 放到 launcher / control surface 的契约文档、实现默认值和测试里  
   - 例如明确：大块 `developer_instructions` 不得长期依赖命令行内联传递；应改为文件、状态文件或短引用

也就是说，这个案例不应主要归到“用户说太多”或“prompt 写得不好”，而应主要归到：

- 工具调用失败经验
- launcher / 接口契约经验
- Windows CLI 长度限制下的控制面设计经验

如果把它转成后续默认做法，建议写成两条长期规则：

- 默认入口优先暴露短命令和少量必要参数
- 稳定上下文优先下沉到配置文件、参数文件、状态文件或 repo-local state，而不是持续拼接到命令行

这样，历史经验才真正变成下一次实施时可直接复用的输入。

## 9. 调度、切换与升级路径

### 9.1 Backend-family 规则

必须长期坚持：

- 同一 durable task / run 只允许选择一个 durable backend family：同一次持久化任务不得在运行中混用多个耐久后端家族
- 整个产品线允许 `native_omx` 与 `langgraph` 并存
- `subagent` 永远不作为 durable backend family

### 9.2 切换规则

推荐切换策略：

- 早期读上下文 / freeze plan：优先 leader + `subagent`
- worker-heavy execution：优先 `native_omx`
- graph-shaped long-running phased execution：优先 `langgraph`
- lane 不健康时：显式降级，不隐式漂移

### 9.3 升级路径

推荐路径：

1. 先固定三条 lane 的稳定叙事
2. 再把 `langgraph` 的 graph-native durable thread contract 固化
3. 再把 control plane、approval、recovery 统一成共享 surface
4. 再引入 memory/context/vector/GUI 等增强层

## 10. 仓库结构与实现落点

建议实现落点保持如下：

- 用户级共享层
- `C:\Users\lenovo\.codex\` - 用于承接共享 launcher、共享 support scripts、共享 role catalog、共享 helper 安装产物、共享运行时与共享状态开关
  - 用于承接共享 launcher、共享 support scripts、共享 role catalog、共享 helper 安装产物、共享运行时与共享状态开关

- 跨项目共享运行时层
  - 用户级 shared venv、用户级共享 helper、副本产物与可复用模板
  - 这些内容可以跨项目复用，但不能承载任何单项目的 canonical durable state

- `docs_bilingual/governance/` - 保持总方法论与治理边界
  - 保持总方法论与治理边界
- `docs_bilingual/implementation_plans/` - 记录面向当前目标态的实施方案
  - 记录面向当前目标态的实施方案
- `openspec/` - 放 proposal / design / spec / tasks
  - 放 proposal / design / spec / tasks
- `.omx/state/` - repo-local durable state
  - repo-local durable state
- `.omx/plans/` - 辅助计划、收敛产物、协作结果
  - 辅助计划、收敛产物、协作结果
- `tools/` - 各种 adapter、control helpers、eval helpers、GUI launchers
  - 各种 adapter、control helpers、eval helpers、GUI launchers

作为历史外部 OpenClaw 参考源，不应把未来实现继续散落回 `D:\PythonProject_OpenClaw` 做主线实现。

换句话说：

- 用户级层负责“所有项目怎么共用”
- 项目级层负责“这个仓库如何承接”

二者必须协同，但不能混成一个状态面。

## 11. 运行时边界与兼容性规则

以下边界必须保持稳定：

- leader session 不下沉
- `subagent` 不持久化为常驻 worker
- `native_omx` 不被重新解释为过渡层
- `langgraph` 不吞并全量运行时
- `oh-my-codex` 继续是 Codex 之上的 workflow / control layer

必须向后兼容的对象包括：

- `inspect/status/run surface`：面向操作员的检查、状态和运行入口集合
- `shared durable-state summary contract`：跨 lane 可消费的共享耐久摘要契约
- `artifact identity`：artifact 的稳定身份标识
- `approval identity`：审批对象和审批动作的稳定身份标识
- `recovery pointer identity`：恢复指针和恢复目标的稳定身份标识
- `backend-family selection semantics`：后端家族选择的稳定语义

## 12. 失败恢复、可观测性与排障

最小可观测面至少要暴露：

- active / blocked / failed runs：当前运行中、阻塞中和失败的线程/任务集合
- current phase / current node / current backend family：当前阶段、当前节点和当前使用的 durable backend family
- pending approvals：所有尚未决议的审批项
- recovery posture：当前线程可否恢复、建议如何恢复、阻塞在哪里
- artifact presence：关键 durable artifact 是否存在和是否可消费
- worker team status：当前 durable worker team 的健康与占用状态
- cost / concurrency / backlog：成本、并发占用和排队积压的最小指标

恢复面至少要区分：

- resume：从当前阻塞点继续执行
- replay：重放既有执行历史以恢复语义
- redrive：从失败分支重新驱动后续流程
- time-travel：跳回某个旧检查点或旧状态面
- update-state recovery：通过受控状态修补后恢复执行
- manual takeover：操作员显式接管恢复流程

不得把以上动作混成一个模糊的 `recover` 按钮。

## 13. 验证、测试与验收门槛

方案完成的最低验收标准应包括：

- 文档叙事统一，不再把 LangGraph 写成当前 MVP 叙事
- 三条 lane 的职责分层稳定
- inspect / approval / recovery 具备统一 surface
- 关键高风险动作有审计和 guarded action
- 安全关键提示词提醒都有对应脚本控制，或者明确登记为尚未落地的 gap，并由用户级总安全边界 checker 验证
- startup context-retention canary behavior is documented in project-level `project_startup_summary.*`; `AGENTS.md` is only a recovery reread target and must not contain the literal canary prompt, while the canary checker can report the cold-start recovery procedure when transcript evidence is available
- regression gate 已经存在
- 至少有 cold-start recovery drill
- 至少有一套失败分支 redrive drill
- 至少有一套 approval wait / approval reject 演练

建议复用的验证工具：

- `promptfoo`：评测与回归
- repo-local smoke / replay tests：状态和恢复

## 14. 分阶段实施顺序

### 14.0 Release train overlay for smaller delivery slices / 面向小版本交付的 release 轨道

这份 draft 必须通过更小的 release slices 交付，不能一次性拉成长实施波次。

推荐 release train：

| Release | 含义 | 实施姿态 |
| --- | --- | --- |
| `R0 Governance Baseline` | startup、OpenSpec、worktree、session ownership、MCP scope 和 safety-rule script backing。 | 基本已是 implemented baseline。 |
| `R0.5 Inspectable Durable State` | 只读 durable state status、selector safety 和 helper mirror source-of-truth。 | 基本已是 implemented baseline。 |
| `R0.6 Durable Routing Smoke Gate` | 未来 automatic durable routing exercise 的 dry-run 或 read-only gate。 | 下一条 active release slice。 |
| `R0.7 Native OMX Adoption MVP` | 在一个低风险 worker-centric task 中受控采用 `native_omx`。 | 未来 reviewed release slice。 |
| `R0.8 LangGraph Adoption MVP` | 在一个带 checkpoint、approval、frozen brief 或 survivor queue 信号的 graph-shaped task 中受控采用 `langgraph`。 | 未来 reviewed release slice。 |
| `R1.0 Personal Durable Team MVP` | 第一个可多项目使用的 personal durable-team MVP，具备可检查 lane 和 guarded actions。 | 未来 MVP，不是当前实施。 |
| `R1.1 Multi-project Consumer Rollout` | 跨项目 consumer rollout，同时保持 repo-local durable truth。 | 未来 rollout。 |
| `R2.0 Production Durable Team` | 完整生产目标，包含更强 memory、recovery、GUI 和 graph-native orchestration。 | 北极星目标，不是当前实施。 |

Release rules：

- 本 draft 保持 `status: draft`，直到某个具体 release slice 通过 OpenSpec 被提升。
- 每个 release slice 都必须有自己的 target repository、phase、task scope、validation path、rollback path 和 operator consent boundary。
- 某个 release slice 可以更新本 draft，但不得宣称整个 production durable-team target 已经实现。
- runtime exercises 从 `R0.6 Durable Routing Smoke Gate` 开始，而且该 release 默认 read-only。
- launcher 或 installer slice 要标记 production，还必须通过 R0.6.1 Codex native rollback gate，用来证明 native Codex、raw bypass、wrapper smoke、config sentinel 和 rollback evidence。

更细 release ladder：

| Release | 含义 | 实施姿态 |
| --- | --- | --- |
| `R0.6.0 Gate Template` | future smoke/adoption gate changes 及其 required fields 的模板。 | 下一条安全 planning slice。 |
| `R0.6.1 Gate Field Checker And Codex Native Rollback Gate` | required gate fields 的 checker-backed enforcement，并要求 native Codex、raw bypass、wrapper、config sentinel 和 rollback evidence。 | 当前安全 script-backed slice。 |
| `R0.6.2 Read-Only State Sampling` | 对一个 target repository 进行 status-only sampling。 | future read-only slice。 |
| `R0.6.3 Dry-Run Routing Decision` | 不进入 apply mode，只解释 no-team、native_omx 或 langgraph decision。 | future dry-run slice。 |
| `R0.6.4 Expected-Result Fixture` | 预期 dry-run decision 的 regression fixture。 | future test slice。 |
| `R0.6.5 Cross-Project Read-Only Review` | consumer-project review，用来证明 repo-local truth 不泄漏。 | future cross-project slice。 |
| `R0.7.0 Low-Risk Target Selection` | 第一个 native_omx target repository 和 task selection。 | future reviewed slice。 |
| `R0.7.1 Native OMX Dry-Run Stability` | apply mode 之前的稳定 native_omx plan。 | future dry-run slice。 |
| `R0.7.2 Explicit Apply Consent` | `-Apply` 前的精确 consent record。 | future consent slice。 |
| `R0.7.3 Lifecycle Record Check` | launch、reuse、shutdown 和 tracked-record evidence。 | future lifecycle slice。 |
| `R0.7.4 Restart Recovery Check` | native_omx state 的冷启动 inspection。 | future recovery slice。 |
| `R0.7.5 Native OMX Closeout Archive` | native_omx adoption 的 evidence archive 和 residue cleanup。 | future closeout slice。 |
| `R0.8.0 Graph-Shaped Task Selection` | 带 checkpoint、approval、frozen brief 或 survivor-queue signal 的 LangGraph target task。 | future reviewed slice。 |
| `R0.8.1 Checkpoint Smoke` | langgraph state 的保存与恢复 evidence。 | future smoke slice。 |
| `R0.8.2 Approval Gate Smoke` | operator decisions 的 pause 和 approval evidence。 | future smoke slice。 |
| `R0.8.3 Frozen Brief Smoke` | research-to-implementation frozen brief evidence。 | future handoff slice。 |
| `R0.8.4 Survivor Queue Smoke` | bug-review survivor queue evidence。 | future triage slice。 |
| `R0.8.5 LangGraph Closeout Archive` | 归档 evidence，但不把 langgraph 变成无关任务默认 lane。 | future closeout slice。 |
| `R0.9 Lane Arbitration` | native_omx、langgraph 和 no durable team 的 conflict rules。 | future arbitration release。 |
| `R1.0 Personal Durable Team MVP` | 第一个单用户、多项目可用 MVP。 | future MVP。 |
| `R1.1 Multi-Project Consumer Rollout` | 推广到 consumer repositories，同时保持 repo-local durable truth。 | future rollout。 |
| `R1.2 Operational Hardening` | logging、MCP scope、config sentinel、helper mirror、cleanup 和 rollback hardening。 | future hardening release。 |
| `R2.0.0 Production Readiness Standard` | production acceptance criteria 和 release gates。 | future production slice。 |
| `R2.0.1 Durable Memory Model` | memory boundaries、retention 和 replay policy。 | future production slice。 |
| `R2.0.2 Crash Recovery` | interruption 之后的 safe inspection 和 resume。 | future production slice。 |
| `R2.0.3 Graph-Native Orchestration` | 在 graph-shaped execution 确实合理时启用 graph-native orchestration。 | future production slice。 |
| `R2.0.4 Security And Secrets Boundary` | credentials、permissions 和 untrusted-input protection。 | future production slice。 |
| `R2.0.5 Performance And Concurrency Test` | worker count、provider pacing 和 long-running stability tests。 | future production slice。 |
| `R2.0.6 Operator Dashboard` | 清晰的 operator-facing status 和 control surface。 | future production slice。 |
| `R2.0.7 Multi-Project Maintenance Strategy` | repositories 之间的长期维护策略。 | future production slice。 |
| `R2.0.8 Production Release And Rollback` | 只有 rollback evidence 存在后才正式 release。 | final production slice。 |

### 14.1 Stage 0：叙事与治理对齐

目标：

- 把目标态假设基线和仓库叙事对齐

前置条件：

- 无

退出条件：

- startup summary、plan、OpenSpec 状态叙事一致
- 三条 lane 长期分工描述一致

### 14.2 第一阶段：持久化内核契约化

目标：

- 固化 `langgraph` lane 的 production-grade durable thread contract

重点：

- checkpoint / event envelope / migration compatibility：检查点、事件包络与迁移兼容矩阵
- approval / recovery provenance：审批与恢复来源链
- shared durable summary：跨 lane 可消费的共享耐久摘要契约

退出条件：

- 线程可 inspect、可 resume、可 recover、可判定兼容性

### 14.3 第二阶段：交互与执行语义统一

目标：

- 把 CLI、PowerShell、control API 的动作面统一

重点：

- Intent / Command / Event / Task / Approval / Artifact 语义统一：把意图、命令、事件、任务、审批和工件统一成一套动作模型
- pause / resume / reject / recover 语义统一：暂停、继续、拒绝和恢复的动作边界不再因 lane 不同而变化

退出条件：

- 操作员能用一致心智模型理解和操作三条 lane

### 14.4 第三阶段：团队编排层产品化

目标：

- 明确 persistent team 的默认模型

重点：

- hybrid 默认：专家角色优先在 leader 侧 burst，执行角色优先进入 durable lane
- homogeneous durable workers：默认以同质 worker 为主，而不是全异构常驻团队
- mixed compose opt-in：异构 persistent compose 只作为高级显式开启模式
- ownership / converge / escalation 语义：明确归属、收敛和人工升级规则

退出条件：

- 并行、合流、人工升级路径具备明确 owner 和 converge 机制

### 14.5 第四阶段：质量门、回归门、安全加固

目标：

- 在放大自动化能力前，先补 runtime gate 与 regression gate

重点：

- runtime QA gate：运行时质量门，阻止明显不该继续的执行继续
- promptfoo regression：用 promptfoo 做离线评测与回归门
- approval / audit / secret / policy hardening：审批、审计、秘密和策略加固

退出条件：

- 高风险动作不可绕过 gate
- 新版本可对比，且退化可量化

### 14.6 第五阶段：记忆、上下文增强与向量层

目标：

- 在 durable core 稳定后，再引入 memory 和 retrieval 增强

重点：

- structured memory store：结构化长期记忆存储
- QMD local lookup：本地 authority/spec/docs 的优先检索层
- optional embedding provider：可插拔 embedding 提供者
- optional vector substrate：可插拔向量检索底层

退出条件：

- memory 不污染 state
- retrieval 不取代 durable truth

### 14.7 第六阶段：本地 GUI 控制中心

目标：

- 提供 observer-first / guarded-actions-only operator surface

重点：

- PySide6 desktop shell：本地桌面控制中心壳层
- inspect / approval / recovery / replay / cost panels：检查、审批、恢复、回放和成本面板
- GUI 与 CLI 共用 action contract：GUI 不自建第二套动作语义

退出条件：

- 个人开发者在不读源码情况下可恢复大多数活动线程

## 15. 风险、反模式与防跑偏规则

最危险的跑偏方向包括：

- 把 LangGraph 写成全栈替代层
- 把 `subagent` 偷偷持久化成 worker
- 把 `native_omx` 降级成“旧后端”
- 把 long-term memory 当成 workflow state
- 把 vector layer 当成 durable truth
- 先做重型 GUI，再补恢复面
- 没有 regression gate 就扩大自动化
- 让 GUI 成为第二套真控制面

必须长期坚持的规则是：

- additive-only：新能力只能做增量扩展，不能改写旧语义
- observer-first：先做只读观察，再做写入和执行动作
- guarded-actions-only：高风险动作必须进入受控动作模型
- leader-owned final integration：最终 fan-in、最终集成和最终批准都归 leader
- one durable task, one backend family：一项持久化任务只使用一个后端家族

## 16. 与 OpenSpec / 治理文档的关系

本方案的层级是：

- 白皮书之下
- OpenSpec 具体变更之前
- startup / governance / implementation plan 的桥接层

在权威边界上，应长期区分：

| 权威层 | 主要负责 |
| --- | --- |
| 白皮书 | 总方法论、总目标态、十层框架 |
| `docs_bilingual/governance/` | 稳定用户级规则、共享运行时规则、长期 policy、权威边界 |
| 当前 implementation plan | 兼顾用户级与项目级的共享实施方案，解释多项目如何共用、当前仓库如何承接 |
| OpenSpec proposal / design / spec / tasks | 当前仓库的结构性实现变更、迁移步骤、任务拆分与验收 |

本方案负责：

- 解释可供所有 `PyCharm / Codex CLI` 项目共用的目标态架构
- 解释用户级、跨项目共享层和项目级的分工
- 解释当前仓库如何承接这套共享方案
- 解释实施顺序
- 解释工具复用边界

本方案不替代：

- 白皮书总方法论
- governance authority
- OpenSpec proposal / design / spec / tasks

任何触及以下内容的多文件改动，都应进入 OpenSpec 主线：

- 控制面
- 审批面
- 恢复面
- 记忆面
- 向量面
- GUI 面

## 17. 当前主线与后续增量队列

在该目标假设基线下，建议的后续主线切分为：

1. `sync-langgraph-production-grade-narrative-and-status` - proposed follow-up mainline for aligning narrative and status with production-grade goals.
2. `stabilize-langgraph-runtime-contracts-for-solo-production-operations` - proposed follow-up mainline for hardening runtime contracts for solo operation.
3. `unify-operator-control-surfaces-for-inspect-approval-recovery` - proposed follow-up mainline for one inspect, approval, and recovery surface.
4. `add-runtime-quality-regression-and-security-gates` - proposed follow-up mainline for quality, regression, and security gates.
5. `extend-memory-and-context-governance-after-core-stabilizes` - proposed follow-up mainline for adding governed memory and context after core stability.
6. `add-minimal-local-gui-control-center-after-operator-surface-stabilizes` - proposed follow-up mainline for a minimal local GUI after operator surfaces stabilize.

优先级判断：

- 先修叙事和恢复面
- 再修控制面和回归门
- 最后才重投 GUI 和向量层

## 18. 当前决策

本方案当前固定以下决策：

- `subagent` 保持 leader-side expert lane
- `native_omx` 保持 worker-centric durable lane
- `langgraph` 作为 graph-native persistent team kernel
- `SQLite` 作为优先 durable metadata / audit substrate
- `QMD` 作为优先 local lookup sidecar
- `promptfoo` 作为优先 regression/eval harness
- `PySide6` 作为后手控制中心实现
- `Redis`、`jina-embeddings` 仅在明确需要时引入
- `ClawTeam-OpenClaw`、`OpenViking`、`lossless-claw-enhanced` 仅借鉴设计，不直接并入主线
- `Light Judge`、`memory-lancedb-pro-skill` 不进入主线依赖
