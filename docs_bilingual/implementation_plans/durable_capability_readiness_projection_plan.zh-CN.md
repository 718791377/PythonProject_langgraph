---
doc_id: durable_capability_readiness_projection_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/durable_capability_readiness_projection_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable Capability Readiness Projection Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Project durable lane state as installed, enabled, selected, and ready without collapsing those states.

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan; automatic_orchestration_routing_enforcement_plan

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
阶段：Stage C implementation package ready for local validation, commit, and local-main integration
责任会话：main Codex leader session
当前门禁：本地 CI 与本地 MR review 通过后合入本地 main；远端发布仍不在范围内，除非用户明确批准
Stage C 进入条件：用户已明确要求继续实施本子 implementation plan
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_capability_switch_chain.py
- tools/check_effective_lane_fit_evidence.py
- docs_bilingual/governance/langgraph_user_level_runtime_policy.md
- test/*capability*readiness*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- capability switch state schema
- LangGraph readiness evidence

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

## Real Runtime Implementation Gap

Readiness projection is checker-backed, but live installed/enabled/selected/ready refresh is not implemented. Real runtime work must probe user-level and repo-local state and refresh projections without collapsing fields.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for installed-only, enabled-not-selected, selected-not-ready, and ready states.
- [x] Update evidence checks to require distinct state fields.
- [x] Document user-facing wording for backend_default and backend_ready.
- [x] Run capability switch and effective-lane checks plus local gate.
- [ ] Stage D real runtime: implement readiness probe helper that refreshes installed, enabled, selected, and ready for native_omx and LangGraph without collapsing states.
- [ ] Stage D real runtime: record probe source, timestamp, backend family, selector evidence, version evidence, and blockers in sanitized projection receipts.
- [ ] Stage D real runtime: wire projection refresh into activation evidence without claiming durable workflow adoption or persistent-team launch.
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
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for installed/enabled/selected/ready probe refresh; this package updates plan governance only and does not run live runtime.
- 2026-05-30 Stage C 实施：`tools/check_capability_switch_chain.py` 现在校验 durable capability readiness projections，要求区分 `installed`、`enabled`、`selected`、`ready` 四个字段，并强制 `ready == installed && enabled && selected` 不变量。
- 2026-05-30 Stage C fixtures：`test/check_capability_switch_chain.test.py` 覆盖 installed-only、enabled-not-selected、selected-not-ready、ready、collapsed-ready 与 missing-field readiness 状态。
- 2026-05-30 Stage C 文档：`docs_bilingual/governance/langgraph_user_level_runtime_policy.md` 与 `.zh-CN.md` 记录 `backend_default` / `backend_ready` 对外措辞，并澄清 readiness 不表示当前任务已经采用 durable workflow、tracked thread 或 persistent team。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
