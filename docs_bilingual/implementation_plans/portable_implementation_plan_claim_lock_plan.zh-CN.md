---
doc_id: portable_implementation_plan_claim_lock_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/portable_implementation_plan_claim_lock_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage C implementation
phase: 1
batch: 1
confirmation_required: true
confirmed_for_implementation_at: 2026-05-28
---

# Portable Implementation Plan Claim Lock Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Implement a Git and filesystem portable single-active-session claim lock for each child implementation plan without requiring OMX or LangGraph.

## 来源方案

- codex_governance_session_visibility_and_plan_lock_plan; codex_user_level_cross_session_durable_state_isolation_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage C implementation slice for Phase 1 Batch 1。
- 阶段：Phase 1。
- 状态：本子方案已由用户确认为 Stage C 实施项；可以在声明的 feature worktree 内开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage C 实施已合入本地 main 并已验证
责任会话：main Codex leader session
当前门禁：纳入 Phase 1 收口；本收口包合入本地 main 后，远端发布已获授权
Stage C 进入条件：Stage B 子方案包合入本地 `main` 后，用户已确认继续实施本子方案
最后更新：2026-05-29
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_implementation_plan_claim_lock.py
- tools/claim_implementation_plan.py
- .omx/session-claims/ examples or fixtures
- test/*claim*lock*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- claim file format
- docs_bilingual/docs_registry.yaml if registry fields are added

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define the portable claim schema with plan path, branch, worktree, session id, and expiry or release state.
- [x] Add tests for one active claim, stale claim, released claim, and conflicting active claim.
- [x] Implement the claim helper and checker without depending on OMX or LangGraph.
- [x] Run claim-lock tests, worktree receipt checker, and local gate.
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
- 2026-05-29 Phase 1 收口：portable child-plan claim locking 已通过 `fb3ad75` 进入本地 `main`；Phase 1 收口验证确认其已实现、已集成，并可进入已授权的远端发布包。
- 2026-05-28 Stage C 本地集成：实施包已快进合入本地 `main`；合入后 `tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` 通过；当时远端发布仍待授权，后续 2026-05-29 Phase 1 收口已获得明确发布授权。
- 2026-05-28 Stage C 验证：在 `implement-portable-plan-claim-lock-20260528` 分支中通过 `python test/check_implementation_plan_claim_lock.test.py`、`tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` 和 `tools/ci/local_mr_review.ps1`。
- 2026-05-28 Stage C 实施：新增 `tools/check_implementation_plan_claim_lock.py`、`tools/claim_implementation_plan.py`、聚焦测试和本地 guard 注册，用于 portable implementation-plan claim locking。
- 2026-05-28 Stage C 进入：用户确认继续实施本子方案；runtime/checker 工作前已在 `implement-portable-plan-claim-lock-20260528` 分支更新治理状态。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
