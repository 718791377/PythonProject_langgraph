---
doc_id: user_level_cli_anything_wxwork_cli_governance_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
  - docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md
---

# 用户级 CLI-Anything 与 WXWork_CLI 治理方案

> **For agentic workers:** 使用 `superpowers:executing-plans`。只有在分配互不重叠写入集合后才使用并行子代理。本方案只管理 CLI-Anything 与 WXWork_CLI surfaces；Browser/CLI adapters 与 Codex harnesses 是独立兄弟方案。

## 目标

把 `CLI-Anything` 与 `WXWork_CLI` 治理为一个用户级 lane；未来 `WXWork_CLI` 可以通过 CLI-Anything 控制企业微信桌面进程 `WXWork.exe`。这个 lane 不是 Codex harnesses。

## 架构

Codex 先在本仓库保留项目级 guard source，只有 receipts、pins、smoke evidence、rollback pointers、redaction 与 operator authorization 完备后，才提升为用户级 wrapper。CLI-Anything generation/control 与 WXWork_CLI GUI actions 在相关 guard 证明请求安全前保持阻塞。

## 技术栈

Python guard scripts、JSON receipts、本地测试、CI manifest entries、docs registry、OpenSpec requirements、`C:\Users\lenovo\.codex` 下的用户级 Codex state、CLI-Anything 参考源，以及未来 WXWork_CLI wrapper receipts。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local; Stage B checker/test/spec migration is complete; Stage C runtime-promotion ladder is documented and checker-backed; Stage D real CLI-Anything/WXWork_CLI runtime is planned but not executed; remote publication remains closed.
Runtime boundary: this repo-local package does not install CLI-Anything, fork or run WXWork_CLI, start or control `WXWork.exe`, send messages, click GUI controls, mutate enterprise WeChat state, mutate user-level runtime state, or mark the lane installed-user-level/smoke-tested/active-candidate.
Runtime gap: real runtime work still requires CLI-Anything install/update, WXWork_CLI fork/adaptation, WXWork.exe discovery/start/control receipts, R4 smoke receipts, and R5 send/action handoff receipts guarded by current operator authorization, GUI owner lease, target/action allowlist, timeout, redaction, and rollback evidence.
Implementation evidence: `tools/check_user_level_cli_anything_wxwork_cli_governance.py` and focused tests enforce CLI-Anything/WXWork_CLI naming, reject legacy WeCom/browser-adapter/harness ownership confusion, and keep live GUI automation disabled until R3/R4/R5 evidence exists.
<!-- CURRENT_STATUS_END -->

## 参考源

| Surface | 参考源 | 后续更新证据要求 |
| --- | --- | --- |
| CLI-Anything | https://github.com/HKUDS/CLI-Anything | source URL、immutable pin or commit、retrieved_at、license note、rollback pointer |
| WXWork_CLI | 面向 WXWork.exe control through CLI-Anything 的本地 Codex governance fork | wrapper path hash、owner lane、operator receipt、dry-run smoke、rollback pointer |
| WXWork.exe target | 只能通过 gated future WXWork_CLI lane 控制的企业微信桌面进程 | global lease、session match、expiry、no message-content evidence |

## 治理层级拆分

| 阶段 | 治理层级 | 允许工作 | 提升门禁 |
| --- | --- | --- | --- |
| 0 | 项目级 | taxonomy、source references、docs registry、OpenSpec wording | local docs gate |
| 1 | 项目级 | receipts、path redaction、no hard-load、no live control 的 guard/checker/tests | focused tests 与 local gate |
| 2 | 可复用项目级 | 可供其他 repo 使用的 generic receipt 与 authorization schema | checker-backed evidence 与 examples |
| 3 | 用户级 | CLI-Anything / WXWork_CLI install/update receipt 与 wrapper dry-run | 明确用户级授权、smoke pass、rollback pointer |
| 4 | 用户级 active-candidate | 有界 WXWork.exe dry-run 或 live handoff candidate | operator confirmation、global lease、expiry、rollback、no message body exposure |

