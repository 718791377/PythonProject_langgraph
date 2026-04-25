## Context

当前用户级 Codex / oh-my-codex 工作流已经具备包装启动、leader 侧原生 subagent 路由、通过 `omx team` 的持久 worker 执行、原生 Windows durable-team backend 支持，以及 repo-local `.omx` 运行态隔离。但它还缺少一个图结构化的持久化编排内核，无法优雅承接 checkpoint 化长运行执行、interrupt/resume 审批点、持久化研究交接，以及持久化的对抗式评审幸存队列。

LangGraph 之所以适合，是因为它官方能力就集中在 long-running、stateful orchestration、persistence、interrupts、memory 和 subgraphs。这里的目标不是替换 Codex / oh-my-codex，而是把 LangGraph 作为下层 durable orchestration backend 接进现有体系。

## Goals / Non-Goals

**Goals:**

- 把 LangGraph 作为可选 durable orchestration backend 接进现有 Codex / oh-my-codex 工作流
- 保持 leader 侧原生 subagent 和同构持久 worker 默认形态不变
- 正式化七阶段 root graph 与可复用子图
- 持久化研究到实现交接与对抗式评审幸存队列
- 把 LangGraph 运行态桥接进现有 `.omx` 状态模型
- 让 backend 选择显式可见、可操作

**Non-Goals:**

- 不用 LangGraph 替换 Codex
- 不移除当前 direct `omx team` 路径
- 不把研究角色或 bug triad 做成默认常驻 worker
- 不把 mixed persistent pane 变成默认拓扑
- 第一版不要求 LangSmith Deployment、Agent Server 或云端基础设施

## Decisions

### Decision 1：LangGraph 是 backend augmentation，不是 platform replacement

LangGraph 放在现有 Codex / oh-my-codex 流程之下：

- Codex CLI 继续做 leader 和最终集成者
- oh-my-codex 继续做用户级控制层和工作流层
- LangGraph 负责 selected long-running task 的 durable orchestration

### Decision 2：第一版采用 Python sidecar service

第一版实现形态采用原生 Windows 下的 Python LangGraph sidecar，并通过 additive entrypoints 调用。

原因：

- LangGraph 官方 Python 面最直接对齐 persistence、interrupts 和 subgraphs
- 这样可以把 orchestration runtime 和 PowerShell wrapper 层分开
- 不需要把图状态硬塞进 leader 会话本身

### Decision 3：使用 repo-local thread identity 与 checkpoint storage

第一版 durable identity 模型采用 repo-local thread namespace，例如：

- `thread_id = <repo-hash>:<worktree-id>:<task-id>`

第一版 persistence backend 先走本地简单形态：

- SQLite checkpointer 或等价本地持久化
- 状态与元数据根目录放在 `.omx/state/langgraph/`

### Decision 4：root graph 直接镜像现有七阶段开发流

root graph 应直接采用已经稳定下来的七阶段：

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

条件边需要支持前期 burst、执行到 stabilize 的升级，以及 verify 失败后回 stabilize。

### Decision 5：用子图承载角色家族，而不是每个角色一个长驻图

第一版 LangGraph 设计优先做少量可复用子图：

- research subgraph
- planning subgraph
- execution subgraph
- verification subgraph
- adversarial-review subgraph

这与当前“执行持久化、专家突发化”的工作流一致，并避免把所有专家角色都做成长驻 durable worker。

### Decision 6：研究交接持久化的是对象，不是研究团队

研究结果应被持久化为冻结后的 implementation brief，至少包括：

- objective
- non-goals
- accepted decisions
- constraints
- interfaces
- ownership boundaries
- acceptance criteria
- validation plan

实现必须从新的实现上下文继续，而不是继续吃开放式研究历史。

### Decision 7：对抗式 bug 评审持久化的是 survivor queue，不是 triad 常驻化

`bug-finder`、`bug-rebutter`、`bug-judge` 继续保持 bursty expert call。

真正持久化的是：

- candidate 元数据
- judge survivor
- debugger lane ownership
- fix / verify 状态

持久化 debugger lane 可以存在，但 bug triad 本身不应成为默认常驻团队。

### Decision 8：`.omx` 继续是 repo-local runtime discovery 根目录

LangGraph 运行态不应另起一套完全独立的 repo-local root，而应桥接到现有 `.omx`：

- `.omx/state/langgraph/threads/`
- `.omx/state/langgraph/checkpoints/`
- `.omx/state/langgraph/interrupts/`
- `.omx/state/langgraph/store/`
- `.omx/state/langgraph/backend.json`

## Risks / Trade-offs

- [Risk] 两套 durable backend 会让 operator 混淆。 → Mitigation：增加显式 backend selector 和清晰 playbook 文案。
- [Risk] LangGraph persistence 与现有 `.omx` 状态发生双重真相。 → Mitigation：坚持 `.omx` 作为 runtime root，并定义唯一桥接合同。
- [Risk] 研究交接即使冻结，也可能仍然把太多噪声带进实现。 → Mitigation：要求冻结 brief，并强制 fresh execution context。
- [Risk] 对抗式评审如果把所有 candidate 都持久化，会迅速噪声化。 → Mitigation：默认只持久化 judge 保留下来的 survivor。
- [Risk] interrupt / resume 增加 operator 负担。 → Mitigation：只在 plan freeze、高风险 stabilize、最终验收失败这些明确节点 interrupt。

## Migration Plan

1. 先增加 backend 选择控制面 requirement。
2. 再增加 LangGraph-oriented entrypoints 和 playbook 规则。
3. 实现一个最小 Python sidecar，至少包含一个 root graph、本地 persistence 和 repo-local thread identity。
4. 再接 research brief persistence 和 fresh execution restart 边界。
5. 再接 adversarial-review survivor queue 和 debugger-lane 消费路径。
6. 最后验证 restart、resume、interrupt 与 cross-repository isolation。
7. 在 LangGraph 稳定前，始终保留当前 direct `omx team` 路径作为 fallback。

## Open Questions

- backend selector 应该是全局的、repo-local 的，还是两层都支持？
- 第一版 persistence backend 是否只允许 SQLite 文件模式，还是一开始就允许 Postgres 选项？
- 实现阶段应该是一任务一持久 thread，还是 root thread 下再分 per-slice execution threads？
- 第一版 LangGraph 是否只通过新入口暴露，还是也要接到现有 automatic durable routing helper？
