---
doc_id: gstack_codex_delivery_loop_runtime_governance_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B follow-up child plan
phase: 4
batch: 3
confirmation_required: true
---

# gstack Codex Delivery Loop Runtime 治理方案

> 给 agentic worker：使用 `superpowers:executing-plans`；只有写入范围互不重叠时才并行使用子代理。本包只记录 checker 加 runtime 目标，不创建脚本、不安装 gstack、不启用 runtime 行为。

## 目标

新增 Phase 4 子方案，把 `garrytan/gstack` 工作流治理 fork 成 Codex 本地 delivery-loop 检查与受保护的未来 runtime 目标。

## 参考源

| 参考源 | 必须继承的要求 |
| --- | --- |
| https://github.com/garrytan/gstack | AI 辅助软件交付流程：Think、Plan、Build、Review、Test、Ship、Reflect；角色化 review skills、浏览器 QA、发布检查、安全护栏、Codex second opinion、team mode、Codex host install target、opt-in telemetry 边界。 |
| https://gstack.lol/ | 后续 source refresh 的公开入口链接。本会话在 2026-06-06 本地 DNS 检查失败，因此本包以 GitHub README 作为已核验主参考。 |

## 范围决定

- 层级：先作为 `D:/PythonProject_langgraph` 的项目级治理与项目级 runtime 方案。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`。
- 阶段：Phase 4，因为它影响 Codex 对话工作流、plan/review/QA/ship 纪律和用户可见 delivery-loop 状态。
- 本包：只更新方案、registry 和父方案索引；不创建 checker、runtime helper、hook、skill install、MCP wrapper，不启动浏览器，不 clone gstack，不设置 telemetry，不修改用户级配置。
- 后续实现：必须达到 checker 加 runtime 层级后，才能声明 ready。
- 远端发布：除非用户明确要求 remote publication，否则不在范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: active child-plan definition; code work is not started.
Stage: documentation package records the checker plus runtime requirement and source links.
Owner session: `plan-gstack-codex-delivery-loop-20260606` only owns this plan-document package.
Current gate: validate implementation-plan rules, OpenSpec guard, precommit update/archive review, local gate, and local MR review before local main integration. Remote publication is not authorized.
Runtime boundary: no gstack runtime is installed, cloned, enabled, invoked as a hook, registered as a skill, connected to browser QA, or promoted to user level by this package.
<!-- CURRENT_STATUS_END -->

## Checker 与 Runtime 目标

后续代码包必须先提供这些 repo-local 表面，才能声称达到 R2 readiness：

- `tools/check_gstack_codex_delivery_loop.py --root . --json` 校验保存的 delivery-loop evidence、plan/checker/runtime 登记和参考源新鲜度。
- `tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` 报告当前 Codex delivery-loop 阶段与缺失 evidence，不写文件。
- `tools/gstack_codex_delivery_loop_runtime.py plan-dry-run --root . --json` 给出 Think/Plan/Build/Review/Test/Ship/Reflect 下一步建议，不编辑方案或 durable state。
- `tools/gstack_codex_delivery_loop_runtime.py review-dry-run --root . --json` 报告 reviewer、QA、security、documentation 和 release-readiness 缺口，不应用修复。
- `tools/gstack_codex_delivery_loop_runtime.py qa-dry-run --root . --json` 检查 browser QA 是否可准入并记录 blocker，不启动浏览器。
- `tools/gstack_codex_delivery_loop_runtime.py ship-dry-run --root . --json` 检查 local-main-first readiness 和 remote-publication gate 状态，不 push、不开 MR、不同步 GitHub。
- 未来 `--apply` 或 live 模式必须有显式 operator authorization、receipt/rollback evidence、timeout 控制，以及 local-main / remote-publication 边界检查。

未来 checker/runtime 不能改写或绕过的边界包括 OpenSpec authority、`Routing trace`、`Updated Plan`、implementation-plan claim locks、local-main-first gates、remote-publication approval gates、receipt/redaction rules、user-level install receipts、browser/GUI authorization、secret redaction 和 telemetry opt-in。

## Runtime 推广阶梯

| 阶段 | 范围 | 必要证据 |
| --- | --- | --- |
| R0 source preflight | 项目级 | Source URLs、获取日期、gstack command/workflow 映射，并证明没有 install/run。 |
| R1 dry-run runtime | 项目级 | fixture 支持的 `analyze`、`plan-dry-run`、`review-dry-run`、`qa-dry-run` 和 `ship-dry-run`；不改文件。 |
| R2 checker/runtime helper | 项目级 | checker、受保护 helper、测试、OpenSpec guard wiring、CI manifest 登记和 docs registry 登记。 |
| R3 user-level install | 用户级延后 | 显式授权、不可变 source pin、Codex-host install receipt、rollback pointer 和 redaction evidence。 |
| R4 smoke runtime | 用户级延后 | 有边界的 help/status/dry-run smoke receipt，带 timeout 和 rollback evidence。 |
| R5 active-candidate | 用户级延后 | 在 hook、全局 skill activation、browser QA、gbrain-like memory、telemetry 或 always-on workflow routing 前，先有明确 active-candidate receipt。 |

## 文件归属

本子方案拥有自身方案文件和上述未来 checker/runtime 名称。它不拥有 upstream gstack、用户级 `~/.codex/skills/gstack-*`、`~/.claude/skills/gstack`、browser adapter runtime、gbrain 或 memory stores、全局 Codex launchers、MCP Router 配置、consumer-project injected context files、telemetry settings 或 remote-publication automation。

## 并行会话契约

同一时间只能有一个 session claim 本 implementation plan。后续代码工作可与无关 Phase 4 工作并行，但 docs registry、CI manifest、OpenSpec guard wiring、delivery-loop fixtures 和 conversation-surface fixtures 必须有串行 hotspot owner。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 创建本子方案和中文 companion。
- [x] 记录 gstack 参考链接和已核验 GitHub README source boundary。
- [x] 要求后续实现达到 checker 加 runtime，而不是只做文本治理。
- [ ] 后续实现：新增 `check_gstack_codex_delivery_loop.py`，带 focused fixtures 和 JSON output。
- [ ] 后续实现：新增 `gstack_codex_delivery_loop_runtime.py`，包含 `analyze`、dry-run stage checks，以及受保护的未来 apply/live 模式。
- [ ] 后续实现：登记 focused tests、OpenSpec guard wiring 和 CI manifest 覆盖。
- [ ] 后续 runtime 推广：R3-R5 用户级安装、browser QA、hooks、gbrain-like memory、telemetry 和 always-on routing 必须受明确授权以及 receipt/rollback/redaction evidence 约束。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- `python tools/check_implementation_plan_rules.py --root . --json` - 校验 implementation plan registry、双语 companion、parent-plan、体积与 evidence-index 规则。
- `python tools/run_openspec_guard.py --root .` - 校验 OpenSpec 状态和仓库治理 guard wiring。
- `python tools/check_precommit_update_archive.py --root . --json` - 在提交前校验必须的 update/archive review。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - 在集成前运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - 在合入本地 main 前运行 local MR review gate。

后续代码工作还必须为 checker 和 runtime helper 添加 focused tests。

## 验收标准

- 本子方案已登记为 active，并链接到父方案。
- 方案记录 gstack 参考源和 Codex-local checker/runtime 目标。
- 方案说明本包不会 clone、install、enable、smoke-run 或 live-run gstack。
- R3-R5 用户级激活继续延后，并由 receipt gate 约束。
- 未来 runtime 不能绕过 local-main-first gates、remote-publication approval、browser/GUI authorization、telemetry opt-in 或 receipt/redaction boundaries。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 文档包：branch `plan-gstack-codex-delivery-loop-20260606` 创建本 active Phase 4 子方案，记录 `garrytan/gstack` 与 `gstack.lol` 参考源，并把 checker/runtime 代码留给后续实现包。
<!-- EVIDENCE_INDEX_END -->
