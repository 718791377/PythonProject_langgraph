# codex-template-implementation-plan-governance Delta 规格中文对照

## 目的
定义本仓库如何维护可复用项目模板的实施计划，避免复制 live runtime state，也避免混淆不同模板能力层级。

## 要求
### Requirement: 模板实施计划必须分离可复用模板意图和 live project state

可复用项目模板的实施计划必须描述预期生成项目行为、验证路径和回滚路径，不得把当前仓库会话、`.omx/state/`、active worktree claims、本地 runtime logs 或目标项目 dirty working tree 当作可复用模板事实。

#### 场景：模板计划提到 runtime state
- **WHEN** 计划讨论 `.omx/state/`、LangGraph runtime state、worktree claims、launcher payloads、MCP entries 或 Comet workflow evidence
- **THEN** 它必须说明该项是 reusable template artifact、generated-project local state surface，还是 current-session evidence
- **AND** 它不得要求未来项目复制当前 live state directories 或 active session records

### Requirement: General 与 General_2 模板计划必须保持不同能力层级

`PythonProject_General` 计划必须描述 fuller reusable Codex/OpenSpec/Comet governance template，可包含可选 oh-my-codex、native_omx、LangGraph compatibility source、MCP scope policy、launcher payload policy、local and remote gate parity 和 generated-project durable-state scaffolding。

`PythonProject_General_2` 计划必须只描述 local Git、OpenSpec、Superpowers governance 和 native Codex subagents 模板层级。它不得把 oh-my-codex、native_omx、LangGraph durable backend、remote CI/MR、remote publication 或 `.omx/state/` 描述为当前启用能力。

#### 场景：维护者比较两份计划
- **WHEN** 维护者并排阅读两份 implementation plans
- **THEN** `PythonProject_General` 必须可识别为 fuller governance template
- **AND** `PythonProject_General_2` 必须可识别为 local-only native-subagent template

### Requirement: Comet 引用必须标明 OpenSpec 与 Superpowers 治理边界

引用 `/comet` 或 Comet 的模板实施计划必须把 Comet 描述为 OpenSpec + Superpowers governance workflow：OpenSpec 负责 WHAT 和 lifecycle artifacts，Superpowers 负责 HOW 和 implementation practice，Comet 负责 phases 与 evidence 协调。这些引用不得把 Comet 当成 native subagent、oh-my-codex、native_omx、LangGraph 或 durable-team backend。

#### 场景：计划引入 Comet 术语
- **WHEN** 模板实施计划使用 `/comet`、Open、Design、Build、Verify、Archive、OpenSpec 或 Superpowers 等术语
- **THEN** 它必须解释这些术语在本地计划中的治理角色
- **AND** 它必须区分 subagent evidence、skills、profiles 和 durable backends

### Requirement: 模板计划重构必须 UTF-8 clean 且 decision complete

重构后的实施计划必须保存为 UTF-8，避免 mojibake 和 replacement-character markers，并包含足够决策，使未来 agent 不依赖历史聊天即可实施。至少必须说明 goal、non-goals、target capability tier、implementation sequence、validation commands、acceptance criteria 和 rollback path。

#### 场景：未来冷启动会话恢复模板工作
- **WHEN** 会话在没有原始聊天上下文的情况下打开重构后的 implementation plan
- **THEN** 会话必须能识别要实施什么、不实施什么、如何验证、如何回滚
- **AND** 计划不得要求复制损坏的终端输出或隐藏聊天上下文
