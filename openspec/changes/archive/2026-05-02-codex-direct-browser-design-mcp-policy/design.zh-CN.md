## Design / 设计

该策略现在区分 Codex 直连能力和外部 MCP Router 状态：

- `CODEX_PRIVATE` 列出 oh-my-codex MCP server，这些 server 绝不能通过 MCP Router 路由。
- `CODEX_DIRECT_UTILITY` 列出浏览器和设计 MCP server，Codex 应直接使用这些 server。
- `mcp_router` 对 Codex 来说是 disabled-by-policy；启用该 bridge 是 checker error。
- MCP Router 仍可以为其他客户端包含浏览器或设计 server，但该状态不能满足 Codex 直连能力要求。

checker 保持只读。它只读取 Codex config 和 MCP Router database state 进行验证，不编辑用户级文件。
