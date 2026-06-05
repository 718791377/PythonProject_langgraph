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

> **For agentic workers:** 使用 `superpowers:executing-plans`；只有在写入集合互不重叠时才使用并行子代理。本子方案只管理 Browser/CLI adapters。CLI-Anything/WXWork_CLI 与 Codex harnesses 是兄弟方案，不是 adapter lane。

## 目标

Browser/CLI adapter lane 仅限 `chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge` 与 `OpenCLI`。这些 adapter 不是 Codex harnesses，本方案也不管理 CLI-Anything、WXWork_CLI、WXWork.exe、Pi 或 oh-my-pi。

## 架构

先在本仓库落地项目级治理：browser owner lease、port lease、隔离 profile、sensitive-action authorization、redaction、dry-run/live-start gate。只有具备 install/update receipt、smoke evidence、rollback pointer 与 owner evidence 后，才允许提升为用户级 adapter wrapper。

## 技术栈

Python adapter guard、`codex-port`、browser owner registry、chrome-devtools-mcp 参考源、cdp-bridge-mcp 参考源、OpenCLI 参考源、JSON receipt、OpenSpec、本地测试、CI manifest，以及提升后才允许使用的 `C:\Users\lenovo\.codex` 用户级 wrapper 状态。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；Stage B checker/test/spec migration 已完成；Stage C runtime-promotion ladder 已文档化并 checker-backed；remote publication remains closed。
Current gate: local `main` integration 前验证 split adapter checker、focused adapter tests、precommit/archive review、OpenSpec guard、local gate 与 local MR review。
Canonical adapter set: exactly `chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge` 与 `OpenCLI`。
Runtime boundary: 本 repo-local package 不 install tools、不 start browsers、不 call sensitive MCP methods、不 read cookies、不 execute JavaScript、不 mutate browser/GUI state、不 mutate user-level runtime state，也不把任何 adapter 标记为 installed-user-level/smoke-tested/active-candidate。Runtime promotion 保持 not installed/started/enabled in this package。
Implementation evidence: `tools/check_user_level_browser_cli_adapter_boundary.py` 拒绝 adapter lane tables 里的 CLI-Anything、WXWork_CLI、WXWork.exe、wecom-cli 与 harness wording；`test/check_user_level_browser_cli_adapter_boundary.test.py` 以及既有 chrome/CDP/OpenCLI tests 覆盖该 lane 与 R0-R5 runtime promotion markers。
<!-- CURRENT_STATUS_END -->

## 参考源

| Adapter | 参考源 | 后续更新证据要求 |
| --- | --- | --- |
| chrome-devtools-mcp | https://github.com/ChromeDevTools/chrome-devtools-mcp | source URL、package/pin、install receipt、smoke、rollback pointer |
| cdp-bridge-mcp / CDP Bridge | https://github.com/Unagi-cq/cdp-bridge-mcp | source URL、pin、port/owner lease evidence、redaction evidence |
| OpenCLI | https://github.com/jackwener/OpenCLI | source URL、pin、`--port auto` evidence、owner lease、authorization receipt |

## 治理层级拆分

| 阶段 | 治理层级 | 允许工作 | 提升门禁 |
| --- | --- | --- | --- |
| 0 | 项目级 | 分类、参考源、no-harness 边界 | docs/OpenSpec gate |
| 1 | 项目级 | adapter checker/tests、owner/port lease 检查、敏感动作 fail-closed | focused tests 与 local gate |
| 2 | 可复用项目级 | 可移植 adapter guard contract | checker-backed examples |
| 3 | 用户级 | wrapper install/update receipt、smoke、rollback plan | 明确授权并通过项目级 guard |
| 4 | 用户级 active-candidate | 有界 adapter live start 或 action handoff | owner lease、authorization receipt、expiry、redaction、rollback evidence |

## Runtime Promotion Ladder

本 lane 使用共享 R0-R5 ladder；本包仍然 not installed/started/enabled in this package。

