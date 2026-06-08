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

> 给 agentic worker：使用 `superpowers:executing-plans`；只有写入范围互不重叠时才并行使用子代理。本 R4 包实现 repo-local checker 与受保护 runtime helper；不安装 upstream gstack、不启用 hook、不启动 browser QA、不启用 telemetry、不修改 user-level Codex 配置，也不提升为 always-on runtime。

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
- 本包：实现 repo-local checker、受保护 runtime helper、focused tests、OpenSpec guard wiring、CI manifest registration、safety-rule registry entry，以及方案/父方案状态更新。
- Runtime 边界：本包不执行 hook、skill install、MCP wrapper、browser launch、gstack clone、telemetry setup、user-level config mutation、active-candidate promotion 或 remote publication。
- 后续 live implementation：任何真实 user-level install/update、browser QA、hooks、gbrain-like memory、telemetry 或 always-on routing 都需要单独的显式授权包与 receipt。
- 远端发布：除非用户明确要求 remote publication，否则不在范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R5 检查器支撑的 active-candidate 门禁已在本地实现；真实敏感 live action 仍然需要当前 lane receipt 通过后才能继续。
Stage: gstack Codex delivery-loop runtime governance 的 R5 runtime-governance receipt package。
Owner session: `resume-019e8aa7-r5-runtime-governance-batch`；feature branch 是 `implement-r5-runtime-governance-batch-20260607`。
Current gate: 先运行 focused tests、repository guard、precommit update/archive review、local CI 和 local MR review，再通过 guarded local-main-first integration；remote publication 仍未授权。
R5 evidence: `gstack-delivery-loop active-candidate lane profile` 由 `tools/check_r5_active_candidate_receipts.py` 和 `tools/user_level_receipt_governance.py active-check` 通用合约验证。
Runtime boundary: 本 R5 package 只验证 fixture-backed receipts 和 checker wiring；不安装 user-level tools，不启动 browser/GUI，不发送 WXWork 消息，不启动 durable workers，不运行 live harness jobs，不运行 Spec Kit live/apply modes，不修改 user-level config，不修改 remote publication。
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## 冲突优先级

gstack 只提供 delivery-loop 结构：Think、Plan、Build、Review、Test、Ship 与 Reflect。它可以建议排序、review、QA 或 ship readiness，但不得覆盖 Comet control、OpenSpec WHAT authority、Superpowers HOW discipline、implementation-plan claims、local-main-first gates、remote-publication approval、user-level install receipts、browser/GUI authorization 或 telemetry opt-in。若它与 Codex harness candidate runtime governance 冲突，gstack 只在 advisory delivery-loop ordering 上优先；harness-specific read/write/runtime safety 仍归 harness plan。若它与 Spec Kit templates 冲突，gstack 在 delivery-loop sequencing 上优先，而 Spec Kit 仍只是 subordinate template/probe source。未来 runtime 必须为每个 allow/block/advisory 结果输出 `authority_decision`。

Authority priority string: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

## Checker 与 Runtime 目标

本 R4 代码包提供这些 repo-local 表面：

- `tools/check_gstack_codex_delivery_loop.py --root . --json` 校验保存的 delivery-loop evidence、plan/checker/runtime 登记、参考源新鲜度，以及与 Comet、OpenSpec/Superpowers、harnesses 或 Spec Kit 冲突时的 `authority_decision` 结果。
- `tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` 报告当前 Codex delivery-loop 阶段与缺失 evidence，不写文件。
- `tools/gstack_codex_delivery_loop_runtime.py plan-dry-run --root . --json` 给出 Think/Plan/Build/Review/Test/Ship/Reflect 下一步建议，不编辑方案或 durable state。
- `tools/gstack_codex_delivery_loop_runtime.py review-dry-run --root . --json` 报告 reviewer、QA、security、documentation 和 release-readiness 缺口，不应用修复。
- `tools/gstack_codex_delivery_loop_runtime.py qa-dry-run --root . --json` 检查 browser QA 是否可准入并记录 blocker，不启动浏览器。
- `tools/gstack_codex_delivery_loop_runtime.py ship-dry-run --root . --json` 检查 local-main-first readiness 和 remote-publication gate 状态，不 push、不开 MR、不同步 GitHub。
- `tools/gstack_codex_delivery_loop_runtime.py smoke --receipt-dir <dir> --json` 写入有边界的 R4 smoke receipt。没有 install receipt 时写 blocked receipts / not-smoke-tested receipt evidence；有显式 fixture install receipt 时运行 bounded help smoke，脱敏 JSON 输出中的原始路径/密钥，记录 timeout release 和 rollback-pointer hashes，并保持对 user-level state 只读。
- `test/gstack_codex_delivery_loop_runtime.test.py` 与 `test/check_gstack_codex_delivery_loop.test.py` 覆盖 dry-run JSON、R4 blocked/positive receipts、authority priority、安全标志拦截和 redaction。
- 未来 `--apply` 或 live 模式必须有显式 operator authorization、receipt/rollback evidence、timeout 控制，以及 local-main / remote-publication 边界检查。

