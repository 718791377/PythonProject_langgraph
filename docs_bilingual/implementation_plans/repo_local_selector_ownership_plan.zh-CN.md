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

# Repo-local Selector Ownership 方案

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

确保 active durable selector 是 repository-local 的，不能跨 repository 或 worktree 泄漏，并且不能从 compatibility records 自动接管。

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
Status: implemented-local
Status: R5 检查器支撑的 active-candidate 门禁已在本地实现；真实敏感 live action 仍然需要当前 lane receipt 通过后才能继续。
Stage: repo-local selector ownership 的 R5 runtime-governance receipt package。
Owner session: `resume-019e8aa7-r5-runtime-governance-batch`；feature branch 是 `implement-r5-runtime-governance-batch-20260607`。
Current gate: 先运行 focused tests、repository guard、precommit update/archive review、local CI 和 local MR review，再通过 guarded local-main-first integration；remote publication 仍未授权。
R5 evidence: `selector active-candidate receipt linkage and same-repo adoption split` 由 `tools/check_r5_active_candidate_receipts.py` 和 `tools/user_level_receipt_governance.py active-check` 通用合约验证。
Runtime boundary: 本 R5 package 只验证 fixture-backed receipts 和 checker wiring；不安装 user-level tools，不启动 browser/GUI，不发送 WXWork 消息，不启动 durable workers，不运行 live harness jobs，不运行 Spec Kit live/apply modes，不修改 user-level config，不修改 remote publication。
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## 文件归属

- `.omx/state/selectors/active.json` schema 或 fixture - 定义 repo-local active selector truth。
- `tools/check_durable_artifact_state_surfaces.py` - 验证 durable artifact 与 state-surface evidence。
- `tools/check_repo_local_selector_ownership.py` - 验证 selector ownership 与跨 repo fail-closed 行为。
- `tools/repo_local_selector_runtime.py` - 写入、释放、stale-reclaim 并 smoke-test repo-local selector receipt。
- `test/*selector*ownership*` - 覆盖 selector ownership checker regression fixture。
- `test/repo_local_selector_runtime.test.py` - 覆盖 R4 selector runtime regression 行为。

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
- [x] Stage D real runtime：实现 selector write/refresh helper，记录 owner session、backend family、lease expiry、selector revision 与 rollback pointer。
- [x] Stage D real runtime：实现 selector release/stale-reclaim helper，要求 selector id 与 nonce 显式匹配，并写入 audit receipts。
- [x] Stage D real runtime：提供 dry-run 与 apply modes，并在 cross-repo selector adoption 时 fail closed。
- [x] R4 user-level smoke runtime：新增 bounded read-only selector smoke，写入 `smoke-tested` receipt，且不修改 active selector。
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `python test/repo_local_selector_runtime.test.py` - 验证 selector write/refresh、release、stale-reclaim、dry-run/apply、fail-closed 与 R4 smoke receipt。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## 验收标准

- 本地 `main` 合入后，用户已确认本子方案。
- active session claim 在写入工作开始前明确指向本子方案路径。
- 行为变更必须先有失败测试或 checker fixture。
- 治理文档、runtime helper、checker、测试、安全注册表和 CI 注册保持一致。
- R4 smoke receipt 只写入已脱敏 repo-local selector evidence，不修改 user-level state、browser data，也不在 smoke 阶段改 active selector。
- 证据以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 repo-local selector ownership 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-05 Stage D R4 implementation：branch `implement-repo-local-selector-r4-20260605` 新增 `tools/repo_local_selector_runtime.py`、`test/repo_local_selector_runtime.test.py`、CI manifest registration 与 safety registry wiring，覆盖 selector write/refresh、显式 nonce release、stale reclaim、dry-run/apply fail-closed 行为和 R4 `smoke-tested` receipts。
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for active selector write, refresh, renewal, and release helpers; this package updates plan governance only and does not run live runtime.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 Stage C 实施开始：在 tracked 写入前创建 active session claim `main-codex-repo-local-selector-ownership-20260530`；本实施新增 repo-local selector fixtures、checker、guard wiring 与治理文档。
- 2026-05-30 本地验证：selector ownership checker、durable artifact surface tests、OpenSpec guard JSON tests、precommit review checks、worktree receipt check 与 `tools/ci/local_gate.ps1` 均已在 feature commit 前通过。
<!-- EVIDENCE_INDEX_END -->
