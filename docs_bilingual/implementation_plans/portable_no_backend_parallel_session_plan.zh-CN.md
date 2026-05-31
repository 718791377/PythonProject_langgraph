---
doc_id: portable_no_backend_parallel_session_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/portable_no_backend_parallel_session_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Portable No Backend Parallel Session Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Support multi-session parallel implementation using only Git worktrees, registry entries, and portable claim files when OMX and LangGraph are unavailable.

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
Status: implementation-in-progress
Stage: Stage C portable no-backend implementation package
Owner session: codex-portable-no-backend-parallel-session-20260530
Current gate: focused tests, claim-lock and receipt checks, and local gate passed; commit the package, run local MR review, then merge into local main. Remote publication remains out of scope.
Stage C entry condition: satisfied by the 2026-05-30 user request to continue and locally merge this child-plan implementation
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/claim_implementation_plan.py
- tools/check_implementation_plan_claim_lock.py
- docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md
- test/check_implementation_plan_claim_lock.test.py

## 上游调度契约

Portable no-backend session 消费 Phase 1A scheduler/ROB 契约：无后端 claim 只有在预测写集和实际写集后续能通过 `local-main-retire.lock` 保护的 session-owned ROB 流程自退休时，才允许并行执行。


## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- claim lock helper
- worktree isolation policy

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan for current local implementation.
- [x] Define no-backend session startup, claim, release, and cleanup steps.
- [x] Add tests proving the same child plan cannot have two active sessions while different child plans can be claimed in parallel.
- [x] Update governance docs with the portable fallback path.
- [x] Run claim lock, worktree receipt, and local gate checks.
- [x] Align portable claim startup and status output with the Phase 1A scheduler/ROB entry model before runtime integration.
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
- 2026-05-30 local MR review repair: portable startup now preserves Stage A confirmation metadata in claim and receipt so non-document implementation can satisfy the confirmed-plan gate.
- 2026-05-30 validation before commit: focused claim-lock tests, implementation-plan rules, precommit update/archive, ROB checker, worktree receipt checker, diff whitespace check, py_compile, worktree hygiene, and full local gate passed in the feature worktree.
- 2026-05-30 Stage C implementation: added portable `start`, `status`, and metadata-only `release` surfaces to `tools/claim_implementation_plan.py`; startup writes an active claim, worktree receipt, and predicted ROB entry, while focused tests cover same-plan denial, different-plan parallel claims, and safe release without file deletion.
- 2026-05-30 完整提交流程对齐：无 OMX/LangGraph 后端场景不再依赖固定 leader 退休队列；后续 runtime 应使用 portable claim、ROB entry 和 `local-main-retire.lock` 实现 session-owned self-retire。
- 2026-05-29 上游契约补充：引用 Phase 1A scheduler/ROB 模型，作为后续 portable/receipt runtime 对齐依据。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
