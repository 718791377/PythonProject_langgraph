---
doc_id: openspec_usage_convention
lang: zh-CN
canonical: docs_bilingual/governance/openspec_usage_convention.md
translation_of: docs_bilingual/governance/openspec_usage_convention.md
doc_class: governance
status: active
---

# OpenSpec 使用约定

## 0. OpenSpec 治理对齐说明

本文档继续承担仓库内 OpenSpec 日常使用约定的治理说明职责。

关于文档分层与 OpenSpec 双语治理的可复用权威形态，现由下列主干 spec 承接：
`openspec/specs/documentation-layering-and-bilingual-openspec-governance/spec.md`

关于共享 runtime guardrails、runtime-state 命名标准以及项目级 official upstream-source baselines 的可复用权威形态，现由下列 OpenSpec change 承接：
`openspec/changes/runtime-guardrails-and-official-source-baselines/`

关于官方 OpenSpec 权威顺序、bootstrap refresh 以及仓库级 enforcement surfaces 的仓库本地权威形态，现由下列治理文档承接：
`docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md`

这种承接不替代本文档。本文档继续作为仓库实践、rollout discipline 和面向操作解释的 companion 文档。

## 1. 目的

本文用于定义当前仓库内 OpenSpec 的项目级使用约定。

对本仓库而言，OpenSpec 治理还必须额外带上一条边界：

- 用户级共享 runtime 与控制面可以被同一台机器上的多个 `PyCharm / Codex CLI` 项目复用
- 本仓库继续作为项目级承接层，负责 repo-local source、repo-local durable state 与仓库级结构变更
- repo-local durable truth 不得被上提到用户级共享运行时或用户级 state 目录

## 1A. 新会话统一入口规则

新会话默认不应把本文作为第一读取入口。

应先读取以下两份项目级启动摘要：

- [project_startup_summary.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.zh-CN.md)
- [project_startup_summary.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.md)

之后再由模型根据当前任务判断是否需要进入本文。

## 1B. 官方工作流与强制面

当问题涉及以下任一方面时，应读取：

- [openspec_official_workflow_policy.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md)

包括：

- 官方 OpenSpec 权威顺序
- bootstrap 或 refresh 行为
- 仓库级 guard、hook 或 CI 强制面

本文继续承担仓库实践和文档边界 companion 的角色，不替代官方工作流策略。

## 2. 当前已部署状态

OpenSpec 已经在仓库内完成部署并可使用，当前目标不是重新初始化，而是形成持续、规范的日常使用方式。

## 3. 适用范围

本约定适用于：

- 项目级 OpenSpec 使用方式
- Spec、实施方案、治理文档之间的分工
- 共享用户级表面与 repo-local source-of-truth 之间的项目级承接边界
- 实施前确认规则
- 通用经验升级进入 Spec 的标准

## 4. 实施前确认规则

### 4.1 先文档，后实施

实施前必须先把持久化决策记录清楚，再进入 runtime 或代码变更：

1. 先更新最合适的既有 `docs_bilingual/` 文件；目录选择应根据 doc_class 和内容判断，而不是默认所有决策都进入 `implementation_plans/`。
2. 只有没有合适既有文件能够干净承载该决策时，才新建 `docs_bilingual/` 中英文文档对。
3. 再由 `docs_bilingual/` 决策判断是否需要派生更新 `openspec/` 或 `docs/`：OpenSpec 用于 durable capability/spec lifecycle 工作，`docs/` 只用于 Superpowers runtime artifacts 或 `docs/` 目录契约本身。
4. 不得仅仅因为更新了 `docs_bilingual/`，就机械创建 `openspec/` 或 `docs/` 文件。
5. 已确认 `/plan` 后进入非纯文档任务执行时，先把本地治理包按完整本地流程提交并合入本地 `main`，然后停在远端发布门，再等待后续命令进入代码或 runtime 实施。

对于已经确认的本地实施任务，本地治理包合入本地 `main` 前不需要再次询问用户确认。远端发布仍然是独立授权边界。

