## Context

Codex 用户级 team-mode 这条主线已经有一系列归档批次，分别落地了 controls、startup binding、team entrypoints、routing thresholds、burst-review roles、automatic durable-team routing、native Windows backend、worker breakaway lifecycle、startup leader protocol 以及 provider pacing。随后，仓库里的双语实施方案文档又进一步收紧了规则，明确了原生 Codex subagent 的定位、wrapped leader 路由和裸 Codex 默认行为的边界、custom agent TOML 的放置规则、并发上限以及写多型 fan-out 的安全约束。

当前真正的瓶颈已经不再是运行时能力，而是这些规则在可复用 spec 层还没有形成正式合同。现有 common specs 已经覆盖 controls、startup posture 和 routing thresholds，但仍未正式化以下内容：

- 原生 Codex subagent 作为显式 leader 编排基础能力的语义
- 原生 Codex subagent 与 durable `omx team` 之间的分层关系
- 通用用户级 agent TOML 与仓库级 agent TOML 的分层位置规则
- 独立 custom agent TOML 的最小 schema
- `agents.max_threads` 与 `agents.max_depth` 必须显式、可检查
- 写多型并行比读多型 fan-out 需要更严格的 ownership 与集成边界

相关利益方：

- 用户级 installer / wrapper 维护者
- routing-policy 与 startup 层维护者
- operator playbook 与文档维护者
- 未来会复用这套用户级 Codex / oh-my-codex 工作流的其他仓库

## Goals / Non-Goals

**Goals:**

- 把已经进入计划文档的新 native-subagent 规则提升成可复用的 OpenSpec requirements
- 防止未来 wrapper、playbook 和生成资产把裸 Codex 错写成“默认自动拉起 subagent”
- 为 native-subagent limit surface 和 custom-agent 放置边界建立正式控制面合同
- 正式定义“读多型 fan-out 可以优先使用，写多型并行必须加门”的路由策略边界
- 保持 native Codex base layer、wrapped native-routed mode 和 enhanced OMX mode 三者语义分离

**Non-Goals:**

- 不实现新的 durable-team backend 或 worker lifecycle 机制
- 不把 mixed persistent pane 变成默认形态
- 不替换原生 Codex 可执行入口，也不修改 OpenClaw runtime 配置
- 不把这条 change 扩展成泛化的多 agent 框架评估项目
- 不在合同与验证面尚未成型前就强行引入更大运行时行为变化

## Decisions

### Decision 1：新增一个 native-subagent boundary capability，而不是把所有内容塞进现有 spec

我们将新增 `codex-user-level-team-mode-native-subagent-boundaries` 这个 capability。

原因：

- 当前缺失的是一组横切但概念上高度一致的规则
- 它们同时涉及语义、配置边界、并发上限、执行安全规则与术语边界
- 如果全部硬塞进 `controls` 或 `routing-thresholds`，就会模糊“操作控制面”和“原生 subagent 合同”之间的边界

备选方案：

- 只给 `controls` 和 `routing-thresholds` 增补 delta requirement
- 否决原因：最终合同会继续碎片化，不利于后续跨仓库复用

### Decision 2：控制面变化继续保持 additive

我们只在“控制面本身发生变化”的地方扩展 `codex-user-level-team-mode-controls`，核心是加入受管 native-subagent limit surface，并继续保持 additive 资产模型。

原因：

- P0 已经明确了 additive control 的基本模式
- limit 管理属于控制面，而不属于 startup posture 或 worker 执行层
- 这样才能继续守住 native Codex base-layer 的安全边界

备选方案：

- 把 `agents.max_threads` 与 `agents.max_depth` 完全写进 routing policy 或 leader instructions
- 否决原因：并发上限不仅要在会话里生效，还必须让 operator 在会话外也能检查

### Decision 3：把自动专家路由定义为“leader 侧 overlay”，而不是“裸 Codex 默认行为”

