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

- `archive/mr6-automatic-routing-readiness` - 已落地的 readiness-review closeout，确认 automatic durable routing hookup 已经存在于较早的 team-mode implementation line；不要把 MR 6 重新打开成新的 runtime implementation work。
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` 与 `.zh-CN.md` - canonical durable-state isolation plans 现在说明 MR 1 到 MR 6 都已完成；任何未来 live smoke 或 adoption gate 都必须是单独 reviewed change。
- `fix/omx-mcp-windows-cleanup-output` - 已落地的代码变更，在保留 direct `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` MCP entries 的同时，抑制 wrapped `codex-ohmy` `/resume` cleanup 中正常的 Windows `taskkill` 成功输出。
- `archive/stabilize-omx-mcp-windows-cleanup-output` - 已通过 GitLab MR `!74` 合并的 OpenSpec archive closeout；归档位于 `openspec/changes/archive/2026-05-04-stabilize-omx-mcp-windows-cleanup-output/`。
- `openspec/specs/codex-user-level-windows-cleanup-output-control/spec.md` 与 `.zh-CN.md` - stable specs 现在要求 scoped cleanup-output control、PATH 恢复、direct `omx_*` MCP 保留和 checker-backed validation。
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.md` - stable spec，要求当前 mainline memory handoff 在列出下一步前先识别最新落地增量。

本次刷新开始时的发布与 active-change 状态：

- `main`、`gitlab/main` 与 `github/main` - 在 GitLab MR `!74` 合并并同步 GitHub 后，三者都指向提交 `fccaf73ef45a9c9fb12a1e0f6da1bcfcf4dc11b3`。
- GitLab main pipeline `#2497474485` 已通过，目标提交为 `fccaf73ef45a9c9fb12a1e0f6da1bcfcf4dc11b3`。
- `openspec list` 在 `refresh-mainline-memory-after-cleanup-output-closeout` 于隔离 worktree 中打开前显示没有 active changes。
- `archive/stabilize-omx-mcp-windows-cleanup-output` 和 `archive/mainline-memory-refresh` 的本地 archive worktrees 已在确认干净且已合并后移除。
- 打开本刷新分支前，`python tools/check_worktree_session_hygiene.py --root . --json` 与 `python tools/check_session_ownership_claims.py --root . --json` 已在 `main` 通过。

当前判断：

- bounded durable-state rollout queue 中的 MR 1 到 MR 6 都已完成。
- automatic durable routing helper 已经作为 generated user-level surface 存在；未来工作不得为了宣称 MR 6 已实现而重复实现现有 `omx-team-auto.ps1` 行为。
- Windows cleanup-output 修复已经实现、安装、通过 `/resume` 人工验证、归档、合并到 GitLab `main`，并同步到 GitHub。
- `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 仍是 Codex-direct MCP entries；MCP Router 不托管这些 Codex 专属工具。
- 新会话不应再把旧 MCP-scope、MR 5 helper mirror、MR 6 readiness 或 Windows cleanup-output 工作当成当前必须实施目标。

## 2026-06-01 Phase 5 远端发布修复记录

本节记录 Phase 5 远端发布修复状态.

- GitLab MR `!126` 已合并 Phase 5 收口内容.
- GitLab `main` pipeline 因 merge commit subject 被保存成问号而失败; 内容验证已在分支 pipeline 通过.
- 修复必须前向进行: 不改写历史, 不 force-push; 用 UTF-8 安全的 merge subject 合并前向修复提交.
- GitLab `main` CI 通过前, 不同步 GitHub; 此时仍报告为发布进行中.

## MCP Scope Routing Reminder（MCP 范围路由提醒）

当问题涉及 MCP server placement（MCP 服务器放在哪里）时，使用以下路由：

- `omx_state` - oh-my-codex state surfaces（状态表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_memory` - oh-my-codex memory surfaces（记忆表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_code_intel` - oh-my-codex code-intelligence surfaces（代码智能表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `omx_trace` - oh-my-codex trace surfaces（追踪表面）的 Codex 专属 MCP server；保留为 Codex 直连 MCP，不交给 MCP Router 共享管理。
- `mcp_router` - Codex 侧 bridge entry（桥接入口），用来连接 MCP Router；除非操作者为了受控测试明确重新启用，否则 Codex 侧保持禁用。
- `chrome-devtools` - browser/devtools MCP capability，必须为需要浏览器自动化的项目保持可用。
- `pencil` - design/canvas MCP capability，必须为需要设计任务的场景保持可用。

除非用户明确要求，仓库代码和 MR 不得修改 user-level MCP configuration（用户级 MCP 配置）或 MCP Router database state（MCP Router 数据库状态）。

## 当前 change 准入结论

本次 handoff refresh 合并后，仓库可以进入下一轮明确命名的小步 OpenSpec change，但必须尊重任何 live local ownership claims：

- 写文件前必须用 `openspec list --json` 检查 active-change 状态。
- 创建新写入范围前，必须用 `python tools/check_session_ownership_claims.py --root . --precheck-task ... --json` 检查本地 task ownership。
- stale branch 或 remote-branch 信号必须先分类为 completed-stale residue，新的写入范围才能继续。
- 对单切片文档、checker refresh 或 readiness-review 工作，仍然不允许启动 durable team。
- 本地 `main` 是第一集成面；GitLab 和 GitHub 保留为远端发布与镜像面。

## 新会话安全下一步

本次刷新落地后，写文件前先明确选择以下动作之一：

1. `durable routing smoke/adoption gate` - 只有用户明确指定 target repository、phase、task 和 operator consent boundary 时才执行；必须打开单独 reviewed OpenSpec change，并且在任何 `-Apply` 动作前先从 dry-run 或只读证据开始。
2. `strict MCP Router audit` - 运行 `python tools/check_mcp_router_scope_policy.py --root . --strict-router-state --json` 检查本地 MCP Router drift（漂移），然后只报告手动清理建议，不编辑数据库。
3. `skills context budget follow-up` - 如果操作者希望减少 skill-description warnings，可打开单独 user-level skills governance change；不得删除 browser、Vercel 或 design 能力作为捷径。
4. `new active implementation slice` - 只有在确认没有 active changes，或明确接管现有 active change 后，才创建新的 OpenSpec change。

## 重要防漂移说明

- 本仓库拥有 Codex orchestration line（Codex 编排产品线）；不要回到 `D:\PythonProject_OpenClaw` 为这条线做新实施。
- `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 与 `D:\project` 是 consumer projects（消费项目），各自保留自己的 repo-local facts 与 durable state。
- 需要浏览器自动化的项目仍然可以使用 browser capability（浏览器能力）；不要为了减少启动上下文而删除 browser 或 Vercel 相关 skills。
- 除非用户明确授权，user-level skills 与 `C:\Users\lenovo\.codex\config.toml` 不属于本 change 范围。
- PowerShell 中看到中文乱码通常是输出编码问题；只有 Python UTF-8 读取也显示源文本损坏时，才把它当成源文件损坏。