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

- `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - 当前命名主线，用于 post-migration LangGraph capability-gap synchronization（迁移后 LangGraph 能力差距同步）与相邻 operator-surface maintenance（操作员控制面维护）。
- `docs_bilingual/project_startup_summary.md` - 稳定仓库入口 startup summary，用来把快速变化的执行状态指向本文。
- `AGENTS.md` - 仓库指令入口，继续作为路由和安全提醒的权威表面。

当新会话需要在打开或继续 OpenSpec change 前确认当前主线真实进展时，先读本文。

## 当前交接快照

先读本节，再读更早的 implementation notes（实施说明）或 archived change history（归档变更历史）。

最新落地增量：

- `codex-direct-browser-design-mcp-policy` - 已落地的 policy change，用于保留 browser/design MCP capability，并防止 MCP-scope cleanup 禁用必要的浏览器或设计自动化表面。
- `archive/codex-direct-browser-design-mcp-policy` - 已通过 GitLab 合并的 OpenSpec archive closeout；归档位于 `openspec/changes/archive/2026-05-02-codex-direct-browser-design-mcp-policy/`。
- `sync-durable-rollout-plan-status` - 已落地的 OpenSpec change，更新 cross-session durable-state isolation plan，使 MR 5 helper mirror source-of-truth 工作不再被描述为下一步 active durable-state slice。
- `docs/fix-status-sync-chinese-text` - 已落地的 follow-up，用可读 UTF-8 中文替换中文 status-sync artifacts 中损坏的问号占位文本。
- `archive/sync-durable-rollout-plan-status` - 已通过 GitLab 合并的 OpenSpec archive closeout；归档位于 `openspec/changes/archive/2026-05-02-sync-durable-rollout-plan-status/`。
- `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` 与 `.zh-CN.md` - 稳定 specs 现在要求 durable-state rollout queues 不得把已归档切片列为下一步 active work。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` 与 `.zh-CN.md` - canonical durable-state isolation plans 现在把 MR 5 标记为已完成，并把 MR 6 或 MR 6 readiness review 重述为下一步 decision point。
- `codex-user-level-mcp-scope-policy` 以及 `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` / `.zh-CN.md` - 稳定 MCP scope policy 仍是 Codex-direct 与 MCP Router-managed MCP entries 的路由权威。
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - 稳定 spec，要求当前 mainline memory handoff 在列出下一步前先识别最新落地增量。

本次刷新开始时的发布与 active-change 状态：

- `main`、`gitlab/main` 与 `github/main` - 在打开 `refresh-mainline-memory-after-durable-rollout-status-sync` 前，本地 clone 中三者都指向提交 `b8223434bf873d93c22ab82ac26ec095e99e0576`。
- GitLab main pipeline `#2495016689` 已通过，目标提交为 `b8223434bf873d93c22ab82ac26ec095e99e0576`。
- `openspec list --json` 在本刷新 change 于隔离 worktree 中打开前返回空的 `changes` 数组。
- `refresh-mainline-memory-after-durable-rollout-status-sync` 是当前 handoff-refresh OpenSpec change。它只刷新 memory；如果另一个 live session 仍拥有 broad `openspec/specs` 范围，则 archive 应稍后串行执行。

当前判断：

- Codex direct browser/design MCP policy 已经实现、归档、合并到 GitLab `main`，并同步到 GitHub。
- durable rollout plan status-sync 工作已经实现、中文文本已修复、已归档、合并到 GitLab `main`，并同步到 GitHub。
- 新会话不应重新打开 MR 5 helper mirror source-of-truth 工作；它已经完成并纳入已实现 baseline。
- 新会话不应再把旧 replay、diff-approval、task-ownership precheck、MCP-scope 或 durable-rollout MR 5 工作当成当前必须实施目标。

## MCP Scope Routing Reminder（MCP 范围路由提醒）

当问题涉及 MCP server placement（MCP 服务器放在哪里）时，使用以下路由：

- `omx_state` - oh-my-codex state surfaces（状态表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_memory` - oh-my-codex memory surfaces（记忆表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_code_intel` - oh-my-codex code-intelligence surfaces（代码智能表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_trace` - oh-my-codex trace surfaces（追踪表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `mcp_router` - Codex 侧 bridge entry（桥接入口），用来连接 MCP Router；Codex 可以保留这个直连入口，但 MCP Router 不得把自己作为子 server 管理。
- `chrome-devtools` - browser/devtools MCP capability，必须为需要浏览器自动化的项目保持可用。
- `pencil` - design/canvas MCP capability，必须为需要设计任务的场景保持可用。

除非用户明确要求，仓库代码和 MR 不得修改 user-level MCP configuration（用户级 MCP 配置）或 MCP Router database state（MCP Router 数据库状态）。

## 当前 change 准入结论

本次 handoff refresh 合并后，仓库可以进入下一轮明确命名的小步 OpenSpec change，但必须尊重任何 live local ownership claims：

- 当前 startup surfaces 已经有 MCP scope、worktree isolation 与 durable-state status-sync boundaries 的专门指针。
- 写文件前必须用 `openspec list --json` 检查 active-change 状态。
- 创建新写入范围前，必须用 `python tools/check_session_ownership_claims.py --root . --precheck-task ... --json` 检查本地 task ownership。
- 对单切片文档、checker refresh 或 readiness-review 工作，仍然不允许启动 durable team。
- GitLab 仍是权威 MR 与合并表面；GitHub 仍是合并后的镜像目标。

## 新会话安全下一步

本次刷新落地后，写文件前先明确选择以下动作之一：

1. `MR 6 readiness review` - 创建或继续单独命名的 OpenSpec change，复核 MR 3 到 MR 5 的证据是否仍足以支撑 automatic durable routing hookup。
2. `automatic durable routing hookup` - 只有 MR 6 readiness 被接受后，才能通过单独 reviewed change 把真实 task-flow thresholds 接入 `native_omx` / `langgraph` 选择。
3. `strict MCP Router audit` - 运行 `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` 检查本地 MCP Router drift（漂移），然后只报告手动清理建议，不编辑数据库。
4. `archive this memory refresh` - 只有在没有 active session 拥有重叠的 `openspec/specs` 范围时才执行；必须在串行 archive worktree 中归档。
5. `new OpenSpec change` - 只有在确认没有 active changes，或明确接管现有 active change 后，才创建新的 change。

## 重要防漂移说明

- 本仓库拥有 Codex orchestration line（Codex 编排产品线）；不要回到 `D:\PythonProject_OpenClaw` 为这条线做新实施。
- `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 与 `D:\project` 是 consumer projects（消费项目），各自保留自己的 repo-local facts 与 durable state。
- 需要浏览器自动化的项目仍然可以使用 browser capability（浏览器能力）；不要为了减少启动上下文而删除 browser 或 Vercel 相关 skills。
- 除非用户明确授权，user-level skills 与 `C:\Users\lenovo\.codex\config.toml` 不属于本 change 范围。
- PowerShell 中看到中文乱码通常是输出编码问题；只有 Python UTF-8 读取也显示源文本损坏时，才把它当成源文件损坏。
