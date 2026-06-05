---
doc_id: durable_smoke_adoption_gate_template_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/durable_smoke_adoption_gate_template_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable Smoke Adoption Gate Template Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Create the durable smoke and adoption gate template before any live durable runtime exercise or apply-mode adoption is allowed.

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 2。
- 阶段：Phase 3。
- 状态：本文件是 active 子 implementation_plan；用户已确认实施只读 gate-template 包。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：feature worktree 中已完成验证的实施包
责任会话：main Codex leader session
当前门禁：用户已确认继续实施；runtime exercise、live smoke 和 apply mode 仍延后，必须等本 gate 通过且后续 reviewed change 明确授权后才能进入
Stage C 进入条件：本地验证已通过；下一步是只读 gate-template 包完成 local MR review 并合入本地 main
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- docs_bilingual/governance/langgraph_user_level_runtime_policy.md
- tools/*durable*gate*
- test/*durable*gate*
- codex-durable-state-status.ps1

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- codex-durable-state-status.ps1
- tools/install-codex-user-level-team-mode.ps1

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

## Real Runtime Implementation Gap

Durable smoke/adoption is still template-only. Real runtime work must provide an executable durable smoke runner, apply-mode adoption helper, R3/R4/R5 receipts, and fail-closed evidence before any live adoption is claimed.

<!-- TASK_BACKLOG_START -->
- [x] 确认本子方案进入实施。
- [x] 定义 R0.6.0 gate template fields 和 R0.6.1 gate field checker behavior。
- [x] 增加 negative checker fixtures，用于在缺少 gate template 时阻止 R0.6.2 live smoke 或 apply-mode adoption。
- [x] 记录 runtime exercise、live smoke 和 apply mode 必须延后到本 gate 通过之后。
- [x] Run durable gate tests and local gate.
- [ ] Stage D real runtime: implement executable durable smoke runner that writes sanitized R4 smoke receipts and never collapses smoke success into adoption.
- [ ] Stage D real runtime: implement apply-mode adoption helper that writes selected/running/adopted/released receipts and fail-closed rollback evidence.
- [ ] Stage D real runtime: add live adoption handoff receipts with operator authorization, backend-family ownership, timeout release, and cleanup evidence.
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
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for real durable smoke, apply-mode adoption, and live adoption; this package updates plan governance only and does not run live runtime.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 实施：扩展 `tools/check_durable_routing_smoke_gate_template.py`，支持 candidate-template validation，并默认运行 `tools/fixtures/durable_routing_smoke_gate_template/` 下的只读 self-test fixtures；现有 OpenSpec guard 调用会覆盖这些 fixtures，因为该 checker 默认执行 self-test。
- 2026-05-30 验证：`python tools\check_durable_routing_smoke_gate_template.py --root . --json`、`python tools\check_document_pair_policy.py --root . --json`、`python tools\check_name_clarity_rules.py --root . --json`、`python tools\check_precommit_update_archive.py --root . --json` 和 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` 已在 feature worktree 中于提交前通过。Local MR review 是 feature commit 清洁后的合入前门禁。
<!-- EVIDENCE_INDEX_END -->
