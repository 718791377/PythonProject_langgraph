---
doc_id: parallel_plan_openspec_comet_archive_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/parallel_plan_openspec_comet_archive_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 7
batch: 5
confirmation_required: true
---

# Parallel Plan OpenSpec Comet Archive Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Validate OpenSpec and Comet guard health and archive completed changes as one serial integration package when appropriate.

## 来源方案

- multi_plan_parallel_session_orchestration_plan; comet_runtime_agile_focus_area_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 5。
- 阶段：Phase 7。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: archive package implemented locally; complete local flow will integrate this package into local `main`.
Stage: Stage C Phase 7 OpenSpec/Comet archive package.
Owner session: `codex-20260603-parallel-plan-openspec-comet-archive`.
Current gate: run `tools/complete_local_flow_to_remote_gate.py` for local `main` integration, then stop at the remote-publication approval gate.
Stage C entry condition: satisfied by the 2026-06-03 user confirmation for this child implementation plan, local git commit, and local `main` integration.
Last updated: 2026-06-03.
Status update: `refactor-user-level-mcp-governance-modern-structure` is archived to `openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure/`. Stable-spec sync is skipped because the current stable MCP/skills/browser/CLI spec already has broader current coverage. Remaining complete active changes are deferred because their verify, branch-handling, source-plan, or archive-readiness evidence is outside this single serial archive package.
<!-- CURRENT_STATUS_END -->

## 文件归属

- openspec/changes/*
- openspec/specs/*
- docs/superpowers/*
- tools/run_openspec_guard.py

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- OpenSpec stable specs
- openspec archive directories

## 并行会话契约

- 本阶段最大并行 session 数：1。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration; the current user request records the implementation confirmation.
- [x] Identify completed active OpenSpec changes that must archive before final integration; this package selects `refactor-user-level-mcp-governance-modern-structure`.
- [x] Run official OpenSpec verification and Comet guard checks for the selected archive package.
- [x] Promote stable spec deltas only after implementation validation is complete; stable-spec sync is skipped because existing stable coverage is broader than the historical delta.
- [x] Run archive validation and local gate before local `main` integration.
- [x] Before archiving MCP/skills/browser/CLI OpenSpec work, record each extracted child lane state. Receipt/redaction, port/browser-owner, discovery facade, and browser/CLI adapter boundary are implemented-local; the broader source surface is partially archived by `refactor-user-level-mcp-governance-modern-structure`; remaining complete active changes are deferred to later evidence-owned archive packages.
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
- 2026-06-03 Phase 7 archive implementation: archived `refactor-user-level-mcp-governance-modern-structure` to `openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure/`; stable-spec sync was skipped to avoid replacing broader current stable MCP/skills/browser/CLI coverage with the older narrow delta; remaining complete active changes are deferred because their verify/branch/archive evidence is outside this package write ownership.
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-01 receipt/redaction archive note: `user_level_capability_receipt_rollback_redaction_plan` is implemented-local; no live user-level install or sensitive runtime action was performed, and the related stable spec already contains the generic receipt governance requirement. Archive timing remains a Phase 7 decision for the broader MCP/skills/browser/CLI source surface.
- 2026-06-01 port/browser-owner archive note: `user_level_port_browser_owner_isolation_plan` 已 implemented-local；本包仅补强仓库本地 guard 与测试，不执行 live browser start 或 sensitive runtime action；archive timing 仍由更广 MCP/skills/browser/CLI source surface 的 Phase 7 决策处理。
- 2026-06-01 discovery facade archive note: `user_level_mcp_skills_discovery_facade_plan` 已 implemented-local；仅修改 repo-local facade helpers/tests，不执行 live MCP/browser/runtime action，source surface archive timing 仍交由 Phase 7 处理。
- 2026-06-01 browser/CLI adapter boundary archive note: `user_level_browser_cli_adapter_boundary_plan` 已 implemented-local；本包仅修改 repo-local checker/plan evidence，不执行 live browser start、GUI automation、install、cookie read 或 sensitive runtime action；更广 source surface archive timing 仍交给未来 Phase 7 archive package。
<!-- EVIDENCE_INDEX_END -->
