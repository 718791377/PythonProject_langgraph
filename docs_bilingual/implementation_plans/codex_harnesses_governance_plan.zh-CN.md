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
Status: planned Stage A split target；本文档包不启用 Pi 或 oh-my-pi runtime。
Owner session: 当前 main Codex session 拥有 parent-plan hotspot 与本 child-plan creation package。
Remote publication: not authorized / 远端发布未授权。
Boundary: Codex harnesses 不得替代 Codex、native subagents、native_omx、LangGraph、`codex-ohmy` 或 `apply_patch`。
<!-- CURRENT_STATUS_END -->

## 参考源

| Reference | URL | 本 Codex fork 可复用内容 | 禁止行为 |
| --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | reliability ideas、recoverable editing、explicit failure surfacing | 复制未知代码或绕过 repo guards |
| oh-my-pi | https://github.com/can1357/oh-my-pi | sidecar UX、update/rollback concepts、Pi-oriented runtime ergonomics | 替代 Codex launcher 或持有 provider secrets |
| Pi | https://pi.dev/ | Pi runtime/RPC reference 与未来 smoke source | 未经 one-task authorization 修改当前 worktree |
| Pi packages | https://pi.dev/packages | package discovery/update reference | 没有 pin/receipt/rollback evidence 就安装 packages |

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
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 注册本双语 child plan。
- [x] Stage A：记录全部四个 harness source URLs，便于后续 refresh。
- [x] Stage A：说明只有本 lane 称为 Codex harnesses。
- [x] Stage A：将 Pi/oh-my-pi reference-sidecar 内容作为迁移输入保留到 Stage B checker migration。
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
- 2026-06-04 Stage A evidence: 本方案记录 Codex harnesses split target、四个参考源链接与 no-takeover boundary；implementation evidence pending Stage B.
<!-- EVIDENCE_INDEX_END -->
