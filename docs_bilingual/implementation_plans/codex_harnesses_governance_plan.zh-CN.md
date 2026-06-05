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
Runtime gap：真实 runtime 仍需要 Pi/oh-my-pi sidecar install 或 pinned package candidate、harness job runner、executable read/write guards、R3 install/update receipt、R4 smoke receipt 与 R5 bounded live handoff evidence。
Implementation evidence：`tools/check_codex_harnesses_governance.py` 要求 source ledger rows、source pin、retrieved_at、license note、rollback pointer、no Codex takeover、unpinned Pi packages check、read guard、write guard、job state、isolated worktree、changed-path report 与 fake Pi job marker。
<!-- CURRENT_STATUS_END -->

## Source Ledger

| Source | URL | source pin | retrieved_at | license note | rollback pointer |
| --- | --- | --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |
| oh-my-pi | https://github.com/can1357/oh-my-pi | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |
| Pi | https://pi.dev/ | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |
| Pi packages | https://pi.dev/packages | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |
| Pi package candidate | https://pi.dev/packages | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |
| oh-my-pi package candidate | https://github.com/can1357/oh-my-pi | source pin pending before R3 | retrieved_at required before R3 | license note required before R3 | rollback pointer required before R3 |

## 治理层级拆分

- 项目级治理：source ledger、no Codex takeover、fake Pi job、read/write guard fixture、job state schema。
- 可复用项目级治理：harness job receipt schema、isolated worktree、changed-path report 与 rollback contract。
- 用户级治理：Pi/oh-my-pi sidecar install/update、R4 smoke 与 R5 bounded live handoff。

## Runtime Promotion Ladder

| Runtime stage | Level | Codex harnesses scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | 刷新 The Harness Problem、oh-my-pi、Pi、Pi packages 参考源；不安装 Pi 或 oh-my-pi。 | Source URLs、source pin plan、retrieved_at、license note、rollback pointer、no Codex takeover。 |
| R1 project-level fake/dry-run runtime | project-level | 只运行 fake Pi job fixture 与 deterministic read guard/write guard。 | fake Pi job state、read guard、write guard、no live Pi runtime。 |
| R2 reusable project-level helper/guard | reusable project-level | 维护 job state、isolated worktree、changed-path report、redaction、rollback 的 guard/checker schema。 | guard schema、local tests、local gate、changed-path report。 |
| R3 user-level install/update receipt | user-level | 明确授权后记录 Pi/oh-my-pi install/update。 | `installed-user-level` receipt、package pin、no unpinned Pi packages、no Codex takeover。 |
| R4 user-level smoke runtime | user-level | 运行受限 read-only Pi/oh-my-pi smoke 或 sidecar status probe；不运行 write-capable harness job。 | `smoke-tested` receipt、read guard、job state、timeout release、rollback readiness。 |
| R5 active-candidate / bounded live handoff | user-level active-candidate | active sidecar 只能在 Codex leader ownership 下运行一个 bounded harness job。 | `active-candidate` receipt、isolated worktree、read guard、write guard、job state、changed-path report、rollback/cleanup evidence。 |

本包保持 not installed/started/enabled in this package；active sidecar 必须有 no Codex takeover evidence。

## 文件归属

本方案拥有 Codex harness governance docs、future `codex_harnesses_governance` checker/guard、Pi/oh-my-pi reference rows、job-state schemas 与 read-only/write guard tests。

## 并行 session 合约

一个 session 独占本 implementation_plan。其他 session 可处理 CLI-Anything/WXWork_CLI 或 Browser/CLI adapters，但不得同时修改本方案、future harness checker/tests、docs registry、CI manifest 或 shared OpenSpec hotspots。

## Real Runtime Implementation Gap（真实 runtime 缺口）

后续 Stage D runtime 必须完成：

- 实现 Pi/oh-my-pi sidecar install/update receipt，包含 pinned source/package、rollback pointer 与 no-Codex-takeover evidence。
- 实现 harness job runner receipts，包含 executable read/write guards、isolated worktree evidence、changed-path reporting、cleanup 与 rollback。
- 在任何 R5 active-candidate handoff 之前，先运行 bounded R4 read-only smoke 并记录 `smoke-tested` receipt。
- R5 live harness job 必须经过 current operator authorization、owner lease、target/action allowlist、timeout release 与 post-run cleanup evidence。

## Task Backlog（任务 Backlog）

<!-- TASK_BACKLOG_START -->
- [x] Stage A：说明只有本 lane 叫 Codex harnesses。
- [x] Stage A：记录 The Harness Problem、oh-my-pi、Pi 与 Pi packages reference links。
- [x] Stage B：增加 source ledger、source pin、retrieved_at、license note 与 rollback pointer 要求。
- [x] Stage B：增加 checker/spec 覆盖 no Codex takeover、unpinned Pi packages、read guard、write guard、job state、isolated worktree 与 changed-path report。
- [x] Stage C：增加 R0-R5 Codex harnesses ladder、fake Pi job dry-run boundary、installed-user-level/smoke-tested/active-candidate marker 与 no-takeover active sidecar gates。
<!-- TASK_BACKLOG_END -->

## Stage B 待迁移工作

- Stage D real runtime 仍需单独实施，当前只完成治理/checker/test。
- active sidecar 不得接管 Codex launcher、native agents、native_omx、LangGraph 或 apply_patch。

## 验收标准

- 中文对照版正文为中文。
- source ledger 每一行保留 source pin、retrieved_at、license note、rollback pointer。
- R3/R4/R5 之前不得声明 Pi/oh-my-pi sidecar 已安装、已 smoke 或 active-candidate。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 Pi/oh-my-pi sidecar、harness job runner、executable read/write guards 与 R3/R4/R5 receipts 标记为 pending Stage D runtime work；no runtime is installed, started, smoked, or live-run。
- 2026-06-05 Stage C runtime promotion evidence：branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for Codex harnesses, keeps Pi/oh-my-pi sidecar runtime not installed/started/enabled, and checker-backs no-takeover active sidecar constraints。
- 2026-06-04 Stage B implementation evidence：`tools/check_codex_harnesses_governance.py` 和 `test/check_codex_harnesses_governance.test.py` verify source ledger、no Codex takeover、read guard、write guard、job state、isolated worktree、changed-path report 与 no unpinned Pi packages。
<!-- EVIDENCE_INDEX_END -->
