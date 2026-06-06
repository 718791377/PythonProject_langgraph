---
doc_id: comet_runtime_policy_checker_alignment_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/comet_runtime_policy_checker_alignment_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Runtime Policy Checker Alignment Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Align Comet runtime behavior, governance policy, OpenSpec specs, checker coverage, and local integration gates.

## 来源方案

- comet_runtime_agile_focus_area_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 4。
- 阶段：Phase 5。
- 状态：已确认并以最小 closeout/alignment 包实施；现有 Comet policy、stable spec、checker、runtime test 与 CI 注册证据已经一致，因此本包不需要修改 runtime/test 源文件。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: completed and locally integrated; included in the current remote-publication carrier
Stage: Phase 5 final closeout package
Owner session: `main-codex-leader-comet-runtime-policy-checker-alignment-20260531`
Current gate: remote publication authorized by the current user message; no further local Phase 5 work remains
Stage C entry condition: satisfied by user confirmation on 2026-05-31 after the Stage B child-plan package was merged to local `main`
Priority update: 2026-06-07 docs-only refresh records Comet-first control priority; no runtime code changes occur in this package.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## 冲突优先级

Comet 继续作为 control layer 协调 OpenSpec WHAT 与 Superpowers HOW。若 gstack delivery-loop advice、Codex harness candidate runtime 或 Spec Kit templates 与 Comet routing 冲突，Comet wins。未来 checker/runtime 应输出 `authority_decision: comet_control_wins`。

## 文件归属

- openspec/specs/*comet*/spec.md
- openspec/specs/*comet*/spec.zh-CN.md
- tools/run_openspec_guard.py
- test/*comet*policy*alignment*
- docs_bilingual/governance/*comet*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- OpenSpec stable specs
- Comet checker registration

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Map Comet runtime requirements to stable OpenSpec spec statements.
- [x] Add checker coverage for policy/runtime drift.
- [x] Update CI/local gate registration if new checker or tests are added.
- [x] Run verify_official_openspec, run_openspec_guard, and local gate.
- [x] Record Comet-first conflict priority; no new scripts.
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
- 2026-06-07 conflict-priority refresh: Comet-first priority; Checker + Runtime deferred.
- 2026-05-31 Stage C 最小 closeout：用户已确认实施；现有对齐证据通过 `python tools/check_openspec_comet_superpowers_policy.py --root . --json`、`python test/comet_runtime_management_flow.test.py`、`python tools/check_implementation_plan_rules.py --root . --json` 和 `python tools/check_worktree_task_receipt.py --root . --json`；checker 报告 `Spec source: stable` 且没有 policy/spec/runtime 术语缺口，因此除本计划对之外不需要源文件修改。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-31 remote-publication carrier: this Phase 5 child plan is included in local `main` and the current user-authorized GitLab/GitHub publication package; no further local Phase 5 implementation work remains before Phase 6 admission.
<!-- EVIDENCE_INDEX_END -->
