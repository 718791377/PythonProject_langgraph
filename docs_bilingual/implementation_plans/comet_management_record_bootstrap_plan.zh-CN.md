---
doc_id: comet_management_record_bootstrap_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/comet_management_record_bootstrap_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Management Record Bootstrap Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Create and validate Comet management records that capture focus-area checklist evidence for each phase.

## 来源方案

- comet_runtime_agile_focus_area_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 4。
- 阶段：Phase 5。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：已实施并已完成本地验证，可合入本地 `main`
阶段：Stage C 实施包
责任会话：`codex-implement-comet-management-record-bootstrap-20260531`
当前门禁：本地 `main` fast-forward 集成，随后进入远端发布批准门；远端发布仍不在范围内且未授权
Stage C 进入条件：当前用户在 2026-05-31 对 Stage B 子方案创建后的继续实施请求已满足该条件
本地集成包：分支 `implement-comet-management-record-bootstrap-20260531`；最终 local-main commit 与验证证据记录在 assistant 回复和本地 git 历史中
最后更新：2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- .codex/skills/comet/scripts/comet-state.sh or installed Comet script source
- .codex/skills/comet/scripts/comet-guard.sh or installed Comet script source
- openspec/changes/*/management.md fixtures
- test/*comet*management*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- comet-state.sh
- comet-guard.sh

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 在本地 main 集成后确认本子方案。
- [x] 为 Open、Design、Build、Verify、Archive 和 Monitoring 增加 management-record fixture 示例。
- [x] 在脚本归属明确后实现 bootstrap 行为。
- [x] 验证必需 management record 路径字段和安全路径约束。
- [x] 运行 Comet 脚本测试、OpenSpec guard 和 local gate。
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
- 2026-05-31 Stage C 实施收口：当前用户确认已授权本子方案实施；分支 `implement-comet-management-record-bootstrap-20260531` 通过确认 Comet runtime management record、阶段 checklist gate、Monitoring return state、路径校验和 archive closing evidence 已实现并由聚焦测试覆盖来关闭本方案。最终 local-main commit 与验证证据记录在 assistant 回复和本地 git 历史中。
- 2026-05-28 runtime 基线：`.codex/skills/comet/scripts/comet-state.sh` 会创建 `management.md` 并记录 `management_record`、`monitoring_status`、`control_decision`、`target_phase`、`rework_reason` 和 `iteration_count`；`.codex/skills/comet/scripts/comet-yaml-validate.sh`、`comet-guard.sh` 与 `comet-archive.sh` 会校验 management-record 路径、checklist evidence、Monitoring-loop clearance 和 closing evidence。
- 2026-05-28 测试覆盖基线：`test/comet_runtime_management_flow.test.py` 覆盖 Open、Design、Build、Verify、Archive 与 Monitoring 的 management evidence、return-transition invariants、UTF-8/legacy label 兼容性、必需字段校验和安全路径约束；该测试已登记在 `tools/ci/ci_test_manifest.json`。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
