# Codex 用户级 Orchestration Activation Policy

## 目的

定义 Codex CLI 的可复用用户级 orchestration-activation policy，使 orchestration 能跨新旧任务流被重新检查、retrofit 并被实际采用。

## 要求

### Requirement: 用户级安装必须暴露 orchestration-activation policy

用户级安装必须为 Codex CLI 暴露一套可复用的 orchestration-activation policy。

该 policy 必须定义：

- activation 是面向当前任务流的
- activation 不能只限制在新项目或新会话
- 哪些事件必须触发 activation re-check
- 什么属于硬路由指令
- 当 activation thresholds 命中且没有 blocker 时，Codex CLI 必须做什么

#### Scenario: 操作员检查用户级 activation policy

- **WHEN** 操作员检查用户级 orchestration policy surfaces
- **THEN** 他必须能够识别 activation posture、re-check triggers、hard directives 和 retrofit rules
- **AND** 不应只能通过 repository-local 项目文档去推断这些规则

### Requirement: prompt-independent collaboration parity 必须由 checker 背书

仓库必须提供 `tools/check_orchestration_collaboration_evidenceguard.py`，用 fixture pairs 证明相同任务在有无协作短语时得到相同 routing decision。该 checker 还必须校验 cold-start read-order evidence、durable/persistent evidenceguard records、structured expert lifecycle audit events 与 LangGraph state release evidence。

durable/persistent evidenceguard 必须拒绝缺少 active selector、backend family、preflight、ownership plan、manifest 或 LangGraph thread state、heartbeat、close 与 leader absorption evidence 的 selected、running 或 complete team 声明。LangGraph state release 必须拒绝已完成任务仍残留 stale `running`，除非写入 `completed_at`、`final_phase`、`result_summary` 与 `released_by`。

#### Scenario: 检查 prompt-independent collaboration parity evidence

- **WHEN** evidenceguard 校验 prompt-independent collaboration fixtures
- **THEN** 有协作短语和无协作短语的 paired cases 必须在相同 task shape 下产生相同 route fields
- **AND** 缺少 frozen-plan 或 slice thresholds 的显式 `omx` / `LangGraph` directive 必须报告具名 blocker 或未满足阈值
- **AND** routing reason 不得使用 missing user reminders

#### Scenario: 检查 durable 与 LangGraph 完成证据

- **WHEN** 已保存的 durable/persistent 或 LangGraph evidence 被检查
- **THEN** 缺少 selector、manifest 或 thread-state、heartbeat、close、leader absorption evidence 的 durable/persistent team 声明必须失败
- **AND** 完成后的 LangGraph task 若仍是 `running` 且缺少 release fields，必须失败

### Requirement: 既有项目和既有会话必须保持 orchestration-retrofit 能力

用户级 orchestration policy 必须支持以下 retrofit：

- 既有项目中的新会话
- 既有 live session 在 reload、restart、用户显式路由指令或 tracked durable-state detection 之后

#### Scenario: 既有 live session 被用户明确要求使用 `omx`

- **WHEN** 用户明确要求 Codex CLI 使用 `omx`
- **THEN** Codex CLI 必须把该指令视为硬路由指令
- **AND** 除非存在具体 blocker，否则必须采用对应 orchestration path
- **AND** 如果没有采用该 orchestration path，就必须解释具体 blocker
