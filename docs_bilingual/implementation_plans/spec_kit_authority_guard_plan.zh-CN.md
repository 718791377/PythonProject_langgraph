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
状态：plan-updated；checker/runtime implementation pending
阶段：Stage D documentation-only update package
责任会话：update-spec-kit-runtime-plan-20260606
当前门禁：只更新本方案及其双语对照；运行 plan/OpenSpec/precommit/local gates，然后本地 main 集成并停在 remote-publication gate
Runtime boundary：本包不运行 `specify init`、不创建 `.specify/`、不安装或升级 Spec Kit、不生成命令文件，也不实现 checker/runtime 脚本
Priority update：2026-06-07 记录 Spec Kit 为最低优先级 subordinate template/probe surface；Checker + Runtime 仍是未来实现。
最后更新：2026-06-07
<!-- CURRENT_STATUS_END -->

## 冲突优先级

Spec Kit 不得高于 Comet、OpenSpec、Superpowers、gstack delivery-loop advisory checks、Codex harness candidate runtime guards、implementation-plan claims、本地 main 门禁或远端发布门。`specify init`、`.specify/`、`specs/`、`/speckit.*`、`$speckit-*` 继续保持 blocked/subordinate/do-not-run，除非未来 active implementation plan 与显式授权批准。未来 checker/runtime 必须输出 `authority_decision`。这里的 `authority_decision` 是机器可读 allow/block/subordinate 字段，用于记录胜出的 authority layer、原因与已应用的 priority outcome。

## 文件归属

- 未来扩展的既有 checker 目标：`tools/check_spec_kit_authority_guard.py`
- 未来扩展的既有测试目标：`test/*spec_kit*authority*`
- 由 subordinate adapter 方案拥有的未来 runtime 目标：`tools/spec_kit_subordinate_runtime.py`
- 治理边界：`docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md`

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- Spec Kit guard checker
- .specify path handling
- `tools/spec_kit_subordinate_runtime.py` 的未来 helper contract
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
- [x] 记录官方 `github/spec-kit` 参考源，以及未来 Checker + Runtime implementation boundary。
- [x] Record Spec Kit lowest-priority subordinate boundary; no Checker + Runtime scripts.
- [ ] Future Checker implementation：扩展 `tools/check_spec_kit_authority_guard.py`，使其按照 subordinate-adapter authority rule 校验所有 `.specify/`、`specs/`、`/speckit.*`、`$speckit-*`、`specify init`、`specify self check`、extension 或 preset 证据。 `authority_decision` 是记录胜出 authority layer 与原因的 allow/block/subordinate 字段。
- [ ] Future Runtime implementation：任何 live Spec Kit 命令前都必须先有受保护 dry-run/probe helper；live `specify init --here --force`、安装、升级、template 写入、agent-command 写入或 constitution 写入都必须具备显式操作者授权、receipt、rollback evidence 与单独 implementation approval。
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
- 2026-06-07 conflict-priority refresh：本 docs-only 包记录 Spec Kit 的最低优先级从属边界；不运行 `specify init`，不创建 `.specify/`，不实现 Checker + Runtime 脚本。
- 2026-06-06 Spec Kit reference refresh：branch `update-spec-kit-runtime-plan-20260606` 记录 `github/spec-kit` 官方来源与未来 Checker + Runtime 要求；未运行 `specify init`，也未实现脚本。
- 2026-05-28 Stage B 子方案创建：随父级多方案并行编排的子方案包创建；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-06-01 implementation package：新增 `tools/check_spec_kit_authority_guard.py`、`test/spec_kit_authority_guard.test.py`、从属适配器治理文档、CI manifest 注册、安全规则脚本支撑登记，以及 OpenSpec guard 集成；本地门禁前聚焦测试已通过。
<!-- EVIDENCE_INDEX_END -->