我们将扩展 `codex-user-level-team-mode-routing-thresholds`，明确自动专家角色路由是 leader 侧策略，建立在原生 Codex subagent 之上，而不是原生 Codex 裸行为本身。

原因：

- 这与当前研究材料给出的产品边界一致
- 它能让 wrapped 行为继续保持诚实、可检查
- 它可以防止未来生成资产暗示“裸 Codex 会默认自动拉起角色”

备选方案：

- 把这类澄清只写进 startup-only spec
- 否决原因：这不只是首轮启动问题，而是整个可复用路由模型的语义边界

### Decision 4：agent TOML 采用“用户级 + 仓库级”分层，而不是只保留一个全局目录

我们会正式化以下分层规则：

- 跨仓库复用角色放在用户级 Codex home
- 仓库特化角色放在 `<repo>/.codex/agents/`
- 独立 custom agent TOML 至少定义 `name`、`description`、`developer_instructions`

原因：

- 这样既保留复用能力，又不会把仓库特化行为全部堆进同一个全局桶里
- 这也符合当前 operator 预期与计划文档里已经形成的“全局 / 仓库”分层思路

备选方案：

- 统一只允许用户级 agent 文件
- 否决原因：仓库本地特化本来就是原生 Codex 配置面的一部分

### Decision 5：写多型并行必须比读多型 fan-out 受到更严格约束

native-subagent 合同将显式要求：

- 优先把并行 fan-out 用在读多型或边界非常清晰的任务上
- 写多型多 agent 执行只有在 ownership 隔离、热点串行规则、以及 leader 最终集成都已定义时才成立

原因：

- 这同时符合产品研究材料与 long-running agent 方法论
- 它为后续所有路由和编排工作提供稳定安全边界

备选方案：

- 只要任务已经拆分，就把所有并行执行都视为同一等级
- 否决原因：这样会把 merge conflict 与最终集成风险严重低规格化

## Risks / Trade-offs

- [Risk] 新 capability 可能与现有 `controls` 和 `routing-thresholds` spec 产生概念重叠。 → Mitigation：把新 capability 仅用于原生 subagent 合同规则，把资产生成要求留在 `controls`，把策略语义留在 `routing-thresholds`。
- [Risk] operator 可能把 `codex-subagent-limits.ps1` 误解成一个范围很大的配置写工具。 → Mitigation：先明确该表面至少必须可检查；如果支持写入，也必须保持受限、增量和可回滚。
- [Risk] 术语边界看起来像“只是文档问题”，从而再次漂移。 → Mitigation：把 leader / playbook 生成资产也绑定到同一份合同，并通过 spec-backed acceptance 一起验证。
- [Risk] 写多型 gating 会让某些多 writer 实验看起来变慢。 → Mitigation：把规则写清楚，让实验只在 ownership 隔离已被正式化后 opt in，而不是靠漂移行为碰运气。

## Migration Plan

1. 先补 proposal、design 与 spec delta，正式化 native-subagent 合同。
2. 在后续实现步骤中，再去更新 installer、控制资产以及生成出来的 routing / playbook 资产。
3. 在至少一个测试仓库中验证 wrapped native-routed 启动、plain single-agent 启动、limit-surface 生成，以及 operator 指南的术语边界。
4. 如果受管 limit 写入表面不稳定，则先保留 inspection 路径，把写入能力后移，但不放松合同本身。

回滚策略：

- 只回滚实现阶段新增或修改的 additive installer 输出、生成文档与 routing-policy 表面
- 保持原生 Codex base layer 不变
- 不回滚与本次 contract-tightening 无关的既有 P0-P7 结果

## Open Questions

- 受管 limit surface 应该直接写回 Codex config，还是应当先保持 inspection-first，等 operator 验证更充分后再开放写入？
- 如果同名角色同时存在于用户级和仓库级目录，仓库本地 `.codex/agents/` 是否需要显式 precedence 规则？
- `OpenHands` 与归档后的 `OpenDevin` 术语边界，是否只保留在 operator 文档中，还是也应该进入生成出来的帮助文本？
