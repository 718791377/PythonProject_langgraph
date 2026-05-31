---
doc_id: worktree_receipt_claim_lifecycle_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/worktree_receipt_claim_lifecycle_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Worktree Receipt Claim Lifecycle Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Define and enforce active, paused, ready-to-merge, merged-local-main, completed, superseded, stale, and cleaned lifecycle states for worktree receipts and session claims.

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan; codex_governance_session_visibility_and_plan_lock_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 2。
- 阶段：Phase 3。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
status: active
stage: Stage C local implementation package
owner_session: implement-worktree-receipt-claim-lifecycle-20260530
current_gate: implement, validate, archive, commit, and merge to local main; stop at remote publication gate
stage_c_entry_condition: satisfied by explicit user request on 2026-05-30 to continue this plan
last_updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_worktree_task_receipt.py
- .omx/worktree-task-receipt.json fixtures
- .omx/session-claims fixtures
- test/*worktree*receipt*

## 上游调度契约

Worktree receipt lifecycle 是 Phase 1A scheduler/ROB 模型的状态来源：ready-to-merge 对应 ROB `ready`，merged-local-main 对应 `retired`，stale/superseded 对应 blocked 或 flushed entry。


## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- receipt lifecycle schema
- cleanup helper behavior

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add schema fixtures for every allowed lifecycle state.
- [x] Require completion fields for merged, completed, cleaned, and remote-sync-needed states.
- [x] Document cleanup and branch deletion evidence without forcing immediate cleanup.
- [x] Run receipt checker, local gate, local MR review, archive, and post-archive validation.
- [x] Align receipt lifecycle states with Phase 1A ROB entry states before runtime integration.
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
- 2026-05-30 validation package: focused receipt tests, receipt checker, implementation-plan checker, OpenSpec spec validation, pre-commit update/archive review, local gate, and local MR review all passed before local main integration.
- 2026-05-30 implementation package: added `stale` receipt/claim lifecycle validation, all-state fixtures, and completion-evidence grouping; OpenSpec change `implement-worktree-receipt-claim-lifecycle-20260530` records stale as a classification state rather than cleanup or branch-deletion evidence.
- 2026-05-30 完整提交流程对齐：receipt lifecycle 继续作为 ROB 状态来源；`ready-to-merge` 对应 ready 候选包，`merged-local-main` 对应持锁自退休后的 retired evidence。
- 2026-05-29 上游契约补充：引用 Phase 1A scheduler/ROB 模型，作为后续 portable/receipt runtime 对齐依据。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
