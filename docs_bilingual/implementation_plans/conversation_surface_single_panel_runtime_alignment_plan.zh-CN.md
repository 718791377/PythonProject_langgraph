---
doc_id: conversation_surface_single_panel_runtime_alignment_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/conversation_surface_single_panel_runtime_alignment_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
confirmation_required: true
---

# Conversation Surface Single-Panel Runtime Alignment Plan 中文实施方案

> 面向 agentic worker：本方案经操作者确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；这里的 Markdown checkbox 只用于 implementation plan 内部任务追踪。

## 目标

把用户可见的 `Routing trace` 与 `Updated Plan` 会话表面在治理文档、checker fixture、用户级 runtime 生成器、已安装用户级产物以及两个通用项目模板中对齐。本修复防止 `experts_now` / `durable_team` 这类旧短格式 routing 示例再次出现，也防止用户可见 `Updated Plan` 面板被重复、嵌套或改写成 Markdown checkbox 清单。

## 来源方案

- `chinese_routing_trace_conversation_surface_plan` - 既有固定标签会话表面方案。
- `routing_trace_structured_evidence_schema_plan` - 结构化 routing evidence 字段契约。
- `codex_governance_session_visibility_and_plan_lock_plan` - plan 可见性与会话表面边界治理。
- `multi_plan_parallel_session_orchestration_plan` - 父级编排方案与防冲突治理上下文。

## 范围决策

- 防冲突优先级保持 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- 仓库范围：更新 `D:/PythonProject_langgraph` 内的项目治理、checker/runtime 源码、fixtures 与用户级安装器。
- 用户级范围：通过本仓库安装器刷新 `C:/Users/lenovo/.codex` 下生成/安装的 Codex team-mode 表面，并只记录 smoke 证据；安装产物不是 source of truth。
- 模板范围：仓库 runtime 完成后，更新 `D:/PythonProject_General` 与 `D:/PythonProject_General_2`，让其他项目和新电脑继承明确后的会话表面契约。
- 除非操作者显式要求远端 push、GitLab MR、GitLab merge 或 GitHub sync，否则远端发布不在范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：操作者已确认 active plan，等待本地 plan 集成到 local `main`
Owner session：`codex-conversation-surface-plan-20260612`
当前门禁：plan 提交、本地验证、本地 main 集成，然后进入 runtime 实现分支
远端发布：未授权；必须停在 remote-publication approval gate
最后更新：2026-06-12
<!-- CURRENT_STATUS_END -->

## 文件归属

- 方案与登记：本文件、英文主文件和 `docs_bilingual/docs_registry.yaml`。
- Runtime 实现切片：`docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`、`.zh-CN.md`、`tools/install-codex-user-level-team-mode.ps1`、`tools/check_orchestration_collaboration_evidenceguard.py`、`tools/check_orchestration_trace_evidence.py`、相关测试，以及 `test/fixtures/orchestration_prompt_independent_collaboration_parity/conversation_surface_*`。
- 模板实现切片：`D:/PythonProject_General` 与 `D:/PythonProject_General_2` 中承载会话表面契约的模板说明和 Codex agent/template assets。

## 热点串行规则

同一时间只能由一个 session 拥有以下热点：

- 用户可见 `Routing trace` 示例与字段名
- 用户可见 `Updated Plan` 渲染契约
- collaboration evidenceguard fixtures 与校验逻辑
- 用户级安装器生成的 `team-leader` instruction payload
- `PythonProject_General` 与 `PythonProject_General_2` 中的模板 AGENTS/team-leader 表面

## 任务清单

<!-- TASK_BACKLOG_START -->
- [ ] 先提交并合入本 implementation plan 到 local `main`，再开始 runtime 修改。
- [ ] 更新治理文案，使 `Routing trace` 使用完整 checker-compatible 字段集，`Updated Plan` 是单个 CLI/tree `✔`/`□` 面板。
- [ ] 替换安装器旧措辞和生成示例中的 `experts_now`、`durable_team=<...>`、`checkbox/status-list semantics` 或模糊 checklist semantics。
- [ ] 加强会话表面 checker 与 fixtures，拒绝重复 `Updated Plan`、嵌套 `Updated Plan`、Markdown checkbox `Updated Plan`、重复 `Routing trace` 和旧 routing 短字段。
- [ ] 运行 targeted checker tests、OpenSpec guard、本地 gate 和 local MR review。
- [ ] 从仓库源码重新安装或刷新用户级 team-mode runtime，并对已安装产物执行旧措辞 smoke search。
- [ ] 将 runtime 实现合入 local `main`，并停在 remote-publication gate。
- [ ] 更新 `D:/PythonProject_General`：先方案提交再模板实现提交，并合入 local `main`。
- [ ] 更新 `D:/PythonProject_General_2`：先方案提交再模板实现提交，并合入 local `main`。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- `python test/check_orchestration_collaboration_evidenceguard.test.py` - checks conversation-surface evidenceguard behavior.
- `python test/check_orchestration_trace_evidence.test.py` - checks full routing trace evidence fields.
- `python tools/run_openspec_guard.py --root .` - checks OpenSpec and repository governance guards.
- `python tools/check_precommit_update_archive.py --root . --json` - checks pre-commit update and archive readiness.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local MR review gate.
- 用户级 smoke：搜索已安装用户级表面中是否仍有 `checkbox/status-list semantics`、`experts_now`、`Routing trace: phase=..., experts_now` 和旧 `durable_team=<selected|not_selected>` 示例。
- 模板 smoke：对两个模板仓库执行同样旧措辞搜索，并确认任何剩余 `Updated Plan` guidance 都指向单个 CLI/tree `✔`/`□` 面板。

## 验收标准

- 治理/runtime 表面中的 `Routing trace` 示例使用完整字段名：`phase`、`capability_chain`、`backend_default`、`backend_ready`、`experts`、`durable_workflow`、`persistent_team`、`main_session_escalation`、`approval_timeout_risk`、`approval_receipt` 与 `why`。
- 当前用户可见 guidance 不再把 `experts_now` 或 `durable_team=<selected|not_selected>` 当作 live routing trace contract。
- `Updated Plan` guidance 明确为单个用户可见 CLI/tree 进度面板，使用 `✔` 与 `□`；Markdown checkbox 只保留给 implementation plan 文件。
- Checker fixtures 拒绝重复/嵌套 `Updated Plan` 输出和重复/旧字段 `Routing trace` 输出。
- 用户级已安装产物和两个模板通过旧措辞残留 smoke search。
- 仓库与模板变更只提交并合入各自 local `main`；远端发布继续受门禁保护。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- Evidence is pending until the plan commit, runtime implementation commit, user-level smoke, template updates, local gates, and local main integrations complete.
<!-- EVIDENCE_INDEX_END -->