未来 checker/runtime 不能改写或绕过的边界包括 OpenSpec authority、`Routing trace`、`Updated Plan`、implementation-plan claim locks、local-main-first gates、remote-publication approval gates、receipt/redaction rules、user-level install receipts、browser/GUI authorization、secret redaction 和 telemetry opt-in。

## Runtime 推广阶梯

| 阶段 | 范围 | 必要证据 |
| --- | --- | --- |
| R0 source preflight | 已本地实现 | Source URLs、获取日期、gstack command/workflow 映射，并证明没有 upstream install/run。 |
| R1 dry-run runtime | 已本地实现 | fixture 支持的 `analyze`、`plan-dry-run`、`review-dry-run`、`qa-dry-run` 和 `ship-dry-run`；不改文件。 |
| R2 checker/runtime helper | 已本地实现 | checker、受保护 helper、测试、OpenSpec guard wiring、CI manifest 登记和 docs registry 登记。 |
| R3 user-level install | 仅 fixture-backed；live 延后 | checker/runtime 接受显式 install-receipt-shaped fixture evidence。真实 user-level install 仍需要单独显式授权、不可变 source pin、Codex-host install receipt、rollback pointer 和 redaction evidence。 |
| R4 smoke runtime | fixture-backed 已本地实现；live 延后 | 有边界的 help/status/dry-run smoke receipt 可以基于显式 fixture/existing wrapper 运行并带 timeout/rollback evidence；真实 upstream smoke 仍需单独授权。 |
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
- [x] 记录冲突优先级：低于 Comet/OpenSpec/Superpowers；只在 delivery-loop ordering 上作为 advisory，高于 harness runtime-candidate selection 与 Spec Kit templates。
- [x] R4 实现：新增 `check_gstack_codex_delivery_loop.py`，带 focused fixtures 和 JSON output。
- [x] R4 实现：新增 `gstack_codex_delivery_loop_runtime.py`，包含 `analyze`、dry-run stage checks、guarded fixture-backed smoke receipts，并且没有 apply/live 模式。
- [x] R4 实现：登记 focused tests、OpenSpec guard wiring、safety-rule registry 条目和 CI manifest 覆盖。
- [x] Runtime 推广边界：R3-R4 fixture-backed receipt/smoke 已在本地实现；真实 user-level install、browser QA、hooks、gbrain-like memory、telemetry、always-on routing 与 R5 active-candidate 继续延后，直到显式授权与 receipt/rollback/redaction evidence 满足。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- `python tools/check_implementation_plan_rules.py --root . --json` - 校验 implementation plan registry、双语 companion、parent-plan、体积与 evidence-index 规则。
- `python tools/run_openspec_guard.py --root .` - 校验 OpenSpec 状态和仓库治理 guard wiring。
- `python tools/check_precommit_update_archive.py --root . --json` - 在提交前校验必须的 update/archive review。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - 在集成前运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - 在合入本地 main 前运行 local MR review gate。

本 R4 包已经为 checker 和 runtime helper 增加 focused tests。

## 验收标准

- 本子方案已登记为 active，并链接到父方案。
- 方案记录 gstack 参考源和 Codex-local checker/runtime 目标。
- 方案说明本包不会 clone、install、enable、hook、browser-run、telemetry-run 或 live-run upstream gstack。
- R3-R4 fixture-backed receipt/smoke evidence 已在本地实现；真实 user-level activation 与 R5 active-candidate 继续延后，并由 receipt gate 约束。
- Runtime 不能绕过 local-main-first gates、remote-publication approval、browser/GUI authorization、telemetry opt-in 或 receipt/redaction boundaries。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 gstack Codex delivery-loop runtime governance 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-07 R4 implementation package：branch `implement-gstack-delivery-loop-r4-20260607` 新增 `tools/gstack_codex_delivery_loop_runtime.py`、`tools/check_gstack_codex_delivery_loop.py`、focused tests、OpenSpec guard wiring、CI manifest registration 与 safety-rule registry backing。Dry-run actions 与 fixture-backed R4 smoke receipts 已实现；真实 user-level install/live/browser/hook/telemetry/R5 active-candidate work 仍延后。
- 2026-06-07 conflict-priority refresh：本 docs-only package 记录 gstack 是低于 Comet/OpenSpec/Superpowers 的 subordinate delivery-loop advisory governance；仅在 advisory ordering 上高于 harness/Spec Kit；Checker + Runtime code 仍延后。
- 2026-06-06 文档包：branch `plan-gstack-codex-delivery-loop-20260606` 创建本 active Phase 4 子方案，记录 `garrytan/gstack` 与 `gstack.lol` 参考源，并把 checker/runtime 代码留给后续实现包。
<!-- EVIDENCE_INDEX_END -->
