---
doc_id: spec_kit_subordinate_adapter_governance_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/spec_kit_subordinate_adapter_governance_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Subordinate Adapter Governance Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

将 GitHub Spec Kit 记录为可选的 subordinate adapter / template / runtime-probe 来源；任何 Spec Kit 命令或生成模板影响本仓库前，都必须先有未来 checker 与受保护 runtime implementation。

## 来源方案

- codex_governance_session_visibility_and_plan_lock_plan

## 参考源

- `https://github.com/github/spec-kit` - 官方仓库与 README；记录 `specify init`、`/speckit.constitution` -> `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement` 工作流、可选 `/speckit.clarify`、`/speckit.analyze`、`/speckit.checklist`，以及 Codex skills-mode `$speckit-*` 表面。
- `https://github.github.io/spec-kit/` - 官方文档首页；记录 Spec Kit 作为 Spec-Driven Development toolkit，以及 Spec -> Plan -> Tasks -> Implement artifact chain。
- `https://github.github.io/spec-kit/reference/core.html` - 官方 core command reference；记录 initialization、integration、PowerShell script selection、force/overwrite、no-git 与 self-check 命令边界。

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和 runtime 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 4。
- 阶段：Phase 6。
- 状态：本文件是 active 子 implementation_plan，但在本地 `main` 合入后仍必须等待用户确认，才能开始非文档实现。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: R4 implemented as a dry-run checker/runtime package
Stage: R4 Checker + Runtime implementation package
Owner session: implement-spec-kit-authority-guard-r4-20260607
Current gate: local-main-first validation and integration for this package; after local integration, stop at the remote-publication gate
Runtime boundary: dry-run only; this package records and implements dry-run/probe runtime support without installing Spec Kit, running `specify init`, writing `.specify/`, creating root `specs/`, or exposing `/speckit.*`/`$speckit-*` commands
Priority update: 2026-06-07 keeps Spec Kit as the lowest-priority subordinate adapter behind Comet, OpenSpec/Superpowers, gstack, and Codex harnesses.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## 冲突优先级

本 adapter 不得高于 Comet、OpenSpec、Superpowers、gstack delivery-loop advisory checks、Codex harness candidate runtime guards、implementation-plan claims、local-main-first gates 或 remote-publication gates。它只能在 authority checks 通过后，把 Spec Kit artifacts 翻译为可审查的 subordinate inputs。受保护 runtime 模式必须记录 `authority_decision`、`source_url`、`source_pin`、`dry_run_only`、receipt/rollback paths，以及 `specify init`、`.specify/`、`specs/`、`/speckit.*`、`$speckit-*` 是否仍保持 blocked/subordinate/do-not-run。这里的 `authority_decision` 是机器可读 allow/block/subordinate 字段，用于记录胜出的 authority layer 与已应用的 priority outcome。

## 文件归属

- 治理文档：`docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md` 与 `.zh-CN.md`
- 既有 authority checker consumer：`tools/check_spec_kit_authority_guard.py`
- 未来 runtime helper 目标：`tools/spec_kit_subordinate_runtime.py`
- 未来测试：`test/spec_kit_subordinate_runtime.test.py` 与既有 Spec Kit authority tests
- 只有新增文档时才触碰 registry hotspot：`docs_bilingual/docs_registry.yaml`

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- new governance doc registry entries
- 未来 `tools/spec_kit_subordinate_runtime.py` helper 与 tests
- `.specify/`、`specs/`、slash-command 与 skills-mode generated surfaces

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Document authority order: Comet controls OpenSpec WHAT and Superpowers HOW; Spec Kit may only provide subordinate templates unless a separate plan changes that.
- [x] Add usage boundaries for any future specify command.
- [x] Register the new governance pair if created.
- [x] Run docs registry and implementation-plan checks.
- [x] Record official `github/spec-kit` reference sources and future Checker + Runtime implementation requirements.
- [x] Record lowest-priority subordinate-adapter conflict handling behind Comet, OpenSpec/Superpowers, gstack, and Codex harnesses.
- [x] R4 Checker implementation: verify subordinate adapter usage for Spec Kit artifacts, command files, skills-mode `$speckit-*` surfaces, generated templates, extensions, presets, and workflow outputs without allowing governance-authority migration; require `authority_decision` evidence.
- [x] R4 Runtime implementation: add `tools/spec_kit_subordinate_runtime.py` with `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run` modes; live/apply mode names are rejected and all supported modes remain dry-run only with receipts, rollback pointers, redacted output, timeout controls, and local-main-first validation evidence.
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
- 2026-06-07 R4 implementation package: implemented dry-run-only Spec Kit subordinate runtime receipts plus checker validation for generated Spec Kit surfaces and receipt authority decisions; no live Spec Kit command, install, `.specify/`, root `specs/`, `/speckit.*`, or `$speckit-*` surface was created.
- 2026-06-07 conflict-priority refresh：本 docs-only package 记录 Spec Kit 只作为 subordinate adapter/template/probe；live 或 apply modes 仍延后到未来 Checker + Runtime implementation 与显式授权之后。
- 2026-06-06 Spec Kit reference refresh：branch `update-spec-kit-runtime-plan-20260606` 记录官方 `github/spec-kit` references 与未来 Checker + Runtime helper 要求；未安装或运行 Spec Kit。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-01 Stage C 实施：复用已注册的 `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md` 与 `.zh-CN.md` 治理文档对，补充未来 `specify` 命令边界措辞，并将本子方案标记为 implemented-local；验证证据记录在本地命令输出和最终 assistant 回复中。
<!-- EVIDENCE_INDEX_END -->
