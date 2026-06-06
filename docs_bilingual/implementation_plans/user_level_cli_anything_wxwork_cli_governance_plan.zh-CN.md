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

> **给 agentic workers：** 使用 `superpowers:executing-plans`；只有写入集合互不重叠时才允许并行子代理。本方案只管理 CLI-Anything/WXWork_CLI，不是 Browser/CLI adapter，也不是 Codex harnesses；not Codex harnesses。

## 目标

把 `https://github.com/HKUDS/CLI-Anything` 作为参考源，约束通过 CLI-Anything 控制企业微信 `WXWork.exe` 的 `WXWork_CLI` lane，并把真实 send/action 限制到 R5。

## 架构

repo-local 阶段只维护治理、checker、helper、adapter-generation 与 dry-run evidence。真实 runtime 阶段才允许安装 CLI-Anything、fork/adaptation `WXWork_CLI`、发现/控制 `WXWork.exe`，并且必须经过 global lease、operator authorization、timeout release 与 rollback pointer。

## 技术栈

Python helper、CLI-Anything reference、`WXWork_CLI` adapter-plan、`WXWork.exe` 进程探测、JSON receipt、message redaction、ephemeral message handling、local CI 与 OpenSpec guard。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；Stage B checker/test/spec migration 已完成；Stage C runtime-promotion ladder 已记录并由 checker 支撑；Stage D R4 local smoke receipt tooling 已实现；真实 GUI/live WXWork runtime 仍未安装、启动或启用。
Runtime boundary：本 repo-local package 不安装 CLI-Anything，不 fork 或 uncontrolled-run WXWork_CLI，不启动或控制 WXWork.exe，不发送消息，不点击 GUI 控件，不修改企业微信状态，也不保存 no message-content，不把 lane 标记为 active-candidate。R4 smoke-tested receipt 只允许在已有 installed-user-level receipt 且 wrapper 可解析时执行 bounded help/status/safe-discovery；若显式命名 WXWork.exe GUI target，则必须有 global lease。
Runtime gap：真实 live runtime 仍需要 CLI-Anything install/update、WXWork_CLI fork/adaptation、实际 user-level R3 install receipts、授权 R4 smoke execution，以及 R5 send/action handoff 的 target/action allowlist、message redaction、ephemeral message handling、operator authorization、global lease、timeout release 与 rollback pointer。
Implementation evidence：tools/wxwork_cli_governance.py smoke-record 可写入脱敏 R4 smoke-tested receipts，且不 process probe、不 GUI control、不 send action、不保存 message body；smoke-check 校验 receipt，tools/check_user_level_cli_anything_wxwork_cli_governance.py 对 R4 helper surface 做 checker-backed 验证。
<!-- CURRENT_STATUS_END -->

## 参考源

| 项 | 参考源 | 本方案中的作用 |
| --- | --- | --- |
| CLI-Anything | https://github.com/HKUDS/CLI-Anything | 用作 GUI/CLI adapter-generation 模式参考。 |
| WXWork_CLI | repo-derived fork/adaptation | 用 CLI-Anything 控制 `WXWork.exe` 的用户级候选 runtime。 |

## 治理层级拆分

- 项目级治理：命名、边界、checker、test、fixture、adapter-plan、adapter-generation。
- 可复用项目级治理：helper schema、receipt schema、global lease schema、redaction 规则。
- 用户级治理：真实安装、启动、探测、smoke 与 live handoff 证据。

## Runtime Promotion Ladder

| Runtime stage | Level | CLI-Anything/WXWork_CLI scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | 只检查 CLI-Anything 参考源、`WXWork.exe` 目标、当前 helper 与平台约束。 | Source URL、no install/run evidence、sanitized transcript。 |
| R1 project-level fake/dry-run runtime | project-level | 运行 fake WXWork_CLI fixture、adapter-plan 与 adapter-generation dry run。 | fake command result、no GUI mutation、no message-content。 |
| R2 reusable project-level helper/guard | reusable project-level | 维护 CLI-Anything/WXWork_CLI guard、global lease、operator authorization、timeout release、rollback pointer 与 redaction schema。 | helper/checker tests、CI/OpenSpec guard。 |
| R3 user-level install/update receipt | user-level | 明确授权后安装/更新 CLI-Anything，并生成/复制 `WXWork_CLI`。 | `installed-user-level` receipt、source pin、wrapper hash、rollback pointer。 |
| R4 user-level smoke runtime | user-level | 只做 `WXWork.exe` discovery/help/status smoke，不发送消息。 | `smoke-tested` receipt、bounded transcript、timeout release。 |
| R5 active-candidate / bounded live handoff | user-level active-candidate | 仅在 allowlist 和授权下执行一次 send/action。 | `active-candidate` receipt、target/action allowlist、message redaction、ephemeral message handling。 |

