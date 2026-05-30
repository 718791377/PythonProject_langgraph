---
doc_id: collaboration_evidenceguard_and_bilingual_openspec_surface_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/collaboration_evidenceguard_and_bilingual_openspec_surface_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Collaboration Evidenceguard And Bilingual OpenSpec Surface Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Give the orchestration collaboration evidenceguard and bilingual OpenSpec stable spec surface a single owner so checker, fixture, CI, and spec updates do not scatter across Phase 4 work.

## 来源方案

- automatic_orchestration_routing_enforcement_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 3。
- 阶段：Phase 4。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：implementation-in-progress
阶段：Stage C collaboration evidenceguard and bilingual OpenSpec surface package
责任会话：codex-collaboration-evidenceguard-bilingual-openspec-20260530
当前门禁：已记录用户确认；checker、fixture registration、双语 OpenSpec、CI manifest 与 focused regression test 更新已准备进入 local gate 和 local MR review，之后再合入本地 main
Stage C 进入条件：已由 2026-05-30 用户请求继续并本地合入本子方案实现而满足
最后更新：2026-05-30
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/check_orchestration_collaboration_evidenceguard.py
- test/fixtures/orchestration_*
- test/check_orchestration_collaboration_evidenceguard.test.py
- openspec/specs/codex-user-level-orchestration-activation-policy/spec.md
- openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md
- tools/ci/ci_test_manifest.json

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- tools/check_orchestration_collaboration_evidenceguard.py
- openspec/specs/codex-user-level-orchestration-activation-policy/spec.md
- openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md
- tools/ci/ci_test_manifest.json

## 并行会话契约

- 本阶段最大并行 session 数：3。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Inventory evidenceguard requirements that are not already owned by narrower Phase 4 child plans.
- [x] Add bilingual OpenSpec spec statements for evidenceguard authority and saved evidence requirements.
- [x] Register new evidenceguard fixtures and CI tests in one serialized update.
- [x] Run OpenSpec guard, evidenceguard tests, mirrored CI check, and local gate.
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
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-30 Stage C 实现包：增加 required evidenceguard fixture registration、manifest-registered collaboration evidenceguard regression test 与双语 OpenSpec fixture-surface requirement；local gate 和 local MR review 证据记录在会话回复和 worktree receipt 中。
<!-- EVIDENCE_INDEX_END -->
