---
doc_id: codex_harnesses_governance_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/codex_harnesses_governance_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# Codex Harnesses 治理方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`；只有写入集合互不重叠时才允许并行子代理。本方案只管理 Codex harnesses，不管理 CLI-Anything/WXWork_CLI，也不管理 Browser/CLI adapters。

## 目标

按照 The Harness Problem、oh-my-pi、Pi 与 Pi packages 的参考源，为 Codex 设计 harness 治理：未来可接入 Pi/oh-my-pi sidecar 和 harness job runtime，但不得替代 Codex leader、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch 或 local-main-first gates。

## 架构

repo-local 阶段只维护 source ledger、checker、test、fake Pi job、read guard、write guard、job state、isolated worktree 与 changed-path report。真实 runtime 需要 R3 install/update receipt、R4 read-only smoke 与 R5 bounded live handoff。

## 技术栈

Pi/oh-my-pi reference、JSON job state、read guard、write guard、isolated worktree、changed-path report、rollback pointer、local CI 与 OpenSpec guard。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；Stage B source-ledger/checker/spec migration 已完成；Stage C runtime-promotion ladder 已记录并由 checker 支撑；Stage D real-runtime implementation 尚未安装、启动、smoke 或 live-run。
Runtime boundary：Codex harnesses 是未来 harness jobs 的治理包装；它们不会替代 Codex、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch 或 local-main-first gates；no Codex takeover。
Runtime gap：真实 runtime 仍需要 Pi/oh-my-pi sidecar install 或 pinned package candidate、harness job runner、executable read/write guards、R3 install/update receipt、R4 smoke receipt 与 R5 bounded live handoff evidence；当前 R4 helper/checker 不安装、不启动、不 live-run Pi/oh-my-pi，缺少 R3 receipt 时只写 blocked receipts，且这些 blocked receipts 保持 not smoke-tested。
Implementation evidence：`tools/check_codex_harnesses_governance.py` 要求 source ledger rows、source pin、retrieved_at、license note、rollback pointer、no Codex takeover、unpinned Pi packages check、read guard、write guard、job state、isolated worktree、changed-path report 与 fake Pi job marker；R4 本地工具新增 `tools/run_codex_harnesses_smoke.py`、`tools/check_codex_harnesses_smoke_receipts.py` 与 `codex_harnesses_smoke_receipts.test.py`，用于生成/校验只读 smoke 或 blocked receipts。
Source refresh：2026-06-06 新增 revfactory/harness、ohmyopenagent 和 snow-cli 三个 reference-only 参考源；后续 Checker + Runtime 需改为 candidate-registry-driven，本包不实现 runtime。
<!-- CURRENT_STATUS_END -->


## Source Ledger

| Source | URL | source pin | retrieved_at | license note | rollback pointer |
| --- | --- | --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | source pin: URL snapshot | retrieved_at: 2026-06-04 | license note: article reference only | rollback pointer: remove derived harness rules |
| oh-my-pi | https://github.com/can1357/oh-my-pi | source pin: d9f5a8c7ac770b91d75d6df52459bd16042936fe on main as observed 2026-06-06 | retrieved_at: 2026-06-04 and refreshed 2026-06-06 | license note: inspect upstream license before reuse | rollback pointer: remove sidecar helper copy and candidate receipt |
| Pi | https://pi.dev/ | source pin: docs version or snapshot required before runtime implementation | retrieved_at: 2026-06-04 | license note: docs reference only | rollback pointer: remove Pi runtime assumptions |
| Pi packages | https://pi.dev/packages | source pin: package version required for each candidate | retrieved_at: 2026-06-04 | license note: package license must be recorded per package | rollback pointer: remove package candidate and receipt |
| revfactory/harness | https://github.com/revfactory/harness | source pin: b8fb858ea9209d6b0d9000e551d3dedbbacb88aa on main as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports Apache-2.0; reference-only unless a later change explicitly vendors code | rollback pointer: remove team-factory candidate and derived pattern rows |
| ohmyopenagent | https://github.com/ymymssss/ohmyopenagent | source pin: 4b923aaa7e7660a57623a2cf59fd92e47fced772 on default branch feat-zh-cn-system-prompts as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports NOASSERTION/Other; reference-only, no code/config copy before license review | rollback pointer: remove discipline-agent candidate and derived prompt-boundary rows |
| snow-cli | https://github.com/MayDay-wpf/snow-cli | source pin: f1846e27b655832f52b1e51c190a12b58219cc71 on main as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports NOASSERTION/Other; reference-only, no code/config copy before license review | rollback pointer: remove terminal-agent candidate and derived CLI-runtime rows |


## Codex Harness 扩展参考源后的重设

本次刷新只更新方案和参考源，不实现 Checker + Runtime。R0-R4 之后的方向需要从 Pi/oh-my-pi-only 改为 candidate-registry-driven。candidate registry 是机器可检查的候选表，至少记录 `candidate_id`、`source_url`、`source_pin`、`license_note`、`adapter_kind`、`runtime_stage`、`allowed_actions`、`guard_profile`、`rollback_pointer` 和 `receipt_paths`。

