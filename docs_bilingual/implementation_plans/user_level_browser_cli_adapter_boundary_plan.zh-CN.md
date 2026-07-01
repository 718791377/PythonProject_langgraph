---
doc_id: user_level_browser_cli_adapter_boundary_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级 Browser / CLI Adapter 边界方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`；只有写入集合互不重叠时才允许并行子代理。本子方案只管理 Browser/CLI adapters。CLI-Anything/WXWork_CLI 与 Codex harnesses 是兄弟方案，not adapters。

## 目标

把 Browser/CLI adapter lane 收窄到 `chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge` 与 `OpenCLI`，并把真实安装、启动、探测、smoke/live handoff 放到 R3/R4/R5 证据门之后。

## 架构

repo-local 包只提供治理、checker、adapter guard 和 test。用户级 runtime 需要 owner lease、authorization receipt、codex-port、`--port auto`、target/action allowlist、redaction 与 rollback evidence。

## 技术栈

`chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge`、`OpenCLI`、browser owner registry、codex-port、JSON receipt、local CI 与 OpenSpec guard。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for `user_level_browser_cli_adapter_boundary_plan`.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `user-level-browser-cli-adapter-boundary`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
<!-- CURRENT_STATUS_END -->

## 参考源

| Adapter | Reference source | 作用 |
| --- | --- | --- |
| chrome-devtools-mcp | https://github.com/ChromeDevTools/chrome-devtools-mcp | Chrome DevTools MCP adapter。 |
| cdp-bridge-mcp / CDP Bridge | https://github.com/Unagi-cq/cdp-bridge-mcp | CDP bridge adapter。 |
| OpenCLI | https://github.com/jackwener/OpenCLI | CLI adapter reference。 |

## 治理层级拆分

- 项目级治理：adapter naming、边界、checker、test、fixture。
- 可复用项目级治理：owner lease、authorization receipt、codex-port 与 `--port auto` 规则。
- 用户级治理：真实 install/start/probe/smoke/live handoff evidence。

## Runtime Promotion Ladder

| Runtime stage | Level | Adapter scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | 只检查参考源、端口策略、browser owner registry 与 helper。 | Source URL、no install/run evidence、sanitized transcript。 |
| R1 project-level fake/dry-run runtime | project-level | 运行 fake adapter/port fixtures。 | fake command result、no browser mutation。 |
| R2 reusable project-level helper/guard | reusable project-level | 维护 adapter guard、owner lease、authorization receipt、codex-port 与 `--port auto` 策略。 | helper/checker tests、CI/OpenSpec guard。 |
| R3 user-level install/update receipt | user-level | 明确授权后安装/更新 adapter。 | `installed-user-level` receipt、source pin、wrapper hash、rollback pointer。 |
| R4 user-level smoke runtime | user-level | help/status/port smoke，不读取敏感浏览器数据。 | `smoke-tested` receipt、bounded transcript、timeout release。 |
| R5 active-candidate / bounded live handoff | user-level active-candidate | 受控 browser/CLI handoff。 | `active-candidate` receipt、owner lease + authorization receipt、target/action allowlist、rollback pointer。 |

本包保持 not installed/started/enabled in this package。

## 文件归属

本方案拥有 Browser/CLI adapter plan、checker、port/owner helper 和相关测试。CLI-Anything/WXWork_CLI 与 Codex harnesses 是兄弟方案，not adapters。

## 并行 session 合约

一个 session 独占本 implementation_plan。其他 session 可处理 CLI-Anything/WXWork_CLI 或 Codex harnesses，但不得同时改本方案、adapter checker、codex-port schema 或 shared OpenSpec hotspots。

## Real Runtime Implementation Gap（真实 runtime 缺口）

后续 Stage D runtime 必须完成：

- 固定 chrome-devtools-mcp、cdp-bridge-mcp 与 OpenCLI 的 source/ref/version。
- 执行用户级 install/update，并记录 `installed-user-level` receipts。
- 启动/探测前获取 owner lease + authorization receipt，端口使用 codex-port 与 `--port auto`。
- R4 只做 help/status/port smoke；R5 live handoff 必须有 target/action allowlist、redaction、rollback pointer 与 timeout release。

## Task Backlog（任务 Backlog）

<!-- TASK_BACKLOG_START -->
- [x] Stage A：拆分 Browser/CLI adapter lane，只保留 canonical adapter set。
- [x] Stage B：增加 checker/test/spec，验证 adapter table 与 forbidden sibling lane boundary。
- [x] Stage C：记录 R0-R5 runtime promotion ladder，并保持 not installed/started/enabled in this package。
- [x] Stage C：把真实 install/start/probe/smoke/live handoff 移出已完成 backlog，列为 Stage D pending runtime work。
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- 本方案只把 `chrome-devtools-mcp`、`CDP Bridge` 和 `OpenCLI` 视为 adapter lane。
- 真实 browser/CLI 操作需要 owner lease + authorization receipt。
- sensitive browser data 读取与 JavaScript 执行仍受 R5 live handoff gate 约束。

## Adapter lane status

| Adapter | Status | Boundary |
| --- | --- | --- |
| chrome-devtools-mcp | implemented-local governance only | R3 前不安装；R4 只 smoke help/status/port。 |
| CDP Bridge | implemented-local governance only | R3 前不安装；R4 只 smoke help/status/port。 |
| OpenCLI | implemented-local governance only | R3 前不安装；R4 只 smoke help/status/port。 |

## 验证门禁

- `python tools/check_user_level_browser_cli_adapter_boundary.py --root . --json` - 验证 Browser/CLI adapter 边界。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文。
- Adapter lane table 只包含 canonical adapter set。
- R3/R4/R5 之前不得声明已安装、已 smoke 或 active-candidate。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 Browser/CLI adapter boundary 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-06 R4 local smoke tooling evidence?branch `implement-browser-cli-adapter-r4-20260606` adds `tools/run_browser_cli_adapter_smoke.py`, `tools/check_browser_cli_adapter_smoke_receipts.py`, and `browser_cli_adapter_smoke_receipts.test.py`; blocked receipts are not smoke-tested.
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 chrome-devtools-mcp、cdp-bridge-mcp 与 OpenCLI 的 install/start/probe、R4 smoke 与 R5 handoff 标记为 Stage D pending；未安装、未启动、未 live-run。
- 2026-06-04 Stage B evidence：`tools/check_user_level_browser_cli_adapter_boundary.py` 与 focused tests 已验证 adapter boundary。
<!-- EVIDENCE_INDEX_END -->
