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

# Worktree Receipt 与 Claim 生命周期方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`；本方案拥有 worktree-task-receipt 与 session-claim lifecycle 状态机。

## 目标

定义并执行 `active`、`paused`、`ready-to-merge`、`merged-local-main`、`completed`、`superseded`、`stale` 与 `cleaned` 生命周期，覆盖 worktree receipt 与 session claim。

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan；codex_governance_session_visibility_and_plan_lock_plan
- 本方案为多 session worktree 隔离和本地 main 集成提供 lifecycle 证据层。

## 范围决策

- 每个 feature worktree 必须有 `.omx/worktree-task-receipt.json`。
- 每个 active branch 必须有 `.omx/session-claims/*.json` 中的 branch-matching claim。
- 清理只能在 local main 包含 feature commit 且 rollback ref 存在后进行。
- remote publication 不是本生命周期自动推进的一部分。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；receipt/claim 生命周期校验已经存在，并能阻止未分类 feature worktree 直接进入集成。
Current gate：本地提交、local gate、local MR review 与 guarded local-main helper；remote publication 关闭。
Runtime boundary：当前 checker 能验证状态，但不会自动推进 active→ready→merged→cleaned，也不会自动删除 worktree 或 branch。
Runtime gap：若要自动化 lifecycle，需要 runtime helper 执行 active→ready→merged→cleaned 状态变更，写入 completion receipt、rollback ref、local main commit、cleanup result 与 remote-sync-needed 状态。
<!-- CURRENT_STATUS_END -->

## 文件归属

- `tools/check_worktree_task_receipt.py` - 校验 worktree task receipt 与 lifecycle 状态。
- `tools/complete_local_flow_to_remote_gate.py` - 执行本地合入到 remote gate 的受控流程。
- `tools/cleanup_integrated_worktree.py` - 清理已集成本地 feature worktree 与分支。
- `.omx/worktree-task-receipt.json` fixture
- `.omx/session-claims/*.json` fixture

## 上游调度契约

本方案消费 implementation_plan claim 与 local-main retire lock 的结果，不重新定义它们。上游调度器必须先保证同一 implementation_plan 同一时间只有一个 session 处理。

## 热点串行规则

receipt schema、claim schema、cleanup helper、complete local flow helper 与 local-main retire lock 必须串行修改。

## 并行会话契约

一个 session 独占本 implementation_plan。其他 session 可并行处理独立 runtime lane，但不得同时改 lifecycle schema 或 cleanup helper。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

现有能力是校验，不是自动推进。后续 runtime 包需要：

<!-- TASK_BACKLOG_START -->
- [x] Stage B：定义 receipt/claim 生命周期状态。
- [x] Stage B：实现 feature worktree receipt 与 branch-matching claim 检查。
- [x] Stage C：记录自动 lifecycle helper 仍是 pending runtime。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：实现 active→ready-to-merge→merged-local-main→cleaned 推进 helper。
- Stage D real runtime：写入 completed_at、rollback_ref、local_main_commit、cleaned_worktree、deleted_branch 与 remote_sync_status。
- Stage D real runtime：为异常路径写入 paused、superseded 或 stale，并保留 rollback/cleanup evidence。

## 验证门禁

- `python tools/check_worktree_task_receipt.py --root . --json` - 验证 worktree receipt lifecycle。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。
- `tools/ci/local_mr_review.ps1` - 执行本地 MR review gate。

## 验收标准

- 中文对照版正文为中文。
- 每个状态转换都有明确前置条件和证据输出。
- Stage D 前不得声明自动 lifecycle 推进已经实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 lifecycle 推进 helper 列为 Stage D pending。
- 2026-05-30 Stage B evidence：已有 worktree task receipt 与 session claim checker 验证 active worktree 证据。
<!-- EVIDENCE_INDEX_END -->