### 4.2 用户要求“加入或更新 Spec”时的处理方式

当用户要求加入或更新 Spec/文档时：

1. 先整理拟写入内容
2. 先确认内容是否已经足够完整
3. 然后再创建或更新目标文件

## 5. 通用经验进入 Spec 的标准

只有满足以下条件的内容，才适合进入稳定通用 Spec：

- 不依赖某一条临时任务
- 不绑定某一次运行或编号
- 不只适用于单个实现细节
- 对后续维护和排查有长期价值

## 6. 与现有文档的分工

### 6.1 OpenSpec

OpenSpec 负责承载长期可复用规则、通用架构边界和稳定 change 结构。

凡是跨主线、长期稳定、可复用、并且预期在执行时应作为权威依据的项目级规则，都应优先提升到 OpenSpec。

这也包括：本仓库如何承接用户级共享 runtime / control surface，同时继续把 repo-local source 与 repo-local durable truth 保持为项目级权威面。

### 6.2 实施方案文档

实施方案负责承载当前主线、阶段推进、瓶颈、当前 rollout 细节。

### 6.2A 启动摘要

`project_startup_summary.*` 只负责稳定的项目启动入口内容：

- 启动铁律
- 项目级概览
- 主线一句话状态
- 阅读顺序指引

它不应膨胀成详细的运行中进度账本。

### 6.2B Memory 文档

`docs_bilingual/memory/` 负责承载会话级和主线级的活动进度，包括：

- 最新结论
- 当前阻塞点
- 未闭合分支
- 下一步验证目标

Memory 文档用于衔接会话，但不替代 OpenSpec 权威层。

### 6.3 经验总表

经验总表负责承载后续可能再升级进 Spec 的可复用经验教训。

### 6.4 治理与运行文档

治理与运行文档继续保留各自权威地位，不应为了“Spec 化”而把所有内容强塞进 `openspec/specs`。

治理文档负责定义文档分层边界、提升标准、双语维护规则以及跨层同步规则。

运维手册负责面向用户和操作者的说明，不替代 spec。

### 6.4A 与功能验证工作流的关系

项目级功能验证工作流仍然是一份独立的执行层 companion 文档，而不是 OpenSpec 使用治理本身的一部分。

当工作需要以下能力时，应使用：

- `docs_bilingual/operations/feature_validation_workflow.zh-CN.md` - 功能切片验证与结构化验证报告的中文运维指南。

包括：

- 功能切片识别
- 针对性验证选择
- 结构化结果、缺口与下一步汇总

OpenSpec 与 OPSX 负责定义结构性工作如何提出、实施、验证与提升。

功能验证工作流负责定义：当结构性或多切片变更已经发生时，如何诚实地验证这条变更。

两者是互补关系：

- OpenSpec / OPSX 负责结构化 change 流程与 artifact 权威层
- `feature_validation_workflow.*` 负责仓库级验证执行与结果汇总纪律

两者不得互相静默替代。

## 7. 当前优先建议纳入 OpenSpec 的主题

当前最适合纳入 OpenSpec 的主题包括：

- agent 架构
- 归一化判断与轻量模型辅助
- 候选结果选择与在线纠偏
- 官方 sub-agent rollout 分支

## 7A. 强制性首选闭环规则

对后续仓库工作，现在有一条必须遵守的治理规则：

- 只要某个问题在 direct rule 或简单确定性检查之后仍然需要多条件判断，维护者就必须先在下列受治理闭环方案之间做选择

这两条方案是：

- `candidate pool + 归一化 + 有界轻量模型灰区判定` - 用于有界灰区选择或仲裁的受治理闭环模式。
- `candidate pool + 归一化 + 有界轻量模型灰区判定 + 在线纠偏 + 样本沉淀` - 用于重复漂移、后续纠偏和可复用样本沉淀的受治理闭环模式。

对有界灰区选择或仲裁，必须先用较短方案。

对预期会重复漂移、后续需要纠偏、或样本沉淀有价值的问题，必须先用完整方案。

