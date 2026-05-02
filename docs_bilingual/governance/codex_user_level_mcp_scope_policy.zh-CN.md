---
doc_id: codex_user_level_mcp_scope_policy
lang: zh-CN
doc_class: governance
status: active
---

# Codex 用户级 MCP 范围策略

## 1. 目的

本策略定义哪些 MCP server 由 Codex 直接使用，哪些 MCP server 可以保留在 MCP Router 中给非 Codex 客户端使用。

`MCP` 是 Model Context Protocol 的缩写，表示 Codex 和其他客户端使用的工具服务器协议。

`MCP Router` 是共享路由应用，可以把选定的 MCP server 暴露给 Trae、VS Code、PyCharm 或其他非 Codex 客户端。

`Codex` 是 OpenAI 编码代理客户端，在本仓库的编排工作流中作为 leader 使用。

## 2. 权限边界

使用以下边界规则：

```text
Codex direct tools stay direct.
MCP Router stays disabled for Codex by default.
```

这表示 Codex 默认不能通过 `mcp_router` bridge 访问浏览器、设计或编排工具。

`mcp_router` 是 Codex 侧 MCP server entry，用来让 Codex 连接到 MCP Router。

MCP Router 仍然可以服务非 Codex 客户端。MCP Router 的 server 列表不代表 Codex 能力，除非 Codex 显式启用 `mcp_router` bridge；本策略默认禁止这样做。

## 3. Codex 私有直连 MCP server

`omx_state` 是 oh-my-codex 的状态 MCP server，用来读取和写入 Codex mode 状态。

`omx_memory` 是 oh-my-codex 的记忆 MCP server，用来读取和写入 Codex 项目记忆与 notepad 数据。

`omx_code_intel` 是 oh-my-codex 的代码智能 MCP server，供 Codex 执行仓库诊断和代码搜索。

`omx_trace` 是 oh-my-codex 的 trace MCP server，用来检查 Codex agent-flow trace 数据。

当 oh-my-codex 层启用时，这些 Codex 私有 MCP server 必须在 Codex 用户级配置中保持直连启用。

这些 Codex 私有 MCP server 不能通过 MCP Router 暴露为供其他客户端使用的共享 server entry。

## 4. Codex 直连通用 MCP server

`chrome-devtools` 是浏览器调试 MCP server，用于浏览器页面、DOM 快照、截图、控制台数据和网络检查。

`pencil` 是设计 MCP server，用于 Pencil 设计文档、视觉变量、节点读取和导出。

Codex 必须通过 Codex 直连 MCP entry 使用 `chrome-devtools` 和 `pencil`，不能通过 `mcp_router` bridge 使用它们。

`C:\Users\lenovo\.codex\config.toml` 是本 Windows 机器上的用户级 Codex 配置文件，用来控制 Codex 的直连 MCP server entry。

当操作者希望 Codex 具备浏览器或设计能力时，`chrome-devtools` 和 `pencil` 的 Codex 直连 entry 应保持启用。

如果 MCP Router 也包含供 Trae、VS Code、PyCharm 或其他非 Codex 客户端使用的 `chrome-devtools` 或 `pencil`，该 Router 状态属于外部客户端状态，不算作 Codex 访问路径。

## 5. Codex 的 MCP Router bridge 规则

Codex 侧 `mcp_router` bridge 默认必须保持禁用或不存在。

Codex 正常启动时不能加载 MCP Router 的全量工具目录，因为 MCP Router 可能聚合很大的跨客户端工具列表，增加启动成本、工具选择噪声和 `/resume` 风险。

`tools/list` 是 MCP 方法，用来返回某个 MCP server 的工具名称、描述和输入 schema。即使每个工具本身有效，过大的 `tools/list` payload 也会消耗启动预算。

重新启用 Codex 侧 `mcp_router` bridge 需要未来另一个已批准的治理变更；该变更必须定义有边界的 Codex 专用 Router profile，并验证 `tools/list` 大小、resume 启动和直连 MCP fallback 行为。

## 6. Router 自引用规则

`mcp-router` 是 MCP Router 应用或包名称，不能被注册成由 MCP Router 自己管理的 server。

MCP Router 不能管理一个反过来指向 MCP Router 的 server entry，因为这会形成自引用，并可能造成递归路由、重复启动或混乱的工具暴露。

## 7. 高风险共享 server 规则

`windows-cli` 是 Windows shell MCP server，不能通过 MCP Router 暴露给 Codex。

SSH 管理 MCP server 是可以创建、更新或删除 SSH 连接记录的工具；默认不能通过 MCP Router 暴露给 Codex。

部署类 MCP server 是可以发布或修改远程基础设施的工具；没有任务级审批门禁时，不能通过 MCP Router 暴露给 Codex。

这些工具可以在操作者接受外部客户端风险时保留在 MCP Router 中供其他客户端使用。

## 8. 必需的 checker 行为

`tools/check_mcp_router_scope_policy.py` 是仓库内 checker，用来验证 Codex MCP 范围划分并报告 MCP Router drift。

当本地用户级文件存在时，checker 必须验证 Codex 直连启用了 `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`chrome-devtools` 和 `pencil`。

checker 必须验证 Codex 侧 `mcp_router` bridge 默认已禁用或不存在。

checker 必须把 MCP Router 中的 `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace`、`mcp-router` 或 `mcp_router` server 记录报告为 drift。

checker 不需要仅因为 MCP Router 为非 Codex 客户端包含 `chrome-devtools` 或 `pencil` 而失败；Codex 访问由 Codex 直连 entry 和禁用的 `mcp_router` bridge 控制。

默认 guard 路径可以把 MCP Router 数据库 drift 报告为 warning，因为 MCP Router 属于外部用户级应用状态。操作者需要审计本机实时状态时，可以用 strict 本地运行把该 drift 变为失败。

## 9. 历史 bridge 例外

`tools/mcp_router_scope_policy_exceptions.json` 是仓库拥有的 MCP scope exception registry，供 checker 使用。

早期的 `mcp-router-disabled-for-resume-stability` exception 记录了 Codex 侧 `mcp_router` bridge 启用时 `/resume` 不稳定。

该 exception 现在已解决，因为本策略将禁用 bridge 设为 Codex 默认规则。

除非未来另一个已批准的治理变更明确反转默认规则，并提供有边界的 Router profile 验证，否则不能重新激活该 exception。

## 10. 验证命令

修改本策略或 checker 后，运行以下命令：

```powershell
python tools/check_mcp_router_scope_policy.py --root . --json
python tools/run_openspec_guard.py --root . --json
git diff --check
```

`python tools/check_mcp_router_scope_policy.py --root . --json` 会运行 MCP 范围 checker，并输出机器可读的 JSON。

`python tools/run_openspec_guard.py --root . --json` 会运行仓库聚合 guard，覆盖 OpenSpec 和治理检查。

`git diff --check` 会在提交前检查 diff 是否存在空白字符问题。
