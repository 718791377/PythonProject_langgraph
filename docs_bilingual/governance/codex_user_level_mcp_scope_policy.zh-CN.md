---
doc_id: codex_user_level_mcp_scope_policy
lang: zh-CN
doc_class: governance
status: active
---

# Codex 用户级 MCP 范围策略

## 1. 目的

本策略定义哪些 MCP server 是 Codex 专属直连服务，哪些 MCP server 可以交给 MCP Router 统一管理，供多个客户端复用。

`MCP` 是 Model Context Protocol 的缩写，表示 Codex 和其他客户端使用的工具服务器协议。

`MCP Router` 是共享路由应用，用来把选定的 MCP server 暴露给 Codex、Trae、VS Code、PyCharm 等多个客户端。

`Codex` 是 OpenAI 编码代理客户端，在本仓库的编排工作流中作为 leader 使用。

## 2. 权限边界

使用以下边界规则：

```text
Codex orchestration truth stays Codex-dedicated.
Cross-client utility tools may go through MCP Router.
```

这条规则表示：Codex 编排事实必须留在 Codex 专属直连层；跨客户端通用工具可以通过 MCP Router 共享。

Codex 专属 MCP server 必须继续直接配置给 Codex，不能作为共享 MCP Router server 管理。

MCP Router 应只管理跨客户端通用 MCP server；这些服务不得拥有 Codex 会话状态、持久化编排状态、仓库本地事实，或需要审批保护的写权限。

## 3. Codex 专属 MCP server

`omx_state` 是 oh-my-codex 的状态 MCP server，用来读取和写入 Codex mode 状态。

`omx_memory` 是 oh-my-codex 的记忆 MCP server，用来读取和写入 Codex 项目记忆与 notepad 数据。

`omx_code_intel` 是 oh-my-codex 的代码智能 MCP server，供 Codex 执行仓库诊断和代码搜索。

`omx_trace` 是 oh-my-codex 的 trace MCP server，用来检查 Codex agent-flow trace 数据。

当 oh-my-codex 层启用时，这些 Codex 专属 MCP server 必须在 Codex 用户级配置中保持启用。

这些 Codex 专属 MCP server 不能通过 MCP Router 暴露为供其他客户端使用的共享 server entry。

## 4. MCP Router 共享通用服务

`chrome-devtools` 是浏览器调试 MCP server，用于浏览器页面、DOM 快照、截图、控制台数据和网络检查。

`pencil` 是设计 MCP server，用于 Pencil 设计文档、视觉变量、节点读取和导出。

当多个客户端需要同一浏览器或设计能力时，这些共享通用 MCP server 可以由 MCP Router 管理。

当 `chrome-devtools` 或 `pencil` 由 MCP Router 管理时，`C:\Users\lenovo\.codex\config.toml` 中对应的 Codex 直连 server entry 应禁用或不存在。

`C:\Users\lenovo\.codex\config.toml` 是本 Windows 机器上的用户级 Codex 配置文件，用来控制 Codex 的直连 MCP server entry。

## 5. Router 自引用规则

`mcp_router` 是 Codex 侧 MCP server entry，用来让 Codex 连接到 MCP Router。

`mcp-router` 是 MCP Router 应用或包名称，不能被注册成由 MCP Router 自己管理的 server。

MCP Router 不能管理一个反过来指向 MCP Router 的 server entry，因为这会形成自引用，并可能造成递归路由、重复启动或混乱的工具暴露。

## 6. 高风险共享服务规则

`windows-cli` 是 Windows shell MCP server；没有明确操作者批准和强审批门禁时，不能通过 MCP Router 广泛暴露。

SSH 管理 MCP server 是可以创建、更新或删除 SSH 连接记录的工具；除非任务明确需要，否则不应默认暴露给 Codex。

部署类 MCP server 是可以发布或修改远程基础设施的工具；通过 MCP Router 共享时应保持只读或受审批门禁保护。

## 7. 必需的 checker 行为

`tools/check_mcp_router_scope_policy.py` 是仓库内 checker，用来验证 Codex MCP 范围划分并报告 MCP Router drift。

当本地用户级文件存在时，checker 必须验证 Codex 直接启用了 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace`。

当本地用户级文件存在且 MCP Router 启用时，checker 必须验证 `chrome-devtools` 和 `pencil` 的 Codex 直连 entry 已禁用或不存在。

checker 必须把 MCP Router 中的 `omx_state`、`omx_memory`、`omx_code_intel`、`omx_trace` 或 `mcp-router` server 记录报告为 drift。

默认 guard 路径可以把 MCP Router 数据库 drift 报告为 warning，因为 MCP Router 属于外部用户级应用状态。操作者需要审计本机实时状态时，可以用 strict 本地运行把该 drift 变为失败。

## 8. ???? Codex bridge ???

`tools/mcp_router_scope_policy_exceptions.json` ?????? MCP scope exception registry????? checker ?????????????????

????? Codex ? `mcp_router` bridge ??? `/resume` ????????????????? bridge?`mcp_router` bridge ? Codex ?? MCP Router ???? MCP server entry?

??????? `tools/mcp_router_scope_policy_exceptions.json`??????? `id`?`reason` ? `recovery_condition`?`id` ????????`reason` ??????????`recovery_condition` ?????? bridge ??????????

????? active ????MCP Router ???????? Trae?VS Code ? PyCharm ???????Codex ??????? `mcp_router` bridge?

??????? `omx_state`?`omx_memory`?`omx_code_intel` ? `omx_trace` ? Codex ?????????? oh-my-codex MCP server???????????????? trace ???

? byte-transparent MCP-safe wrapper ? direct bridge path ?? initialize?tools/list????? resume-startup ???????????????byte-transparent MCP-safe wrapper ???? MCP stdio ??????????

## 9. 验证命令

修改本策略或 checker 后，运行以下命令：

```powershell
python tools/check_mcp_router_scope_policy.py --root . --json
python tools/run_openspec_guard.py --root . --json
git diff --check
```

`python tools/check_mcp_router_scope_policy.py --root . --json` 会运行 MCP 范围 checker，并输出机器可读的 JSON。

`python tools/run_openspec_guard.py --root . --json` 会运行仓库聚合 guard，覆盖 OpenSpec 和治理检查。

`git diff --check` 会在提交前检查 diff 是否存在空白字符问题。
