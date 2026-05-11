# 生命周期裁剪规则

本文定义如何为两种目标架构模式裁剪 12 层生命周期：

- Codex CLI 个人开发者生产级持久化团队：12 层主干 + 4 个虚拟部门 + 24 个责任域 + 18 个横切模块 + 48 个核心文档 + 12 个受治理 AI Agent + 12 本推荐书籍。
- 个人级生产级一人公司经营系统：12 层主干 + 5 个虚拟部门 + 30 个责任域 + 20 个横切模块 + 60 个核心文档 + 15 个受治理 AI Agent + 15 本推荐书籍 + 12 个最小启动文档。

本文是 `product_business_document_lifecycle.zh-CN.md`、`codex_durable_team_platform_build_lifecycle.zh-CN.md`、`codex_project_consumption_lifecycle.zh-CN.md` 和 `pmi_project_management_reference_map.zh-CN.md` 的治理叠加层。

本规则由本地 `Business Management/` 与 `PMP/` 综合支撑。本地参考资料已经按 PDF 每页、EPUB spine item 和 Markdown 全文读取；本文只记录仓库特定 operating rules，不复制源书正文。

## 裁剪原则

裁剪是按工作的风险和不确定性选择最小充分治理系统，不是从心智模型里删除层级。

所有工作仍然使用同一套 12 层地图。裁剪只决定：

- 哪些层级需要完整文档；
- 哪些层级可以用 canvas、issue、OpenSpec 工件或短 note 摘要；
- 哪些审批、检查、评审、发布、回滚证据和复盘必须存在；
- 是整个项目轻量，还是只有某个阶段、某个 gate 或某个模块轻量。

## 过程组式裁剪门

在打开大型文档栈、启动 durable workers、选择 LangGraph、发布 release，或判断一个小变更可以保持轻量之前，先使用这个 gate。

### 输入

- 目标模式：Codex 平台目标或一人公司目标。
- 工作类型：新产品、平台 runtime 变更、项目模板变更、纯文档更新、spike、实验、本地内部工具、客户可见变更、支付或信任影响变更、合规敏感变更、长期架构变更。
- 受影响的生命周期层级、责任域、横切模块、核心文档和受治理 Agent。
- 风险与不确定性：金钱、用户、信任、安全、隐私、法务合规、数据、可用性、成本、迁移、发布、回滚和干系人风险。
- 耦合：共享接口、runtime entrypoint、durable state、跨项目模板、公开 API 或下游项目依赖。
- 当前证据：来源综合、用户证据、指标、OpenSpec 状态、Git 状态、测试证据、运营事故和经验教训。
- 约束：时间预算、CI minutes、provider pacing budget、operator attention、模型/工具可用性和审批限制。

### 工具与技术

- 裁剪评分卡：把影响分类为完整、release slice、阶段局部轻量、模块级轻量或整个项目轻量。
- 风险与不确定性矩阵：区分高风险但清晰的交付工作，和高不确定性的发现工作。
- 预测式/适应式/混合式选择：清晰高风险交付使用预测式 gate；探索工作使用适应式 slice；发现后仍必须进入交付门的工作使用混合流。
- 范围边界评审：判断轻量化适用于整个项目、某个阶段、某个模块，还是某个文档 gate。
- 架构边界评审：检查依赖方向、数据 ownership、信任边界、接口稳定性、回滚路径和状态 ownership。
- 治理深度评审：选择需要的审批、OpenSpec 工件、本地 CI、本地 MR review、远端确认、release notes、rollback 和 retrospective。
- 升级评审：定义哪些信号会强制从轻量治理扩展到更完整治理。

### 输出

- 裁剪决策记录：完整架构、整个项目轻量、阶段局部轻量、模块级轻量，或混合模式。
- 当前范围的最小充分文档集。
- 明确列出展开的层级和摘要的层级。
- 必要审批、评审、验证、发布、回滚和复盘证据。
- 升级触发条件和负责重新裁剪的 owner。
- 继续、停止、做 spike、拆分范围或扩展治理的决策。

## 什么时候采用完整架构

只要出现以下任一触发条件，就对受影响范围采用完整架构：

- 工作是新产品、新商业 offer、重大业务转向或长期平台。
- 工作影响金钱、外部用户、客户承诺、支付、信任、安全、法务合规、隐私或受监管决策支持。
- 工作改变数据 ownership、durable state、持久化、secrets、权限、身份认证、授权或审计证据。
- 工作改变 runtime entrypoints、wrappers、launchers、MCP 放置、共享 helpers、项目模板、OpenSpec 治理、CI gates、release gates 或 rollback 行为。
- 工作创建或改变共享接口、API contract、跨项目模板、Agent 权限、durable-worker 行为或 graph checkpoints。
- 工作具有广泛采用影响、公开文档影响、客户支持影响或高回滚成本。
- 多个模块、团队、Agent、仓库或外部系统必须协调。

完整架构不等于立刻写满全部 48 或 60 个文档。它意味着 12 层全部被显式考虑，并且受影响层级获得完整证据、ownership、验证、发布、回滚和学习覆盖。

## 什么时候允许整个项目轻量

只有同时满足以下条件，才允许整个项目轻量：

- 项目是早期想法、私有 spike、本地学习练习或小型内部工具。
- 没有外部用户、客户承诺、收入承诺、支付流、法务合规暴露、生产数据、敏感数据或信任边界。
- 结果可逆或可丢弃。
- 不改变共享 runtime entrypoint、durable state、跨项目模板、公开 API、CI gate、release gate 或下游项目依赖。
- 一个 owner 能理解整个系统和回滚路径，不需要隐藏协调。

