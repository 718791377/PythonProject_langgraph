## Why

当前的 Codex / oh-my-codex 持久化工作流已经具备 leader 侧原生 subagent、同构持久 worker 团队、启动路由和 repo-local 运行态隔离，但它仍然缺少一个真正的“持久化编排内核”，无法优雅承接长运行多步骤执行、checkpoint、interrupt 和可恢复图状态。LangGraph 现在正适合补这个缺口，因为它本身就明确强调 long-running、stateful workflow、persistence、interrupts、subgraphs 和 durable execution。

## What Changes

- 新增一个基于 LangGraph 的持久化编排 backend，并把它接到现有 `Codex CLI + oh-my-codex` 工作流下面，而不是替换现有体系。
- 保持 `Codex CLI` 作为 leader 和最终集成者，保持专家角色为短突发调用，把 LangGraph 作为长运行执行流的持久化编排内核。
- 定义一个与现有开发节奏一致的七阶段 root graph，并使用 research / planning / execution / verification / stabilization 子图。
- 把“研究到实现”的交接持久化为冻结后的 implementation brief，并要求实现阶段从一个全新的执行上下文继续，而不是复用开放式研究上下文。
- 把对抗式 bug 评审持久化为 `bug-judge` 保留的 survivor queue，由持久化 debugger lane 消费，而不是把 `bug-finder / bug-rebutter / bug-judge` 变成默认常驻 worker。
- 为 LangGraph thread、checkpoint、interrupt、store 数据和 backend 元信息定义 repo-local `.omx` bridge 规则。
- 增加用户级控制面与入口脚本，让 operator 能显式选择 durable orchestration backend，并检查 LangGraph thread 状态与恢复能力。

## Capabilities

### New Capabilities
- `langgraph-durable-orchestration-backend`：把 LangGraph 作为持久化编排 backend 接入现有 Codex / oh-my-codex leader 模型，覆盖 graph persistence、interrupts、subgraphs、研究交接、对抗式评审幸存队列以及 `.omx` bridge 规则

### Modified Capabilities
- `codex-user-level-team-mode-controls`：把 durable orchestration backend 选择与 LangGraph 运行态表面加入生成出来的用户级控制面
- `codex-user-level-team-mode-team-entrypoints`：增加 LangGraph 的 run/status/resume/inspect 入口以及相应的 playbook 指南
- `codex-user-level-team-mode-automatic-team-routing`：当 durable backend 选择为 LangGraph 时，允许自动 durable routing 选择 LangGraph 路径

## Impact

- impact_scope:
  - 用户级 Codex / oh-my-codex 控制资产
  - `.omx` 下的持久化编排运行态与状态布局
  - 生成出来的 playbook 与 operator 入口脚本
  - controls / entrypoints / automatic durable routing 相关 OpenSpec spec
- explicit_non_goals:
  - 不替换原生 `codex`、`codex.cmd`、`codex.ps1`
  - 不移除当前 `omx team` backend
  - 不把 mixed persistent panes 变成默认拓扑
  - 不引入 WSL2 依赖
  - 不把专家角色变成默认常驻 worker
- rollout_sequence:
  - 先定义 proposal、design 和 spec 合同
  - 再增加 backend 选择控制面与 LangGraph 运行态布局
  - 再增加 LangGraph run/status/resume/inspect 入口
  - 再增加 LangGraph MVP backend 与 graph 骨架
  - 最后验证 interrupt/resume、thread persistence、研究 brief 持久化和 survivor queue 流
- rollback_plan:
  - LangGraph 集成保持 additive，并且可通过 backend 选择器关闭
  - 保留当前直接 `omx team` 路径作为回滚安全兜底
  - 如果 LangGraph 编排失败或尚未成熟，则把 backend selector 切回当前原生 durable 路径
- validation_path:
  - 运行 `openspec validate --all`
  - 验证生成控制面和 backend-selector 状态输出
  - 验证一个 LangGraph thread 的持久化与重启后恢复
  - 验证 interrupt -> 人工确认 -> resume
  - 验证 research brief 持久化和 fresh execution-context restart
  - 验证对抗式 bug survivor queue 如何进入 debugger lane
- mainline_classification:
  - 属于 existing mainline continuation
  - 更具体地说，是 Codex / oh-my-codex team-mode 主线下的 durable-orchestration backend expansion
