---
doc_id: user_level_capability_receipt_rollback_redaction_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_capability_receipt_rollback_redaction_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级能力 Receipt、Rollback 与 Redaction 实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:executing-plans`；只有当实现切片写集互斥时才使用 `superpowers:subagent-driven-development`。本子方案从旧 MCP/skills/browser/CLI 来源方案拆出，必须通过常规 claim、hotspot 与 local-main retire 门禁执行。

## 目标

在任何用户级 MCP、browser 或 CLI harness 通道成为 active runtime surface 前，先提供共享 authorization receipt、update receipt、rollback pointer 与 redaction 契约。

## 来源提取

从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 的 Slice 7 以及 Slice 2、5、6 的敏感通道门禁提取。

本文件是 `multi_plan_parallel_session_orchestration_plan.zh-CN.md` 下拆分出的子 implementation plan。旧来源方案保留为历史索引和 baseline checker 索引；它不是本 lane 的单一执行包。

## 阶段位置

- 父方案阶段：Phase 1 施工安全底座。
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

后续实现可触及 `tools/user_level_receipt_governance.py`、receipt/redaction 测试、OpenSpec delta 与用户级治理文档；本次创建方案仅改文档。

后续实现 claim 必须在编辑前列出精确文件归属。worker 不是独自在代码库中工作，不得 revert 其他 worker 的更改，并且必须报告 changed paths。

## 并行会话契约

只编辑本方案、spec 或测试时，可与端口/浏览器归属和 discovery facade 工作并行；若修改共享 receipt helper，则独占该 hotspot，adapter 方案必须在其合入后消费契约。

共享 hotspot 仍通过父方案、implementation-plan claim lock、ROB entry 与 local-main retire lock 串行化。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [ ] 冻结最小 authorization receipt 字段：action、target、scope、expiry、session 与 operator confirmation。
- [ ] 冻结 update receipt 字段：tool name、installed version、source URL、install path、wrapper path、state path、smoke test command、updater command、rollback pointer、owner lane 与 redaction status。
- [ ] 禁止在已保存 receipt 中保留 raw secrets、cookies、tokens、browser data、message contents 与 plugin description dumps。
- [ ] 定义 rollback pointer 默认输出 hash；raw path 仅能在明确授权的本地证据中可见。
- [ ] 若后续实现修改 runtime 或测试，必须把 checker/CI 变化注册进共享 guard。
- [ ] 在任何 live install、live start、GUI write、cookie read 或 sensitive MCP call 前，先把合入后的 receipt 契约交给 Phase 6 adapter 方案消费。
- [ ] 运行本 child lane 的聚焦验证。
- [ ] 产生实现证据后更新父方案 evidence index 与 Phase 7 集成方案。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- OpenSpec aggregate guard: `python tools/run_openspec_guard.py --root . --json` verifies official workflow, document policy, and name clarity rules.
- Pre-commit update/archive review: `python tools/check_precommit_update_archive.py --root . --json` verifies required related-file updates and archive state.
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
