---
doc_id: mainline_sync_langgraph_capability_gap_after_migration_aware_live_primary_engine_compatibility_state_startup_summary
lang: zh-CN
status: active
doc_class: startup_summary
translation_of: docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md
---

# 主线 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` 启动摘要

## 适用范围

这份摘要承载当前命名仓库主线中容易漂移的交接细节：

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - 当前命名主线，用于 post-migration LangGraph capability-gap synchronization（迁移后 LangGraph 能力差距同步） 与相邻 operator-surface maintenance（操作员控制面维护）。
- `docs_bilingual/project_startup_summary.md` - 稳定仓库入口 startup summary，用来把快速变化的执行状态指向本文。
- `AGENTS.md` - 仓库指令入口，继续作为路由和安全提醒的权威表面。

当新会话需要在打开或继续 OpenSpec change 前确认当前主线真实进展时，先读本文。

## 当前交接快照

先读本节，再读更早的 implementation notes（实施说明） 或 archived change history（归档变更历史）。

最新落地增量：

- `formalize-mcp-router-scope-policy` - 已归档 OpenSpec change，用来确定哪些 MCP server 属于 Codex direct configuration（Codex 直连配置），哪些可以交给 MCP Router 管理。
- `codex-user-level-mcp-scope-policy` - 稳定 OpenSpec capability，用来记录 MCP Router scope requirements（范围需求） 与 self-management exclusions（禁止自管理规则）。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` - 英文 MCP scope governance policy，用来说明 MCP Router 共享管理与 Codex 专属直连 MCP 的边界。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` - MCP scope governance policy 的中文对照文件。
- `tools/check_mcp_router_scope_policy.py` - checker（检查脚本），用于验证仓库 policy，并可选执行严格本地 MCP Router 状态检查。
- `refresh-mainline-memory-after-task-ownership-precheck` - 已归档 OpenSpec change，用来引入稳定 mainline memory handoff requirement（主线记忆交接需求）。
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - 稳定 spec，要求当前 mainline memory handoff 在列出下一步前先识别最新落地增量。

本次刷新开始时的发布与 active-change 状态：

- `main`、`gitlab/main` 与 `github/main` - 仓库发布引用；本次刷新分支创建前，本地 clone 中三者都指向提交 `f6cc0f6`。
- `openspec list --json` - active-change inventory command（活动变更盘点命令）；在打开 `refresh-mainline-memory-after-mcp-scope-policy` 前，它返回空的 `changes` 数组。
- `refresh-mainline-memory-after-mcp-scope-policy` - 当前用于刷新本文的 OpenSpec change；它合并并归档后，除非有更新的 change，新会话应再次预期没有 active changes。

当前判断：

- MCP Router scope policy 已经实现、归档并同步到 GitHub。
- mainline memory handoff requirement 已经实现并归档。
- 除非出现新证据，新会话不应重新打开 MCP Router scope design（范围设计）。
- 新会话不应再把旧 replay、diff-approval 或 task-ownership precheck 工作当成当前必做实施目标。

## MCP Scope Routing Reminder（MCP 范围路由提醒）

当问题涉及 MCP server placement（MCP 服务器放在哪里） 时，使用以下路由：

- `omx_state` - oh-my-codex state surfaces（状态表面） 的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_memory` - oh-my-codex memory surfaces（记忆表面） 的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_code_intel` - oh-my-codex code-intelligence surfaces（代码智能表面） 的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_trace` - oh-my-codex trace surfaces（追踪表面） 的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `mcp_router` - Codex 侧 bridge entry（桥接入口），用来连接 MCP Router；Codex 可以保留这个直连入口，但 MCP Router 不得把自己作为子 server 管理。
- `chrome-devtools` - shared browser/devtools MCP server candidate（共享浏览器/开发者工具 MCP 候选），当其他 IDE 也需要时可以交给 MCP Router 管理。
- `pencil` - shared MCP server candidate（共享 MCP 候选），当多个客户端需要时可以交给 MCP Router 管理。

除非用户明确要求，仓库代码和 MR 不得修改 user-level MCP configuration（用户级 MCP 配置） 或 MCP Router database state（MCP Router 数据库状态）。

## 当前 change 准入结论

本次 handoff refresh 合并或归档后，仓库可以进入下一轮明确命名的小步 OpenSpec change：

- 当前 startup surfaces（启动表面） 已经有专门的 MCP scope policy 指针。
- 写文件前必须用 `openspec list --json` 检查 active-change 状态。
- 对单切片文档或 checker 刷新工作，仍然不允许启动 durable team。
- GitLab 仍是权威 MR 与合并表面；GitHub 仍是合并后的镜像目标。

## 新会话安全下一步

本次刷新落地后，写文件前先明确选择以下动作之一：

1. `strict MCP Router audit` - 运行 `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` 检查本地 MCP Router drift（漂移），然后只报告手动清理建议，不编辑数据库。
2. `durable-state status hardening` - 继续 active durable-state isolation plan（持久化状态隔离方案），改进只读状态报告，不启动 durable team。
3. `general template follow-up` - 只在独立项目或专用分支里继续 local Git plus OpenSpec plus native subagent template（本地 Git 加 OpenSpec 加原生 subagent 模板） 工作。
4. `new OpenSpec change` - 只有在确认没有 active changes，或明确接管现有 active change 后，才创建新的 change。

## 重要防漂移说明

- 本仓库拥有 Codex orchestration line（Codex 编排产品线）；不要回到 `D:\PythonProject_OpenClaw` 为这条线做新实施。
- `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 与 `D:\project` 是 consumer projects（消费项目），各自保留自己的 repo-local facts 与 durable state。
- 需要浏览器自动化的项目仍然可以使用 browser capability（浏览器能力）；不要为了减少启动上下文而删除 browser 或 Vercel 相关 skills。
- PowerShell 中看到中文乱码通常是输出编码问题；只有 Python UTF-8 读取也显示源文本损坏时，才把它当成源文件损坏。
