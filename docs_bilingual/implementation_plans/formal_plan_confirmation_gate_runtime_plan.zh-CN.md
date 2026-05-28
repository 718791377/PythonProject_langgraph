---
doc_id: formal_plan_confirmation_gate_runtime_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/formal_plan_confirmation_gate_runtime_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 1
batch: 1
confirmation_required: true
---

# Formal Plan Confirmation Gate Runtime Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Enforce that chat-only plan confirmation is not enough for non-document implementation.

## 来源方案

- implementation_plan_confirmation_gate

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 1。
- 阶段：Phase 1。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage C 实施包
责任会话：implement-formal-plan-confirmation-gate-runtime-20260528
当前门禁：验证并提交 feature 分支实施包
Stage C 进入条件：已由指向本 active implementation plan 的已确认 receipt/claim 满足
最后更新：2026-05-28
<!-- CURRENT_STATUS_END -->

## 文件归属

- docs_bilingual/governance/openspec_opsx_project_usage_policy.md
- docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md
- tools/check_plan_exit_execution_governance.py
- tools/complete_local_flow_to_remote_gate.py
- test/*plan*confirmation*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- tools/complete_local_flow_to_remote_gate.py
- precommit helper surfaces

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 合入仍由 leader 串行执行。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add negative tests for chat-only confirmation without a committed active implementation-plan file.
- [x] Add positive tests for active registered committed plan-file confirmation.
- [x] Implement the helper/checker gate with fail-closed behavior.
- [x] Update governance docs and run the plan-exit checker plus local gate.
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
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-28 Stage C 实施：receipt/claim 已记录用户明确确认 `docs_bilingual/implementation_plans/formal_plan_confirmation_gate_runtime_plan.md`，并关联 Stage B 治理包 `4a92f9fc673923a6fec9e31cbcee0526535531b7`；定向测试与仓库门禁证据记录在本次实施会话输出中。
<!-- EVIDENCE_INDEX_END -->