最小输出通常是短 canvas、范围说明、验收说明、验证说明和 lessons-learned note。如果修改代码，即使项目其他部分保持轻量，也必须保留技术和执行证据。

## 什么时候允许阶段局部轻量

当项目整体需要较完整治理，但某个阶段低风险或仍处于探索状态时，可以采用阶段局部轻量。

示例：

- 发现阶段可以先使用访谈笔记、机会地图和原型反馈，再冻结完整 PRD。
- 指标阶段可以先用简单北极星 note，再补 tracking plan 和 data dictionary。
- 增长阶段可以先做小型渠道测试，再判断是否需要完整增长 operating model。
- 复盘阶段在没有事故、客户影响或政策变化时，可以先用简短经验 note。

阶段局部轻量必须说明哪个阶段是轻量的、它触达哪些上游和下游层级，以及什么证据会触发扩展。

## 什么时候允许模块级轻量

在一个整体受完整治理的项目内部，如果某个模块边界清晰、可逆、低风险，可以采用模块级轻量。

允许示例：

- 完整平台 release 内的纯文档 appendix。
- 不改变 launcher 行为、共享状态、secrets 或 CI gates 的本地 helper script。
- 不发布、不面向客户、不耦合生产数据的原型 UI 组件。
- 为后续 MRD 或 strategy review 提供输入的非权威研究摘要。

模块级轻量必须保留完整项目的架构边界。轻量模块仍然需要 owner、scope boundary、validation note、rollback 或 deletion path，以及 learning note。

## 什么时候必须采用混合架构

当不确定性高，但最终交付风险也高时，采用混合路径。

混合流：

1. 先适应式启动：spike、prototype、discovery interview、document experiment 或 proof of concept。
2. 记录 spike 的轻量输入、工具与技术、输出。
3. 在 production change、platform publication、customer commitment、durable state change 或 remote release 前冻结预测式计划。
4. 先只展开受影响层级。
5. 如果耦合、采用、支持、合规或回滚风险变成系统性，再扩展到项目级完整治理。

对 AI 时代项目工作而言，如果任务开始时不清晰，但可能演化为真实平台、产品、客户、收入、信任或运营系统，默认使用混合方式。

## 升级触发条件

当以下任一情况出现时，从轻量治理升级到更完整治理：

- spike 变成 production code。
- 本地工具变成共享模板、launcher、CI gate 或 reusable helper。
- 文档 note 变成市场承诺、产品承诺、治理规则或 stable spec。
- 模块开始触达 secrets、identity、permissions、personal data、customer data、money、legal/compliance 或 release state。
- 单个 owner 已无法审查完整影响。
- 回滚变得昂贵、含糊或依赖外部方。
- 用户、客户、操作者或干系人反馈带来新义务。
- 重复事故或支持问题说明轻量路径已经不够。

升级应先扩展受影响的层级、阶段或模块。只有当耦合变成系统性时，才扩展整个项目。

## 按裁剪结果选择最小文档集

| 结果 | 最小充分文档或记录 |
| --- | --- |
| 整个项目轻量 | `project_canvas.md`、scope/non-goal note、validation note、owner note、lessons note |
| 阶段局部轻量 | 带输入 / 工具与技术 / 输出的阶段 note、dependency note、evidence trigger、next-gate decision |
| 模块级轻量 | module scope note、owner、boundary、validation、rollback 或 deletion path、learning note |
| 平台 release slice | OpenSpec proposal/design/tasks、触达层级说明、technical 和 organization evidence、test/release/rollback evidence、archive 和 lessons |
| 完整 Codex 平台架构 | 白皮书、MRD、北极星 Plan，以及面向受影响平台目标的战略/指标/产品/技术/组织/执行/增长/运营/复盘覆盖 |
| 完整一人公司架构 | 先用 12 个最小启动文档，再随着收入、客户、合规、交付和运营证据增长，扩展 BRD/MRD/strategy/metrics/product/technical/organization/execution/growth/operations/retrospective 文档 |

## Codex 平台裁剪

对 `D:\PythonProject_langgraph` 来说，凡是影响可复用编排行为、原生 subagent 路由、`native_omx`、LangGraph、worktree safety、OpenSpec governance、user-level launcher policy、skill/profile governance、local-main-first publication 或 shared templates 的变更，都需要对受影响范围采用完整架构。

普通纯文档 OpenSpec change 可以保持 release-slice 大小，但仍必须记录变更层级、来源证据、验证证据和归档证据。

不能只因为引用了完整架构就启动 durable team。durable team 启动仍然要求计划已冻结，并且至少存在两个基本独立的执行切片。

## 一人公司裁剪

对于下游一人公司经营系统，不要一开始创建全部 60 个文档。先从 12 个最小启动文档开始：

`company-thesis.md`、`business-model.md`、`offer.md`、`pricing.md`、`user-segments.md`、`growth-model.md`、`finance-model.md`、`ops-playbook.md`、`metrics.yaml`、`risk-register.md`、`agent-governance.md`、`monthly-review.md`。

当业务获得付费客户、重复交付、支持义务、财务复杂度、合规暴露、敏感数据、外部伙伴、重复事故，或低风险支持以外的 Agent 自动化时，再扩展到更完整治理。

## 裁剪复核节奏

在以下 gate 复核裁剪：

- 打开或扩展大型 OpenSpec change 之前；
- 承诺公开发布或客户可见发布之前；
- 启动 durable workers 或 graph orchestration 之前；
- 改变共享 runtime、durable state、secrets、permissions 或 release gates 之前；
- 事故、验证失败、重复支持问题或重大战略变化之后；
- retrospective closing 期间。

收尾输出应说明下一轮继续轻量、扩展某个层级/模块，还是回到更小的治理足迹。
