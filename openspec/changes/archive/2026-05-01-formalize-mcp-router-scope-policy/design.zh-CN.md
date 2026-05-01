## 上下文

MCP Router 是外部用户级应用状态。本仓库可以定义策略并提供 checker，但仓库 MR 不能直接修改用户的 MCP Router 数据库或 UI 配置。

因此 checker 分为两层：

1. 当 `C:\Users\lenovo\.codex\config.toml` 或显式 `--codex-config` 文件存在时，Codex 配置检查是阻塞项；`C:\Users\lenovo\.codex\config.toml` 是用户级 Codex 配置文件。
2. MCP Router 数据库检查默认报告 drift；当使用 `--strict-router-state` 时，checker 会把 drift 作为阻塞错误，用于本机审计。

## 决策

### Decision: Codex 专属 MCP 保持直连

`omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 继续作为 Codex 直连 MCP server，因为它们读取或写入 Codex 编排状态、项目记忆、代码智能上下文或 trace 数据。

### Decision: 共享 browser/design MCP 放入 Router

`chrome-devtools` 和 `pencil` 是跨客户端通用 MCP server。它们可以由 MCP Router 管理，并且不应同时在同一个用户级 profile 中作为 Codex 直连 entry 启用。

### Decision: Router 自引用属于 drift

`mcp-router` 或等价 Router 自引用 entry 不能出现在 MCP Router 管理的 server 列表中。Codex 只应保留 `mcp_router` entry；`mcp_router` 是 Codex 侧连接 MCP Router 的 bridge。

### Decision: checker 行为必须 CI-safe

当用户级 Codex 配置或 MCP Router 状态不存在时，checker 必须在 CI 中通过。缺失的用户级 runtime 文件应报告为 informational skip，而不是仓库失败。

## 风险

- MCP Router 数据库字段可能随应用版本变化。除非请求 strict 模式，否则 checker 会把不可读或未知 router 状态当作 warning。
- 禁用的 server 可能仍留在 MCP Router 历史记录中。当数据库暴露 `disabled` 字段时，checker 会区分 active drift 与 disabled residue。
- 当前 launcher 仍可能为 Codex 专属 MCP server 传递命令行 override。这是可接受的，因为策略要求这些 server 保持 Codex 直连。