在这些受治理方案被考虑之前，维护者不得默认退回：

- prompt-only heuristic
- 一次性局部 patch
- 绕过共享闭环术语的临时 ad hoc 说法

## 8. 验收口径

当以下条件都成立时，OpenSpec 相关工作才算结构性完成：

- change / spec 文档彼此一致
- 验证完成
- 相关实施方案或治理文档已经同步

## 8A. OpenSpec 双语权威规则

项目级 OpenSpec 工件应遵循双语权威规则：

- 英文 ASCII 工件为主
- 中文工件为对照翻译
- 更新顺序为先英文、后中文

这条规则适用于所有从 `docs_bilingual/` 提升进入 OpenSpec 的可复用规则。

## 9. 当前建议

在当前仓库中，应把 OpenSpec 作为稳定规范层和 change 管理层，同时把动态实施细节继续放在专门的实施方案文档中。

## 10. Child Sub-Agent 的 Prompt 治理

仓库中所有 child sub-agent 都应默认遵守统一的 prompt 完整性治理规则。

这包括：

- `Research child run` - 负责研究和证据收集的 child sub-agent 运行。
- `Judge child run` - 负责证据、就绪度和风险评审的 child sub-agent 运行。
- `Implement child run` - 负责执行实现任务的 child sub-agent 运行。
- 后续新增的定制化 child 角色

治理边界必须明确：

- prompt 完整性由 orchestrator 侧治理
- review-side child sub-agent 只 review 结果，不 review prompt 模板
- prompt review 不允许递归发展成 reviewer of reviewer

如果 prompt 不完整的主要原因来自用户侧信息缺失，系统必须用简洁、亲和、适合群聊的方式向用户补充确认，而不应直接暴露后台实现术语。

对于当前官方 sub-agent rollout 分支，这条 review-side 边界还必须继续保持显式：

- `prompt-governor` 只留在 orchestrator 内部治理层
- `prompt-governor` 绝不提升成 live official child 角色
- `Judge child run` 只负责输出、证据、readiness 与风险 review
- `Judge child run` 不得 review child prompt template 或 prompt-governor 指令

因此，当前 rollout 状态必须理解为：

- `Research child run`：当前唯一的 live official child target
- `Judge child run`：尚未 live-childize，仍以 evidence-only 或 replay-report 为主
- `Implement child run`：尚未 live-childize，仍以 evidence-only 或 replay-report 为主
- `prompt-governor`：仅 internal-only，且不进入 live official child rollout

当前 `sessions_spawn unknown method` 应继续归入 change-level runtime blocker 跟踪，而不是改写 stable architecture。

同理，后续像 `local` 这样的迁移，也不能只因为仓库代码与静态文档已经对齐官方 spawn semantics 就提前开始。必须先由 active gateway runtime 证明官方 spawn surface 已端到端可达。

## 11. 统一的泄露与串台术语约定

后续治理文档、实施方案和经验沉淀中，只要涉及泄露或串台问题，默认使用经验总表里定义的共享术语。

不要再临时创造彼此重叠的说法；如果已有术语适用，应优先使用：

- `self_leakage` - agent 自身隐藏上下文、指令或中间状态发生泄漏。
- `cross_talk` - 跨边界发生非预期信息混入的总称。
- `inter_agent_cross_talk` - 不同 agent 或 child run 之间发生串台。
- `cross_message_cross_talk` - 同一工作流中不同 message 之间发生串台。
- `cross_conversation_cross_talk` - 不同 conversation 或 session 之间发生串台。
- `misrouted_return` - 结果或回复被送到错误 recipient 或 route。
- `state_contamination` - runtime state 或 durable state 被无关上下文污染。
- `template_misapplication` - 错误 prompt、document 或 workflow template 被套用到任务上。
- `overflow_induced_leakage` - context overflow、截断或压缩导致的泄漏。

如果后续确实需要新增子类，应先判断它属于：

- 结果类型
- 串台子类
- 还是诱因标签

然后再决定是否扩展统一术语表。

