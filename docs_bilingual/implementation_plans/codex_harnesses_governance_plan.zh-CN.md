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
Status: implemented-local; Stage B source-ledger/checker/spec migration is complete and remote publication remains closed.
Runtime boundary: Codex harnesses are governance wrappers around future harness jobs; they do not replace Codex, native subagents, native_omx, LangGraph, codex-ohmy, apply_patch, or local-main-first publication gates.
Implementation evidence: `tools/check_codex_harnesses_governance.py` requires source ledger rows, source pin, retrieved_at, license note, rollback pointer, no Codex takeover, unpinned Pi packages rejection, read guard, write guard, job state, isolated worktree, and changed-path report markers.
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

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-04 Stage B implementation evidence: `tools/check_codex_harnesses_governance.py` and `test/check_codex_harnesses_governance.test.py` verify the harness-only lane, source ledger, no-takeover boundary, read/write guards, job state, isolated worktree, changed-path report, and no unpinned Pi packages.
<!-- EVIDENCE_INDEX_END -->