- The Harness Problem + oh-my-pi：提供 hash-anchored edits、recoverable edits、显式失败、update receipt 和 rollback 启发。
- Pi + Pi packages：提供 runtime/package pin、install/update receipt、smoke command 和 rollback 模型。
- revfactory/harness：提供 team-factory candidate kind，包含团队架构、pipeline/fan-out/expert-pool/supervisor 模式。
- ohmyopenagent：提供 discipline-layer candidate kind，包含 intent gate、tool/MCP/skill boundary 和 rollback/uninstall 姿态。
- snow-cli：提供 terminal-agent-runtime candidate kind，包含 sub-agent config、hooks/MCP、sensitive-command policy 以及 headless/async task lifecycle。

新增参考源不会把已有 R4 本地 smoke receipt 追认为真实 runtime evidence；它们只要求后续 Checker + Runtime 实现改为 registry-backed 设计。

## Next Checker + Runtime Requirements（本包不实现）

- 扩展 `tools/check_codex_harnesses_governance.py` 和测试，要求七个 source URL、source pin、retrieved_at、license note、rollback pointer 和 candidate-registry marker。
- 新增 candidate registry schema/fixture，覆盖 `pi-runtime`、`oh-my-pi-sidecar`、`team-factory`、`discipline-layer` 和 `terminal-agent-runtime`。
- 重构 `tools/run_codex_harnesses_smoke.py` 和 `tools/check_codex_harnesses_smoke_receipts.py`，让 R4 receipt 包含 `candidate_id`、`adapter_kind`、`guard_profile`、`source_pin`、`license_note`、`sensitive_command_policy`、`hook_policy` 和 async/headless lifecycle state。
- NOASSERTION/Other 参考源（ohmyopenagent、snow-cli）在后续 license review 前只能 reference-only；Apache-2.0 参考源（revfactory/harness）也需要后续 vendoring 决策才能复用代码。
- 保持 Codex leader ownership：generated teams、discipline agents、hooks、MCP surfaces 和 terminal sub-agents 只能在 Codex-selected guards 通过后做受限建议或受限任务。


## 治理层级拆分

- 项目级治理：source ledger、candidate registry、no Codex takeover、fake candidate job、read/write guard fixture 与 job state schema。
- 可复用项目级治理：candidate registry schema、harness job receipt schema、isolated worktree、changed-path report、sensitive-command policy、hook policy、async/headless lifecycle 与 rollback contract。
- 用户级治理：selected candidate install/update、R4 read-only smoke/status probe 与 R5 bounded live handoff。


## Runtime Promotion Ladder

| Runtime stage | Level | Codex harnesses scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | 刷新 The Harness Problem、oh-my-pi、Pi、Pi packages、revfactory/harness、ohmyopenagent 与 snow-cli 参考源；不安装或运行任何 candidate。 | Source URLs、source pin、retrieved_at、license note、rollback pointer、no Codex takeover、candidate registry entry。 |
| R1 project-level fake/dry-run runtime | project-level | 只运行 fake candidate job fixture 与 deterministic read guard/write guard。 | fake Pi job 或 fake candidate job state、read guard、write guard、no live runtime。 |
| R2 reusable project-level helper/guard | reusable project-level | 维护 candidate registry、job state、isolated worktree、changed-path report、redaction、sensitive-command policy、hook policy、async/headless policy 与 rollback 的 guard/checker schema。 | guard schema、local tests、local gate、changed-path report。 |
| R3 user-level install/update receipt | user-level | 明确授权后按 selected candidate 记录 install/update。 | `installed-user-level` receipt、candidate id、package/source pin、no unpinned Pi packages 或 unpinned registry candidates、no Codex takeover。 |
| R4 user-level smoke runtime | user-level | 通过 `tools/run_codex_harnesses_smoke.py` 或后续 registry-backed runner 运行受限 read-only candidate smoke/status probe；不运行 write-capable harness job。 | `tools/check_codex_harnesses_smoke_receipts.py` 或后续 registry checker 校验 `smoke-tested` receipt、read guard、job state、timeout release、redaction、rollback readiness；缺少 R3 install receipt 时生成 blocked receipts，且 not smoke-tested。 |
| R5 active-candidate / bounded live handoff | user-level active-candidate | active candidate 只能在 Codex leader ownership 下运行一个 bounded harness job。 | `active-candidate` receipt、isolated worktree、read guard、write guard、job state、no Codex takeover、changed-path report、rollback/cleanup evidence。 |

本包保持 not installed/started/enabled in this package；active sidecar 或 active candidate 必须有 no Codex takeover evidence。


## 文件归属

本方案拥有 Codex harness governance docs、future `codex_harnesses_governance` checker/guard、source ledger rows、candidate registry schemas、job-state schemas 与 read-only/write guard tests。

