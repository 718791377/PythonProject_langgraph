## ADDED Requirements

### Requirement: 仓库必须提供一个 additive 的 LangGraph 持久化编排 backend
仓库必须提供一个基于 LangGraph 的持久化编排 backend，并把它接到现有 Codex / oh-my-codex leader 工作流之下，而不是替换该工作流。

该 backend 必须保持：

- 当前主 Codex CLI 会话仍是 leader
- oh-my-codex 仍是用户级控制层和工作流层
- LangGraph 只是 selected long-running task 的持久化编排内核

#### Scenario: 操作员选择 LangGraph backend
- **WHEN** 操作员启用 LangGraph durable orchestration backend
- **THEN** 工作流必须保持当前主 Codex CLI 会话作为 leader
- **AND** 不得把 LangGraph 重新定义成 Codex 本身的替代品

### Requirement: LangGraph backend 必须持久化 repo-local threads 与 checkpoints
LangGraph backend 必须通过 repo-local thread identity 和 checkpoints 持久化执行流。

至少要求：

- 每个 durable execution 都使用稳定的 `thread_id`
- `thread_id` 必须包含 repository、worktree identity 和 task identifier
- checkpoint 数据必须能从 repo-local `.omx` 状态中被重新发现

#### Scenario: 一个长运行任务被恢复
- **WHEN** 操作员恢复一个此前已经启动的 LangGraph 编排任务
- **THEN** backend 必须通过稳定的 repo-local identity 找到现有 thread
- **AND** 它必须从持久化 checkpoint 状态继续，而不是从头重跑

### Requirement: LangGraph backend 必须用 root graph 镜像七阶段开发流
LangGraph backend 必须提供一个 root graph，并镜像 durable team 工作流中的阶段：

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

#### Scenario: 图状态从 planning 进入 execution
- **WHEN** 任务已经冻结计划，并且有足够的执行切片值得 durable execution
- **THEN** root graph 必须能从 `freeze-plan` 过渡到 `execute-parallel`
- **AND** 它必须把当前 phase 持久化进图状态

### Requirement: 研究到实现交接必须持久化为冻结后的 implementation brief
LangGraph durable flow 必须把研究输出持久化为冻结后的 implementation brief，而不是直接带着完整开放式研究上下文进入实现。

该 brief 至少必须包含这些结构化字段：

- objective
- non-goals
- accepted decisions
- constraints
- ownership boundaries
- acceptance criteria

在 brief 冻结后，实现必须从 fresh implementation context 重新开始。

#### Scenario: 开放式研究转入实现
- **WHEN** research 和 planning 已经产出批准后的 implementation brief
- **THEN** 工作流必须先持久化该 brief，再进入 durable execution
- **AND** 实现路径必须从 fresh execution context 启动，而不是继续复用完整研究上下文

### Requirement: 对抗式 bug 评审必须持久化 survivor queue，而不是 triad 常驻化
LangGraph durable flow 必须让 `bug-finder`、`bug-rebutter`、`bug-judge` 保持为 bursty review roles。

真正被持久化的对象必须是 judge 保留的 survivor queue，以及它们后续的 ownership 和验证状态。

#### Scenario: 争议性 bug 评审把结果送入 debugger lane
- **WHEN** 对抗式 bug 评审产出 judge 保留的幸存项
- **THEN** 工作流必须把这些幸存项持久化为 repair queue
- **AND** 不得要求 `bug-finder`、`bug-rebutter`、`bug-judge` 变成默认常驻 worker

### Requirement: LangGraph backend 必须支持 interrupts 和 operator 驱动的 resume
该 durable orchestration backend 必须支持人工审批点的 interrupt，并能在之后从持久化状态 resume。

第一版至少必须支持这些 interruptable approval points：

- plan freeze
- risky stabilize decisions
- failed final verification

#### Scenario: plan-freeze 审批点暂停图执行
- **WHEN** 工作流走到 plan-freeze approval point
- **THEN** 图必须能够 interrupt，并把待审批状态暴露给 operator
- **AND** operator 必须能够在批准后 resume 同一条 thread