## Runtime Promotion Ladder

本 lane 使用共享 R0-R5 ladder；本包仍然 not installed/started/enabled in this package。

| Runtime stage | 层级 | CLI-Anything/WXWork_CLI 范围 | 证据门禁 |
| --- | --- | --- | --- |
| R0 project-level preflight | 项目级 | 盘点 CLI-Anything source、planned WXWork_CLI wrapper shape、Windows path assumptions 与 `WXWork.exe` 可用性；不 clone、不 install、不 probe process、不读取消息。 | Source URL、source pin plan、retrieved_at、non-mutating environment probe、no install/run transcript。 |
| R1 project-level fake/dry-run runtime | 项目级 | 只使用 fake receipts 与 dry-run adapter-plan / gui-plan / gui-check fixtures。 | Dry-run dispatch evidence、`gui_control_performed=false`、`runs_cli_anything=false`、no message-content。 |
| R2 reusable project-level helper/guard | 可复用项目级 | 将 `tools/cli_anything_governance.py` 与 `tools/wxwork_cli_governance.py` 保持为可复用 guard pattern，覆盖 redaction、lease、authorization、timeout release、rollback pointer。 | Focused tests、local gate、reusable receipt schema、changed-path report。 |
| R3 user-level install/update receipt | 用户级 | 只有显式授权、immutable source pin、install/update receipt、smoke command、updater command、rollback pointer、owner lane 与 path hashes 齐备后，才记录 CLI-Anything 或 WXWork_CLI wrapper install/update。 | `installed-user-level` receipt；不输出 raw install/wrapper/state paths；不自动修改 Codex config。 |
| R4 user-level smoke runtime | 用户级 | 只运行 bounded help/status/dry-run smoke。WXWork GUI 仍保持 no-send 与 no-message-content。 | `smoke-tested` receipt、bounded transcript、命名 GUI target 时需要 global lease、timeout release、rollback readiness。 |
| R5 active-candidate / bounded live handoff | 用户级 active-candidate | one-task WXWork_CLI live handoff 才可包含 send action allowed only at R5。 | `active-candidate` receipt、global WXWork lease、explicit operator authorization、target/action allowlist、message redaction、ephemeral message handling、session match、future expiry、timeout release、rollback/stop evidence、post-run action report。 |

R5 send boundary：任何 WXWork_CLI send action 在 R5 之前都禁止；即使到了 R5，也不得在仓库证据里暴露 raw message-content，必须使用 target/action allowlist，message payload 必须 ephemeral/redacted，并保留 rollback/stop evidence。

## 文件归属

本子方案拥有未来 CLI-Anything 与 WXWork_CLI 治理文档、guards、tests、receipts 与 source-reference checks。它不拥有 chrome-devtools-mcp、cdp-bridge-mcp、OpenCLI、Pi、oh-my-pi 或 Codex harnesses。

## 并行 session 合约

同一时间只能有一个 session 认领本 implementation_plan。其他 session 可以并行处理 Browser/CLI adapters 或 Codex harnesses，但不得在没有串行 hotspot lease 的情况下编辑本方案、未来 checker、tests、docs registry、CI manifest 或共享 OpenSpec 热点。

## 任务 Backlog

## Real Runtime Implementation Gap

This lane is still governance-only for real GUI automation. The next runtime package must install CLI-Anything, create or pin the WXWork_CLI fork/adaptation that drives `WXWork.exe`, and record safe receipts before any enterprise WeChat interaction. Required later evidence:

- CLI-Anything source/package pin, install/update command, wrapper path hash, updater command, rollback pointer, and sanitized R3 receipt.
- WXWork_CLI fork/adaptation commit or package pin, clear delta from upstream CLI-Anything usage, wrapper path hash, rollback pointer, and sanitized R3 receipt.
- WXWork.exe discovery/start/status receipts for R4 smoke that do not send messages or mutate enterprise WeChat state.
- R5 send/action handoff receipts with current operator authorization, GUI owner lease, target/action allowlist, expiry, timeout release, transcript redaction, and rollback/cleanup evidence.