## 12. 大并发可控、防串台、防泄露的项目级硬要求

后续所有 `user -> orchestrator -> sub-agent` 链路，都必须同时满足：

- 大并发可控
- 防串台
- 防泄露

防串台至少覆盖：

- `inter_agent_cross_talk` - 不同 agent 或 child run 之间发生串台。
- `cross_message_cross_talk` - 同一工作流中不同 message 之间发生串台。
- `cross_conversation_cross_talk` - 不同 conversation 或 session 之间发生串台。
- `misrouted_return` - 结果或回复被送到错误 recipient 或 route。
- `state_contamination` - runtime state 或 durable state 被无关上下文污染。
- `template_misapplication` - 错误 prompt、document 或 workflow template 被套用到任务上。

防泄露至少覆盖：

- `self_leakage` - agent 自身隐藏上下文、指令或中间状态发生泄漏。
- agent 间、消息间、会话间的内容误泄
- `overflow_induced_leakage` - context overflow、截断或压缩导致的泄漏。

以后验收不能只看“是否跑通”或“是否单次回复成功”。还必须看：

- 高并发下是否仍可控
- 是否防串台
- 是否防泄露

## 13. Runtime State 命名标准

在仓库继续增加更多渠道 agent 和 runtime 分支之前，runtime state 目录必须采用稳定、ASCII 化的命名规则。

统一格式为：

- `channel__agent_identity__runtime_role` - 组合 channel、稳定 agent 身份与 runtime role 的 runtime-state 目录命名模式。

这条规则的目的是避免后续在同一渠道下出现多个 agent 时继续混淆。

因此 runtime state 命名必须：

- 区分渠道
- 区分稳定的 agent 身份
- 区分 runtime 角色或功能
- 不得把 task id、message id 或会话级临时标识带进目录名

当前已有的泛名目录在过渡期可以继续作为迁移源存在，但后续标准化和新 agent onboarding 应把这套格式作为默认目标。

## 14. 历史外部 OpenClaw 参考源

以下链接仍可作为历史外部 OpenClaw 参考源，在需要做迁移说明或产品上下文对照时使用：

- `https://github.com/openclaw/openclaw` - 用于迁移和产品上下文对照的历史外部 OpenClaw 仓库参考。
- `https://docs.openclaw.ai/start/getting-started` - historical external OpenClaw references：getting-started 文档 URL，用于迁移和产品上下文对照。

但它们不再是本仓库当前编排主线的权威源。

它们只适用于：

- 早期 OpenClaw 产品假设的历史对照
- 迁移说明
- 明确位于本仓库 repo-local orchestration source-of-truth 之外的外部产品上下文核对

使用规则如下：

- GitHub 仓库仍是 OpenClaw 自身的外部官方仓库源
- 官方文档仍是 OpenClaw 自身的外部官方文档入口源
- 但这两处来源不得覆盖本仓库自己的 repo-local orchestration source、repo-local durable-state contract 与当前治理文档体系
- 这两处链接也不应被写成“仅适用于当前主线”的局部基准

## 15. 项目级 OpenSpec Sources

以下对象应视为整个项目的 OpenSpec sources：

- 官方 upstream baseline：
- `https://github.com/Fission-AI/OpenSpec` - 用作项目级 OpenSpec 对齐基线的官方 upstream OpenSpec 仓库。
- 项目本地 companion source：
- `D:\PythonProject_langgraph` - 本项目 OpenSpec 治理的本地 companion 仓库与事实来源。

后续涉及 OpenSpec 使用方式、术语对齐、change 结构、规范更新与升级判断时，应优先以上游官方仓库作为 authoritative baseline，而不是以分支级说明、局部方案或临时备注代替。

项目本地 companion source 可用于：

- 项目 onboarding
- 本地教学材料
- 仓库特定的 OpenSpec workflow explanation

同时：

- GitHub 仓库继续作为后续 OpenSpec 更新与对齐工作的官方 upstream source
- 本地 companion source 可以支持仓库实践、项目级承接规则与 onboarding，但不得把 upstream baseline 改写成分支级或任务级 authority

