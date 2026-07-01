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

# Durable 能力 Ready 状态投影方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案定义 installed、enabled、selected、ready 的投影与显式刷新，不直接安装 runtime。

## 目标

把 durable lane 的状态明确投影为 `installed`、`enabled`、`selected` 与 `ready`，禁止把这些状态折叠成一个粗略 availability flag。

## 来源方案

- codex_user_level_cross_session_durable_state_isolation_plan；automatic_orchestration_routing_enforcement_plan
- 关联治理文档：`docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md`

## 范围决策

- `installed` 表示 runtime 或 helper 可被发现。
- `enabled` 表示 capability switch 允许使用。
- `selected` 表示当前 task flow 或 selector 选择该 lane。
- `ready` 表示 preflight、receipt、selector 与 smoke/adoption gate 均满足。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for `durable_capability_readiness_projection_plan`.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `durable-capability-readiness-projection`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
<!-- CURRENT_STATUS_END -->

## 文件归属

- `tools/check_capability_switch_chain.py` - 校验 capability switch 依赖链与禁用/启用边界。
- `tools/check_effective_lane_fit_evidence.py` - 校验 native_omx 与 LangGraph lane fit 证据。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` - 说明用户级 LangGraph runtime 安装与 readiness 边界。
- `test/*capability*readiness*` - 覆盖 capability readiness 投影与状态刷新行为。
- 后续 `.omx/state/*readiness*` fixture 或 receipt schema。

## 热点串行规则

capability switch chain、selector schema、readiness projection schema 与 CI guard 注册必须串行。

## 并行会话契约

一个 session 独占本 implementation_plan。其他 session 可做 selector 或 receipt runtime，但 readiness projection schema 的变更必须在本方案下串行合入。

## 任务清单

## Runtime Refresh Scope（runtime refresh 范围）

Stage D/R4 已实现显式 readiness projection refresh：`codex-durable-state-status.ps1 -RefreshReadiness` 会写入 repo-local readiness projection receipt；默认 status path 仍保持只读。后续可以继续扩展更深的 source evidence，但不得折叠 installed/enabled/selected/ready 字段。

<!-- TASK_BACKLOG_START -->
- [x] Stage B：定义 installed/enabled/selected/ready 不能折叠。
- [x] Stage B：把 capability switch chain 与 lane-fit evidence 接入检查。
- [x] Stage C：记录 readiness projection 的真实 runtime gap。
- [x] Stage D/R4：实现显式 readiness probe/refresh helper，刷新 native_omx 与 LangGraph 的 installed、enabled、selected、ready 字段且不折叠状态。
- [x] Stage D/R4：记录 source receipt、timestamp、backend family、selector evidence、version evidence 与 blockers，写入 sanitized projection receipt。
- [x] Stage D/R4：将 projection refresh metadata 接入 status/activation evidence，同时明确不声明 durable workflow adoption 或 persistent-team launch。
<!-- TASK_BACKLOG_END -->

## Stage D runtime work（已实现 runtime refresh）

- Stage D/R4 runtime：通过显式 `-RefreshReadiness` 写入 readiness projection receipt。
- Stage D/R4 runtime：receipt 字段包含 installed、enabled、selected、ready、blockers、generated_at 与 source receipts。
- Stage D/R4 runtime：默认 status path 不创建 `.omx`，避免把只读状态检查变成 durable adoption 或 team launch。

## 验证门禁

- `python tools/check_capability_switch_chain.py --root . --json` - 验证 capability switch 链路。
- `python tools/check_effective_lane_fit_evidence.py --root . --json` - 验证 lane-fit evidence。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文，保留必要 token。
- readiness 报告必须能说明每个状态的来源和 blocker。
- Stage D/R4 refresh 不得被表述为 durable workflow adoption 或 persistent-team launch。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 durable capability readiness projection 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-06 Stage D/R4 runtime refresh：分支 `implement-durable-capability-readiness-r4-20260605` 增加显式 `codex-durable-state-status.ps1 -RefreshReadiness -Json` receipt 生成，写入 `.omx/state/readiness/durable-capability-readiness-projection.json`；保留独立 readiness 字段以及 source/selector/version/blocker 证据，并记录 `durable_workflow_adopted=false` 与 `persistent_team_launched=false`；目标验证 `python .\test\check_capability_switch_chain.test.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1`、`python .\tools\run_openspec_guard.py --root .` 与 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` 已于 2026-06-06 通过。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 runtime probe/refresh installed/enabled/selected/ready 投影列为 Stage D pending；本 R4 包补齐显式 refresh receipt runtime。
- 2026-05-30 Stage C 实施：`tools/check_capability_switch_chain.py` 现在校验 durable capability readiness projections，要求区分 `installed`、`enabled`、`selected`、`ready` 四个字段，并强制 `ready == installed && enabled && selected` 不变量。
- 2026-05-30 Stage C fixtures：`test/check_capability_switch_chain.test.py` 覆盖 installed-only、enabled-not-selected、selected-not-ready、ready、collapsed-ready 与 missing-field readiness 状态。
- 2026-05-30 Stage C 文档：`docs_bilingual/governance/langgraph_user_level_runtime_policy.md` 与 `.zh-CN.md` 记录 `backend_default` / `backend_ready` 对外措辞，并澄清 readiness 不表示当前任务已经采用 durable workflow、tracked thread 或 persistent team。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
<!-- EVIDENCE_INDEX_END -->
