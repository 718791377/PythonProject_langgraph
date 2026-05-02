## Why / 为什么

Codex 默认不应消费 MCP Router 的聚合工具目录。最近 MCP Router diagnostics 显示 `tools/list` payload 很大，这会增加 Codex 启动成本、工具选择噪声和 `/resume` 风险。

Codex 仍然需要浏览器和设计能力，但应通过 `chrome-devtools` 和 `pencil` 的 Codex 直连 MCP entry 获得，而不是通过 Codex 侧 `mcp_router` bridge。

## What Changes / 变更内容

- 将 Codex 侧 `mcp_router` bridge 禁用固化为默认策略，不再作为临时 exception。
- 将 `chrome-devtools` 和 `pencil` 分类为 Codex 直连通用 MCP server。
- 保持 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 为 Codex 私有直连 MCP server。
- 更新 MCP scope checker，要求浏览器和设计工具使用 Codex 直连 entry，并在 Codex `mcp_router` bridge 被启用时失败。
- 将之前的 resume-stability bridge-disabled exception 标记为 resolved。

## Non-goals / 非目标

- 不修改 `C:\Users\lenovo\.codex\config.toml`；这是用户级 Codex 配置文件。
- 不删除或修改 MCP Router database state。
- 不阻止 MCP Router 服务 Trae、VS Code 或 PyCharm 等非 Codex 客户端。