本包保持 not installed/started/enabled in this package；send action allowed only at R5。

## 文件归属

本方案拥有 CLI-Anything/WXWork_CLI plan、checker、helper 与测试。它不拥有 Browser/CLI adapters，也 not Codex harnesses。

## 并行 session 合约

一个 session 独占本 implementation_plan。其他 session 可处理 Browser/CLI adapters 或 Codex harnesses，但不得同时修改本方案、WXWork helper、global lease schema 或 shared OpenSpec hotspots。

## Real Runtime Implementation Gap（真实 runtime 缺口）

后续 Stage D runtime 必须完成：

- 固定 CLI-Anything source/ref，执行 install/update，并记录 `installed-user-level` receipt。
- fork/adaptation `WXWork_CLI`，记录 adapter-plan、adapter-generation、wrapper hash、update command 与 rollback pointer。
- 发现或启动 `WXWork.exe` 前先获取 operator authorization 与 global lease。
- R4 只允许 help/status/discovery smoke；R5 才允许 send/action，且必须有 target/action allowlist、message redaction、ephemeral message handling、timeout release 与 rollback pointer。

## Task Backlog（任务 Backlog）

<!-- TASK_BACKLOG_START -->
- [x] Stage A：拆分 CLI-Anything/WXWork_CLI lane，明确它不是 Browser/CLI adapter，也不是 Codex harnesses；not Codex harnesses。
- [x] Stage B：增加 checker/test/spec，强制 WXWork_CLI、WXWork.exe、adapter-plan 与 adapter-generation marker。
- [x] Stage C：增加 R0-R5 runtime promotion ladder，并保持 not installed/started/enabled in this package。
- [x] Stage C：把 R3/R4/R5 真实 runtime 工作移出已完成 backlog，列为 Stage D pending runtime work。
- [x] Stage D R4 local smoke tooling：新增 smoke-record / smoke-check receipt 支持，只允许 bounded help/status/safe-discovery smoke；不 GUI control、不 send action、不保存 message body，并记录 timeout release、redaction、rollback readiness，命名 WXWork.exe 时要求 global lease。
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- 旧混合方案已拆分，本方案只管理 CLI-Anything/WXWork_CLI。
- checker 要求 `WXWork_CLI`、`WXWork.exe`、global lease、operator authorization、timeout release、rollback pointer、no message-content、send action allowed only at R5。
- 真实消息内容必须采用 message redaction 与 ephemeral message handling。

## 验收标准

- 中文对照版正文为中文。
- `adapter-plan` 与 `adapter-generation` marker 保留，以满足 checker。
- R5 之前不得执行 send/action。
- remote publication 关闭，除非当前用户消息明确授权。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 Stage D R4 local smoke tooling evidence：branch implement-cli-anything-wxwork-r4-20260606 新增 tools/wxwork_cli_governance.py smoke-record / smoke-check 与 focused tests；生成的 R4 receipts 同时通过 WXWork helper 与通用 tools/user_level_receipt_governance.py smoke-check，并保持 sanitized、no GUI control、no send action、no message body、timeout release、rollback readiness，命名 WXWork.exe 时要求 global lease。
- 2026-06-05 real-runtime gap update：branch runtime-plan-standard-20260605 将 CLI-Anything install/update、WXWork_CLI fork/adaptation、WXWork.exe control、R4 smoke 与 R5 send/action handoff 标记为 Stage D pending；未安装、未启动、未 live-run。
- 2026-06-04 Stage B evidence：tools/check_user_level_cli_anything_wxwork_cli_governance.py 与 focused tests 已验证 CLI-Anything/WXWork_CLI lane。
<!-- EVIDENCE_INDEX_END -->
