---
doc_id: repo_local_selector_ownership_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/repo_local_selector_ownership_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Repo Local Selector Ownership Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Ensure active durable selectors are repository-local and cannot leak across repositories or worktrees.

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 2。
- 阶段：Phase 3。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage C implementation package
责任会话：main-codex-repo-local-selector-ownership-20260530
当前门禁：本地验证已通过；准备 local MR review 与本地 main 合入；远端发布仍不在范围内
Stage C 进入条件：2026-05-30 用户确认继续实施 repo_local_selector_ownership_plan，条件已满足
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- .omx/state/selectors/active.json schema or fixtures
- tools/check_durable_artifact_state_surfaces.py
- tools/*selector*
- test/*selector*ownership*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- .omx/state/selectors/active.json
- .omx/state/selectors/leases/*

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

## Real Runtime Implementation Gap

Selector ownership is checker-backed, but automatic selector refresh is not implemented. Real runtime work must write, renew, release, and audit repo-local active selectors under ownership and stale-lock rules.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for same-repo, cross-repo, and stale selector ownership.
- [x] Update checker logic to fail closed on cross-repository selector adoption.
- [x] Document safe selector inspection and no-auto-adoption behavior.
- [x] Run durable state surface checks and local gate.
- [ ] Stage D real runtime: implement selector write/refresh helper that records owner session, backend family, lease expiry, selector revision, and rollback pointer.
- [ ] Stage D real runtime: implement selector release/stale-reclaim helper with explicit nonce matching and audit receipts.
- [ ] Stage D real runtime: add dry-run and apply modes that fail closed on cross-repo selector adoption.
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
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for active selector write, refresh, renewal, and release helpers; this package updates plan governance only and does not run live runtime.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 Stage C 实施开始：在 tracked 写入前创建 active session claim `main-codex-repo-local-selector-ownership-20260530`；本实施新增 repo-local selector fixtures、checker、guard wiring 与治理文档。
- 2026-05-30 本地验证：selector ownership checker、durable artifact surface tests、OpenSpec guard JSON tests、precommit review checks、worktree receipt check 与 `tools/ci/local_gate.ps1` 均已在 feature commit 前通过。
<!-- EVIDENCE_INDEX_END -->
