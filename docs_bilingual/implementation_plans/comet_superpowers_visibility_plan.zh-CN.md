---
doc_id: comet_superpowers_visibility_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/comet_superpowers_visibility_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Superpowers Visibility Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Make Superpowers HOW-layer skill usage explicit in Comet Design, Build, Verify, and branch-finishing phases.

## 来源方案

- comet_runtime_agile_focus_area_plan; codex_governance_session_visibility_and_plan_lock_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 4。
- 阶段：Phase 5。
- 状态：本文件是 active 子 implementation_plan；用户已在 2026-05-31 的冷启动继续实施请求中确认执行。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage C 实施与本地 main 集成包
责任会话：main-codex-leader-comet-superpowers-visibility-20260531
当前门禁：本地 `main` 集成前运行目标检查、共享 local gate 和本地 MR review
Stage C 进入条件：已由用户 2026-05-31 的冷启动继续实施请求满足
最后更新：2026-05-31
<!-- CURRENT_STATUS_END -->

## 文件归属

- .codex/skills/comet/SKILL.md
- .codex/skills/comet-design/SKILL.md
- .codex/skills/comet-build/SKILL.md
- .codex/skills/comet-verify/SKILL.md
- docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md
- docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md
- tools/check_comet_superpowers_visibility.py
- tools/run_openspec_guard.py
- tools/safety_rule_script_backing_registry.json
- tools/ci/ci_test_manifest.json
- test/*superpowers*visibility*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- Comet skill instructions
- Superpowers skill invocation evidence

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 通过用户 2026-05-31 的冷启动继续实施请求确认本子方案进入实施。
- [x] 增加 using-superpowers、writing-plans、executing-plans、test-driven-development、verification-before-completion 和 finishing-a-development-branch 的证据预期。
- [x] 更新 Comet skill 文档，使 OpenSpec remains WHAT 且 Superpowers remains HOW。
- [x] 增加 checker 或测试覆盖，确保 Comet 声明 Superpowers 使用时不能缺少 HOW-layer evidence。
- [ ] Run skill boundary, Superpowers visibility, and local gate checks.
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的子方案更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## 验收标准

- 用户已在 2026-05-31 的继续实施请求中确认本子方案，且该确认发生在非文档实施前。
- active session claim 在写入工作开始前明确指向本子方案路径。
- 行为变更必须先有失败测试或 checker fixture。
- 治理文档、runtime helper、checker、测试和 CI 注册保持一致。
- 证据以轻量索引记录，不向本方案正文追加大型证据包。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-31 Stage C 启动：用户已确认实施；认领 `main-codex-leader-comet-superpowers-visibility-20260531` 串行拥有 Comet/Superpowers 可见性热点。
<!-- EVIDENCE_INDEX_END -->
