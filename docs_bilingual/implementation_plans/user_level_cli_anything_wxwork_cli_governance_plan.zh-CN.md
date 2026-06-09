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
Status: implemented-local
Status: CLI-Anything user-level install evidence recorded; WXWork_CLI integration is delegated to the operator-designated external consumer project and remains out of this repository package.
Stage: R6 CLI-Anything user-level install evidence plus existing R5 WXWork_CLI governance handoff.
Owner session: `resume-019e8aa7-cli-anything-install`; feature branch `install-cli-anything-user-level-20260609`.
Current gate: focused tests, repository guard, precommit update/archive review, local CI, local MR review, guarded local-main-first integration; remote publication remains unauthorized.
Install evidence: source `https://github.com/HKUDS/CLI-Anything`; `cli-anything-hub==0.3.0`; ignored receipt `.omx/cli-anything/cli-anything.lock.json`; `installed-user-level`; `install_performed=true`; `network_fetch_performed=true`; `wxwork_cli_installed=false`; `wxwork_cli_controlled=false`.
R5 evidence: `wxwork-cli active-candidate lane profile` remains governed by `tools/check_r5_active_candidate_receipts.py` and `tools/user_level_receipt_governance.py active-check`; WXWork_CLI live/send implementation is handed off to the operator-designated external consumer project.
Runtime boundary: this package installs/smoke-tests CLI-Anything only; it does not install/start/control WXWork_CLI, start WXWork.exe, send WXWork messages, launch durable workers, run live harness jobs, run Spec Kit live/apply modes, mutate user-level Codex config, or mutate remote publication. Historical R5 governance packages remained not installed/started/enabled in this package.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-09
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
- [x] Stage E CLI-Anything user-level install: install `CLI-Anything` skills from `HKUDS/CLI-Anything`, install `cli-anything-hub==0.3.0`, create `cli-hub` wrappers, pass `cli-hub --help`, validate `installed-user-level` receipt, keep `wxwork_cli_installed=false` and `wxwork_cli_controlled=false`, and delegate WXWork_CLI to the operator-designated external consumer project.
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
- 2026-06-09 CLI-Anything user-level install evidence: branch `install-cli-anything-user-level-20260609` installed user-level skills from `https://github.com/HKUDS/CLI-Anything`, installed `cli-anything-hub==0.3.0`, exposed `cli-hub 0.3.0`, passed `cli-hub --help`, and wrote ignored receipt `.omx/cli-anything/cli-anything.lock.json`. Receipt validation reports `installed-user-level`, `install_performed=true`, `network_fetch_performed=true`, `user_level_config_mutated=false`, `wxwork_cli_installed=false`, `wxwork_cli_controlled=false`, source URL preserved, raw private paths redacted, and rollback pointer hashed. WXWork_CLI integration is handed off to the operator-designated external consumer project; no WXWork.exe start/control/send occurred.
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 CLI-Anything / WXWork_CLI governance 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-06 Stage D R4 local smoke tooling evidence：branch implement-cli-anything-wxwork-r4-20260606 新增 tools/wxwork_cli_governance.py smoke-record / smoke-check 与 focused tests；生成的 R4 receipts 同时通过 WXWork helper 与通用 tools/user_level_receipt_governance.py smoke-check，并保持 sanitized、no GUI control、no send action、no message body、timeout release、rollback readiness，命名 WXWork.exe 时要求 global lease。
- 2026-06-05 real-runtime gap update：branch runtime-plan-standard-20260605 将 CLI-Anything install/update、WXWork_CLI fork/adaptation、WXWork.exe control、R4 smoke 与 R5 send/action handoff 标记为 Stage D pending；未安装、未启动、未 live-run。
- 2026-06-04 Stage B evidence：tools/check_user_level_cli_anything_wxwork_cli_governance.py 与 focused tests 已验证 CLI-Anything/WXWork_CLI lane。
<!-- EVIDENCE_INDEX_END -->
