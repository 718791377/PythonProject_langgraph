## ADDED Requirements

### Requirement: 生成控制面必须暴露 native-subagent 上限控制表面
用户级 installer 必须生成一个增量式控制资产，用于暴露这套工作流所使用的 native-subagent fan-out 上限。

该资产必须允许 operator 查看，并在受支持时管理，`agents.max_threads` 与 `agents.max_depth`，同时不得修改原生 `codex`、`codex.cmd`、`codex.ps1` 基础入口。

#### Scenario: installer 渲染增量上限控制面
- **WHEN** installer 把用户级 team-mode 资产渲染到目标 Codex home
- **THEN** 它必须生成 native-subagent 上限控制资产
- **AND** 该资产必须保持原生 Codex 基础入口不变
