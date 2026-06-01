---
doc_id: user_level_browser_cli_adapter_boundary_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级 Browser 与 CLI Adapter 边界实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:executing-plans`；只有当实现切片写集互斥时才使用 `superpowers:subagent-driven-development`。本子方案从旧 MCP/skills/browser/CLI 来源方案拆出，必须通过常规 claim、hotspot 与 local-main retire 门禁执行。

## 目标

将 chrome-devtools-mcp、CDP Bridge、OpenCLI、CLI-Anything 与 `wecom-cli` 保持为受治理的 on-demand 或 reference adapter，而不是竞争性治理层。

## 来源提取

从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 的 Slice 5 与 Slice 6 提取。

本文件是 `multi_plan_parallel_session_orchestration_plan.zh-CN.md` 下拆分出的子 implementation plan。旧来源方案保留为历史索引和 baseline checker 索引；它不是本 lane 的单一执行包。

## 阶段位置

- 父方案阶段：Phase 6 从属 Adapter 边界。
- 执行模型：视情况多阶段推进；只有写集互斥或 hotspot 已明确串行化时，才允许多会话并行。
- 远端发布：本方案不授权远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: active and unclaimed for implementation.
Current gate: 非文档实现前必须完成 child-plan confirmation、clean feature worktree、branch-matching claim 与 hotspot declaration。
Source relation: 从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 提取；不要把旧来源方案直接挂成父方案子方案。
Runtime boundary: 本次创建方案不安装工具、不启动浏览器、不调用 sensitive MCP、不修改用户级 runtime state。
<!-- CURRENT_STATUS_END -->

## 文件归属

后续实现可触及 adapter guard helper、OpenCLI guard 测试、CDP/chrome-devtools governance 测试、WeCom guard helper 与文档；默认不得执行 live GUI 或 browser mutation。

后续实现 claim 必须在编辑前列出精确文件归属。worker 不是独自在代码库中工作，不得 revert 其他 worker 的更改，并且必须报告 changed paths。

## 并行会话契约

adapter-specific 工作仅在写集互斥时可并行；live start、install、cookies、typing/clicking、JS execution、GUI write 与 WeCom GUI automation 在 receipt 和 owner evidence 合入前保持 blocked。

共享 hotspot 仍通过父方案、implementation-plan claim lock、ROB entry 与 local-main retire lock 串行化。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [ ] read-only tab inventory 无需 sensitive authorization。
- [ ] click、type、navigate、JavaScript execution、cookie read 与 raw browser data access 必须要求 authorization receipt。
- [ ] OpenCLI 类 adapter 必须使用 `--port auto` 和已清洗的 `codex-port` lease evidence。
- [ ] CLI-Anything 保持 generation-first；缺少 receipt 与 smoke evidence 时阻止 hard-load skills。
- [ ] `wecom-cli` 保持 API/Webhook-first；WXWork GUI dispatch 必须要求 global lease、operator confirmation、timeout release 与 dry-run evidence。
- [ ] 集成前必须把每个 adapter lane 报告为 `reference-only`、`planned`、`on-demand` 或 `active-candidate`。
- [ ] 运行本 child lane 的聚焦验证。
- [ ] 产生实现证据后更新父方案 evidence index 与 Phase 7 集成方案。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- MCP scope checker: `python tools/check_mcp_router_scope_policy.py --root . --json` verifies Codex direct MCP boundaries and Router isolation.
- OpenSpec aggregate guard: `python tools/run_openspec_guard.py --root . --json` verifies official workflow, document policy, and name clarity rules.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.

## 验收标准

- 本 lane 按阶段边界保持 discovery、receipt、lease 或 adapter 分离。
- 没有所需 receipt、owner、rollback 与 redaction evidence 时，不启用 sensitive runtime action。
- 任何 checker、test 或 OpenSpec 变更必须在 local main integration 前注册进共享 guard。
- local main integration 保持串行，远端发布仍等待显式授权。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01：由 MCP/skills/browser/CLI decomposition package 创建子方案；实现证据等待后续 claim。
<!-- EVIDENCE_INDEX_END -->