| Runtime stage | 层级 | Browser/CLI adapter 范围 | 证据门禁 |
| --- | --- | --- | --- |
| R0 project-level preflight | 项目级 | 盘点 chrome-devtools-mcp、cdp-bridge-mcp / CDP Bridge、OpenCLI sources、package managers、port ranges 与 owner-profile assumptions；不 install、不 launch、不 connect、不读取 browser data。 | Source URLs、source pin plan、non-mutating environment probe、owner/port risk notes。 |
| R1 project-level fake/dry-run runtime | 项目级 | 运行 owner lease、codex-port、CDP action classification 与 OpenCLI start preflight 的 deterministic dry-run fixtures。 | `start_performed=false`、`connect_performed=false`、无 cookie/raw browser data、focused tests。 |
| R2 reusable project-level helper/guard | 可复用项目级 | 保持 chrome-devtools-mcp、CDP Bridge、OpenCLI 的可复用项目级 guard，并强制 owner lease + authorization receipt。 | Guard schema、redaction contract、local gate、changed-path report。 |
| R3 user-level install/update receipt | 用户级 | 每个 adapter 只有具备显式授权、immutable pin、package/source URL、install/update receipt、smoke command、updater command、rollback pointer、owner lane 与 path hashes 后才记录 install/update。 | `installed-user-level` receipt；没有显式用户级授权不得修改 Codex config。 |
| R4 user-level smoke runtime | 用户级 | 只对已安装 adapter 运行 bounded help/status/read-only smoke；不执行 sensitive click/type/navigate/JavaScript/cookie/raw-browser-data action。 | `smoke-tested` receipt、命名 browser target 时需要 owner lease、timeout release、redaction、rollback readiness。 |
| R5 active-candidate / bounded live handoff | 用户级 active-candidate | one-task live adapter handoff 才可在 owner lease + authorization receipt 下执行 sensitive actions。 | `active-candidate` receipt、owner lease + authorization receipt、target/action allowlist、expiry、rollback pointer、action transcript redaction、cleanup evidence。 |

Sensitive browser actions 在 R5 之前保持 blocked。R5 中 click/type/navigate/JavaScript/cookie/raw-browser-data 操作必须有当前 owner evidence、explicit authorization receipt、target/action allowlist 与 sanitized action reporting。

## 文件归属

本子方案拥有 Browser/CLI adapter 文档、未来 adapter scope checker 更新、chrome-devtools-mcp/CDP/OpenCLI guard 测试与 source-reference 检查。它不拥有 CLI-Anything、WXWork_CLI、企业微信、Pi、oh-my-pi 或 Codex harnesses。

## 并行 session 合约

同一时间只能有一个 session 认领本 implementation_plan。其他 session 可以并行处理 CLI-Anything/WXWork_CLI 或 Codex harnesses，但不得在没有串行 hotspot lease 的情况下编辑本方案、未来 checker/tests、docs registry、CI manifest 或共享 OpenSpec 热点。

## 任务 Backlog

<!-- TASK_BACKLOG_START -->
- [x] Keep read-only tab inventory allowed without sensitive authorization where the specific guard allows it.
- [x] Require authorization receipt for click, type, navigate, JavaScript execution, cookie read, and raw browser data access.
- [x] Require OpenCLI-style adapters to use `--port auto` and sanitized `codex-port` lease evidence.
- [x] Stage A: record the canonical Browser/CLI adapter set and reference source links.
- [x] Stage A: state that CLI-Anything/WXWork_CLI and Codex harnesses are sibling plans, not adapters.
- [x] Stage B: replace the old mixed baseline checker with the split adapter checker.
- [x] Stage B: add negative coverage for CLI-Anything, WXWork_CLI, WXWork.exe, wecom-cli, and harness terms in adapter lane tables.
- [x] Stage B: update CI manifest, safety registry, and OpenSpec guard wiring.
- [x] Stage C runtime promotion：加入 R0-R5 Browser/CLI adapter ladder、installed-user-level/smoke-tested/active-candidate markers，以及 R5 sensitive actions 的 owner lease + authorization receipt gates。
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- Adapter checker/tests 现在只接受三个 canonical adapters。
- Negative coverage 会拒绝 adapter lane tables 中的 CLI-Anything、WXWork_CLI、WXWork.exe、wecom-cli 与 harness wording。
- CI manifest、safety registry 与 OpenSpec guard wiring 已更新。
- Temporary legacy compatibility markers 已从 adapter lane ownership 中移除。
## 已实现合约

