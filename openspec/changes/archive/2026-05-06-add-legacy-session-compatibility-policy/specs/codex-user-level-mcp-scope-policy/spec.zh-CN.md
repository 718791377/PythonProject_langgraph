## ADDED Requirements / 新增需求

### Requirement: Legacy Resume MCP Workarounds SHALL Be Scoped Per Invocation / 旧会话 Resume 的 MCP 绕过必须限定为单次启动

当某个陈旧旧 thread 无法干净启动时，旧会话必须把临时 per-invocation MCP override（单次启动 MCP 覆盖）限定在受影响的旧 thread 范围内。

per-invocation MCP override 是一次性的 Codex 配置覆盖，例如 `-c "mcp_servers.omx_code_intel.enabled=false"`。

此类覆盖不得被当成永久禁用 Codex 私有 MCP server 或默认编辑用户级 Codex 配置的授权。

#### Scenario: A legacy old thread fails on one direct MCP server / 某个旧 thread 因一个直连 MCP server 失败

- **GIVEN** 旧会话因为陈旧的 direct MCP startup state 失败
- **WHEN** 操作者继续该旧 thread
- **THEN** 可以仅对该次启动使用 per-invocation override 禁用受影响 server
- **AND** 新会话的 direct MCP policy 必须保持不变

#### Scenario: A new wrapped session starts normally / 新 wrapped session 正常启动

- **GIVEN** oh-my-codex 已为正常工作启用
- **WHEN** 新 wrapped session 启动
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`chrome-devtools` 和 `pencil` 必须继续受 direct Codex MCP policy 约束
- **AND** 旧会话 workaround 不得全局移除这些 server
