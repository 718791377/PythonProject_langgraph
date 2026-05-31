---
doc_id: comet_phase_checklist_gate_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/comet_phase_checklist_gate_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Phase Checklist Gate Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Require phase-specific management checklist evidence before Comet forward transitions.

## 来源方案

- comet_runtime_agile_focus_area_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 4。
- 阶段：Phase 5。
- 状态：用户已确认继续实施；本 Stage C 包补充显式回归覆盖和收口证据，并验证既有 Comet runtime 门禁行为。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：已实施并完成本地验证，准备本地 main 集成
阶段：Stage C 实施/收口包
责任会话：当前主 Codex leader session；精确 claim ID 存在 `.omx/session-claims/`
当前门禁：本地 main 集成，然后停在远端发布批准门；远端发布仍未授权
Stage C 进入条件：用户于 2026-05-31 确认继续实施，条件已满足
本地验证：Comet runtime management 测试、OpenSpec Comet/Superpowers policy check、implementation-plan rules 与 run_openspec_guard 已通过；local_gate 和 local_mr_review 在本地 main 集成前运行
最后更新：2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- .codex/skills/comet/scripts/comet-guard.sh
- .codex/skills/comet/scripts/comet-state.sh
- test/*comet*phase*checklist*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- comet-guard.sh
- comet-state.sh

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add failing tests for missing Open, Design, Build, Verify, Archive, and Monitoring checklist items.
- [x] Update transition guards to require checked evidence before forward movement.
- [x] Keep return transitions separate from forward transitions.
- [x] Run Comet tests, run_openspec_guard, and local gate.
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
- 2026-05-31 Stage C closeout: user confirmation is recorded; branch `implement-comet-phase-checklist-gate-20260531` adds explicit static and behavior regression coverage for Open, Design, Build, Verify, Archive, and Monitoring checklist gates; existing runtime transition guard, state, archive, and monitoring-return behavior is validated without duplicating script churn; local validation and local-main integration evidence are recorded in local git history and the assistant response.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