Stage D pending runtime work list:

- Stage D real runtime: install CLI-Anything with source/package pin, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: fork/adapt WXWork_CLI from CLI-Anything with explicit source pin, delta notes, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: implement WXWork.exe discovery/start/status smoke that records R4 `smoke-tested` receipt without sending messages or mutating GUI state.
- Stage D real runtime: define R5 WXWork_CLI send/action handoff guarded by operator authorization, GUI owner lease, target/action allowlist, expiry, timeout release, transcript redaction, and rollback/cleanup evidence.

<!-- TASK_BACKLOG_START -->
- [x] Stage A: register this bilingual child plan in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: record CLI-Anything source URL `https://github.com/HKUDS/CLI-Anything`.
- [x] Stage A: state that WXWork_CLI controls `WXWork.exe` through CLI-Anything and is not Codex harnesses.
- [x] Stage A: keep old source plans as migration inputs until Stage B checker migration.
- [x] Stage B: split CLI-Anything tests out of generic CDP/OpenCLI coverage.
- [x] Stage B: rename active WeCom helper/test surfaces to canonical `WXWork_CLI`.
- [x] Stage B: add checker coverage for source URL, adapter-plan and adapter-generation semantics, no-message-content, global lease, operator authorization, timeout release, rollback pointer, and dry-run boundaries.
- [x] Stage B: update CI manifest, safety registry, and OpenSpec guard registration.
- [x] Stage C runtime promotion：加入 R0-R5 项目级优先/用户级 ladder、installed-user-level/smoke-tested/active-candidate markers，以及 R5-only WXWork_CLI send-action gates。
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- Dedicated CLI-Anything/WXWork_CLI surface checker coverage 已落地。
- CLI-Anything tests 已从 generic CDP/OpenCLI coverage 中拆出。
- Active WeCom surfaces 已迁移到 canonical `WXWork_CLI` 命名，同时保留 archive history。
- No-message-content、global lease、operator authorization、timeout-release、rollback 与 dry-run checks 已 checker-backed。
- CI manifest 与 OpenSpec guard registration 已更新。
- Old source plans 已在 checkers 不再依赖后删除。
## 验收标准

- CLI-Anything/WXWork_CLI 永远不被描述为 Codex harnesses。
- active docs 使用 `WXWork_CLI` 表示未来 WXWork.exe control lane。
- 没有 receipt-backed authorization，不得安装、clone、运行、探测、读取消息、发送消息或控制 WXWork.exe。
- 用户级提升在 project-level guards 本地通过前保持阻塞。
- Runtime promotion 必须明确：R0/R1/R2 保持项目级或可复用项目级；R3 需要 `installed-user-level`；R4 需要 `smoke-tested`；R5 需要 `active-candidate`，且只有 R5 才可考虑 WXWork_CLI send action。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` classifies CLI-Anything install, WXWork_CLI fork/adaptation, WXWork.exe control, R4 smoke, and R5 send/action handoff as pending Stage D runtime work; no GUI runtime is installed, started, controlled, smoked, or live-run.
- 2026-06-05 Stage C runtime promotion evidence：branch `runtime-promotion-plan-20260605` 记录 CLI-Anything/WXWork_CLI 的 R0-R5 promotion gates，保持本包 not installed/started/enabled，并 checker-back R5-only send action controls。
- 2026-06-04 Stage B implementation evidence: `tools/check_user_level_cli_anything_wxwork_cli_governance.py`, `test/check_user_level_cli_anything_wxwork_cli_governance.test.py`, `test/cli_anything_governance.test.py`, and `test/wxwork_cli_governance.test.py` verify the CLI-Anything/WXWork_CLI split lane, adapter-plan and adapter-generation semantics, no-message-content boundary, global lease, operator authorization, timeout release, rollback pointer, and dry-run-only dispatch.
<!-- EVIDENCE_INDEX_END -->
