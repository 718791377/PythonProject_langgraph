# codex-user-level-mcp-scope-policy 规范

## 目的

定义用户级 MCP server 边界：哪些服务是 Codex 专属直连 MCP server，哪些服务是通过 MCP Router 管理的跨客户端通用 MCP server。

## ADDED Requirements

### Requirement: Codex 专属 MCP server 必须保持 Codex 直连

Codex 专属 MCP server 必须继续直接配置给 Codex，且不能通过 MCP Router 作为共享 server entry 管理。

Codex 专属 MCP server 包括 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace`；它们分别用于 Codex 状态、记忆、代码智能和 trace 数据。

#### Scenario: Codex 启动时启用了 oh-my-codex

- **WHEN** Codex 启动并启用 oh-my-codex 层
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 必须作为 Codex 直连 MCP server 可用
- **AND** 这些 server 不能被要求必须经过 MCP Router

#### Scenario: 审计 MCP Router

- **WHEN** 审计 MCP Router 管理的 server 记录
- **THEN** `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace` 的 active 记录必须被报告为 drift
- **AND** 操作者必须被提示将这些 server 保持为 Codex 专属

### Requirement: 共享通用 MCP server 可以由 MCP Router 管理

当多个客户端需要同一能力，且该 server 不拥有 Codex 编排状态时，跨客户端通用 MCP server 可以由 MCP Router 管理。

共享通用 MCP server 包括 `chrome-devtools` 和 `pencil`；它们分别用于浏览器调试和设计资料访问。

#### Scenario: 浏览器与设计 MCP server 被共享

- **WHEN** `chrome-devtools` 或 `pencil` 由 MCP Router 管理
- **THEN** 对应的 Codex 直连 server entry 必须禁用或不存在
- **AND** Codex 必须通过 MCP Router bridge 访问该能力

### Requirement: MCP Router 不能管理自己

MCP Router 不能包含 `mcp-router`、`mcp_router` 或其他 Router 自引用 managed server entry。

#### Scenario: 检测到 Router 自引用

- **WHEN** MCP Router 管理的 server 记录包含 `mcp-router` 或 `mcp_router`
- **THEN** checker 必须报告 self-reference drift
- **AND** 操作者必须移除或禁用该自引用 Router server entry

### Requirement: MCP 范围策略必须有脚本验证支撑

MCP 范围策略必须由可执行 checker 支撑，该 checker 能验证本地 Codex 配置并报告 MCP Router drift。

#### Scenario: 仓库 guard 在没有用户级 runtime 文件时运行

- **WHEN** 仓库 guard 在 CI 或其他没有用户级 Codex / MCP Router 文件的环境中运行
- **THEN** checker 必须用 informational output 跳过本地 runtime 验证
- **AND** guard 必须继续验证仓库拥有的策略工件

#### Scenario: 请求 strict 本地审计

- **WHEN** 操作者使用 strict Router-state 验证运行 checker
- **THEN** Codex 专属 server 的 active MCP Router 记录必须成为阻塞错误
- **AND** active Router 自引用记录也必须成为阻塞错误
