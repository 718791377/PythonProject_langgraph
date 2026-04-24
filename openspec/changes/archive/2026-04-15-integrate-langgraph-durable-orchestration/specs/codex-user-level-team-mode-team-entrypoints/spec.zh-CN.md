## ADDED Requirements

### Requirement: 安装器必须生成 LangGraph 持久化编排入口
安装器必须向目标 Codex home 生成 additive 的 LangGraph-oriented durable orchestration entrypoints。

生成出来的 LangGraph 资产至少必须包含以下 operator 表面：

- run / start
- status / inspect
- resume
- interrupt inspection

生成 playbook 必须说明这些 LangGraph 入口和现有 `omx team` 入口之间的关系。

#### Scenario: 操作员检查生成出来的 LangGraph 入口
- **WHEN** installer 把用户级 team-mode 资产渲染到目标 Codex home
- **THEN** 它必须在那里生成 additive 的 LangGraph entrypoint 资产
- **AND** 生成 playbook 必须解释它们如何与现有 `omx team` wrapper 共存