- `tools/chrome_devtools_mcp_managed.py` 保持 chrome-devtools-mcp on-demand：isolated-session 与 project-profile plans 是 dry-run，live start 需要 install receipt evidence，repo-local MVP 仍推迟实际浏览器启动。
- `tools/cdp_bridge_governance.py` 允许 read-only tab inventory 不带敏感授权，但 click、type、navigate、JavaScript execution、cookie read、raw browser data access 与 unknown actions 必须有 owner evidence 加 authorization receipt，否则 fail closed。
- `tools/opencli_governance.py` 保持 OpenCLI on-demand，要求 `--port auto`，验证 sanitized `codex-port` lease evidence，target-bound actions 需要 owner evidence，sensitive actions 需要 authorization receipts，并且即使存在 install receipt evidence 也推迟 live start。
- Sibling-lane note：`tools/cli_anything_governance.py` 与 `tools/wxwork_cli_governance.py` 归 CLI-Anything/WXWork_CLI child plan，不归 Browser/CLI adapter lane。
- Legacy note：`wecom-cli` active helper ownership 已移除；archive references 仅保留历史用途。

## Adapter lane status

| Adapter lane | Status | Repo-local evidence | Live/runtime boundary |
| --- | --- | --- | --- |
| chrome-devtools-mcp | on-demand | `tools/chrome_devtools_mcp_managed.py`, `test/chrome_devtools_mcp_managed.test.py` | No live browser start without install receipt and owner evidence; repo-local MVP still defers actual start. |
| CDP Bridge / cdp-bridge-mcp | on-demand | `tools/cdp_bridge_governance.py`, `test/cdp_bridge_governance.test.py` | Read-only tab inventory allowed; sensitive actions require owner lease plus authorization receipt. |
| OpenCLI | on-demand | `tools/opencli_governance.py`, OpenCLI coverage in `test/cdp_bridge_governance.test.py` | Requires `--port auto`, sanitized `codex-port` lease evidence, owner evidence, and receipt-gated sensitive actions. |

## 验证门禁

- Baseline checker：`python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` 在 Stage B 迁移前仍必跑。
- OpenSpec aggregate guard：`python tools/run_openspec_guard.py --root . --json` 验证 official workflow、document policy 与 name clarity rules。
- Whitespace check：`git diff --check` 验证 patch 没有 whitespace errors。

## 验收标准

- canonical adapter set 只包含 chrome-devtools-mcp、cdp-bridge-mcp / CDP Bridge 与 OpenCLI。
- CLI-Anything/WXWork_CLI 与 Codex harnesses 只作为 sibling plans 或 temporary migration inputs 出现。
- 没有 receipt、owner、rollback 与 redaction evidence，不启用任何 sensitive runtime action。
- 本地 main 集成保持串行，remote publication 仍需显式授权。
- Browser/CLI adapter runtime promotion 必须明确：R0/R1/R2 保持项目级或可复用项目级；R3 需要 `installed-user-level`；R4 需要 `smoke-tested`；R5 需要 `active-candidate`、owner lease + authorization receipt 与 sensitive actions 的 target/action allowlist。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 Stage C runtime promotion evidence：branch `runtime-promotion-plan-20260605` 记录 chrome-devtools-mcp、CDP Bridge 与 OpenCLI 的 R0-R5 promotion gates，同时保持本包 not installed/started/enabled。
- 2026-06-01: `user_level_browser_cli_adapter_boundary_plan` implementation evidence recorded branch `implement-user-level-browser-cli-adapter-boundary-20260601` for the earlier mixed adapter package.
- 2026-06-04 Stage B implementation evidence: `tools/check_user_level_browser_cli_adapter_boundary.py`, `test/check_user_level_browser_cli_adapter_boundary.test.py`, and existing chrome/CDP/OpenCLI tests verify the Browser/CLI adapter lane and reject CLI-Anything/WXWork_CLI, WXWork.exe, wecom-cli, and harness wording in adapter lane tables.
<!-- EVIDENCE_INDEX_END -->
