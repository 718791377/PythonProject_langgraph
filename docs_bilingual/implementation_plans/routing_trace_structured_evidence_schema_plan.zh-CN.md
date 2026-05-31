---
doc_id: routing_trace_structured_evidence_schema_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/routing_trace_structured_evidence_schema_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Routing Trace Structured Evidence Schema Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Separate Chinese conversation display from structured ASCII evidence fields for routing traces.

## 来源方案

- automatic_orchestration_routing_enforcement_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- 状态：本子方案已获确认，并已通过本地 `main` 上既有 checker 与文档包完成实现；本文现在记录收口包。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：implemented and locally validated
阶段：Stage C 收口包已合入本地 `main`
责任会话：`codex-update-routing-trace-structured-evidence-schema-status-20260531` 表示本次仅更新状态收口的本地会话认领标识。
当前门禁：收口文档已集成本地 `main`；在用户明确授权 GitLab/GitHub 发布前停在远端发布门
Stage C 进入条件：用户确认与收口文档本地 `main` 集成均已满足
最后更新：2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_orchestration_trace_evidence.py
- test/check_orchestration_trace_evidence.test.py
- tools/check_orchestration_collaboration_evidenceguard.py
- test/fixtures/orchestration_*
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- orchestration evidence fixtures
- trace schema fields

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define required structured fields for phase, capability_chain, backend_default, backend_ready, experts, durable workflow, persistent team, and reason.
- [x] Add invalid checker cases/fixtures with missing blockers or collapsed capability states.
- [x] Update checker logic and docs examples.
- [x] Run orchestration evidence tests and local gate.
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## 验收标准

- 本地 `main` 合入后，用户已确认本子方案。
- active session claim 在写入工作开始前明确指向本子方案路径。
- 行为变更必须先有失败测试或 checker fixture。
- 治理文档、runtime helper、checker、测试和 CI 注册保持一致。
- 证据以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-31 local-main 状态收口：分支 `update-routing-trace-structured-evidence-schema-status-20260531` 表示仅用于记录状态收口的本地分支，在收口文档已集成本地 `main` 后把过期的“等待本地集成”门禁替换为远端发布门。
- 2026-05-31 Stage C 收口：分支 `close-routing-trace-structured-evidence-schema-20260531` 记录 structured routing trace schema 已通过 `tools/check_orchestration_trace_evidence.py`、`test/check_orchestration_trace_evidence.test.py`、`tools/check_orchestration_collaboration_evidenceguard.py` 与 activation-policy 文档表面完成实现；最终 local-main commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 实施基线：本地 `main` 已包含 structured trace 与 collaboration evidence 包，包括固定 `Routing trace` / `Updated Plan` 标签证据以及 expert lifecycle non-evidence handling；验证证据见 checker 测试历史和 local CI 记录。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
