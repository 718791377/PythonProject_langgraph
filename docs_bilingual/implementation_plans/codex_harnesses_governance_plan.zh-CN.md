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

> **For agentic workers:** 使用 `superpowers:executing-plans`。本方案是这次拆分中唯一拥有 `harnesses` 这个词的 child plan；CLI-Anything/WXWork_CLI 与 Browser/CLI adapters 都不是 harnesses。

## 目标

基于列出的 harness/Pi 参考源，fork 一个 Codex-specific harnesses governance model，同时保持 Codex 作为 primary controller。该模型强调 recoverable edits、explicit failures、stateful job handling、read-only/write guards 与 isolated worktrees。

## 架构

项目级治理先在本仓库以 docs、guard contracts、tests 与 state schemas 落地。之后再提升为可复用项目级 helpers。只有 project-level guards 通过，且 receipts 证明 pin、smoke、rollback、redaction 与 no takeover of Codex launchers 后，才允许用户级 Pi 或 oh-my-pi runtime surface。

## 技术栈

Codex CLI、Git worktrees、JSON job state、Python guard/checker scripts、OpenSpec、docs registry、Pi reference runtime、oh-my-pi reference UX，以及 receipt-backed promotion 之后才使用的 user-level Codex state。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；Stage B source-ledger/checker/spec migration 已完成；Stage C runtime-promotion ladder 已文档化并 checker-backed；remote publication remains closed。
Runtime boundary: Codex harnesses 是 future harness jobs 外围的 governance wrappers；它们不替代 Codex、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch 或 local-main-first publication gates。本包不 install Pi/oh-my-pi、不 start Pi runtime、不 enable harness sidecar，也不把该 lane 标记为 installed-user-level/smoke-tested/active-candidate。Runtime promotion 保持 not installed/started/enabled in this package。
Implementation evidence: `tools/check_codex_harnesses_governance.py` 要求 source ledger rows、source pin、retrieved_at、license note、rollback pointer、no Codex takeover、unpinned Pi packages rejection、read guard、write guard、job state、isolated worktree、changed-path report markers 与 R0-R5 runtime promotion markers。
<!-- CURRENT_STATUS_END -->

## Source Ledger

| Reference | URL | Source pin | retrieved_at | License note | Rollback pointer | Reuse scope | Forbidden behavior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | source pin: URL snapshot | retrieved_at: 2026-06-04 | license note: article reference only | rollback pointer: remove derived harness rules | reliability ideas, recoverable editing, explicit failure surfacing | do not copy unknown code or bypass repo guards |
| oh-my-pi | https://github.com/can1357/oh-my-pi | source pin: commit/tag required before implementation | retrieved_at: 2026-06-04 | license note: inspect upstream license before reuse | rollback pointer: remove sidecar helper copy | sidecar UX, update/rollback concepts, Pi-oriented runtime ergonomics | do not replace Codex launcher or own provider secrets |
| Pi | https://pi.dev/ | source pin: docs version or snapshot required | retrieved_at: 2026-06-04 | license note: docs reference only | rollback pointer: remove Pi runtime assumptions | Pi runtime/RPC reference and future smoke source | do not mutate current worktree without one-task authorization |
| Pi packages | https://pi.dev/packages | source pin: package version required | retrieved_at: 2026-06-04 | license note: package license must be recorded per package | rollback pointer: remove package candidate | package discovery/update reference | do not install packages without pin/receipt/rollback evidence |

## 治理层级拆分

| 阶段 | 治理层级 | 允许工作 | 提升门禁 |
| --- | --- | --- | --- |
| 0 | 项目级 | reference source ledger、taxonomy、no-takeover policy | docs/OpenSpec gate |
| 1 | 项目级 | harness state schema、read-only guard、write guard、fake Pi fixtures | focused tests 与 local gate |
| 2 | 可复用项目级 | 可移植 harness guard/checker pattern | examples 与 redaction checks |
| 3 | 用户级 | Pi/oh-my-pi install-record、update-record、rollback-plan、smoke plan | 明确用户授权并通过 project-level guard |
| 4 | 用户级 active-candidate | 有界 read-only Pi/oh-my-pi smoke 或 sidecar handoff | isolated worktree、job state、no takeover、changed-path report |

## Runtime Promotion Ladder

本 lane 使用共享 R0-R5 ladder；本包仍然 not installed/started/enabled in this package。

