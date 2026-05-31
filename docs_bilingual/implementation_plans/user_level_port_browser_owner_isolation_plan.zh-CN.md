---
doc_id: user_level_port_browser_owner_isolation_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_port_browser_owner_isolation_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级端口与浏览器归属隔离实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:executing-plans`；只有当实现切片写集互斥时才使用 `superpowers:subagent-driven-development`。本子方案从旧 MCP/skills/browser/CLI 来源方案拆出，必须通过常规 claim、hotspot 与 local-main retire 门禁执行。

## 目标

让 `codex-port` lease、`pending_bind`、`registry_revision` 与 browser owner registry 在 session、worktree 和 consumer project 之间保持安全。

## 来源提取

从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 的 Slice 3、4，以及 Slice 5 的 OpenCLI lease 要求提取。

本文件是 `multi_plan_parallel_session_orchestration_plan.zh-CN.md` 下拆分出的子 implementation plan。旧来源方案保留为历史索引和 baseline checker 索引；它不是本 lane 的单一执行包。

## 阶段位置

- 父方案阶段：Phase 3 Durable State 与跨 Session 隔离。
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

后续实现可触及端口分配 helper、browser owner registry helper、fixture、测试与 policy 文档；不得触碰 human-owned browser data。

后续实现 claim 必须在编辑前列出精确文件归属。worker 不是独自在代码库中工作，不得 revert 其他 worker 的更改，并且必须报告 changed paths。

## 并行会话契约

当仅拥有 port/browser-owner 文件时，可与 receipt 和 discovery 方案并行；任何共享 state path 或 cleanup 行为必须与 durable-state isolation 工作串行化。

共享 hotspot 仍通过父方案、implementation-plan claim lock、ROB entry 与 local-main retire lock 串行化。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [ ] 保持 Codex 用户级端口范围位于下游 consumer project 范围之前，并要求 OpenCLI 类 adapter 使用 `--port auto`。
- [ ] 定义 `codex-port` 原子 registry 写入，包括可恢复的 `pending_bind` 与单调递增的 `registry_revision`。
- [ ] 在 owner registry 中区分 isolated-session-managed、project-profile 与 human-owned browser assets。
- [ ] 要求自动化 browser target 只能有一个 owner；归属不明确时 fail closed。
- [ ] 阻止自动清理 project-profile 与 human-owned browser assets，除非后续方案提供明确授权证据。
- [ ] 向 Phase 6 adapter 方案暴露已清洗 lease evidence，不泄露 cookies、tokens 或 raw browser data。
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
