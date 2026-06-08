---
doc_id: parallel_plan_checker_ci_integration_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/parallel_plan_checker_ci_integration_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 7
batch: 5
confirmation_required: true
---

# Parallel Plan Checker CI Integration Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

Ensure every new checker, test, and helper introduced by child plans is registered in local and mirrored CI gates.

## 来源方案

- multi_plan_parallel_session_orchestration_plan; automatic_orchestration_routing_enforcement_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 5。
- 阶段：Phase 7。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Stage: Stage C implementation package
Owner session: codex-20260603-parallel-plan-checker-ci
Current gate: implementation package is ready for feature validation, local MR review, local main integration, and then the remote-publication approval gate
Stage C entry condition: satisfied by the user's 2026-06-03 implementation request after the governance package was already merged into local main
Last updated: 2026-06-03
Status update: mirrored-CI checker now validates CI manifest required tests, guard/precommit/safety-rule registration surfaces, canonical local-gate step order, required remote shared-gate flags, and absence of inline remote CI duplication for guard and manifest test runners.
<!-- CURRENT_STATUS_END -->

## 文件归属

- tools/ci/local_gate.ps1
- tools/ci/local_mr_review.ps1
- tools/check_local_mirrored_ci_gate.py
- test/*ci*integration*

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- local gate script
- CI manifest or workflow config

## 并行会话契约

- 本阶段最大并行 session 数：1。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Inventory new checkers and tests from completed child plans.
- [x] Add missing local gate registrations and mirrored CI checks.
- [x] Detect divergence between local and remote CI command sequences.
- [x] Run local gate and local MR review.
- [x] Verify MCP baseline, receipt/redaction, browser-owner, MCP/skills discovery, and adapter guard checks are registered when their extracted lanes change runtime behavior.
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
- 2026-06-01 receipt/redaction lane handoff: `user_level_capability_receipt_rollback_redaction_plan` confirms `tools/user_level_receipt_governance.py`, `test/user_level_receipt_governance.test.py`, the MCP baseline checker, OpenSpec guard registration, and `tools/ci/ci_test_manifest.json` coverage for the receipt lane; future sibling lane changes still need their own registration review.
- 2026-06-01 port/browser-owner lane handoff: `user_level_port_browser_owner_isolation_plan` 确认 `test/codex_port.test.py`、`test/browser_owner_registry.test.py`、`test/cdp_bridge_governance.test.py` 与 `test/chrome_devtools_mcp_managed.test.py` 已登记进 CI manifest；CDP/OpenCLI owner 歧义回归覆盖扩展了既有已登记测试文件，因此无需编辑 CI manifest。
- 2026-06-01 discovery facade lane handoff: `skills2cli.test.py` 与 `mcp2cli.test.py` 已登记进 CI manifest；本包扩展这些已登记聚焦测试以覆盖 risk-profile 与 routing-evidence 行为，并确认 baseline/MCP-scope/agent-surface checker 仍适用。
- 2026-06-01 browser/CLI adapter boundary lane handoff: `user_level_browser_cli_adapter_boundary_plan` 扩展已登记的 MCP baseline checker，用于校验子方案 implemented-local 状态与 lane-state evidence；聚焦覆盖仍位于已登记测试 `chrome_devtools_mcp_managed.test.py`、`cdp_bridge_governance.test.py`、`wecom_cli_governance.test.py`、`user_level_receipt_governance.test.py` 和 `check_user_level_mcp_skills_browser_cli_baseline.test.py`，无需修改 CI manifest。
- 2026-06-03 Stage C implementation: `tools/check_local_mirrored_ci_gate.py` now checks CI manifest structure and required tests, local-gate step ordering, OpenSpec guard/precommit/safety-rule registration surfaces, remote shared-gate flags, and forbidden inline CI duplication for guard or manifest test runners; `test/check_local_mirrored_ci_gate.test.py`, `test/parallel_plan_checker_ci_integration.test.py`, and `tools/ci/ci_test_manifest.json` provide focused CI-registered regression coverage.
<!-- EVIDENCE_INDEX_END -->
