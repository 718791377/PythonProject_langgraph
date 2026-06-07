---
doc_id: spec_kit_authority_guard_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/spec_kit_authority_guard_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Authority Guard Plan（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

更新 Spec Kit 权威边界：未来 checker 与受保护 runtime helper 可以消费 GitHub Spec Kit，但不得让 `specify init`、`.specify/`、`specs/`、`/speckit.*` 或 `$speckit-*` 成为与本仓库既有治理并列或竞争的权威层。

## 来源方案

- codex_governance_session_visibility_and_plan_lock_plan

## 参考源

- `https://github.com/github/spec-kit` - 官方 Spec Kit 仓库与 README；记录 `specify init`、`/speckit.constitution`、`/speckit.specify`、`/speckit.plan`、`/speckit.tasks`、`/speckit.implement` 以及 Codex skills-mode `$speckit-*` 命令表面。
- `https://github.github.io/spec-kit/` - 官方文档首页；记录 Spec -> Plan -> Tasks -> Implement 的 SDD 流程与多 agent 集成模型。
- `https://github.github.io/spec-kit/reference/core.html` - 官方 core command reference；记录 `specify init` 的 `--integration`、`--script`、`--here`、`--force`、`--no-git`、`--ignore-agent-tools` 等选项，以及 `specify self check` 边界。

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
Owner session: implement-spec-kit-authority-guard-r4-closeout-20260607
Current gate: 先 archive 本有界 R4 closeout package，重新运行本地验证，然后合入本地 `main`，并停在 remote-publication gate
Runtime boundary: dry-run only; this package does not run `specify init`, does not create `.specify/` or root `specs/`, does not install or upgrade Spec Kit, and does not expose generated `/speckit.*` or `$speckit-*` command surfaces
Priority update：2026-06-07 将 Spec Kit 固定为位于 Comet、OpenSpec/Superpowers、gstack 与 harness runtime safety 之后的最低优先级 subordinate template/probe surface。
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## 冲突优先级

Spec Kit 严格服从 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 这一优先级顺序。`specify init`、`.specify/`、`specs/`、`/speckit.*`、`$speckit-*` 继续保持 blocked/subordinate/do-not-run，除非未来 active implementation plan 与显式授权批准。未来 checker/runtime 必须输出 `authority_decision`。这里的 `authority_decision` 是机器可读 allow/block/subordinate 字段，用于记录胜出的 authority layer、原因与已应用的严格 priority outcome。

## 文件归属

- 未来扩展的既有 checker 目标：`tools/check_spec_kit_authority_guard.py`
- 既有 authority 测试目标：`test/spec_kit_authority_guard.test.py`
- R4 runtime 目标：`tools/spec_kit_subordinate_runtime.py` 与 `test/spec_kit_subordinate_runtime.test.py`
- 治理边界：`docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md`

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- Spec Kit guard checker
- .specify path handling
- `tools/spec_kit_subordinate_runtime.py` 的 dry-run helper contract 与 runtime test coverage
- parent plan size edits 与 docs registry references

## 并行会话契约

- 本阶段最大并行 session 数：2。
- 本子方案是一个认领单元：同一时间只能有一个 active session 认领。
- 只有认领不同子方案且写入范围互不重叠时，才允许并行实施。
- 本地 `main` 写入仍然串行，但由 `local-main-retire.lock` 保护；持锁 session 只能自退休自己拥有且已 ready 的候选包，并在远端发布门停止。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add tests for safe references to Spec Kit docs and unsafe authority-changing operations.
- [x] Implement a checker that fails closed on .specify governance takeover without an active plan.
- [x] Register the checker in the local gate only after implementation confirmation.
- [x] Run Spec Kit guard tests and local gate.
- [x] Record official `github/spec-kit` reference sources and future Checker + Runtime implementation boundary.
- [x] 记录严格优先级：Spec Kit 位于 Comet、OpenSpec/Superpowers、gstack 与 harness runtime safety 之后。
- [x] R4 Checker implementation: extend `tools/check_spec_kit_authority_guard.py` to validate `.specify/`, root `specs/`, generated `/speckit.*`, `$speckit-*`, `.codex/commands/*speckit*`, `.codex/skills/*speckit*`, `.github/prompts/*speckit*`, root `speckit.*`, root `speckit-*`, extension, preset, and workflow-output surfaces, plus machine-readable `authority_decision` receipt evidence.
- [x] R4 Runtime implementation: add `tools/spec_kit_subordinate_runtime.py` with `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run`; all modes are dry-run only and live/apply modes are rejected.
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
- 2026-06-07 R4 implementation package: added dry-run-only `tools/spec_kit_subordinate_runtime.py`, extended `tools/check_spec_kit_authority_guard.py` receipt and generated-surface validation, added `test/spec_kit_subordinate_runtime.test.py`, extended authority guard tests, and registered runtime/test/script backing before local gates.
- 2026-06-07 R4 closeout package：将严格 authority order 收紧为 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`，提升 stable safety-rule requirement，并在合入本地 main 前 archive 有界 closeout change。
- 2026-06-07 conflict-priority refresh：本包记录严格优先级 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`；不运行 `specify init`，不创建 `.specify/`，所有 runtime 仍为 dry-run only。
- 2026-06-06 Spec Kit reference refresh：branch `update-spec-kit-runtime-plan-20260606` 记录 `github/spec-kit` 官方来源与未来 Checker + Runtime 要求；未运行 `specify init`，也未实现脚本。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-01 implementation package：新增 `tools/check_spec_kit_authority_guard.py`、`test/spec_kit_authority_guard.test.py`、从属适配器治理文档、CI manifest 注册、安全规则脚本支撑登记，以及 OpenSpec guard 集成；本地门禁前聚焦测试已通过。
<!-- EVIDENCE_INDEX_END -->