## 15A. 只读 OpenSpec-aware Control Layer

当某个仓库本地 control layer 被明确配置为只读时，它接入 OpenSpec 的方式应当是：

- 只读 authority reader
- consistency audit 与 phase routing advisor
- 执行后的 validation 与 feedback layer

它不应被视为：

- 仓库写入者
- OpenSpec 工件维护者
- 被委托的 write executor
- 代表仓库启动 write-capable executor 的发起层

推荐的工作顺序是：

1. 读取 stable OpenSpec authority
2. 读取 active changes
3. 读取 companion governance、methodology 与 implementation 文档
4. 读取 trace、log、worker-debug 等 runtime evidence
5. 为独立的 write-capable execution path 产出 routing、scope 与 acceptance guidance
6. 在执行完成后回到只读 control layer，做 alignment、synchronization 与 blocker movement validation

在本仓库中，实际写入工作应继续交给 PyCharm 或 Codex CLI 这类独立 execution path；只读 control layer 只承担 analysis、audit、validation 与 feedback。

## 16. 项目级 Skills 官方源

以下来源应视为整个项目的官方 skills 源：

- `https://github.com/openclaw/clawhub` - 用于 skills 发现上下文的官方 Clawhub 源仓库。
- `https://clawhub.ai/skills?sort=downloads&nonSuspicious=true` - 过滤为可下载 non-suspicious skills 的官方 Clawhub skills 目录页。
- Skillhub 商店安装源：
- `https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/skillhub.md` - 用作项目级 skills 安装参考的 Skillhub installer markdown 来源。

这些来源不改变现有治理规则：

- 可安装不等于 promotion
- 可获取不等于已获得 live 路由权

## 17. Skill 安装必须获得用户授权

本仓库中的任何 skill 安装都必须遵守项目级硬规则：

- 安装必须来自用户明确指令
- 执行安装前必须进行二次确认
- Codex 及其所有 agent 只能建议或推荐，不得自行安装

即使候选 skill 来自项目级官方 skills 源，这条规则也仍然成立。

## 18. 双语同批更新规则

当仓库中的权威工件已经同时存在英文版和中文版时，默认必须在同一批工作中一起更新两边内容。

默认做法是：

- 更新英文主版
- 在同一批工作中同步更新中文对照版
- 除非用户明确授权临时例外，否则不得只更新英文后就停止

在修改中文对照文件之前，必须先确认当前文件能够被正确读取，足以支持安全更新。

如果中文文件因为乱码、编码损坏或终端显示不可靠而无法安全解读：

- 不得继续在不可读文本上做增量补丁
- 必须先通过显式 UTF-8 路径重新读取
- 如有需要，先恢复或重建为可读基线
- 然后再进行本次中文更新

## 19. 中文与双语 Authority 的显式 UTF-8 读取规则

对于仓库中的中文或双语 authority 工件，维护者必须将“显式 UTF-8 读取”视为默认的一方证据读取路径，而不是仅在出问题后才使用的补救动作。

本规则适用于：

- `openspec/changes/*` 下的中文 companion
- `openspec/specs/*` 下的中文 companion
- `docs_bilingual/*` - 受显式 UTF-8 authority-read 规则覆盖的双语文档树。
- 其他主文本或 companion 文本为中文的仓库 authority 工件

在维护者断定某个中文或双语工件已经损坏、乱码或不可读之前，必须先：

1. 通过显式 UTF-8 路径重新读取该工件
2. 区分是源文件损坏，还是终端/控制台显示问题
3. 然后再判断问题究竟属于：
   - 源文件层
   - 读取路径层
   - 还是显示层

不得仅凭终端显示出来的乱码，就把它直接判定为仓库文件本身已经损坏。

理由：

- 中文 authority 文件可能本身存储正确，但受限 shell 或终端仍然会把它显示错。
- 先强制走显式 UTF-8 读取，可以避免误判并减少不必要的文档修复。