| Runtime stage | 层级 | Codex harnesses 范围 | 证据门禁 |
| --- | --- | --- | --- |
| R0 project-level preflight | 项目级 | 刷新 The Harness Problem、oh-my-pi、Pi、Pi packages source ledger；只检查 package/runtime assumptions，不 install Pi 或 oh-my-pi。 | Source URLs、source pin plan、retrieved_at、license note、rollback pointer、no Codex takeover。 |
| R1 project-level fake/dry-run runtime | 项目级 | 只运行 fake Pi job fixtures 与 deterministic read guard/write guard checks。 | Fake job state、read guard、write guard、no live Pi runtime、no Codex launcher mutation。 |
| R2 reusable project-level helper/guard | 可复用项目级 | 保持 job state、isolated worktree、changed-path report、redaction、rollback 的可复用 harness guard/checker schemas。 | Guard schema、local tests、local gate、changed-path report。 |
| R3 user-level install/update receipt | 用户级 | 只有显式授权、immutable source/package pin、install/update receipt、smoke command、updater command、rollback pointer、owner lane 与 path hashes 齐备后，才记录 Pi/oh-my-pi install/update。 | `installed-user-level` receipt、package pin、no unpinned Pi packages、no launcher takeover。 |
| R4 user-level smoke runtime | 用户级 | 只运行 bounded read-only Pi/oh-my-pi smoke 或 sidecar status probe；不运行 write-capable harness job。 | `smoke-tested` receipt、read guard、job state、timeout release、redaction、rollback readiness。 |
| R5 active-candidate / bounded live handoff | 用户级 active-candidate | active sidecar candidate 只可在 Codex leader ownership 下运行一个 bounded harness job。 | `active-candidate` receipt、isolated worktree、read guard、write guard、job state、no Codex takeover、changed-path report、rollback/cleanup evidence。 |

Codex harnesses active sidecar 不得替代 Codex、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch、local-main-first publication gates 或当前 main Codex CLI leader session。

## 文件归属

本子方案拥有 Codex harness governance docs、未来 `codex_harnesses_governance` checker/guard、Pi/oh-my-pi source ledgers、job-state schemas 与 read-only/write guard tests。它不拥有 CLI-Anything、WXWork_CLI、chrome-devtools-mcp、cdp-bridge-mcp 或 OpenCLI。

## 并行 session 合约

同一时间只能有一个 session 认领本 implementation_plan。独立 session 可以处理 CLI-Anything/WXWork_CLI 或 Browser/CLI adapters，但不得在没有串行 lease 的情况下编辑本方案、未来 harness checker/tests、docs registry、CI manifest 或共享 OpenSpec 热点。

## 任务 Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: state that only this lane is called Codex harnesses.
- [x] Stage A: record The Harness Problem, oh-my-pi, Pi, and Pi packages reference links.
- [x] Stage A: state no Codex takeover, no replacement of native Codex/OMX/LangGraph/apply_patch, and no live Pi execution.
- [x] Stage B: add source ledger requirements for source pin, retrieved_at, license note, and rollback pointer.
- [x] Stage B: add checker/spec coverage for no Codex takeover, no unpinned Pi packages, read guard, write guard, job state, isolated worktree, and changed-path report.
- [x] Stage B: wire checker/tests into CI manifest, safety registry, and OpenSpec guard.
- [x] Stage C runtime promotion：加入 R0-R5 Codex harnesses ladder、fake Pi job dry-run boundary、installed-user-level/smoke-tested/active-candidate markers，以及 no-takeover active sidecar gates。
<!-- TASK_BACKLOG_END -->

## Stage B 待迁移工作

- 添加 `codex_harnesses_governance` checker/guard。
- source refresh 必须要求 source URL、pin/ref、retrieved_at、license note 与 rollback pointer。
- 任何 sidecar output 被视为 actionable 前，必须有 read-only guard 与 write guard evidence。
- 添加 fake Pi/oh-my-pi fixture tests，覆盖 no takeover 与不得修改当前 worktree。
- 更新 CI manifest 与 OpenSpec guard registration。
- 从即将删除的 source plans 中迁移旧 Pi/harness references。

## 验收标准

- Codex harnesses 是独立 lane，不同于 CLI-Anything/WXWork_CLI 与 Browser/CLI adapters。
- Pi/oh-my-pi 只能作为 reference 或 user-level sidecar candidate，永远不是 Codex launcher。
- 没有 receipt、pin、smoke、rollback、redaction 与 no-takeover evidence，不启用任何 user-level runtime。
- 未来任何 write-capable harness path 都需要 isolated worktree ownership 与 changed-path reporting。
- Codex harnesses runtime promotion 必须明确：R0/R1/R2 保持项目级或可复用项目级；R3 需要 `installed-user-level`；R4 需要 `smoke-tested`；R5 需要 `active-candidate`、isolated worktree、job state、read/write guards、changed-path report 与 no Codex takeover。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 Stage C runtime promotion evidence：branch `runtime-promotion-plan-20260605` 记录 Codex harnesses 的 R0-R5 promotion gates，保持 Pi/oh-my-pi sidecar runtime not installed/started/enabled，并 checker-back no-takeover active sidecar constraints。
- 2026-06-04 Stage B implementation evidence: `tools/check_codex_harnesses_governance.py` and `test/check_codex_harnesses_governance.test.py` verify the harness-only lane, source ledger, no-takeover boundary, read/write guards, job state, isolated worktree, changed-path report, and no unpinned Pi packages.
<!-- EVIDENCE_INDEX_END -->
