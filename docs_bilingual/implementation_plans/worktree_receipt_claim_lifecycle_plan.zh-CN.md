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
Status: implemented-local
Status: R5 检查器支撑的 active-candidate 门禁已在本地实现；真实敏感 live action 仍然需要当前 lane receipt 通过后才能继续。
Stage: worktree receipt 与 claim lifecycle 的 R5 runtime-governance receipt package。
Owner session: `resume-019e8aa7-r5-runtime-governance-batch`；feature branch 是 `implement-r5-runtime-governance-batch-20260607`。
Current gate: 先运行 focused tests、repository guard、precommit update/archive review、local CI 和 local MR review，再通过 guarded local-main-first integration；remote publication 仍未授权。
R5 evidence: `worktree-task lifecycle receipt fields plus generic active-candidate checker` 由 `tools/check_r5_active_candidate_receipts.py` 和 `tools/user_level_receipt_governance.py active-check` 通用合约验证。
Runtime boundary: 本 R5 package 只验证 fixture-backed receipts 和 checker wiring；不安装 user-level tools，不启动 browser/GUI，不发送 WXWork 消息，不启动 durable workers，不运行 live harness jobs，不运行 Spec Kit live/apply modes，不修改 user-level config，不修改 remote publication。
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
Last updated: 2026-06-07
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
- [x] Stage B：定义 receipt/claim lifecycle 状态。
- [x] Stage B：要求 feature worktree receipt 与 branch-matching claim 对齐。
- [x] Stage C：把 lifecycle helper 的真实推进能力标记为 pending runtime。
- [x] Stage D/R4：实现 `active`、`paused`、`ready-to-merge`、`merged-local-main`、`completed`、`stale`、`superseded` 与 `cleaned` 状态推进 helper。
- [x] Stage D/R4：要求每次状态转换记录 owner、previous state、next state、evidence paths、rollback ref 与 cleanup decision。
- [x] Stage D/R4：把 local-main retire evidence 与 guarded cleanup evidence 写入 lifecycle ledger，并且不授权远程发布。
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
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 worktree receipt 与 claim lifecycle 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-06 R4 runtime implementation package：branch `implement-worktree-receipt-claim-lifecycle-r4-20260605` 新增 `tools/advance_worktree_task_lifecycle.py`，把 local-main completion 与 guarded cleanup transition ledger 接入 helper；测试覆盖放入已由 CI 管理的 `test/cleanup_integrated_worktree.test.py`，避免共享 CI manifest hotspot，并在未明确请求 GitLab/GitHub 操作前保持远程发布未授权。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 记录 lifecycle 推进 helper 的 Stage D pending 工作；该包只更新计划治理，不执行 live runtime。
- 2026-05-30 Stage B evidence：worktree task receipt 与 session claim checker 已覆盖 active worktree 基线。
- 2026-05-30 validation package：focused receipt tests、receipt checker、implementation-plan checker、OpenSpec spec validation、pre-commit update/archive review、local gate 与 local MR review 均在本地 main 集成前通过。
- 2026-05-30 implementation package：新增 `stale` receipt/claim lifecycle 校验、全状态 fixtures 与 completion-evidence 分组；OpenSpec change `implement-worktree-receipt-claim-lifecycle-20260530` 将 stale 记录为分类状态，而不是 cleanup 或 branch-deletion evidence。
- 2026-05-30 complete-flow alignment：receipt lifecycle 继续作为 ROB 状态来源；`ready-to-merge` 映射为 ready 候选包，`merged-local-main` 映射为 lock-backed self-retire 后的 retired evidence。
- 2026-05-29 upstream contract supplement：引用 Phase 1A scheduler/ROB 模型作为后续 portable/receipt runtime 对齐来源。
- 2026-05-28 Stage B child-plan creation：作为 parent multi-plan orchestration child-plan package 的一部分创建，最终 commit 记录在 assistant response 和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
