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

## 原生表面修正

- Codex 原生 `update_plan` 工具渲染结果就是 canonical 用户可见 `Updated Plan` 面板。该原生面板已经出现时，assistant 正文不得再手写第二个 `Updated Plan` 标题、嵌套 `Updated Plan` 树节点或 Markdown checkbox 镜像。
- 如果没有输出原生计划面板但仍需要简短文字进度，可以使用 `执行进度` 等非冲突标签；不得冒充原生 `Updated Plan` 面板。
- `Routing trace` 仍然是单个普通文本 activation 诊断。如果外层 wrapper/runtime 已经为当前 activation 注入 trace，assistant 正文不得再输出第二个 `Routing trace` 块。
- Checker 必须把 `• Updated Plan` 这类原生 transcript 前缀识别为同一个 `Updated Plan` 表面并纳入去重计数，同时拒绝同一响应 evidence 后续又出现手写 `Updated Plan:` 块。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: repository runtime, user-level install refresh, native `update_plan` / `Routing trace` single-surface deduplication, and both general template propagations are complete for this implementation pass.
Owner session: `conversation-surface-native-dedup-20260613` plus closeout session `closeout/conversation-surface-native-dedup-20260614`
Current gate: clean integrated local feature worktrees/claims, keep local `main` as the carrier, and stop at the remote-publication approval gate
Remote publication: not authorized; `gitlab/main` and `github/main` remain publication-gated until the operator explicitly requests remote publication
Last updated: 2026-06-14
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
- [x] Commit and merge this implementation plan into local `main` before runtime edits.
- [x] Update governance text so `Routing trace` uses the full checker-compatible field set and `Updated Plan` is one CLI/tree panel using checkmark (U+2714) and empty-square (U+25A1) status glyphs.
- [x] Replace old installer wording and generated examples that mention `experts_now`, `durable_team=<...>`, `checkbox/status-list semantics`, or ambiguous checklist semantics.
- [x] Harden conversation-surface checker logic and fixtures against duplicate `Updated Plan`, nested `Updated Plan`, Markdown checkbox `Updated Plan`, duplicate `Routing trace`, and old routing short fields.
- [x] Run targeted checker tests, OpenSpec guard, and pre-commit update/archive checks for the runtime slice.
- [x] Reinstall or refresh user-level team-mode runtime from repository source and smoke-search installed artifacts for old wording, including the generated `user-level-team-mode-model-instructions.md` cache.
- [x] Record the native `update_plan` panel as the canonical `Updated Plan` surface and ban assistant-written duplicate `Updated Plan` headings after a native panel.
- [x] Extend checker logic and fixtures so `• Updated Plan` counts as the native panel label, native-plus-handwritten duplicate evidence fails, and non-conflicting prose progress labels remain allowed outside the `Updated Plan` surface.
- [x] Extend routing trace guidance so an already injected trace suppresses assistant-written duplicate `Routing trace` output for the same activation.
- [x] Run full local gate and local MR review for the committed runtime implementation.
- [x] Merge the runtime implementation into local `main` and stop at the remote-publication gate.
- [x] Update `D:/PythonProject_General` with a plan commit followed by a template implementation commit and local main integration.
- [x] Update `D:/PythonProject_General_2` with a plan commit followed by a template implementation commit and local main integration.
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
- Checker fixtures 拒绝重复/嵌套 `Updated Plan` 输出、原生面板后再手写 `Updated Plan:` 镜像，以及重复/旧字段 `Routing trace` 输出。
- Runtime guidance 明确要求 assistant 依赖原生 `update_plan` 面板，不再额外写一个 prose `Updated Plan` 块。
- 用户级已安装产物和两个模板通过旧措辞残留 smoke search。
- 仓库与模板变更只提交并合入各自 local `main`；远端发布继续受门禁保护。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- Plan integration: local `main` contains plan commit `ea9a442`.
- Runtime checks passed: `python test/check_orchestration_collaboration_evidenceguard.test.py`, `python test/check_orchestration_trace_evidence.test.py`, `python test/check_stop_slop_caveman_response_density.test.py`, `python test/check_fanout_write_ownership_evidence.test.py`, `python test/check_windows_cleanup_output_control.test.py`.
- Installer test passed: `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`.
- User-level install executed with `tools/install-codex-user-level-team-mode.ps1 -Force`; manifest listed `C:/Users/lenovo/.codex/state/user-level-team-mode-model-instructions.md` as a generated managed artifact.
- User-level smoke passed: `team-leader.toml`, `codex-routing-policy.ps1`, `_codex-user-level-team-mode.ps1`, `_codex-user-level-team-mode-launcher.ps1`, and `user-level-team-mode-model-instructions.md` had no `experts_now`, no old `durable_team=<selected|not_selected>` example, no `checkbox/status-list semantics`, and no Markdown checkbox `Updated Plan` surface.
- Repository guards passed: `python tools/check_precommit_update_archive.py --root . --json`, `python tools/check_launcher_payload_context_boundary.py --root . --json`, and `python tools/run_openspec_guard.py --root .`.
- Native surface dedup checks passed on 2026-06-14: `python test/check_orchestration_collaboration_evidenceguard.test.py`, `python test/check_orchestration_trace_evidence.test.py`, and `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json`.
- Native surface runtime refresh passed on 2026-06-14: `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`, `python tools/run_openspec_guard.py --root .`, `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install-codex-user-level-team-mode.ps1 -Force`, and installed-artifact smoke for old wording/new boundary phrases.
- Runtime local gate evidence passed on local `main`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1800`; generated `local-gate-report.json` / `openspec-guard-report.json` at 2026-06-14T08:41:17Z.
- Local MR review evidence passed on local `main`: `.\tools\ci\local_mr_review.ps1` reported `commits=0 changed_files=0 dirty_files=0` and `local_mr_review: ok` on 2026-06-14.
- Runtime local-main integration evidence: local `main` contains merge commit `73950f8` and feature commit `85745a4`.
- `D:/PythonProject_General` template propagation evidence: local `main` contains plan commit `3fc47e6`, implementation commit `9dcd451`, and registry-format fix `4a7d858`; `python D:/PythonProject_General/tools/check_conversation_surface_contract.py --root D:/PythonProject_General --json` passed with zero legacy hits.
- `D:/PythonProject_General_2` template propagation evidence: local `main` contains plan commit `3d2ee23`, implementation commit `c99ae4c`, and registry-format fix `1952f6d`; `python D:/PythonProject_General_2/tools/check_conversation_surface_contract.py --root D:/PythonProject_General_2 --json` passed with zero legacy hits.
- Template smoke evidence on 2026-06-14: both templates contain no live `experts_now`, no old `durable_team=<selected|not_selected>` routing example, no `checkbox/status-list semantics`, and their remaining `Updated Plan` guidance points to a single CLI/tree panel using U+2714/U+25A1 status markers.
- Remote publication evidence: no remote push, GitLab MR, GitLab merge, or GitHub sync was executed in this closeout; remote publication remains gated by explicit operator approval.
<!-- EVIDENCE_INDEX_END -->