## 并行 session 合约

一个 session 独占本 implementation_plan。其他 session 可处理 CLI-Anything/WXWork_CLI 或 Browser/CLI adapters，但不得同时修改本方案、future harness checker/tests、docs registry、CI manifest 或 shared OpenSpec hotspots。


## Real Runtime Implementation Gap（真实 runtime 缺口）

后续 Stage D runtime 必须完成：

- 实现 candidate-registry-backed install/update receipt，包含 pinned source/package、license posture、rollback pointer 与 no-Codex-takeover evidence。
- 实现 harness job runner receipts，包含 executable read/write guards、isolated worktree evidence、changed-path reporting、sensitive-command policy、hook policy、async/headless lifecycle、cleanup 与 rollback。
- 在任何 R5 active-candidate handoff 之前，先通过 registry-backed runner 运行 bounded R4 read-only smoke/status probe 并记录 `smoke-tested` receipt。
- R5 live harness job 必须经过 current operator authorization、owner lease、target/action allowlist、timeout release 与 post-run cleanup evidence。

## Task Backlog（任务 Backlog）

<!-- TASK_BACKLOG_START -->
- [x] Stage A：说明只有本 lane 叫 Codex harnesses。
- [x] Stage A：记录 The Harness Problem、oh-my-pi、Pi 与 Pi packages reference links。
- [x] Stage B：增加 source ledger、source pin、retrieved_at、license note 与 rollback pointer 要求。
- [x] Stage B：增加 checker/spec 覆盖 no Codex takeover、unpinned Pi packages、read guard、write guard、job state、isolated worktree 与 changed-path report。
- [x] Stage C：增加 R0-R5 Codex harnesses ladder、fake Pi job dry-run boundary、installed-user-level/smoke-tested/active-candidate marker 与 no-takeover active sidecar gates。
- [x] R4 local smoke receipt tooling：新增 `tools/run_codex_harnesses_smoke.py`、`tools/check_codex_harnesses_smoke_receipts.py` 与 `codex_harnesses_smoke_receipts.test.py`；blocked receipts 可作为诚实证据，但仍为 not smoke-tested。
- [x] 2026-06-06 source refresh：记录 revfactory/harness、ohmyopenagent 和 snow-cli 为 reference-only sources；将后续 runtime 方向改为 candidate-registry-driven；只记录 Checker + Runtime 要求，不直接实现。
<!-- TASK_BACKLOG_END -->

## Stage B 待迁移工作

- Stage D real runtime 仍需单独实施，当前只完成治理/checker/test。
- R4 本地 checker 覆盖 `codex_harnesses_smoke_receipts`，接受 blocked receipts 但不把它们当成 smoke-tested。
- active sidecar 不得接管 Codex launcher、native agents、native_omx、LangGraph 或 apply_patch。


## 验收标准

- 中文对照版正文为中文。
- source ledger 七个参考源每一行保留 source pin、retrieved_at、license note、rollback pointer。
- revfactory/harness、ohmyopenagent 和 snow-cli 保持 reference-only，直到后续 Checker + Runtime package 显式实现 candidate-registry checks 和 runtime adapters。
- R3/R4/R5 之前不得声明任何 candidate 已安装、已 smoke 或 active-candidate。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 source refresh evidence：本 docs-only package 新增 `https://github.com/revfactory/harness`、`https://github.com/ymymssss/ohmyopenagent` 和 `https://github.com/MayDay-wpf/snow-cli`，记录 source pin/license posture，并将后续 Checker + Runtime 要求改为 candidate-registry-driven；本包不实现 runtime、不安装、不启动 sidecar、不 live-run harness job、不发生 Codex takeover。
- 2026-06-06 R4 local tooling evidence：`tools/run_codex_harnesses_smoke.py`、`tools/check_codex_harnesses_smoke_receipts.py` 与 `codex_harnesses_smoke_receipts.test.py` 实现受限只读 smoke receipt 生成/校验；缺少 R3 install receipt 时写入 blocked receipts，作为证据可被接受但保持 not smoke-tested；不安装 Pi/oh-my-pi、不启动 sidecar、不运行 live harness job、不进入 active-candidate，也不发生 Codex takeover。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 Pi/oh-my-pi sidecar、harness job runner、executable read/write guards 与 R3/R4/R5 receipts 标记为 pending Stage D runtime work；no runtime is installed, started, smoked, or live-run。
- 2026-06-05 Stage C runtime promotion evidence：branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for Codex harnesses, keeps Pi/oh-my-pi sidecar runtime not installed/started/enabled, and checker-backs no-takeover active sidecar constraints。
- 2026-06-04 Stage B implementation evidence：`tools/check_codex_harnesses_governance.py` 和 `test/check_codex_harnesses_governance.test.py` verify source ledger、no Codex takeover、read guard、write guard、job state、isolated worktree、changed-path report 与 no unpinned Pi packages。
<!-- EVIDENCE_INDEX_END -->
